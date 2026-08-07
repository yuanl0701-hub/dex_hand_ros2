"""Hardware-independent hand controller."""

from __future__ import annotations

from collections.abc import Callable
import time

from .driver import DriverError, GenericMotorDriver
from .gestures import GestureDefinition, GestureLibrary
from .pid import PIDConfig, PIDController
from .safety import SafetyController, SafetyState
from .trajectory import MultiAxisQuinticTrajectory


class HandController:
    """Coordinate gesture, trajectory, PID, and safety behavior."""

    def __init__(
        self,
        driver: GenericMotorDriver,
        gestures: GestureLibrary,
        safety: SafetyController,
        *,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.driver = driver
        self.gestures = gestures
        self.safety = safety
        self._sleep = sleeper
        self._pid = {motor_id: PIDController() for motor_id in driver.config.motor_ids}

    def set_positions(self, positions: dict[int, float]) -> bool:
        validated = self.safety.validate_command(positions)
        return self.driver.set_multiple_positions(validated)

    def set_motor_position(self, motor_id: int, position: float) -> bool:
        return self.set_positions({motor_id: position})

    def add_gesture(
        self,
        name: str,
        positions: dict[int, float],
        description: str = "",
        duration: float = 0.5,
    ) -> bool:
        self.gestures.add(GestureDefinition(name, positions, description, duration))
        return True

    def get_gesture_list(self) -> list[str]:
        return self.gestures.names()

    def run_gesture(self, name: str, speed: float = 1.0) -> bool:
        if speed <= 0:
            raise ValueError("gesture speed must be positive")
        gesture = self.gestures.get(name)
        return self.set_positions(gesture.positions)

    def run_gesture_with_mode(
        self,
        name: str,
        speed: float = 1.0,
        *,
        mode: str = "smooth",
    ) -> bool:
        """Run one gesture as a direct setpoint or a sampled smooth trajectory."""
        normalized_mode = mode.strip().lower()
        if normalized_mode == "direct":
            return self.run_gesture(name, speed)
        if normalized_mode == "smooth":
            return self.run_gesture_smooth(name, speed)
        raise ValueError("gesture execution mode must be direct or smooth")

    def run_gesture_smooth(
        self,
        name: str,
        speed: float = 1.0,
        *,
        sample_period: float = 0.02,
    ) -> bool:
        if speed <= 0:
            raise ValueError("gesture speed must be positive")
        gesture = self.gestures.get(name)
        starts: dict[int, float] = {}
        unavailable: list[int] = []
        for motor_id in self.driver.config.motor_ids:
            position = self.driver.get_position(motor_id)
            if position is None:
                unavailable.append(motor_id)
            else:
                starts[motor_id] = float(position)
        if unavailable and not self.driver.allows_partial_operation():
            raise DriverError(
                "gesture start feedback unavailable for motors: "
                + ", ".join(str(motor_id) for motor_id in unavailable)
            )
        if not starts:
            raise DriverError("gesture start feedback unavailable for every motor")
        targets = {motor_id: gesture.positions[motor_id] for motor_id in starts}
        trajectory = MultiAxisQuinticTrajectory(starts, targets, gesture.duration / speed)
        points = trajectory.sample(sample_period)
        for index, point_set in enumerate(points):
            if self.safety.status.state is not SafetyState.READY:
                return False
            positions = {motor_id: point.position for motor_id, point in point_set.items()}
            if not self.set_positions(positions):
                return False
            if index + 1 < len(points):
                self._sleep(sample_period)
        return True

    def configure_pid(self, motor_id: int, kp: float, ki: float, kd: float) -> None:
        self.driver.config.validate_motor_id(motor_id)
        self._pid[motor_id] = PIDController(PIDConfig(kp=kp, ki=ki, kd=kd))

    def set_motor_with_pid(
        self,
        motor_id: int,
        target: float,
        *,
        tolerance: float = 2.0,
        max_iterations: int = 40,
        sample_period: float = 0.02,
    ) -> bool:
        self.driver.config.validate_motor_id(motor_id)
        self.driver.config.validate_position(target)
        if tolerance < 0 or max_iterations <= 0 or sample_period <= 0:
            raise ValueError("invalid PID execution limits")
        controller = self._pid[motor_id]
        controller.reset()
        for _ in range(max_iterations):
            if self.safety.status.state is not SafetyState.READY:
                return False
            current = self._required_position(motor_id)
            error = target - current
            if abs(error) <= tolerance:
                return True
            effort = controller.compute(target, current, sample_period)
            next_position = current + effort * sample_period
            next_position = max(
                self.driver.config.position_min,
                min(self.driver.config.position_max, next_position),
            )
            if not self.set_motor_position(motor_id, next_position):
                return False
            self._sleep(sample_period)
        return abs(target - self._required_position(motor_id)) <= tolerance

    def run_gesture_with_pid(self, name: str) -> bool:
        gesture = self.gestures.get(name)
        return all(
            self.set_motor_with_pid(motor_id, target)
            for motor_id, target in gesture.positions.items()
        )

    def _hold_after_stop(self, reason: str) -> bool:
        try:
            return self.driver.hold_current_position()
        except Exception as exc:
            self.safety.fault(f"{reason}; actuator hold failed: {exc}")
            return False

    def emergency_stop(self, reason: str = "operator request") -> bool:
        """Latch software stop and request an active actuator hold."""
        self.safety.emergency_stop(reason)
        return self._hold_after_stop(reason)

    def check_watchdog(self) -> bool:
        """Apply watchdog policy and actively hold after a timeout transition."""
        was_ready = self.safety.status.state is SafetyState.READY
        ready = self.safety.check_watchdog()
        if was_ready and not ready:
            self._hold_after_stop(self.safety.status.reason)
            return False
        return ready

    def fault(self, reason: str) -> bool:
        """Latch a non-recoverable software fault and request actuator hold."""
        self.safety.fault(reason)
        return self._hold_after_stop(reason)

    def recover(self) -> bool:
        return self.driver.is_connected() and self.safety.recover()

    def shutdown(self) -> None:
        if self.driver.is_connected() and self.safety.status.state is SafetyState.READY:
            self.emergency_stop("controller shutdown")
        self.safety.shutdown()
        self.driver.disconnect()

    def _required_position(self, motor_id: int) -> float:
        value = self.driver.get_position(motor_id)
        if value is None:
            raise DriverError(f"position unavailable for motor {motor_id}")
        return float(value)

"""Deterministic actuator-level simulation compatible with GenericMotorDriver."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
import random
from threading import RLock
import time
from typing import Callable, Mapping, Optional

from .driver import (
    DriverConfig,
    DriverValidationError,
    GenericMotorDriver,
)


@dataclass(frozen=True)
class SimulatedMotorConfig:
    """First-order plant parameters; positions use normalized-percent units."""

    time_constant: float = 0.20
    max_velocity: float = 250.0
    max_acceleration: float = 1500.0
    command_delay: float = 0.0
    deadband: float = 0.0
    measurement_noise_std: float = 0.0
    command_noise_std: float = 0.0
    random_seed: int = 6048
    deterministic_mode: bool = True
    initial_position: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.time_constant,
            self.max_velocity,
            self.max_acceleration,
            self.command_delay,
            self.deadband,
            self.measurement_noise_std,
            self.command_noise_std,
            self.initial_position,
        )
        if not all(math.isfinite(value) for value in values):
            raise DriverValidationError("simulation parameters must be finite")
        if self.time_constant <= 0 or self.max_velocity <= 0 or self.max_acceleration <= 0:
            raise DriverValidationError("time constant and dynamic limits must be positive")
        if min(
            self.command_delay,
            self.deadband,
            self.measurement_noise_std,
            self.command_noise_std,
        ) < 0:
            raise DriverValidationError("delay, deadband, and noise must be non-negative")


@dataclass(frozen=True)
class MotorSimulationState:
    motor_id: int
    target_position: float
    actual_position: float
    velocity: float
    acceleration: float
    enabled: bool
    fault: str | None
    last_update_time: float


class SimulatedMotorDriver(GenericMotorDriver):
    """Thread-safe first-order plant advanced explicitly by :meth:`step`.

    The unsaturated plant is ``dq/dt = (q_target - q) / tau``. Velocity and
    acceleration are then clamped before semi-implicit Euler integration.
    No background thread is created; a ROS timer or a test owns simulation time.
    """

    _SUPPORTED_FAULTS = {
        "motor_stuck",
        "motor_disconnect",
        "position_bias",
        "reduced_velocity",
        "limit_hit",
        "over_temperature",
        "stale_feedback",
        "command_drop",
    }

    def __init__(
        self,
        port: str = "",
        baudrate: int = 115200,
        config: DriverConfig | None = None,
        simulation_config: SimulatedMotorConfig | None = None,
        *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        del port, baudrate
        super().__init__(config)
        self.simulation_config = simulation_config or SimulatedMotorConfig()
        self.config.validate_position(self.simulation_config.initial_position)
        self._clock = clock
        self._connected = False
        self._simulation_time = 0.0
        self._lock = RLock()
        self._rng = random.Random(self.simulation_config.random_seed)
        now = self._clock()
        initial = self.simulation_config.initial_position
        self._states = {
            motor_id: MotorSimulationState(
                motor_id, initial, initial, 0.0, 0.0, True, None, now
            )
            for motor_id in self.config.motor_ids
        }
        self._pending: list[tuple[float, int, float]] = []
        self._fault_values: dict[int, float] = {}

    @property
    def simulation_time(self) -> float:
        with self._lock:
            return self._simulation_time

    def connect(self) -> bool:
        with self._lock:
            self._connected = True
        return True

    def disconnect(self) -> None:
        with self._lock:
            self._connected = False

    def shutdown(self) -> None:
        self.disconnect()

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def set_single_position(self, motor_id: int, position: float) -> bool:
        return self.set_multiple_positions({motor_id: position})

    def set_multiple_positions(self, positions: Mapping[int, float]) -> bool:
        self._require_connected()
        commands = self.validate_positions(positions, require_complete=False)
        with self._lock:
            for motor_id, position in commands.items():
                state = self._states[motor_id]
                if state.fault == "command_drop":
                    continue
                noise = (
                    self._rng.gauss(0.0, self.simulation_config.command_noise_std)
                    if self.simulation_config.command_noise_std
                    else 0.0
                )
                target = _clamp(
                    position + noise, self.config.position_min, self.config.position_max
                )
                due = self._simulation_time + self.simulation_config.command_delay
                self._pending.append((due, motor_id, target))
            self._apply_due_commands()
        return True

    def get_position(self, motor_id: int) -> Optional[float]:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        with self._lock:
            state = self._states[motor_id]
            if state.fault in {"motor_disconnect", "stale_feedback"}:
                return None
            bias = self._fault_values.get(motor_id, 0.0) if state.fault == "position_bias" else 0.0
            noise = (
                self._rng.gauss(0.0, self.simulation_config.measurement_noise_std)
                if self.simulation_config.measurement_noise_std
                else 0.0
            )
            return _clamp(
                state.actual_position + bias + noise,
                self.config.position_min,
                self.config.position_max,
            )

    def step(self, dt: float) -> dict[int, MotorSimulationState]:
        """Advance all motors synchronously by an explicit positive interval."""
        if not math.isfinite(dt) or dt <= 0:
            raise DriverValidationError("simulation dt must be finite and positive")
        self._require_connected()
        with self._lock:
            self._simulation_time += float(dt)
            self._apply_due_commands()
            now = self._clock()
            updated: dict[int, MotorSimulationState] = {}
            for motor_id, state in self._states.items():
                immobile = not state.enabled or state.fault in {
                    "motor_stuck",
                    "motor_disconnect",
                    "over_temperature",
                    "limit_hit",
                }
                if immobile:
                    velocity = 0.0
                    acceleration = (velocity - state.velocity) / dt
                    position = state.actual_position
                else:
                    error = state.target_position - state.actual_position
                    desired_velocity = 0.0 if abs(error) <= self.simulation_config.deadband else (
                        error / self.simulation_config.time_constant
                    )
                    velocity_limit = self.simulation_config.max_velocity
                    if state.fault == "reduced_velocity":
                        velocity_limit *= self._fault_values.get(motor_id, 0.25)
                    desired_velocity = _clamp(
                        desired_velocity, -velocity_limit, velocity_limit
                    )
                    max_dv = self.simulation_config.max_acceleration * dt
                    velocity = state.velocity + _clamp(
                        desired_velocity - state.velocity, -max_dv, max_dv
                    )
                    position = _clamp(
                        state.actual_position + velocity * dt,
                        self.config.position_min,
                        self.config.position_max,
                    )
                    if position in (self.config.position_min, self.config.position_max):
                        velocity = 0.0
                    acceleration = (velocity - state.velocity) / dt
                updated[motor_id] = replace(
                    state,
                    actual_position=position,
                    velocity=velocity,
                    acceleration=acceleration,
                    last_update_time=now,
                )
            self._states = updated
            return dict(updated)

    def snapshot(self) -> dict[int, MotorSimulationState]:
        self._require_connected()
        with self._lock:
            return dict(self._states)

    def inject_fault(self, motor_id: int, fault: str, value: float = 0.0) -> None:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        if fault not in self._SUPPORTED_FAULTS:
            raise DriverValidationError(f"unsupported simulated fault: {fault}")
        if not math.isfinite(value):
            raise DriverValidationError("fault value must be finite")
        with self._lock:
            self._states[motor_id] = replace(self._states[motor_id], fault=fault)
            self._fault_values[motor_id] = float(value)

    def clear_faults(self, motor_id: int | None = None) -> None:
        self._require_connected()
        ids = self.config.motor_ids if motor_id is None else (motor_id,)
        with self._lock:
            for current_id in ids:
                self.config.validate_motor_id(current_id)
                self._states[current_id] = replace(self._states[current_id], fault=None)
                self._fault_values.pop(current_id, None)

    def reset(self) -> None:
        self._require_connected()
        with self._lock:
            initial = self.simulation_config.initial_position
            now = self._clock()
            self._simulation_time = 0.0
            self._pending.clear()
            self._fault_values.clear()
            self._rng.seed(self.simulation_config.random_seed)
            self._states = {
                motor_id: MotorSimulationState(
                    motor_id, initial, initial, 0.0, 0.0, True, None, now
                )
                for motor_id in self.config.motor_ids
            }

    def change_id(self, old_id: int, new_id: int) -> bool:
        raise DriverValidationError("simulated motor IDs are fixed by configuration")

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(target_id)
        if new_baud <= 0:
            raise DriverValidationError("baud rate must be positive")
        return True

    def _apply_due_commands(self) -> None:
        remaining: list[tuple[float, int, float]] = []
        for due, motor_id, target in self._pending:
            if due <= self._simulation_time:
                self._states[motor_id] = replace(
                    self._states[motor_id], target_position=target
                )
            else:
                remaining.append((due, motor_id, target))
        self._pending = remaining


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))

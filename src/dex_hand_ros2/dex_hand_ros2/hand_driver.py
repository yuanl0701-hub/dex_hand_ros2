"""Compatibility facade for the original project module."""

from __future__ import annotations

from pathlib import Path

from .backends import FeetechDriver, HTS20LDriver, MPD20Driver
from .backends.protocols import FeetechProtocol, ModbusRTUProtocol
from .core.controller import HandController
from .core.driver import DriverConfig, GenericMotorDriver, MockMotorDriver
from .core.gestures import GestureDefinition, GestureLibrary
from .core.pid import PIDConfig, PIDController
from .core.safety import SafetyController
from .simulation.driver import SimulatedMotorConfig, SimulatedMotorDriver

FakeMotorDriver = MockMotorDriver


class RoboticHand(HandController):
    """Backward-compatible controller with validated default gestures."""

    def __init__(
        self,
        driver: GenericMotorDriver,
        gesture_file: str | Path | None = None,
        *,
        watchdog_timeout: float = 1.0,
        max_rate: float = 1000.0,
    ) -> None:
        if gesture_file is None:
            library = GestureLibrary(driver.config)
            for gesture in _default_gestures(driver.config):
                library.add(gesture)
        else:
            library = GestureLibrary.load(gesture_file, driver.config)
        safety = SafetyController(
            driver.config,
            watchdog_timeout=watchdog_timeout,
            max_rate=max_rate,
        )
        super().__init__(driver, library, safety)

    def set_motor_pid(self, motor_id: int, kp: float, ki: float, kd: float) -> bool:
        self.configure_pid(motor_id, kp, ki, kd)
        return True


def _default_gestures(config: DriverConfig) -> list[GestureDefinition]:
    high = config.position_max
    low = config.position_min
    ids = config.motor_ids
    return [
        GestureDefinition("open", {motor_id: high for motor_id in ids}, "Open"),
        GestureDefinition("fist", {motor_id: low for motor_id in ids}, "Fist"),
        GestureDefinition(
            "vgesture",
            {motor_id: high if index in (0, 2) else low for index, motor_id in enumerate(ids)},
            "Legacy V gesture",
        ),
    ]


__all__ = [
    "DriverConfig",
    "FakeMotorDriver",
    "FeetechDriver",
    "FeetechProtocol",
    "GenericMotorDriver",
    "GestureDefinition",
    "HTS20LDriver",
    "MPD20Driver",
    "ModbusRTUProtocol",
    "PIDConfig",
    "PIDController",
    "RoboticHand",
    "SimulatedMotorConfig",
    "SimulatedMotorDriver",
]

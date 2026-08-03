"""Compatibility adapter for the pre-refactor driver factory API."""

from __future__ import annotations

from typing import Mapping

from .backends.factory import (
    ConnectionSettings,
    MPD20Settings,
    SimulationSettings,
    create_driver as create_typed_driver,
)
from .backends.mpd20 import MPD20MotorCalibration
from .core.driver import DriverConfig, GenericMotorDriver
from .simulation.driver import SimulatedMotorConfig


def create_driver(
    backend: str,
    port: str,
    baudrate: int,
    *,
    timeout: float,
    retries: int,
    config: DriverConfig,
    simulation_config: SimulatedMotorConfig | None = None,
    mpd20_calibrations: Mapping[int, MPD20MotorCalibration] | None = None,
    mpd20_device_ids: Mapping[int, int] | None = None,
    hardware_motion_enabled: bool = False,
    hardware_verify_on_connect: bool = True,
    hardware_hold_on_connect: bool = True,
    hardware_require_stationary_on_connect: bool = True,
) -> GenericMotorDriver:
    """Translate the historical flat arguments into typed backend settings."""

    normalized = backend.strip().lower()
    settings: MPD20Settings | SimulationSettings | None = None
    if normalized == "mpd20":
        settings = MPD20Settings(
            calibrations=mpd20_calibrations,
            device_ids=mpd20_device_ids,
            motion_enabled=hardware_motion_enabled,
            verify_on_connect=hardware_verify_on_connect,
            hold_on_connect=hardware_hold_on_connect,
            require_stationary_on_connect=hardware_require_stationary_on_connect,
        )
    elif normalized in {"sim", "simulated"}:
        settings = SimulationSettings(simulation_config or SimulatedMotorConfig())
    return create_typed_driver(
        backend,
        config=config,
        connection=ConnectionSettings(port, baudrate, timeout, retries),
        settings=settings,
    )


__all__ = [
    "ConnectionSettings",
    "MPD20Settings",
    "SimulationSettings",
    "create_driver",
    "create_typed_driver",
]

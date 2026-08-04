"""Typed backend construction without hardware-specific keyword leakage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from ..core.driver import DriverConfig, GenericMotorDriver, MockMotorDriver
from ..simulation.driver import SimulatedMotorConfig, SimulatedMotorDriver
from .feetech import FeetechDriver
from .hts20l import HTS20LDriver
from .mpd20 import MPD20Driver, MPD20MotorCalibration


@dataclass(frozen=True)
class ConnectionSettings:
    """Transport settings shared by serial backends."""

    port: str = ""
    baudrate: int = 115200
    timeout: float = 0.3
    retries: int = 1

    def __post_init__(self) -> None:
        if self.baudrate <= 0 or self.timeout <= 0 or self.retries < 0:
            raise ValueError("invalid backend connection settings")


@dataclass(frozen=True)
class MPD20Settings:
    """MPD20-only startup and per-actuator calibration settings."""

    calibrations: Mapping[int, MPD20MotorCalibration] | None = None
    device_ids: Mapping[int, int] | None = None
    motion_enabled: bool = False
    verify_on_connect: bool = True
    hold_on_connect: bool = True
    require_stationary_on_connect: bool = True
    allow_partial_operation: bool = False


@dataclass(frozen=True)
class SimulationSettings:
    """Simulation-only plant settings."""

    motor: SimulatedMotorConfig = field(default_factory=SimulatedMotorConfig)


BackendSettings = MPD20Settings | SimulationSettings | None


def create_driver(
    backend: str,
    *,
    config: DriverConfig,
    connection: ConnectionSettings | None = None,
    settings: BackendSettings = None,
) -> GenericMotorDriver:
    """Create one backend from a generic request and typed backend settings."""

    normalized = backend.strip().lower()
    connection = connection or ConnectionSettings()
    if normalized in {"fake", "mock"}:
        _require_settings(normalized, settings, type(None))
        return MockMotorDriver(connection.port, connection.baudrate, config)
    if normalized in {"sim", "simulated"}:
        _require_settings(normalized, settings, (SimulationSettings, type(None)))
        simulation = settings.motor if isinstance(settings, SimulationSettings) else None
        return SimulatedMotorDriver(
            connection.port,
            connection.baudrate,
            config,
            simulation_config=simulation,
        )
    if normalized == "mpd20":
        _require_settings(normalized, settings, (MPD20Settings, type(None)))
        mpd20 = settings if isinstance(settings, MPD20Settings) else MPD20Settings()
        return MPD20Driver(
            connection.port,
            connection.baudrate,
            timeout=connection.timeout,
            retries=connection.retries,
            config=config,
            calibrations=mpd20.calibrations,
            device_ids=mpd20.device_ids,
            motion_enabled=mpd20.motion_enabled,
            verify_on_connect=mpd20.verify_on_connect,
            hold_on_connect=mpd20.hold_on_connect,
            require_stationary_on_connect=mpd20.require_stationary_on_connect,
            allow_partial_operation=mpd20.allow_partial_operation,
        )
    if normalized == "hts20l":
        _require_settings(normalized, settings, type(None))
        return HTS20LDriver(
            connection.port,
            connection.baudrate,
            timeout=connection.timeout,
            retries=connection.retries,
            config=config,
        )
    if normalized == "feetech":
        _require_settings(normalized, settings, type(None))
        return FeetechDriver(
            connection.port,
            connection.baudrate,
            timeout=connection.timeout,
            config=config,
        )
    raise ValueError(f"unknown driver_type: {backend}")


def _require_settings(
    backend: str,
    settings: BackendSettings,
    expected: type[object] | tuple[type[object], ...],
) -> None:
    if not isinstance(settings, expected):
        raise TypeError(f"backend {backend} received incompatible settings: {type(settings).__name__}")

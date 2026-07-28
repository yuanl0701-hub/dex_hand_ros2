"""Backend construction from validated configuration."""

from __future__ import annotations

from .driver import DriverConfig, GenericMotorDriver, MockMotorDriver
from .real_drivers import FeetechDriver, HTS20LDriver, MPD20Driver
from .sim_driver import SimulatedMotorConfig, SimulatedMotorDriver


def create_driver(
    backend: str,
    port: str,
    baudrate: int,
    *,
    timeout: float,
    retries: int,
    config: DriverConfig,
    simulation_config: SimulatedMotorConfig | None = None,
) -> GenericMotorDriver:
    """Create a known backend and reject silent fallback."""
    normalized = backend.strip().lower()
    if normalized in {"fake", "mock"}:
        return MockMotorDriver(port, baudrate, config)
    if normalized in {"sim", "simulated"}:
        return SimulatedMotorDriver(
            port, baudrate, config, simulation_config=simulation_config
        )
    if normalized == "mpd20":
        return MPD20Driver(
            port,
            baudrate,
            timeout=timeout,
            retries=retries,
            config=config,
        )
    if normalized == "hts20l":
        return HTS20LDriver(
            port,
            baudrate,
            timeout=timeout,
            retries=retries,
            config=config,
        )
    if normalized == "feetech":
        return FeetechDriver(port, baudrate, timeout=timeout, config=config)
    raise ValueError(f"unknown driver_type: {backend}")

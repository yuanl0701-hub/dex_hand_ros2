"""Translate ROS parameters into typed backend construction requests."""

from __future__ import annotations

from typing import Any, Protocol

from ..backends.factory import (
    ConnectionSettings,
    MPD20Settings,
    SimulationSettings,
    create_driver,
)
from ..backends.mpd20 import build_mpd20_calibrations
from ..core.driver import DriverConfig, GenericMotorDriver
from ..simulation.driver import SimulatedMotorConfig


class ROSParameter(Protocol):
    value: Any


class ROSParameterNode(Protocol):
    def declare_parameter(self, name: str, value: object) -> object: ...
    def get_parameter(self, name: str) -> ROSParameter: ...


BACKEND_PARAMETER_DEFAULTS: dict[str, object] = {
    "serial_port": "/dev/ttyUSB0",
    "baudrate": 115200,
    "serial_timeout": 0.3,
    "serial_retries": 1,
    "hardware_motion_enabled": False,
    "hardware_verify_on_connect": True,
    "hardware_hold_on_connect": True,
    "hardware_require_stationary_on_connect": True,
    # Zero means "reuse the logical IDs"; deployments should override this.
    "mpd20_device_ids": [0],
    "mpd20_raw_min": [120],
    "mpd20_raw_max": [850],
    "mpd20_directions": [1],
    "mpd20_max_speeds": [10],
    "simulation_update_rate": 100.0,
    "sim_time_constant": 0.2,
    "sim_max_velocity": 250.0,
    "sim_max_acceleration": 1500.0,
    "sim_command_delay": 0.0,
    "sim_deadband": 0.0,
    "sim_measurement_noise_std": 0.0,
    "sim_command_noise_std": 0.0,
    "sim_random_seed": 6048,
    "sim_deterministic_mode": True,
    "sim_initial_position": 0.0,
}


def declare_backend_parameters(node: ROSParameterNode) -> None:
    """Declare compatibility parameters owned by backend adapters."""

    for name, value in BACKEND_PARAMETER_DEFAULTS.items():
        node.declare_parameter(name, value)


def create_driver_from_parameters(
    node: ROSParameterNode,
    backend: str,
    config: DriverConfig,
) -> GenericMotorDriver:
    """Build a driver while keeping hardware branches out of the ROS node."""

    connection = ConnectionSettings(
        port=str(node.get_parameter("serial_port").value),
        baudrate=int(node.get_parameter("baudrate").value),
        timeout=float(node.get_parameter("serial_timeout").value),
        retries=int(node.get_parameter("serial_retries").value),
    )
    normalized = backend.strip().lower()
    settings: MPD20Settings | SimulationSettings | None = None
    if normalized == "mpd20":
        count = len(config.motor_ids)
        physical_ids = _expand_device_ids(node, config)
        settings = MPD20Settings(
            calibrations=build_mpd20_calibrations(
                config.motor_ids,
                _expand_per_motor(node, "mpd20_raw_min", count),
                _expand_per_motor(node, "mpd20_raw_max", count),
                _expand_per_motor(node, "mpd20_directions", count),
                _expand_per_motor(node, "mpd20_max_speeds", count),
            ),
            device_ids=dict(zip(config.motor_ids, physical_ids)),
            motion_enabled=bool(node.get_parameter("hardware_motion_enabled").value),
            verify_on_connect=bool(node.get_parameter("hardware_verify_on_connect").value),
            hold_on_connect=bool(node.get_parameter("hardware_hold_on_connect").value),
            require_stationary_on_connect=bool(
                node.get_parameter("hardware_require_stationary_on_connect").value
            ),
        )
    elif normalized in {"sim", "simulated"}:
        settings = SimulationSettings(
            SimulatedMotorConfig(
                time_constant=float(node.get_parameter("sim_time_constant").value),
                max_velocity=float(node.get_parameter("sim_max_velocity").value),
                max_acceleration=float(node.get_parameter("sim_max_acceleration").value),
                command_delay=float(node.get_parameter("sim_command_delay").value),
                deadband=float(node.get_parameter("sim_deadband").value),
                measurement_noise_std=float(
                    node.get_parameter("sim_measurement_noise_std").value
                ),
                command_noise_std=float(node.get_parameter("sim_command_noise_std").value),
                random_seed=int(node.get_parameter("sim_random_seed").value),
                deterministic_mode=bool(node.get_parameter("sim_deterministic_mode").value),
                initial_position=float(node.get_parameter("sim_initial_position").value),
            )
        )
    return create_driver(
        backend,
        config=config,
        connection=connection,
        settings=settings,
    )


def _expand_per_motor(node: ROSParameterNode, name: str, count: int) -> list[int]:
    value = node.get_parameter(name).value
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{name} must be an integer array")
    values = [int(item) for item in value]
    if len(values) == 1:
        return values * count
    if len(values) != count:
        raise ValueError(f"{name} must contain one value or {count} values")
    return values


def _expand_device_ids(node: ROSParameterNode, config: DriverConfig) -> list[int]:
    value = node.get_parameter("mpd20_device_ids").value
    if not isinstance(value, (list, tuple)):
        raise ValueError("mpd20_device_ids must be an integer array")
    values = [int(item) for item in value]
    if values == [0]:
        return list(config.motor_ids)
    if len(values) != len(config.motor_ids):
        raise ValueError(
            f"mpd20_device_ids must contain {len(config.motor_ids)} physical bus addresses"
        )
    return values

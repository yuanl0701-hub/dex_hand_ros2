from pathlib import Path

import pytest

from dex_hand_ros2.backends.factory import (
    ConnectionSettings,
    MPD20Settings,
    SimulationSettings,
    create_driver,
)
from dex_hand_ros2.core import DriverConfig, MockMotorDriver
from dex_hand_ros2.simulation import SimulatedMotorDriver


PACKAGE_ROOT = Path(__file__).parents[1]
CONFIG_ROOT = PACKAGE_ROOT / "config"


def test_typed_factory_rejects_settings_from_another_backend():
    config = DriverConfig((1, 2))
    mock = create_driver("fake", config=config, connection=ConnectionSettings())
    simulated = create_driver(
        "simulated",
        config=config,
        settings=SimulationSettings(),
    )

    assert isinstance(mock, MockMotorDriver)
    assert isinstance(simulated, SimulatedMotorDriver)
    with pytest.raises(TypeError, match="incompatible settings"):
        create_driver("fake", config=config, settings=MPD20Settings())


def test_configuration_layers_do_not_recombine_hardware_and_hand_data():
    runtime = (CONFIG_ROOT / "runtime" / "default.yaml").read_text(encoding="utf-8")
    backend = (CONFIG_ROOT / "backends" / "mpd20.yaml").read_text(encoding="utf-8")
    model = (
        CONFIG_ROOT / "hand_models" / "mpd20_six_axis" / "ros_parameters.yaml"
    ).read_text(encoding="utf-8")
    deployment = (
        CONFIG_ROOT / "deployments" / "mpd20_hand.example.yaml"
    ).read_text(encoding="utf-8")

    assert "mpd20_" not in runtime
    assert "serial_port" not in runtime
    assert "motor_ids:" not in backend
    assert "mpd20_raw_" not in backend
    assert "serial_port" not in model
    assert "mpd20_device_ids" not in model
    assert "pid_kp" not in deployment
    assert "command_watchdog_timeout" not in deployment
    assert "mpd20_device_ids" in deployment
    assert "command_watchdog_enabled: false" in (
        CONFIG_ROOT / "runtime" / "physical_conservative.yaml"
    ).read_text(encoding="utf-8")


def test_legacy_aggregate_configuration_files_are_removed():
    for name in (
        "hand.yaml",
        "mpd20_hand.yaml",
        "simulated_hand.yaml",
        "isaac_sim.yaml",
        "revo2_right_hand.yaml",
    ):
        assert not (CONFIG_ROOT / name).exists()

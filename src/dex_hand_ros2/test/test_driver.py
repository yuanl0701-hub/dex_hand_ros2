import math

import pytest

from dex_hand_ros2.driver import (
    DriverConfig,
    DriverNotConnectedError,
    DriverValidationError,
    MockMotorDriver,
)


def test_driver_config_rejects_invalid_domains():
    with pytest.raises(DriverValidationError):
        DriverConfig((1, 1))
    with pytest.raises(DriverValidationError):
        DriverConfig(position_min=100, position_max=0)


def test_mock_requires_connection_and_disconnect_is_idempotent():
    driver = MockMotorDriver()
    with pytest.raises(DriverNotConnectedError):
        driver.get_position(1)
    assert driver.connect()
    assert driver.get_position(1) == 0.0
    driver.disconnect()
    driver.disconnect()
    assert not driver.is_connected()


def test_mock_validates_atomically():
    driver = MockMotorDriver()
    driver.connect()
    before = driver.snapshot()
    with pytest.raises(DriverValidationError):
        driver.set_multiple_positions({1: 25, 2: math.nan})
    assert driver.snapshot() == before
    with pytest.raises(DriverValidationError):
        driver.set_single_position(99, 10)


def test_mock_state_and_context_cleanup():
    driver = MockMotorDriver()
    with driver:
        assert driver.set_multiple_positions({1: 10, 2: 20})
        assert driver.get_multiple_positions([1, 2]) == {1: 10.0, 2: 20.0}
    assert not driver.is_connected()


def test_mock_id_change_updates_configuration():
    driver = MockMotorDriver()
    driver.connect()
    assert driver.change_id(1, 7)
    assert driver.config.motor_ids == (7, 2, 3, 4, 5, 6)
    assert driver.get_position(7) == 0.0

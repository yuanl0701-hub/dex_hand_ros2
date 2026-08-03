import math

import pytest

from dex_hand_ros2.driver import DriverConfig, DriverValidationError
from dex_hand_ros2.safety import SafetyController, SafetyState


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_limits_nonfinite_unknown_and_completeness():
    safety = SafetyController(DriverConfig(), max_rate=1000)
    with pytest.raises(DriverValidationError):
        safety.validate_command({})
    with pytest.raises(DriverValidationError):
        safety.validate_command({1: math.inf})
    with pytest.raises(DriverValidationError):
        safety.validate_command({7: 10})
    with pytest.raises(DriverValidationError):
        safety.validate_command({1: 10}, require_complete=True)


def test_rate_limit_and_watchdog():
    clock = Clock()
    safety = SafetyController(DriverConfig(), watchdog_timeout=1.0, max_rate=10.0, clock=clock)
    safety.validate_command({1: 0})
    clock.now = 0.5
    with pytest.raises(DriverValidationError):
        safety.validate_command({1: 10})
    clock.now = 1.1
    assert not safety.check_watchdog()
    assert safety.status.state is SafetyState.STOPPED


def test_stop_recovery_fault_and_shutdown():
    safety = SafetyController(DriverConfig())
    safety.emergency_stop()
    safety.emergency_stop("second request")
    assert safety.status.state is SafetyState.STOPPED
    with pytest.raises(DriverValidationError):
        safety.validate_command({1: 0})
    assert safety.recover()
    safety.fault("test fault")
    assert not safety.recover()
    safety.emergency_stop("must not downgrade fault")
    assert safety.status.state is SafetyState.FAULT
    safety.shutdown()
    assert safety.status.state is SafetyState.SHUTDOWN

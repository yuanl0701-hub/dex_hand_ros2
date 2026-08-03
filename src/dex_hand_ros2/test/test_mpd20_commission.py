import pytest

from dex_hand_ros2.backends.mpd20 import MPD20Telemetry
from dex_hand_ros2.commissioning.mpd20_commission import wait_for_jog_completion
from dex_hand_ros2.driver import DriverValidationError
from dex_hand_ros2.mpd20_commission import validate_jog


def telemetry(position, moving=False):
    return MPD20Telemetry(1, 1, position, 0, 0, 0, 0, moving)


class TelemetrySequenceDriver:
    def __init__(self, values):
        self.values = iter(values)

    def read_telemetry(self, motor_id):
        assert motor_id == 1
        return next(self.values)


def test_commissioning_jog_requires_confirmation_and_small_delta():
    with pytest.raises(DriverValidationError, match="confirm"):
        validate_jog(500, 510, 20, False)
    with pytest.raises(DriverValidationError, match="requested raw delta"):
        validate_jog(500, 600, 20, True)
    with pytest.raises(DriverValidationError, match="max_delta"):
        validate_jog(500, 510, 51, True)
    validate_jog(500, 520, 20, True)


def test_commissioning_waits_past_initial_stationary_feedback():
    before = telemetry(205)
    driver = TelemetrySequenceDriver(
        [
            telemetry(205),
            telemetry(207),
            telemetry(210),
            telemetry(210),
            telemetry(210),
        ]
    )

    after = wait_for_jog_completion(
        driver, 1, before, 1.0, poll_interval=0, stable_samples=2
    )

    assert after.raw_position == 210


def test_commissioning_accepts_motion_flag_then_stop():
    before = telemetry(205)
    driver = TelemetrySequenceDriver([telemetry(207, True), telemetry(210)])

    after = wait_for_jog_completion(driver, 1, before, 1.0, poll_interval=0)

    assert after.raw_position == 210

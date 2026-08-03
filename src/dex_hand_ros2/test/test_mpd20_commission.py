import pytest

from dex_hand_ros2.driver import DriverValidationError
from dex_hand_ros2.mpd20_commission import validate_jog


def test_commissioning_jog_requires_confirmation_and_small_delta():
    with pytest.raises(DriverValidationError, match="confirm"):
        validate_jog(500, 510, 20, False)
    with pytest.raises(DriverValidationError, match="requested raw delta"):
        validate_jog(500, 600, 20, True)
    with pytest.raises(DriverValidationError, match="max_delta"):
        validate_jog(500, 510, 51, True)
    validate_jog(500, 520, 20, True)

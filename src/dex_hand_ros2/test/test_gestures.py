import json

import pytest

from dex_hand_ros2.driver import DriverConfig, DriverValidationError
from dex_hand_ros2.gestures import GestureDefinition, GestureLibrary


def complete_positions(value=10):
    return {motor_id: value for motor_id in range(1, 7)}


def test_add_and_ordering():
    library = GestureLibrary(DriverConfig())
    library.add(GestureDefinition("first", complete_positions()))
    library.add(GestureDefinition("second", complete_positions(20)))
    assert library.names() == ["first", "second"]
    assert list(library.get("first").positions) == [1, 2, 3, 4, 5, 6]


def test_rejects_duplicate_missing_units_and_limits():
    library = GestureLibrary(DriverConfig())
    library.add(GestureDefinition("pose", complete_positions()))
    with pytest.raises(DriverValidationError):
        library.add(GestureDefinition("pose", complete_positions()))
    with pytest.raises(DriverValidationError):
        library.add(GestureDefinition("missing", {1: 10}))
    with pytest.raises(DriverValidationError):
        library.add(GestureDefinition("unit", complete_positions(), units="radians"))
    with pytest.raises(DriverValidationError):
        library.add(GestureDefinition("limit", complete_positions(101)))


def test_json_compatible_yaml_loading(tmp_path):
    path = tmp_path / "gestures.yaml"
    path.write_text(
        json.dumps(
            {
                "gestures": [
                    {
                        "name": "pose",
                        "positions": {str(i): i for i in range(1, 7)},
                        "duration": 1.0,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    library = GestureLibrary.load(path, DriverConfig())
    assert library.get("pose").positions[6] == 6.0


def test_unknown_gesture():
    with pytest.raises(KeyError):
        GestureLibrary(DriverConfig()).get("unknown")

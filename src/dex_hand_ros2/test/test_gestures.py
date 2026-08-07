import json
from pathlib import Path

import pytest

from dex_hand_ros2.driver import DriverConfig, DriverValidationError
from dex_hand_ros2.gestures import GestureDefinition, GestureLibrary
from dex_hand_ros2.real_drivers import MPD20Driver


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


def test_packaged_gesture_catalog_is_complete_and_ordered():
    gesture_file = (
        Path(__file__).parents[1]
        / "config"
        / "hand_models"
        / "generic_six_axis"
        / "gestures.json"
    )
    library = GestureLibrary.load(gesture_file, DriverConfig())

    assert library.names() == [
        "open",
        "fist",
        "vgesture",
        "pinch_two",
        "pinch_three",
        "pinch_side",
        "point",
        "thumbs_up",
        "gesture_666",
    ]
    for name in library.names():
        gesture = library.get(name)
        assert list(gesture.positions) == [1, 2, 3, 4, 5, 6]
        assert all(0.0 <= value <= 100.0 for value in gesture.positions.values())


def test_reference_gesture_vectors_remain_backward_compatible():
    gesture_file = (
        Path(__file__).parents[1]
        / "config"
        / "hand_models"
        / "generic_six_axis"
        / "gestures.json"
    )
    library = GestureLibrary.load(gesture_file, DriverConfig())

    assert list(library.get("open").positions.values()) == [100.0] * 6
    assert list(library.get("fist").positions.values()) == [0.0] * 6
    assert list(library.get("vgesture").positions.values()) == [
        100.0,
        0.0,
        100.0,
        0.0,
        0.0,
        0.0,
    ]


def test_mpd20_hardware_gestures_use_safe_raw_equivalent_endpoints():
    gesture_file = (
        Path(__file__).parents[1]
        / "config"
        / "hand_models"
        / "mpd20_six_axis"
        / "commissioning_gestures.json"
    )
    library = GestureLibrary.load(gesture_file, DriverConfig())

    assert library.names() == [
        "open",
        "half_open",
        "fist",
        "vgesture",
        "rock",
        "point",
    ]
    for name in library.names():
        positions = library.get(name).positions
        assert positions[6] == 50.0
        assert all(1.37 <= positions[motor_id] <= 98.63 for motor_id in range(1, 6))
    assert library.get("fist").positions == {
        1: 1.37,
        2: 1.37,
        3: 1.37,
        4: 1.37,
        5: 38.36,
        6: 50.0,
    }
    driver = MPD20Driver("fake", motion_enabled=False, verify_on_connect=False)
    assert [
        driver.position_to_raw(motor_id, library.get("open").positions[motor_id])
        for motor_id in range(1, 6)
    ] == [840] * 5
    assert [
        driver.position_to_raw(motor_id, library.get("fist").positions[motor_id])
        for motor_id in range(1, 5)
    ] == [130] * 4
    assert driver.position_to_raw(5, library.get("fist").positions[5]) == 400

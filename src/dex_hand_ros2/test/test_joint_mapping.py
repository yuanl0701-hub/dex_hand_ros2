import math

import pytest

from dex_hand_ros2.joint_mapping import MotorJointMapping, map_joint_state
from dex_hand_ros2.kinematics import planar_fingertip


def test_mapping_endpoints_direction_offset_and_scale():
    forward = MotorJointMapping(1, "motor_1_joint", joint_min_rad=-0.2, joint_max_rad=1.0)
    assert forward.to_joint(0.0) == pytest.approx(-0.2)
    assert forward.to_joint(100.0) == pytest.approx(1.0)
    reverse = MotorJointMapping(
        2,
        "motor_2_joint",
        joint_min_rad=0.0,
        joint_max_rad=1.0,
        direction=-1,
        offset_rad=0.1,
        scale=0.5,
    )
    assert reverse.to_joint(0.0) == pytest.approx(0.6)
    assert reverse.to_joint(100.0) == pytest.approx(0.1)
    assert reverse.velocity_to_joint(10.0) == pytest.approx(-0.05)


def test_mapping_rejects_nonfinite_limits_and_missing_state():
    mapping = MotorJointMapping(1, "motor_1_joint")
    with pytest.raises(ValueError):
        mapping.to_joint(math.nan)
    with pytest.raises(ValueError):
        mapping.to_joint(101.0)
    with pytest.raises(ValueError):
        map_joint_state([mapping], {})


def test_joint_state_arrays_and_nominal_forward_kinematics():
    mappings = [
        MotorJointMapping(1, "motor_1_joint"),
        MotorJointMapping(2, "motor_2_joint", direction=-1),
    ]
    names, positions, velocities = map_joint_state(
        mappings, {1: 0.0, 2: 100.0}, {1: 10.0, 2: 20.0}
    )
    assert names == ["motor_1_joint", "motor_2_joint"]
    assert positions == pytest.approx([0.0, 0.0])
    assert velocities == pytest.approx([0.12, -0.24])
    x, y = planar_fingertip(0.0)
    assert x == pytest.approx(0.097)
    assert y == pytest.approx(0.0)


def test_one_motor_can_fan_out_to_coupled_virtual_joints():
    mappings = [
        MotorJointMapping(
            1,
            "finger_proximal_joint",
            joint_min_rad=0.0,
            joint_max_rad=1.41,
            direction=-1,
        ),
        MotorJointMapping(
            1,
            "finger_distal_joint",
            joint_min_rad=0.0,
            joint_max_rad=1.41 * 1.155,
            direction=-1,
        ),
    ]
    names, positions, velocities = map_joint_state(
        mappings, {1: 0.0}, {1: -10.0}
    )
    assert names == ["finger_proximal_joint", "finger_distal_joint"]
    assert positions == pytest.approx([1.41, 1.41 * 1.155])
    assert positions[1] == pytest.approx(1.155 * positions[0])
    assert velocities[1] == pytest.approx(1.155 * velocities[0])

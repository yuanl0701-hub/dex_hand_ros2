import math

import pytest

from dex_hand_ros2.trajectory import MultiAxisQuinticTrajectory, QuinticTrajectory


def test_quintic_boundary_conditions():
    trajectory = QuinticTrajectory(2, 12, 2.0)
    start = trajectory.evaluate(0)
    end = trajectory.evaluate(2.0)
    assert start.position == pytest.approx(2)
    assert start.velocity == pytest.approx(0)
    assert start.acceleration == pytest.approx(0)
    assert end.position == pytest.approx(12)
    assert end.velocity == pytest.approx(0, abs=1e-10)
    assert end.acceleration == pytest.approx(0, abs=1e-10)


def test_quintic_nonzero_boundary_conditions():
    trajectory = QuinticTrajectory(
        1,
        5,
        2,
        start_velocity=0.5,
        end_velocity=-0.25,
        start_acceleration=0.1,
        end_acceleration=-0.2,
    )
    start = trajectory.evaluate(0)
    end = trajectory.evaluate(2)
    assert (start.position, start.velocity, start.acceleration) == pytest.approx((1, 0.5, 0.1))
    assert (end.position, end.velocity, end.acceleration) == pytest.approx((5, -0.25, -0.2))


def test_samples_include_endpoint_and_monotonic_time():
    samples = QuinticTrajectory(0, 1, 1.0).sample(0.3)
    assert samples[-1].time == 1.0
    assert all(a.time < b.time for a, b in zip(samples, samples[1:]))
    assert all(math.isfinite(point.jerk) for point in samples)


def test_invalid_trajectory_inputs():
    with pytest.raises(ValueError):
        QuinticTrajectory(0, 1, 0)
    with pytest.raises(ValueError):
        QuinticTrajectory(0, 1, 1).sample(0)
    with pytest.raises(ValueError):
        MultiAxisQuinticTrajectory({1: 0}, {2: 1}, 1)


def test_multi_axis_dimensions():
    trajectory = MultiAxisQuinticTrajectory({1: 0, 2: 10}, {1: 10, 2: 0}, 1)
    end = trajectory.evaluate(1)
    assert end[1].position == pytest.approx(10)
    assert end[2].position == pytest.approx(0)

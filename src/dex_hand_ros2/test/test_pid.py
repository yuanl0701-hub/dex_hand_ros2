import pytest

from dex_hand_ros2.pid import PIDConfig, PIDController


def test_pid_zero_error_and_reset():
    pid = PIDController(PIDConfig(kp=1.0, ki=1.0, kd=1.0))
    assert pid.compute(1.0, 1.0, 0.1) == 0.0
    pid.compute(2.0, 1.0, 0.1)
    pid.reset()
    assert pid.integral == 0.0
    assert pid.previous_error is None


def test_pid_positive_negative_and_saturation():
    pid = PIDController(PIDConfig(kp=10, output_min=-2, output_max=2))
    assert pid.compute(1, 0, 0.1) == 2
    assert pid.compute(0, 1, 0.1) == -2


def test_pid_integral_clamp_and_anti_windup():
    pid = PIDController(
        PIDConfig(
            kp=10,
            ki=1,
            output_min=-1,
            output_max=1,
            integral_min=-0.5,
            integral_max=0.5,
        )
    )
    for _ in range(10):
        pid.compute(10, 0, 0.1)
    assert pid.integral == 0.0


@pytest.mark.parametrize("dt", [0.0, -1.0])
def test_pid_rejects_invalid_dt(dt):
    with pytest.raises(ValueError):
        PIDController().compute(1, 0, dt)


def test_pid_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        PIDConfig(kp=-1)
    with pytest.raises(ValueError):
        PIDConfig(output_min=1, output_max=1)

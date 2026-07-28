import math

import pytest

from dex_hand_ros2.driver import DriverConfig, DriverNotConnectedError, DriverValidationError
from dex_hand_ros2.sim_driver import SimulatedMotorConfig, SimulatedMotorDriver
from dex_hand_ros2.pid import PIDConfig, PIDController


def make_driver(**kwargs):
    driver = SimulatedMotorDriver(
        config=DriverConfig(),
        simulation_config=SimulatedMotorConfig(**kwargs),
        clock=lambda: 10.0,
    )
    driver.connect()
    return driver


def test_connect_initial_state_and_shutdown():
    driver = SimulatedMotorDriver()
    with pytest.raises(DriverNotConnectedError):
        driver.get_position(1)
    assert driver.connect()
    assert driver.get_position(1) == 0.0
    assert driver.snapshot()[1].velocity == 0.0
    driver.shutdown()
    assert not driver.is_connected()


def test_target_does_not_instantly_change_actual_and_step_advances():
    driver = make_driver()
    driver.set_single_position(1, 80.0)
    assert driver.get_position(1) == 0.0
    state = driver.step(0.01)[1]
    assert 0.0 < state.actual_position < 80.0
    assert state.target_position == 80.0


def test_velocity_and_acceleration_limits_and_position_bounds():
    driver = make_driver(max_velocity=5.0, max_acceleration=10.0)
    driver.set_single_position(1, 100.0)
    for _ in range(500):
        state = driver.step(0.01)[1]
        assert abs(state.velocity) <= 5.0 + 1e-9
        assert abs(state.acceleration) <= 10.0 + 1e-9
        assert 0.0 <= state.actual_position <= 100.0


def test_six_motors_step_synchronously():
    driver = make_driver()
    driver.set_multiple_positions({motor_id: motor_id * 10.0 for motor_id in range(1, 7)})
    snapshot = driver.step(0.02)
    assert set(snapshot) == set(range(1, 7))
    assert all(state.last_update_time == 10.0 for state in snapshot.values())
    assert snapshot[6].actual_position >= snapshot[1].actual_position


def test_seeded_noise_is_reproducible():
    config = dict(measurement_noise_std=0.1, random_seed=42)
    first, second = make_driver(**config), make_driver(**config)
    assert [first.get_position(1) for _ in range(5)] == [
        second.get_position(1) for _ in range(5)
    ]


def test_fault_injection_clear_and_reset():
    driver = make_driver(initial_position=10.0)
    driver.set_single_position(1, 90.0)
    driver.inject_fault(1, "motor_stuck")
    driver.step(0.1)
    assert driver.get_position(1) == 10.0
    driver.clear_faults(1)
    driver.step(0.1)
    assert driver.get_position(1) > 10.0
    driver.inject_fault(1, "motor_disconnect")
    assert driver.get_position(1) is None
    driver.reset()
    assert driver.get_position(1) == 10.0
    assert driver.snapshot()[1].fault is None


def test_command_delay_drop_and_defensive_validation():
    driver = make_driver(command_delay=0.1)
    driver.set_single_position(1, 50.0)
    assert driver.snapshot()[1].target_position == 0.0
    driver.step(0.05)
    assert driver.snapshot()[1].target_position == 0.0
    driver.step(0.05)
    assert driver.snapshot()[1].target_position == 50.0
    driver.inject_fault(2, "command_drop")
    driver.set_single_position(2, 50.0)
    assert driver.snapshot()[2].target_position == 0.0
    with pytest.raises(DriverValidationError):
        driver.step(math.nan)
    with pytest.raises(DriverValidationError):
        driver.inject_fault(1, "invented")


def test_pid_position_command_converges_on_dynamic_plant():
    driver = make_driver()
    controller = PIDController(
        PIDConfig(
            kp=1.0, ki=2.0, kd=0.01,
            output_min=0.0, output_max=100.0,
            integral_min=-100.0, integral_max=100.0,
            derivative_filter=0.8,
        )
    )
    for _ in range(600):
        command = controller.compute(80.0, driver.snapshot()[1].actual_position, 0.01)
        driver.set_single_position(1, command)
        driver.step(0.01)
    assert abs(driver.get_position(1) - 80.0) < 0.1

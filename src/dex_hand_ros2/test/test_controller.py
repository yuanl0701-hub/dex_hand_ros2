from dex_hand_ros2.driver import DriverConfig, MockMotorDriver
from dex_hand_ros2.gestures import GestureDefinition, GestureLibrary
from dex_hand_ros2.controller import HandController
from dex_hand_ros2.safety import SafetyController


def make_controller():
    config = DriverConfig()
    driver = MockMotorDriver(config=config)
    driver.connect()
    gestures = GestureLibrary(config)
    gestures.add(
        GestureDefinition("target", {motor_id: 50 for motor_id in config.motor_ids}, duration=0.1)
    )
    safety = SafetyController(config, max_rate=1e12)
    return HandController(driver, gestures, safety, sleeper=lambda _: None), driver


def test_smooth_gesture_reaches_target():
    controller, driver = make_controller()
    assert controller.run_gesture_smooth("target", sample_period=0.02)
    assert driver.snapshot() == {motor_id: 50.0 for motor_id in range(1, 7)}


def test_pid_converges_with_mock():
    controller, driver = make_controller()
    controller.configure_pid(1, 10, 0, 0)
    assert controller.set_motor_with_pid(
        1, 25, tolerance=0.5, max_iterations=200, sample_period=0.05
    )
    assert abs(driver.get_position(1) - 25) <= 0.5


def test_emergency_stop_rejects_motion_and_recovers():
    controller, _ = make_controller()
    controller.emergency_stop()
    assert not controller.run_gesture_smooth("target")
    assert controller.recover()
    assert controller.run_gesture("target")

import pytest

from dex_hand_ros2.driver import DriverConfig, MockMotorDriver
from dex_hand_ros2.driver import DriverError
from dex_hand_ros2.gestures import GestureDefinition, GestureLibrary
from dex_hand_ros2.controller import HandController
from dex_hand_ros2.safety import SafetyController
from dex_hand_ros2.safety import SafetyState


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


def test_smooth_gesture_omits_unavailable_motor_in_partial_mode():
    class PartialDriver(MockMotorDriver):
        def get_position(self, motor_id):
            if motor_id == 6:
                return None
            return super().get_position(motor_id)

        def allows_partial_operation(self):
            return True

    config = DriverConfig()
    driver = PartialDriver(config=config)
    driver.connect()
    gestures = GestureLibrary(config)
    gestures.add(
        GestureDefinition(
            "target", {motor_id: 50 for motor_id in config.motor_ids}, duration=0.1
        )
    )
    controller = HandController(
        driver,
        gestures,
        SafetyController(config, max_rate=1e12),
        sleeper=lambda _: None,
    )

    assert controller.run_gesture_smooth("target", sample_period=0.02)
    assert driver.snapshot() == {
        motor_id: (0.0 if motor_id == 6 else 50.0) for motor_id in config.motor_ids
    }


def test_smooth_gesture_rejects_unavailable_motor_in_strict_mode():
    class StrictDriver(MockMotorDriver):
        def get_position(self, motor_id):
            if motor_id == 6:
                return None
            return super().get_position(motor_id)

    config = DriverConfig()
    driver = StrictDriver(config=config)
    driver.connect()
    gestures = GestureLibrary(config)
    gestures.add(
        GestureDefinition(
            "target", {motor_id: 50 for motor_id in config.motor_ids}, duration=0.1
        )
    )
    controller = HandController(
        driver,
        gestures,
        SafetyController(config, max_rate=1e12),
        sleeper=lambda _: None,
    )

    with pytest.raises(DriverError, match="unavailable for motors: 6"):
        controller.run_gesture_smooth("target", sample_period=0.02)


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


def test_controller_watchdog_reports_stopped_after_successful_hold():
    class Clock:
        now = 0.0

        def __call__(self):
            return self.now

    clock = Clock()
    config = DriverConfig()
    driver = MockMotorDriver(config=config)
    driver.connect()
    gestures = GestureLibrary(config)
    gestures.add(GestureDefinition("target", {motor_id: 50 for motor_id in config.motor_ids}))
    safety = SafetyController(config, watchdog_timeout=1.0, max_rate=1e12, clock=clock)
    controller = HandController(driver, gestures, safety, sleeper=lambda _: None)
    assert controller.set_motor_position(1, 0)
    clock.now = 1.1

    assert not controller.check_watchdog()
    assert controller.safety.status.state is SafetyState.STOPPED

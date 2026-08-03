import struct

import pytest

from dex_hand_ros2.driver import DriverConfig, DriverError, DriverValidationError
from dex_hand_ros2.protocols import ModbusRTUProtocol
from dex_hand_ros2.real_drivers import (
    MPD20Driver,
    MPD20MotorCalibration,
    build_mpd20_calibrations,
)


class FakeTransport:
    def __init__(self, chunks):
        self.is_open = True
        self.chunks = list(chunks)
        self.writes = []

    def write(self, data):
        self.writes.append(bytes(data))
        return len(data)

    def read(self, size):
        if not self.chunks:
            return b""
        chunk = self.chunks.pop(0)
        assert len(chunk) == size
        return chunk

    def flush(self):
        pass

    def close(self):
        self.is_open = False


def modbus_frame(body):
    return body + struct.pack("<H", ModbusRTUProtocol.crc(body))


def response_chunks(body):
    response = modbus_frame(body)
    return [response[:3], response[3:]]


def make_driver(transport, *, calibration=None, motion_enabled=True):
    config = DriverConfig((1,))
    return MPD20Driver(
        "fake",
        config=config,
        calibrations={1: calibration or MPD20MotorCalibration()},
        motion_enabled=motion_enabled,
        verify_on_connect=False,
        hold_on_connect=False,
        transport_factory=lambda *_: transport,
    )


def test_position_mapping_and_feedback_function_code():
    speed_body = bytes.fromhex("01060003000a")
    write_body = bytes.fromhex("0106000201e5")
    read_body = bytes.fromhex("01040201e5")
    transport = FakeTransport(
        [
            *response_chunks(speed_body),
            *response_chunks(write_body),
            *response_chunks(read_body),
        ]
    )
    driver = make_driver(transport)
    assert driver.connect()

    assert driver.set_single_position(1, 50.0)
    assert driver.get_position(1) == pytest.approx(50.0)
    assert transport.writes[0][:6] == speed_body
    assert transport.writes[1][:6] == write_body
    assert transport.writes[2][:6] == bytes.fromhex("010400020001")


def test_reversed_mapping_and_motion_gate():
    calibration = MPD20MotorCalibration(120, 850, -1, 10)
    driver = make_driver(FakeTransport([]), calibration=calibration)
    assert driver.position_to_raw(1, 0.0) == 850
    assert driver.position_to_raw(1, 100.0) == 120
    assert driver.raw_to_position(1, 850) == pytest.approx(0.0)
    assert driver.raw_to_position(1, 120) == pytest.approx(100.0)
    with pytest.raises(DriverError, match="outside calibrated"):
        driver.raw_to_position(1, 119)

    disabled = make_driver(FakeTransport([]), motion_enabled=False)
    assert disabled.connect()
    with pytest.raises(DriverValidationError, match="motion is disabled"):
        disabled.set_single_position(1, 50)


def test_verify_on_connect_reads_complete_telemetry_block():
    values = [1, 5, 485, 0, 20, 0, 0, 0]
    payload = b"".join(struct.pack(">H", value) for value in values)
    body = bytes([1, 4, len(payload)]) + payload
    transport = FakeTransport(response_chunks(body))
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1,)),
        motion_enabled=False,
        verify_on_connect=True,
        hold_on_connect=False,
        transport_factory=lambda *_: transport,
    )

    assert driver.connect()
    assert transport.writes[0][:6] == bytes.fromhex("010400000008")


def test_active_hold_rewrites_measured_raw_position():
    speed_body = bytes.fromhex("01060003000a")
    read_body = bytes.fromhex("01040201f4")
    hold_body = bytes.fromhex("0106000201f4")
    transport = FakeTransport(
        [
            *response_chunks(speed_body),
            *response_chunks(read_body),
            *response_chunks(hold_body),
        ]
    )
    driver = make_driver(transport)
    assert driver.connect()
    assert driver.hold_current_position()
    assert transport.writes[1][:6] == bytes.fromhex("010400020001")
    assert transport.writes[2][:6] == hold_body


def test_connect_rejects_feedback_outside_calibration():
    values = [1, 5, 900, 0, 20, 0, 0, 0]
    payload = b"".join(struct.pack(">H", value) for value in values)
    body = bytes([1, 4, len(payload)]) + payload
    transport = FakeTransport(response_chunks(body))
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1,)),
        motion_enabled=False,
        verify_on_connect=True,
        hold_on_connect=False,
        transport_factory=lambda *_: transport,
    )

    with pytest.raises(DriverError, match="outside calibrated"):
        driver.connect()
    assert not driver.is_connected()


def test_connect_can_require_stationary_actuators():
    values = [1, 5, 485, 0, 20, 0, 0, 1]
    payload = b"".join(struct.pack(">H", value) for value in values)
    body = bytes([1, 4, len(payload)]) + payload
    transport = FakeTransport(response_chunks(body))
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1,)),
        motion_enabled=False,
        verify_on_connect=True,
        hold_on_connect=False,
        require_stationary_on_connect=True,
        transport_factory=lambda *_: transport,
    )

    with pytest.raises(DriverError, match="moving during startup"):
        driver.connect()
    assert not driver.is_connected()


def test_moving_startup_requests_hold_before_disconnect_when_motion_enabled():
    values = [1, 5, 500, 0, 20, 0, 0, 1]
    payload = b"".join(struct.pack(">H", value) for value in values)
    telemetry_body = bytes([1, 4, len(payload)]) + payload
    read_body = bytes.fromhex("01040201f4")
    hold_body = bytes.fromhex("0106000201f4")
    transport = FakeTransport(
        [
            *response_chunks(telemetry_body),
            *response_chunks(read_body),
            *response_chunks(hold_body),
        ]
    )
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1,)),
        motion_enabled=True,
        verify_on_connect=True,
        hold_on_connect=True,
        require_stationary_on_connect=True,
        transport_factory=lambda *_: transport,
    )

    with pytest.raises(DriverError, match="moving during startup"):
        driver.connect()
    assert transport.writes[1][:6] == bytes.fromhex("010400020001")
    assert transport.writes[2][:6] == hold_body
    assert not driver.is_connected()


def test_calibration_array_validation():
    calibrations = build_mpd20_calibrations([1, 2], [120, 130], [800, 810], [1, -1], [10, 20])
    assert calibrations[2] == MPD20MotorCalibration(130, 810, -1, 20)
    with pytest.raises(DriverValidationError, match="must match"):
        build_mpd20_calibrations([1, 2], [120], [850, 850], [1, 1], [10, 10])


def test_logical_axis_can_map_to_a_different_physical_device_id():
    read_body = bytes.fromhex("2a040201e5")
    transport = FakeTransport(response_chunks(read_body))
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1,)),
        device_ids={1: 42},
        motion_enabled=False,
        verify_on_connect=False,
        transport_factory=lambda *_: transport,
    )

    assert driver.connect()
    assert driver.get_position(1) == pytest.approx(50.0)
    assert transport.writes[0][0] == 42


def test_mpd20_device_mapping_rejects_duplicates_and_wrong_logical_keys():
    with pytest.raises(DriverValidationError, match="exactly match"):
        MPD20Driver("fake", config=DriverConfig((1, 2)), device_ids={1: 10})
    with pytest.raises(DriverValidationError, match="unique"):
        MPD20Driver(
            "fake",
            config=DriverConfig((1, 2)),
            device_ids={1: 10, 2: 10},
        )

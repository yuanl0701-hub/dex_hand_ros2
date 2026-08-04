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


class AddressAwareTransport:
    """Respond by Modbus address so one device can fail without ending the bus."""

    def __init__(self, failing_ids=()):
        self.is_open = True
        self.failing_ids = set(failing_ids)
        self.positions = {1: 485, 2: 485, 3: 485}
        self.writes = []
        self.buffer = bytearray()

    def write(self, data):
        request = bytes(data)
        self.writes.append(request)
        address = request[0]
        function = request[1]
        self.buffer.clear()
        if address in self.failing_ids:
            return len(request)
        if function == 6:
            register, value = struct.unpack(">HH", request[2:6])
            if register == MPD20Driver.TARGET_POSITION_REGISTER:
                self.positions[address] = value
            self.buffer.extend(request)
        elif function == 4:
            register, count = struct.unpack(">HH", request[2:6])
            if register == 0 and count == MPD20Driver.TELEMETRY_REGISTER_COUNT:
                values = [1, 5, self.positions[address], 0, 20, 0, 0, 0]
            elif register == MPD20Driver.PRESENT_POSITION_REGISTER and count == 1:
                values = [self.positions[address]]
            else:
                raise AssertionError(f"unexpected function-04 request: {request.hex()}")
            payload = b"".join(struct.pack(">H", value) for value in values)
            self.buffer.extend(modbus_frame(bytes([address, function, len(payload)]) + payload))
        else:
            raise AssertionError(f"unexpected Modbus function: {function}")
        return len(request)

    def read(self, size):
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

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


def test_partial_operation_quarantines_failed_axis_and_continues_batch():
    transport = AddressAwareTransport(failing_ids={2})
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1, 2, 3)),
        motion_enabled=True,
        verify_on_connect=True,
        hold_on_connect=True,
        require_stationary_on_connect=True,
        allow_partial_operation=True,
        retries=1,
        transport_factory=lambda *_: transport,
    )

    assert driver.connect()
    assert driver.unavailable_motor_ids == (2,)
    assert driver.motor_failure_counts[2] >= 1

    before = len(transport.writes)
    assert driver.set_multiple_positions({1: 25, 2: 25, 3: 25})
    command_writes = transport.writes[before:]
    target_addresses = [
        request[0]
        for request in command_writes
        if request[1] == 6
        and struct.unpack(">H", request[2:4])[0] == MPD20Driver.TARGET_POSITION_REGISTER
    ]
    assert target_addresses == [1, 3]
    assert driver.is_motor_available(1)
    assert not driver.is_motor_available(2)
    assert driver.is_motor_available(3)


def test_partial_operation_rejoins_motor_after_feedback_recovers():
    transport = AddressAwareTransport(failing_ids={2})
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1, 2, 3)),
        motion_enabled=True,
        verify_on_connect=True,
        hold_on_connect=False,
        allow_partial_operation=True,
        retries=0,
        transport_factory=lambda *_: transport,
    )

    assert driver.connect()
    assert driver.get_position(2) is None
    assert driver.unavailable_motor_ids == (2,)

    transport.failing_ids.clear()
    assert driver.get_position(2) == pytest.approx(50.0)
    assert driver.unavailable_motor_ids == ()
    assert driver.set_multiple_positions({1: 40, 2: 40, 3: 40})
    assert driver.is_motor_available(2)


def test_partial_operation_still_rejects_startup_when_every_axis_is_missing():
    transport = AddressAwareTransport(failing_ids={1, 2, 3})
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1, 2, 3)),
        motion_enabled=False,
        verify_on_connect=True,
        hold_on_connect=False,
        allow_partial_operation=True,
        retries=0,
        transport_factory=lambda *_: transport,
    )

    with pytest.raises(DriverError, match="no MPD20 actuator responded"):
        driver.connect()
    assert not driver.is_connected()


def test_partial_operation_keeps_emergency_hold_strict():
    transport = AddressAwareTransport(failing_ids={2})
    driver = MPD20Driver(
        "fake",
        config=DriverConfig((1, 2, 3)),
        motion_enabled=True,
        verify_on_connect=True,
        hold_on_connect=False,
        allow_partial_operation=True,
        retries=0,
        transport_factory=lambda *_: transport,
    )

    assert driver.connect()
    with pytest.raises(DriverError, match="MPD20 hold failed.*2"):
        driver.hold_current_position()

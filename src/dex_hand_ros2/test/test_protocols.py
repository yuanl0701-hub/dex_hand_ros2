import struct

import pytest

from dex_hand_ros2.driver import DriverError
from dex_hand_ros2.protocols import FeetechProtocol, ModbusRTUProtocol


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


def test_modbus_crc_known_vector():
    request = bytes.fromhex("01030000000a")
    assert ModbusRTUProtocol.crc(request) == 0xCDC5


def test_modbus_read_and_response_validation():
    response = modbus_frame(bytes([1, 3, 2, 0, 42]))
    transport = FakeTransport([response[:3], response[3:]])
    protocol = ModbusRTUProtocol("fake", 115200, transport_factory=lambda *_: transport)
    assert protocol.connect()
    assert protocol.read_holding_registers(1, 2) == [42]
    assert transport.writes[0][:6] == bytes.fromhex("010300020001")


def test_modbus_read_input_registers_uses_function_04():
    response = modbus_frame(bytes([1, 4, 2, 0x01, 0xE5]))
    transport = FakeTransport([response[:3], response[3:]])
    protocol = ModbusRTUProtocol("fake", 115200, transport_factory=lambda *_: transport)
    assert protocol.connect()
    assert protocol.read_input_registers(1, 2) == [485]
    assert transport.writes[0][:6] == bytes.fromhex("010400020001")


def test_modbus_rejects_crc_and_wrong_address():
    bad_crc = bytes([1, 3, 2, 0, 42, 0, 0])
    protocol = ModbusRTUProtocol(
        "fake",
        115200,
        retries=0,
        transport_factory=lambda *_: FakeTransport([bad_crc[:3], bad_crc[3:]]),
    )
    protocol.connect()
    with pytest.raises(DriverError, match="CRC"):
        protocol.read_holding_registers(1, 2)

    wrong_address = modbus_frame(bytes([2, 3, 2, 0, 42]))
    protocol = ModbusRTUProtocol(
        "fake",
        115200,
        retries=0,
        transport_factory=lambda *_: FakeTransport([wrong_address[:3], wrong_address[3:]]),
    )
    protocol.connect()
    with pytest.raises(DriverError, match="address"):
        protocol.read_holding_registers(1, 2)


def test_modbus_write_echo():
    response = modbus_frame(bytes.fromhex("01060002004d"))
    transport = FakeTransport([response[:3], response[3:]])
    protocol = ModbusRTUProtocol("fake", 115200, transport_factory=lambda *_: transport)
    protocol.connect()
    assert protocol.write_single_register(1, 2, 77)


def test_modbus_exception_frame():
    response = modbus_frame(bytes([1, 0x83, 2]))
    transport = FakeTransport([response[:3], response[3:]])
    protocol = ModbusRTUProtocol("fake", 115200, transport_factory=lambda *_: transport)
    protocol.connect()
    with pytest.raises(DriverError, match="exception code 2"):
        protocol.read_holding_registers(1, 2)


def test_feetech_packet_and_status_response():
    parameters = bytes([0x34, 0x12])
    length = len(parameters) + 2
    checksum = FeetechProtocol.checksum(1, length, [0, *parameters])
    transport = FakeTransport([bytes([0xFF, 0xFF, 1, length]), bytes([0, *parameters, checksum])])
    protocol = FeetechProtocol("fake", 115200, transport_factory=lambda *_: transport)
    protocol.connect()
    status, result = protocol.request(1, FeetechProtocol.INST_READ, [0x38, 2])
    assert status == 0
    assert result == parameters


def test_feetech_rejects_checksum():
    transport = FakeTransport([bytes([0xFF, 0xFF, 1, 2]), bytes([0, 0])])
    protocol = FeetechProtocol("fake", 115200, transport_factory=lambda *_: transport)
    protocol.connect()
    with pytest.raises(DriverError, match="checksum"):
        protocol.request(1, FeetechProtocol.INST_WRITE, [1, 2])

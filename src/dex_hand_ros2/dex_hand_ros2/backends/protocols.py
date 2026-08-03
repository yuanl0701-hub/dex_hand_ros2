"""Serial protocols with injectable transports for deterministic testing."""

from __future__ import annotations

import struct
from threading import RLock
from typing import Callable, Protocol, Sequence

from ..core.driver import DriverError, DriverNotConnectedError, DriverValidationError


class ByteTransport(Protocol):
    is_open: bool

    def write(self, data: bytes) -> int: ...
    def read(self, size: int) -> bytes: ...
    def flush(self) -> None: ...
    def close(self) -> None: ...


TransportFactory = Callable[[str, int, float], ByteTransport]


def default_serial_factory(port: str, baudrate: int, timeout: float) -> ByteTransport:
    """Create pyserial lazily so pure modules work without the dependency."""
    try:
        import serial  # type: ignore[import-untyped]
    except ImportError as exc:
        raise DriverError("pyserial is required for a real serial backend") from exc
    return serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=timeout,
    )


class ModbusRTUProtocol:
    """Minimal Modbus RTU register client with strict response validation."""

    def __init__(
        self,
        port: str,
        baudrate: int,
        *,
        timeout: float = 0.3,
        retries: int = 1,
        transport_factory: TransportFactory = default_serial_factory,
    ) -> None:
        if not port:
            raise DriverValidationError("serial port must not be empty")
        if baudrate <= 0 or timeout <= 0 or retries < 0:
            raise DriverValidationError("invalid serial timeout, baud rate, or retries")
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.retries = retries
        self._factory = transport_factory
        self._transport: ByteTransport | None = None
        self._lock = RLock()

    def connect(self) -> bool:
        try:
            self._transport = self._factory(self.port, self.baudrate, self.timeout)
        except Exception as exc:
            raise DriverError(f"failed to open serial port {self.port}: {exc}") from exc
        return self.is_connected()

    def disconnect(self) -> None:
        with self._lock:
            if self._transport is not None:
                try:
                    self._transport.close()
                finally:
                    self._transport = None

    def is_connected(self) -> bool:
        return self._transport is not None and self._transport.is_open

    @staticmethod
    def crc(data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc

    @classmethod
    def frame(cls, address: int, function: int, payload: bytes) -> bytes:
        if not 1 <= address <= 247:
            raise DriverValidationError("Modbus address must be in [1, 247]")
        body = struct.pack(">BB", address, function) + payload
        return body + struct.pack("<H", cls.crc(body))

    def _exchange(self, request: bytes, response_length: int) -> bytes:
        if not self.is_connected() or self._transport is None:
            raise DriverNotConnectedError("serial transport is not connected")
        last_error: DriverError | None = None
        with self._lock:
            for _ in range(self.retries + 1):
                written = self._transport.write(request)
                self._transport.flush()
                if written != len(request):
                    last_error = DriverError("short serial write")
                    continue
                header = self._transport.read(3)
                if len(header) != 3:
                    last_error = DriverError(f"short response header: {len(header)} of 3 bytes")
                    continue
                tail_length = 2 if header[1] & 0x80 else response_length - 3
                tail = self._transport.read(tail_length)
                response = header + tail
                if len(tail) != tail_length:
                    last_error = DriverError(
                        f"short response: {len(response)} of {3 + tail_length} bytes"
                    )
                    continue
                received_crc = struct.unpack("<H", response[-2:])[0]
                if self.crc(response[:-2]) != received_crc:
                    last_error = DriverError("response CRC mismatch")
                    continue
                if header[1] & 0x80:
                    raise DriverError(f"Modbus exception code {header[2]}")
                return response
        raise last_error or DriverError("serial exchange failed")

    def _read_registers(
        self,
        address: int,
        register: int,
        count: int,
        *,
        function: int,
    ) -> list[int]:
        if not 0 <= register <= 0xFFFF or not 1 <= count <= 125:
            raise DriverValidationError("invalid register or register count")
        request = self.frame(address, function, struct.pack(">HH", register, count))
        response = self._exchange(request, 5 + 2 * count)
        self._validate_header(response, address, function)
        if response[2] != 2 * count:
            raise DriverError("Modbus byte count mismatch")
        return [
            struct.unpack(">H", response[offset : offset + 2])[0]
            for offset in range(3, 3 + 2 * count, 2)
        ]

    def read_holding_registers(self, address: int, register: int, count: int = 1) -> list[int]:
        """Read function-03 configuration/command registers."""
        return self._read_registers(address, register, count, function=0x03)

    def read_input_registers(self, address: int, register: int, count: int = 1) -> list[int]:
        """Read function-04 telemetry registers."""
        return self._read_registers(address, register, count, function=0x04)

    def write_single_register(self, address: int, register: int, value: int) -> bool:
        if not 0 <= register <= 0xFFFF or not 0 <= value <= 0xFFFF:
            raise DriverValidationError("invalid register or value")
        payload = struct.pack(">HH", register, value)
        request = self.frame(address, 0x06, payload)
        response = self._exchange(request, 8)
        self._validate_header(response, address, 0x06)
        if response[2:6] != payload:
            raise DriverError("Modbus write echo mismatch")
        return True

    @staticmethod
    def _validate_header(response: bytes, address: int, function: int) -> None:
        if response[0] != address:
            raise DriverError("response address mismatch")
        if response[1] == function | 0x80:
            raise DriverError(f"Modbus exception code {response[2]}")
        if response[1] != function:
            raise DriverError("response function mismatch")


class FeetechProtocol:
    """Feetech packet encoder/decoder with response checksum validation."""

    HEADER = b"\xff\xff"
    INST_READ = 0x02
    INST_WRITE = 0x03

    def __init__(
        self,
        port: str,
        baudrate: int,
        *,
        timeout: float = 0.1,
        transport_factory: TransportFactory = default_serial_factory,
    ) -> None:
        if not port or baudrate <= 0 or timeout <= 0:
            raise DriverValidationError("invalid Feetech serial configuration")
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._factory = transport_factory
        self._transport: ByteTransport | None = None
        self._lock = RLock()

    @staticmethod
    def checksum(servo_id: int, length: int, fields: Sequence[int]) -> int:
        return (~(servo_id + length + sum(fields))) & 0xFF

    @classmethod
    def frame(cls, servo_id: int, instruction: int, parameters: Sequence[int]) -> bytes:
        if not 1 <= servo_id <= 253:
            raise DriverValidationError("Feetech ID must be in [1, 253]")
        if any(not 0 <= value <= 255 for value in parameters):
            raise DriverValidationError("Feetech parameters must be bytes")
        length = len(parameters) + 2
        fields = [instruction, *parameters]
        return bytes(
            [0xFF, 0xFF, servo_id, length, *fields, cls.checksum(servo_id, length, fields)]
        )

    def connect(self) -> bool:
        try:
            self._transport = self._factory(self.port, self.baudrate, self.timeout)
        except Exception as exc:
            raise DriverError(f"failed to open serial port {self.port}: {exc}") from exc
        return self.is_connected()

    def disconnect(self) -> None:
        with self._lock:
            if self._transport is not None:
                try:
                    self._transport.close()
                finally:
                    self._transport = None

    def is_connected(self) -> bool:
        return self._transport is not None and self._transport.is_open

    def request(
        self, servo_id: int, instruction: int, parameters: Sequence[int]
    ) -> tuple[int, bytes]:
        if not self.is_connected() or self._transport is None:
            raise DriverNotConnectedError("serial transport is not connected")
        request = self.frame(servo_id, instruction, parameters)
        with self._lock:
            if self._transport.write(request) != len(request):
                raise DriverError("short serial write")
            self._transport.flush()
            header = self._transport.read(4)
            if len(header) != 4 or header[:2] != self.HEADER:
                raise DriverError("invalid or short Feetech response header")
            response_id, length = header[2], header[3]
            payload = self._transport.read(length)
        if response_id != servo_id or len(payload) != length or length < 2:
            raise DriverError("invalid Feetech response metadata")
        status = payload[0]
        parameters_out = payload[1:-1]
        expected = self.checksum(response_id, length, [status, *parameters_out])
        if payload[-1] != expected:
            raise DriverError("Feetech checksum mismatch")
        if status != 0:
            raise DriverError(f"Feetech status error 0x{status:02x}")
        return status, parameters_out

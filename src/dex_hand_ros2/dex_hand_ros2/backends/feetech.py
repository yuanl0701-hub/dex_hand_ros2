"""Feetech hardware adapter."""

from __future__ import annotations

from typing import Optional

from ..core.driver import DriverConfig, DriverValidationError, GenericMotorDriver
from .protocols import FeetechProtocol, TransportFactory, default_serial_factory


class FeetechDriver(GenericMotorDriver):
    """Feetech adapter that requires a valid status response for every write."""

    ADDR_ID = 0x05
    ADDR_BAUDRATE = 0x06
    ADDR_GOAL_POSITION = 0x2A
    ADDR_PRESENT_POSITION = 0x38
    RAW_MAX = 4095
    BAUD_MAP = {115200: 7, 38400: 4, 19200: 3, 9600: 1}

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        *,
        timeout: float = 0.1,
        config: DriverConfig | None = None,
        transport_factory: TransportFactory = default_serial_factory,
    ) -> None:
        super().__init__(config)
        self._protocol = FeetechProtocol(
            port, baudrate, timeout=timeout, transport_factory=transport_factory
        )

    def connect(self) -> bool:
        return self._protocol.connect()

    def disconnect(self) -> None:
        self._protocol.disconnect()

    def is_connected(self) -> bool:
        return self._protocol.is_connected()

    def _to_raw(self, position: float) -> int:
        span = self.config.position_max - self.config.position_min
        return int(round((position - self.config.position_min) / span * self.RAW_MAX))

    def _from_raw(self, raw: int) -> float:
        span = self.config.position_max - self.config.position_min
        return self.config.position_min + raw / self.RAW_MAX * span

    def set_single_position(self, motor_id: int, position: float) -> bool:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        self.config.validate_position(position)
        raw = self._to_raw(position)
        self._protocol.request(
            motor_id,
            FeetechProtocol.INST_WRITE,
            [self.ADDR_GOAL_POSITION, raw & 0xFF, (raw >> 8) & 0xFF],
        )
        return True

    def get_position(self, motor_id: int) -> Optional[float]:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        _, payload = self._protocol.request(
            motor_id,
            FeetechProtocol.INST_READ,
            [self.ADDR_PRESENT_POSITION, 2],
        )
        if len(payload) != 2:
            return None
        return self._from_raw(payload[0] | payload[1] << 8)

    def change_id(self, old_id: int, new_id: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(old_id)
        if not 1 <= new_id <= 253:
            raise DriverValidationError("new Feetech ID must be in [1, 253]")
        self._protocol.request(old_id, FeetechProtocol.INST_WRITE, [self.ADDR_ID, new_id])
        return True

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(target_id)
        if new_baud not in self.BAUD_MAP:
            raise DriverValidationError(f"unsupported Feetech baud rate: {new_baud}")
        self._protocol.request(
            target_id,
            FeetechProtocol.INST_WRITE,
            [self.ADDR_BAUDRATE, self.BAUD_MAP[new_baud]],
        )
        return True

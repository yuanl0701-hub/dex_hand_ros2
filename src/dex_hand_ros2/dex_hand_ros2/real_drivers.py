"""Real serial backends. Register maps remain explicit and auditable."""

from __future__ import annotations

from typing import Optional

from .driver import DriverConfig, DriverValidationError, GenericMotorDriver
from .protocols import FeetechProtocol, ModbusRTUProtocol, TransportFactory, default_serial_factory


class MPD20Driver(GenericMotorDriver):
    """MPD20 adapter based on the register map preserved in the project snapshot."""

    BAUD_MAP = {115200: 4, 38400: 7, 19200: 8, 9600: 9, 4800: 10}
    ID_REGISTER = 0x0000
    BAUD_REGISTER = 0x0001
    POSITION_REGISTER = 0x0002

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        *,
        timeout: float = 0.3,
        retries: int = 1,
        config: DriverConfig | None = None,
        transport_factory: TransportFactory = default_serial_factory,
    ) -> None:
        super().__init__(config)
        self._protocol = ModbusRTUProtocol(
            port,
            baudrate,
            timeout=timeout,
            retries=retries,
            transport_factory=transport_factory,
        )

    def connect(self) -> bool:
        return self._protocol.connect()

    def disconnect(self) -> None:
        self._protocol.disconnect()

    def is_connected(self) -> bool:
        return self._protocol.is_connected()

    def set_single_position(self, motor_id: int, position: float) -> bool:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        self.config.validate_position(position)
        return self._protocol.write_single_register(
            motor_id, self.POSITION_REGISTER, int(round(position))
        )

    def get_position(self, motor_id: int) -> Optional[float]:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        values = self._protocol.read_holding_registers(motor_id, self.POSITION_REGISTER, 1)
        return float(values[0])

    def change_id(self, old_id: int, new_id: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(old_id)
        if not 1 <= new_id <= 247:
            raise DriverValidationError("new Modbus ID must be in [1, 247]")
        return self._protocol.write_single_register(old_id, self.ID_REGISTER, new_id)

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(target_id)
        if new_baud not in self.BAUD_MAP:
            raise DriverValidationError(f"unsupported MPD20 baud rate: {new_baud}")
        return self._protocol.write_single_register(
            target_id, self.BAUD_REGISTER, self.BAUD_MAP[new_baud]
        )


class HTS20LDriver(MPD20Driver):
    """HTS-20L position adapter.

    The recovered repository does not contain an authoritative baud-code table,
    so persistent baud changes are deliberately blocked.
    """

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        del target_id, new_baud
        raise NotImplementedError(
            "HTS-20L baud mapping is blocked pending authoritative documentation"
        )


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

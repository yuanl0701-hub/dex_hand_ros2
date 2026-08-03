"""MPD20-S hardware adapter and calibration model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional, Sequence

from ..core.driver import (
    DriverConfig,
    DriverError,
    DriverValidationError,
    GenericMotorDriver,
)
from .protocols import ModbusRTUProtocol, TransportFactory, default_serial_factory


@dataclass(frozen=True)
class MPD20MotorCalibration:
    """Per-actuator mapping from normalized hand units to MPD20 raw position."""

    raw_min: int = 120
    raw_max: int = 850
    direction: int = 1
    max_speed: int = 10

    def __post_init__(self) -> None:
        if any(
            isinstance(value, bool) or not isinstance(value, int)
            for value in (self.raw_min, self.raw_max, self.direction, self.max_speed)
        ):
            raise DriverValidationError("MPD20 calibration values must be integers")
        if not 0 <= self.raw_min < self.raw_max <= 0x03FF:
            raise DriverValidationError(
                "MPD20 raw limits must satisfy 0 <= raw_min < raw_max <= 1023"
            )
        if self.direction not in (-1, 1):
            raise DriverValidationError("MPD20 direction must be -1 or 1")
        if not 1 <= self.max_speed <= 100:
            raise DriverValidationError("MPD20 max_speed must be in [1, 100]")


@dataclass(frozen=True)
class MPD20Telemetry:
    """Function-04 input-register snapshot documented by MPD20 V1.5."""

    hardware_version: int
    software_version: int
    raw_position: int
    raw_speed: int
    raw_load: int
    raw_voltage: int
    raw_temperature: int
    moving: bool


def build_mpd20_calibrations(
    motor_ids: Sequence[int],
    raw_mins: Sequence[int],
    raw_maxs: Sequence[int],
    directions: Sequence[int],
    max_speeds: Sequence[int],
) -> dict[int, MPD20MotorCalibration]:
    """Build an ID-keyed calibration map from ROS-friendly parallel arrays."""
    arrays = (raw_mins, raw_maxs, directions, max_speeds)
    if any(len(values) != len(motor_ids) for values in arrays):
        raise DriverValidationError("MPD20 calibration arrays must match the number of motor_ids")
    return {
        int(motor_id): MPD20MotorCalibration(
            int(raw_mins[index]),
            int(raw_maxs[index]),
            int(directions[index]),
            int(max_speeds[index]),
        )
        for index, motor_id in enumerate(motor_ids)
    }


class MPD20Driver(GenericMotorDriver):
    """MPD20-S RS-485 adapter using the vendor's Modbus RTU register map."""

    BAUD_MAP = {115200: 4, 38400: 7, 19200: 8, 9600: 9, 4800: 10}
    ID_REGISTER = 0x0000
    BAUD_REGISTER = 0x0001
    TARGET_POSITION_REGISTER = 0x0002
    MAX_SPEED_REGISTER = 0x0003
    PRESENT_POSITION_REGISTER = 0x0002
    TELEMETRY_REGISTER_COUNT = 8

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        *,
        timeout: float = 0.3,
        retries: int = 1,
        config: DriverConfig | None = None,
        calibrations: Mapping[int, MPD20MotorCalibration] | None = None,
        device_ids: Mapping[int, int] | None = None,
        motion_enabled: bool = True,
        verify_on_connect: bool = False,
        hold_on_connect: bool = False,
        require_stationary_on_connect: bool = False,
        transport_factory: TransportFactory = default_serial_factory,
    ) -> None:
        super().__init__(config)
        if calibrations is None:
            self.calibrations = {
                motor_id: MPD20MotorCalibration() for motor_id in self.config.motor_ids
            }
        else:
            self.calibrations = dict(calibrations)
            if set(self.calibrations) != set(self.config.motor_ids):
                raise DriverValidationError(
                    "MPD20 calibration IDs must exactly match configured motor IDs"
                )
        self.device_ids = (
            {motor_id: motor_id for motor_id in self.config.motor_ids}
            if device_ids is None
            else {int(logical_id): int(device_id) for logical_id, device_id in device_ids.items()}
        )
        if set(self.device_ids) != set(self.config.motor_ids):
            raise DriverValidationError(
                "MPD20 device-ID mapping must exactly match configured logical motor IDs"
            )
        physical_ids = tuple(self.device_ids.values())
        if (
            len(set(physical_ids)) != len(physical_ids)
            or any(not 1 <= device_id <= 247 for device_id in physical_ids)
        ):
            raise DriverValidationError("MPD20 physical device IDs must be unique in [1, 247]")
        self.motion_enabled = bool(motion_enabled)
        self.verify_on_connect = bool(verify_on_connect)
        self.hold_on_connect = bool(hold_on_connect)
        self.require_stationary_on_connect = bool(require_stationary_on_connect)
        if self.require_stationary_on_connect and not self.verify_on_connect:
            raise DriverValidationError("require_stationary_on_connect requires verify_on_connect")
        self._protocol = ModbusRTUProtocol(
            port,
            baudrate,
            timeout=timeout,
            retries=retries,
            transport_factory=transport_factory,
        )

    def connect(self) -> bool:
        if not self._protocol.connect():
            return False
        try:
            if self.verify_on_connect:
                moving_ids: list[int] = []
                for motor_id in self.config.motor_ids:
                    telemetry = self.read_telemetry(motor_id)
                    self.raw_to_position(motor_id, telemetry.raw_position)
                    if telemetry.moving:
                        moving_ids.append(motor_id)
                if self.require_stationary_on_connect and moving_ids:
                    if self.motion_enabled and self.hold_on_connect:
                        self.hold_current_position()
                    raise DriverError(
                        "MPD20 actuators moving during startup: "
                        + ", ".join(str(motor_id) for motor_id in moving_ids)
                    )
            if self.motion_enabled:
                if self.hold_on_connect:
                    self.hold_current_position()
                for motor_id in self.config.motor_ids:
                    self.set_max_speed(motor_id, self.calibrations[motor_id].max_speed)
        except Exception:
            self._protocol.disconnect()
            raise
        return True

    def disconnect(self) -> None:
        self._protocol.disconnect()

    def is_connected(self) -> bool:
        return self._protocol.is_connected()

    def set_single_position(self, motor_id: int, position: float) -> bool:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        self.config.validate_position(position)
        return self.set_raw_position(motor_id, self.position_to_raw(motor_id, position))

    def set_raw_position(self, motor_id: int, raw_position: int) -> bool:
        """Write a calibrated raw target; intended for bounded commissioning."""
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        if not self.motion_enabled:
            raise DriverValidationError(
                "MPD20 motion is disabled; complete calibration and set "
                "hardware_motion_enabled=true"
            )
        if isinstance(raw_position, bool) or not isinstance(raw_position, int):
            raise DriverValidationError("MPD20 raw position must be an integer")
        calibration = self.calibrations[motor_id]
        if not calibration.raw_min <= raw_position <= calibration.raw_max:
            raise DriverValidationError(
                f"motor {motor_id} raw target {raw_position} outside calibrated "
                f"range [{calibration.raw_min}, {calibration.raw_max}]"
            )
        return self._protocol.write_single_register(
            self._device_id(motor_id),
            self.TARGET_POSITION_REGISTER,
            raw_position,
        )

    def get_position(self, motor_id: int) -> Optional[float]:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        values = self._protocol.read_input_registers(
            self._device_id(motor_id), self.PRESENT_POSITION_REGISTER, 1
        )
        return self.raw_to_position(motor_id, values[0])

    def read_telemetry(self, motor_id: int) -> MPD20Telemetry:
        """Read the complete documented function-04 telemetry block."""
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        values = self._protocol.read_input_registers(
            self._device_id(motor_id), 0, self.TELEMETRY_REGISTER_COUNT
        )
        return MPD20Telemetry(
            hardware_version=values[0],
            software_version=values[1],
            raw_position=values[2],
            raw_speed=values[3],
            raw_load=values[4],
            raw_voltage=values[5],
            raw_temperature=values[6],
            moving=bool(values[7]),
        )

    def position_to_raw(self, motor_id: int, position: float) -> int:
        """Convert one validated normalized command into a calibrated raw value."""
        self.config.validate_motor_id(motor_id)
        self.config.validate_position(position)
        calibration = self.calibrations[motor_id]
        logical_span = self.config.position_max - self.config.position_min
        ratio = (float(position) - self.config.position_min) / logical_span
        if calibration.direction == -1:
            ratio = 1.0 - ratio
        raw = calibration.raw_min + ratio * (calibration.raw_max - calibration.raw_min)
        return int(round(raw))

    def raw_to_position(self, motor_id: int, raw_position: int) -> float:
        """Convert MPD20 feedback into the common normalized command domain."""
        self.config.validate_motor_id(motor_id)
        calibration = self.calibrations[motor_id]
        if not calibration.raw_min <= raw_position <= calibration.raw_max:
            raise DriverError(
                f"motor {motor_id} raw position {raw_position} outside calibrated "
                f"range [{calibration.raw_min}, {calibration.raw_max}]"
            )
        ratio = (raw_position - calibration.raw_min) / (calibration.raw_max - calibration.raw_min)
        if calibration.direction == -1:
            ratio = 1.0 - ratio
        return self.config.position_min + ratio * (
            self.config.position_max - self.config.position_min
        )

    def set_max_speed(self, motor_id: int, max_speed: int) -> bool:
        """Set the MPD20 holding-register speed limit (vendor scale 1..100)."""
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        if isinstance(max_speed, bool) or not isinstance(max_speed, int):
            raise DriverValidationError("MPD20 max_speed must be an integer")
        if not 1 <= max_speed <= 100:
            raise DriverValidationError("MPD20 max_speed must be in [1, 100]")
        return self._protocol.write_single_register(
            self._device_id(motor_id), self.MAX_SPEED_REGISTER, max_speed
        )

    def hold_current_position(self) -> bool:
        """Stop commanded travel by rewriting each measured raw position."""
        self._require_connected()
        if not self.motion_enabled:
            return True
        failures: list[str] = []
        for motor_id in self.config.motor_ids:
            try:
                raw_position = self._protocol.read_input_registers(
                    self._device_id(motor_id), self.PRESENT_POSITION_REGISTER, 1
                )[0]
                self._protocol.write_single_register(
                    self._device_id(motor_id), self.TARGET_POSITION_REGISTER, raw_position
                )
            except Exception as exc:
                failures.append(f"{motor_id}: {exc}")
        if failures:
            raise DriverError("MPD20 hold failed for " + "; ".join(failures))
        return True

    def change_id(self, old_id: int, new_id: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(old_id)
        if not 1 <= new_id <= 247:
            raise DriverValidationError("new Modbus ID must be in [1, 247]")
        if new_id in self.device_ids.values():
            raise DriverValidationError("new Modbus ID is already present in the deployment")
        changed = self._protocol.write_single_register(
            self._device_id(old_id), self.ID_REGISTER, new_id
        )
        if changed:
            self.device_ids[old_id] = new_id
        return changed

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(target_id)
        if new_baud not in self.BAUD_MAP:
            raise DriverValidationError(f"unsupported MPD20 baud rate: {new_baud}")
        return self._protocol.write_single_register(
            self._device_id(target_id), self.BAUD_REGISTER, self.BAUD_MAP[new_baud]
        )

    def _device_id(self, logical_motor_id: int) -> int:
        """Resolve a reusable logical axis to this hand's physical bus address."""

        self.config.validate_motor_id(logical_motor_id)
        return self.device_ids[logical_motor_id]

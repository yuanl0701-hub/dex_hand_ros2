"""Hardware-independent driver contract and deterministic in-memory backend."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import math
from threading import RLock
from typing import Mapping, Optional, Sequence


class DriverError(RuntimeError):
    """Base class for motor-driver failures."""


class DriverNotConnectedError(DriverError):
    """Raised when an operation requires an active connection."""


class DriverValidationError(ValueError):
    """Raised when a command is outside the configured logical domain."""


@dataclass(frozen=True)
class DriverConfig:
    """Logical motor configuration in normalized-percent units."""

    motor_ids: tuple[int, ...] = (1, 2, 3, 4, 5, 6)
    position_min: float = 0.0
    position_max: float = 100.0

    def __post_init__(self) -> None:
        if not self.motor_ids or len(set(self.motor_ids)) != len(self.motor_ids):
            raise DriverValidationError("motor_ids must be non-empty and unique")
        if any(not isinstance(motor_id, int) or motor_id <= 0 for motor_id in self.motor_ids):
            raise DriverValidationError("motor IDs must be positive integers")
        if not all(math.isfinite(value) for value in (self.position_min, self.position_max)):
            raise DriverValidationError("position limits must be finite")
        if self.position_min >= self.position_max:
            raise DriverValidationError("position_min must be less than position_max")

    def validate_motor_id(self, motor_id: int) -> None:
        if motor_id not in self.motor_ids:
            raise DriverValidationError(f"unknown motor ID: {motor_id}")

    def validate_position(self, position: float) -> None:
        if not isinstance(position, (int, float)) or not math.isfinite(float(position)):
            raise DriverValidationError("position must be finite")
        if not self.position_min <= float(position) <= self.position_max:
            raise DriverValidationError(
                f"position {position} outside [{self.position_min}, {self.position_max}]"
            )


class GenericMotorDriver(ABC):
    """Common synchronous driver interface used by controllers and ROS adapters."""

    def __init__(self, config: DriverConfig | None = None) -> None:
        self.config = config or DriverConfig()

    @abstractmethod
    def connect(self) -> bool:
        """Open required resources and report whether the backend is ready."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close resources. Calling this repeatedly must be safe."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Return whether commands may currently be issued."""

    @abstractmethod
    def set_single_position(self, motor_id: int, position: float) -> bool:
        """Set one normalized motor position."""

    def set_multiple_positions(self, positions: Mapping[int, float]) -> bool:
        """Validate all values before applying the command set."""
        self._require_connected()
        normalized = self.validate_positions(positions, require_complete=False)
        return all(
            self.set_single_position(motor_id, value) for motor_id, value in normalized.items()
        )

    @abstractmethod
    def get_position(self, motor_id: int) -> Optional[float]:
        """Read one normalized motor position, or ``None`` on communication failure."""

    def get_multiple_positions(self, motor_ids: Sequence[int]) -> dict[int, Optional[float]]:
        """Read a deterministic ordered set of positions."""
        return {motor_id: self.get_position(motor_id) for motor_id in motor_ids}

    def hold_current_position(self) -> bool:
        """Best-effort active hold used by software stop paths.

        This is not equivalent to removing actuator power. Backends with a more
        direct stop primitive should override this method.
        """
        self._require_connected()
        positions = self.get_multiple_positions(self.config.motor_ids)
        unavailable = [motor_id for motor_id, position in positions.items() if position is None]
        if unavailable:
            raise DriverError(
                "cannot hold motors with unavailable feedback: "
                + ", ".join(str(motor_id) for motor_id in unavailable)
            )
        return self.set_multiple_positions(
            {
                motor_id: float(position)
                for motor_id, position in positions.items()
                if position is not None
            }
        )

    def change_id(self, old_id: int, new_id: int) -> bool:
        """Request an optional persistent device-ID change."""
        del old_id, new_id
        raise NotImplementedError("this backend does not support persistent ID changes")

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        """Request an optional persistent baud-rate change."""
        del target_id, new_baud
        raise NotImplementedError("this backend does not support persistent baud changes")

    def validate_positions(
        self, positions: Mapping[int, float], *, require_complete: bool
    ) -> dict[int, float]:
        if not positions:
            raise DriverValidationError("position command must not be empty")
        normalized: dict[int, float] = {}
        for motor_id, position in positions.items():
            self.config.validate_motor_id(motor_id)
            self.config.validate_position(position)
            normalized[motor_id] = float(position)
        if require_complete and set(normalized) != set(self.config.motor_ids):
            raise DriverValidationError("position command must contain every configured motor")
        return {
            motor_id: normalized[motor_id]
            for motor_id in self.config.motor_ids
            if motor_id in normalized
        }

    def _require_connected(self) -> None:
        if not self.is_connected():
            raise DriverNotConnectedError("motor driver is not connected")

    def __enter__(self) -> GenericMotorDriver:
        if not self.connect():
            raise DriverError("motor driver failed to connect")
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.disconnect()


class MockMotorDriver(GenericMotorDriver):
    """Thread-safe deterministic backend with no ROS or serial dependency."""

    def __init__(
        self,
        port: str = "",
        baudrate: int = 115200,
        config: DriverConfig | None = None,
        initial_position: float = 0.0,
    ) -> None:
        del port, baudrate
        super().__init__(config)
        self.config.validate_position(initial_position)
        self._positions = {motor_id: float(initial_position) for motor_id in self.config.motor_ids}
        self._connected = False
        self._lock = RLock()

    def connect(self) -> bool:
        with self._lock:
            self._connected = True
            return True

    def disconnect(self) -> None:
        with self._lock:
            self._connected = False

    def is_connected(self) -> bool:
        with self._lock:
            return self._connected

    def set_single_position(self, motor_id: int, position: float) -> bool:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        self.config.validate_position(position)
        with self._lock:
            self._positions[motor_id] = float(position)
        return True

    def set_multiple_positions(self, positions: Mapping[int, float]) -> bool:
        self._require_connected()
        normalized = self.validate_positions(positions, require_complete=False)
        with self._lock:
            self._positions.update(normalized)
        return True

    def get_position(self, motor_id: int) -> Optional[float]:
        self._require_connected()
        self.config.validate_motor_id(motor_id)
        with self._lock:
            return self._positions[motor_id]

    def change_id(self, old_id: int, new_id: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(old_id)
        if new_id <= 0 or new_id in self._positions:
            raise DriverValidationError("new motor ID must be positive and unused")
        with self._lock:
            self._positions[new_id] = self._positions.pop(old_id)
            updated_ids = tuple(
                new_id if motor_id == old_id else motor_id for motor_id in self.config.motor_ids
            )
            self.config = DriverConfig(
                updated_ids,
                self.config.position_min,
                self.config.position_max,
            )
        return True

    def change_baudrate(self, target_id: int, new_baud: int) -> bool:
        self._require_connected()
        self.config.validate_motor_id(target_id)
        if new_baud <= 0:
            raise DriverValidationError("baud rate must be positive")
        return True

    def snapshot(self) -> dict[int, float]:
        """Return a copy for tests and experiment logging."""
        self._require_connected()
        with self._lock:
            return dict(self._positions)

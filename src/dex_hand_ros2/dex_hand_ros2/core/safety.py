"""Central hardware-independent validation, emergency-stop, and watchdog policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math
import time
from typing import Callable, Mapping

from .driver import DriverConfig, DriverValidationError


class SafetyState(str, Enum):
    READY = "ready"
    STOPPED = "stopped"
    FAULT = "fault"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True)
class SafetyStatus:
    """Observable state of the safety controller."""

    state: SafetyState
    reason: str
    last_command_time: float | None


class SafetyController:
    """Fail-safe validator using normalized positions and an injectable clock."""

    def __init__(
        self,
        config: DriverConfig,
        *,
        watchdog_timeout: float = 1.0,
        max_rate: float = 100.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if not math.isfinite(watchdog_timeout) or watchdog_timeout <= 0:
            raise ValueError("watchdog_timeout must be finite and positive")
        if not math.isfinite(max_rate) or max_rate <= 0:
            raise ValueError("max_rate must be finite and positive")
        self.config = config
        self.watchdog_timeout = watchdog_timeout
        self.max_rate = max_rate
        self._clock = clock
        self._state = SafetyState.READY
        self._reason = ""
        self._last_command_time: float | None = None
        self._last_positions: dict[int, float] = {}

    @property
    def status(self) -> SafetyStatus:
        return SafetyStatus(self._state, self._reason, self._last_command_time)

    def validate_command(
        self, positions: Mapping[int, float], *, require_complete: bool = False
    ) -> dict[int, float]:
        if self._state is not SafetyState.READY:
            raise DriverValidationError(f"commands disabled: {self._state.value}: {self._reason}")
        if not positions:
            raise DriverValidationError("position command must not be empty")

        normalized: dict[int, float] = {}
        for motor_id, position in positions.items():
            self.config.validate_motor_id(motor_id)
            self.config.validate_position(position)
            normalized[motor_id] = float(position)
        if require_complete and set(normalized) != set(self.config.motor_ids):
            raise DriverValidationError("command must contain every configured motor")

        now = self._clock()
        if self._last_command_time is not None:
            dt = now - self._last_command_time
            if dt <= 0:
                raise DriverValidationError("command clock must advance")
            for motor_id, position in normalized.items():
                if motor_id in self._last_positions:
                    rate = abs(position - self._last_positions[motor_id]) / dt
                    if rate > self.max_rate:
                        raise DriverValidationError(
                            f"motor {motor_id} rate {rate:.3f} exceeds {self.max_rate}"
                        )
        self._last_positions.update(normalized)
        self._last_command_time = now
        return normalized

    def emergency_stop(self, reason: str = "operator request") -> None:
        """Latch the stopped state."""
        if self._state in {SafetyState.READY, SafetyState.STOPPED}:
            self._state = SafetyState.STOPPED
            self._reason = reason

    def recover(self) -> bool:
        """Recover only from an operator stop, never from fault or shutdown."""
        if self._state is not SafetyState.STOPPED:
            return False
        self._state = SafetyState.READY
        self._reason = ""
        self._last_command_time = None
        self._last_positions.clear()
        return True

    def fault(self, reason: str) -> None:
        self._state = SafetyState.FAULT
        self._reason = reason

    def check_watchdog(self) -> bool:
        """Latch a stop after an established command stream becomes stale."""
        if (
            self._state is SafetyState.READY
            and self._last_command_time is not None
            and self._clock() - self._last_command_time > self.watchdog_timeout
        ):
            self.emergency_stop("command watchdog timeout")
            return False
        return self._state is SafetyState.READY

    def shutdown(self) -> None:
        self._state = SafetyState.SHUTDOWN
        self._reason = "controller shutdown"

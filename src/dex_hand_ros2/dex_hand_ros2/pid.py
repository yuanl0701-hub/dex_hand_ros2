"""Deterministic PID controller independent of wall-clock time."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PIDConfig:
    """PID gains and saturation limits."""

    kp: float = 2.0
    ki: float = 0.1
    kd: float = 0.05
    output_min: float = -100.0
    output_max: float = 100.0
    integral_min: float = -50.0
    integral_max: float = 50.0
    derivative_filter: float = 0.0

    def __post_init__(self) -> None:
        values = (
            self.kp,
            self.ki,
            self.kd,
            self.output_min,
            self.output_max,
            self.integral_min,
            self.integral_max,
            self.derivative_filter,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("PID configuration values must be finite")
        if min(self.kp, self.ki, self.kd) < 0:
            raise ValueError("PID gains must be non-negative")
        if self.output_min >= self.output_max:
            raise ValueError("output_min must be less than output_max")
        if self.integral_min >= self.integral_max:
            raise ValueError("integral_min must be less than integral_max")
        if not 0.0 <= self.derivative_filter < 1.0:
            raise ValueError("derivative_filter must be in [0, 1)")


class PIDController:
    """Positional PID with clamping anti-windup and optional derivative filtering."""

    def __init__(self, config: PIDConfig | None = None) -> None:
        self.config = config or PIDConfig()
        self.reset()

    def reset(self) -> None:
        """Clear integral and derivative history."""
        self.integral = 0.0
        self.previous_error: float | None = None
        self.filtered_derivative = 0.0

    def compute(self, setpoint: float, measurement: float, dt: float) -> float:
        """Return a saturated control effort for an explicit positive sample time."""
        if not all(math.isfinite(value) for value in (setpoint, measurement, dt)):
            raise ValueError("PID inputs must be finite")
        if dt <= 0:
            raise ValueError("dt must be positive")

        error = setpoint - measurement
        derivative = 0.0 if self.previous_error is None else (error - self.previous_error) / dt
        alpha = self.config.derivative_filter
        self.filtered_derivative = alpha * self.filtered_derivative + (1.0 - alpha) * derivative

        candidate_integral = _clamp(
            self.integral + error * dt,
            self.config.integral_min,
            self.config.integral_max,
        )
        candidate = (
            self.config.kp * error
            + self.config.ki * candidate_integral
            + self.config.kd * self.filtered_derivative
        )
        output = _clamp(candidate, self.config.output_min, self.config.output_max)

        saturation_pushes_outward = (candidate > self.config.output_max and error > 0) or (
            candidate < self.config.output_min and error < 0
        )
        if not saturation_pushes_outward:
            self.integral = candidate_integral
        self.previous_error = error
        return output


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))

"""Hardware-independent quintic trajectories in normalized motor coordinates."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping


@dataclass(frozen=True)
class TrajectoryPoint:
    time: float
    position: float
    velocity: float
    acceleration: float
    jerk: float


class QuinticTrajectory:
    """Fifth-order polynomial satisfying position, velocity, and acceleration bounds."""

    def __init__(
        self,
        start: float,
        end: float,
        duration: float,
        *,
        start_velocity: float = 0.0,
        end_velocity: float = 0.0,
        start_acceleration: float = 0.0,
        end_acceleration: float = 0.0,
    ) -> None:
        values = (
            start,
            end,
            duration,
            start_velocity,
            end_velocity,
            start_acceleration,
            end_acceleration,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("trajectory inputs must be finite")
        if duration <= 0:
            raise ValueError("duration must be positive")
        self.duration = float(duration)
        t = self.duration
        a0 = float(start)
        a1 = float(start_velocity)
        a2 = float(start_acceleration) / 2.0
        c0 = end - (a0 + a1 * t + a2 * t**2)
        c1 = end_velocity - (a1 + 2.0 * a2 * t)
        c2 = end_acceleration - 2.0 * a2
        a3 = (10.0 * c0 - 4.0 * c1 * t + 0.5 * c2 * t**2) / t**3
        a4 = (-15.0 * c0 + 7.0 * c1 * t - c2 * t**2) / t**4
        a5 = (6.0 * c0 - 3.0 * c1 * t + 0.5 * c2 * t**2) / t**5
        self.coefficients = (a0, a1, a2, a3, a4, a5)

    def evaluate(self, sample_time: float) -> TrajectoryPoint:
        if not math.isfinite(sample_time):
            raise ValueError("sample time must be finite")
        t = max(0.0, min(self.duration, float(sample_time)))
        a0, a1, a2, a3, a4, a5 = self.coefficients
        return TrajectoryPoint(
            time=t,
            position=a0 + a1 * t + a2 * t**2 + a3 * t**3 + a4 * t**4 + a5 * t**5,
            velocity=a1 + 2 * a2 * t + 3 * a3 * t**2 + 4 * a4 * t**3 + 5 * a5 * t**4,
            acceleration=2 * a2 + 6 * a3 * t + 12 * a4 * t**2 + 20 * a5 * t**3,
            jerk=6 * a3 + 24 * a4 * t + 60 * a5 * t**2,
        )

    def sample(self, sample_period: float) -> list[TrajectoryPoint]:
        if not math.isfinite(sample_period) or sample_period <= 0:
            raise ValueError("sample_period must be finite and positive")
        count = int(math.floor(self.duration / sample_period))
        times = [index * sample_period for index in range(count + 1)]
        if not math.isclose(times[-1], self.duration):
            times.append(self.duration)
        return [self.evaluate(t) for t in times]


class MultiAxisQuinticTrajectory:
    """Synchronized collection of scalar quintic trajectories."""

    def __init__(
        self, starts: Mapping[int, float], ends: Mapping[int, float], duration: float
    ) -> None:
        if not starts or set(starts) != set(ends):
            raise ValueError("start and end axes must be non-empty and identical")
        self.duration = duration
        self.axes = {
            axis: QuinticTrajectory(starts[axis], ends[axis], duration) for axis in sorted(starts)
        }

    def evaluate(self, sample_time: float) -> dict[int, TrajectoryPoint]:
        return {axis: trajectory.evaluate(sample_time) for axis, trajectory in self.axes.items()}

    def sample(self, sample_period: float) -> list[dict[int, TrajectoryPoint]]:
        reference = next(iter(self.axes.values())).sample(sample_period)
        return [self.evaluate(point.time) for point in reference]

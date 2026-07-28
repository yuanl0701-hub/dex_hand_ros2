"""Validated mapping from logical normalized motors to virtual URDF joints."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping


@dataclass(frozen=True)
class MotorJointMapping:
    motor_id: int
    joint_name: str
    normalized_min: float = 0.0
    normalized_max: float = 100.0
    joint_min_rad: float = 0.0
    joint_max_rad: float = 1.2
    direction: int = 1
    offset_rad: float = 0.0
    scale: float = 1.0

    def __post_init__(self) -> None:
        values = (
            self.normalized_min,
            self.normalized_max,
            self.joint_min_rad,
            self.joint_max_rad,
            self.offset_rad,
            self.scale,
        )
        if self.motor_id <= 0 or not self.joint_name.strip():
            raise ValueError("mapping requires a positive motor ID and joint name")
        if not all(math.isfinite(value) for value in values):
            raise ValueError("mapping values must be finite")
        if self.normalized_min >= self.normalized_max:
            raise ValueError("normalized_min must be less than normalized_max")
        if self.joint_min_rad >= self.joint_max_rad:
            raise ValueError("joint_min_rad must be less than joint_max_rad")
        if self.direction not in (-1, 1):
            raise ValueError("direction must be +1 or -1")
        if self.scale <= 0:
            raise ValueError("scale must be positive")

    def to_joint(self, position: float, *, clamp: bool = False) -> float:
        if not math.isfinite(position):
            raise ValueError("normalized position must be finite")
        if not self.normalized_min <= position <= self.normalized_max:
            if not clamp:
                raise ValueError("normalized position is outside mapping limits")
            position = max(self.normalized_min, min(self.normalized_max, position))
        fraction = (position - self.normalized_min) / (
            self.normalized_max - self.normalized_min
        )
        if self.direction == -1:
            fraction = 1.0 - fraction
        raw = self.joint_min_rad + fraction * (
            self.joint_max_rad - self.joint_min_rad
        )
        return self.offset_rad + self.scale * raw

    def velocity_to_joint(self, velocity: float) -> float:
        if not math.isfinite(velocity):
            raise ValueError("normalized velocity must be finite")
        gain = self.scale * (self.joint_max_rad - self.joint_min_rad) / (
            self.normalized_max - self.normalized_min
        )
        return self.direction * gain * velocity


def map_joint_state(
    mappings: list[MotorJointMapping],
    positions: Mapping[int, float],
    velocities: Mapping[int, float] | None = None,
) -> tuple[list[str], list[float], list[float]]:
    """Return ordered JointState-compatible name, position and velocity arrays."""
    if len({item.joint_name for item in mappings}) != len(mappings):
        raise ValueError("joint names in mappings must be unique")
    velocities = velocities or {}
    names, joint_positions, joint_velocities = [], [], []
    for item in mappings:
        if item.motor_id not in positions:
            raise ValueError(f"missing position for motor {item.motor_id}")
        names.append(item.joint_name)
        joint_positions.append(item.to_joint(float(positions[item.motor_id])))
        joint_velocities.append(item.velocity_to_joint(float(velocities.get(item.motor_id, 0.0))))
    return names, joint_positions, joint_velocities

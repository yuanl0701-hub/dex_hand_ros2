"""Nominal planar forward kinematics for simulation evidence only."""

from __future__ import annotations

import math
from typing import Sequence


def planar_fingertip(
    active_angle: float,
    lengths: Sequence[float] = (0.045, 0.030, 0.022),
    mimic_ratios: Sequence[float] = (1.0, 0.7, 0.5),
) -> tuple[float, float]:
    """Compute a nominal three-link fingertip position in metres."""
    if len(lengths) != 3 or len(mimic_ratios) != 3:
        raise ValueError("three lengths and three mimic ratios are required")
    values = (active_angle, *lengths, *mimic_ratios)
    if not all(math.isfinite(value) for value in values) or any(
        length <= 0 for length in lengths
    ):
        raise ValueError("kinematic inputs must be finite and lengths positive")
    cumulative = 0.0
    x = y = 0.0
    for length, ratio in zip(lengths, mimic_ratios):
        cumulative += active_angle * ratio
        x += length * math.cos(cumulative)
        y += length * math.sin(cumulative)
    return x, y

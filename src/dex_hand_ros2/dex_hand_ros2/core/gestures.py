"""Validated hardware-independent gesture definitions and configuration loading."""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any, Mapping

from .driver import DriverConfig, DriverValidationError


@dataclass(frozen=True)
class GestureDefinition:
    name: str
    positions: dict[int, float]
    description: str = ""
    duration: float = 0.5
    units: str = "normalized_percent"


class GestureLibrary:
    """Ordered validated gesture collection."""

    def __init__(self, config: DriverConfig) -> None:
        self.config = config
        self._gestures: dict[str, GestureDefinition] = {}

    def add(self, gesture: GestureDefinition, *, replace: bool = False) -> None:
        name = gesture.name.strip()
        if not name:
            raise DriverValidationError("gesture name must not be empty")
        if name in self._gestures and not replace:
            raise DriverValidationError(f"duplicate gesture name: {name}")
        if gesture.units != "normalized_percent":
            raise DriverValidationError("gesture units must be normalized_percent")
        if not math.isfinite(gesture.duration) or gesture.duration <= 0:
            raise DriverValidationError("gesture duration must be finite and positive")
        positions = self._validate_complete(gesture.positions)
        self._gestures[name] = GestureDefinition(
            name=name,
            positions=positions,
            description=gesture.description,
            duration=float(gesture.duration),
            units=gesture.units,
        )

    def get(self, name: str) -> GestureDefinition:
        try:
            return self._gestures[name]
        except KeyError as exc:
            raise KeyError(f"unknown gesture: {name}") from exc

    def names(self) -> list[str]:
        return list(self._gestures)

    def _validate_complete(self, positions: Mapping[int, float]) -> dict[int, float]:
        if set(positions) != set(self.config.motor_ids):
            raise DriverValidationError("gesture must define every configured motor exactly once")
        result: dict[int, float] = {}
        for motor_id in self.config.motor_ids:
            position = positions[motor_id]
            self.config.validate_position(position)
            result[motor_id] = float(position)
        return result

    @classmethod
    def load(cls, path: str | Path, config: DriverConfig) -> GestureLibrary:
        """Load JSON-compatible YAML without requiring PyYAML.

        If PyYAML is installed, ordinary YAML is also accepted.
        """
        source = Path(path)
        text = source.read_text(encoding="utf-8")
        try:
            data: Any = json.loads(text)
        except json.JSONDecodeError:
            try:
                import yaml  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ValueError(
                    "gesture file is not JSON-compatible YAML and PyYAML is unavailable"
                ) from exc
            data = yaml.safe_load(text)
        if not isinstance(data, dict) or not isinstance(data.get("gestures"), list):
            raise ValueError("gesture file must contain a gestures list")
        library = cls(config)
        for raw in data["gestures"]:
            if not isinstance(raw, dict) or not isinstance(raw.get("positions"), dict):
                raise ValueError("each gesture must be an object with positions")
            positions = {int(key): value for key, value in raw["positions"].items()}
            library.add(
                GestureDefinition(
                    name=str(raw.get("name", "")),
                    positions=positions,
                    description=str(raw.get("description", "")),
                    duration=float(raw.get("duration", 0.5)),
                    units=str(raw.get("units", "normalized_percent")),
                )
            )
        return library

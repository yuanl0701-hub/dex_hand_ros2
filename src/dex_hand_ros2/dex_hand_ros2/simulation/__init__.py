"""Deterministic simulation backend and fault-injection support."""

from .driver import MotorSimulationState, SimulatedMotorConfig, SimulatedMotorDriver

__all__ = ["MotorSimulationState", "SimulatedMotorConfig", "SimulatedMotorDriver"]

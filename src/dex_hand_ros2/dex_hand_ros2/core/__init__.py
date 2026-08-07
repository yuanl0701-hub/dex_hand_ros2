"""Hardware-independent control domain.

Nothing in this package may import ROS 2, a serial protocol, or a concrete
motor backend.  Hardware adapters depend on this package, never the reverse.
"""

from .controller import HandController
from .driver import (
    DriverConfig,
    DriverError,
    DriverNotConnectedError,
    DriverValidationError,
    GenericMotorDriver,
    MockMotorDriver,
)
from .gestures import GestureDefinition, GestureLibrary
from .joint_mapping import MotorJointMapping, map_joint_state
from .pid import PIDConfig, PIDController
from .safety import SafetyController, SafetyState, SafetyStatus
from .trajectory import MultiAxisQuinticTrajectory, QuinticTrajectory

__all__ = [
    "DriverConfig",
    "DriverError",
    "DriverNotConnectedError",
    "DriverValidationError",
    "GenericMotorDriver",
    "GestureDefinition",
    "GestureLibrary",
    "HandController",
    "MockMotorDriver",
    "MotorJointMapping",
    "MultiAxisQuinticTrajectory",
    "PIDConfig",
    "PIDController",
    "QuinticTrajectory",
    "SafetyController",
    "SafetyState",
    "SafetyStatus",
    "map_joint_state",
]

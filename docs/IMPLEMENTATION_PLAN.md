# Remaining Implementation Plan

## Critical — target verification

1. On Ubuntu 22.04/ROS 2 Humble, run dependency resolution, clean `colcon`
   build, interface inspection, fake launch, tests, and shutdown checks.
2. Record exact ROS distribution, Python version, command output, and Git
   commit in the implementation changelog.
3. Correct only observed ROS build/runtime defects; do not convert an
   unexecuted check into a verified status.

## High — hardware validation

1. Obtain authoritative MPD20 and HTS20L register/baud documentation.
2. Confirm the exact Feetech model and whether write instructions return status.
3. Establish a powered-hardware test procedure including current limits,
   mechanical clearance, emergency power isolation, and recovery.
4. Verify one motor before multi-motor commands; capture raw packets and results.

## High — model gate

1. Obtain a verified URDF/Xacro, meshes, axes, joint limits, and motor mapping.
2. Audit the model before implementing `JointState`, TF, FK, IK, ros2_control,
   standard trajectories, or RViz.
3. If any geometry is missing, keep these features blocked.

## Medium — integration and experiments

1. Add ROS launch tests and typed diagnostic/status messages while preserving
   compatibility topics.
2. Execute trajectory and PID logging first on the mock, then on hardware under
   the approved safety procedure.
3. Report raw measurements and analysis separately.

Each stage must update implementation status, interface inventory, thesis
traceability, and the changelog.

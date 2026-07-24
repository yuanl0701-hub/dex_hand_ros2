# Technical Debt

## Critical

- ROS 2 compilation and runtime behavior are unverified for the current source.
- MPD20/HTS20L register semantics and Feetech response behavior require
  authoritative device verification.
- Emergency stop is a software command latch, not a certified power or
  torque-removal function.

## High

- No verified URDF, motor-to-joint mapping, link geometry, physical limits, or
  coordinate frames exist.
- Real serial calls remain synchronous inside the single background worker.
  This protects executor callbacks but limits concurrent feedback.
- Legacy `Int32MultiArray` commands and JSON-in-`String` status are weakly typed.
  They are retained for compatibility.
- Node parameter validation occurs at startup; dynamic parameter callbacks are
  not implemented.

## Medium

- Runtime-added gestures are not persisted.
- The command watchdog latches after a command stream becomes stale but cannot
  prove a hardware-safe hold state.
- PID convergence is verified only against an instantaneous mock plant.
- No ROS launch tests or QoS/network stress tests exist.

## Low

- The compatibility interface name `PIDconfig` has nonstandard capitalization.
- Gesture CLI is intentionally minimal.
- Setup metadata is retained for Python tooling although ROS builds use CMake.

Generated `build/`, `install/`, and `log/` files were previously committed.
They are now excluded because they obscure source review and embed
machine-specific paths and binaries.

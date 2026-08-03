# Technical Debt

## Critical

- Current source builds and passes package tests in the Humble container; the
  physical deployment host and serial hardware runtime remain unverified.
- MPD20 register semantics now match the supplied V1.5 manual and Modbus Poll
  guide, but electrical timing, ID wiring, per-axis calibration, stop response
  and fault behavior still require physical verification. HTS20L and Feetech
  remain unverified against hardware.
- Emergency stop is a software command latch, not a certified power or
  torque-removal function. MPD20 now receives an active position-hold request,
  but an independent hardware power-disconnect stop remains mandatory.

## High

- No verified URDF, motor-to-joint mapping, link geometry, physical limits, or
  coordinate frames exist.
- The browser UI now discovers logical axes dynamically, but the nominal
  URDF/RViz and Isaac/Revo2 assets retain model-specific six-axis assumptions.
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
- Layered Mock and simulated launches have manual container smoke coverage,
  but no automated launch test or QoS/network stress test exists.

## Low

- The compatibility interface name `PIDconfig` has nonstandard capitalization.
- Gesture CLI is intentionally minimal.
- Setup metadata is retained for Python tooling although ROS builds use CMake.

Generated `build/`, `install/`, and `log/` files were previously committed.
They are now excluded because they obscure source review and embed
machine-specific paths and binaries.

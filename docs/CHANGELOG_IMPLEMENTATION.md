# Implementation Changelog

## 2026-07-23

### Repository recovery

- Confirmed clean baseline `main` at `665395d175882320303474bc9ff659c792371cf2`.
- Verified the broken gitlink referenced `7424eae0d385ee0b16c2331a339872c0d33d08cf`.
- `git ls-remote origin` succeeded after network approval.
- Exact-SHA `git fetch --no-tags origin 7424eae…` succeeded in an isolated
  temporary repository.
- Recovered source was normalized into a self-contained package.

### Implemented

- Correct ROS package metadata and interface generation configuration.
- Driver abstraction, deterministic mock, strict Modbus/Feetech protocols,
  real-driver adapters, safety/watchdog, emergency stop, gesture library,
  quintic trajectories, PID, asynchronous ROS adapter, launch/configuration,
  tests, experiment export, and audit/thesis documentation.
- Model-dependent FK/IK/RViz work was not attempted because verified geometry
  is absent.

### Commands and actual results

| Command | Result |
|---|---|
| Initial `git ls-remote origin` in sandbox | Failed: network name resolution blocked |
| Approved `git ls-remote origin` | Passed; `main`/HEAD at `665395d…` |
| Approved exact-SHA fetch | Passed; object type `commit`, exact hash matched |
| Initial `python3 -m pytest` | Blocked: Apple system Python has no pytest |
| Initial `compileall` | Blocked: Apple cache path outside sandbox |
| `ruff check src/dex_hand_ros2/dex_hand_ros2 src/dex_hand_ros2/test` | Passed |
| `PYTHONPATH=src/dex_hand_ros2 /opt/anaconda3/bin/pytest -q src/dex_hand_ros2/test` | Passed: 30 tests at that stage |
| `PYTHONPYCACHEPREFIX=/private/tmp/dex-hand-pycache python3 -m compileall -q ...` | Passed |
| `mypy ... --exclude '(hand_node\|config_node\|gesture_cli)\.py'` | Passed |
| Final pure Python test suite | Passed: 34 tests |
| Final Ruff lint and format checks | Passed |
| Final mypy core check | Passed: no issues in 12 source files |
| XML syntax check for `package.xml` | Passed |
| Theoretical trajectory export smoke test | Passed; output labeled `algorithm_output` in `/private/tmp` |
| `git diff --check` | Passed |
| `python3 setup.py --name --version` from repository root | Failed: command used the wrong working directory |
| `python3 setup.py --name --version` from `src/dex_hand_ros2` | Passed |
| `command -v cmake`, `colcon`, `ros2`, `rclpy` | No commands found; ROS/CMake verification blocked by environment |

ROS 2 build, launch, and hardware tests were not run and are not recorded as
passing.
# 2026-07-24 — Humble interface split and thesis experiment automation

- Pulled Ubuntu evidence commit `cd0657a` with fast-forward-only Git semantics.
- Confirmed the Humble duplicate-target failure caused by generating interfaces
  and installing Python code under the same `dex_hand_ros2` package name.
- Split messages and services into `dex_hand_interfaces`; updated Python
  imports and package dependencies.
- Removed committed colcon build/install/log caches while retaining raw E00
  failure evidence.
- Corrected an unverified historical summary that incorrectly claimed the
  split and three successful builds had already occurred.
- Added Ubuntu bootstrap and one-command E00--E07 experiment collection.
- Added machine-readable metadata, raw CSV, summary tables, dependency-free SVG
  figures, evidence index, checksums, and archive generation.
- Local status: pure/static validation pending in this change; ROS 2 Humble
  execution remains to be verified on Ubuntu.

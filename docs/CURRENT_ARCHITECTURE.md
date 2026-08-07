# Current Architecture

## Implemented package architecture

```mermaid
flowchart TB
  Interfaces["dex_hand_interfaces (msg/srv)"] --> ROS["dex_hand_ros2 ROS adapters"]
  ROS --> Loader["ros/backend_loader"]
  ROS --> Core["core/"]
  Core --> Controller["HandController"]
  Controller --> Safety["Safety / gestures / trajectory / PID"]
  Controller --> Driver["GenericMotorDriver"]
  Loader --> Factory["backends/factory"]
  Factory --> Mock["MockMotorDriver"]
  Factory --> Sim["simulation/"]
  Factory --> MPD20["backends/mpd20.py"]
  Factory --> Feetech["backends/feetech.py"]
  Factory --> HTS["backends/hts20l.py"]
  MPD20 --> Protocols["backends/protocols.py"]
  Feetech --> Protocols
  Protocols --> Serial["Injected or pyserial transport"]
  Commission["commissioning/"] --> MPD20
  Experiment["Thesis experiment client"] --> Interfaces
  Experiment --> Evidence["CSV / JSON / SVG evidence bundle"]
```

Legacy top-level modules such as `driver.py`, `real_drivers.py` and
`sim_driver.py` are compatibility import layers. New implementation code
imports from `core/`, `backends/`, or `simulation/`.

## Configuration overlay

```mermaid
flowchart LR
  Runtime["runtime policy"] --> Merge["ROS parameter overlay"]
  Backend["backend family"] --> Merge
  Model["hand model"] --> Merge
  Deployment["physical hand instance"] --> Merge
  CLI["launch overrides"] --> Merge
  Merge --> Node["dex_hand_node"]
```

- `runtime/` owns control, safety and QoS policy.
- `backends/` owns protocol/transport startup settings.
- `hand_models/` owns logical axes, joint mapping and gestures.
- `deployments/` owns serial path, physical device IDs and calibration.

For MPD20, `motor_ids` are reusable logical axes and `mpd20_device_ids` are
per-hand Modbus addresses. The backend resolves that mapping before every bus
operation.

## Node topology

```mermaid
flowchart LR
  Clients["External command clients"] --> Hand["dex_hand_node"]
  Hand --> Status["/dex_hand/status"]
  Hand --> MotorState["/dex_hand/motor_state"]
  ConfigClients["Configuration clients"] --> Config["dex_hand_config_node"]
  Hand --> Backend["Selected backend"]
  Config --> Backend2["Dedicated real backend"]
```

The hand and configuration nodes should not open the same serial device
simultaneously.

For MPD20, the normalized control domain is mapped per motor to calibrated raw
register limits. Physical startup is read-only by default, probes every ID with
function 04, requires stationary feedback, and needs an explicit motion gate.
Stop, watchdog, consecutive feedback-failure and shutdown paths request an
active hold by rewriting measured raw positions as targets. This is not a
hardware torque-off function.

## Command flow

```mermaid
flowchart LR
  Command["Topic or service command"] --> Validate["Shape/value validation"]
  Validate --> Queue["Single worker queue"]
  Queue --> Safety["Safety and stop state"]
  Safety --> Control["Gesture / trajectory / PID"]
  Control --> Driver["Driver adapter"]
```

## Feedback flow

```mermaid
flowchart LR
  Driver["Driver read"] --> Worker["Non-executor worker"]
  Worker --> Motor["MotorState per motor"]
  Safety["Safety status"] --> JSON["Status JSON"]
  JSON --> Status["/dex_hand/status"]
```

## Remaining boundary

The nominal URDF/RViz and Revo2 assets remain model-specific. A future verified
physical description can move into a separate ROS description package without
changing `core/` or the motor backends.

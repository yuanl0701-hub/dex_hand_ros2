# Current Architecture

## Implemented package architecture

```mermaid
flowchart TB
  ROS["ROS 2 adapters"] --> Controller["HandController"]
  Controller --> Safety["SafetyController"]
  Controller --> Gestures["GestureLibrary"]
  Controller --> Trajectory["Quintic trajectories"]
  Controller --> PID["PIDController"]
  Controller --> Driver["GenericMotorDriver"]
  Driver --> Mock["MockMotorDriver"]
  Driver --> Real["MPD20 / HTS20L / Feetech"]
  Real --> Protocols["Modbus RTU / Feetech protocols"]
  Protocols --> Serial["Injected or pyserial transport"]
```

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

## Proposed target architecture

After a verified URDF and motor-to-joint mapping exist, a separate description
package may add `robot_state_publisher`, `JointState`, TF, RViz, and standard
joint trajectory interfaces. None are part of the current architecture.

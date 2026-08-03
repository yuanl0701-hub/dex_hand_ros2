# ROS 2 Interface Inventory

ROS interfaces and launch installation are container-verified with ROS 2 Humble.
MPD20 serial behavior remains unverified on physical hardware. Topic QoS
defaults to reliable, keep-last, depth 10. Reliability and depth are startup
parameters used by the automated reliable/best-effort comparison.

## Topics

| Interface name | Type | Message type | Direction | Provider | Consumer | QoS | Source evidence | Status | Problem |
|---|---|---|---|---|---|---|---|---|---|
| `/dex_hand/gesture_cmd` | Topic | `dex_hand_interfaces/msg/GestureCmd` | Input | External/`gesture_cli` | `dex_hand_node` | Configurable; Reliable/10 default | `gesture_cmd_callback` | Implemented but not verified | Normalized motor mapping only |
| `/dex_hand/motor_pos_cmd` | Topic | `std_msgs/msg/Int32MultiArray` | Input | External | `dex_hand_node` | Configurable; Reliable/10 default | `motor_pos_callback` | Implemented but not verified | Legacy array shape `[id, position]` |
| `/dex_hand/motor_pos_pid_cmd` | Topic | `std_msgs/msg/Int32MultiArray` | Input | External | `dex_hand_node` | Configurable; Reliable/10 default | `motor_pos_pid_callback` | Implemented but not verified | Legacy array shape |
| `/dex_hand/pid_config` | Topic | `dex_hand_interfaces/msg/PIDconfig` | Input | External | `dex_hand_node` | Configurable; Reliable/10 default | `pid_config_callback` | Implemented but not verified | No persistent gain store |
| `/dex_hand/status` | Topic | `std_msgs/msg/String` | Output | `dex_hand_node` | External | Configurable; Reliable/10 default | `publish_status` | Implemented but not verified | JSON in string for compatibility |
| `/dex_hand/motor_state` | Topic | `dex_hand_interfaces/msg/MotorState` | Output | `dex_hand_node` | External | Configurable; Reliable/10 default | `_read_and_publish_states` | Implemented but not verified | One message per motor; normalized position |

## Services

| Interface name | Type | Message type | Direction | Provider | Consumer | QoS | Source evidence | Status | Problem |
|---|---|---|---|---|---|---|---|---|---|
| `/dex_hand/list_gestures` | Service | `std_srvs/srv/Trigger` | Output API | `dex_hand_node` | External | Service default | `list_gestures_callback` | Implemented but not verified | Names returned as comma-separated text |
| `/dex_hand/demo_gestures` | Service | `std_srvs/srv/Trigger` | Input API | `dex_hand_node` | External | Service default | `demo_gestures_callback` | Implemented but not verified | Completion is asynchronous |
| `/dex_hand/add_gesture` | Service | `dex_hand_interfaces/srv/AddGesture` | Input API | `dex_hand_node` | External | Service default | `add_gesture_callback` | Implemented but not verified | Runtime additions are not persisted |
| `/dex_hand/run_gesture_pid` | Service | `dex_hand_interfaces/srv/RunGesturePid` | Input API | `dex_hand_node` | External | Service default | `run_gesture_pid_callback` | Implemented but not verified | Completion is asynchronous |
| `/dex_hand/emergency_stop` | Service | `std_srvs/srv/SetBool` | Input API | `dex_hand_node` | External | Service default | `emergency_stop_callback` | Implemented but not verified | Software latch; no proven torque-off |
| `/dex_hand/change_id` | Service | `dex_hand_interfaces/srv/ChangeId` | Input API | `dex_hand_config_node` | External | Service default | `change_id_callback` | Implemented but not verified | Hardware-only, persistent change |
| `/dex_hand/change_baud` | Service | `dex_hand_interfaces/srv/ChangeBaud` | Input API | `dex_hand_config_node` | External | Service default | `change_baud_callback` | Implemented but not verified | HTS20L mapping deliberately blocked |

## Parameters

| Interface name | Type | Message type | Direction | Provider | Consumer | QoS | Source evidence | Status | Problem |
|---|---|---|---|---|---|---|---|---|---|
| `driver_type` | Parameter | string | Input | User/YAML | Both nodes | N/A | `_declare_parameters` | Implemented but not verified | Startup-only |
| `serial_port` | Parameter | string | Input | User/YAML | Both nodes | N/A | node constructors | Implemented but not verified | Platform-specific path |
| `baudrate` | Parameter | integer | Input | User/YAML | Both nodes | N/A | node constructors | Implemented but not verified | Device-specific |
| `serial_timeout` | Parameter | double | Input | User/YAML | Both nodes | N/A | node constructors | Implemented but not verified | Untuned on hardware |
| `serial_retries` | Parameter | integer | Input | User/YAML | Both nodes | N/A | node constructors | Implemented but not verified | Untuned on hardware |
| `motor_ids` | Parameter | integer array | Input | User/YAML | Both nodes | N/A | node constructors | Implemented but not verified | Logical IDs only |
| `motor_labels` | Parameter | string array | Input | User/YAML | `dex_hand_node` | N/A | startup validation/status | Implemented and container-verified | Must align with motor IDs |
| `position_min` / `position_max` | Parameter | double | Input | User/YAML | `dex_hand_node` | N/A | `DriverConfig` | Implemented but not verified | Normalized limits |
| `hardware_motion_enabled` | Parameter | boolean | Input | User/YAML | `dex_hand_node` | N/A | `MPD20Driver` | Implemented and container-verified | False by default; physical behavior pending |
| `hardware_verify_on_connect` | Parameter | boolean | Input | User/YAML | `dex_hand_node` | N/A | `MPD20Driver.connect` | Implemented and container-verified | Function-04 timing pending |
| `hardware_hold_on_connect` | Parameter | boolean | Input | User/YAML | `dex_hand_node` | N/A | `MPD20Driver.connect` | Implemented and container-verified | Active hold, not torque-off |
| `hardware_require_stationary_on_connect` | Parameter | boolean | Input | User/YAML | `dex_hand_node` | N/A | `MPD20Driver.connect` | Implemented and container-verified | Moving flag requires hardware verification |
| `mpd20_raw_min` / `mpd20_raw_max` | Parameter | integer arrays | Input | User/YAML | `dex_hand_node` | N/A | MPD20 calibration | Implemented and unit-verified | Per-hand mechanical calibration required |
| `mpd20_directions` | Parameter | integer array | Input | User/YAML | `dex_hand_node` | N/A | MPD20 calibration | Implemented and unit-verified | Values must be -1 or 1 |
| `mpd20_max_speeds` | Parameter | integer array | Input | User/YAML | `dex_hand_node` | N/A | MPD20 startup | Implemented and unit-verified | Vendor scale; physical tuning required |
| `max_command_rate` | Parameter | double | Input | User/YAML | `dex_hand_node` | N/A | `SafetyController` | Implemented but not verified | Normalized percent/s |
| `command_watchdog_timeout` | Parameter | double | Input | User/YAML | `dex_hand_node` | N/A | `SafetyController` | Implemented but not verified | Hardware value untuned |
| `state_poll_failure_limit` | Parameter | integer | Input | User/YAML | `dex_hand_node` | N/A | state-future callback | Implemented and container-verified | Escalates to non-recoverable fault |
| `status_pub_freq` | Parameter | double | Input | User/YAML | `dex_hand_node` | N/A | status timer | Implemented but not verified | Serial polling capacity unknown |
| `pid_kp` / `pid_ki` / `pid_kd` | Parameter | double | Input | User/YAML | `dex_hand_node` | N/A | PID initialization | Implemented but not verified | Not hardware tuned |
| `gesture_file` | Parameter | string | Input | User/YAML | `dex_hand_node` | N/A | `RoboticHand` construction | Implemented but not verified | Startup-only |
| `qos_reliability` | Parameter | string | Input | User/YAML | `dex_hand_node` | N/A | `_reliability_policy` | Implemented but not verified | `reliable` or `best_effort`; startup-only |
| `qos_depth` | Parameter | integer | Input | User/YAML | `dex_hand_node` | N/A | QoS construction | Implemented but not verified | Positive; startup-only |

No actions, lifecycle nodes, explicit callback groups, standard joint-trajectory
action, or `use_sim_time` behavior are implemented. `JointState` and TF are
available only on the nominal simulation/visualization path; they are not a
verified physical-hand model.

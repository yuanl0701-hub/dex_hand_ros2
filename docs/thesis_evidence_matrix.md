# Simulation thesis evidence matrix

| Claim | Source | Test | Experiment/asset | Level | Limitation |
|---|---|---|---|---|---|
| Target and actual states differ dynamically | `sim_driver.py` | `test_target_does_not_instantly_change_actual_and_step_advances` | step CSV; Figs 01--03 | Pure-Python + experiment verified | Assumed plant |
| Dynamic limits are enforced | `sim_driver.py` | `test_velocity_and_acceleration_limits_and_position_bounds` | trajectory metrics | Experiment verified | No system identification |
| Six axes step synchronously | `sim_driver.py` | `test_six_motors_step_synchronously` | gesture CSV; Fig 08 | Experiment verified | Independent axes |
| Seeded noise is repeatable | `sim_driver.py` | `test_seeded_noise_is_reproducible` | metadata seed 6048 | Pure-Python verified | PRNG only |
| Faults are explicit/recoverable | `sim_driver.py` | `test_fault_injection_clear_and_reset` | fault CSV; Figs 11--12 | Experiment verified | Logical faults |
| Mapping handles direction/offset | `joint_mapping.py` | `test_mapping_endpoints_direction_offset_and_scale` | mapping YAML | Pure-Python verified | Not calibrated |
| Nominal fingertip is reproducible | `kinematics.py` | `test_joint_state_arrays_and_nominal_forward_kinematics` | workspace CSV; Figs 09--10 | Experiment verified | Assumed planar geometry |
| PID converges on dynamic plant | PID + plant | `test_pid_position_command_converges_on_dynamic_plant` | PID CSV; Figs 06--07 | Experiment verified | Output is position command |
| `/joint_states` publishes mapped state | `hand_node.py` | mapping tests + Humble colcon | Mac Docker run `103359Z`, ~99.98 Hz | ROS 2 runtime verified | Docker/software timing |
| `robot_state_publisher` derives TF | launch + Xacro | TF query | Six frames, rosbag, RViz screenshots | ROS 2 runtime verified | Nominal geometry |
| Online faults are observable through ROS | `SetSimFault.srv`, `hand_node.py` | Service call | stuck status and rosbag | ROS 2 runtime verified | Logical fault only |
| RViz displays joint motion | Xacro + RViz config | Two configurations captured | `rviz_virtual_hand.png`, `rviz_open_pose.png` | ROS 2 runtime verified | Mesa software rendering |
| Named gestures switch the virtual hand | `GestureCmd` callback, gesture library, controller, simulated plant | E08 runtime trace and terminal-state checks | `gesture_switch_20260725`: 999 JointState messages; three Revo2 USD poses reconstructed from terminal targets | ROS 2 runtime verified; USD views are qualitative | Anatomical mapping is a visualisation convention, not hardware calibration |
| Mock remains instantaneous | `driver.py` unchanged | full legacy suite | — | Pure-Python verified | Test double only |
| Results prove hardware performance | None | None | None | Physical hardware unverified | Prohibited claim |

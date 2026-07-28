# Isaac Sim 4.5.0 灵巧手仿真指南

本流程面向 Ubuntu 22.04、ROS 2 Humble 和 Isaac Sim 4.5.0。它把项目中的
Xacro 展开为 URDF，由 Isaac Sim 导入为固定基座 articulation，并通过 ROS 2
Bridge 接收六个关节的位置命令。用户发送已有的手势名称后，可以在 Isaac Sim
视口中看到姿态平滑切换。

## 数据流与证据边界

```text
/dex_hand/gesture_cmd (dex_hand_interfaces/GestureCmd)
                  |
                  v
       /dex_hand_node + simulated plant
                  |
                  v
/dex_hand/joint_command (sensor_msgs/JointState)
                  |
           Isaac Sim ROS 2 Bridge
                  |
                  v
       six-joint articulation in PhysX
                  |
                  v
/isaac_joint_states (sensor_msgs/JointState)
```

命令和反馈使用不同话题，避免 Isaac Sim 发布的关节状态被再次当成控制命令。
自定义手势消息只由外部 ROS 2 节点处理；跨入 Isaac Sim 的消息是标准
`sensor_msgs/JointState`，因此 Isaac Sim 环境不需要编译项目的自定义接口。

当前 URDF 是六个单自由度关节的名义可视化模型，质量、惯量、碰撞体、关节轴和
驱动增益均为仿真假设，不是实物标定结果。该流程能够证明 ROS 2 手势链路、
关节映射和 Isaac Sim 中的动作切换，不能据此声称具有真实硬件精度。

## 1. 首次准备

确认项目已同步到 Ubuntu，然后执行：

```bash
cd ~/yl/dex_hand_ros2
./scripts/bootstrap_ubuntu.sh
```

找到 Isaac Sim 安装目录。该目录中必须存在 `python.sh`。例如：

```bash
export ISAAC_SIM_PATH=~/isaacsim
test -x "$ISAAC_SIM_PATH/python.sh" && echo "Isaac Sim path: OK"
```

如果你的安装目录不同，请替换为实际路径。不要把项目的 Conda 环境强行注入
Isaac Sim；启动脚本使用 Isaac Sim 自带的 Python，并在启动前加载系统安装的
ROS 2 Humble。

## 2. 一键启动

在第一个终端运行：

```bash
cd ~/yl/dex_hand_ros2
export ISAAC_SIM_PATH=~/isaacsim
./scripts/run_isaacsim.sh
```

脚本会依次完成：

1. 使用 `rosdep` 补齐 ROS 依赖并构建两个 ROS 2 包；
2. 将 `virtual_dex_hand.urdf.xacro` 展开到
   `.isaacsim/generated/virtual_dex_hand.urdf`；
3. 启动手势控制节点并发布 `/dex_hand/joint_command`；
4. 用 Isaac Sim 的 `python.sh` 导入 URDF、创建 ROS 2 Action Graph 并播放仿真。

第一次启动 Isaac Sim 可能较慢。成功后终端会显示 `DEX hand loaded in Isaac
Sim`，视口中应出现固定在地面上方的蓝色手掌和六个浅色运动部件。

如果 Isaac Sim 不在 `~/isaacsim`：

```bash
./scripts/run_isaacsim.sh \
  --isaac-sim-path /你的/isaac-sim-4.5.0/目录
```

可选地保存已经配置好 ROS 2 Action Graph 的 USD：

```bash
./scripts/run_isaacsim.sh \
  --save-stage "$PWD/.isaacsim/dex_hand.usd"
```

调试完成后可使用 `--skip-build` 跳过重复构建；无窗口服务器可加 `--headless`。

## 3. 演示手势切换

保持第一个终端和 Isaac Sim 窗口运行，在第二个终端执行：

```bash
cd ~/yl/dex_hand_ros2
./scripts/demo_isaacsim_gestures.sh
```

脚本会依次演示项目中的九个手势并回到 `open`。也可以只演示指定手势：

```bash
./scripts/demo_isaacsim_gestures.sh open fist point thumbs_up open
```

调整每个手势的停留时间和运动速度：

```bash
GESTURE_INTERVAL_SECONDS=4 GESTURE_SPEED=0.6 \
  ./scripts/demo_isaacsim_gestures.sh open pinch_two fist open
```

单独发送一个命令：

```bash
source /opt/ros/humble/setup.bash
source ~/yl/dex_hand_ros2/install/setup.bash
ros2 topic pub --once /dex_hand/gesture_cmd \
  dex_hand_interfaces/msg/GestureCmd \
  "{gesture: 'fist', speed: 0.8}"
```

## 4. 验收检查

在第二个终端加载环境：

```bash
source /opt/ros/humble/setup.bash
source ~/yl/dex_hand_ros2/install/setup.bash
```

确认 ROS 控制节点存在：

```bash
ros2 node list | grep dex_hand_node
```

确认发送给 Isaac Sim 的命令持续更新：

```bash
timeout 8 ros2 topic hz /dex_hand/joint_command
```

频率应接近配置的 100 Hz。确认 Isaac Sim 正在返回 articulation 状态：

```bash
ros2 topic echo --once /isaac_joint_states
```

输出应包含六个名称：

```text
motor_1_joint
motor_2_joint
motor_3_joint
motor_4_joint
motor_5_joint
motor_6_joint
```

列出可用手势：

```bash
ros2 service call /dex_hand/list_gestures std_srvs/srv/Trigger "{}"
```

## 5. 常见问题

### 找不到 `python.sh`

传入 Isaac Sim 的实际安装目录：

```bash
find "$HOME" -maxdepth 4 -name python.sh -path '*isaac*' -print
export ISAAC_SIM_PATH=/搜索得到的目录
```

### Isaac Sim 中有模型但不动作

依次检查：

```bash
ros2 topic info /dex_hand/joint_command --verbose
ros2 topic echo --once /dex_hand/joint_command
ros2 topic info /isaac_joint_states --verbose
```

命令话题应同时有 ROS 节点发布者和 Isaac Sim 订阅者。检查第一个终端是否出现
ROS 2 Bridge、URDF importer 或 articulation 的报错，并查看：

```bash
tail -n 100 .isaacsim/logs/ros_controller.log
```

### ROS 2 话题在两个进程之间不可见

先退出 Isaac Sim，再在同一终端重新运行启动脚本。确认没有混用不同的
`ROS_DOMAIN_ID`，并保留 Fast DDS：

```bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
unset ROS_DOMAIN_ID
./scripts/run_isaacsim.sh
```

### 结束仿真

关闭 Isaac Sim 窗口或在第一个终端按 `Ctrl+C`。启动脚本会同时停止它创建的
`/dex_hand_node`，不会结束其他终端中的 ROS 2 节点。

## 官方依据

- [Isaac Sim 4.5 ROS 2 安装与 Humble 环境](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/install_ros.html)
- [Isaac Sim 4.5 URDF Importer](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_setup/import_urdf.html)
- [Isaac Sim 4.5 ROS 2 Joint Control](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/ros2_tutorials/tutorial_ros2_manipulation.html)

# Isaac Sim 4.5.0 灵巧手仿真指南

本流程面向 Ubuntu 22.04、ROS 2 Humble 和 Isaac Sim 4.5.0。默认直接加载
仓库内置的 `assets/revo2_right_hand/revo2_right_hand.usd`；也保留把项目
Xacro 展开为 URDF 的轻量回退方案。两种模型都通过 ROS 2 Bridge 接收六个
主动关节的位置命令。
用户发送已有的手势名称后，可以在 Isaac Sim 视口中看到姿态平滑切换。

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
    six-command articulation in PhysX
                  |
                  v
/isaac_joint_states (sensor_msgs/JointState)
```

命令和反馈使用不同话题，避免 Isaac Sim 发布的关节状态被再次当成控制命令。
自定义手势消息只由外部 ROS 2 节点处理；跨入 Isaac Sim 的消息是标准
`sensor_msgs/JointState`，因此 Isaac Sim 环境不需要编译项目的自定义接口。

Revo2 右手 USD 包含 6 个带位置驱动的主动关节和 5 个 PhysX mimic 从动关节，
并带有质量、惯量、碰撞体、关节限位和驱动参数。它比简化 Xacro 更适合验证
六电机控制接口和手势的解剖可读性。当前“逻辑电机编号到解剖关节”的对应关系
仍是软件可视化适配，不是通过真实 Revo2 接线或 SDK 标定得到的硬件映射。

| 逻辑电机 | Revo2 主动关节 | 上限 |
|---:|---|---:|
| 1 | `right_index_proximal_joint` | 80.787° |
| 2 | `right_ring_proximal_joint` | 80.787° |
| 3 | `right_middle_proximal_joint` | 80.787° |
| 4 | `right_pinky_proximal_joint` | 80.787° |
| 5 | `right_thumb_metacarpal_joint` | 89.954° |
| 6 | `right_thumb_proximal_joint` | 59.015° |

索引指与中指分别使用电机 1 和 3，是为了让项目原有 `vgesture` 的含义保持
可辨认。五个 distal 关节不占用额外电机命令，由 USD 自带的 mimic 关系联动。

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

## 2. 仓库内置 Revo2 资产

项目已经把 Revo2 右手的完整依赖闭包放在：

```text
assets/revo2_right_hand/
```

正常 `git clone` 或 `git pull` 后不需要再复制外部 `Collected_g2`。可验证资产：

```bash
cd ~/yl/dex_hand_ros2/assets/revo2_right_hand
sha256sum -c SHA256SUMS
```

四个文件必须保持在同一目录，因为主层使用相对引用。其完整性摘要和来源边界
记录在同目录 `README.md`。该 Revo2 右手只引用 Isaac Sim 内置
`OmniPBR.mdl`，不依赖原始集合中的其他纹理目录。

## 3. 一键启动

在第一个终端运行：

```bash
cd ~/yl/dex_hand_ros2
export ISAAC_SIM_PATH=~/isaacsim
./scripts/run_isaacsim.sh
```

脚本会依次完成：

1. 使用 `rosdep` 补齐 ROS 依赖并构建两个 ROS 2 包；
2. 加载 Revo2 专用的六主动关节映射和 USD 关节限位；
3. 启动手势控制节点并发布 `/dex_hand/joint_command`；
4. 引用 Revo2 USD，验证 6 个主动和 5 个 mimic 关节均存在；
5. 创建 ROS 2 Action Graph 并播放仿真。

第一次启动 Isaac Sim 可能较慢。成功后终端会显示 `DEX hand loaded in Isaac
Sim`，并列出 Revo2 的六个受控关节。视口中应出现完整 Revo2 右手。

如果 Isaac Sim 不在 `~/isaacsim`：

```bash
./scripts/run_isaacsim.sh \
  --isaac-sim-path /你的/isaac-sim-4.5.0/目录
```

也可以不用环境变量，直接指定资产：

```bash
./scripts/run_isaacsim.sh \
  --revo2-usd /你的/Collected_g2/SubUSDs/revo2_right_hand.usd
```

如需回退到项目的简化 Xacro：

```bash
./scripts/run_isaacsim.sh --nominal-xacro
```

可选地保存已经配置好 ROS 2 Action Graph 的 USD：

```bash
./scripts/run_isaacsim.sh \
  --save-stage "$PWD/.isaacsim/dex_hand.usd"
```

调试完成后可使用 `--skip-build` 跳过重复构建；无窗口服务器可加 `--headless`。
仓库内置 Revo2 是默认模型。设置 `REVO2_USD_PATH` 或传入 `--revo2-usd`
可以临时使用另一份 Revo2 右手资产。

## 4. 演示手势切换

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

## 5. 验收检查

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

输出应至少包含六个主动关节名称：

```text
right_index_proximal_joint
right_ring_proximal_joint
right_middle_proximal_joint
right_pinky_proximal_joint
right_thumb_metacarpal_joint
right_thumb_proximal_joint
```

Revo2 状态还可能包含五个 distal mimic 关节，这是正常结果。

列出可用手势：

```bash
ros2 service call /dex_hand/list_gestures std_srvs/srv/Trigger "{}"
```

## 6. 常见问题

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
ROS 2 Bridge、USD/URDF 加载或 articulation 的报错，并查看：

```bash
tail -n 100 .isaacsim/logs/ros_controller.log
```

如果日志显示缺少 Revo2 关节，确认加载的是
`revo2_right_hand.usd`，而不是 `_base.usd` 或 `_physics.usd` 单独一层。

### 模型呈白色或材质缺失

先验证仓库内四个 USD 的摘要，并确认没有移动其中任一文件：

```bash
(cd assets/revo2_right_hand && sha256sum -c SHA256SUMS)
```

该资产使用 Isaac Sim 内置的 `OmniPBR.mdl`，不需要外部 `materials/` 或
`textures/`。如果摘要通过但材质仍异常，检查 Isaac Sim 的内置材质扩展和
Console 中的 MDL 加载错误。

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

## 可验证结论与不能外推的结论

完成上述验收后，可以支持：

- 同一套六维手势控制接口能够驱动另一套六主动关节的 Isaac Sim articulation；
- 逻辑电机命令、关节名称映射、限位换算和连续姿态切换工作正常；
- Revo2 的五个从动关节能通过资产自带 mimic 约束联动；
- ROS 2 命令与 Isaac Sim 状态反馈链路可运行。

不能仅凭该仿真支持：

- MPD20、HTS20L 或 Revo2 实物通信协议已经兼容；
- 电机 ID 与真实手指接线关系正确；
- 力矩、速度、温升、抓取力或接触稳定性达到真实硬件指标；
- 该控制系统无需适配即可部署到任意“六电机灵巧手”。

因此论文中宜称为“面向第二种六主动关节模型的接口可移植性仿真”，不要称为
“已在其他六电机硬件上验证”。

## 官方依据

- [Isaac Sim 4.5 ROS 2 安装与 Humble 环境](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/installation/install_ros.html)
- [Isaac Sim 4.5 URDF Importer](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/robot_setup/import_urdf.html)
- [Isaac Sim 4.5 ROS 2 Joint Control](https://docs.isaacsim.omniverse.nvidia.com/4.5.0/ros2_tutorials/tutorial_ros2_manipulation.html)

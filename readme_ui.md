# DEX Hand 网页控制使用说明

本文说明如何在 ROS 2 Jazzy 环境下使用浏览器控制当前 MPD20 六轴机械手。网页节点
不会直接访问串口，而是把浏览器操作转换为现有 ROS 2 话题和服务；MPD20 控制节点仍然
负责串口通信、位置限制、掉线重试、安全状态和动作执行。

## 1. 使用前检查

启动网页前必须满足以下条件：

- MPD20 电机均使用 115200 波特率，物理 ID 1--6 不重复；
- `/dev/ttyUSB0` 可读写，且只由机械手控制节点占用；
- `lab_hand_001.yaml` 中的 ID、raw 范围、方向和最大速度已经检查；
- 手指运动范围内无人、无物，并且现场有独立的硬件断电急停；
- 网页节点与机械手节点使用相同的 `ROS_DOMAIN_ID` 和 RMW 实现。

软件“紧急停止”会尝试把各电机保持在当前位置，不是安全转矩关闭（STO），不能代替
硬件断电。

## 2. 更新和首次构建

```bash
cd ~/dex_hand/dex_hand_ros2
git pull --ff-only origin agent/mpd20-hardware-deployment
```

更新代码、网页或手势配置后，下一次启动机械手时加入 `--build`。如果本地
`lab_hand_001.yaml` 已经完成标定，不要用示例配置覆盖它。

## 3. 启动机械手和网页

### 终端 1：启动 MPD20 控制节点

首次构建或更新后：

```bash
cd ~/dex_hand/dex_hand_ros2
./scripts/start_mpd20_jazzy.sh --build --enable-motion
```

后续正常启动：

```bash
cd ~/dex_hand/dex_hand_ros2
./scripts/start_mpd20_jazzy.sh --enable-motion
```

看到类似以下日志后，保持该终端运行：

```text
DEX hand ready with backend=mpd20
```

### 终端 2：启动网页节点

```bash
cd ~/dex_hand/dex_hand_ros2
./scripts/run_hand_web_ui.sh --ros-distro jazzy
```

浏览器通常会自动打开：

```text
http://127.0.0.1:8765
```

如果没有自动打开，手动访问该地址。需要禁止自动打开浏览器时：

```bash
./scripts/run_hand_web_ui.sh --ros-distro jazzy --no-browser
```

不要使用 `sh scripts/run_hand_web_ui.sh`。该启动器是 Bash 脚本，应使用 `./scripts/...`
或 `bash scripts/...`。

## 4. 手势控制

网页从 `/dex_hand/status` 自动读取当前控制节点实际加载的手势，不依赖写死的按钮列表。
当前 MPD20 手势如下：

| 网页按钮 | ROS 名称 | 动作 |
|---|---|---|
| 张开 | `open` | 五个屈曲轴张开，ID 6 保持中位 |
| 半张开 | `half_open` | 六轴移动到归一化中位 |
| 握拳 | `fist` | ID 1--4 屈曲，ID 5 拇指屈曲，ID 6 保持中位 |
| V 手势 | `vgesture` | 食指和中指张开，其余手指屈曲 |
| 摇滚手势 | `rock` | 食指和小指张开，中指、无名指和拇指屈曲 |
| 指向 | `point` | 食指张开，其余手指和拇指屈曲 |

点击一次按钮只发送一次手势消息。当前实体配置使用 `direct` 模式，每个可用电机只写
一次最终目标，电机内部完成运动。网页上的“动作速度”必须大于 0，但在 `direct` 模式
下不会改变 MPD20 的实际速度；实际速度来自 `lab_hand_001.yaml` 中的
`mpd20_max_speeds`。

页面显示“Gesture sent”表示 ROS 消息已经发布，不代表所有电机已经到位。应同时观察：

- 终端 1 中的 `gesture <name>: success/failed` 日志；
- 页面中的电机反馈；
- `/dex_hand/status` 中的安全状态和不可用电机列表。

控制节点正忙时，新手势可能被拒绝。等待当前操作结束后再点击，不要连续快速点击。

## 5. 页面各区域

### 状态区域

- “ROS 控制器在线”：网页收到了机械手状态，且后端连接存在；
- “安全状态”：正常控制应为 `ready`；
- 电机反馈：显示归一化位置和速度；
- 操作/错误框：显示网页节点最近一次发布动作或服务错误。

如需查看完整状态：

```bash
cd ~/dex_hand/dex_hand_ros2
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /dex_hand/status
```

重点字段包括：

```text
connected
safety_state
hardware_motion_enabled
gesture_execution_mode
unavailable_motor_ids
motor_failure_counts
motor_last_errors
```

### 电机独立控制

每个电机滑块使用 `0..100` 归一化位置，不是 MPD20 raw 值。点击“发送位置”会向单轴
发送普通位置命令；“PID 发送”会运行软件 PID 多次读取和写入。

实体手通常优先使用普通位置命令。只有完成单轴标定并确认运动方向、机械范围和安全目标
后才能使用滑块。不要把网页的 0 或 100 理解为绝对安全的机械端点。

### 紧急停止和恢复

- “紧急停止”调用 `/dex_hand/emergency_stop`，锁存停止状态并尝试保持当前位置；
- “恢复控制”解除软件停止状态；恢复前必须先排除触发停止的原因；
- 如果某个电机无响应，主动保持可能失败，此时应使用硬件断电急停。

### 高级控制

- “PID 参数”和“PID 运行手势”主要用于受控实验，不建议在未调参的实体手上直接使用；
- “添加临时手势”只添加到当前运行节点，节点重启后不会自动保存到 JSON；
- “复位模拟电机”“清除全部故障”和“仿真故障注入”是仿真功能，不用于 MPD20 实机。

## 6. 电机掉线时的行为

当前 MPD20 后端首先按 `serial_retries` 重试。重试仍失败时，该电机会进入
`unavailable_motor_ids`，其他在线电机继续执行命令。后续反馈恢复后，该电机从下一条
命令重新加入，不会在已经执行到一半的手势中途加入。

掉线容忍只是保证其他轴可以继续，不代表多指协调动作仍然完整。反复掉线应检查供电、
RS485 A/B/GND、端子接触、地址、波特率和串口占用。

## 7. 网页启动参数

```text
--ros-distro NAME   ROS 2 发行版，当前实体机使用 jazzy
--host ADDRESS      监听地址，默认 127.0.0.1
--port PORT         HTTP 端口，默认 8765
--no-browser        不自动打开浏览器
```

例如端口 8765 已被占用时：

```bash
./scripts/run_hand_web_ui.sh --ros-distro jazzy --port 8766
```

默认 `127.0.0.1` 只能由本机访问。网页没有登录、鉴权或 TLS，不要将它直接暴露到公共
网络。只有在可信、隔离的局域网和硬件急停均已就绪时，才考虑使用非本机监听地址。

## 8. 常见问题

### 页面显示“等待 ROS 控制器”

确认终端 1 仍在运行，并检查两个终端的 ROS 环境：

```bash
echo "$ROS_DOMAIN_ID"
echo "$RMW_IMPLEMENTATION"
ros2 node list
ros2 topic list | grep dex_hand
```

### 页面可以打开，但点击手势后电机不动

依次确认：

1. 机械手使用了 `--enable-motion` 启动；
2. 页面安全状态为 `ready`；
3. 终端 1 没有显示 `command rejected while busy`；
4. `/dex_hand/status` 中 `hardware_motion_enabled` 为 `true`；
5. 目标电机不在 `unavailable_motor_ids` 中。

### 页面仍显示旧按钮或旧文字

更新并重新构建：

```bash
cd ~/dex_hand/dex_hand_ros2
git pull --ff-only origin agent/mpd20-hardware-deployment
./scripts/start_mpd20_jazzy.sh --build --enable-motion
```

随后重新启动网页节点并刷新浏览器。

### 端口已被占用

```bash
fuser -v 8765/tcp
./scripts/run_hand_web_ui.sh --ros-distro jazzy --port 8766
```

### 出现未绑定变量错误

先更新代码，并确保通过 Bash 启动：

```bash
git pull --ff-only origin agent/mpd20-hardware-deployment
./scripts/run_hand_web_ui.sh --ros-distro jazzy
```

不要使用 `sh scripts/run_hand_web_ui.sh`。

## 9. 停止系统

先停止发送新命令，然后分别在网页节点终端和机械手节点终端按 `Ctrl+C`。控制节点退出时
会尝试保持执行器，但这仍不是硬件断电。如果机械结构需要人工操作或维护，应关闭电机
电源。

网页实现位于：

- `src/dex_hand_ros2/web/index.html`：浏览器界面；
- `src/dex_hand_ros2/dex_hand_ros2/hand_web_ui.py`：HTTP 到 ROS 2 的转换节点；
- `scripts/run_hand_web_ui.sh`：Jazzy/Humble 兼容启动器。

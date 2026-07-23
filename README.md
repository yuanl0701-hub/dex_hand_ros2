# DEX 灵巧手 ROS2 控制项目

基于 ROS2 的 DEX 灵巧手驱动与控制，支持手势切换、自定义手势、PID 闭环控制和实时状态反馈。

---

## 功能概览

| 功能 | 说明 |
|------|------|
| 手势切换 | 预定义 open / fist / vgesture 三种手势，通过话题或交互终端即时执行 |
| 自定义手势 | 通过服务动态注册任意6自由度手势，注册后可通过名称调用 |
| 演示模式 | 自动循环播放内置手势，1秒间隔 |
| 单电机控制 | 精确控制指定电机位置（0-100%），支持 PID 闭环到位 |
| PID 配置 | 实时调整各电机的 Kp / Ki / Kd 参数 |
| 参数配置 | 修改电机 ID、串口波特率 |
| 状态反馈 | 定时发布连接状态，执行结果日志实时输出 |
| 模拟驱动 | 内置 FakeMotorDriver，无需硬件即可测试全部功能 |

---

## 环境要求

- Ubuntu 20.04 / 22.04
- ROS2 (Foxy / Humble)，或 conda 安装的 ROS2
- Python 3.8+

```bash
# 安装依赖
pip install pyserial colcon-common-extensions
```

---

## 快速开始

### 1. 编译

```bash
cd ~/yl/ros2_ws_v1.0
colcon build --packages-select dex_hand_ros2
source install/setup.bash
```

### 2. 启动节点（无硬件模拟模式）

首次使用建议用 fake 模式验证：

```bash
# 终端1 — 启动节点（保持运行）
conda activate env_ros                          # 如果用 conda
source ~/yl/ros2_ws_v1.0/install/setup.bash
python3 -m dex_hand_ros2.hand_node --ros-args -p driver_type:=fake
```

看到以下日志表示启动成功：

```
[INFO] 机械手连接成功，驱动类型: fake，PID 默认 Kp=2.0 Ki=0.1 Kd=0.05
```

### 3. 交互终端（推荐）

```bash
# 终端2 — 手势控制
conda activate env_ros
source ~/yl/ros2_ws_v1.0/install/setup.bash
python3 -m dex_hand_ros2.gesture_cli
```

交互效果：

```
==================================================
  灵巧手手势控制终端
  预定义手势: open | fist | vgesture
  输入 'list' 查看全部手势
  输入 'demo' 启动演示模式
  输入 'quit' 退出
==================================================

手势名> open           ← 输入后回车，立即执行张开手势
手势名> fist           ← 握拳
手势名> vgesture       ← V字手势
手势名> quit           ← 退出
```

---

## 连接真实硬件

将 `driver_type` 和 `serial_port` 对应硬件：

| 驱动类型 | 参数值 | 协议 |
|----------|--------|------|
| MPD20 | `mpd20` | Modbus RTU |
| Feetech | `feetech` | Feetech 协议 |
| HTS20L | `hts20l` | Modbus RTU |

```bash
python3 -m dex_hand_ros2.hand_node --ros-args -p driver_type:=mpd20 -p serial_port:=/dev/ttyUSB0
```

---

## 命令行操作参考

### 手势控制

```bash
# 执行预定义手势
ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_ros2/msg/GestureCmd "{gesture: 'open', speed: 0.8}"
ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_ros2/msg/GestureCmd "{gesture: 'fist', speed: 1.0}"
ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_ros2/msg/GestureCmd "{gesture: 'vgesture', speed: 0.5}"
```

### 自定义手势

```bash
# 注册"捏取"手势（6个电机位置百分比）
ros2 service call /dex_hand/add_gesture dex_hand_ros2/srv/AddGesture \
  "{name: 'pinch', positions: [30,30,80,80,80,80], description: '捏取', duration: 0.5}"

# 执行自定义手势
ros2 topic pub --once /dex_hand/gesture_cmd dex_hand_ros2/msg/GestureCmd "{gesture: 'pinch', speed: 1.0}"
```

### 演示模式

```bash
ros2 service call /dex_hand/demo_gestures std_srvs/srv/Trigger {}
```

### 单电机控制

```bash
# 电机3 开到 80%（直接模式）
ros2 topic pub --once /dex_hand/motor_pos_cmd std_msgs/msg/Int32MultiArray "{data: [3, 80]}"

# 电机3 开到 80%（PID 闭环模式）
ros2 topic pub --once /dex_hand/motor_pos_pid_cmd std_msgs/msg/Int32MultiArray "{data: [3, 80]}"
```

### 参数配置

```bash
# 修改 PID 参数
ros2 topic pub --once /dex_hand/pid_config dex_hand_ros2/msg/PIDconfig "{motor_id: 1, kp: 3.0, ki: 0.2, kd: 0.1}"

# 查看连接状态
ros2 topic echo /dex_hand/status

# 查看所有可用手势
ros2 service call /dex_hand/list_gestures std_srvs/srv/Trigger {}
```

---

## 架构

```
┌──────────────────────┐
│   gesture_cli.py     │  ← 交互终端（可选）
│   (python -m)        │
└────────┬─────────────┘
         │ GestureCmd Topic
         ▼
┌──────────────────────┐
│   DexHandROS2Node    │  ← hand_node.py
│  ┌────────────────┐  │
│  │  RoboticHand   │  │  ← 手势管理 / PID 执行
│  └───────┬────────┘  │
│  ┌───────▼────────┐  │
│  │  MotorDriver   │  │  ← MPD20 / Feetech / Fake
│  └───────┬────────┘  │
│  ┌───────▼────────┐  │
│  │  Protocol      │  │  ← ModbusRTU / FeetechProtocol
│  └───────┬────────┘  │
└──────────┼───────────┘
           │ Serial
           ▼
     ┌──────────┐
     │  机械手   │
     │  6电机   │
     └──────────┘
```

---

## ROS2 接口一览

### Topics

| Topic | 消息类型 | 方向 | 说明 |
|-------|----------|------|------|
| `/dex_hand/gesture_cmd` | `GestureCmd` | 订阅 | 手势控制指令 |
| `/dex_hand/motor_pos_cmd` | `Int32MultiArray` | 订阅 | 单电机位置控制 |
| `/dex_hand/motor_pos_pid_cmd` | `Int32MultiArray` | 订阅 | PID 闭环电机控制 |
| `/dex_hand/pid_config` | `PIDconfig` | 订阅 | PID 参数配置 |
| `/dex_hand/status` | `String` | 发布 | 连接状态 |
| `/dex_hand/motor_state` | `MotorState` | 发布 | 电机状态 |

### Services

| 服务 | 类型 | 说明 |
|------|------|------|
| `/dex_hand/list_gestures` | `Trigger` | 列出所有可用手势 |
| `/dex_hand/demo_gestures` | `Trigger` | 启动演示模式 |
| `/dex_hand/add_gesture` | `AddGesture` | 注册自定义手势 |
| `/dex_hand/run_gesture_pid` | `RunGesturePid` | PID 模式执行手势 |
| `/dex_hand/change_id` | `ChangeId` | 修改电机 ID |
| `/dex_hand/change_baud` | `ChangeBaud` | 修改波特率 |

### ROS2 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `driver_type` | `mpd20` | 驱动类型：mpd20 / feetech / hts20l / fake |
| `serial_port` | `/dev/ttyUSB0` | 串口设备路径 |
| `baudrate` | `115200` | 串口波特率 |
| `status_pub_freq` | `10.0` | 状态发布频率(Hz) |
| `pid_kp` | `2.0` | PID 比例系数 |
| `pid_ki` | `0.1` | PID 积分系数 |
| `pid_kd` | `0.05` | PID 微分系数 |

---

## 项目结构

```
dex_hand_ros2/
├── CMakeLists.txt
├── package.xml
├── setup.py
├── setup.cfg
├── dex_hand_ros2/
│   ├── __init__.py
│   ├── hand_node.py          # ROS2 主节点
│   ├── hand_driver.py         # 驱动层（Modbus/Feetech/PID/手势）
│   ├── config_node.py         # 参数配置节点
│   ├── gesture_cli.py         # 交互式终端
│   ├── msg/
│   │   ├── GestureCmd.msg     # 手势指令消息
│   │   ├── MotorState.msg     # 电机状态消息
│   │   └── PIDconfig.msg      # PID 配置消息
│   ├── srv/
│   │   ├── AddGesture.srv     # 注册手势服务
│   │   ├── RunGesturePid.srv  # PID 手势服务
│   │   ├── ChangeId.srv       # 修改ID服务
│   │   └── ChangeBaud.srv     # 修改波特率服务
│   └── scrips/
│       ├── hand_node.sh
│       └── config_node.sh
└── resource/
    └── dex_hand_ros2
```

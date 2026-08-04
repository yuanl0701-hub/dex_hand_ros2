# DEX Hand 项目部署 README

本文是本仓库的统一部署入口，适用于安全验证、仿真、MPD20 实体手，以及后续接入
新的灵巧手。目标系统为 Ubuntu 22.04 + ROS 2 Humble。

> 当前 MPD20 软件链路已通过纯 Python、伪串口和 ROS 2 Humble 容器验证，但尚未在
> 本人的实体灵巧手上完成验收。示例行程、方向和轴映射不得作为已标定数据使用。

## 1. 部署结构

项目按五类内容组织，新增硬件时不要跨层填写参数：

```text
src/dex_hand_ros2/dex_hand_ros2/
├── core/                 通用控制、安全、手势、PID、轨迹和逻辑驱动接口
├── backends/             MPD20、Feetech、HTS20L 和串行协议适配
├── simulation/           确定性仿真和故障注入
├── commissioning/        只在硬件调试阶段使用的预检/小步移动工具
└── ros/                  ROS 参数到后端设置的集成层

src/dex_hand_ros2/config/
├── runtime/              与硬件无关的控制、安全和 QoS 策略
├── backends/             某类电机/总线的通信和启动策略
├── hand_models/          自由度、逻辑轴、关节映射、URDF 配套和手势
└── deployments/          某一只实体手的端口、物理 ID、行程、方向和限速
```

配置按以下顺序叠加，右侧文件覆盖左侧同名参数：

```text
runtime → backend → hand_model → deployment → launch 命令行覆盖
```

### 参数归属

| 参数 | 应放位置 | 是否可复制到另一只手 |
|---|---|---|
| 看门狗、QoS、状态频率、PID 默认值 | `config/runtime/` | 可作为策略模板 |
| 协议类型、波特率支持、启动检查策略 | `config/backends/` | 同型号电机可复用 |
| 逻辑轴、关节名称、传动关系、手势 | `config/hand_models/` | 同机械结构可复用 |
| 串口、物理总线 ID、raw 范围、方向、限速 | `config/deployments/` | 每只实体手重新确认 |

`motor_ids` 是手型内稳定的逻辑轴编号；`mpd20_device_ids` 是某一只手实际使用的
Modbus 地址。二者按数组顺序映射，因此更换电机地址不再要求修改手势文件。

## 2. 系统准备

安装 Ubuntu 22.04 和 ROS 2 Humble 后：

```bash
cd /path/to/dex_hand_ros2
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-up-to dex_hand_ros2
source install/setup.bash
colcon test --packages-select dex_hand_ros2
colcon test-result --verbose
```

每次打开新终端都需要：

```bash
source /opt/ros/humble/setup.bash
source /path/to/dex_hand_ros2/install/setup.bash
```

## 3. 无硬件安全检查

先确认通用控制链路能够运行：

```bash
ros2 launch dex_hand_ros2 hand.launch.py
```

另一个终端发送手势并观察状态：

```bash
ros2 topic pub --once /dex_hand/gesture_cmd \
  dex_hand_interfaces/msg/GestureCmd \
  "{gesture: open, speed: 1.0}"

ros2 topic echo /dex_hand/status
ros2 topic echo /dex_hand/motor_state
```

默认后端是内存 Mock，不会访问串口或驱动实体电机。

## 4. 仿真部署

轻量仿真和 RViz：

```bash
ros2 launch dex_hand_ros2 simulated_hand.launch.py use_rviz:=true
```

如果要替换手型描述：

```bash
ros2 launch dex_hand_ros2 simulated_hand.launch.py \
  hand_model_config:=/absolute/path/to/your_hand_model.yaml \
  gesture_file:=/absolute/path/to/your_gestures.json
```

Isaac Sim 4.5 使用：

```bash
export ISAAC_SIM_PATH=~/isaacsim
./scripts/run_isaacsim.sh
```

仿真配置只能验证软件接口、时序和故障路径，不能证明真实行程、负载或急停性能。

## 5. MPD20 实体手首次部署

### 5.1 硬件前提

- 电机必须是使用 RS-485 的 MPD20-25S；
- 电机由独立、满足峰值功率的 5–9 V 电源供电；
- 所有电机共地，RS485 A/B 极性正确；
- 总线上每个物理 ID 唯一；
- 现场具有独立于 ROS 和主机的硬件断电急停；
- 第一次运动应卸载或断开连杆，并保证运动范围内无人、无物。

软件急停是主动保持当前位置，不是 STO，也不能代替硬件断电。

### 5.2 为当前实体手建立部署文件

```bash
cp src/dex_hand_ros2/config/deployments/mpd20_hand.example.yaml \
  src/dex_hand_ros2/config/deployments/lab_hand_001.yaml
```

在 `lab_hand_001.yaml` 中填写：

- `serial_port`：优先使用 `/dev/serial/by-id/...`；
- `mpd20_device_ids`：对应逻辑轴 1、2、3……的实际 Modbus 地址；
- `mpd20_raw_min` / `mpd20_raw_max`：装配后的保守机械行程；
- `mpd20_directions`：确保逻辑方向和手型约定一致；
- `mpd20_max_speeds`：首次从 5–10 的低速开始。

同型号共享的 MPD20 后端策略默认设置：

```yaml
serial_retries: 2
hardware_allow_partial_operation: true
```

因此单次事务最多尝试三次；仍无响应的轴会被隔离，其他轴继续完成命令。状态话题会报告
`unavailable_motor_ids` 和逐轴错误计数，反馈恢复后该轴从下一条命令重新加入。需要完整
六轴协调的部署应在自己的覆盖 YAML 中显式设置
`hardware_allow_partial_operation: false`。急停和退出保持不使用宽松语义。

实体运行覆盖还设置 `gesture_execution_mode: direct`：每轴只写一次手势最终目标，实际
运动速度由 `mpd20_max_speeds` 控制。默认仿真运行使用 `smooth`，继续生成五次轨迹
中间点。`direct` 减少串口写入和阶梯式跟随，但 Modbus 逐轴写入并非硬件同步广播。

当前 Jazzy 实机可直接使用：

```bash
./scripts/start_mpd20_jazzy.sh --build --enable-motion
```

脚本默认使用 `/dev/ttyUSB0`、`lab_hand_001.yaml` 和 MPD20 实体手势文件，检查串口
权限及占用后启动。后续无需重建时省略 `--build`。动作写入必须显式给出
`--enable-motion`。

若机械轴定义与 `mpd20_six_axis` 不同，应复制整个手型目录，而不是把轴定义写进
实体部署文件：

```bash
cp -R src/dex_hand_ros2/config/hand_models/mpd20_six_axis \
  src/dex_hand_ros2/config/hand_models/my_hand_model
```

然后修改 `my_hand_model/ros_parameters.yaml` 和手势 JSON，并在 launch 时传入
`hand_model_config`、`gesture_file`。

### 5.3 串口权限和只读预检

```bash
ls -l /dev/serial/by-id/
groups
```

若没有串口权限，将用户加入 `dialout` 后注销并重新登录。不要长期使用 `sudo ros2`。

预检只读取 MPD20 输入寄存器，不下发位置：

```bash
ros2 run dex_hand_ros2 mpd20_preflight \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --baudrate 115200 \
  --ids 1,2,3,4,5,6
```

必须确认所有 ID 均回复、`all_stationary=true`，并核对原始位置。

### 5.4 单轴小步调试

从预检输出读取某个物理 ID 的当前 `raw_position`，只移动 5–10 个计数：

```bash
ros2 run dex_hand_ros2 mpd20_commission \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --id 1 \
  --raw-target REPLACE_WITH_CURRENT_PLUS_5 \
  --max-speed 5 \
  --max-delta 20 \
  --confirm-small-jog
```

逐轴记录物理 ID、机械轴、增大原始值时的运动方向、安全上下限和允许速度。完成所有轴
之前不要使用完整手势。

### 5.5 禁止运动启动

```bash
./scripts/deploy_mpd20_ubuntu.sh \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --config src/dex_hand_ros2/config/deployments/lab_hand_001.yaml
```

脚本会构建、执行只读预检，并保持 `hardware_motion_enabled=false`。确认状态中的
`motor_ids` 是逻辑轴、总线回复来自部署文件中的 `mpd20_device_ids`。

### 5.6 显式启用运动

只有在逐轴标定、硬件急停和空载检查完成后：

```bash
./scripts/deploy_mpd20_ubuntu.sh \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --config src/dex_hand_ros2/config/deployments/lab_hand_001.yaml \
  --enable-motion
```

或直接使用分层 launch：

```bash
ros2 launch dex_hand_ros2 mpd20_hand.launch.py \
  deployment_config:=/absolute/path/lab_hand_001.yaml \
  hand_model_config:=/absolute/path/my_hand_model/ros_parameters.yaml \
  gesture_file:=/absolute/path/my_hand_model/commissioning_gestures.json \
  serial_port:=/dev/serial/by-id/YOUR_ADAPTER \
  motion_enabled:=true
```

先发单轴中间值，再发全手手势：

```bash
ros2 topic pub --once /dex_hand/motor_pos_cmd \
  std_msgs/msg/Int32MultiArray "{data: [1, 50]}"

ros2 topic pub --once /dex_hand/gesture_cmd \
  dex_hand_interfaces/msg/GestureCmd \
  "{gesture: half_open, speed: 1.0}"
```

## 6. 部署另一只相同 MPD20 灵巧手

同型号、同机械结构时不要复制上一只手的标定结果：

1. 复用 `core/`、`backends/mpd20.py` 和相同的 `hand_models/<model>/`；
2. 新建 `config/deployments/<new_hand>.yaml`；
3. 重新确认物理 ID、方向、原始行程和最大速度；
4. 完成只读预检和逐轴小步调试；
5. 空载验证后才启用运动。

如果新手的物理 ID 不同，只改 `mpd20_device_ids`，不改手势中的逻辑轴编号。

## 7. 接入不同电机或不同灵巧手

### 相同位置控制语义、不同电机

1. 在 `dex_hand_ros2/backends/<motor>.py` 实现 `GenericMotorDriver`；
2. 原始编码、寄存器、停止方式和遥测全部留在该后端；
3. 在 `backends/factory.py` 增加该后端的类型化设置；
4. 在 `ros/backend_loader.py` 负责 ROS 参数转换；
5. 新建 `config/backends/<motor>.yaml`；
6. 使用伪传输测试帧、超时、反馈、停止和边界值；
7. 新建实体部署文件，不修改 `core/`。

`change_id` 和 `change_baudrate` 是可选能力；不支持时可以保留基类的
`NotImplementedError`。

### 不同机械结构

新建 `config/hand_models/<model>/`，至少包含：

- `ros_parameters.yaml`：逻辑轴、标签、关节映射和角度范围；
- `gestures.json`：每个手势必须覆盖所有逻辑轴；
- 经过验证的 URDF/mesh（需要可视化或运动学时）。

不要把串口、总线 ID 或实体行程写进手型目录。

### 力矩、速度、触觉或腱绳耦合手

当前核心接口以独立逻辑轴的位置命令和位置反馈为前提。若新硬件主要使用力矩/速度控制、
触觉闭环或复杂腱绳状态，不能只靠 YAML 接入；需要扩展核心命令/反馈能力、ROS 消息和
安全状态机，并重新完成实时性与失效安全验证。

## 8. 验收清单

- [ ] Mock 后端、纯 Python 测试和 ROS 包测试通过；
- [ ] 设备型号、总线、电源、接地和 A/B 极性确认；
- [ ] 稳定串口路径与普通用户权限正常；
- [ ] 物理 ID 唯一，逻辑轴到物理 ID 的映射存档；
- [ ] 所有轴只读预检通过且静止；
- [ ] 每轴方向、保守行程和低速限制逐轴确认；
- [ ] 单轴 50% 命令无碰撞、卡滞或连杆干涉；
- [ ] 软件停止、通信断开、节点退出和看门狗完成实测；
- [ ] 独立硬件断电急停完成实测；
- [ ] 空载通过后逐级加载并记录误差、时间、通信错误和温升。

更详细的 MPD20 寄存器核对和首次调试说明见
[`docs/MPD20_PHYSICAL_DEPLOYMENT.md`](docs/MPD20_PHYSICAL_DEPLOYMENT.md)。

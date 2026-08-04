# MPD20 灵巧手实机部署与复用指南

## 1. 当前结论

当前仓库已经具备可部署到 **MPD20-25S（RS-485）六轴灵巧手**的 ROS 2
软件链路：MPD20 Modbus RTU 驱动、归一化位置映射、只读预检、单轴小步调试、
真机参数文件、真机手势文件、专用 launch、急停/看门狗主动保持和 Ubuntu 部署脚本。

截至 2026-07-30 的证据范围：

- 代码与 MPD20 V1.5 手册、Modbus Poll 图示完成交叉核对；
- 纯 Python 测试、静态检查和 ROS 2 Humble 容器构建/测试通过；
- **没有连接本人的实体灵巧手**，所以电机 ID、手指对应关系、机械安全行程、方向、
  供电裕量、急停响应时间和负载性能仍是“已实现但未实机验证”；
- 在完成本文第 5--8 节前，不应使用 `motion_enabled:=true`。

## 2. 资料核对结果

依据 `文献资料/MPD20/MPD20系列..V1 2.pdf` 和
`文献资料/MPD20/modbus ..V1.pdf`：

| 项目 | MPD20-25S 手册定义 | 当前实现 |
|---|---|---|
| 物理接口 | GND、5--9 V、RS485-A、RS485-B | 外部 USB/串口 RS-485 透明适配器 |
| 串口 | 8N1，默认 115200 bit/s | pyserial 8N1，默认 115200 |
| 当前状态读取 | 功能码 `0x04`，输入寄存器 0--7 | 启动逐 ID 读取全部 8 个寄存器 |
| 当前位置 | 输入寄存器地址 `2` | `read_input_registers(..., 2, 1)` |
| 目标位置 | 保持寄存器地址 `2`，功能码 `0x06` | 每轴标定后写入 |
| 最高速度 | 保持寄存器地址 `3`，范围 0--100 | 配置限定为 1--100，启动时写入 |
| 原始目标范围 | 手册标称 120--850 | 每电机 `raw_min/raw_max`，默认 120/850 |
| ID | 每台设备必须唯一 | 软件采用标准 Modbus 地址 1--247 |
| 波特率代码 | 4=115200、7=38400、8=19200、9=9600、10=4800 | 同表；未猜测 57600 的代码 |

修复前代码把归一化 `0..100` 直接写入目标寄存器，并用功能码 `0x03` 读取当前位置；
这两点均不符合手册，不能作为真机部署版本。现在驱动保持上层 `0..100` 接口，按每轴
标定映射到原始位置，并用 `0x04` 读取反馈。

同目录的原灵巧手论文确认了六个执行自由度：食指、中指、无名指、小指弯曲，拇指弯曲
和拇指对掌/旋转；论文也确认使用 RS-485 扩展板并逐台修改地址。但是论文没有记录
“ID 对应哪根手指”、每轴安全原始范围或正反方向。因此仓库不能诚实地预填这三类数据。

## 3. 硬件前提

1. 电机后缀必须是 **MPD20-25S / RS-485**。MPD20-25P、25U、25A、25FR 分别使用
   PWM、LV-TTL、模拟量或正反转供电，不能直接使用本驱动。
2. RS-485 板必须透明传输 Modbus RTU；若扩展板内部还有自定义主控协议，需要为该板
   另写驱动，不能把它当 `/dev/ttyUSB*` 直接使用。
3. 所有电机 ID 必须唯一。出厂均为同一 ID 时，只能一次连接一台进行改址。
4. 电机电源不能取自普通 USB-RS485 转换器。手册给出单台 5--9 V、额定 5 W、堵转
   12 W；六台堵转功率的算术上限为 72 W。电源、线束、保险和接插件需要按实际同时
   动作比例及工程裕量核算，并设置硬件断电急停。
5. 软件急停是“停止继续下发并把当前位置写回为目标”的主动保持，不是认证的 STO，
   也不能替代切断执行器电源的硬件急停。

## 4. Ubuntu 22.04 / ROS 2 Humble 准备

```bash
cd /path/to/dex_hand_ros2
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble
colcon build --symlink-install --packages-up-to dex_hand_ros2
source install/setup.bash
colcon test --packages-select dex_hand_ros2
colcon test-result --verbose
```

建议使用稳定设备名：

```bash
ls -l /dev/serial/by-id/
```

若当前用户没有串口权限，将用户加入 `dialout` 后注销并重新登录；不要以长期运行
`sudo ros2 ...` 的方式绕过权限。

## 5. 首次分配电机 ID

仅在确认恢复方法并且总线上只接一台待改址电机时使用配置节点。主控制节点和配置节点
不能同时打开同一串口。

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run dex_hand_ros2 config_node --ros-args \
  -p serial_port:=/dev/serial/by-id/YOUR_ADAPTER \
  -p baudrate:=115200 \
  -p motor_ids:="[1]"
```

另一个终端将当前 ID 1 改为 2：

```bash
ros2 service call /dex_hand/change_id dex_hand_interfaces/srv/ChangeId \
  "{command: '1>2'}"
```

收到确认后断电、断开该电机、接入下一台并重复。最终建议 ID 1--6，但 ID 与轴的对应
关系由装配人员决定并记录。不要在多台仍共享默认 ID 时发送改址命令。

## 6. 只读总线预检

先断开连杆负载或确保手指活动范围内无人、无物，再上电并等待电机停止。预检工具不会
写任何寄存器：

```bash
ros2 run dex_hand_ros2 mpd20_preflight \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --baudrate 115200 \
  --ids 1,2,3,4,5,6
```

通过条件：六个 ID 均有回复、`all_stationary=true`、
`all_within_calibration=true`。输出会保留每轴硬件/软件版本、原始位置、原始负载和
移动标志。手册注明速度、电压、温度字段暂不可用，不能基于这些字段实现保护判断。

## 7. 单轴映射和方向确认

`mpd20_commission` 只允许单轴、显式确认、最多 50 个原始计数的小步移动，默认上限为
20。先从预检 JSON 读取该轴 `raw_position`，选择相差 5--10 的目标；下例的目标值必须
替换，不能照抄：

```bash
ros2 run dex_hand_ros2 mpd20_commission \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --id 1 \
  --raw-target REPLACE_WITH_CURRENT_PLUS_5 \
  --max-speed 5 \
  --max-delta 20 \
  --confirm-small-jog
```

逐轴记录：

| ID | 机械轴 | 原始值增大时的动作 | 安全 raw_min | 安全 raw_max | direction |
|---|---|---|---:|---:|---:|
| 1 | 实测填写 | 打开/闭合 | 实测填写 | 实测填写 | 1 或 -1 |

标定原则：逻辑位置 `100` 始终表示该轴的“手张开”端点，逻辑位置 `0` 表示“手闭合”
端点。若原始值增大使该轴张开，`direction=1`；若原始值增大使该轴闭合，
`direction=-1`。`raw_min/raw_max` 应是连杆装好后不会撞机械限位的保守范围，而不是
无条件照搬电机本体的 120/850。

## 8. 写入本手配置

复制模板后只修改副本：

```bash
cp src/dex_hand_ros2/config/deployments/mpd20_hand.example.yaml \
  src/dex_hand_ros2/config/deployments/lab_hand_001.yaml
```

在 `lab_hand_001.yaml` 中填写：

- `mpd20_device_ids`：按手型逻辑轴顺序排列的实际唯一 Modbus ID；
- `mpd20_raw_min` / `mpd20_raw_max`：装配后的保守安全范围；
- `mpd20_directions`：使归一化 100 对应张开；
- `mpd20_max_speeds`：从 5--10 开始，实测后再提高；

逻辑轴、标签、关节映射和手势属于
`config/hand_models/mpd20_six_axis/`。模板手势只有 `open`、`half_open`、`fist`
三个全轴姿态；通用仿真手势不能未经机械映射和空载验证直接用于实物。需要改变看门狗等
运行策略时，应复制 `config/runtime/physical_conservative.yaml`，不要写入实体标定文件。

## 9. 启动和首轮无负载验收

部署脚本默认构建、只读预检并以禁止动作方式启动：

```bash
./scripts/deploy_mpd20_ubuntu.sh \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --config src/dex_hand_ros2/config/deployments/lab_hand_001.yaml
```

确认状态中的六个标签、连接状态和 `hardware_motion_enabled=false`。完成前述标定并布置
硬件急停后，才显式允许动作：

```bash
./scripts/deploy_mpd20_ubuntu.sh \
  --port /dev/serial/by-id/YOUR_ADAPTER \
  --config src/dex_hand_ros2/config/deployments/lab_hand_001.yaml \
  --enable-motion
```

先测试单轴中间值，再测试手势：

```bash
ros2 topic pub --once /dex_hand/motor_pos_cmd std_msgs/msg/Int32MultiArray \
  "{data: [1, 50]}"

ros2 topic pub --once /dex_hand/gesture_cmd \
  dex_hand_interfaces/msg/GestureCmd \
  "{gesture: half_open, speed: 1.0}"
```

急停和恢复：

```bash
ros2 service call /dex_hand/emergency_stop std_srvs/srv/SetBool "{data: true}"
ros2 service call /dex_hand/emergency_stop std_srvs/srv/SetBool "{data: false}"
```

MPD20 后端策略默认启用 `hardware_allow_partial_operation=true`。每个 Modbus 事务会先按
`serial_retries` 重试；耗尽后只把该轴标记为离线，当前多轴命令继续驱动其他在线轴。
离线轴在 `/dex_hand/motor_state` 中报告 `connected=false`、位置 `-1`，并出现在状态 JSON
的 `unavailable_motor_ids`、`motor_failure_counts` 和 `motor_last_errors` 中。后台反馈重新
读通后会重设该轴限速，并从**下一条**命令恢复，不会在当前手势中途突然追赶目标。
若某轴在手势开始前已经离线，平滑轨迹只为其余具有有效起点反馈的轴生成。

这种降级模式不能保证完整手势或抓取几何。若应用要求六轴协调，应在部署覆盖文件中设
`hardware_allow_partial_operation: false`，恢复任意单轴失败即中止命令的严格模式。
无论采用哪种模式，急停、看门狗和节点退出的主动保持仍是严格路径：任何轴无法确认保持
都会报告 `fault`，不能视为可靠停止。看门狗超时会进入可人工恢复的 `stopped`。

首次验收必须记录命令时间、反馈位置、移动标志、掉线轴、重试次数、急停请求到停止的
时间，并在空载通过后再逐级增加负载。

## 10. 实机验收清单

- [ ] 型号确认为 MPD20-25S，RS485 A/B 极性及 GND/VCC 接线复核；
- [ ] 电源、线束、保险、硬件断电急停满足六电机最坏工况；
- [ ] ID 唯一，波特率一致，稳定设备路径和 `dialout` 权限正常；
- [ ] 只读预检六轴均回复、静止、反馈落在标定范围；
- [ ] 六个 ID 到机械轴的对应关系逐轴确认并存档；
- [ ] 每轴 `raw_min/raw_max/direction/max_speed` 在空载下确认；
- [ ] 单轴 50% 命令方向正确，无撞限位、卡滞或连杆干涉；
- [ ] `open`、`half_open`、`fist` 空载按顺序通过；
- [ ] 运动中软件急停、通信断开、节点退出和看门狗超时均完成实测；
- [ ] 硬件断电急停独立于 ROS/主机并完成实测；
- [ ] 负载逐级增加，记录位置误差、动作时间、通信错误和温升；
- [ ] PID 接口保持禁用，直到独立完成每轴闭环辨识和增益整定。

## 11. 系统复用性

| 新系统情形 | 复用性 | 通常需要修改 |
|---|---|---|
| 同为六轴 MPD20-25S、相同机械结构 | 高 | 真机 YAML、ID/标签、每轴范围/方向/速度、手势 |
| MPD20-25S，但电机数量或机械结构变化 | 中高 | 上述配置、完整手势向量、Web UI、URDF/关节映射、运动学 |
| 电机数量相同，但换成其他 Modbus 寄存器表 | 中 | 新驱动适配器、工厂注册、参数、协议测试、launch |
| 换成 CAN/PWM/厂商 SDK 电机 | 中低 | 新传输层和 `GenericMotorDriver` 实现，依赖和故障语义 |
| 增加触觉/力控/接触规划 | 低到中 | 新消息、传感器驱动、实时控制、安全策略和实验验证 |

可直接复用的部分：`DriverConfig` 的归一化域、`HandController`、手势库、五次轨迹、
软件 PID、ROS 话题/服务、安全状态机、仿真后端和测试框架。驱动通过
`GenericMotorDriver` 隔离，换硬件不需要重写控制算法。

当前仍有六轴模型假设的部分：

- `virtual_dex_hand.urdf.xacro`、RViz 和 Isaac/Revo2 映射固定为六个独立输入；
- 随仓库提供的真机手势文件固定包含 ID 1--6；
- 默认节点参数有六个标签和六组关节映射，但可由自定义 YAML 覆盖；
- `Int32MultiArray` 指令和 JSON 状态为兼容接口，类型约束较弱。

Web UI 已从 `/dex_hand/status` 动态读取逻辑轴、标签和手势，不再固定校验 ID 1--6。

## 12. 部署另一只新灵巧手时的修改点

1. **同型号 MPD20 手**：复用手型目录，新建一份 `deployments/<hand>.yaml`，不要复制
   上一只实体手的标定结果。
2. **不同电机数量**：新建手型目录并修改逻辑 `motor_ids`、`motor_labels`、关节映射和
   每个手势的完整位置集合；在部署文件中填写同长度的 `mpd20_device_ids` 和标定数组。
   Web UI 会动态适配，URDF/关节映射仍需针对机械结构修改。
3. **不同机械传动**：重新标定方向和安全范围，重写手势；若要关节角/指尖位置控制，
   必须提供实际几何、轴系、连杆参数并替换当前名义 URDF/运动学。
4. **不同电机协议**：在 `backends/<motor>.py` 新增 `GenericMotorDriver` 子类，在
   `backends/factory.py` 注册类型化 backend，并为读写帧、单位映射、超时、故障和
   停止语义增加伪传输测试；随后新建后端 YAML 和实体部署 YAML。
5. **不同安全要求**：软件主动保持不能视为硬件安全功能。按新电机能力加入使能、制动、
   STO 或继电器控制，并单独完成风险分析与停机时间测量。

换手时不应修改 `core/controller.py` 来适配寄存器，也不应把原始编码值写进手势文件；
原始单位只属于具体驱动和实体标定层，手势始终保留在统一的 `0..100` 逻辑域。

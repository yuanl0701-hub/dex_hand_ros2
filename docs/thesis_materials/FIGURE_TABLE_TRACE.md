# 图表—证据追溯表

| 论文材料 | 原始证据 | 统计单位 | 纳入/排除说明 |
|---|---|---|---|
| 表 1 软件验证 | E00 build summary、E01 logs、E02/E04 summaries、E05/E06 summaries | 构建、测试或确定性场景 | 仅报告通过数量与范围 |
| 图 1 / 表 2 时序 | `E03_timing/*/command_latency.csv`、`state_interarrival.csv` | 每条件 5 次独立运行 | 全部 9000 个匹配观测纳入；408.009 ms 未删除 |
| 图 2 / 表 3 安全 | `E04_safety/safety_timing.csv` | 同一会话内 20 次技术重复 | 软件状态范围；不推断物理断力矩 |
| 图 3 轨迹 | `E05_trajectory/raw/trajectory_samples.csv` 的 T07 | 1 个确定性展示场景 | 表 1 同时汇总全部 15 个场景 |
| 图 4 / 表 4 控制器 | `E06_pid/raw/pid_samples.csv`、`pid_summary.csv` | 每控制器 4 个确定性场景 | 理想积分对象；不作显著性检验 |
| 不纳入正文 | `E07_resources/*` | 无有效节点资源单位 | 监测到 `ros2 run` 包装进程而非实际节点 |

## 数据完整性

- 实验归档 SHA-256：`47920f495003c87861902d370fc900138ba4f8929b442b1628c52972fc453f3d`
- 归档内部校验：153 个条目，`checksums.sha256` 全部通过。
- `run_status.csv`：34 个步骤均记录为 `completed`，退出码均为 0。
- 人工干预：两个节点在数据采集结束后的清理阶段由操作员发送 SIGINT；此事实需在局限性中披露。
- 图表数据排除：无。CPU 压力条件中的 408.009 ms 观测保留在分析与完整范围插图中。

## 复现命令

```bash
cd /path/to/dex_hand_ros2
MPLCONFIGDIR=/tmp/dex_hand_matplotlib \
  python3 docs/thesis_materials/make_paper_materials.py \
  /path/to/20260724T114059Z_2e70cf1_full.tar.gz
```

默认输出至 `docs/thesis_materials/generated/`，其中包含 SVG、PDF、600 dpi PNG、
论文表格、图源数据和 `provenance.json`。


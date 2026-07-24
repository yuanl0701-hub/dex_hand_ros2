# Package-level algorithm tooling

No physical hand measurements are stored in this repository.

`tools/export_trajectory.py` exports deterministic theoretical output from the
implemented quintic algorithm. Its metadata labels the output
`algorithm_output`; it must not be presented as hardware tracking data.

The workspace-level `scripts/run_thesis_experiments.sh` additionally collects
Ubuntu/ROS 2 virtual-backend evidence under `experiments/runs/`. Raw data retain
timestamps, units, configuration, evidence scope, and Git commit.

Hardware measurements still require the actual hand, verified motor
configuration, calibration, and a synchronized logging procedure.

# Experiment tooling

No real measurements are stored in this repository.

`tools/export_trajectory.py` exports deterministic theoretical output from the
implemented quintic algorithm. Its metadata labels the output
`algorithm_output`; it must not be presented as hardware tracking data.

Planned hardware measurements require Ubuntu/ROS 2, the actual hand, verified
motor configuration, and a synchronized logging procedure. Raw data must retain
timestamps, units, configuration, and Git commit. Empty result locations use
`.gitkeep` and contain no fabricated curves or values.

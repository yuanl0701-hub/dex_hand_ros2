import csv
import json

from dex_hand_ros2.experiment import ExperimentMetadata, write_trajectory_csv
from dex_hand_ros2.trajectory import QuinticTrajectory


def test_trajectory_export_has_units_and_metadata(tmp_path):
    metadata = ExperimentMetadata.create(
        data_kind="algorithm_output",
        units="normalized_percent",
        git_commit="test-commit",
        configuration={"duration_s": 1.0},
    )
    data_path, metadata_path = write_trajectory_csv(
        tmp_path / "trajectory.csv",
        QuinticTrajectory(0, 1, 1).sample(0.5),
        metadata,
    )
    with data_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    assert rows[0][0] == "time_s"
    assert rows[-1][0] == "1.0"
    loaded = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert loaded["data_kind"] == "algorithm_output"
    assert loaded["git_commit"] == "test-commit"

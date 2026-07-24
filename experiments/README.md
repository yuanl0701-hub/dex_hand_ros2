# Experiment Evidence

`E00_environment/` contains the historical Ubuntu deployment failure imported
from commit `cd0657a`. It is retained as troubleshooting evidence and must not
be reported as a successful post-fix build.

New experiment runs are created by:

```bash
./scripts/run_thesis_experiments.sh
```

Generated directories:

- `runs/<run-id>/`: raw data, logs, summaries, tables, figures, metadata, and
  checksums.
- `archives/<run-id>.tar.gz`: portable evidence bundle.

Both directories are ignored by Git. Review `run_status.csv` and
`EVIDENCE_INDEX.md` before using a run in the thesis. A command returning a
non-zero exit code remains in the evidence bundle and must not be represented
as successful.

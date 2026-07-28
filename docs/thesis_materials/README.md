# Thesis experiment materials

This directory converts the audited ROS 2 experiment archive into manuscript
materials without modifying the archive.

## Generate

```bash
MPLCONFIGDIR=/tmp/dex_hand_matplotlib \
  /opt/anaconda3/bin/python docs/thesis_materials/make_paper_materials.py \
  /Users/yuanlei/Downloads/20260724T114059Z_2e70cf1_full.tar.gz
```

## Outputs

- `MANUSCRIPT_MATERIALS_ZH.md`: ready-to-adapt Chinese Methods, Results,
  Discussion, captions and terminology.
- `FIGURE_TABLE_TRACE.md`: claim-to-source trace and evidence exclusions.
- `generated/figures`: editable SVG/PDF and 600 dpi PNG figures.
- `generated/tables`: analysis-ready CSV tables.
- `generated/source_data`: the exact values used by each figure.
- `generated/paper_tables.tex`: `booktabs`-style LaTeX tables.
- `generated/provenance.json`: archive hash, sample-unit definitions and exclusions.

E07 is intentionally omitted from manuscript figures because its resource
monitor sampled the ROS 2 CLI wrapper rather than the child node.

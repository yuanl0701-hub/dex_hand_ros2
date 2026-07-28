# Revo2 right-hand Isaac Sim asset

This directory contains the complete dependency closure needed to load the
supplied Revo2 right-hand entry layer:

- `revo2_right_hand.usd`: entry layer and variant selections;
- `revo2_right_hand_base.usd`: visual geometry and materials;
- `revo2_right_hand_physics.usd`: rigid bodies, collisions, drives, limits,
  articulation root and mimic joints;
- `revo2_right_hand_sensor.usd`: supplied sensor layer.

The entry layer uses relative references, so these four files must remain in
the same directory. `OmniPBR.mdl` is an Isaac Sim built-in material; the
separate `Collected_g2/SubUSDs/materials` and `textures` folders are not in the
dependency closure of this right-hand asset and are therefore not duplicated
here.

## Provenance

The files were copied byte-for-byte on 2026-07-28 from the user-provided
project asset directory:

```text
/Users/yuanlei/MINE/AIRs_Intern/Collected_g2/SubUSDs/
```

No asset file was edited or converted. The source collection did not include
a standalone license file next to these USD layers. Repository publication
and redistribution therefore rely on the project owner's authorization and
should follow any upstream terms that apply to the original collection.

Use `SHA256SUMS` to verify that a Git checkout contains the exact copied
layers:

```bash
cd assets/revo2_right_hand
sha256sum -c SHA256SUMS
```

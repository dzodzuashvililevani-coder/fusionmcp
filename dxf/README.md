# dxf/

**Purpose:** 2D cut files. What actually goes to the laser, CNC, or printer.

**Data stored here:** **Vector** -- `.dxf` (and `.svg` if a cutter needs it).
Technically text, but machine-generated. Never hand-edit: regenerate from
Fusion instead, or the file and the model silently diverge.

## Portals

| Portal | Pattern | Type | Holds |
|---|---|---|---|
| `cut____` | `frame_v*_cut.dxf` | Vector | Full nested sheet, ready to cut |
| `parts____` | `part_*.dxf` | Vector | Single part, for test cuts |
| `test____` | [kerf_test.dxf](kerf_test.dxf) | Vector | Squares + screw holes to calibrate your cutter. `frame kerf-test` |

## Kerf -- do this before the real cut

The blade or beam removes material. Generate the coupon, cut it, measure the
resulting square:

```powershell
frame kerf-test          # writes dxf/kerf_test.dxf
```

`kerf = nominal - measured`. Put the answer in [`params.yaml`](../params.yaml)
`stock.kerf_mm`. The same coupon carries an M2 and an M3 hole at the sizes this
design actually drills, so it also tells you whether `holes.screw_clearance_mm`
lets a screw through *this* plywood.

This is the only DXF generated outside Fusion -- it has no model to export
from, and you need it before the first real cut.

Rough starting points: laser 0.15-0.25mm, CNC = endmill diameter, jigsaw ~1.5mm.

Skip this and every hole comes out oversized and every slot loose -- which on a
wooden frame means motor screws that will not stay tight.

## Layer convention

| Layer | Meaning |
|---|---|
| `CUT` | Through cuts, outer profile |
| `HOLES` | Drilled/cut holes -- motor bolts, FC standoffs, zipties |
| `ENGRAVE` | Surface marks -- part labels, centre lines, fold references |
| `REFERENCE` | Construction geometry. **Do not cut.** Delete before sending |

## Before sending to the cutter

1. `frame check` passes with zero failures
2. Kerf measured and in `params.yaml` -- `export_dxf` writes NOMINAL geometry
   and expects the cutter's software to apply the offset. Do not compensate twice
3. `REFERENCE` layer removed
4. Everything fits inside 250x250mm
5. Grain direction considered -- arms should run *along* the grain, not across

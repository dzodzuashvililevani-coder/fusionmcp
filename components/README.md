# components/

**Purpose:** Everything the tools need to know about physical parts -- what they
weigh, where they sit, what they are made of.

**Data stored here:** YAML only. No code, no images.
Photos of these parts live in [`photos/own/`](../photos/README.md).

## Portals

| Portal | File | Type | Holds | Edited by |
|---|---|---|---|---|
| `loadout____` | [loadout.yaml](loadout.yaml) | YAML | Every component's `mass_g` and `pos_mm` `[x,y,z]` | **You**, from `docs/measurements.md` |
| `materials____` | [materials.yaml](materials.yaml) | YAML | Wood density table, g/cm^3 | Rarely -- reference data |

## What is *not* here

Motors and the frame itself are **not** listed in `loadout.yaml`. The mass
budget adds them automatically:

- motor mass and count come from `params.yaml -> motors`
- motor positions come from the geometry solver
- frame mass is computed from cut area x thickness x density

Listing them by hand would double-count them.

## Coordinates

`pos_mm: [x, y, z]` measured from the frame centre, in millimetres.
`+x` = right, `+y` = forward (nose), `+z` = up.
`x` and `y` drive the CG check. `z` only affects the reported CG height --
a rough estimate is fine.

## Adding a component

1. Weigh it (0.1g kitchen scale is enough).
2. Decide roughly where it mounts relative to the centre.
3. Add a row to `loadout.yaml`.
4. `frame mass` -- watch the CG offset. Over 5mm and the validator complains.

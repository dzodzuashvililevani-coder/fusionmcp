# cad/

**Purpose:** Fusion model exports. The 3D side of the project.

**Data stored here:** **Binary CAD** -- `.f3d`, `.step`, `.stl`.
Not diffable. Git stores a complete copy of every version, so these files
bloat the repo fast.

## Portals

| Portal | Pattern | Type | Holds |
|---|---|---|---|
| `model____` | `frame_v*.f3d` | Binary CAD | Fusion archive, full parametric history |
| `step____` | `frame_v*.step` | Binary CAD | Neutral solid, opens in any CAD |
| `print____` | `*.stl` | Binary CAD | Meshes for 3D-printed parts (camera mount, standoffs) |

Empty until the first Fusion session. Real source of truth is
[`params.yaml`](../params.yaml) -- these are outputs.

## Naming

```
frame_v3.f3d          milestone 3 of the frame
camera_mount_v1.stl   a printed part
```

Version numbers only, no dates -- the git log has the dates.

## Commit policy

Commit a **milestone**, not every save. Roughly: when `frame check` passes
and you would be willing to cut it.

Before committing, note in [`docs/build-log.md`](../docs/build-log.md) which
`params.yaml` values the model was built from. That link is what makes an old
`.f3d` useful later.

If this folder passes ~50MB, move it to Git LFS.

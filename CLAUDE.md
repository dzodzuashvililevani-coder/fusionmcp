# drone-wood-frame -- master index

Parametric wooden FPV drone frame cut from 250x250mm stock, built around
components salvaged from a Temu toy drone.

**`params.yaml` is the single source of truth.** Every calculation, every
validation rule, and the Fusion model all derive from it. Change a number
there, re-run `frame report`, rebuild.

---

## Portals

Jump straight to the thing you need. Every folder also has its own `README.md`
with a finer-grained table.

| Portal | Path | Type | Holds |
|---|---|---|---|
| `params____` | [params.yaml](params.yaml) | YAML | **Start here.** All design numbers |
| `loadout____` | [components/loadout.yaml](components/loadout.yaml) | YAML | Component masses + positions for CG |
| `materials____` | [components/materials.yaml](components/materials.yaml) | YAML | Wood density table |
| `loader____` | [src/frame_tools/params.py](src/frame_tools/params.py) | Python | Find the project root, load YAML, screw + hole sizes |
| `geometry____` | [src/frame_tools/geometry.py](src/frame_tools/geometry.py) | Python | Arm-length solver, motor coordinates |
| `mass____` | [src/frame_tools/mass.py](src/frame_tools/mass.py) | Python | Mass budget, centre of gravity |
| `thrust____` | [src/frame_tools/thrust.py](src/frame_tools/thrust.py) | Python | Thrust-to-weight, hover throttle |
| `validate____` | [src/frame_tools/validate.py](src/frame_tools/validate.py) | Python | Pre-cut design rules |
| `fusionout____` | [src/frame_tools/fusion.py](src/frame_tools/fusion.py) | Python | Builds the Fusion payload + User Parameter table |
| `dxfout____` | [src/frame_tools/dxf_out.py](src/frame_tools/dxf_out.py) | Python | Kerf calibration coupon (the only non-Fusion DXF) |
| `cli____` | [src/frame_tools/cli.py](src/frame_tools/cli.py) | Python | `frame` command entry point |
| `measure____` | [docs/measurements.md](docs/measurements.md) | Markdown | Caliper checklist to fill in |
| `buildlog____` | [docs/build-log.md](docs/build-log.md) | Markdown | What actually happened |
| `planner____` | [docs/planner/](docs/planner/README.md) | Markdown | Planner role contract for Plan-Gate-Verify |
| `inbox____` | [docs/implementer/](docs/implementer/README.md) | Markdown | Implementer inbox: plans, gates, error fixes |
| `fusion____` | [fusion_scripts/](fusion_scripts/README.md) | Python (in Fusion) | Scripts that run inside Fusion |
| `handoff____` | [fusion_scripts/frame_params.json](fusion_scripts/frame_params.json) | JSON | The generated handoff. `frame fusion -o` writes it |
| `mcp____` | [.mcp.json](.mcp.json) | JSON | Fusion MCP endpoint, picked up by Claude Code |
| `editor____` | [.vscode/](.vscode/README.md) | JSON | Interpreter path, pytest, debug config |
| `cad____` | [cad/](cad/README.md) | Binary CAD | `.f3d` / `.step` exports |
| `cut____` | [dxf/](dxf/README.md) | Vector | `.dxf` files for the cutter |
| `photos____` | [photos/](photos/README.md) | Raster | Part photos + web reference images |
| `tests____` | [tests/](tests/README.md) | Python | Design invariants |
| `install____` | [install-fusion-scripts.ps1](install-fusion-scripts.ps1) | PowerShell | Register `fusion_scripts/` with Fusion, as shims back to the repo |
| `carry____` | [carry-session.ps1](carry-session.ps1) | PowerShell | Move a Claude conversation into this project's session store |

---

## Data type vocabulary

Used in every folder's portal table, so the type is always unambiguous.

| Tag | Extensions | Diffable | Notes |
|---|---|---|---|
| **YAML** | `.yaml` | yes | Hand-edited data. Comments allowed and encouraged |
| **Python** | `.py` | yes | Runs in the project venv |
| **Python (in Fusion)** | `.py` | yes | Runs in Fusion's own interpreter. `adsk.*` only exists there |
| **Markdown** | `.md` | yes | Docs and indexes |
| **JSON** | `.json` | yes | Machine output only. Never hand-edit |
| **PowerShell** | `.ps1` | yes | Windows helper scripts |
| **Vector** | `.dxf`, `.svg` | text, but do not hand-edit | Generated cut geometry |
| **Binary CAD** | `.f3d`, `.step`, `.stl` | **no** | Git stores whole copies. Commit milestones only |
| **Raster** | `.jpg`, `.png` | **no** | Photos and web references. Downscale before committing |

There is no JavaScript in this project. If a browser tool ever gets added it
goes in a new `web/` folder with its own README.

---

## Commands

```powershell
frame report      # geometry + mass + checks
frame geometry    # arm length, motor coordinates
frame mass        # mass budget and centre of gravity
frame check       # pre-cut validation, exits nonzero on failure
frame fusion      # resolved numbers as JSON on stdout
frame fusion -o   # ...written to fusion_scripts/frame_params.json instead
frame kerf-test   # write dxf/kerf_test.dxf to calibrate the cutter
pytest            # design invariants
```

Setup, once:

```powershell
uv venv
uv pip install -e ".[dev,dxf]"
```

## Conventions

- Coordinates are **millimetres**, origin at the frame centre,
  `+x` = right, `+y` = forward (nose), `+z` = up.
- Masses are **grams**. Densities are **g/cm^3**.
- Never hardcode a dimension in Python. Add it to `params.yaml` and read it.
- **Every folder has a `README.md`** with a portal table. Add a row when you
  add a file. `pytest` fails if a folder is missing its README.
- **`params.yaml` as committed must pass `frame check`.** A repo whose default
  numbers fail its own validator teaches you to ignore the validator. If a
  constraint can be *solved for*, solve it in `geometry.py` rather than only
  reporting it in `validate.py`.
- **Geometry is solved exactly once**, in `geometry.py`. Fusion and the DXF
  consume `frame fusion` output; nothing downstream recomputes a dimension.
- Inside Fusion, **every API length is centimetres** regardless of document
  units. Convert at the boundary with `_common.mm()` / `to_mm()`.
- For multi-agent work, use [docs/planner/](docs/planner/README.md) and
  [docs/implementer/](docs/implementer/README.md): plans and sign-offs are
  files, gates are hard halts, and the planner is not the implementer.

# drone-wood-frame

A parametric wooden FPV drone frame, cut from 250x250mm stock, using salvaged
components (motors, ESCs, flight controller, camera) from a Temu toy drone.

`params.yaml` is the single source of truth. Everything else - the calculators,
the validation, the Fusion model, the DXF cut files - is derived from it.

## Setup

```powershell
uv venv
uv pip install -e ".[dev,dxf]"
```

`dev` gives you `pytest`, `dxf` gives you `ezdxf` for the kerf coupon. The base
install needs only `pyyaml`.

Check it worked:

```powershell
frame report      # must end "0 failures"
pytest -q
```

Then register the Fusion-side scripts, once:

```powershell
.\install-fusion-scripts.ps1
```

That does not copy them -- it installs shims that call back into
[`fusion_scripts/`](fusion_scripts/README.md), so editing a script and
re-running it in Fusion picks up the change with no restart and no second copy
to keep in sync.

## Use

```powershell
frame report      # geometry + mass + checks (start here)
frame geometry    # arm length, motor coordinates
frame mass        # mass budget and centre of gravity
frame check       # pre-cut validation - exits nonzero if something is wrong
frame fusion      # resolved numbers as JSON, for the Fusion MCP
frame fusion -o   # ...written to fusion_scripts/frame_params.json instead
frame kerf-test   # write dxf/kerf_test.dxf, to measure your cutter's kerf
```

## Workflow

1. Measure your salvaged parts -> fill in `docs/measurements.md`
2. Copy those numbers into `params.yaml` and `components/loadout.yaml`
3. `frame report` until every check passes
4. `frame kerf-test`, cut the coupon, put the measured kerf back in `params.yaml`
5. `frame fusion -o`, then run `frame_sync_params` in Fusion to load the parameters
6. Model the plate and arms against those parameters, naming cut sketches `CUT_*`
7. `frame_nest_parts` and `frame_mass_check` in Fusion, then `frame_export_dxf` -> `dxf/`
8. Cut, assemble, and log what actually happened in `docs/build-log.md`

Steps 5-7 are the [`fusion_scripts/`](fusion_scripts/README.md) run order.
Step 4 before step 7, not after: an uncalibrated kerf means every motor screw
hole comes out oversized, and a loose motor mount on a wooden arm does not stay
tight.

## Fusion MCP

Fusion -> Preferences -> General -> API -> enable **Fusion MCP Server** (port 27182).

The endpoint is already committed in [`.mcp.json`](.mcp.json), so Claude Code
picks it up from this folder -- approve the server when it prompts, then run
`/mcp` to confirm it connected. Nothing else to configure.

**Use `127.0.0.1`, not `localhost`.** The server checks the Host header and
answers `403 Forbidden` to anything else, including `localhost:27182`, which is
the same address by any other measure. Verified against a live server on
2026-08-24: `127.0.0.1` initializes and lists four tools
(`fusion_mcp_read`, `fusion_mcp_update`, `fusion_mcp_execute`,
`fusion_mcp_electronics_read`); `localhost` is refused before the handshake.

To register it globally instead of per-project:

```powershell
claude mcp add --transport http fusion http://127.0.0.1:27182/mcp
```

Fusion must be **open, with a design active**, or the tools connect but have
nothing to act on.

**MCP explores; scripts repeat.** Use the MCP conversationally to try things,
then lock whatever worked into a script in `fusion_scripts/` so the next frame
does not need the conversation again.

## Finding things

**[CLAUDE.md](CLAUDE.md) is the master index** - portal table for the whole
project plus the data-type vocabulary. Start there.

Every folder then has its own `README.md` with a finer-grained portal table
saying what it holds and in what format:

| Folder | Holds | Data type |
|---|---|---|
| [components/](components/README.md) | Part masses, positions, wood densities | YAML |
| [src/frame_tools/](src/frame_tools/README.md) | The calculation engine | Python |
| [tests/](tests/README.md) | Design invariants | Python |
| [fusion_scripts/](fusion_scripts/README.md) | Scripts that run *inside* Fusion | Python (in Fusion) |
| [docs/](docs/README.md) | Measurements in, lessons out | Markdown |
| [cad/](cad/README.md) | Fusion exports | Binary CAD |
| [dxf/](dxf/README.md) | 2D cut files | Vector |
| [photos/](photos/README.md) | Part photos + sourced web references | Raster |

`pytest` fails if a folder is missing its README or its portal table, so the
index cannot silently rot.

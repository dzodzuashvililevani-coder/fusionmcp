# src/

**Purpose:** Container for the installable Python package. No logic lives at
this level -- it exists so `pip install -e .` resolves `frame_tools` cleanly
without the repo root leaking onto `sys.path`.

**Data stored here:** Python packages only.

## Portals

| Portal | Path | Type | Holds |
|---|---|---|---|
| `tools____` | [frame_tools/](frame_tools/README.md) | Python | The calculation engine -- geometry, mass, thrust, validation, CLI |

A second package would go beside `frame_tools/` with its own README.

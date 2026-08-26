# .vscode/

**Purpose:** Editor configuration, committed so the setup is reproducible.

**Data stored here:** JSON (JSONC -- comments are allowed in these files).

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `settings____` | [settings.json](settings.json) | JSON | Interpreter path, `src/` + Fusion stubs on the analysis path, pytest on |
| `extensions____` | [extensions.json](extensions.json) | JSON | Recommended extensions, prompted on first open |
| `launch____` | [launch.json](launch.json) | JSON | Debug config for `frame report` |

The interpreter path points at `.venv/Scripts/python.exe`, so run
`uv venv && uv pip install -e .` before opening or Pylance will not resolve
`frame_tools`.

## Why `adsk` resolves

`python.analysis.extraPaths` also points at Fusion's own API stubs:

```
${env:APPDATA}/Autodesk/Autodesk Fusion 360/API/Python/defs
```

That is what stops Pylance marking `import adsk.core` as unresolved in
[`fusion_scripts/`](../fusion_scripts/README.md). It resolves through `$env:`
rather than a literal path, so it is portable across Windows machines and stays
committable. If those files are missing, open Fusion once -- it writes them.

The stubs are for *editing only*. Nothing in `.venv` can import `adsk`, and
`pytest` fakes it instead -- see [`tests/fusion_stub.py`](../tests/fusion_stub.py).

Machine-specific overrides belong in `settings.local.json` (gitignored), not here.

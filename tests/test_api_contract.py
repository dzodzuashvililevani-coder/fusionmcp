"""Keep the committed OpenAPI snapshot in lockstep with the live app."""
from __future__ import annotations

import json
import subprocess
import sys

from fcc.api.app import GENERATED_HEADER, create_app
from frame_tools.params import project_root
from frame_tools.report_api import build_report, openapi_bytes

ROOT = project_root()


def live_schema() -> dict:
    app = create_app(report_provider=lambda: build_report(ROOT), root=ROOT)
    return app.openapi()


def test_openapi_snapshot_matches_live_app():
    snapshot = (ROOT / "web" / "src" / "openapi.json").read_bytes()
    expected = json.loads(snapshot)

    assert live_schema() == expected
    assert openapi_bytes(ROOT) == snapshot


def test_openapi_snapshot_carries_generated_header():
    schema = live_schema()

    assert schema["x-generated"] == GENERATED_HEADER
    assert "Generated, do not edit" in schema["info"]["description"]


def test_openapi_regeneration_command_matches_committed_snapshot(tmp_path):
    out = tmp_path / "openapi.json"

    result = subprocess.run(
        [sys.executable, "-m", "frame_tools.report_api", "--write-openapi", str(out)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert out.read_bytes() == (ROOT / "web" / "src" / "openapi.json").read_bytes()

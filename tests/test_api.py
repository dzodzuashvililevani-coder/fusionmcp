"""Validate the FCC FastAPI layer."""
from __future__ import annotations

from pathlib import Path
import shutil

from fastapi.testclient import TestClient
import pytest

from fcc.api.app import create_app
from frame_tools.report_api import build_report
from frame_tools.params import project_root

ROOT = project_root()


def copy_project_data(tmp_path: Path) -> None:
    for directory in ("components", "docs"):
        (tmp_path / directory).mkdir(exist_ok=True)
    for relpath in (
        "fields.yaml",
        "params.yaml",
        "components/materials.yaml",
        "components/loadout.yaml",
        "docs/measurements.md",
    ):
        shutil.copy2(ROOT / relpath, tmp_path / relpath)


def client_for(tmp_path: Path) -> TestClient:
    return TestClient(create_app(report_provider=lambda: build_report(tmp_path), root=tmp_path))


def read_data_bytes(root: Path) -> dict[str, bytes]:
    return {
        relpath: (root / relpath).read_bytes()
        for relpath in ("params.yaml", "components/loadout.yaml", "docs/measurements.md")
    }


def changed_line_numbers(before: bytes, after: bytes) -> list[int]:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    assert len(before_lines) == len(after_lines)
    return [
        index
        for index, (old, new) in enumerate(zip(before_lines, after_lines), start=1)
        if old != new
    ]


def test_api_package_does_not_import_frame_tools():
    findings = []
    for path in (ROOT / "src" / "fcc" / "api").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from frame_tools" in text or "import frame_tools" in text:
            findings.append(path.relative_to(ROOT).as_posix())

    assert not findings


def test_fields_endpoint_returns_spec_values_status_revision_and_lines(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)

    response = client.get("/api/fields")

    assert response.status_code == 200
    payload = response.json()
    assert payload["revision"]
    assert len(payload["fields"]) == 21
    stock = next(field for field in payload["fields"] if field["id"] == "stock_thickness")
    assert stock == {
        "id": "stock_thickness",
        "question": "Measure actual wood stock thickness with calipers.",
        "unit": "mm",
        "min": 1.0,
        "max": 8.0,
        "file": "params.yaml",
        "line": 11,
        "current_value": 3.0,
        "status": "todo",
        "measurement_label": "Actual thickness (measure, do not trust the label)",
        "group": "stock",
    }


def test_report_endpoint_uses_injected_provider_and_preserves_check_text(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)

    response = client.get("/api/report")

    assert response.status_code == 200
    payload = response.json()
    assert payload["headline"] == [
        {"label": "Arm radius", "value": 91.9, "unit": "mm"},
        {"label": "All-up weight", "value": 139.1, "unit": "g"},
        {"label": "Thrust-to-weight", "value": 3.45, "unit": ""},
        {"label": "CG offset", "value": 0.74, "unit": "mm"},
    ]
    stock = next(check for check in payload["checks"] if check["name"] == "stock thickness")
    assert stock["status"] == "ok"
    assert stock["detail"] == "3.0mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended"


def test_preview_returns_writer_diff_and_writes_nothing(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    before = read_data_bytes(tmp_path)

    response = client.post("/api/fields/stock_thickness/preview", json={"value": "3.2"})

    assert response.status_code == 200
    assert "-  thickness_mm: 3.0          # TODO measure with caliper" in response.json()["diff"]
    assert "+  thickness_mm: 3.2          # TODO measure with caliper" in response.json()["diff"]
    assert read_data_bytes(tmp_path) == before


def test_write_endpoint_updates_value_checklist_report_and_revision(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    fields = client.get("/api/fields").json()
    before_params = (tmp_path / "params.yaml").read_bytes()
    before_measurements = (tmp_path / "docs" / "measurements.md").read_bytes()

    response = client.post(
        "/api/fields/stock_thickness/value",
        json={"value": "3.2", "revision": fields["revision"]},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["result"]["file"] == "params.yaml"
    assert payload["result"]["line_number"] == 11
    assert payload["result"]["checklist_ticked"] is True
    assert payload["warnings"] == []
    assert payload["revision"] != fields["revision"]
    assert payload["report"]["checks"]
    assert "10 passed" not in str(payload["report"])

    after_params = (tmp_path / "params.yaml").read_bytes()
    after_measurements = (tmp_path / "docs" / "measurements.md").read_bytes()
    assert changed_line_numbers(before_params, after_params) == [11]
    assert after_params.count(b"\r\n") == before_params.count(b"\r\n")
    assert after_params.count(b"\n") == before_params.count(b"\n")
    assert changed_line_numbers(before_measurements, after_measurements) == [45]
    assert after_measurements.count(b"\r\n") == before_measurements.count(b"\r\n")
    assert after_measurements.count(b"\n") == before_measurements.count(b"\n")


def test_failing_value_still_writes_and_returns_failed_check_verbatim(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    revision = client.get("/api/fields").json()["revision"]

    response = client.post(
        "/api/fields/stock_thickness/value",
        json={"value": "0.5", "revision": revision},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["warnings"] == ["stock_thickness is outside the expected 1..8 mm range"]
    failed = next(check for check in payload["report"]["checks"] if check["status"] == "fail")
    assert failed["name"] == "stock thickness"
    assert failed["detail"] == "0.5mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended"
    assert "thickness_mm: 0.5" in (tmp_path / "params.yaml").read_text(encoding="utf-8")


def test_unknown_field_returns_404_with_valid_ids(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    revision = client.get("/api/fields").json()["revision"]

    response = client.post("/api/fields/nope/value", json={"value": "1", "revision": revision})

    assert response.status_code == 404
    assert "unknown field id 'nope'" in response.json()["detail"]
    assert "stock_thickness" in response.json()["detail"]


def test_non_numeric_value_returns_422_and_writes_nothing(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    before = read_data_bytes(tmp_path)
    revision = client.get("/api/fields").json()["revision"]

    response = client.post(
        "/api/fields/stock_thickness/value",
        json={"value": "not-a-number", "revision": revision},
    )

    assert response.status_code == 422
    assert read_data_bytes(tmp_path) == before


def test_stale_revision_returns_409_with_current_values_and_writes_nothing(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)
    old_revision = client.get("/api/fields").json()["revision"]
    (tmp_path / "params.yaml").write_bytes(
        (tmp_path / "params.yaml").read_bytes().replace(b"thickness_mm: 3.0", b"thickness_mm: 3.1", 1)
    )
    before = read_data_bytes(tmp_path)

    response = client.post(
        "/api/fields/stock_thickness/value",
        json={"value": "3.2", "revision": old_revision},
    )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["detail"] == "project files changed outside the app; reload before saving"
    stock = next(field for field in detail["current"]["fields"] if field["id"] == "stock_thickness")
    assert stock["current_value"] == 3.1
    assert read_data_bytes(tmp_path) == before


def test_health_returns_ok_and_project_root(tmp_path):
    copy_project_data(tmp_path)
    client = client_for(tmp_path)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "project_root": str(tmp_path)}


@pytest.mark.parametrize("word", ["path", "file", "filename", "dir", "root"])
def test_openapi_accepts_no_filesystem_targets(word, tmp_path):
    copy_project_data(tmp_path)
    schema = client_for(tmp_path).get("/openapi.json").json()

    offenders = []
    for route, methods in schema["paths"].items():
        for method, operation in methods.items():
            for parameter in operation.get("parameters", []):
                if parameter.get("name", "").lower() == word:
                    offenders.append(f"{method.upper()} {route} parameter {word}")
            body = operation.get("requestBody", {})
            for content in body.get("content", {}).values():
                schema_ref = content.get("schema", {}).get("$ref", "")
                name = schema_ref.rsplit("/", 1)[-1].lower()
                model = schema.get("components", {}).get("schemas", {}).get(schema_ref.rsplit("/", 1)[-1], {})
                properties = set(model.get("properties", {}))
                if word in properties or word == name:
                    offenders.append(f"{method.upper()} {route} body {word}")

    assert not offenders


def test_no_cors_middleware_is_installed(tmp_path):
    copy_project_data(tmp_path)
    app = create_app(report_provider=lambda: build_report(tmp_path), root=tmp_path)

    assert all("CORSMiddleware" not in repr(middleware.cls) for middleware in app.user_middleware)

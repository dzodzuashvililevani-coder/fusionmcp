"""FastAPI app factory for the FCC API."""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI

from .models import ApiState, ReportProvider
from .routes import build_router


GENERATED_HEADER = (
    "Generated, do not edit. Regenerate with "
    ".\\.venv\\Scripts\\python.exe -m frame_tools.report_api --write-openapi web\\src\\openapi.json"
)


def create_app(report_provider: ReportProvider, root: Path) -> FastAPI:
    app = FastAPI(
        title="FCC Workstation API",
        version="1.0.0",
        description=GENERATED_HEADER,
    )
    app.include_router(build_router(ApiState(root=root, report_provider=report_provider)))

    original_openapi = app.openapi

    def openapi_with_header():
        if app.openapi_schema:
            return app.openapi_schema
        schema = original_openapi()
        schema["x-generated"] = GENERATED_HEADER
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = openapi_with_header
    return app

"""Routes for the domain-blind FCC API."""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from fastapi import APIRouter, HTTPException

from fcc.errors import AmbiguousLabel, FccError, LabelNotFound, PathRefused, SpecError, UnsurgicalEdit
from fcc.fields import FieldSpec, coerce_value, current_value, field_by_id, is_todo_guess, load_fields
from fcc.writer import locate, preview, write_value

from .models import (
    ApiState,
    FieldInfo,
    FieldsResponse,
    HealthResponse,
    PreviewRequest,
    PreviewResponse,
    Report,
    StaleRevisionResponse,
    ValueWriteRequest,
    ValueWriteResponse,
    WriteResultModel,
)

DATA_FILES = ("params.yaml", "components/loadout.yaml", "docs/measurements.md")


def build_router(state: ApiState) -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(ok=True, project_root=str(state.root))

    @router.get("/fields", response_model=FieldsResponse)
    def fields() -> FieldsResponse:
        return _fields_response(state.root)

    @router.get("/report", response_model=Report)
    def report() -> Report:
        return state.report_provider()

    @router.post("/fields/{field_id}/preview", response_model=PreviewResponse)
    def field_preview(field_id: str, payload: PreviewRequest) -> PreviewResponse:
        try:
            field = field_by_id(field_id, root=state.root)
            value = coerce_value(field, payload.value)
            return PreviewResponse(diff=preview(field, value, root=state.root))
        except FccError as exc:
            raise _http_error(exc) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.post(
        "/fields/{field_id}/value",
        response_model=ValueWriteResponse,
        responses={409: {"model": StaleRevisionResponse}},
    )
    def field_value(field_id: str, payload: ValueWriteRequest) -> ValueWriteResponse:
        if payload.revision != revision(state.root):
            raise HTTPException(
                status_code=409,
                detail=StaleRevisionResponse(
                    detail="project files changed outside the app; reload before saving",
                    current=_fields_response(state.root),
                ).model_dump(),
            )
        try:
            field = field_by_id(field_id, root=state.root)
            value = coerce_value(field, payload.value)
            warnings = _warnings(field, value)
            result = write_value(field, value, root=state.root)
        except FccError as exc:
            raise _http_error(exc) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return ValueWriteResponse(
            result=WriteResultModel(**result.__dict__),
            report=state.report_provider(),
            revision=revision(state.root),
            warnings=warnings,
        )

    return router


def _fields_response(root: Path) -> FieldsResponse:
    return FieldsResponse(
        revision=revision(root),
        fields=[field_info(field, root) for field in load_fields(root=root)],
    )


def field_info(field: FieldSpec, root: Path) -> FieldInfo:
    line_number, _ = locate(field, root=root)
    return FieldInfo(
        id=field.id,
        question=field.question,
        unit=field.unit,
        min=field.min,
        max=field.max,
        file=field.file,
        line=line_number,
        current_value=current_value(field, root=root),
        status="todo" if is_todo_guess(field, root) else "measured",
        measurement_label=field.measurement_label,
        group=_group(field),
    )


def revision(root: Path) -> str:
    digest = sha256()
    for relpath in DATA_FILES:
        stat = (root / relpath).stat()
        digest.update(relpath.encode("utf-8"))
        digest.update(str(stat.st_mtime_ns).encode("ascii"))
        digest.update(str(stat.st_size).encode("ascii"))
    return digest.hexdigest()[:16]


def _warnings(field: FieldSpec, value: int | float) -> list[str]:
    if field.min <= value <= field.max:
        return []
    return [f"{field.id} is outside the expected {field.min:g}..{field.max:g} {field.unit} range"]


def _group(field: FieldSpec) -> str:
    if field.file == "params.yaml":
        return field.key_path.split(".", 1)[0]
    if field.file == "components/loadout.yaml":
        return "loadout"
    return "measurements"


def _http_error(exc: FccError) -> HTTPException:
    if isinstance(exc, SpecError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, UnsurgicalEdit):
        return HTTPException(status_code=409, detail=str(exc))
    if isinstance(exc, PathRefused):
        return HTTPException(status_code=400, detail=str(exc))
    if isinstance(exc, (LabelNotFound, AmbiguousLabel)):
        return HTTPException(status_code=500, detail=str(exc))
    return HTTPException(status_code=500, detail=str(exc))

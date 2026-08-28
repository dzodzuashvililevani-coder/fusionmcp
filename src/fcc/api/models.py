"""Pydantic models for the FCC API contract."""
from __future__ import annotations

from typing import Any, Callable, Literal

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    ok: bool
    project_root: str


class FieldInfo(BaseModel):
    id: str
    question: str
    unit: str
    min: float
    max: float
    file: str
    line: int
    current_value: Any
    status: Literal["measured", "todo"]
    measurement_label: str | None
    group: str


class FieldsResponse(BaseModel):
    revision: str
    fields: list[FieldInfo]


class PreviewRequest(BaseModel):
    value: str | int | float


class PreviewResponse(BaseModel):
    diff: str


class ValueWriteRequest(BaseModel):
    value: str | int | float
    revision: str


class WriteResultModel(BaseModel):
    file: str
    line_number: int
    old_text: str
    new_text: str
    checklist_ticked: bool


class HeadlineItem(BaseModel):
    label: str
    value: float | str
    unit: str


class CheckModel(BaseModel):
    status: Literal["ok", "warn", "fail"]
    name: str
    detail: str


class Report(BaseModel):
    headline: list[HeadlineItem]
    checks: list[CheckModel]


class ValueWriteResponse(BaseModel):
    result: WriteResultModel
    report: Report
    revision: str
    warnings: list[str]


class StaleRevisionResponse(BaseModel):
    detail: str
    current: FieldsResponse


ReportProvider = Callable[[], Report]


class ApiState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    root: Any
    report_provider: ReportProvider

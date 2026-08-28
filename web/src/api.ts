import type { components } from "./api.d";

export type FieldInfo = components["schemas"]["FieldInfo"];
export type FieldsResponse = components["schemas"]["FieldsResponse"];
export type Report = components["schemas"]["Report"];
export type CheckModel = components["schemas"]["CheckModel"];
export type HeadlineItem = components["schemas"]["HeadlineItem"];
export type ValueWriteResponse = components["schemas"]["ValueWriteResponse"];
export type StaleRevisionResponse = components["schemas"]["StaleRevisionResponse"];

type ApiPayload = Record<string, unknown>;

export class ApiError extends Error {
  readonly status: number;
  readonly payload: unknown;

  constructor(status: number, payload: unknown) {
    const message = extractMessage(payload) || `request failed with status ${status}`;
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.payload = payload;
  }
}

export async function fetchFields(): Promise<FieldsResponse> {
  return request<FieldsResponse>("/api/fields");
}

export async function fetchReport(): Promise<Report> {
  return request<Report>("/api/report");
}

export async function previewField(fieldId: string, value: string): Promise<string> {
  const response = await request<components["schemas"]["PreviewResponse"]>(
    `/api/fields/${encodeURIComponent(fieldId)}/preview`,
    {
      method: "POST",
      body: JSON.stringify({ value })
    }
  );
  return response.diff;
}

export async function saveField(
  fieldId: string,
  value: string,
  revision: string
): Promise<ValueWriteResponse> {
  return request<ValueWriteResponse>(`/api/fields/${encodeURIComponent(fieldId)}/value`, {
    method: "POST",
    body: JSON.stringify({ value, revision })
  });
}

export function stalePayload(error: unknown): StaleRevisionResponse | null {
  if (!(error instanceof ApiError) || error.status !== 409) {
    return null;
  }
  const payload = error.payload as { detail?: unknown };
  const detail = payload?.detail;
  if (isObject(detail) && "current" in detail && "detail" in detail) {
    return detail as StaleRevisionResponse;
  }
  if (isObject(error.payload) && "current" in error.payload && "detail" in error.payload) {
    return error.payload as StaleRevisionResponse;
  }
  return null;
}

async function request<T>(url: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...init.headers
    }
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    throw new ApiError(response.status, payload);
  }
  return payload as T;
}

function extractMessage(payload: unknown): string | null {
  if (!isObject(payload) || !("detail" in payload)) {
    return null;
  }
  const detail = (payload as ApiPayload).detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (isObject(detail) && typeof detail.detail === "string") {
    return detail.detail;
  }
  return null;
}

function isObject(value: unknown): value is ApiPayload {
  return typeof value === "object" && value !== null;
}

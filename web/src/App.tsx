import { useEffect, useMemo, useState, type ReactNode } from "react";
import FieldCard, { type PreviewState, type SaveState } from "./FieldCard";
import FieldQueue from "./FieldQueue";
import ReportPanel from "./ReportPanel";
import {
  ApiError,
  fetchFields,
  fetchReport,
  previewField,
  saveField,
  stalePayload,
  type FieldInfo,
  type FieldsResponse,
  type Report
} from "./api";

type ThemeChoice = "system" | "light" | "dark";

export default function App() {
  const [fieldsResponse, setFieldsResponse] = useState<FieldsResponse | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [preview, setPreview] = useState<PreviewState>({ status: "empty" });
  const [saveState, setSaveState] = useState<SaveState>({ status: "idle" });
  const [theme, setTheme] = useState<ThemeChoice>(() => readTheme());
  const [loadError, setLoadError] = useState<string | null>(null);
  const [lastSaveHadFailure, setLastSaveHadFailure] = useState(false);

  const fields = fieldsResponse?.fields ?? [];
  const selectedField = useMemo(
    () => fields.find((field) => field.id === selectedId) ?? fields[0] ?? null,
    [fields, selectedId]
  );

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    void loadWorkstation();
  }, []);

  useEffect(() => {
    if (selectedField && selectedField.id !== selectedId) {
      setSelectedId(selectedField.id);
    }
  }, [selectedField, selectedId]);

  useEffect(() => {
    if (!selectedField) {
      return;
    }
    setInputValue(formatValue(selectedField.current_value));
    setPreview({ status: "empty" });
    setSaveState({ status: "idle" });
  }, [selectedField?.id, selectedField?.current_value]);

  useEffect(() => {
    if (!selectedField) {
      return;
    }
    const trimmed = inputValue.trim();
    if (!trimmed || Number.isNaN(Number(trimmed))) {
      setPreview({ status: "empty" });
      return;
    }
    const handle = window.setTimeout(() => {
      setPreview({ status: "loading" });
      previewField(selectedField.id, trimmed)
        .then((diff) => setPreview({ status: "ready", diff }))
        .catch((error: unknown) => setPreview({ status: "error", message: messageFor(error) }));
    }, 250);
    return () => window.clearTimeout(handle);
  }, [inputValue, selectedField]);

  const measured = fields.filter((field) => field.status === "measured").length;
  const progress = `${measured} of ${fields.length}`;
  const outOfRange = Boolean(selectedField && isNumeric(inputValue) && !withinRange(selectedField, Number(inputValue)));

  async function loadWorkstation() {
    setLoadError(null);
    try {
      const [nextFields, nextReport] = await Promise.all([fetchFields(), fetchReport()]);
      setFieldsResponse(nextFields);
      setReport(nextReport);
      setLastSaveHadFailure(false);
    } catch (error) {
      setLoadError(messageFor(error));
    }
  }

  function handleSelect(field: FieldInfo) {
    setSelectedId(field.id);
  }

  function handleTheme(nextTheme: ThemeChoice) {
    setTheme(nextTheme);
    window.localStorage.setItem("workstation-theme", nextTheme);
  }

  async function handleSave() {
    if (!selectedField || !fieldsResponse || !isNumeric(inputValue)) {
      setPreview({ status: "empty" });
      return;
    }
    setSaveState({ status: "saving" });
    try {
      const response = await saveField(selectedField.id, inputValue.trim(), fieldsResponse.revision);
      setReport(response.report);
      setFieldsResponse(updateFieldsAfterSave(fieldsResponse, selectedField.id, inputValue.trim(), response.revision));
      setSaveState({
        status: "saved",
        message: `${response.result.file}:${response.result.line_number}; checklist ${
          response.result.checklist_ticked ? "ticked" : "unchanged"
        }`,
        warnings: response.warnings
      });
      setLastSaveHadFailure(response.report.checks.some((check) => check.status === "fail"));
    } catch (error) {
      const stale = stalePayload(error);
      if (stale) {
        setFieldsResponse(stale.current);
        setSaveState({ status: "stale", message: stale.detail });
      } else {
        setSaveState({ status: "error", message: messageFor(error) });
      }
    }
  }

  return (
    <main className="app-shell">
      <header className="topline">
        <div>
          <p className="section-label">frame workstation</p>
          <h1>Measurement Bench</h1>
        </div>
        <div className="topline-actions">
          <div className="progress-pill" aria-label="Measurement progress">
            <span>{progress}</span>
            <code>[==-]</code>
          </div>
          <div className="theme-switch" role="group" aria-label="Theme">
            {(["system", "light", "dark"] as ThemeChoice[]).map((choice) => (
              <button
                type="button"
                key={choice}
                data-active={theme === choice ? "true" : "false"}
                onClick={() => handleTheme(choice)}
              >
                {choice}
              </button>
            ))}
          </div>
        </div>
      </header>

      {loadError ? <div className="notice notice-fail">{loadError}</div> : null}

      <section className="workstation-grid">
        <Pane label="TO MEASURE" hint={progress}>
          <FieldQueue fields={fields} selectedId={selectedField?.id ?? null} onSelect={handleSelect} />
        </Pane>

        <Pane label="CURRENT MEASUREMENT" hint={selectedField ? selectedField.status : ""}>
          <FieldCard
            field={selectedField}
            value={inputValue}
            preview={preview}
            saveState={saveState}
            outOfRange={outOfRange}
            onValueChange={setInputValue}
            onSave={handleSave}
            onReload={loadWorkstation}
          />
          <div className="viewer-slot">
            <span className="section-label">phase 7 component viewer slot</span>
          </div>
        </Pane>

        <Pane label="DESIGN STATE" hint={report ? `${report.checks.length} checks` : ""}>
          <ReportPanel report={report} showFailureBanner={lastSaveHadFailure} />
        </Pane>
      </section>
    </main>
  );
}

function Pane({ label, hint, children }: { label: string; hint: string; children: ReactNode }) {
  return (
    <section className="pane">
      <header className="pane-head">
        <span>{label}</span>
        <small>{hint}</small>
      </header>
      {children}
    </section>
  );
}

function updateFieldsAfterSave(
  current: FieldsResponse,
  fieldId: string,
  value: string,
  revision: string
): FieldsResponse {
  return {
    revision,
    fields: current.fields.map((field) =>
      field.id === fieldId ? { ...field, current_value: Number(value), status: "measured" } : field
    )
  };
}

function formatValue(value: unknown): string {
  return typeof value === "number" || typeof value === "string" ? String(value) : "";
}

function isNumeric(value: string): boolean {
  return value.trim() !== "" && !Number.isNaN(Number(value));
}

function withinRange(field: FieldInfo, value: number): boolean {
  return field.min <= value && value <= field.max;
}

function messageFor(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "request failed";
}

function readTheme(): ThemeChoice {
  const stored = window.localStorage.getItem("workstation-theme");
  return stored === "light" || stored === "dark" ? stored : "system";
}

function applyTheme(theme: ThemeChoice) {
  if (theme === "system") {
    document.documentElement.removeAttribute("data-theme");
  } else {
    document.documentElement.dataset.theme = theme;
  }
}

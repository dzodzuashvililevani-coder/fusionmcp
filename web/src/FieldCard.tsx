import type { FieldInfo } from "./api";

export type PreviewState =
  | { status: "empty" }
  | { status: "loading" }
  | { status: "ready"; diff: string }
  | { status: "error"; message: string };

export type SaveState =
  | { status: "idle" }
  | { status: "saving" }
  | { status: "saved"; message: string; warnings: string[] }
  | { status: "stale"; message: string }
  | { status: "error"; message: string };

type FieldCardProps = {
  field: FieldInfo | null;
  value: string;
  preview: PreviewState;
  saveState: SaveState;
  outOfRange: boolean;
  onValueChange: (value: string) => void;
  onSave: () => void;
  onReload: () => void;
};

export default function FieldCard({
  field,
  value,
  preview,
  saveState,
  outOfRange,
  onValueChange,
  onSave,
  onReload
}: FieldCardProps) {
  if (!field) {
    return (
      <div className="field-card empty-card">
        <p className="empty-copy">No fields returned by the API.</p>
      </div>
    );
  }

  return (
    <form
      className="field-card"
      onSubmit={(event) => {
        event.preventDefault();
        onSave();
      }}
    >
      <div className="target-line">
        {field.file}:{field.line}
      </div>
      <h2>{field.question}</h2>
      <div className="field-meta">{field.id}</div>

      <label className="value-shell">
        <span className="section-label">value</span>
        <span className="value-row">
          <input
            aria-label={field.question}
            inputMode="decimal"
            value={value}
            onChange={(event) => onValueChange(event.target.value)}
          />
          <span className="unit-chip">{field.unit}</span>
          <span className="range-chip">
            {formatNumber(field.min)}..{formatNumber(field.max)}
          </span>
        </span>
      </label>

      {outOfRange ? (
        <div className="notice notice-warn" role="status">
          <strong>WARN</strong>
          <span>
            {field.id} is outside {formatNumber(field.min)}..{formatNumber(field.max)}{" "}
            {field.unit}; still saved when confirmed.
          </span>
        </div>
      ) : null}

      <PreviewBlock field={field} preview={preview} />

      {saveState.status === "saved" ? (
        <div className="notice notice-ok" role="status">
          <strong>SAVED</strong>
          <span>{saveState.message}</span>
        </div>
      ) : null}

      {saveState.status === "stale" ? (
        <div className="notice notice-fail" role="alert">
          <strong>STALE</strong>
          <span>{saveState.message}</span>
          <button className="link-button" type="button" onClick={onReload}>
            Reload
          </button>
        </div>
      ) : null}

      {saveState.status === "error" ? (
        <div className="notice notice-fail" role="alert">
          <strong>ERROR</strong>
          <span>{saveState.message}</span>
        </div>
      ) : null}

      <div className="action-row">
        <button className="primary-button" type="submit" disabled={saveState.status === "saving"}>
          {saveState.status === "saving" ? "Saving" : "Save"}
        </button>
        <button className="secondary-button" type="button" onClick={onReload}>
          Reload
        </button>
        <span className="key-hint">Enter saves</span>
      </div>
    </form>
  );
}

function PreviewBlock({ field, preview }: { field: FieldInfo; preview: PreviewState }) {
  if (preview.status === "empty") {
    return <pre className="diff-block faint">enter a number to preview the change</pre>;
  }
  if (preview.status === "loading") {
    return <pre className="diff-block faint">preview pending</pre>;
  }
  if (preview.status === "error") {
    return <pre className="diff-block diff-error">{preview.message}</pre>;
  }

  const blocks = splitUnifiedDiff(preview.diff);
  const hasChecklist = field.measurement_label ? blocks.some((block) => block.file === "docs/measurements.md") : false;

  return (
    <div className="preview-stack" aria-label="Server diff preview">
      {blocks.map((block) => (
        <section className="diff-block" key={block.file}>
          <div className="diff-title">{block.file}</div>
          <pre>
            {block.lines.map((line, index) => (
              <span className={diffLineClass(line)} key={`${line}-${index}`}>
                {line || " "}
                {"\n"}
              </span>
            ))}
          </pre>
        </section>
      ))}
      {!field.measurement_label ? (
        <pre className="diff-block faint">docs/measurements.md - no checklist line for this field</pre>
      ) : null}
    </div>
  );
}

type DiffBlock = {
  file: string;
  lines: string[];
};

function splitUnifiedDiff(diff: string): DiffBlock[] {
  const blocks: DiffBlock[] = [];
  let current: DiffBlock | null = null;
  for (const line of diff.split(/\r?\n/)) {
    if (line.startsWith("+++ b/")) {
      current = { file: line.slice("+++ b/".length), lines: [] };
      blocks.push(current);
      continue;
    }
    if (line.startsWith("--- ")) {
      continue;
    }
    if (!current) {
      current = { file: "preview", lines: [] };
      blocks.push(current);
    }
    if (line.length > 0) {
      current.lines.push(line);
    }
  }
  return blocks;
}

function diffLineClass(line: string): string {
  if (line.startsWith("+")) {
    return "diff-plus";
  }
  if (line.startsWith("-")) {
    return "diff-minus";
  }
  return "diff-context";
}

function formatNumber(value: number): string {
  return Number.isInteger(value) ? value.toFixed(0) : String(value);
}

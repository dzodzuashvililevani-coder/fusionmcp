import type { FieldInfo } from "./api";

export type FieldGroup = {
  group: string;
  fields: FieldInfo[];
};

type FieldQueueProps = {
  fields: FieldInfo[];
  selectedId: string | null;
  onSelect: (field: FieldInfo) => void;
};

export function groupFields(fields: FieldInfo[]): FieldGroup[] {
  const byGroup = new Map<string, FieldInfo[]>();
  for (const field of fields) {
    const existing = byGroup.get(field.group);
    if (existing) {
      existing.push(field);
    } else {
      byGroup.set(field.group, [field]);
    }
  }
  return Array.from(byGroup, ([group, grouped]) => ({ group, fields: grouped }));
}

export default function FieldQueue({ fields, selectedId, onSelect }: FieldQueueProps) {
  return (
    <nav className="field-queue" aria-label="Measurement fields">
      {groupFields(fields).map((group) => (
        <section className="field-group" key={group.group}>
          <h3>{group.group}</h3>
          <div className="field-list">
            {group.fields.map((field) => (
              <button
                className="field-row"
                data-active={field.id === selectedId ? "true" : "false"}
                data-status={field.status}
                type="button"
                key={field.id}
                onClick={() => onSelect(field)}
              >
                <span className="status-dot" aria-hidden="true" />
                <span className="field-row-id">{field.id}</span>
                <span className="field-row-value">
                  {formatCurrentValue(field.current_value)} {field.unit}
                </span>
              </button>
            ))}
          </div>
        </section>
      ))}
    </nav>
  );
}

function formatCurrentValue(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toFixed(0) : String(value);
  }
  if (typeof value === "string") {
    return value;
  }
  return "";
}

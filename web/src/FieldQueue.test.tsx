import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import FieldQueue from "./FieldQueue";
import type { FieldInfo } from "./api";

describe("FieldQueue", () => {
  it("renders fields supplied at runtime", () => {
    const field: FieldInfo = {
      id: "invented_probe_span",
      question: "Read a fixture-only probe span.",
      unit: "ticks",
      min: 2,
      max: 7,
      file: "fixture.yaml",
      line: 4,
      current_value: 5,
      status: "todo",
      measurement_label: null,
      group: "fixture"
    };

    render(<FieldQueue fields={[field]} selectedId={null} onSelect={vi.fn()} />);

    expect(screen.getByText("invented_probe_span")).toBeInTheDocument();
    expect(screen.getByText("5 ticks")).toBeInTheDocument();
  });
});

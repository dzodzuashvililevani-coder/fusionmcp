# Review: user UI manifesto

**Created:** 2026-08-29
**Reviews:** [user-UI-manifesto.md](user-UI-manifesto.md)
**Status:** brainstorming review, not an implementation plan
**Companion:** [review-user-UI-manifesto-alignment.md](review-user-UI-manifesto-alignment.md)
— Claude's parallel review: how the manifesto fits the decisions already made,
what of it is already built, and what to do first.

---

## 1. What I understand you are asking for

You are not only describing a nicer measurement screen. You are describing a
future **creation workspace**: a local-first UI where a user starts with an
idea, gives the system a project document and any hardware they already have,
and then works with AI-assisted tools to turn that idea into a physical
skeleton.

In this context, "skeleton" means the real-world physical structure of the
project: frame, layout, component placement, materials, blueprints, 2D/3D
models, measurements, and the reasoning behind all of it.

The UI should help the user move through this sequence:

1. Describe the idea.
2. Identify available hardware and missing hardware.
3. Gather requirements and constraints.
4. Explore possible physical layouts.
5. Measure real components.
6. Generate and validate 2D/3D design artifacts.
7. Record design decisions and rejected alternatives.
8. Produce a final report that explains how to build the physical project and
   why it is designed that way.

The most important part of the manifesto is this: **the UI is a workspace made
of tools, not a fixed page.** The system should show the right tool when the
current project state calls for it, and keep less relevant tools available
without cluttering the workspace.

---

## 2. Strongest ideas in the manifesto

### 2.1 The project-document-first flow is right

Starting from a written project document is the correct move. It gives the AI a
source of intent before it starts suggesting parts, shapes, or materials.

Without this document, the AI has to infer too much. With it, the system can
ask better questions:

- What is the mission?
- What must not change?
- What hardware is already fixed?
- What constraints are real?
- What is just a preference?
- What facts are missing before design can begin?

That document becomes the first source of truth for the project's purpose. The
physical model and blueprints should be downstream from it.

### 2.2 Conditional tools are the right UI model

A fixed dashboard with every possible tool visible would become unusable. This
project wants many tool types: chat, components, measurements, requirements,
missing parts, material comparison, 2D view, 3D view, reports, decisions, and
exports.

If all of that is visible all the time, the user is forced to manage the UI
instead of the project. Conditional output solves that: the workspace presents
what matters for the current step, while keeping the rest reachable.

The key design challenge is that conditional output must be explainable. The UI
should not hide a tool silently. If the system decides "you need the missing
parts tool now," it should be clear why.

### 2.3 The final report is not an afterthought

The final report is one of the strongest parts of the idea. A physical project
is not finished when a model exists. It is finished when another person can
understand:

- what was built;
- what it is for;
- what materials and components were used;
- what measurements are verified;
- what alternatives were rejected;
- why the final shape was chosen;
- how to recreate or improve it.

That final report is also the bridge to the separate knowledge-capture system.
The project creates the artifact and evidence. The knowledge system can later
extract reusable lessons.

### 2.4 Real-world measurement input is a good future direction

The ESP32/digital measuring tool idea fits the system well, but it should come
after the manual measurement loop is stable. The current UI should treat
measurements as structured events:

```text
field id + value + unit + source + time + confidence
```

If that shape exists now, a future digital caliper, scale, or sensor can feed
the same pipeline without redesigning the app.

---

## 3. Main risks

### 3.1 This is bigger than one UI

The manifesto touches at least six systems:

1. Project intake and requirement extraction.
2. Component registry.
3. Measurement workflow.
4. Design workspace with 2D/3D tools.
5. AI chat and decision support.
6. Final report and knowledge handoff.

All six are valid, but they should not be built at once. The danger is building
a wide workspace where every tool exists in weak form and none is trusted.

The safer path is to build vertical slices. A vertical slice means one complete
workflow from input to output, even if it is narrow.

Example first slice:

```text
project document -> extracted requirements -> component list ->
measurement fields -> one saved measurement -> updated report
```

That teaches the workspace how to move data through the system before it tries
to cover every kind of physical project.

### 3.2 Conditional UI can become confusing if the state model is weak

Conditional tools need a clear project state model. The UI should know whether
the project is in intake, requirement review, component inventory, measuring,
layout exploration, validation, manufacturing, or final reporting.

Without states, the UI becomes "AI decided to show this." That will feel random.

The better model is:

```text
project phase -> active question -> suggested tools
```

For example:

| Project phase | Active question | Tools shown |
|---|---|---|
| Intake | What is being built? | Project document, AI chat, extracted requirements |
| Inventory | What parts exist? | Components list, missing parts, source/evidence viewer |
| Measurement | What facts are still guesses? | Measurement panel, component viewer, report |
| Layout | Where should parts go? | 2D view, 3D view, weight distribution, AI chat |
| Validation | Does the skeleton satisfy constraints? | Report, failed checks, decision log |
| Export | What can be manufactured? | Blueprint viewer, CAD/DXF exports, final checklist |
| Report | What did we decide and why? | Report compiler, decision log, artifacts |

### 3.3 AI extraction must not become silent truth

The AI can analyze the project document and extract hardware, requirements, and
constraints. But extracted data should not immediately become verified project
truth.

The UI should label data by source and confidence:

- `user-provided`
- `ai-inferred`
- `estimated`
- `measured`
- `verified`
- `contradicted`

This matters because physical projects punish false confidence. If the AI
infers that a motor weighs 18g, that is useful as a guess, but it must remain
visibly different from a value measured on a scale.

### 3.4 The boundary with the knowledge-capture system needs to stay clear

The manifesto says this project will work with a final knowledge-capture
variant. That is the correct split, but the UI must respect it.

This project should create:

- project documents;
- component records for this build;
- measurements;
- decisions;
- blueprints;
- 2D/3D files;
- validation reports;
- final phase reports.

The separate knowledge-capture system should later decide:

- what becomes reusable knowledge;
- how reusable components are indexed;
- how lessons are generalized across projects;
- how cross-project search works.

If this project tries to become the full knowledge system too early, it will
slow down the physical-building loop.

---

## 4. Proposed workspace model

The workspace should have three persistent regions and one conditional region.

### 4.1 Left: project map and tool dock

This area answers: "Where am I, and what can I open?"

It should show:

- project phase;
- current active task;
- components;
- measurements;
- decisions;
- artifacts;
- reports;
- available tools.

This should be compact and stable. It should not change shape every time the AI
responds.

### 4.2 Center: active work surface

This is where the currently selected tool lives.

Examples:

- project document intake;
- requirements review;
- component details;
- measurement form;
- 2D blueprint view;
- 3D model view;
- material comparison;
- report editor.

The center should show one primary task at a time. This prevents the workspace
from becoming visually noisy.

### 4.3 Right: AI and evidence panel

This area answers: "Why is the system saying this?"

It should contain:

- AI chat;
- source excerpts from the project document;
- linked component records;
- decision rationale;
- warnings about assumptions;
- next suggested actions.

This panel should be able to cite local project files and records. If the AI
says "the frame needs a wider center plate," the UI should show whether that
came from a requirement, a measurement, a validation check, or a guess.

### 4.4 Conditional tool tray

The conditional tray is where occasional tools appear.

Examples:

- missing hardware analysis;
- material comparison;
- layout alternatives;
- weight distribution;
- export tool;
- sensor connection status;
- final report compiler.

The tray should show why each tool is suggested:

```text
Suggested: Missing parts
Reason: Project document mentions motors and ESCs, but no battery is recorded.
```

This keeps conditional output understandable.

---

## 5. Suggested tool inventory

### Always available

| Tool | Purpose |
|---|---|
| AI chat | Reason about the project, ask questions, explain checks |
| Project map | Navigate requirements, components, measurements, decisions, artifacts |
| Components list | Show all known parts and their data quality |
| Measurement queue | Show what facts are still missing or guessed |
| Report panel | Show current validation state |
| Decision log | Record why choices were made |

### Contextual

| Tool | Appears when |
|---|---|
| Project document viewer | Intake, requirement review, final report |
| Missing parts | Required component categories are absent |
| Material comparison | Material is undecided or a validation problem mentions material |
| Weight distribution | Components have masses and positions |
| Hardware compatibility | Component interfaces must match |
| 2D blueprint viewer | Geometry can be generated |
| 3D model viewer | A parametric model exists |
| Export tools | Design passes enough checks to manufacture |
| Final report compiler | Project has artifacts and decisions to summarize |

### Future hardware-input tools

| Tool | Input source |
|---|---|
| Digital scale | mass |
| Digital caliper | length, width, thickness, hole spacing |
| ESP32 sensor bridge | custom physical measurements |
| Camera/photo station | visual evidence and later measurement extraction |
| Multimeter input | voltage, resistance, continuity |

The important rule: these tools should feed the same measurement/event model as
manual input. The UI should not care whether a value came from typing or from a
sensor, except for the source label.

---

## 6. Data model to brainstorm

This is not final, but it is the shape I would start from.

### Project

```yaml
name: tri-motor-test-frame
goal: Build a physical frame for three large motors and controller hardware.
status: intake | inventory | measuring | layout | validating | export | complete
source_document: docs/project.md
```

### Requirement

```yaml
id: req-fit-three-motors
text: Must hold three large motors safely.
source: project_document
confidence: user-provided
priority: must | should | nice
state: active | revised | rejected
```

### Component

```yaml
id: motor-a
name: Large motor
category: motor
source: user-provided
status: known | missing-data | measured | verified
dimensions:
  diameter_mm:
    value: null
    source: missing
  mass_g:
    value: null
    source: missing
```

### Measurement

```yaml
id: motor-a-mass
component: motor-a
field: mass_g
value: 42.3
unit: g
source: manual | digital-scale | caliper | ai-inferred | datasheet
state: guessed | measured | verified | contradicted
evidence: docs/measurements.md
```

### Decision

```yaml
id: decision-center-plate-material
question: What should the center plate be made from?
choice: 3mm plywood
why: Available, cuttable, passes stiffness check for this prototype.
alternatives:
  - option: acrylic
    rejected_because: Brittle around motor screw loads.
  - option: carbon fiber
    rejected_because: Not available for this build.
sources:
  - params.yaml
  - frame report
state: proposed | accepted | superseded
```

### Artifact

```yaml
id: frame-v1-dxf
type: blueprint | dxf | 3d-model | report | photo
path: dxf/frame-v1.dxf
created_from:
  - params.yaml
  - components/loadout.yaml
state: draft | validated | exported | used
```

---

## 7. Brainstormed user flow

### Step 1: Welcome

The welcome screen should be short. It should not be a marketing page. It should
answer:

- This system helps turn an idea into a physical skeleton.
- It works from project documents, components, measurements, models, and
  decisions.
- It produces blueprints, validation reports, and a final build report.

Primary action: **Create project**.

### Step 2: Project intake

The user enters:

- project name;
- project document;
- known hardware;
- known materials;
- optional constraints.

The system should not immediately create a design. First it should create an
analysis draft.

### Step 3: AI analysis review

The AI extracts:

- goal;
- requirements;
- available components;
- missing components;
- missing measurements;
- assumptions;
- open questions.

The user reviews and accepts, edits, or rejects each extracted item. This is
important. AI output becomes project state only after the user accepts it.

### Step 4: Inventory

The workspace shows known hardware and missing hardware.

For the example:

```text
Known:
  - 3 motors
  - flight controller
  - 3 ESCs

Missing or unknown:
  - battery
  - frame material
  - propellers
  - motor dimensions
  - motor mass
  - mounting hole pattern
```

The AI can suggest what data is needed next and why.

### Step 5: Measurement

The measurement queue opens when the design depends on unknown real-world
values. The UI should clearly mark:

- guessed values;
- measured values;
- verified values;
- values that are out of plausible range.

This is close to what the current workstation already does for the drone frame.

### Step 6: Layout exploration

Once enough data exists, the workspace can propose physical skeleton variants.

Examples:

- triangular frame;
- Y-frame;
- central body with three arms;
- protected electronics cage;
- stacked layout;
- flat plate layout.

For each variant, the UI should show:

- what requirements it satisfies;
- what constraints it risks;
- material and manufacturing implications;
- rough mass and dimensions;
- what is still unknown.

### Step 7: Design decision

When the user picks a variant, the decision log should record:

- chosen option;
- alternatives considered;
- why each rejected option lost;
- measurements and facts used;
- AI recommendation, if any;
- user's final decision.

The decision log should not be optional. It is how the system learns.

### Step 8: Modeling and validation

The system generates or updates 2D/3D artifacts and runs validation. Failed
checks should be visible beside the model, not hidden in a terminal.

### Step 9: Export and final report

The final report compiler gathers:

- project purpose;
- accepted requirements;
- component list;
- measurements;
- decisions;
- blueprints;
- 3D models;
- validation results;
- build notes;
- known limitations.

The user should be able to review it section by section before finalizing.

---

## 8. First implementation slices to consider later

These are not plans. They are candidate slices that could later become plans.

### Slice A: Project intake without AI

Build a project creation screen that accepts a name and Markdown document, then
stores them in a predictable folder. No AI extraction yet.

Why first: it creates the durable project object and tests the navigation model.

### Slice B: AI extraction as reviewable draft

Add an AI step that extracts requirements, components, missing data, and open
questions from the project document. Nothing becomes project state until the
user accepts it.

Why second: it adds intelligence without giving it silent write authority.

### Slice C: Component registry

Create a component list tool with source and measurement status. Component rows
open their backing data file.

Why third: components are the bridge between project intent and physical design.

### Slice D: Decision records

Add a decision log with accepted/rejected alternatives.

Why fourth: every future design choice needs a place to store the "why."

### Slice E: Report compiler

Generate a large final report from project document, components, measurements,
decisions, validation output, and artifacts.

Why later: it needs real inputs before it can be useful.

---

## 9. Questions for you

These are the questions I would ask before turning this into a plan.

1. **Is this UI meant for this drone-frame repo first, or for the future general
   creation system first?** My recommendation is to build it through this repo
   first and extract later, because real projects reveal the schema.
2. **Should AI be allowed to write project state directly, or should every AI
   extraction start as a user-reviewable draft?** I strongly recommend drafts
   first.
3. **What does a project document need to contain at minimum?** Goal, mission,
   constraints, available hardware, desired physical form, and success criteria
   seem like the minimum.
4. **Should the workspace be single-project only for now?** I recommend yes.
   Multi-project management is a different product.
5. **What is the first physical project this generalized workspace should serve:
   the current drone frame, a second drone, or something unrelated?**
6. **How much should the UI optimize for touch/tablet use at the workbench?**
   This affects layout, control size, and whether keyboard shortcuts matter.
7. **Where should final reports live?** In this repo's `docs/reports/`, in a
   per-project folder, or in the separate knowledge-capture system?
8. **What data is allowed to be guessed?** I recommend guesses are allowed only
   when visibly marked and never promoted to verified without measurement or
   build evidence.
9. **What are the first real-world measuring devices you want to support?**
   Digital caliper and scale are the obvious first two.
10. **Should the AI chat be a general chat, or should it be anchored to the
    currently open tool?** I recommend anchored chat first, because it produces
    more useful context and fewer vague answers.

---

## 10. My recommendation

The manifesto is pointing at the right long-term system, but the first version
should be smaller and stricter than the full vision.

Start with a **project-state workspace**:

```text
project document -> extracted requirements -> components ->
measurements -> decisions -> artifacts -> final report
```

Make every AI output reviewable before it becomes project state. Make every
number carry a source and confidence. Make every major design choice produce a
decision record. Keep the workspace flexible, but tie every conditional tool to
a visible project phase or active question so the UI does not feel random.

The current measurement workstation is already the first narrow version of this
idea. The next useful step is not to build every tool. It is to define the
project-state model that tells the workspace which tool should appear, what data
it reads, what data it writes, and how that data becomes part of the final
report.

# docs/reports/

**Purpose:** Plain-language reports on finished work. One per roadmap phase.

**Data stored here:** Markdown only. A report explains what a phase built, how
the pieces fit together, where each file lives, what was decided and why, and
what the phase deliberately did not do. It is written for someone who was not in
the room — including your future self.

A report is written **after** the phase is verified, never during it. The plan in
[`../codex/`](../codex/README.md) says what will be built; the sign-off says
whether it was; the report explains it to a human.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `phase1____` | [phase-1-data-spine.md](phase-1-data-spine.md) | Markdown | Phase 1: the field spec, the surgical writer, the two CLI commands, and a full map of the project |
| `phase2____` | [phase-2-workstation.md](phase-2-workstation.md) | Markdown | Phase 2: the FastAPI API, React workstation, `frame ui`, and browser write-through verification |

## What belongs in a report

| Section | Answers |
|---|---|
| The problem | Why this work existed at all |
| What you can do now | The new capability, shown running |
| What was built | Each file, what it does, why it is separate |
| Follow one command through the code | The real call path, file by file |
| Where everything lives | The project map |
| How it was reviewed | What the process caught, honestly |
| By the numbers | Size, tests, dependencies added |
| What it does not do | Limitations, stated before they surprise anyone |
| Exit criteria | Measured against the roadmap's own bar |
| What it unblocks | What can start now |

## Rules

- **No jargon without explanation.** If a term is unavoidable, define it in the
  sentence that first uses it.
- **Show real output.** Paste commands that were actually run, not invented
  examples.
- **Report failures too.** A phase that took four review rounds is more
  instructive than one that claims it took none.
- **Say what was not done.** Every limitation stated here is one that does not
  have to be discovered.

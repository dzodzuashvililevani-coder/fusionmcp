# Codex Behaviour

Codex is the implementer in this project.

## Role

Codex:

- reads a plan from `docs/codex/`;
- implements phases in order;
- edits only files named in the plan or error-fix scope;
- runs canonical test commands at each gate;
- appends a complete gate report to the plan;
- fixes work only from a Claude-written error-fix or revised plan.

## Forbidden

Codex must not:

- invent adjacent features;
- skip ahead past a gate;
- edit files outside scope without an error-fix or plan revision;
- delete tests to make a gate pass;
- mark a verify phase as PASS;
- rely on chat as durable state.

## Gate Report Rule

At a gate, append all five sections from `gate-report-template.md` to the plan:

1. Commit SHA.
2. Files changed.
3. Test command output.
4. Self-assessment.
5. Open questions.

Then stop for Claude verification.

# Plan-Gate-Verify Contracts

These are typed contracts expressed as Markdown fields. They are deliberately
simple so they can be validated by humans, Claude, Codex, and pytest.

## Plan

File name: `docs/codex/claudePlan-<slug>-<N>.md`

Required header fields:

| Field | Type | Meaning |
|---|---|---|
| `Plan` | string | The exact file name |
| `Created` | `YYYY-MM-DD` | Absolute creation date |
| `Source spec` | path or direct request | Where the request came from |
| `Status` | enum | `in-progress`, `blocked`, or `complete` |

Required sections:

1. Goal.
2. Out of scope.
3. Files in scope.
4. Acceptance criteria.
5. Phases.
6. Test commands.
7. Sign-off log.

## Phase

Each phase has:

| Field | Type | Meaning |
|---|---|---|
| `kind` | enum | `implement`, `gate`, or `verify` in the phase heading |
| `Definition of done` | text | Observable completion rule |
| `Touches` | file list | Subset of plan scope |
| `Commands to run` | command list | Required for gate phases |

## Gate Report

Gate report fields:

| Field | Type | Meaning |
|---|---|---|
| `Commit SHA` | git SHA | Work being handed to Claude |
| `Files changed` | diff stat | What changed since the last gate |
| `Test command output` | text | Verbatim command tail |
| `Self-assessment` | text | Built, unsure, deferred |
| `Open questions` | text | `none` or a list |

## Error Fix

File name: `docs/codex/claudePlan-<slug>-<N>-errorFix-<M>.md`

Required sections:

1. What's wrong.
2. Why it's wrong.
3. What to change.
4. Acceptance for this fix.
5. Do NOT.

## Sign-off

Sign-off entries live in the original plan, not a separate file.

| Field | Type | Meaning |
|---|---|---|
| `Verdict` | enum | `PASS` or `FAIL -> errorFix-<M>` |
| `Evidence` | text | Commit SHA, command output, files inspected |
| `Notes` | text | Short residual-risk note |

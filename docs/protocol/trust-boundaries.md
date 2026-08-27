# Trust Boundaries

Plan-Gate-Verify works only if agent output is treated as untrusted input until
it passes a gate.

## File Boundaries

- Keep durable state in repo files, not chat.
- Keep local tool state out of git: `.claude/`, `.codex/`, `.agents/`,
  `.venv/`, `.pytest_cache/`, `.pytest-run-tmp/`, and `.pytest-work-tmp/`.
- Do not commit secrets, credentials, personal account names, or local absolute
  user paths.
- Do not hand-edit generated machine outputs unless the folder README says it
  is safe.

## Path Boundaries

Any automation added later must:

- refuse `..` path traversal;
- refuse writes outside the project root unless the user explicitly requested
  an external artifact;
- refuse `.git/`, virtualenv, cache, and local tool directories;
- prefer repo-relative paths in plans and reports.

## Subprocess Boundaries

Any subprocess wrapper added later must:

- pass user input as arguments, not shell-interpolated strings;
- set a timeout on every subprocess call;
- map missing executables, timeouts, and command failures to clear statuses;
- record command output in the gate report before any sign-off.

## Learning Boundary

Never let unverified output become a future input. Build logs, lessons, reusable
prompts, and templates should be updated after a passing gate, not before.

## Current Enforcement

- `tests/test_privacy.py` scans tracked text files for common secrets, emails,
  private identifiers, and local user paths.
- `tests/test_protocol.py` checks the protocol folders and templates.
- `tests/test_structure.py` keeps every project folder documented with a portal
  table.

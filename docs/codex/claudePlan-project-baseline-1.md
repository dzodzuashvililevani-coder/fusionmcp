# Project baseline remediation

**Plan:** claudePlan-project-baseline-1.md
**Created:** 2026-08-28
**Source spec:** `docs/brainstorming/review-project-final.md` and user request on 2026-08-28
**Status:** gate-complete-awaiting-review

## 1. Goal (<= 3 sentences)

Remediate the project-baseline problems found by Claude: fragile protocol tests,
misnamed duplicate review content, missing protocol record for the mission
baseline work, and canonical commands that no longer run on this Windows
workstation. Preserve the finalized FusionControlCenter description, but make
the verification surface structural and repeatable.

## 2. Out of scope

- Filling physical measurements or changing guessed dimensions.
- Building the web workstation.
- Building the standalone knowledge-capture project.
- Renaming the repository.
- Changing Fusion geometry, mass, thrust, validation, or script behavior.

## 3. Files in scope

```
.gitignore
README.md
CLAUDE.md
docs/README.md
docs/project/README.md
docs/project/description.md
docs/protocol/README.md
docs/protocol/trust-boundaries.md
docs/codex/plan-template.md
docs/codex/claudePlan-web-workstation-1.md
docs/codex/claudePlan-project-baseline-1.md
docs/knowledge/capture-candidates.md
docs/brainstorming/README.md
docs/brainstorming/idea-user-1.md
docs/brainstorming/review-user-1.md
docs/brainstorming/review-icm-paper.md
docs/brainstorming/review-project-final.md
docs/brainstorming/idea-web-workstation.md
tests/test_protocol.py
tests/test_structure.py
```

OFF-LIMITS: `params.yaml`, `components/loadout.yaml`, solver code, Fusion
scripts, CAD/DXF outputs, and private local agent folders.

## 4. Acceptance criteria

1. `idea-user-1.md` contains the user manifesto as durable repo state.
2. The duplicate Codex manifesto review is removed or renamed so no
   `idea-*.md` file contains review content.
3. Project description tests assert durable structure rather than exact prose
   sentences.
4. The knowledge candidate template supports per-dimension provenance for
   component facts.
5. Canonical commands use Python module entry points and a usable temp
   directory, because `frame.exe` is blocked by Windows Application Control and
   `.pytest-run-tmp` cannot be repaired from this shell.
6. The project index files point to `docs/project/` and `docs/knowledge/`.
7. Privacy checks pass on tracked text files.
8. The final diff is committed with sanitized git author metadata.

## 5. Phases

### Phase 1: implement - remediation

**Definition of done:** all acceptance criteria are implemented in the files in
scope.

### Phase 2: gate - verification

**Definition of done:** gate report appended, then halt.

**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
git diff --check
git status --short
```

### Phase 3: verify - Claude/user

**Definition of done:** Claude or the user reviews the gate report and accepts
or requests a follow-up fix.

## 6. Test commands (canonical)

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Both must be clean before commit. The older `.pytest-run-tmp` directory remains
an environment artifact only and is not a valid gate target on this machine.

## 7. Sign-off log

### Gate report - 2026-08-28

## Commit SHA

Pre-commit working tree. Final commit SHA is recorded in git history after this
gate report is committed.

## Files changed

- Added `docs/codex/claudePlan-project-baseline-1.md` as the retroactive
  protocol record requested by Claude's review.
- Saved the user manifesto in `docs/brainstorming/idea-user-1.md`.
- Removed the duplicate misnamed Codex review file
  `docs/brainstorming/idea-fusion-control-center-manifesto-review.md`.
- Added and indexed `docs/project/` and `docs/knowledge/`.
- Updated active protocol docs and plan templates to use Python module
  commands instead of blocked `.exe` shims.
- Updated pytest canonical command to use `.pytest-work-tmp` and disable pytest
  cache writes.
- Reworked protocol tests to assert document structure and required contracts
  instead of exact prose sentences.
- Extended `docs/knowledge/capture-candidates.md` with per-dimension component
  provenance.

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
116 passed in 1.38s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider --basetemp=.pytest-work-tmp
1 passed in 0.14s
```

Environment remediation attempted:

```powershell
Remove-Item -LiteralPath .pytest-run-tmp -Recurse -Force
Access is denied.

takeown / icacls against .pytest-run-tmp
Successfully processed 0 files; Failed processing 1 files
Access is denied.
```

`.\.venv\Scripts\frame.exe report` is still blocked by Windows Application
Control. `python.exe -m frame_tools.cli report` is clean and is now the
canonical command.

## Self-assessment

The necessary repo fixes are implemented. B1 could not be repaired at the file
system level from this shell, so the deterministic gate now avoids the locked
path deliberately. B2 is an OS policy block against the generated shim, so the
canonical command now uses the Python module entry point.

E1 is addressed by preparing this work for commit. E2 is addressed by structural
tests. E3 is addressed by deleting the misnamed duplicate review.

## Open questions

- `.pytest-run-tmp` remains a broken local directory and may need manual removal
  from an elevated Windows shell outside Codex.
- The design numbers are still guesses until the real hardware measurements are
  filled in.

### Phase 3 sign-off - 2026-08-28

**Verdict:** PASS by user direction.

**Evidence:** The user reviewed Claude's follow-up, accepted moving knowledge
capture out of this repository, and instructed Codex to review the new roadmap
and start implementation.

**Notes:** This closes the retroactive baseline-plan ambiguity from
`review-project-final.md` F2 for purposes of Phase 1. Future multi-step work
continues through Plan-Gate-Verify.

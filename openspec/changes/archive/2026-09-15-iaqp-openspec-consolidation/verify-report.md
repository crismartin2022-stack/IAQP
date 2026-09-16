```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:9ef7942af1aa90c9f909a2dab3a6edfdc42cb3225a3df34939b354444ba648fd
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 4/4
scenarios: 8/8
test_command: PYTHONDONTWRITEBYTECODE=1 python3 pruebas.py
test_exit_code: 0
test_output_hash: sha256:0b71f795a8e0650ff35e913a44ee741ba2109f4f3a75ade1d24531e0bc60a53c
build_command: PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q .
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: iaqp-openspec-consolidation
**Version**: N/A
**Mode**: Standard (`strict_tdd: false`)
**Verified on**: 2026-09-15, branch `chore/iaqp-consolidation-closeout` created from `origin/staging` after PRs #12–#17 merged; re-verified after the governance requirements were relocated to `specs/openspec-governance/spec.md`.

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 16 |
| Tasks complete | 16 |
| Tasks incomplete | 0 |

### Build & Tests Execution

**Build**: ✅ Passed

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m compileall -q .   -> exit 0, no output
```

**Tests**: ✅ project test command passed; ✅ 8/8 scenario checks passed; ⚠️ unit suites not runnable locally

```text
PYTHONDONTWRITEBYTECODE=1 python3 pruebas.py            -> exit 0 (statistical RNG and roulette evidence; informational, no assertions; output varies per run)
bash iaqp-verify-scenarios.sh (session evidence script)  -> exit 0, 8/8 PASS, output sha256:5f4f0212662a344524212ca2898a43d07f5348e7eea7f9d93f887a706baa10b8
python3 -m unittest discover -s tests                   -> 7 import errors: No module named 'httpx' (environmental; suites unchanged by this change)
```

The scenario script aborts with exit 125 if `rg`, `fd`, `jq`, `git`, or `gentle-ai` is missing, and each negated check first asserts that its input was read. Negative control: the sanitization detector flagged a URL, a variable assignment, a project reference, and a UUID sample, and passed a clean table row.

**Coverage**: ➖ Not available

### Spec Compliance Matrix

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Canonical SDD State Location | Progress matches the canonical branch | Scenario check s11: native `sdd-status` progress of `iaqp-isolated-staging-bootstrap` equals checkbox counts of its `tasks.md` on `origin/staging` (10/13) | ✅ COMPLIANT |
| Canonical SDD State Location | Divergent copy in a secondary checkout | s12: `git worktree list` has one entry; the unit2 checkout and both IAQP worktrees are absent | ✅ COMPLIANT |
| Canonical SDD State Location | Planning artifacts never committed | s13: proposal, design, exploration, and both spec domains exist on `origin/staging`; the proposal records 10/13 | ✅ COMPLIANT |
| No Partial Archive State | Archive copy without verification evidence | s21: incomplete archive copy absent on `origin/staging` and on disk; originals present | ✅ COMPLIANT |
| No Partial Archive State | Empty domain directory | s22: no empty directory under `openspec/` | ✅ COMPLIANT |
| Records Match Attested Live State | Live resource without record | s31: `live-state-reconciliation.md` is dated 2026-09-15 on `origin/staging`; no phase-4 task is checked | ✅ COMPLIANT |
| Records Match Attested Live State | Sanitized evidence only | s32: the record is read and contains no URL, domain, UUID, project reference, or variable assignment (plus negative control) | ✅ COMPLIANT |
| Consolidated Changes Pass Native Status | Blocker cleared | s41: native status of `iaqp-isolated-staging-bootstrap` reports zero blocked reasons | ✅ COMPLIANT |

**Compliance summary**: 8/8 scenarios compliant

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| Canonical SDD State Location | ✅ Implemented | Single IAQP checkout; all change records on `staging` |
| No Partial Archive State | ✅ Implemented | `project-memory-and-local-guide` restored intact (10/12) |
| Records Match Attested Live State | ✅ Implemented | Dated, names-only reconciliation; phase-4 tasks stay open |
| Consolidated Changes Pass Native Status | ✅ Implemented | Every IAQP change reports no blocked reasons |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| Base on `origin/staging` | ✅ Yes | Tracker created from `origin/staging` |
| Back up untracked files before switching | ⚠️ Deviated (recorded) | Workspace folder instead of session scratchpad; every file accounted for against `staging` before deletion |
| Restore `project-memory-and-local-guide` | ✅ Yes | Archive copy was byte-identical to the restored originals |
| Rephrase route tokens | ✅ Yes | Endpoint names without path-like backticks on task lines |
| Correct planning artifacts | ✅ Yes | Status section, historical note, testing strategy |
| Normalize config | ✅ Yes | `execution_mode: auto`; testing facts for unittest suites |
| Move release plan into the change | ✅ Yes | Identical to the original after the banner |
| Live inventory record | ✅ Yes | `live-state-reconciliation.md` |
| PR slicing | ⚠️ Deviated (recorded) | Planned PR 3 (466 lines) split into PR 3 and PR 4 |
| Worktree retirement | ✅ Yes | Three checkouts removed, two prunable entries pruned, branches kept |
| Spec placement | ⚠️ Deviated (recorded) | Requirements relocated unchanged from `project-memory` to the new capability `openspec-governance`; the native composer cannot merge requirements into the narrative memory spec |

### Issues Found

**CRITICAL**: None

**WARNING**:
- IAQP unit suites cannot run locally (`httpx` missing); the last passing evidence came from temporary virtual environments that no longer exist.
- Delivery incident: PRs #13–#15 merged into their parent branches instead of the tracker; recovered by PR #16 before tracker PR #17. Tracker ancestry must be verified after every chain merge.
- The first scenario run executed under a `bash` without ripgrep and produced false results, including one false pass; ripgrep was installed and the script hardened. The run cited above is the evidence of record.
- The proposal originally declared `project-memory` as a modified capability; that spec has no requirement headings, so the requirements now live in `openspec-governance`.

**SUGGESTION**:
- Commit a CI-runnable OpenSpec state check if these scenario checks become routine.
- Optionally rename the Railway environment named `production` in the staging project.

### Verdict

PASS WITH WARNINGS
All 16 tasks are complete and all 8 spec scenarios were verified at runtime; the warnings are environmental, delivery-process, or spec-placement notes.

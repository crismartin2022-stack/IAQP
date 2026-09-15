# Tasks: IAQP OpenSpec Consolidation

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~940 authored (planning artifacts ~360, release plan draft 183, consolidation and roadmap docs ~330, reconciliation and config ~70) plus 414 generated Supabase CLI config |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 bootstrap records → PR 2 live state and hygiene → PR 3 consolidation records |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

Each slice stays under 400 authored lines; the generated CLI config is excluded from the authored count.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Corrected bootstrap planning artifacts; route tokens | PR 1 → tracker | `gentle-ai sdd-status iaqp-isolated-staging-bootstrap --cwd . --json` | N/A: documentation only | Revert PR 1 |
| 2 | Live-state record, release plan draft, hygiene | PR 2 → PR 1 branch | `python3 -m compileall -q .` | N/A: no runtime change | Revert PR 2 |
| 3 | Consolidation and roadmap records, config | PR 3 → PR 2 branch | `gentle-ai sdd-status iaqp-openspec-consolidation --cwd . --json` | N/A: documentation only | Revert PR 3 |

## Phase 1: Safe Base

- [x] 1.1 Back up every untracked file of the IAQP checkout to the workspace backup folder outside the repository; record the file list.
- [x] 1.2 Create tracker `chore/iaqp-openspec-consolidation` from `origin/staging`; create `chore/iaqp-bootstrap-records` from the tracker.
- [x] 1.3 Restore `openspec/changes/project-memory-and-local-guide/`; delete `openspec/changes/archive/2026-09-03-project-memory-and-local-guide/` and the empty spec folder.

## Phase 2: Bootstrap Records (PR 1)

- [x] 2.1 Correct progress statements in `openspec/changes/iaqp-isolated-staging-bootstrap/proposal.md`, `openspec/changes/iaqp-isolated-staging-bootstrap/design.md`, and `openspec/changes/iaqp-isolated-staging-bootstrap/exploration.md` to 10/13 with phase 4 open.
- [x] 2.2 Check `openspec/changes/iaqp-isolated-staging-bootstrap/specs/isolated-staging-runtime/spec.md` and `openspec/changes/iaqp-isolated-staging-bootstrap/specs/isolated-staging-topology/spec.md` against merged code; correct stale statements.
- [x] 2.3 In `openspec/changes/iaqp-isolated-staging-bootstrap/tasks.md`, write the salud and ready endpoint names without backticks on task lines 2.2, 2.4, and 4.2; change nothing else.
- [x] 2.4 Native status for the bootstrap change reports no blocked reasons and 10/13 (spec: Blocker cleared).
- [x] 2.5 Secret-pattern scan and `git diff --check --cached`; commit; push; open PR 1 into the tracker.

## Phase 3: Live State and Hygiene (PR 2)

- [x] 3.1 Write `openspec/changes/iaqp-isolated-staging-bootstrap/live-state-reconciliation.md` per design; annotate phase-4 tasks.
- [x] 3.2 Move the root release plan draft to `openspec/changes/iaqp-isolated-staging-bootstrap/release-plan-draft.md` with a stale-claims banner.
- [x] 3.3 Add `__pycache__/` to `.gitignore`; stage `.gitignore`, `supabase/.gitignore`, `supabase/config.toml`.
- [x] 3.4 Run `python3 -m compileall -q .` and `python3 -m unittest discover -s tests`; scan; commit; push; open PR 2 into PR 1 branch.

## Phase 4: Consolidation Records (PR 3)

- [x] 4.1 Normalize `openspec/config.yaml`: valid execution mode and strategy values, testing facts for the unittest suites.
- [x] 4.2 Stage `openspec/changes/iaqp-staging-homologation-roadmap/` and `openspec/changes/iaqp-openspec-consolidation/`; commit; push; open PR 3 into PR 2 branch.
- [x] 4.3 Native status for every IAQP change reports no blocked reasons (spec: Progress matches the canonical branch).

## Phase 5: Retirement

- [ ] 5.1 After the tracker merges into staging, check the unit2 checkout and both iaqp worktrees for unique commits or files; remove clean ones; prune; delete the backup folder.

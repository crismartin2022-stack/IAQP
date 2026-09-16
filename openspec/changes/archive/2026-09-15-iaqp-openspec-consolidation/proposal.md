# Proposal: IAQP OpenSpec Consolidation

## Intent

IAQP code is merged in `origin/staging`, but OpenSpec is split across four checkouts. The only proposal, design, and specs for `iaqp-isolated-staging-bootstrap` are untracked and describe 3/13 progress while `origin/staging` records 10/13. Two native blockers stop the pipeline. Source: `openspec/changes/iaqp-staging-homologation-roadmap/exploration.md`.

## Scope

### In Scope
- Base canonical work on `origin/staging`; preserve untracked planning artifacts from `IAQP/` before switching.
- Land bootstrap proposal, design, and spec domains corrected to merged progress; keep `tasks.md` from `origin/staging`.
- Clear `edit_authority_missing`: stop backticked HTTP routes in `tasks.md` from reading as paths.
- Resolve the incomplete `project-memory-and-local-guide` archive move and its empty spec directory.
- Settle `openspec/config.yaml` once: valid strategy values, testing facts (unittest suites in `tests/`).
- Record a sanitized read-only inventory of the Railway and Supabase `IAQP Staging` projects.
- Preserve `STAGING_AND_RELEASE_PLAN.md` as phase-4 input; ignore `__pycache__/` and local Supabase state.
- Retire `IAQP-unit2-runtime-readiness/`, `.worktrees/*iaqp*`, and prunable external worktrees after landing.

### Out of Scope
- Game, wallet, persistence, or API behavior changes; phase-4 work; deploys; migrations; branch protection.
- Deleting remote branches, including abandoned `feat/iaqp-staging-runtime-readiness`.

## Capabilities

### New Capabilities
- `openspec-governance`: SDD change state lives only in `IAQP/openspec`; secondary checkouts carry no change trackers; records claim only attested live state.

### Modified Capabilities
None. (Relocated from `project-memory` at archive time on 2026-09-15: that spec is a narrative memory document without requirement headings, so the native composer cannot merge requirements into it.)

## Approach

Exploration approach 1. Casino safety invariants and QuartzPlay wallet ownership are untouched: documentation and repository hygiene only.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `openspec/changes/iaqp-isolated-staging-bootstrap/` | New/Modified | Corrected planning artifacts; route tokens |
| `openspec/changes/project-memory-and-local-guide/`, `archive/` | Modified/Removed | Archive resolution |
| `openspec/specs/openspec-governance/spec.md` | New | Governance requirements (canonical location, archive state, live-state records, native status) |
| `openspec/config.yaml` | Modified | Strategy values and testing facts |
| `.gitignore`, `supabase/.gitignore`, `supabase/config.toml` | New | Local-state hygiene |
| Secondary checkouts | Removed | Local only |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Stale narrative overwrites true progress | Med | Correct artifacts against `origin/staging` before commit |
| Untracked work lost when switching base | Med | Back up untracked files first; verify after |
| Identifiers committed | Low | Scan diff for IDs/URLs/keys |

## Rollback Plan

Revert the consolidation PR. Untracked originals stay backed up until merge. Checkouts are re-creatable from untouched remote branches. The inventory is read-only.

## Dependencies

- Sanitized staging inventory (authorized 2026-09-15).
- PR into `staging`.

## Reviewer Workload Forecast

Mostly documentation, near 400 lines. Decision needed before apply: No. Chained PRs recommended: Only if tasks exceed 400. 400-line budget risk: Medium. Session delivery strategy `auto-chain`.

## Success Criteria

- [ ] Native status reports no blockers for `iaqp-isolated-staging-bootstrap` and shows 10/13.
- [ ] `project-memory-and-local-guide` is either archived or intact, never half-moved.
- [ ] `git status` in `IAQP/` is clean of OpenSpec and scaffolding files.
- [ ] `python3 -m compileall -q .` passes.
- [ ] Secondary checkouts removed; remote branches untouched.

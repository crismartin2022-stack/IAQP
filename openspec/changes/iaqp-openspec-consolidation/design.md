# Design: IAQP OpenSpec Consolidation

## Technical Approach

Move `IAQP/` onto a consolidation branch created from `origin/staging`, carry the untracked planning artifacts, correct them to merged progress, clear both native blockers, and record the 2026-09-15 sanitized live inventory. Documentation and repository hygiene only; casino invariants and wallet ownership are untouched. Satisfies `specs/project-memory/spec.md`.

## Architecture Decisions

| Decision | Options | Tradeoff | Choice |
|---|---|---|---|
| Base | `feat/iaqp-staging-schema`; `origin/staging` | Current branch lacks phases 2–3 | `git switch -c chore/iaqp-openspec-consolidation origin/staging`; verified safe: tracked edits are identical in both commits and no untracked path exists in `staging` |
| Untracked safety | Switch directly; back up first | Direct switch is safe but irreversible if wrong | Copy untracked files to a workspace backup folder outside the repository (survives the session) before switching; delete backup only after merge |
| `project-memory-and-local-guide` | Finish archive; restore | Archive copy lacks verify evidence (5 files, no verify report) | Restore the five originals, delete the untracked archive copy and the empty `specs/project-memory/` husk; change stays active at 10/12 |
| Route tokens | Grant edit authority; rephrase | Grant widens authority for a parsing artifact | Rephrase `/salud` and `/ready` in `tasks.md` as endpoint names without a leading slash inside backticks, or append `(read-only)`; confirm with native status |
| Bootstrap planning artifacts | Commit as-is; correct | As-is states 3/13 | Correct progress statements to `staging` (10/13, phase 4 open) before commit; keep `tasks.md` from `staging` |
| Config | Keep dirty; normalize | Dirty file uses undocumented `session-auto` | Valid values: `execution_mode: auto`, `delivery_strategy: ask-on-risk`, `feature-branch-chain`; testing facts: unittest suites under `tests/` |
| Release plan draft | Commit at root; move into change | Root file implies approved plan | Move to `openspec/changes/iaqp-isolated-staging-bootstrap/release-plan-draft.md` as phase-4 input with a stale-claims banner |
| Live inventory | Tasks notes; one record | Divergence must stay visible | New `iaqp-isolated-staging-bootstrap/live-state-reconciliation.md`; phase-4 tasks stay open with dated annotations; a completed task whose resource the inventory cannot observe returns to open |

## Data Flow

    IAQP/ untracked ──► backup ──► branch from origin/staging ──► corrected artifacts ──► PR into staging
    secondary checkouts ──► verified no unique content ──► worktree removal + prune
    CLI inventory (names only) ──► live-state-reconciliation.md

## File Changes

| File | Action | Description |
|---|---|---|
| `openspec/changes/iaqp-isolated-staging-bootstrap/{proposal,design,exploration}.md`, `specs/isolated-staging-{runtime,topology}/spec.md` | Create | Corrected planning artifacts |
| `openspec/changes/iaqp-isolated-staging-bootstrap/tasks.md` | Modify | Route tokens only |
| `openspec/changes/iaqp-isolated-staging-bootstrap/live-state-reconciliation.md` | Create | Sanitized inventory |
| `openspec/changes/iaqp-isolated-staging-bootstrap/release-plan-draft.md` | Create | Moved from root draft |
| `openspec/changes/project-memory-and-local-guide/**` | Restore | Originals back; husk removed |
| `openspec/changes/archive/2026-09-03-project-memory-and-local-guide/**` | Delete | Incomplete untracked copy |
| `openspec/changes/iaqp-staging-homologation-roadmap/`, `openspec/changes/iaqp-openspec-consolidation/` | Create | Roadmap and this change |
| `openspec/config.yaml` | Modify | Valid values, testing facts |
| `.gitignore`, `supabase/.gitignore`, `supabase/config.toml` | Create | Add `__pycache__/`; local Supabase config has only a comment matching role names |

## Interfaces / Contracts

`live-state-reconciliation.md` observations:

| Resource | Observation |
|---|---|
| Railway project | Exists; single environment named `production` |
| `staging-api` | Deploys from `staging`; last deploy succeeded 2026-09-11; public domain exists |
| Variables | `DATABASE_URL`, `APP_ENV`, `ALLOWED_ORIGINS`, service key, `QP_URL`, `QP_ALLOWED_HOSTS` (wallet guard inputs, by design) |
| Supabase project | Active, 0 Edge Functions; row, Auth, Storage counts not measurable under current authorization |

Owner actions: confirm `QP_URL` targets QuartzPlay staging; confirm database target is the staging Supabase project; decide environment naming.

## Worktree Retirement Procedure

For `IAQP-unit2-runtime-readiness/` and `.worktrees/*iaqp*`: branch tip reachable from its remote branch (the abandoned branch stays on the remote); `git status --porcelain` shows only known duplicates; then `git worktree remove --force`; finally `git worktree prune` for the two prunable external entries.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Syntax | Python compiles | `python3 -m compileall -q .` |
| Unit | Merged suites still pass on base | `python3 -m unittest discover -s tests` |
| Records | Blockers cleared, progress matches | `gentle-ai sdd-status` for every IAQP change; `git diff --check`; secret-pattern scan |

## Threat Matrix

N/A — no product routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary changes; VCS operations are manual delivery steps.

## Migration / Rollout

No migration required. Rollback: revert the PR; restore untracked files from backup before merge; recreate checkouts from remote branches.

## Open Questions

- [ ] Owner answers for `QP_URL` target, database target, and environment naming (recorded as pending, non-blocking).
- [ ] Remaining two `project-memory-and-local-guide` tasks are QuartzPlay-scoped; closing them is a follow-up.

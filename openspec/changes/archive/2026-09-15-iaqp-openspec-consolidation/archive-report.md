# Archive Report: iaqp-openspec-consolidation

- **Archived:** 2026-09-15 to `openspec/changes/archive/2026-09-15-iaqp-openspec-consolidation/`
- **Final state at close:** 16/16 tasks complete; verification `pass_with_warnings` with 0 blockers and 0 CRITICAL findings (`verify-report.md`, re-verified after the spec relocation below).

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| `openspec-governance` | Created | 4 requirements, 8 scenarios; mechanical copy to `openspec/specs/openspec-governance/spec.md` with an empty `diff` |
| `project-memory` | Not modified | The main spec is a narrative memory document with no requirement headings; `gentle-ai sdd-archive-compose` refused the delta, so the requirements were relocated unchanged to `openspec-governance` before archive |

## Archive Contents

- `proposal.md` ✅ (capabilities updated to the relocation)
- `specs/openspec-governance/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (16/16)
- `apply-progress.md` ✅
- `verify-report.md` ✅

## Delivery Record

- Issue #11.
- PRs #12 (bootstrap records), #13 (live state and hygiene), #14 (roadmap and config), #15 (consolidation records), #16 (recovery of #13–#15, which had merged into their parent branches instead of the tracker), and #17 (tracker into `staging`). All merged on 2026-09-15.
- IAQP staging redeploy triggered by #17: `SUCCESS`.

## Final-State Facts

These facts supersede the intermediate snapshots in `apply-progress.md`:

- Task 5.1, listed as remaining in Batch 3, is complete (see Batch 4): the secondary checkouts were removed, the prunable entries pruned, and the backup deleted after every file was accounted for against `staging`.
- `verify-report.md` is the second verification run. The first run was superseded because the spec location changed.

## Mechanical Copy Evidence

- `diff -r` of the change spec against the new main spec: empty.
- `diff -r` of the pre-move snapshot against the archived folder: empty (exit 0). This report is additive and excluded from that comparison.

## Open Follow-ups (Outside This Change)

- Install the application dependencies (`httpx`) locally so the unit suites under `tests/` can run.
- Value-level checks that `DATABASE_URL` and `QP_URL` target the staging Supabase project and QuartzPlay staging (needs owner approval).
- Phase 4 of `iaqp-isolated-staging-bootstrap` (topology runbook and smoke).
- Owner decision on the `staging` → `main` release.
- Optional rename of the Railway environment named `production` in the staging project.

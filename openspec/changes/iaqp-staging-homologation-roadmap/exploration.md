## Exploration: IAQP staging and production homologation roadmap

Project-wide exploration requested when the orchestrator took control of the project. Goal: reach a working, isolated staging environment, then homologate staging with production. OpenSpec in `IAQP/` is the single source of truth for project state.

Evidence sources: `openspec/**` in the four IAQP checkouts (`IAQP/`, `IAQP-unit2-runtime-readiness/`, `.worktrees/fix-iaqp-staging-wallet-guard/`, `.worktrees/iaqp-staging-runtime-readiness-v2/`), local git refs (no fetch), native `gentle-ai sdd-status`, the workspace handoff, and a read-only account-level access check of the Supabase and Railway CLIs (project names and status only). No code was modified and no remote resource was changed.

### Current State

#### 1. `origin/staging` is the canonical code state; every local checkout is stale

Verified with local refs:

| Ref | In `origin/staging` | In `origin/main` | Role |
|---|---|---|---|
| `feat/iaqp-staging-schema` (checked out in `IAQP/`) | Yes | No | Schema Foundation, merged |
| `feat/iaqp-staging-runtime-readiness-v2` | Yes | No | Runtime readiness, merged |
| `fix/iaqp-staging-wallet-guard` | Yes | No | Wallet boundary guard, merged |
| `feat/iaqp-staging-runtime-readiness` (checked out in `IAQP-unit2-runtime-readiness/`) | No | No | Abandoned first approach; superseded by v2 |

`origin/main` is 7 commits behind `origin/staging`: no IAQP staging work has been promoted to production. `origin/staging` contains `supabase/migrations/20260910150000_initial_iaqp_schema.sql`, `main.py`, `billetera.py`, `tests/test_runtime_readiness.py`, `tests/test_wallet_guard.py`, and `.github/workflows/semgrep.yml` (also present on `origin/main`).

#### 2. OpenSpec state diverges across checkouts

| Change | Checkout | Progress | Notes |
|---|---|---|---|
| `iaqp-isolated-staging-bootstrap` | `IAQP/` | 3/13, blocked | Only copy with proposal, design, exploration, and two spec domains, all untracked and never committed; its `tasks.md` narrative predates merged progress |
| `iaqp-isolated-staging-bootstrap` | `.worktrees/fix-iaqp-staging-wallet-guard/` | 10/13 | Most advanced; mirrors `origin/staging` (phases 1–3 done, phase 4 open); `tasks.md` only |
| `iaqp-isolated-staging-bootstrap` | `IAQP-unit2-runtime-readiness/`, `.worktrees/iaqp-staging-runtime-readiness-v2/` | 7/13 | Superseded interim states |
| `project-memory-and-local-guide` | `IAQP/` | blocked | Uncommitted, half-finished archive move: originals deleted, untracked archive copy under `archive/2026-09-03-*`, and an empty `specs/project-memory/` directory left behind |
| `project-memory-and-local-guide` | other three checkouts | 10/12 | Intact un-archived copy, identical to `origin/staging`; the two open tasks belong to QuartzPlay scope |

`openspec/config.yaml` in `IAQP/` carries uncommitted workflow edits; the committed version and other checkouts still use the obsolete `ask-always` strategy value.

#### 3. Native blockers, with verified causes

- `iaqp-isolated-staging-bootstrap` — `blocked(edit_authority_missing)`, reported edit root `/`. Allowed edit roots are the `IAQP/` repository. `tasks.md` backticks the HTTP routes `/salud` and `/ready`; the validator reads backticked tokens as paths, so those absolute-looking routes resolve outside the repository. Fix: rephrase the routes or mark them `(read-only)` in `tasks.md`. No edit-authority grant is required.
- `project-memory-and-local-guide` — "specs/ has files but no non-empty `<domain>/spec.md`": caused by the empty directory left by the incomplete archive move in `IAQP/` only.

#### 4. Staging readiness

| Area | State | Evidence level |
|---|---|---|
| Schema Foundation (4 `iaqp_*` tables, synthetic seed) | Merged to `staging` | Redacted migration rehearsal recorded in `tasks.md` |
| Runtime readiness (fail-closed `APP_ENV`/`ALLOWED_ORIGINS`, DB-probing `/ready`, liveness `/salud`) | Merged to `staging` | Deterministic unittest suite |
| Wallet boundary guard (HTTPS + host allowlist before any outbound call) | Merged to `staging` | Unittest suite, stub-based |
| Semgrep workflow | Present on `main` and `staging` | Workflow file only; required-check enforcement unverified |
| Railway staging project and Supabase staging project | Both named `IAQP Staging`, exist live | Not attested in OpenSpec |
| Live staging deployment, `/ready` on a real target | Unknown | None |
| Topology, smoke runbook, failure boundary (phase 4) | Open | Draft `STAGING_AND_RELEASE_PLAN.md`, untracked, partly stale |

Note: the QuartzPlay change `quartzplay-isolated-staging-bootstrap` also records an attempt to create the `IAQP Staging` Railway project. That cross-product record must not be treated as IAQP evidence; IAQP attestation belongs in this repository.

#### 5. Production homologation

| Dimension | Known | Missing |
|---|---|---|
| Environment separation | Draft plan: staging deploys only from `staging`, production only from `main`, disjoint `DATABASE_URL`, `QP_URL`, service key, domains | Verification that Railway triggers and variables match |
| Database | Separate Supabase projects intended; schema migration versioned | Staging migration parity on the live project; backup policy; restore drill into a disposable target |
| Release flow | `staging → main` release PR with checks, acceptance evidence, rollback plan, owner approval | Branch protection and required checks on `staging` and `main` (needs admin-level verification) |
| Observability | Required by draft plan | Structured logs with environment, revision, request id, and no secret leakage |
| Wallet integration | Guard allows only approved QuartzPlay hosts | Staging-only integration against QuartzPlay staging, which depends on QuartzPlay's own staging schema gates |

### Affected Areas

- `IAQP/openspec/changes/iaqp-isolated-staging-bootstrap/` — canonical change to rebuild on top of `origin/staging`; `tasks.md` route tokens cause the native block.
- `IAQP/openspec/changes/project-memory-and-local-guide/` and `archive/` — incomplete archive move to finish or revert.
- `IAQP/openspec/config.yaml` — uncommitted workflow values to settle once.
- `IAQP/STAGING_AND_RELEASE_PLAN.md` — untracked release plan draft; input for phase 4.
- `IAQP/supabase/config.toml`, `.gitignore`, `supabase/.gitignore`, `__pycache__/` — untracked local scaffolding and build artifacts.
- `main.py`, `billetera.py`, `supabase/migrations/`, `tests/` on `origin/staging` — merged contract the live staging deployment must satisfy.
- `IAQP-unit2-runtime-readiness/`, `.worktrees/*iaqp*` — stale checkouts to retire.

### Approaches

1. **Rebase OpenSpec on `origin/staging`, then finish phase 4** — one reconciliation change moves `IAQP/` onto `origin/staging`, lands the untracked proposal/design/specs corrected to real progress (10/13), fixes the route tokens, finishes the archive move, and settles `config.yaml`; then phase 4 and live deploy proof follow.
   - Pros: One canonical state that matches merged code; clears both native blockers; smallest path to a real staging deployment.
   - Cons: Untracked planning documents must be rewritten, not committed as-is.
   - Effort: Low

2. **Continue from the most advanced worktree (`fix-iaqp-staging-wallet-guard`)** — keep working in that checkout and ignore `IAQP/`.
   - Pros: Tasks already at 10/13.
   - Cons: Loses the only proposal/design/spec documents; leaves `IAQP/` dirty and blocked; keeps state split across checkouts.
   - Effort: Low, but perpetuates fragmentation

3. **Commit `IAQP/` working tree as-is** — check in the current untracked documents and archive move.
   - Pros: Nothing lost.
   - Cons: Commits a 3/13 narrative that contradicts merged 10/13 progress; regresses the recorded truth.
   - Effort: Low, incorrect

### Recommendation

Approach 1. Proposed SDD sequence:

| # | Change | Depends on | Human authorization | Size vs 400-line budget |
|---|---|---|---|---|
| 1 | `iaqp-openspec-consolidation`: move `IAQP/` onto `origin/staging`, land corrected bootstrap planning artifacts, fix route tokens, finish archive, settle config, retire stale checkouts | — | Commit/PR to `staging` | Small–medium; documentation only |
| 2 | Live-state reconciliation: sanitized read-only inventory of the `IAQP Staging` Railway and Supabase projects | 1 | Read-only remote access to staging projects | Small |
| 3 | Bootstrap phase 4: topology, owner smoke runbook, failure boundary, finalized release plan | 2 | Owner acceptance | Small |
| 4 | Staging deploy proof: live `/ready`, migration parity, redacted logs | 3 | Remote staging deploy and migration apply | Evidence-only |
| 5 | `iaqp-release-guardrails`: branch protection, required checks (Semgrep, tests) on `staging` and `main` | 1 | Repository admin | Settings only |
| 6 | `iaqp-production-homologation`: observability, backup and restore drill, staging wallet integration against QuartzPlay staging | 4, 5, QuartzPlay staging schema | Production reads; restore target | Medium; chained PRs |
| 7 | First `staging → main` release | 6 | Owner release approval | Release PR |

### Risks

- Committing the current `IAQP/` working tree would overwrite recorded progress with a stale 3/13 narrative.
- The incomplete archive move leaves `project-memory-and-local-guide` blocked until finished or reverted.
- Live `IAQP Staging` resources exist without OpenSpec attestation; their bindings and variables are unverified.
- Branch protection and required-check enforcement cannot be verified with current access (push, not admin).
- `STAGING_AND_RELEASE_PLAN.md` contains stale audit claims (for example Semgrep reported absent while the workflow is merged).
- Staging wallet integration depends on QuartzPlay staging, which is gated on its own schema replay proof.
- Two prunable external worktrees under a temporary system directory are registered in `git worktree list`.

### Ready for Proposal

Yes, for change 1 (`iaqp-openspec-consolidation`). The orchestrator must confirm with the user: authorization for the read-only staging inventory in change 2, whether to retire the stale checkouts and the abandoned `feat/iaqp-staging-runtime-readiness` branch, and the product ordering relative to QuartzPlay.

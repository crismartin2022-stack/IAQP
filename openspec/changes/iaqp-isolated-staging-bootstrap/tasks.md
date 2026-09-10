# Tasks: Isolated IAQP Staging Bootstrap

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 460-620 |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 migration -> PR 2 readiness/CORS -> PR 3 wallet guard -> PR 4 topology and smoke |
| Delivery strategy | ask-on-risk |
| Chain strategy | feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|---|---|---|---|
| 1 | Empty-schema migration | PR 1 | Base: feature/tracker; rehearsal evidence; forward-fix rollback. |
| 2 | Policy, CORS, and readiness | PR 2 | Base: PR 1 branch; manual HTTP evidence. |
| 3 | Wallet destination guard | PR 3 | Base: PR 2 branch; no-request evidence. |
| 4 | Topology runbook and smoke | PR 4 | Base: PR 3 branch; owner evidence. |

## Phase 1: Schema Foundation

- [x] 1.1 Create `supabase/migrations/<timestamp>_initial_iaqp_schema.sql` for `iaqp_semillas`, `iaqp_rondas`, `iaqp_apuestas`, and `iaqp_movimientos`, with required constraints and pending-movement index.
- [x] 1.2 Create idempotent synthetic-only `supabase/seed.sql`; do not include production or QuartzPlay records.
- [x] 1.3 Record manual migration evidence: on an empty isolated Supabase project run `supabase db reset`, `supabase db push`, and `supabase migration list --linked`; rerun approved path and record parity without connection values.

#### Unit 1.3 Migration Evidence

| Check | Redacted result |
|---|---|
| Prior reset run 1 | `supabase db reset --linked` completed successfully against isolated IAQP Staging. |
| Prior reset run 2 | `supabase db reset --linked` completed successfully against isolated IAQP Staging. |
| Parity check | `supabase migration list --linked` completed successfully. Local `20260910150000` equals remote `20260910150000`; parity passed. |

## Phase 2: Runtime Readiness And Origins

- [x] 2.1 Modify `main.py` to validate `APP_ENV` and non-local `ALLOWED_ORIGINS`: exact HTTP(S) origins only; reject wildcards, paths, queries, credentials, and invalid values.
- [x] 2.2 Modify `main.py` to preserve liveness-only `/salud` and add `/ready`, acquiring `get_pool()` then executing `SELECT 1`; return generic `503` and log only error class on failure.
- [x] 2.3 Create `.env.example` with non-secret placeholders for `APP_ENV`, `ALLOWED_ORIGINS`, `DATABASE_URL`, `QP_URL`, `QP_ALLOWED_HOSTS`, and `IAQP_SERVICE_KEY`.
- [x] 2.4 Add deterministic ASGI regression tests for approved/unapproved CORS and database-up/database-down `/ready`; run compilation and legacy smoke separately from test assertions.

#### Unit 2 Test Evidence

| Command | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit2-venv/bin/python -m unittest discover -s tests -v` | Passed: 8 tests. |
| `APP_ENV=staging ALLOWED_ORIGINS=https://approved.example PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit2-venv/bin/python -m compileall -q .` | Passed: exit 0. |
| `APP_ENV=staging ALLOWED_ORIGINS=https://approved.example PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit2-venv/bin/python pruebas.py` | Passed: exit 0; informational RNG smoke only, not an assertion. |

## Phase 3: Wallet Boundary

- [x] 3.1 Modify `billetera.py` to parse `QP_URL` and require staging HTTPS hostname membership in `QP_ALLOWED_HOSTS`, rejecting production or unapproved targets before `httpx.AsyncClient` request creation.
- [x] 3.2 Record allowed-host and rejected-host manual/stub evidence, proving rejected configuration sends no request and logs no URL credentials, keys, or authorization headers.
- [x] 3.3 Run `python3 -m compileall -q .` and `python3 pruebas.py`; record exact result and wallet-mutation status as `N/A` because this change authorizes no transaction.

#### Unit 3 Test Evidence

| Check | Result |
|---|---|
| Allowed host stub | `https` destination with exact `QP_ALLOWED_HOSTS` membership created one stubbed request. |
| Rejected host stub | Unapproved URL with URL credentials raised a generic definitive error before `httpx.AsyncClient`; no request or wallet log was emitted. |
| Non-HTTPS stub | `http` destination raised a generic definitive error before `httpx.AsyncClient`. |
| Production compatibility stub | Existing production request behavior proceeded without a staging allowlist restriction. |
| Deterministic tests | `PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit3-venv/bin/python -m unittest discover -s tests -v` passed: 13 tests. |
| Compilation | `APP_ENV=staging ALLOWED_ORIGINS=https://approved.example PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit3-venv/bin/python -m compileall -q .` passed: exit 0. |
| Legacy smoke | `APP_ENV=staging ALLOWED_ORIGINS=https://approved.example PYTHONDONTWRITEBYTECODE=1 /var/folders/sw/9651fn8523j550fx9rs3htmh0000gn/T/opencode/iaqp-unit3-venv/bin/python pruebas.py` passed: exit 0; informational RNG smoke only, not an assertion. |
| Wallet mutation | `N/A` -- no transaction was authorized or sent. |

## Phase 4: Isolated Topology And Smoke

- [ ] 4.1 Update `STAGING_AND_RELEASE_PLAN.md` with protected `staging`, dedicated IAQP Railway service/generated HTTPS domain, separate empty Supabase identity, required variables, migration command, and redaction checklist.
- [ ] 4.2 Add owner smoke procedure: record branch, service, project reference, domain, revision, migration parity, `/ready`, and redacted logs; reject `/salud`, game, betting, and wallet smoke.
- [ ] 4.3 Document failure boundary: halt promotion, disable traffic or redeploy known-good revision, retain database, and forward-fix migrations without production, QuartzPlay, or destructive schema rollback.

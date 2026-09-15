# Design: Isolated IAQP Staging Bootstrap

Create staging safeguards before exposing IAQP game or wallet behavior. Cloud actions remain owner-operated evidence, not automation.

## Technical Approach

Use one initial migration for four tables used by `ciclo.py`, `billetera.py`, and `main.py`; game rules and transitions stay unchanged. Validate policy before startup, retain `/salud` as liveness, add database-only `/ready`, and reject invalid wallet targets before HTTP.

## Architecture Decisions

| Decision | Alternatives considered | Rationale |
|---|---|---|
| SQL migration | Runtime DDL; console schema | Versioned SQL makes empty Supabase repeatable; runtime DDL hides drift. |
| Current-query schema | Redesign; QuartzPlay data | Four IAQP-only tables support writes/audits without changing rules or wallet ownership. |
| `/ready`: pool + `SELECT 1` | Reuse `/salud`; query game data | Proves database reachability without data or mutation. |
| Fail-closed CORS | `*`; inferred origins | Invalid non-local lists fail startup. |
| Parsed wallet host allowlist | Prefix/blocklist; mutation proof | Rejects production/unapproved targets before any request. |

## Data Flow

```text
Railway staging variables
  -> startup policy validation -> asyncpg pool -> live tables
  -> GET /ready -> acquire pool -> SELECT 1 -> 200 or generic 503

bet/payout -> billetera._llamar -> validate QP_URL host -> httpx -> QuartzPlay staging only
browser Origin -> CORSMiddleware -> explicit ALLOWED_ORIGINS -> IAQP API
```

`DATABASE_URL` exists only in Railway staging variables and targets a dedicated empty IAQP Supabase project. `QP_URL` and `IAQP_SERVICE_KEY` remain QuartzPlay-owned integration inputs; no balance or QuartzPlay record enters IAQP storage.

## File Changes

| File | Action | Description |
|---|---|---|
| `supabase/migrations/<timestamp>_initial_iaqp_schema.sql` | Create | Four tables, keys/FKs, uniqueness, statuses, timestamps, JSON fields, pending index. |
| `supabase/seed.sql` | Create | Idempotent synthetic fixture, or empty no-op seed. |
| `main.py` | Modify | Policy validation, `/ready`, explicit CORS; preserve `/salud`. |
| `billetera.py` | Modify | Validate destination before outbound calls; never log URL/key. |
| `.env.example` | Create | Non-secret names and placeholders. |
| `STAGING_AND_RELEASE_PLAN.md` | Modify | Owner evidence, migration command, target identity, rollback. |
| `pruebas.py` | Modify | Manual evidence cases if its script structure permits. |
| `tests/test_runtime_readiness.py` | Create | Deterministic CORS and readiness regression tests (added during apply). |
| `tests/test_wallet_guard.py` | Create | Stub-based wallet destination guard tests (added during apply). |

## Interfaces / Contracts

```text
GET /salud  -> 200 {"ok": true, "mesas": [...]}  # no database probe
GET /ready  -> 200 {"ok": true} | 503 {"ok": false}

Runtime variables:
APP_ENV=local|staging|production
ALLOWED_ORIGINS=<comma-separated exact origins>
QP_URL=<HTTPS QuartzPlay base URL>
QP_ALLOWED_HOSTS=<comma-separated staging hosts; required in staging>
DATABASE_URL, IAQP_SERVICE_KEY
```

For `staging` and `production`, origins MUST be exact `http`/`https`, without path/query/credentials or `*`. In staging, `QP_URL` MUST be HTTPS and hostname equal `QP_ALLOWED_HOSTS`; no production host may appear. Invalid config raises generic errors without values. `/ready` logs error class only and returns generic `503`.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Migration | Empty schema and repeatability | `supabase db reset`, `db push`, and `migration list --linked` parity. |
| Runtime | CORS and readiness paths | Deterministic ASGI unittest suite in `tests/test_runtime_readiness.py`; verify no secret response/log. |
| Wallet | Allowed/rejected hosts before `httpx` | Stub-based unittest suite in `tests/test_wallet_guard.py`; no-request evidence. |
| Regression | RNG/roulette | `python3 pruebas.py`; `python3 -m compileall -q .` |

Limits: no CI database, cloud credentials, QuartzPlay staging API, or wallet mutation is available. Owner gates supply this proof. (Updated 2026-09-15: the unittest suites above were added during apply.)

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or process-integration boundary.

## Migration / Rollout

Apply only to dedicated empty IAQP Supabase after owner verifies identity without connection data. Railway staging deploys only `staging`, has distinct variables/domain, and healthchecks `/ready`; production stays `main`-only. Record branch protection, service/environment, project reference, domain, revision, migration parity, `/ready`, and redacted logs. Do not configure QuartzPlay or send wallet transactions.

Rollback: halt promotion; disable staging traffic or redeploy prior known-good revision. Retain database for diagnosis and forward-fix migrations; never blindly reverse schema, use unknown Railway Postgres, touch production, or mutate QuartzPlay.

## Open Questions

- [ ] Owner must provide approved staging QuartzPlay hostnames before wallet-enabled staging can start.
- [ ] Confirm whether staging bootstrap should run live loops before a separate synthetic wallet/test-account change authorizes game smoke tests.

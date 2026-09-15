# Proposal: Isolated IAQP Staging Bootstrap

## Intent

Provide isolated IAQP staging with no production data or QuartzPlay coupling. Staging must prove schema readiness, explicit origins, and no production wallet traffic.

## Scope

### In Scope
- Versioned migrations and repeatable empty-database path; data is synthetic.
- Database-aware `/ready`; `/salud` remains liveness-only.
- Explicit non-local `ALLOWED_ORIGINS` policy and a staging wallet destination guard that rejects production or unapproved targets without logging secrets.
- Owner-operated `staging`, dedicated Railway service/domain, empty Supabase project, and deployment evidence.

### Out of Scope
- QuartzPlay code, configuration, account creation, or wallet smoke transactions.
- Data copying, secret values, DNS changes, CI, alerts, backups, or restore drills.
- Roulette rules, draw timing, seed isolation, settlement behavior, and wallet balance ownership.

## Capabilities

### New Capabilities
- `isolated-staging-runtime`: Schema, readiness, CORS, and wallet-target controls.
- `isolated-staging-topology`: Branch, service, database, domain, evidence, and rollback controls.

### Modified Capabilities
None.

## Approach

Deliver safeguards before infrastructure exposure. Migrate a separate empty Supabase project and deploy protected `staging` only to dedicated IAQP Railway. QuartzPlay may consume approved origin later in its own change.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `supabase/migrations/` | New | Canonical IAQP schema path. |
| `main.py` | Modified | Readiness, startup, and explicit CORS policy. |
| `billetera.py` | Modified | Staging wallet destination validation. |
| `STAGING_AND_RELEASE_PLAN.md` | Modified | Evidence and owner runbook. |
| Railway, Supabase, GitHub | New | Owner-operated staging topology. |

## Gates

- Migration rehearsal provisions an empty staging database; no production or QuartzPlay data exists.
- `/ready` acquires a database connection and runs a minimal query; logs expose no secrets.
- Staging rejects wildcard CORS and production/unapproved wallet targets; no wallet mutation occurs in this change.
- Owner records branch, isolated project/service/database identities, domain, revision, `/ready`, and redacted logs.

## Rollout and Rollback

Roll out reviewed feature branches into protected `staging`; owner then provisions isolated service/database, migrates it, and enables traffic. On failure, halt promotion, disable traffic or redeploy prior revision, retain database for diagnosis, and forward-fix migrations. Never blindly roll back schema, touch production, or mutate QuartzPlay.

## Workload Forecast

Expected delivery: four reversible units: migrations, readiness/CORS, wallet guard, and topology/runbook. Total likely exceeds 400 changed lines.

Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High

## Status (2026-09-15)

Units 1–3 (migration, readiness and CORS, wallet guard) are merged into `staging` through PRs #6, #8, and #10; `tasks.md` records 10/13. Unit 4 (topology runbook and smoke) is open.

## Success Criteria

- [ ] An empty isolated database reaches required IAQP schema version reproducibly.
- [ ] `/ready` proves database readiness; `/salud` is not accepted as readiness evidence.
- [ ] Staging accepts only explicit origins and cannot call production wallet hosts.
- [ ] Owner evidence proves branch, service, Supabase project, domain, revision, and zero-data isolation.

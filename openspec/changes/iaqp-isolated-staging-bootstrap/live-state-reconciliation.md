# Live-State Reconciliation: IAQP Isolated Staging Bootstrap

- **Date:** 2026-09-15
- **Recorded by:** `iaqp-openspec-consolidation`
- **Method:** read-only listing with the existing Railway and Supabase CLI sessions; variable names only. No values, identifiers, domains, hostnames, or rows were read or recorded.
- **Authorization:** owner-approved for the staging projects only; no production project was queried.

## Observations

| Resource | Expected by tasks and design | Observed | Divergence | Owner action |
|---|---|---|---|---|
| Railway staging project | Dedicated IAQP project with one service deploying only `staging` (4.1) | Project `IAQP Staging` exists; its single environment is named `production`; service `staging-api` deploys from branch `staging`; last deployment succeeded on 2026-09-11; a public domain exists | Environment name reads as production; a deployment exists before the phase-4 runbook | Optional rename (non-blocking); record runbook evidence under 4.1–4.2 |
| Service variable names | `APP_ENV`, `ALLOWED_ORIGINS`, `DATABASE_URL`, `QP_URL`, `QP_ALLOWED_HOSTS`, service key (design contract) | All six names present | None by name | Confirm `QP_URL` targets QuartzPlay staging and `DATABASE_URL` targets the IAQP staging Supabase project; a value-level host match needs separate approval |
| Supabase project | Separate empty IAQP project (4.1) | `IAQP Staging` is active, PostgreSQL 17, 0 Edge Functions; migration parity recorded under task 1.3 | Row, Auth, and Storage counts unmeasured | Zero-data proof needs linked or credentialed access under separate approval |
| Readiness | Ready endpoint result recorded by the owner (4.2) | Not checked; no HTTP probe was authorized | Unknown | Owner smoke under 4.2 |

## Task Status Effect

- Tasks 4.1–4.3 stay open; this inventory closes no task.
- No completed task depends on a resource the inventory failed to observe; task 1.3 migration evidence stands.

## Commands (identifiers replaced)

- `railway list --json`
- `railway service list --project <ref> --environment <env> --json`
- `railway deployment list --project <ref> --environment <env> --service <name> --limit 1 --json`
- `railway variable list --project <ref> --environment <env> --service <name> --json | jq keys`
- `supabase projects list -o json`
- `supabase functions list --project-ref <ref> -o json`

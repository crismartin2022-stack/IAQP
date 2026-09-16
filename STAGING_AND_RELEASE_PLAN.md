# IAQP Staging and Release Plan

**Status:** staging runbook in force since 2026-09-16. It supersedes the draft kept at
`openspec/changes/iaqp-isolated-staging-bootstrap/release-plan-draft.md`, which remains history only.
This document authorizes no production change.

## Topology

| Layer | Staging | Production |
|---|---|---|
| Git branch | `staging` (protected; changes arrive only through reviewed PRs) | `main` (protected; release PRs from `staging` only) |
| Railway | Project `IAQP Staging`, service `staging-api`, deploy trigger `staging`, Railway-generated HTTPS domain | Separate production project; never shared with staging |
| Database | Supabase project `IAQP Staging`, separate and synthetic-data only | Separate production database |
| Wallet target | QuartzPlay **staging** API only | QuartzPlay production API |

Railway names the single environment inside the staging project `production`. That is a naming
artifact, not a production binding; the project is the isolation boundary.

## Required Variables (names only)

| Variable | Rule |
|---|---|
| `APP_ENV` | `staging`. Startup fails closed on any other non-local value mismatch |
| `ALLOWED_ORIGINS` | Exact `https` origins of approved staging frontends; no wildcard, path, query, or credentials |
| `DATABASE_URL` | Supabase `IAQP Staging` (pooler or direct host); never a Railway Postgres of unknown ownership |
| `QP_URL` | `https` base URL of the QuartzPlay staging API |
| `QP_ALLOWED_HOSTS` | Must contain the `QP_URL` host and must never contain a production host |
| `IAQP_SERVICE_KEY` | Distinct from production |
| `ANTHROPIC_API_KEY` | Optional; when absent the dealer chat returns an explicit unconfigured result |

## Migrations

- Source of truth: ordered SQL files in `supabase/migrations/`.
- Apply only to `IAQP Staging`: `supabase link --project-ref <ref>` then `supabase db push --linked`,
  with the database password read from a local file and never printed or committed.
- Parity check: `supabase migration list --linked`; every local version must appear remotely and no
  remote version may be missing locally.
- Recovery is forward-fix only. Never reverse schema destructively.

## Redaction Checklist

Record only statuses, booleans, counts, and version numbers. Never record connection strings,
passwords, keys, project references, domains, hostnames, rows, player identifiers, or raw logs that
contain any of them.

## Smoke Procedure

Read-only. Run after every deployment to `staging`. Every row must pass.

| # | Check | Pass criterion |
|---|---|---|
| 1 | Deployment | Latest `staging-api` deployment is `SUCCESS` and its revision equals the `staging` tip |
| 2 | Environment | `APP_ENV` is `staging` |
| 3 | Origins | `ALLOWED_ORIGINS` has no wildcard |
| 4 | Database target | `DATABASE_URL` host is Supabase and carries the `IAQP Staging` project reference |
| 5 | Wallet target | `QP_URL` is `https`, its host is in `QP_ALLOWED_HOSTS`, equals the QuartzPlay staging API host, and no production host is allowlisted |
| 6 | Liveness | `GET /salud` returns 200 with `ok: true`. Liveness only; never readiness evidence |
| 7 | Readiness | `GET /ready` returns 200 with `{"ok": true}` |
| 8 | CORS | An allowed origin receives `Access-Control-Allow-Origin`; a disallowed origin does not |
| 9 | Migration parity | Local and remote migration versions match |

Record for each run: branch, service, deployment status, revision match, migration parity, readiness
result, CORS result, and redacted log notes. Keep project references and domains outside Git.

**Out of scope for smoke:** game rounds, betting, wallet debits or credits, and any use of `/salud`
as readiness proof. These need a separate, owner-approved integration test with isolated test
accounts.

## Failure Boundary

1. **Halt promotion.** No PR from `staging` to `main` while any smoke row fails.
2. **Restore service.** Redeploy the last known-good `staging-api` deployment in Railway, or disable
   the staging domain if the failure exposes data or credentials.
3. **Retain the database** for diagnosis. Do not reset, restore, or recreate it without owner approval.
4. **Forward-fix** code and migrations through a new PR to `staging`; never patch `staging` directly.
5. **Never touch** production resources or QuartzPlay while handling a staging failure.
6. **Secret exposure:** rotate or revoke the credential first, then fix configuration and rescan.

## Promotion to Production

Not authorized by this document. A release requires a PR from `staging` to `main`, current smoke
evidence, a migration and rollback plan, required checks green, and explicit owner approval of the
release window.

## Known Gaps (2026-09-16)

- `ANTHROPIC_API_KEY` is absent in staging, so the dealer chat is unconfigured there.
- Unit suites under `tests/` need `httpx` installed locally to run.
- Required-check enforcement on `staging` and `main` must be confirmed by a repository administrator.

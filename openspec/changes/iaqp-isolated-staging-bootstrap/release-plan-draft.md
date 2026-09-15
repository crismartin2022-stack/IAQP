> **Draft, not an approved plan.** Moved from the repository root on 2026-09-15 as phase-4 input for `iaqp-isolated-staging-bootstrap`. Some audit claims are stale (for example, the Semgrep workflow is reported absent but is merged on `main` and `staging`). Re-verify every claim before use.

# IAQP Staging And Release Plan

This is an execution plan, not infrastructure configuration. It gives a non-programmer product owner clear approval points while Claude prepares small, reviewable pull requests. No production data, credentials, domains, or cloud resources are changed by following this document until the owner explicitly approves each external action.

## Current Verified State

### IAQP repository

| Area | Verified state | Delivery consequence |
|---|---|---|
| Git | Branch is `main`; remote is `crismartin2022-stack/IAQP` | Create and protect `staging` before feature delivery. |
| Railway configuration | `Procfile` starts `uvicorn main:app --host 0.0.0.0 --port $PORT`; no tracked Railway configuration file or GitHub Actions workflow exists | Railway service, environment bindings, domains, and current deployment branch are not verifiable from this repository. Inspect them read-only before setup. |
| Database | `main.py` requires `DATABASE_URL` and creates an `asyncpg` pool during application startup | A bad database binding prevents startup. Staging needs its own Supabase connection string and readiness test. |
| Cross-service wallet | `billetera.py` reads `QP_URL` and `IAQP_SERVICE_KEY` | Staging must call a designated QuartzPlay staging API using a distinct service key. It must never point at production. |
| Browser access | `ALLOWED_ORIGINS` defaults to `*` | Require an explicit staging allowlist before exposing a staging domain. |
| Schema delivery | `supabase/config.toml` exists, but no versioned SQL migrations are present | Establish canonical migrations and repeatable seed/test data before any staging database is used. |

### Railway evidence and boundary

The verified QuartzPlay repository audit records an active Railway backend connected to Supabase, with Railway Postgres retained as backup and a separate failed Railway service. That evidence is for QuartzPlay, not proof of IAQP's current Railway bindings. Treat every existing Railway Postgres service as **unknown ownership and unknown data** until an owner identifies it read-only.

**Decision:** do not repurpose, attach, reset, migrate into, or use an unknown Railway Postgres service for IAQP staging. Create a dedicated Supabase staging project instead.

## Target Delivery Model

```text
feature branch -> PR to staging -> required checks + staging deploy + owner acceptance
staging -> PR to main -> required checks + production release approval -> production deploy

IAQP Railway staging -> Supabase staging
IAQP Railway production -> Supabase production
QuartzPlay staging API -> IAQP staging wallet integration
```

Railway supports per-environment configuration and service deployment triggers by Git branch. Configure staging services to deploy only from `staging`; leave production services deploying only from `main`. Use separate environment-scoped variables and domains.

Supabase staging is a separate project with its own credentials, schema lifecycle, backups, and restore exercise. It is not a copy of a production connection string and not a shared database with QuartzPlay.

## Responsibilities And Approval Points

| Role | Owns | Must approve or perform |
|---|---|---|
| Product owner | Product risk, access, release decision | Creates/authorizes cloud resources; approves data policy, staging acceptance, and each production release. |
| Claude | Code and documentation changes in feature branches | Prepares one work unit per PR, tests it, reports evidence, and never uses or prints secrets. |
| Technical reviewer | Safety and operational review | Reviews migrations, environment separation, monitoring, rollback evidence, and required-check results. |
| GitHub administrator | Repository controls | Creates/protects `staging` and `main`, configures required checks, and grants least-privilege access. |
| Railway/Supabase owner | Cloud configuration | Performs approved console changes, stores secrets in platform controls, validates values by name and target only. |

The product owner works with Claude by opening one approved issue per outcome, asking Claude for a `type/description` branch and PR, reviewing the plain-English acceptance evidence, then approving merge. Claude must not merge, deploy, alter secrets, or create cloud resources without explicit owner action.

## Code-Preparation Prerequisites

Complete these PRs before creating public staging traffic. Keep tests and documentation in same work unit as behavior.

1. Add canonical, ordered SQL migrations under `supabase/migrations/`, plus repeatable fake staging seed data. Document schema ownership and migration command. Do not seed real customer, betting, payment, or Telegram data.
2. Add a database-aware `/ready` endpoint that checks pool acquisition and a minimal query with a short timeout. Keep `/salud` as liveness only; neither endpoint may reveal credentials, connection strings, stack traces, or internal data.
3. Replace wildcard CORS with an explicit `ALLOWED_ORIGINS` requirement outside local development. Configure staging and production lists independently.
4. Make all external destinations environment-configured: `DATABASE_URL`, `QP_URL`, `IAQP_SERVICE_KEY`, `ANTHROPIC_API_KEY`, and allowed origins. Add a committed `.env.example` containing names and non-secret placeholders only.
5. Add startup validation that fails clearly when required production/staging variables are absent, malformed, or point to a disallowed production host from staging. Never log variable values.
6. Add a staging-safe integration mode. Wallet mutations must target only QuartzPlay staging with isolated test accounts and an independent key. Disable or stub any real-money, notification, scheduled retry, or external-provider action until its staging credential and behavior are tested.
7. Add automated tests for startup validation, CORS policy, `/ready`, failed database readiness, and wallet destination selection. Keep existing `python -m pruebas.pruebas` passing.
8. Add structured logs and deployment correlation: environment name, release revision, request ID, readiness failures, wallet outcome category, and error class. Redact authorization headers, connection strings, and query parameters carrying secrets.

## Supabase Staging Setup

1. Owner creates a new empty Supabase project named for IAQP staging. Confirm project reference and region without recording credentials in GitHub, chat, source, or this document.
2. Claude prepares migrations and database tests. Technical reviewer confirms migrations can provision an empty database deterministically.
3. Owner runs approved migration process through CI/CD, not an ad-hoc production laptop command. Supabase recommends CI/CD migration checks and required checks to block invalid migrations.
4. Populate only synthetic data, or an owner-approved anonymized dataset with no secrets or personal data. Record source, scope, and deletion date outside the repository.
5. Store staging connection details only in Railway staging variables and required CI secret storage. Verify target by project reference/host suffix, never by displaying the URL.
6. Establish backup policy for both Supabase projects. Before production release enablement, perform and record a staging restore drill into a disposable, separate target; verify migration version and essential read/write behavior; then destroy that drill target.

## Railway Staging Setup

Perform only after code prerequisites pass.

1. Owner performs a read-only Railway inventory: project, environments, services, deployment branches, domains, healthchecks, variable names, and status. Record no values or credentials. Classify any Railway Postgres service before touching it; unknown means out of scope.
2. Create a Railway `staging` environment by duplicating service topology from production only after owner review. Duplication is a starting topology, not permission to retain production settings.
3. For every IAQP staging service, set deployment trigger branch to `staging`. Verify every production service remains triggered only by `main`.
4. Assign unique staging domains. Configure `ALLOWED_ORIGINS` to those staging frontend origins only.
5. Replace copied configuration with staging-specific values: Supabase staging `DATABASE_URL`, QuartzPlay staging `QP_URL`, unique `IAQP_SERVICE_KEY`, staging provider credentials, and staging-only public URLs. Remove or disable production-only integrations.
6. Set Railway healthcheck to `/ready` only after its database-safe implementation has been deployed. Set suitable deployment timeout and inspect deploy logs for startup/readiness failure.
7. Add Railway log/metric alerts for deploy failure, repeated readiness failure, unhandled 5xx responses, database connection exhaustion, and wallet retry/failure threshold. Alerts must go to a staging-only operational channel first.
8. Run a smoke deployment from a harmless commit merged into `staging`; verify service revision, environment label, staging database target, domain isolation, readiness, logs, and test wallet behavior.

## Test And Observability Gates

| Gate | Evidence required before merge to `staging` | Evidence required before merge to `main` |
|---|---|---|
| Code | Formatter/linter, unit tests, `python -m pruebas.pruebas`, migration validation, and required GitHub checks pass | Same checks pass against latest `staging`; no unreviewed production-only change. |
| Security | Semgrep required check passes; no exposed secret is accepted | Same required check passes; all high-severity findings resolved or formally risk-accepted by owner and reviewer. |
| Database | Empty-project migration rehearsal and database tests pass | Staging migration and restore-drill evidence is current; production migration has rollback/forward-fix plan. |
| Deployment | Railway staging deploy is healthy and `/ready` passes | Owner approves release window; production deploy and `/ready` pass. |
| Integration | Staging-only QuartzPlay wallet tests use test accounts and prove no production request | Re-run relevant staging flow; production integration is enabled only after owner approval. |
| Observability | Logs identify revision/environment and contain no secrets; alerts tested | Post-release logs/metrics are stable through agreed observation window. |

Do not promote on a green deploy alone. A release requires both technical evidence and product-owner acceptance of affected flows.

## Semgrep Plan

### Audited integration status

Audit date: 2026-09-02. Both Git repositories were checked for tracked `.github` workflows, tracked Semgrep-named files, YAML workflow/configuration files, and Semgrep references in relevant source/configuration files.

| Repository | Exact status |
|---|---|
| IAQP (`IAQP`) | **Absent.** No tracked `.github` directory, GitHub Actions workflow, Semgrep file/configuration, or Semgrep reference was found. |
| QuartzPlay (`app`) | **Absent.** No tracked `.github` directory, GitHub Actions workflow, Semgrep file/configuration, or Semgrep reference was found. Its only tracked YAML file is `openspec/config.yaml`, not CI. |

This audit verifies repository integration only. It does not claim that Semgrep AppSec Platform, authenticated Semgrep CI, organization policies, historical cloud scans, or remote GitHub checks are configured.

### Required implementation PR (future work; not created now)

1. Add one GitHub Actions workflow in each repository, or deliberately document a shared reusable workflow if both repositories are moved into one controlled workflow design. Do not create it as part of this plan.
2. Trigger it on `pull_request` events whose base branch is `staging` or `main`. Use least privilege: `permissions: contents: read`.
3. Install Semgrep CLI with this exact pinned version: `python -m pip install semgrep==1.174.0`. Do not use an unpinned action, `latest`, or a floating package range.
4. Run this required blocking command in every applicable PR job: `semgrep scan --config=auto --error`. Semgrep documents that `--error` makes findings produce a failing exit status.
5. Name check consistently, for example `Semgrep / scan`, then make that exact check required on both `staging` and `main` branch protection rules. Required-check configuration happens only after first successful workflow run exposes check name.
6. Do not set `SEMGREP_APP_TOKEN`, do not use `semgrep ci`, and do not state authenticated product capabilities are enabled. If owner later wants Semgrep platform reporting, create a separate approved setup task defining access, retention, and token handling.

### Secrets scan strategy

1. Run `semgrep scan --config=auto --error` on every PR as above. Treat any secret-like finding as a release blocker.
2. Add a separate repository-history and working-tree secret review before first enforcement and after any exposure incident. Use an approved dedicated secret scanner or Semgrep capability only after its exact command, scope, credential model, and false-positive process are reviewed. Do not assume authenticated historical Semgrep scanning exists.
3. If a credential appears in source, CI output, commit history, issue, or log: stop promotion; revoke/rotate it with provider owner; remove it from active code; clean history only under an approved incident procedure; then rescan and document evidence without copying secret material.
4. Configure Actions logs to avoid printing environment values. Pass secrets only through GitHub/Railway secret stores; mask errors and avoid diagnostic commands that dump environments.

### Baseline and legacy-code transition

1. Before making Semgrep required, run an owner-approved full scan in an isolated CI run and triage every result: fix, precise documented suppression with rationale/expiry, or accepted risk with owner and reviewer approval.
2. Create a reviewed baseline commit/reference after triage. During transition, PR scans may use Semgrep's `--baseline-commit <approved-baseline>` addition so unchanged legacy findings do not hide new risk. Fetch sufficient Git history in Actions for this mode.
3. New or changed code must have zero unresolved blocking findings. Baseline does not excuse a finding in changed code.
4. Set a dated burn-down target and remove baseline mode once legacy findings are fixed or explicitly suppressed. Keep `--error` throughout; no blanket exclusion, silent ignore, or downgrade of critical rules.

### Failure handling

| Failure | Required response |
|---|---|
| Semgrep finding | PR stays unmerged. Claude fixes code, adds a narrowly scoped justified suppression only when reviewer approves, or owner records risk acceptance. Rerun check. |
| Semgrep tool/config failure | PR stays unmerged. Fix pinned installation, workflow permissions, checkout history, or rule retrieval; do not bypass by removing `--error`. |
| Suspected secret | Stop release and follow secrets response above. Rotation precedes merge. |
| False positive | Reviewer verifies it; record rationale close to suppression, scope it to one rule/location, set review date, and keep check required. |

## Branch And PR Flow

1. GitHub administrator creates `staging` from reviewed `main`, protects both branches, blocks direct pushes, requires one approved review, requires current branch, and enables required checks including Semgrep after it exists.
2. Product owner opens an approved issue. Claude creates a branch matching `type/description`, for example `feat/readiness-endpoint`, from `staging`.
3. Claude makes one independently reversible work unit per commit, using a Conventional Commit message. Tests, migration, and documentation for that behavior stay with it. Split work nearing 400 changed lines into chained PRs.
4. Claude opens a PR from feature branch to `staging`, links approved issue, adds exactly one `type:*` label, and supplies test/rollback evidence. Product owner and reviewer approve only after all required checks pass.
5. Railway deploys `staging`. Owner runs acceptance checklist and records pass/fail. A failed staging test returns work to a new feature PR; never patch `staging` directly.
6. Claude or owner opens a release PR from `staging` to `main`. It contains no unrelated changes, repeats required checks, includes staging evidence, migration plan, rollback plan, and owner release approval.
7. Merge to `main` only in approved release window. Railway deploys production from `main`; owner observes health and key metrics before declaring release complete.

## Rollback

1. **Staging incident:** halt promotion, disable affected staging integration/traffic, revert only offending work-unit PR or redeploy prior known-good staging revision. Keep staging database for diagnosis unless it contains prohibited data.
2. **Production application incident:** stop promotion, identify last known-good revision, use Railway rollback/redeploy procedure approved by owner, and verify `/ready`, logs, and critical read-only flow. Do not roll back database schema blindly.
3. **Migration incident:** prefer a tested forward fix. Restore only from verified backup into a separate recovery target first; owner and reviewer approve any production restore after data-loss impact is known.
4. **Secret incident:** rotate/revoke first, then fix deployment/configuration and rescan. A code revert does not invalidate an exposed credential.
5. For every rollback, record trigger, revision, environment, data impact, actions, verification, and follow-up issue without storing secrets.

## Execution Order

1. Owner approves isolated-environment and synthetic-data policy.
2. Claude delivers migrations, readiness, configuration validation, CORS, staging-safe integration flags, tests, and observability in small PRs to `staging`.
3. GitHub administrator creates/protects `staging` and implements required PR controls.
4. Owner creates isolated Supabase staging; team validates migrations, test data, backups, and restore drill.
5. Owner inventories Railway read-only, then creates/configures staging with separate domains and variables.
6. Team ships harmless staging deploy and completes test/observability gates.
7. Team implements Semgrep workflow in separate PRs, establishes baseline transition, then enables required checks.
8. Product owner approves first release PR from `staging` to `main`; monitor and close release only after acceptance gates pass.

## Acceptance Criteria

- [ ] IAQP staging uses a newly created, isolated Supabase project; no unknown Railway Postgres service is used.
- [ ] Staging and production have distinct Railway environment variables, domains, database targets, wallet targets, and credentials.
- [ ] IAQP database schema is reproducible from versioned migrations and verified by CI/database tests.
- [ ] `/ready` proves database readiness without exposing sensitive information; Railway healthcheck uses it.
- [ ] Staging has passed synthetic-data, wallet-isolation, CORS, deployment, alert, and log-redaction checks.
- [ ] `staging` and `main` are protected; feature work reaches them only through reviewed, labeled, issue-linked PRs.
- [ ] IAQP and QuartzPlay each have a future Semgrep PR plan that pins CLI to `1.174.0`, runs `semgrep scan --config=auto --error` on PRs into `staging` and `main`, and makes check required after rollout.
- [ ] Semgrep transition has a reviewed legacy baseline, strict new-code enforcement, secrets-response process, and no claim of authenticated Semgrep product features without separate setup.
- [ ] Rollback and Supabase restore drill evidence exists before first production release using this flow.

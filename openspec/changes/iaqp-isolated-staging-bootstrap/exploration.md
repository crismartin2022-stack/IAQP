# Exploration: iaqp-isolated-staging-bootstrap

> Historical snapshot written before implementation. As of 2026-09-15, migrations, database-aware readiness, explicit CORS, and the wallet destination guard are merged into `staging`. Statements below about their absence, and the `ask-always` strategy value, describe the pre-implementation state only.

## Current State

IAQP is an independent FastAPI service. `Procfile` starts `uvicorn main:app` with Railway-provided `$PORT`. Startup requires `DATABASE_URL`, creates an asyncpg pool, then starts two live roulette loops. `QP_URL` and `IAQP_SERVICE_KEY` direct wallet calls to QuartzPlay; IAQP must not own wallet balances.

No tracked Railway configuration, remote branch-protection evidence, or remote Supabase binding exists in this repository. `supabase/config.toml` enables migrations, but the repository contains no migrations. The live loop immediately writes `iaqp_semillas` and `iaqp_rondas`, so a new empty application database has no usable schema. `/salud` reports process/table liveness only; it does not acquire a database connection. CORS defaults to `*`.

The target is an isolated IAQP staging control plane that can eventually supply QuartzPlay with a generated staging API origin through `REACT_APP_IAQP_URL`. QuartzPlay remains a separate repository, deployment, database, and future configuration change. This exploration authorizes no external action.

## Affected Areas

- `openspec/changes/iaqp-isolated-staging-bootstrap/exploration.md` — records scope, minimum topology, evidence, and constraints for later approval.
- `STAGING_AND_RELEASE_PLAN.md` — existing owner-operated staging, rollback, and isolation guidance; it identifies missing migrations and readiness as prerequisites.
- `main.py` — current startup, wildcard CORS, and liveness-only `/salud` establish limits of first-deploy smoke evidence.
- `ciclo.py` — creates application records at startup; proves an empty application database cannot support a valid game smoke test without future schema work.
- `billetera.py` — reads `QP_URL` and `IAQP_SERVICE_KEY`; staging must use only QuartzPlay staging values when wallet testing is separately approved.
- `Procfile` and `supabase/config.toml` — deployment command and local Supabase declaration; neither proves a live Railway/Supabase binding.
- `openspec/config.yaml` — OpenSpec-only workflow, `ask-always` chain strategy, 400-line review budget, strict TDD disabled, and manual evidence baseline.

## Approaches

1. **Dedicated IAQP staging project and empty Supabase project** — owner creates/protects `staging` from reviewed `main`; creates a separate Railway project with one IAQP service deploying only `staging`; creates a separate empty IAQP Supabase staging project; assigns Railway-generated HTTPS domain; records that domain as future QuartzPlay `REACT_APP_IAQP_URL` input.
   - Pros: Strong isolation from production and QuartzPlay; clear rollback by disabling staging traffic or redeploying prior staging revision; no shared database or unknown Railway Postgres ownership; generated domain avoids DNS change.
   - Cons: Requires approved console work and later schema/readiness/CORS work before game behavior can be accepted; creates no QuartzPlay frontend configuration by itself.
   - Effort: Medium.

2. **Shared Railway project or environment with a staging service** — place IAQP staging alongside existing services while retaining a separate service and Supabase project.
   - Pros: Fewer Railway project-level resources.
   - Cons: Weaker least-privilege and blast-radius separation; existing service/variable ownership is not repository-evidenced; easy to copy production settings accidentally.
   - Effort: Low.

3. **Reuse an existing Railway Postgres or Supabase project** — bind staging to an existing database.
   - Pros: Lowest setup time.
   - Cons: Violates requested isolation and no-row policy; ownership and data classification are unknown; rollback and evidence become unsafe.
   - Effort: Low, unacceptable.

## Recommendation

Use Approach 1. Minimum approved bootstrap sequence:

1. GitHub administrator creates `staging` from reviewed `main`, protects it against direct pushes, and requires review/current branch. Feature work targets `staging`; no branch is created by this exploration.
2. Railway/Supabase owner performs a read-only inventory, then creates a dedicated IAQP Railway staging project and one IAQP staging service with deploy trigger `staging`. Production remains `main`-only. Do not reuse unknown Railway Postgres.
3. Owner creates a separate IAQP Supabase staging project with no IAQP application rows, records only project identity/target evidence, and stores its connection value only in Railway staging variables. No values enter Git, OpenSpec, chat, or logs.
4. Owner assigns the Railway-generated HTTPS API domain. This exact origin is the future QuartzPlay frontend input: `REACT_APP_IAQP_URL=https://<generated-iaqp-staging-domain>`. Do not edit QuartzPlay in this change.
5. Until migrations, database-aware readiness, explicit staging CORS, and staging wallet safeguards exist, treat the domain as bootstrap-only. It must not be accepted for player, betting, or wallet smoke testing.
6. Record manual evidence: protected-branch rule names; Railway project/service/environment and `staging` trigger; Supabase project identity and zero IAQP application rows; generated domain; deployment revision/status; `GET /salud` response; and deploy logs showing no secret values. A successful `/salud` does not prove database readiness.
7. Rollback: halt promotion, disable/remove staging traffic or redeploy the prior known-good staging revision, and keep the staging database for diagnosis unless prohibited data was introduced. Do not roll back schema blindly, touch production, or mutate QuartzPlay.

## Risks

- Empty Supabase has no IAQP schema. The application can start its process and return `/salud` while live loops fail their database writes; no game-level smoke is valid yet.
- Current wildcard CORS permits any origin. Exposing the generated domain before a future explicit staging allowlist is a security gap.
- Current wallet configuration has no staging-host guard. Any wallet smoke must wait for separately reviewed QuartzPlay staging URL, distinct service key, and isolated test-account controls.
- Existing remote Railway, GitHub branch protection, and Supabase state are not proven by repository files. Owner must collect read-only evidence before configuration.
- Railway-generated domain can change if service/domain changes. QuartzPlay must consume the approved final domain only in its own change; no implicit frontend coupling.
- Manual evidence is non-automated and must identify target by environment/project/domain names without exposing connection strings or keys.

## Ready for Proposal

Yes. Proposal should scope only approved, owner-operated IAQP staging bootstrap and its evidence/rollback checklist. It must exclude product code, QuartzPlay edits, cloud execution, GitHub changes, Supabase/database mutation, secrets, branches, and deployments from this exploration. Follow-up code changes for migrations, readiness, CORS, and wallet destination validation are prerequisites for usable staging and should be separate reviewable work units under the 400-line feature-branch-chain policy.

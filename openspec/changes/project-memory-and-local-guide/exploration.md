# Exploration: project-memory-and-local-guide

## Current State

IAQP is a standalone Python 3.11-declared FastAPI service. Its checked-in implementation separates pure roulette/RNG rules (`rng.py`, `ruleta.py`) from round lifecycle (`mesa.py`), live-table orchestration (`ciclo.py`), dealer narration and safety filtering (`crupier.py`), wallet integration (`billetera.py`), and HTTP entry points (`main.py`). PostgreSQL is IAQP-owned; QuartzPlay is the wallet balance authority.

The primary repository has only a short Spanish README, a release/staging plan, OpenSpec configuration, and source comments/docstrings. It has no existing main specs or active change artifacts. `openspec/config.yaml` confirms `artifact_store.mode: openspec`, interactive execution, a 400-line review budget, and no configured automated test framework; `python3 pruebas.py` is the manual statistical evidence script.

QuartzPlay was inspected read-only as a dependency source. It contains a separate Python FastAPI/backend and Telegram bot under `app/bot`, plus a React 18 frontend under `app/frontend`. The frontend routes `/`, `/sitio`, `/casino`, `/box/{agency}`, `/agencia`, and `/admin`; the casino surface calls IAQP at `https://api-casino.iaqp.lat`, while sports, agency, admin, box, and support flows call QuartzPlay at `https://api.iaqp.lat`. The QuartzPlay service owns user balances, sports bets/betslips, agencies/influencers, cashier flows, support, and administrative reporting. IAQP must document these as cross-service boundaries, not merge them into IAQP ownership.

Evidence-based safety and ownership invariants to preserve in shared memory:

- The roulette result is generated only after betting closes (`mesa.py`, `ciclo.py`).
- The active server seed is committed by hash before bets and revealed only after rotation; public state excludes the active seed (`rng.py`, `mesa.py`, `main.py`).
- The AI dealer narrates public state and cannot decide or inspect the hidden seed (`crupier.py`).
- IAQP never stores balances. Bets debit QuartzPlay at acceptance; prizes/devolutions use deterministic external references and retry records (`billetera.py`, `ciclo.py`).
- The current IAQP repository has no tracked SQL migrations despite Supabase migration settings and SQL table names in code; schema ownership and reproducible provisioning remain documentation gaps.
- Current code/configuration contains deployment and endpoint assumptions that need verification before being presented as authoritative. Documentation must label verified code evidence, operational assumptions, and open questions separately.

## Affected Areas

- `openspec/config.yaml` — establishes OpenSpec persistence, project context, safety rules, verification commands, and review-budget constraints.
- `README.md` — current IAQP orientation and invariants; likely source for a corrected/expanded shared project-memory document in a later phase.
- `main.py` — service lifecycle, fixed live-table configuration, API routes, database pool, CORS, public verification, and retry loop.
- `rng.py`, `ruleta.py` — certifiable deterministic RNG, roulette rules, payout model, and theoretical RTP.
- `mesa.py`, `ciclo.py` — round state machine, seed rotation, persistence points, payment ordering, retries, and failure behavior.
- `crupier.py`, `billetera.py` — public-state isolation, responsible-gaming response, wallet ownership, idempotency, and failure semantics.
- `pruebas.py`, `requirements.txt`, `Procfile`, `runtime.txt`, `supabase/config.toml` — evidence, runtime/dependency/deployment declarations, and database tooling boundary.
- `/Users/usuario/Documents/Trabajo 2026/iaqp/app/bot/casino_api.py` — read-only dependency evidence for QuartzPlay API ownership, authentication, agency/admin/cashier/reporting features, and wallet-facing endpoints.
- `/Users/usuario/Documents/Trabajo 2026/iaqp/app/bot/server.py`, `db.py`, `bot_handlers.py`, `auth.py`, `odds_api.py` — read-only evidence for Telegram onboarding, account linking, sports bets, persistent agency sessions, PostgreSQL schema bootstrap, and external odds dependency.
- `/Users/usuario/Documents/Trabajo 2026/iaqp/app/frontend/src/index.js`, `App.jsx`, `Web.jsx`, `Casino.jsx`, `Box.jsx`, `Agencia.jsx`, `Admin.jsx` — read-only evidence for surfaces, user journeys, API destinations, and feature maturity.

### Delivered shared documentation structure

The domain-oriented OpenSpec main spec is delivered at `openspec/specs/project-memory/spec.md`. It is navigable and reviewable in this order:

1. **Purpose and system map** — what IAQP and QuartzPlay each do, who uses each surface, and the one-sentence boundary rule.
2. **Repository and deployment map** — IAQP modules, QuartzPlay components, runtime/deployment declarations, and evidence dates.
3. **Ownership and integration contracts** — wallet authority, database ownership, API base URLs, authentication modes, data crossing the boundary, and failure/idempotency behavior.
4. **Core IAQP architecture** — RNG, roulette, round state machine, live loop, persistence, dealer channels, and public verification.
5. **User journeys** — player roulette, player sports/betslip, Telegram onboarding/linking, agency cashier, box terminal, admin operations, cash out, support, and responsible-gaming interruption. Mark QuartzPlay-only and cross-service steps.
6. **Feature catalog and maturity** — feature purpose, owner service, entry point, backing endpoint/module, persistence, status (`verified`, `partial`, `planned`), and known gaps.
7. **Technology stack rationale** — Python/FastAPI, asyncpg/PostgreSQL/Supabase, httpx, React 18/CRA, Telegram WebApp/bot, external odds provider, Anthropic chat, and why each is used; distinguish declared dependencies from observed runtime behavior.
8. **Safety, operational, and verification rules** — non-negotiable invariants, responsible-gaming behavior, manual evidence command, syntax check, rollback/incident boundaries, and secrets exclusions.
9. **Evidence register and open questions** — source path, claim, last verified date, confidence, owner, and unresolved operational facts. Do not record credentials or secret values.

The shared memory should explain architecture and decisions, not duplicate every endpoint body. Endpoint inventories can be concise tables with links to source paths. Each journey should use: actor, entry point, preconditions, happy path, failure path, data ownership, and exit state.

### Delivered local-only guide

The delivered six-page HTML guide is at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/`, with `index.html` and five topical pages. Its sibling placement outside both repositories is the boundary: it is excluded from Git and from the approved IAQP documentation PR. Local assets remain beside the guide and outside both repositories.

## Approaches

1. **OpenSpec shared memory plus external local guide** — delivered as a concise, evidence-backed `project-memory` spec in IAQP and a richer six-page navigable HTML sibling artifact.
    - Pros: Claude in another environment can read the committed source; ownership stays explicit; local-only requirement is enforced by filesystem placement.
    - Constraint: Two representations need a freshness check; HTML is not source of truth.
    - Delivery: One approved documentation-only PR with an accepted size exception.

2. **Single committed documentation tree serving both purposes** — commit Markdown and HTML together in IAQP.
   - Pros: One checkout contains everything; links and rendering are easy to reproduce.
   - Cons: Violates local-only HTML requirement; exposes internal navigational material in the PR; increases review surface and creates generated-file drift.
   - Effort: Medium

3. **External HTML as the source of truth, with a short OpenSpec pointer** — keep full architecture and journeys only in the local artifact and commit a summary/link.
   - Pros: Less committed text.
   - Cons: Boss's Claude cannot read the complete shared memory from the PR; local path is not portable; important boundary decisions become unverifiable.
   - Effort: Low initially, High long-term risk

## Delivered Decision

Approach 1 is delivered. Committed OpenSpec Markdown is portable project memory and authoritative review input. The sibling HTML is a local presentation artifact derived from it, never a Git or PR artifact or source of truth.

This documentation-only change uses one approved IAQP PR under the `exception-ok` / `size-exception` decision. It contains OpenSpec artifacts only, not HTML, QuartzPlay edits, credentials, secret values, or unverified cloud claims.

### Delivery Scope

The staged OpenSpec artifacts are delivered as one documentation-only PR. The approved `exception-ok` / `size-exception` decision supersedes 400-line splitting and chained-PR planning for this change.

No future delivery slices, split PRs, or local-guide generation phases remain for this change.

## Risks

- QuartzPlay is a read-only dependency source; its implementation may change independently, so cross-service claims need source paths and verification dates.
- Existing code contains contradictory maturity signals (for example, QuartzPlay UI features with mock or partial backend support). The feature catalog must distinguish UI presence from end-to-end availability.
- IAQP's schema is referenced by SQL but not represented by tracked migrations in this repository; database diagrams and persistence claims may remain incomplete until schema evidence is added.
- Endpoint names and deployment hostnames are implementation evidence, not proof of current production topology. Avoid converting them into operational guarantees.
- A local HTML file can drift from committed memory. The delivered guide records source revision/date metadata and remains outside both repositories.
- Documentation may accidentally expose secrets through copied environment examples, `.env` files, service keys, or connection strings. Inspect names and behavior only; never reproduce values.
- The single documentation PR exceeds the default review budget; its approved `exception-ok` / `size-exception` decision records this intentional exception.

## Ready for Proposal

Yes. Exploration establishes the IAQP primary-repo boundary, QuartzPlay read-only dependency boundary, delivered portable OpenSpec memory, delivered six-page sibling local guide, and approved single-PR exception. The PR preserves the no-HTML/no-QuartzPlay/no-implementation scope.

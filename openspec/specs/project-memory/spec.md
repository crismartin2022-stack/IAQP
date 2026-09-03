# IAQP Project Memory

> **Authority:** This committed OpenSpec document is the source of truth for project memory. The local HTML guide is a derived, unversioned reading aid and must be regenerated only after this document is reviewed.

## 1. Takeover Quick Path and Boundary Rule

### Start Here

1. Read the safety invariants in [section 7](#7-safety-invariants-and-verification-playbook).
2. Trace a change through the IAQP module map in [section 4](#4-iaqp-architecture-and-persistence).
3. Check the relevant `CT-###` contract and `JR-###` journey before crossing into QuartzPlay.
4. Refresh affected evidence records before relying on this document for an operational decision.

**Boundary rule:** IAQP owns roulette operation and its service persistence; QuartzPlay owns player wallet balances. QuartzPlay citations are read-only evidence, not IAQP implementation commitments. [EV-IAQP-001] [EV-QP-001]

### Memory Metadata

| Field | Value |
|---|---|
| IAQP revision | `a9f47cc7fc24fce5246e0be55318e245e8351fa2` |
| QuartzPlay revision | `7637a35f4e1452aa1a946997832e7ce8cdc9c254` |
| Evidence verified on | 2026-09-02 |
| IAQP accountable owner | `OQ-001` — not evidenced in repository |
| QuartzPlay accountable owner | `OQ-002` — not evidenced in repository |
| Evidence scope | Checked-in source and configuration only; no live environment inspection |

### Status Legend

| Status | Meaning | Use |
|---|---|---|
| `verified` | Directly supported by cited checked-in source/configuration. | Safe to state as repository evidence. |
| `assumption` | Plausible interpretation lacking enough proof. | Must not become an operational guarantee. |
| `open` | Missing, contradictory, or owner-confirmation-required evidence. | Resolve through named evidence before action. |

## 2. System, Repository, and Deployment Maps

### System Map

```text
QuartzPlay frontend / player surface
        │ observed casino API destination
        ▼
IAQP FastAPI ──► IAQP PostgreSQL/Supabase-configured persistence
        │
        │ service-to-service wallet requests
        ▼
QuartzPlay wallet API ──► QuartzPlay balance authority
```

| Component | Responsibility | Owner | Evidence |
|---|---|---|---|
| IAQP API | Live roulette state, bets, chat, public round verification. | IAQP | [EV-IAQP-001] |
| IAQP game core | Deterministic RNG, European roulette validation and settlement. | IAQP | [EV-IAQP-002] [EV-IAQP-003] |
| IAQP persistence | Round, seed, bet, and pending-payment records named in SQL. Schema provisioning is not reproducible from this repository. | IAQP | [EV-IAQP-004] [OQ-005] |
| QuartzPlay wallet API | Balance reads, debits, and credits called by IAQP. | QuartzPlay | [EV-IAQP-005] [EV-QP-001] |
| QuartzPlay frontend | React entry routes; casino surface has a distinct IAQP destination. | QuartzPlay | [EV-QP-002] |
| QuartzPlay backend/bot | Authentication, persistence, agency/admin and bot surfaces. | QuartzPlay | [EV-QP-003] [EV-QP-004] [EV-QP-005] |

### Repository Map

| Repository | Area | Notes | Evidence |
|---|---|---|---|
| `IAQP` | `main.py` | FastAPI lifecycle, routes, CORS, chat, verification endpoint. | [EV-IAQP-001] |
| `IAQP` | `rng.py`, `ruleta.py` | Pure deterministic game core; no database, network, clock, or LLM dependency in roulette rules. | [EV-IAQP-002] [EV-IAQP-003] |
| `IAQP` | `mesa.py`, `ciclo.py` | Round state machine, live loop, seed rotation, persistence and payment ordering. | [EV-IAQP-004] |
| `IAQP` | `billetera.py` | QuartzPlay wallet client, deterministic references, retry records. | [EV-IAQP-005] |
| `IAQP` | `crupier.py` | Pre-recorded narration, public-state chat filter, responsible-gaming interruption. | [EV-IAQP-006] |
| `IAQP` | `requirements.txt`, `runtime.txt`, `Procfile`, `supabase/config.toml`, `pruebas.py` | Declared stack, local tooling declarations, start command, manual evidence. | [EV-IAQP-007] [EV-IAQP-008] |
| `app` (QuartzPlay) | `bot/` | Read-only backend/bot evidence. | [EV-QP-001] [EV-QP-003] [EV-QP-004] |
| `app` (QuartzPlay) | `frontend/` | Read-only React route and API-destination evidence. | [EV-QP-002] [EV-QP-005] |

### Deployment Map

| Claim | Status | Limitations | Evidence |
|---|---|---|---|
| IAQP declares Python 3.11 and starts Uvicorn with `$PORT`. | `verified` | This is a repository declaration, not proof of a running deployment. | [EV-IAQP-007] |
| IAQP has local Supabase CLI configuration. | `verified` | Configuration does not prove remote bindings, deployed schema, network policy, or live auth behavior. | [EV-IAQP-008] [OQ-005] |
| QuartzPlay frontend contains `api.iaqp.lat` and a casino API destination. | `verified` | Source URL is not proof of current DNS, routing, health, TLS, or production topology. | [EV-QP-002] [OQ-006] |

## 3. Ownership and Cross-Service Contracts

### Ownership Matrix

| Domain | Owner | Rule | Evidence |
|---|---|---|---|
| Player wallet balances | QuartzPlay | IAQP MUST NOT be treated as a balance store. | [EV-IAQP-005] [EV-QP-001] |
| Roulette result, rules, and round state | IAQP | Draw and settlement are IAQP responsibilities. | [EV-IAQP-002] [EV-IAQP-003] [EV-IAQP-004] |
| IAQP operational records | IAQP | Source names IAQP seed, round, bet, and movement tables; schema provisioning remains open. | [EV-IAQP-004] [OQ-005] |
| QuartzPlay authentication, player/account, agency/admin, and bot capabilities | QuartzPlay | IAQP documents them only as read-only dependency context. | [EV-QP-003] [EV-QP-004] [EV-QP-005] |

### Contracts

#### CT-001 — Balance Lookup

| Field | Value |
|---|---|
| Caller → provider | IAQP → QuartzPlay |
| Purpose | Retrieve a player's balance in cents. |
| Request / response | `jugador_id` → `saldo_centavos`. |
| Data owner | QuartzPlay owns balance. IAQP receives a response value only. |
| Authentication evidence | IAQP sends `X-Service-Key`; QuartzPlay-side validation is evidenced. Do not record value. |
| Failure | Missing configuration or `4xx` is definitive; network/other failures retry three attempts then raise wallet error. |
| Retry / idempotency | Lookup has no IAQP idempotency record evidenced. |
| Exit state | Caller receives balance or an `ErrorBilletera`. |
| Evidence | [EV-IAQP-005] [EV-QP-001] |

#### CT-002 — Bet Debit

| Field | Value |
|---|---|
| Caller → provider | IAQP → QuartzPlay |
| Purpose | Fund an accepted IAQP roulette bet before it reaches the table. |
| Request / response | Player, amount in cents, deterministic reference, table, game → post-debit balance. |
| Data owner | QuartzPlay owns balance; IAQP owns accepted in-memory bet and its named IAQP persistence record. |
| Authentication evidence | Service-key header evidence as in `CT-001`; no end-user auth guarantee is inferred. |
| Failure | Wallet failure rejects bet; IAQP does not add it to the round. |
| Retry / idempotency | IAQP checks duplicate reference before debit. References derive from round, player, and bet index; QuartzPlay wallet behavior must preserve duplicate safety for the documented retry model. |
| Exit state | Accepted bet has a balance response and is recorded; rejected bet is absent from the round. |
| Evidence | [EV-IAQP-004] [EV-IAQP-005] [EV-QP-001] |

#### CT-003 — Prize Credit

| Field | Value |
|---|---|
| Caller → provider | IAQP → QuartzPlay |
| Purpose | Credit aggregate settlement returns after a resolved round. |
| Request / response | Player, amount, deterministic prize reference, table/game metadata → post-credit balance. |
| Data owner | QuartzPlay owns balance; IAQP owns settlement and pending-movement audit record. |
| Authentication evidence | Service-key header evidence as in `CT-001`. |
| Failure | Resolved result is not reversed. IAQP records failed payment and scheduled retry handling can later mark it confirmed or blocked. |
| Retry / idempotency | Reference derives from round and player; pending records are retried. QuartzPlay duplicate response semantics are implementation evidence referenced by IAQP comments, not independently tested here. |
| Exit state | Confirmed external credit, or IAQP `fallido`/`trabado` movement requiring operation. |
| Evidence | [EV-IAQP-004] [EV-IAQP-005] [EV-QP-001] |

#### CT-004 — Round Refund Credit

| Field | Value |
|---|---|
| Caller → provider | IAQP → QuartzPlay |
| Purpose | Return funds for an annulled round. |
| Request / response | Player, amount, deterministic refund reference, `devolucion=true` → post-credit balance. |
| Data owner | Same as `CT-003`. |
| Authentication evidence | Service-key header evidence as in `CT-001`. |
| Failure | Uses same pending-record path as prize credit. Exact invoking path for `Mesa.anular()` requires integration confirmation. |
| Retry / idempotency | Deterministic refund reference supports safe retry expectation. |
| Exit state | Confirmed refund or an actionable pending/blocked movement. |
| Evidence | [EV-IAQP-004] [EV-IAQP-005] [OQ-004] |

## 4. IAQP Architecture and Persistence

### Module Responsibilities

| Module | Responsibility | Key constraints | Evidence |
|---|---|---|---|
| `rng.py` | Server seed commitment, HMAC-SHA256 stream, rejection sampling, reproduction. | No adjustable house-edge control. | [EV-IAQP-002] |
| `ruleta.py` | European single-zero rules, validation, result and payout settlement. | Pure module; theoretical RTP is `36/37`. | [EV-IAQP-003] |
| `mesa.py` | Session/seed lifetime and round state transitions. | `ABIERTA → CERRADA → RESUELTA`; resolver rejects an open round. | [EV-IAQP-004] |
| `ciclo.py` | Live-table loop, database records, payment sequence, retry-visible failures. | Closes before resolving; narrates after result. | [EV-IAQP-004] |
| `billetera.py` | QuartzPlay wallet client. | Debits before accepted bet; deterministic refs; no local balance. | [EV-IAQP-005] |
| `crupier.py` | Audio scripts, chat request builder, risk response. | Chat gets filtered public state only; risky language bypasses model. | [EV-IAQP-006] |
| `main.py` | App lifecycle and HTTP API. | Starts fixed tables and retry loop; exposes verification endpoint. | [EV-IAQP-001] |

### Round and Payment Flow

```text
open round + publish seed hash
  → validate request and duplicate reference
  → CT-002 debit succeeds
  → accept and persist bet
  → close round
  → deterministic draw and settlement
  → persist result
  → narrate public result
  → CT-003 credits, recording failures for retry
```

The documented ordering is source-backed behavior, not a claim of transactionality across services. In particular, a database write failure is logged and the loop continues; a payout failure does not reverse an already-resolved result. [EV-IAQP-004] [EV-IAQP-005]

### Persistence Boundaries

| Record / concern | Evidence | Status |
|---|---|---|
| Seeds, rounds, bets, and movements | SQL in `ciclo.py` and `billetera.py` names `iaqp_semillas`, `iaqp_rondas`, `iaqp_apuestas`, `iaqp_movimientos`. | `verified` |
| IAQP balance storage | No balance table or local balance handling evidenced; wallet client declares external authority. | `verified` |
| Repeatable IAQP schema provisioning | Supabase config enables migrations but lists no schema paths; no tracked SQL migrations found in IAQP source inventory. | `open` — [OQ-005] |

## 5. Actor Journeys and Failure Exits

### JR-001 — Player Places Roulette Bet

| Field | Value |
|---|---|
| Actor / entry | Player via IAQP `POST /api/mesa/{mesa_id}/apostar`. |
| Preconditions | Existing live table, open round, player identifier, valid roulette bet, configured wallet path. |
| Steps | 1. **IAQP:** validates table, player and bet. 2. **IAQP → QuartzPlay (`CT-002`):** requests debit. 3. **IAQP:** accepts bet only after debit and attempts IAQP bet persistence. |
| Happy path | Return accepted status, post-debit balance and table bet count. |
| Failure path | Invalid/missing table or bet returns 4xx; definitive wallet error returns 400; transient wallet error returns 503; failed debit means no table entry. |
| Data owner | QuartzPlay balance; IAQP round/bet record. |
| Exit state | Funded accepted bet or explicitly rejected request. |
| Evidence | [EV-IAQP-001] [EV-IAQP-004] [EV-IAQP-005] |

### JR-002 — IAQP Resolves and Pays a Round

| Field | Value |
|---|---|
| Actor / entry | IAQP live-table loop. |
| Preconditions | Open round window expires; table loop and database pool are active. |
| Steps | 1. **IAQP:** closes round. 2. **IAQP:** draws and settles. 3. **IAQP:** records result, then emits narration. 4. **IAQP → QuartzPlay (`CT-003`):** aggregates per-player credits. |
| Happy path | Resolved round has settlement and confirmed payment records. |
| Failure path | Result persistence failure logs an error; payment failure remains actionable and retryable, not a rollback of result. |
| Data owner | IAQP result/audit records; QuartzPlay balances. |
| Exit state | Resolved outcome with confirmed or pending payment follow-up. |
| Evidence | [EV-IAQP-004] [EV-IAQP-005] |

### JR-003 — Player Verifies a Completed Round

| Field | Value |
|---|---|
| Actor / entry | Player via IAQP `GET /api/verificar/{ronda_id}`. |
| Preconditions | Persisted round and associated seed record exist. |
| Steps | **IAQP:** returns public round data, published hash, client seed and nonce; returns server seed only after reveal. |
| Happy path | Reader recomputes hash and HMAC/rejection-sampling result after seed reveal. |
| Failure path | Unknown round returns 404; active seed remains withheld and response says future reveal is required. |
| Data owner | IAQP round/seed audit data. |
| Exit state | Verifiable disclosed round, or incomplete-but-safe active-seed response. |
| Evidence | [EV-IAQP-001] [EV-IAQP-002] [EV-IAQP-004] |

### JR-004 — Player Uses QuartzPlay Casino Surface

| Field | Value |
|---|---|
| Actor / entry | Player at QuartzPlay frontend `/casino` or IAQP-branded host route. |
| Preconditions | Frontend routing and destination configuration are deployed; end-to-end auth/session conditions are not confirmed here. |
| Steps | **QuartzPlay:** selects `Casino` component. **QuartzPlay → IAQP:** frontend source contains casino API destination. |
| Happy path | `partial` — route and destination are source-evidenced, but runtime integration is not exercised. |
| Failure path | `OQ-007` — no end-to-end error behavior validated. |
| Data owner | QuartzPlay frontend/account context; IAQP game state; QuartzPlay balances through contracts. |
| Exit state | `partial` observed integration; no production guarantee. |
| Evidence | [EV-QP-002] [OQ-007] |

### JR-005 — Agency or Admin Uses QuartzPlay Operations

| Field | Value |
|---|---|
| Actor / entry | Agency/admin through QuartzPlay `/agencia` or `/admin` route. |
| Preconditions | QuartzPlay credentials/session or admin key are valid. |
| Steps | **QuartzPlay:** route selection; backend has agency bearer-session and admin-key checks plus operational endpoints. |
| Happy path | `partial` — source has route and protected backend operations. |
| Failure path | Missing/expired session or absent/invalid admin key returns authentication/authorization error in observed code. |
| Data owner | QuartzPlay. |
| Exit state | QuartzPlay operation outcome; no IAQP state change is implied. |
| Evidence | [EV-QP-003] [EV-QP-005] |

### JR-006 — Responsible-Gaming Chat Interruption

| Field | Value |
|---|---|
| Actor / entry | Player sends IAQP table chat message. |
| Preconditions | Existing IAQP table; non-empty message. |
| Steps | **IAQP:** checks risk patterns before external model call. If matched, returns fixed assistance response; otherwise builds a public-state-only model request. |
| Happy path | Risk signal avoids model invocation and returns assistance response. |
| Failure path | Missing model configuration returns explicit unconfigured result; model/service error returns 503. |
| Data owner | IAQP chat buffer and public table state; no hidden seed is passed to model. |
| Exit state | Assistance response, model response, unconfigured response, or 503. |
| Evidence | [EV-IAQP-001] [EV-IAQP-006] |

## 6. Feature/Maturity Catalog and Stack Rationale

### Feature Maturity

| Feature | Owner | Entry / backing source | Maturity | Limitation |
|---|---|---|---|---|
| Live European roulette | IAQP | IAQP API, `mesa.py`, `ciclo.py`, `ruleta.py` | `verified` | Runtime health and schema are not tested here. |
| Provably-fair verification | IAQP | `/api/verificar/{ronda_id}`, `rng.py` | `verified` | Depends on persisted records and seed rotation. |
| Wallet debit/credit integration | Cross-service | `billetera.py`, QuartzPlay wallet handler evidence | `verified` contract shape | Live interoperability and owner acceptance remain untested. |
| Dealer narration and chat safety | IAQP | `crupier.py`, `main.py` | `verified` | External model availability depends on configuration. |
| QuartzPlay casino frontend route | QuartzPlay | `frontend/src/index.js` and casino source references | `partial` | No end-to-end browser/runtime verification. |
| QuartzPlay agency/admin operations | QuartzPlay | Frontend routes and `casino_api.py`/`auth.py` | `partial` | Read-only evidence; implementation can change independently. |
| Reproducible IAQP schema provisioning | IAQP | Supabase config and IAQP SQL references | `planned/open` | No tracked migration source found. |

### Stack Rationale

| Technology | Observed use | Rationale supported by source | Evidence |
|---|---|---|---|
| Python 3.11 | IAQP runtime declaration. | Service runtime. | [EV-IAQP-007] |
| FastAPI | IAQP HTTP lifecycle and routes. | Async API surface. | [EV-IAQP-001] [EV-IAQP-007] |
| asyncpg / PostgreSQL | IAQP connection pool and SQL records. | Async persistence access. | [EV-IAQP-001] [EV-IAQP-004] |
| httpx | IAQP wallet and chat HTTP calls. | Async external API calls. | [EV-IAQP-001] [EV-IAQP-005] |
| HMAC-SHA256 + rejection sampling | IAQP RNG. | Reproducible uniform draw approach. | [EV-IAQP-002] |
| React 18 / CRA | QuartzPlay frontend package and entry. | Frontend routing and screens. | [EV-QP-002] [EV-QP-005] |
| Telegram bot | QuartzPlay server. | Bot handler lifecycle. | [EV-QP-004] |

## 7. Safety Invariants and Verification Playbook

### Non-Negotiable Invariants

| Invariant | Requirement | Evidence |
|---|---|---|
| Draw timing | A roulette draw MUST occur only after betting closes. | [EV-IAQP-004] |
| Seed isolation | Active server seed MUST NOT enter IAQP public state or public verification output before rotation/reveal. | [EV-IAQP-001] [EV-IAQP-004] |
| Dealer isolation | Dealer/model input MUST contain public state only and MUST NOT decide outcomes. | [EV-IAQP-004] [EV-IAQP-006] |
| No configured edge | IAQP MUST NOT add a configurable house-edge control; rules and payout table determine theoretical RTP. | [EV-IAQP-002] [EV-IAQP-003] |
| Wallet authority | IAQP MUST NOT become balance authority; it requests QuartzPlay debit/credit operations. | [EV-IAQP-005] [EV-QP-001] |
| No outcome rollback | A failed prize credit MUST remain an actionable payment failure, not reverse a resolved result. | [EV-IAQP-004] [EV-IAQP-005] |

### Verification Playbook

| Check | Command / method | What it proves | Limitation |
|---|---|---|---|
| Syntax | `python3 -m compileall -q .` | Python files compile in current environment. | Does not run service or contracts. |
| Manual RNG evidence | `python3 pruebas.py` | Prints deterministic, uniformity, RTP, and rules evidence. | Script prints results; it is not a test framework with assertions/coverage. |
| Documentation structure | Check required sections, IDs, fields, links, and safety citations. | Memory completeness and traceability. | Does not verify live system. |
| Diff hygiene | `git diff --check`; inspect changed paths and secret patterns. | Whitespace, approved-scope, and obvious secret-copy review. | Cannot prove absence of every sensitive inference. |
| Cross-service refresh | Record both revisions, inspect cited sources, obtain owner review. | Evidence freshness before operational decisions. | Requires human/system access outside repository. |

## 8. Evidence Register and Open Questions

### Evidence Register

| ID | Status | Repository / owner | Source | Revision / date | Confidence | Claim and limitation | Linked IDs |
|---|---|---|---|---|---|---|---|
| EV-IAQP-001 | verified | IAQP | `main.py` routes, lifespan, chat and verification | `a9f47cc`, 2026-09-02 | High | IAQP exposes live-table, bet, chat and verification APIs. No live endpoint was called. | CT-002, JR-001, JR-003, JR-006 |
| EV-IAQP-002 | verified | IAQP | `rng.py` | `a9f47cc`, 2026-09-02 | High | Seed commitment, HMAC-SHA256 and rejection sampling are source-evidenced. | JR-003 |
| EV-IAQP-003 | verified | IAQP | `ruleta.py` | `a9f47cc`, 2026-09-02 | High | European single-zero validation/settlement and `36/37` theoretical RTP are source-evidenced. | JR-001 |
| EV-IAQP-004 | verified | IAQP | `mesa.py`, `ciclo.py` | `a9f47cc`, 2026-09-02 | High | State order, seed rotation, persistence SQL and live-cycle ordering are source-evidenced. Schema presence is not. | CT-002, CT-003, CT-004, JR-001, JR-002 |
| EV-IAQP-005 | verified | IAQP | `billetera.py` | `a9f47cc`, 2026-09-02 | High | IAQP calls external wallet endpoints with service key, retries and deterministic refs. External behavior not live-tested. | CT-001, CT-002, CT-003, CT-004 |
| EV-IAQP-006 | verified | IAQP | `crupier.py` | `a9f47cc`, 2026-09-02 | High | Chat input filter and responsible-gaming bypass are source-evidenced. | JR-006 |
| EV-IAQP-007 | verified | IAQP | `requirements.txt`, `runtime.txt`, `Procfile` | `a9f47cc`, 2026-09-02 | High | Declared Python/runtime dependencies and Uvicorn start command. Not production proof. | OQ-006 |
| EV-IAQP-008 | verified | IAQP | `supabase/config.toml`, `pruebas.py` | `a9f47cc`, 2026-09-02 | Medium | Local Supabase config and manual statistical evidence script exist. No tracked IAQP migrations found. | OQ-005 |
| EV-QP-001 | verified | QuartzPlay (read-only) | `bot/casino_api.py` wallet handlers | `7637a35f`, 2026-09-02 | Medium | QuartzPlay contains service-key-guarded balance/debit/credit handlers. No live contract test. | CT-001, CT-002, CT-003, CT-004 |
| EV-QP-002 | verified | QuartzPlay (read-only) | `frontend/src/index.js`, frontend source API references | `7637a35f`, 2026-09-02 | Medium | React route selection includes casino and source references distinguish API destinations. No deployed route proof. | JR-004, OQ-006 |
| EV-QP-003 | verified | QuartzPlay (read-only) | `bot/casino_api.py`, `bot/auth.py` | `7637a35f`, 2026-09-02 | Medium | Agency sessions and admin-key protections are in source. No security audit or runtime verification. | JR-005 |
| EV-QP-004 | verified | QuartzPlay (read-only) | `bot/db.py`, `bot/server.py` | `7637a35f`, 2026-09-02 | Medium | Bot startup and independently owned persistence are source-evidenced. Schema may not reflect current deployed state. | OQ-002 |
| EV-QP-005 | verified | QuartzPlay (read-only) | `frontend/package.json`, `frontend/src/index.js` | `7637a35f`, 2026-09-02 | High | React 18/CRA declaration and route entry are source-evidenced. | JR-004, JR-005 |

### Open Questions

| ID | Status | Owner needed | Question | Required resolution evidence | Linked IDs |
|---|---|---|---|---|---|
| OQ-001 | open | IAQP maintainer | Who owns IAQP operations, incident response, and documentation approval? | Named owner in versioned repository governance or owner confirmation. | All IAQP evidence |
| OQ-002 | open | QuartzPlay maintainer | Who accepts review of QuartzPlay-side wallet and account contracts? | Named owner confirmation and contract review record. | EV-QP-001 to EV-QP-004 |
| OQ-003 | open | QuartzPlay maintainer | What authenticated caller identity and authorization rules apply beyond service-key presence? | QuartzPlay contract tests/configuration and owner review, without copying secret values. | CT-001 to CT-004 |
| OQ-004 | open | IAQP maintainer | Which production path invokes round annulment/refund and what compensations precede it? | Exercised integration evidence or source path invoking `Mesa.anular()`. | CT-004 |
| OQ-005 | open | IAQP maintainer | What tracked source provisions IAQP tables and binds current database deployment? | Versioned migrations/schema plus environment-independent provisioning instructions. | EV-IAQP-004, EV-IAQP-008 |
| OQ-006 | open | IAQP and QuartzPlay maintainers | Which hosts, routes, CORS origins, and deployment bindings are current? | Environment-reviewed deployment evidence; source URLs alone do not resolve this. | EV-IAQP-007, EV-QP-002 |
| OQ-007 | open | QuartzPlay maintainer | Does casino frontend behavior complete successfully with IAQP in current environments? | End-to-end test or owner-reviewed runtime evidence. | JR-004 |

## 9. Local-Guide Handoff Contract

### Derived Artifact Boundary

| Requirement | Contract |
|---|---|
| Location | `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` — sibling to `IAQP/` and `app/`. |
| Authority | This Markdown remains authoritative; HTML is derived presentation only. |
| Inputs | Reviewed current `project-memory/spec.md`, IAQP revision, QuartzPlay revision, generation date. |
| Delivered local teaching guide | Exists externally at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` as six task-oriented pages: `index.html` (start takeover), `system-and-business.html` (understand business), `journeys.html` (follow journeys), `features-and-stack.html` (assess features), `architecture-and-operations.html` (change safely), and `evidence-and-unknowns.html` (verify claims). It is local-only and excluded from Git and this PR. Shared local stylesheet: `assets/guide.css`. |
| Navigation | Shared keyboard-accessible navigation, relative links, breadcrumbs, status legend, freshness banner, and no remote dependencies. |
| Freshness | HTML is fresh only when embedded source revisions and generation date correspond to reviewed Markdown. |
| Unknowns | Open questions remain visible as amber TBD markers; they must not be hidden or converted into claims. |
| PR exclusion | Never add, stage, commit, or include generated HTML/assets in IAQP review. |
| Refresh protocol | Capture both revisions/date; inspect changed evidence; update this Markdown; validate; obtain owner review; then regenerate HTML. |

### Documentation Rollback

For an unmerged documentation change, remove the OpenSpec artifacts. For a merged documentation-only change, revert the documentation commit. This memory does not authorize runtime, wallet, deployment, QuartzPlay, cloud-setting, or secret changes.

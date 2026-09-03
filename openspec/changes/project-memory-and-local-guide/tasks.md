# Tasks: Project Memory and Local Guide Handoff

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Actual staged OpenSpec size | 873 insertions; local HTML excluded |
| 400-line budget risk | High |
| Chained PRs recommended | No |
| Suggested split | One approved documentation-only IAQP PR; delivered local guide is external |
| Delivery strategy | exception-ok |
| Chain strategy | size-exception |

Decision needed before apply: No; approved single PR
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

### Delivery Record
- Staged OpenSpec scope: 9 files, 873 insertions.
- Included path: `openspec/` only.

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | Complete canonical IAQP memory and handoff contract | PR 1 | Single IAQP documentation-only PR; accepted size exception |
| 2 | Record delivered local teaching guide boundary | PR 1 | Six-page guide is external, local-only, and excluded from Git and the PR |

## Phase 1: Canonical Memory and Traceability

- [x] 1.1 Update `openspec/specs/project-memory/spec.md` with evidence-backed system behavior, repository/deployment boundaries, ownership, contracts, safety invariants, and verification limits.
- [x] 1.2 Add product-owner business logic: roulette purpose, wallet authority, payment ordering, responsible-gaming behavior, and explicit non-guarantees; link each claim to `EV-`, `CT-`, `JR-`, or `OQ-` records.
- [x] 1.3 Add takeover journeys and feature catalog with purpose, owner, entry, maturity, limitation, and IAQP/QuartzPlay service-tagged steps; keep partial or unsupported QuartzPlay behavior non-verified.
- [x] 1.4 Add concise stack rationale and preserve stable evidence, contract, journey, and open-question identifiers for downstream guide links.

## Phase 2: Delivered Local Guide Handoff

- [x] 2.1 Deliver the six-page sibling guide at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` as an intentional summary/paraphrase, not a field-by-field copy; every topic links to its canonical section or stable ID.
- [x] 2.2 Specify navigable pages for system behavior, business logic, journeys, feature purpose/maturity, IAQP/QuartzPlay relationship, and stack rationale, using local SVG/CSS diagrams only where they improve teaching.
- [x] 2.3 Record offline, keyboard-usable navigation, local links/graphics, source revisions, generation date, visible unknowns, and no remote dependencies or secrets; guide remains outside Git and this PR.

## Phase 3: Validation and Delivery

- [x] 3.1 Validate required sections, unique IDs, complete contract/journey fields, traceable claims, local-link/graphic references, heading/navigation usability, and preserved unknowns.
- [x] 3.2 Run `git diff --check`; inspect secret patterns and changed paths; prove IAQP diff excludes HTML, generators, local output, and `/Users/usuario/Documents/Trabajo 2026/iaqp/app`.
- [x] 3.3 Prepare one approved documentation-only IAQP PR with source revisions, limitations, rollback, `exception-ok` / `size-exception` decision, 873 staged insertions, and explicit local HTML exclusion; do not commit, push, or open it.

## Subsequent QuartzPlay Work (Not This Change)

- [ ] QP.1 Separately validate QuartzPlay authentication, wallet, persistence, deployment, and UI maturity evidence with QuartzPlay ownership review.
- [ ] QP.2 Create QuartzPlay documentation or implementation only in `/Users/usuario/Documents/Trabajo 2026/iaqp/app` through its separate approval flow; do not modify it here.

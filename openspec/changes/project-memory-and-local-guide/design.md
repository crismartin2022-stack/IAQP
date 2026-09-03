# Design: Project Memory and Local Guide Handoff

## Technical Approach

Keep `openspec/specs/project-memory/spec.md` complete, versioned, and authoritative. Delivered sibling HTML guide at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` teaches IAQP takeover through task-oriented summaries and diagrams; it does not mirror canonical fields or replace audit detail. QuartzPlay remains read-only evidence, never an IAQP commitment.

Canonical OpenSpec retains system/repository/deployment maps, ownership, complete contracts and journeys, architecture, maturity, safety, verification, evidence records, and open questions. Guide content selects and paraphrases this material, then provides an explicit route back to it.

## Local Guide Information Architecture

Delivered location: `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/`. It contains six HTML pages, remains local-only, and is excluded from Git and the IAQP PR.

| Page | Reader question | Concise content |
|---|---|---|
| `index.html` | Where do I start? | Boundary rule, freshness, takeover route, safety stop-signs, visible unknowns. |
| `system-and-business.html` | What does system do and why? | Observed behavior, business rules, service ownership, payment ordering, non-guarantees. |
| `journeys.html` | How does work cross system? | Story-like player/operator journeys with entry, service-tagged steps, failure outcome, and final ownership. |
| `features-and-stack.html` | What exists and why this stack? | Feature purpose and maturity, known limits, brief technology rationale; no endpoint inventory dump. |
| `architecture-and-operations.html` | Where do I change or verify behavior? | IAQP module map, round/payment lifecycle, safety invariants, verification path, operational gaps. |
| `evidence-and-unknowns.html` | How do I verify claims? | Evidence-reading method, current open questions, and links to complete canonical registers rather than copied registers. |
| `assets/guide.css`, `assets/*.svg` | How is teaching presented? | Shared local styles and only diagrams that reduce explanation cost. |

Navigation is HTML-only: skip link, persistent primary navigation, `aria-current`, breadcrumbs, local contents, and previous/next links. Labels use reader tasks (“Follow a journey”), not schema. Mobile navigation wraps; every page remains reachable without JavaScript.

Each topic follows: **why it matters → concise explanation → diagram/example when useful → failure or limitation → canonical reference**. Status markers distinguish `verified`, `partial/assumption`, and `open`. Unknowns remain visible; prose never upgrades them into guarantees.

## Architecture Decisions

| Decision | Alternatives / tradeoff | Choice and rationale |
|---|---|---|
| Authority | HTML is approachable but unversioned and drift-prone. | OpenSpec is complete truth; guide is disposable presentation. |
| Organization | Field/page parity simplifies generation but makes poor teaching. | Organize around takeover questions and journeys; paraphrase intentionally. |
| Traceability | Copied audit tables duplicate truth. | Every topic shows canonical file + heading anchor and relevant `EV-`, `CT-`, `JR-`, or `OQ-` IDs. |
| Visuals | Remote libraries are convenient but break offline/privacy rules. | Use local SVG/CSS only, with text equivalents; no required animation or scripting. |
| Boundary | Repository-local ignored output can leak into review. | Keep HTML, generator, and assets outside both repositories and IAQP PRs. |

## Traceability and Refresh Flow

```text
IAQP + QuartzPlay read-only evidence
              ↓
reviewed canonical OpenSpec (complete records)
              ↓ select, paraphrase, cite
local teaching guide (orientation only)
```

Every topic carries a visible “Canonical source” locator such as `../../IAQP/openspec/specs/project-memory/spec.md#3-ownership-and-cross-service-contracts` plus stable IDs. Freshness records both repository revisions, canonical path, and generation date. Refresh order is evidence → OpenSpec review → guide regeneration → link/freshness check. Unsupported content is corrected, marked unknown, or removed.

## Visual, Accessibility, Offline, and Safety Constraints

- Use semantic landmarks, one `h1`, ordered headings, keyboard-visible focus, sufficient contrast, non-color status labels, and responsive/reflow-safe layouts.
- Give each SVG a nearby prose summary; use `<title>`/`<desc>` when informative and hide decorative graphics from assistive technology. Preserve meaning in print and without CSS.
- Use system fonts, relative links, local CSS/SVG, and no CDN, web font, analytics, remote image, iframe, fetch, or network dependency. JavaScript is unnecessary.
- Never copy `.env` content, tokens, service-key values, connection strings, credentials, private URLs, or inferred deployment topology. Environment-variable names may appear only when canonical memory requires them.

## File Changes

| File | Action | Description |
|---|---|---|
| `openspec/changes/project-memory-and-local-guide/design.md` | Modify | Refresh teaching-guide architecture and constraints. |
| `openspec/specs/project-memory/spec.md` | Modify during apply | Preserve complete canonical memory and revised handoff contract. |
| QuartzPlay and local guide paths | None in this change | Evidence remains read-only; HTML/generator/output remain separate. |

## Validation and Delivery

Validate canonical sections and stable IDs, topic-to-canonical locators, heading/navigation model, visible unknowns, and diagram text equivalents. Delivered HTML checks: offline open, keyboard traversal, reflow, no broken relative links, no network requests, matching revisions/date, and no secrets. IAQP checks: `git diff --check`, changed-path and secret-pattern review, and proof that HTML, generators, local output, and QuartzPlay are absent.

Delivery is one documentation-only IAQP PR under accepted `exception-ok` / `size-exception`; local HTML is excluded. No runtime/data migration. Rollback is removal before merge or documentation-commit revert after merge.

## Open Questions

- Who owns IAQP operations/document approval and QuartzPlay contract acceptance?
- What tracked evidence establishes IAQP schema provisioning and current deployment bindings?

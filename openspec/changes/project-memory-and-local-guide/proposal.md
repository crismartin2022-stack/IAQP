# Proposal: Project Memory and Local Guide Handoff

## Intent

Deliver evidence-based IAQP project memory for PR review and downstream Claude readers. Preserve IAQP/QuartzPlay ownership and contract traceability; deliver a six-page local-only HTML guide outside both repositories.

## Scope

### In Scope

- Add `project-memory` OpenSpec capability covering system map, evidence, ownership, integrations, architecture, journeys, maturity, stack, safety, verification, and open questions.
- Cite source paths, dates, confidence, and owners; separate verified evidence, assumptions, and open questions.
- Deliver the six-page local guide at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/`; it remains outside Git and this PR.
- Use one approved documentation-only PR under the `exception-ok` / `size-exception` decision; no split or chained PRs.

### Out of Scope

- IAQP runtime, API, database, deployment, or test changes.
- Local HTML, guide assets, generators, or other local documentation files in Git or this PR.
- QuartzPlay modification; it remains read-only evidence.
- Credentials, secrets, unverified topology, or endpoint guarantees.

## Capabilities

### New Capabilities

- `project-memory`: Portable, evidence-backed documentation of IAQP architecture, service boundaries, contracts, journeys, maturity, safety, and verification.

### Modified Capabilities

- None.

## Approach

Use committed OpenSpec Markdown as authoritative memory, built from IAQP source/configuration and read-only QuartzPlay evidence. Record ownership, data crossing, failure paths, idempotency, and exit states in concise tables and journeys. The six-page sibling local guide is delivered as a presentation artifact and excluded from Git and the approved single documentation PR.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `openspec/specs/project-memory/spec.md` | New | Delivered shared project memory. |
| `openspec/changes/project-memory-and-local-guide/` | Modified | Delivered SDD artifacts. |
| IAQP and QuartzPlay source paths | Read-only | Evidence only; no implementation edits. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Cross-service claims drift | Med | Cite paths, dates, confidence, and owner. |
| UI/backend maturity mismatch | Med | Mark verified, partial, or planned separately. |
| HTML drift or secret exposure | Med | Keep delivered guide external to Git/PR; exclude secrets; record freshness metadata. |

## Rollback Plan

Remove unmerged OpenSpec artifacts. No runtime, QuartzPlay, or local HTML rollback is needed because the guide is external to Git and the PR.

## Dependencies

- Read-only IAQP and QuartzPlay source evidence.
- Approved `exception-ok` / `size-exception` decision for the single documentation PR.

## Success Criteria

- [ ] `project-memory` traces claims to evidence and separates IAQP from QuartzPlay.
- [ ] Wallet authority, API boundaries, data crossing, failure/idempotency, safety, and open questions are explicit.
- [x] Six-page local HTML guide is delivered externally at the documented sibling path and absent from Git and this PR.
- [x] One approved documentation-only PR uses the `exception-ok` / `size-exception` decision.
- [ ] No implementation, QuartzPlay, secret, commit, push, or PR action occurs.

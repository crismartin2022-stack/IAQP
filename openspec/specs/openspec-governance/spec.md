# OpenSpec Governance Specification

## Purpose

Define where IAQP SDD change state lives and how OpenSpec records stay truthful.

No effect on draw timing, auditability, public-state isolation, wallet ownership, or idempotency: this specification governs project records only.

## Requirements

### Requirement: Canonical SDD State Location

IAQP SDD change state MUST live only in `IAQP/openspec`, committed on a branch that descends from the canonical integration branch `staging`. Secondary checkouts MUST NOT hold change trackers that diverge from the canonical location.

#### Scenario: Progress matches the canonical branch

- GIVEN a change whose `tasks.md` is committed on `staging`
- WHEN native SDD status runs in `IAQP/`
- THEN it reports the same task progress as `staging`

#### Scenario: Divergent copy in a secondary checkout

- GIVEN a secondary checkout holds a copy of a change that differs from the canonical copy
- WHEN consolidation runs
- THEN unique content is either merged into the canonical copy or explicitly discarded
- AND the secondary copy is removed with its checkout

#### Scenario: Planning artifacts never committed

- GIVEN proposal, design, or spec artifacts exist only as untracked files
- WHEN they are committed
- THEN their progress statements MUST first be corrected to match the canonical branch

### Requirement: No Partial Archive State

A change MUST be either active with all its artifacts in `openspec/changes/{change-name}/`, or archived under `openspec/changes/archive/YYYY-MM-DD-{change-name}/` with its verification evidence. A partial move MUST NOT be committed.

#### Scenario: Archive copy without verification evidence

- GIVEN an archive copy exists without a verify report and the originals are deleted
- WHEN consolidation runs
- THEN the originals are restored and the incomplete archive copy is removed

#### Scenario: Empty domain directory

- GIVEN a change `specs/` directory contains a domain folder without `spec.md`
- WHEN consolidation completes
- THEN no such empty domain folder remains

### Requirement: Records Match Attested Live State

OpenSpec records MUST describe remote staging resources only from sanitized, attested evidence, and MUST record divergence between records and live state.

#### Scenario: Live resource without record

- GIVEN a sanitized inventory shows a staging resource that records do not attest
- WHEN reconciliation runs
- THEN the record is annotated with dated inventory evidence
- AND no task is marked complete without its own acceptance evidence

#### Scenario: Sanitized evidence only

- GIVEN inventory evidence is recorded
- WHEN a reviewer reads it
- THEN it contains no identifiers, URLs, domains, keys, variable values, or rows

### Requirement: Consolidated Changes Pass Native Status

Every change touched by consolidation MUST report no native blockers when consolidation completes.

#### Scenario: Blocker cleared

- GIVEN a change reported `blocked(edit_authority_missing)` before consolidation
- WHEN consolidation completes
- THEN native status for that change reports no blocked reasons

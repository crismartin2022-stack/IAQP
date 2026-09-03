# Project Memory Specification

## Purpose

Provide complete, precise, evidence-based OpenSpec project memory for an IAQP takeover. Delivered local HTML guide is an approachable teaching aid, not a competing or field-by-field source of truth.

## Requirements

### Requirement: Evidence-backed Memory

Project memory MUST separate verified evidence, assumptions, and open questions. Every factual claim about a repository or service MUST record source path, verification date, confidence, and accountable owner. It MUST NOT contain credentials, secret values, or unverified production-topology guarantees.

#### Scenario: Verified claim is recorded

- GIVEN a claim supported by inspected source or configuration
- WHEN it is added to project memory
- THEN it includes source path, verification date, confidence, and owner
- AND it is marked as verified evidence

#### Scenario: Deployment fact lacks repository proof

- GIVEN a claimed hostname or deployment behavior has no verifiable source evidence
- WHEN project memory describes it
- THEN it is marked as an assumption or open question
- AND it is not presented as a guarantee

### Requirement: Service Boundary and Ownership

Project memory MUST identify IAQP and QuartzPlay as separate services and MUST state their ownership boundaries. It MUST identify QuartzPlay as sole wallet-balance authority and IAQP persistence as IAQP-owned. QuartzPlay evidence MUST be read-only and MUST NOT be represented as an IAQP implementation commitment.

#### Scenario: Wallet authority is documented

- GIVEN a reader reviews a wallet-related flow
- WHEN they consult project memory
- THEN QuartzPlay is named as balance authority
- AND IAQP is not described as storing user balances

#### Scenario: QuartzPlay feature has partial evidence

- GIVEN a QuartzPlay UI feature lacks confirmed end-to-end support
- WHEN it appears in a catalog or journey
- THEN its owner remains QuartzPlay
- AND its maturity is marked partial or planned, not verified

### Requirement: Cross-service Contract Traceability

Project memory MUST trace each IAQP/QuartzPlay contract to evidence and state direction of data crossing, ownership, authentication evidence, failure path, idempotency behavior, and exit state. Missing contract evidence MUST become an open question.

#### Scenario: Documented payment contract

- GIVEN a payment or refund interaction has source evidence
- WHEN its contract is recorded
- THEN request direction, data ownership, failure behavior, idempotency reference, and exit state are identified
- AND each claim links to its evidence record

#### Scenario: Authentication behavior is unknown

- GIVEN contract evidence does not establish an authentication mode
- WHEN the contract is recorded
- THEN authentication is an open question
- AND no authentication guarantee is asserted

### Requirement: IAQP Safety and Verification Memory

Project memory MUST preserve IAQP safety invariants: draws occur after betting closes, active server seeds are not public before rotation, dealer narration uses public state only, and IAQP has no configurable house edge. It MUST identify available verification evidence and limitations.

#### Scenario: Safety review

- GIVEN a developer reviews roulette operation
- WHEN they consult project memory
- THEN draw timing, seed isolation, dealer isolation, and house-edge rule are explicit
- AND each invariant is traceable to evidence

#### Scenario: Test coverage is unavailable

- GIVEN no automated test framework is configured
- WHEN verification is documented
- THEN manual evidence and syntax checks are distinguished from automated coverage
- AND the coverage gap is recorded

### Requirement: Takeover-oriented Navigation

Project memory MUST give a developer a navigable system map, repository map, architecture summary, journeys, feature-maturity catalog, stack rationale, safety rules, verification guidance, evidence register, and open questions. Journeys MUST state actor, entry point, preconditions, happy path, failure path, data owner, and exit state.

#### Scenario: Developer follows a cross-service journey

- GIVEN a developer investigates a player flow crossing services
- WHEN they select its journey
- THEN all required journey fields are available
- AND service-owned steps are visibly distinguished

#### Scenario: Unknown schema provisioning

- GIVEN schema provisioning lacks tracked migration evidence
- WHEN persistence is described
- THEN the gap appears in open questions
- AND project memory does not claim reproducible provisioning

### Requirement: Local-only HTML Handoff

The delivered six-page local HTML guide at `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` MUST derive from reviewed canonical OpenSpec project memory and MUST remain outside both IAQP and QuartzPlay repositories. Canonical OpenSpec memory MUST remain complete and precise; the guide MUST intentionally summarize or paraphrase rather than reproduce every field, table, identifier, or evidence record. Each guide topic MUST identify its canonical OpenSpec section or stable evidence/journey/contract identifier so a reader can trace detail back to the source of truth.

The guide MUST orient a taking-over developer to observed system behavior, product-owner-described business logic, user journeys, feature purpose and maturity, cross-service relationships, and brief stack rationale. It MAY use local SVG or CSS diagrams/graphics where they improve comprehension. It MUST work offline, use no remote dependencies, contain no secrets, display source revisions and generation date, preserve unknowns as unknowns, and be excluded from IAQP pull requests. This change MUST NOT add HTML, generator files, or local documentation output to IAQP.

#### Scenario: Delivered teaching guide is traced to canonical memory

- GIVEN reviewed project memory and delivered guide are available
- WHEN a reader uses the guide
- THEN its location is `/Users/usuario/Documents/Trabajo 2026/iaqp/local-docs/project-memory-and-local-guide/` outside both repositories
- AND it teaches takeover topics with links or identifiers back to canonical OpenSpec sections

#### Scenario: Guide intentionally summarizes a detailed contract

- GIVEN canonical OpenSpec records a contract with all required audit fields
- WHEN the guide explains that contract to a taking-over developer
- THEN it MAY use a concise explanation or local diagram instead of copying every field
- AND it identifies where the complete canonical contract can be read

#### Scenario: Guide content becomes stale or unsupported

- GIVEN a guide claim cannot be traced to reviewed canonical memory or current freshness metadata
- WHEN the guide is reviewed or refreshed
- THEN the claim is corrected, marked unknown, or removed before relying on it
- AND the guide does not turn an assumption or open question into a guarantee

#### Scenario: Local guide is considered for review

- GIVEN the delivered local HTML output exists
- WHEN IAQP pull-request contents are evaluated
- THEN the HTML and its generator/output assets are excluded
- AND complete, precise OpenSpec memory remains the authoritative source

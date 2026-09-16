# Isolated Staging Runtime Specification

## Purpose

Define IAQP runtime safeguards needed before isolated staging can serve traffic.

## Requirements

### Requirement: Versioned Empty-Database Schema

The system MUST provide versioned, ordered migrations that reproduce every IAQP persistence structure required by startup and the live-table lifecycle on an empty database. Migrations MUST NOT copy production or QuartzPlay data, and rerunning the approved migration path MUST preserve the reached schema version without duplicate structures.

#### Scenario: Empty database reaches required schema

- GIVEN an isolated database with no IAQP application rows
- WHEN the approved migration path is applied
- THEN required IAQP tables and constraints exist at the required version
- AND no production or QuartzPlay data is introduced

#### Scenario: Migration path is repeated

- GIVEN an isolated database already at the required schema version
- WHEN the approved migration path is applied again
- THEN it completes without duplicate schema objects or destructive data replacement

### Requirement: Database-Aware Readiness

The system MUST expose `/ready` as readiness evidence only after acquiring an IAQP database connection and completing a minimal database query. `/salud` SHALL remain liveness-only and MUST NOT be accepted as database readiness evidence. Readiness responses and logs MUST NOT disclose connection strings, credentials, or secrets.

#### Scenario: Database is available

- GIVEN the application is running with an accessible migrated database
- WHEN a client requests `/ready`
- THEN the response confirms readiness after a database connection and minimal query succeed

#### Scenario: Database is unavailable

- GIVEN the application process is running but database connection or query fails
- WHEN a client requests `/ready`
- THEN the response does not confirm readiness
- AND diagnostic output contains no secret value

### Requirement: Explicit Staging Origins

The system MUST enforce an explicit non-local staging origin allowlist. It MUST NOT permit wildcard origins in staging and MUST reject requests whose `Origin` is not explicitly approved. Local-development origins MAY be separately allowed only when explicitly configured for that environment.

#### Scenario: Approved staging origin calls API

- GIVEN a request has an explicitly approved staging origin
- WHEN it invokes a CORS-protected endpoint
- THEN the response permits that origin according to the configured policy

#### Scenario: Unapproved origin calls API

- GIVEN a request has a wildcard, production, or otherwise unapproved origin
- WHEN it invokes a CORS-protected endpoint
- THEN the response does not grant cross-origin access

### Requirement: Staging Wallet Target Guard

The system MUST validate the configured wallet destination before any wallet request in staging. It MUST reject production and unapproved destinations without making a wallet request or logging service keys, authorization headers, or URL credentials. This requirement SHALL NOT make IAQP a wallet balance authority.

#### Scenario: Approved staging wallet target

- GIVEN staging configuration names an approved wallet destination
- WHEN IAQP prepares a wallet request
- THEN the request may proceed under existing wallet ownership and idempotency rules

#### Scenario: Production or unapproved wallet target

- GIVEN staging configuration names a production or unapproved destination
- WHEN IAQP prepares a wallet request
- THEN the request is rejected before network activity
- AND logs contain no secret value

# Isolated Staging Topology Specification

## Purpose

Define isolated staging identity, evidence, smoke, and rollback controls.

## Requirements

### Requirement: Zero-Data Isolated Topology

The staging deployment MUST use a protected `staging` branch, dedicated IAQP service and generated HTTPS domain, and a separate database project. It MUST NOT share production resources, copy production data, or create a QuartzPlay configuration or deployment dependency.

#### Scenario: Owner provisions isolated staging

- GIVEN reviewed IAQP staging work is approved for promotion
- WHEN the owner provisions staging resources
- THEN the branch, service, database project, and domain are identifiable as IAQP staging
- AND the database has no production or QuartzPlay application data

#### Scenario: Shared resource is proposed

- GIVEN a proposed staging binding targets a production or shared resource
- WHEN the owner evaluates the binding
- THEN the binding is rejected and staging remains isolated

### Requirement: Deployment Evidence

The owner MUST record redacted evidence of protected branch controls, service and database identities, generated domain, deployed revision, `/ready` result, and relevant logs. Evidence MUST identify the target environment without containing secrets, connection strings, or wallet credentials.

#### Scenario: Readiness smoke succeeds

- GIVEN isolated staging has the required schema and a deployed revision
- WHEN the owner performs the approved readiness smoke
- THEN evidence records the revision, generated domain, and successful `/ready` result

#### Scenario: Evidence contains sensitive material

- GIVEN collected deployment evidence includes a secret or connection value
- WHEN the owner reviews it before recording
- THEN the sensitive value is redacted or omitted

### Requirement: Controlled Smoke Boundary

The staging smoke procedure MUST verify deployment identity and database-aware readiness only. It MUST NOT treat `/salud` as readiness proof, execute player or betting flows, or perform wallet mutations in this change.

#### Scenario: Approved bootstrap smoke

- GIVEN a deployed isolated staging revision
- WHEN the owner runs bootstrap smoke checks
- THEN only identity, redacted logs, and `/ready` evidence determine bootstrap success

#### Scenario: Wallet or game smoke is requested

- GIVEN staging bootstrap is the active change scope
- WHEN a player, betting, or wallet-mutation smoke is proposed
- THEN the procedure rejects it as out of scope

### Requirement: Safe Rollback

On staging failure, the owner MUST halt promotion and disable staging traffic or redeploy a prior known-good staging revision. The owner MUST retain the isolated database for diagnosis and forward-fix migrations; the procedure MUST NOT blindly reverse schema, alter production, or mutate QuartzPlay.

#### Scenario: Deployment fails readiness

- GIVEN a newly deployed staging revision does not satisfy `/ready`
- WHEN the owner performs rollback
- THEN traffic is disabled or a prior known-good staging revision is restored
- AND the isolated database is retained for diagnosis

#### Scenario: Migration issue is found

- GIVEN an isolated staging migration issue is identified
- WHEN the owner plans recovery
- THEN recovery uses a forward fix
- AND no destructive schema rollback is performed

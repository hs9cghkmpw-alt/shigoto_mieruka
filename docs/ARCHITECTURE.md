# Architecture

## System boundary

```text
External service
   |
   v
SourceConnector -- authenticated provider logic belongs here
   |
   v
SourceEvent -- source payload metadata / normalized event
   |
   v
Evidence -- provenance, hash, lifecycle, security
   |
   v
WorkTrace -- observed/reported work event
   |
   +--> Association Engine -- derived prediction only
   |       |
   |       +--> PROVISIONAL
   |       +--> UNASSIGNED when margin is insufficient
   |
   v
Human confirmation / correction
   |
   v
Fact -> Analysis -> Knowledge(candidate)
                       |
                       v
                Human approval
                       |
                       v
              Knowledge lifecycle
                       |
                       v
             Capability Hypothesis
```

## Layer responsibilities

### `domain`
Owns business invariants and state transitions. Domain code must not silently turn guesses into facts.

### `association`
Produces deterministic candidates and raw scores. Scores are explicitly uncalibrated unless an empirical calibration procedure has been completed.

### `ingestion`
Defines source boundaries and conversion from external events to internal Evidence and WorkTrace. Provider authentication/retrieval must remain inside the concrete connector.

### `storage`
Persists validated domain state. Storage is not allowed to weaken security classification or bypass domain validation.

### `experiment`
Measures coverage, selective accuracy and calibration on labeled data. It does not claim real-world performance without real labeled work data.

### `presentation`
Must expose uncertainty, provenance, confirmation/correction and audit history rather than hiding them behind a single score.

## Association rule
The current scorer uses weighted signals. Current weights are hypotheses, not empirically calibrated probabilities. A small score margin between top candidates should result in UNASSIGNED rather than forced assignment.

## Evidence lineage
Evidence carries source identity, observed/captured timestamps, content hash and extraction metadata. Raw source content is not persisted by default. Hash verification must be performed against the source content when available.

## Security
Classification ordering is `PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED`. Derived data must not become less restrictive than its source evidence.

## Persistence
SQLite is the current persistence implementation. It contains domain tables and audit/status-history tables. Schema versioning exists, but a full migration framework remains a roadmap item.

## Transaction boundary
Persistence methods use transactions, but the broader multi-entity lifecycle is not yet fully atomic. Do not assume that a complete ingestion-to-knowledge lifecycle is one transaction.

## Current implementation limitations
- Connector provider integrations are not authenticated real-world integrations yet.
- Evidence-to-Trace currently needs stronger multi-event grouping semantics.
- Association weights are not empirically calibrated.
- Typed reconstruction/read APIs and lifecycle atomicity need further hardening.
- UI is not yet a fully exercised end-to-end product surface.

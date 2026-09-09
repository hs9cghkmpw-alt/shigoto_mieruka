"""Source connector contract and the Evidence -> WorkTrace boundary.

This module deliberately contains no vendor credentials or polling code. A
connector must emit immutable source events; normalization creates evidence
metadata and a WorkTrace without turning predictions into observations.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from domain.evidence import ObservedEvidence, make_evidence_ref, content_hash
from domain.models import Provenance, SecurityClassification, WorkTrace


@dataclass(frozen=True)
class SourceEvent:
    event_id: str
    source_type: str
    observed_at: datetime
    payload: str
    security_classification: SecurityClassification
    provenance: Provenance = Provenance.OBSERVED


class SourceConnector(Protocol):
    connector_id: str
    extractor_version: str

    def collect(self, *, since: datetime | None = None) -> list[SourceEvent]: ...


def to_evidence(event: SourceEvent, *, captured_at: datetime, payload_digest: str | None = None) -> ObservedEvidence:
    ref = make_evidence_ref(
        evidence_id=event.event_id,
        source_type=event.source_type,
        source_id=event.event_id,
        observed_at=event.observed_at,
        captured_at=captured_at,
        content=event.payload,
        extractor_version="connector-boundary",
        security_classification=event.security_classification,
        provenance=event.provenance,
    )
    return ObservedEvidence(ref, payload_digest or content_hash(event.payload))


def evidence_to_trace(event: SourceEvent, evidence: ObservedEvidence) -> WorkTrace:
    """Create only an observed, unassigned trace; association is a later stage."""
    if evidence.evidence.provenance is not Provenance.OBSERVED:
        raise ValueError("evidence_to_trace requires observed evidence")
    return WorkTrace(
        trace_id=f"TRACE:{event.event_id}",
        event_type=event.source_type,
        occurred_at=event.observed_at,
        source=event.source_type,
        content_reference=evidence.evidence.evidence_id,
        security_classification=evidence.evidence.security_classification,
        provenance=Provenance.OBSERVED,
        evidence_ids=[evidence.evidence.evidence_id],
        extractor_version=evidence.evidence.extractor_version,
    )

"""Turn source evidence into WorkTrace without treating inference as observation."""

from domain.models import EvidenceRef, Provenance, SecurityClassification, WorkTrace


def trace_from_evidence(
    *,
    trace_id: str,
    event_type: str,
    evidence: EvidenceRef,
    occurred_at,
    content_reference: str | None = None,
    security_classification: SecurityClassification | None = None,
) -> WorkTrace:
    """Create an observed trace from immutable evidence metadata.

    No Work Item assignment is performed here. Assignment remains a separate
    inference/review step, and source provenance is carried into the trace.
    """
    if evidence.provenance is not Provenance.OBSERVED:
        raise ValueError("trace ingestion requires observed evidence")
    return WorkTrace(
        trace_id=trace_id,
        event_type=event_type,
        occurred_at=occurred_at,
        source=evidence.source_type,
        content_reference=content_reference or evidence.source_id,
        security_classification=security_classification or evidence.security_classification,
        provenance=Provenance.OBSERVED,
        evidence_ids=[evidence.evidence_id],
        extractor_version=evidence.extractor_version,
    )

from datetime import datetime, timezone

from domain.evidence import ObservedEvidence, EvidenceStatus, make_evidence_ref
from domain.models import AssignmentStatus, Provenance, SecurityClassification, WorkTrace
from domain.validation import validate_work_trace


def test_strict_validation_is_canonical():
    trace = WorkTrace("T", "mail", datetime.now(timezone.utc), assignment_status=AssignmentStatus.CONFIRMED, provenance=Provenance.OBSERVED, source="mail")
    errors = validate_work_trace(trace)
    assert "confirmed assignment requires work_item_id" in errors
    assert "confirmed assignment requires prediction to equal confirmed work item" in errors


def test_evidence_hash_and_expiration():
    now = datetime.now(timezone.utc)
    ref = make_evidence_ref(evidence_id="E1", source_type="mail", source_id="M1", observed_at=now, captured_at=now, content="secret", extractor_version="1")
    ev = ObservedEvidence(ref, ref.content_hash, expires_at=now)
    from domain.evidence import expire_evidence
    assert expire_evidence(ev, at=now).status is EvidenceStatus.EXPIRED
    assert ref.security_classification is SecurityClassification.INTERNAL

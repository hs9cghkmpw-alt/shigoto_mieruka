from datetime import datetime, timezone

from domain.evidence import content_hash, make_evidence_ref
from domain.invariants import validate_strict_work_trace
from domain.models import AssignmentStatus, Provenance, WorkTrace


def test_content_hash_is_stable_and_does_not_expose_content():
    assert content_hash("secret") == content_hash("secret")
    assert content_hash("secret") != content_hash("other")
    assert "secret" not in content_hash("secret")


def test_evidence_ref_captures_lineage_not_raw_content():
    now = datetime(2026, 9, 9, 9, tzinfo=timezone.utc)
    evidence = make_evidence_ref(
        evidence_id="E-1",
        source_type="email",
        source_id="MSG-1",
        observed_at=now,
        captured_at=now,
        content="機密な本文",
        extractor_version="email-v1",
    )
    assert evidence.source_id == "MSG-1"
    assert evidence.content_hash
    assert evidence.provenance is Provenance.OBSERVED


def test_strict_invariants_reject_contradictory_confirmed_trace():
    trace = WorkTrace(
        trace_id="T-1",
        event_type="email",
        occurred_at=datetime.now(timezone.utc),
        work_item_id="WI-2",
        predicted_work_item_id="WI-1",
        assignment_status=AssignmentStatus.CONFIRMED,
    )
    errors = validate_strict_work_trace(trace)
    assert "confirmed assignment requires prediction to equal confirmed work item" in errors


def test_strict_invariants_require_source_for_observed_trace():
    trace = WorkTrace(
        trace_id="T-1",
        event_type="email",
        occurred_at=datetime.now(timezone.utc),
        provenance=Provenance.OBSERVED,
    )
    assert "observed trace requires source" in validate_strict_work_trace(trace)

from datetime import datetime, timezone

from domain.evidence import ObservedEvidence, make_evidence_ref
from domain.models import AssignmentStatus, Provenance, SecurityClassification, WorkItem, WorkTrace
from ingestion.contracts import SourceEvent, evidence_to_trace, to_evidence
from storage.sqlite_store import SQLiteStore


def test_evidence_to_trace_never_assigns(tmp_path):
    now = datetime.now(timezone.utc)
    event = SourceEvent("E1", "mail", now, "payload", SecurityClassification.CONFIDENTIAL)
    evidence = to_evidence(event, captured_at=now)
    trace = evidence_to_trace(event, evidence)
    assert trace.assignment_status is AssignmentStatus.UNASSIGNED
    assert trace.provenance is Provenance.OBSERVED
    assert trace.evidence_ids == ["E1"]


def test_sqlite_persists_without_raw_content(tmp_path):
    now = datetime.now(timezone.utc)
    path = tmp_path / "store.sqlite3"
    with SQLiteStore(path) as store:
        item = WorkItem("WI1", "Test")
        store.save_work_item(item)
        event = SourceEvent("E1", "mail", now, "very-secret-raw-content", SecurityClassification.RESTRICTED)
        evidence = to_evidence(event, captured_at=now)
        store.save_evidence(evidence)
        trace = evidence_to_trace(event, evidence)
        store.save_trace(trace)
        store.audit(actor="tester", action="create", entity_type="trace", entity_id="TRACE:E1")
        assert store.count("work_items") == 1
        assert store.count("evidence") == 1
        assert store.count("work_traces") == 1
        assert store.count("audit_events") == 1
    raw = path.read_bytes()
    assert b"very-secret-raw-content" not in raw

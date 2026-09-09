from datetime import datetime, timezone

from domain.evidence import make_evidence_ref, ObservedEvidence
from domain.models import AssignmentCorrection, AssignmentStatus, Provenance, SecurityClassification, WorkItem, WorkTrace
from domain.assignment import correct_assignment
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


def test_sqlite_persists_without_raw_content_and_audits_correction(tmp_path):
    now = datetime.now(timezone.utc)
    path = tmp_path / "store.sqlite3"
    with SQLiteStore(path) as store:
        store.save_work_item(WorkItem("WI1", "Test"))
        event = SourceEvent("E1", "mail", now, "very-secret-raw-content", SecurityClassification.RESTRICTED)
        evidence = to_evidence(event, captured_at=now)
        store.save_evidence(evidence)
        trace = evidence_to_trace(event, evidence)
        trace.predicted_work_item_id = "WI1"
        trace.assignment_status = AssignmentStatus.PROVISIONAL
        store.save_trace(trace)
        correction = correct_assignment(trace, corrected_work_item_id="WI1", corrected_by="tester", reason="human confirmation", corrected_at=now, evidence_ids=["E1"], client_version="ui-v1")
        store.save_trace(trace)
        store.save_correction(correction)
        assert store.count("work_items") == 1
        assert store.count("evidence") == 1
        assert store.count("work_traces") == 1
        assert store.count("assignment_corrections") == 1
        assert store.count("audit_events") == 1
        row = store.connection.execute("SELECT * FROM work_traces WHERE trace_id=?", (trace.trace_id,)).fetchone()
        assert row["evidence_ids"] == '["E1"]'
    assert b"very-secret-raw-content" not in path.read_bytes()

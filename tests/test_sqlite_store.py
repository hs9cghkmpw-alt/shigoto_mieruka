from datetime import datetime, timezone

from domain.models import AssignmentStatus, Provenance, SecurityClassification, WorkItem, WorkTrace
from storage.sqlite_store import TraceStore


def test_sqlite_store_persists_work_items_and_traces():
    store = TraceStore()
    now = datetime(2026, 9, 9, 9, tzinfo=timezone.utc)
    store.save_work_item(WorkItem("WI-1", "資料作成"))
    store.save_trace(
        WorkTrace(
            trace_id="T-1",
            event_type="email",
            occurred_at=now,
            predicted_work_item_id="WI-1",
            assignment_status=AssignmentStatus.PROVISIONAL,
            source="email",
            provenance=Provenance.OBSERVED,
            security_classification=SecurityClassification.CONFIDENTIAL,
            evidence_ids=["E-1"],
            extractor_version="email-v1",
        )
    )
    assert store.connection.execute("SELECT COUNT(*) FROM work_items").fetchone()[0] == 1
    row = store.connection.execute("SELECT * FROM work_traces WHERE trace_id='T-1'").fetchone()
    assert row["predicted_work_item_id"] == "WI-1"
    assert row["provenance"] == "observed"
    assert row["security_classification"] == "confidential"
    assert row["evidence_ids"] == '["E-1"]'
    store.close()

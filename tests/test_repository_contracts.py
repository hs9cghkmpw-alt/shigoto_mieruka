from datetime import datetime, timezone

import pytest

from domain.models import AssignmentStatus, Provenance, SecurityClassification, WorkItem, WorkTrace
from storage.sqlite_store import SQLiteStore


def test_invalid_trace_is_rejected_at_storage_boundary(tmp_path):
    with SQLiteStore(tmp_path / "x.sqlite3") as store:
        trace = WorkTrace("T", "mail", datetime.now(timezone.utc), assignment_status=AssignmentStatus.CONFIRMED, provenance=Provenance.OBSERVED, source="mail")
        with pytest.raises(ValueError, match="confirmed assignment requires work_item_id"):
            store.save_trace(trace)


def test_work_item_reference_must_exist(tmp_path):
    with SQLiteStore(tmp_path / "x.sqlite3") as store:
        trace = WorkTrace("T", "mail", datetime.now(timezone.utc), work_item_id="missing", assignment_status=AssignmentStatus.CONFIRMED, provenance=Provenance.OBSERVED, source="mail")
        with pytest.raises(ValueError, match="work_item_id does not exist"):
            store.save_trace(trace)


def test_duplicate_evidence_content_is_rejected(tmp_path):
    from ingestion.contracts import SourceEvent, to_evidence
    now = datetime.now(timezone.utc)
    event = SourceEvent("E1", "mail", now, "same", SecurityClassification.INTERNAL)
    event2 = SourceEvent("E2", "mail", now, "same", SecurityClassification.INTERNAL)
    with SQLiteStore(tmp_path / "x.sqlite3") as store:
        store.save_evidence(to_evidence(event, captured_at=now))
        with pytest.raises(Exception):
            store.save_evidence(to_evidence(event2, captured_at=now))

from datetime import datetime, timezone

from application.pipeline import ingest_event
from domain.models import SecurityClassification
from ingestion.contracts import SourceEvent


def test_source_to_association_never_confirms():
    now = datetime.now(timezone.utc)
    result = ingest_event(
        SourceEvent("EV1", "test", now, "opaque payload", SecurityClassification.INTERNAL),
        captured_at=now,
        work_item_ids=["W1", "W2"],
        observed_signals={"W1": {"thread_match": True, "evidence_ids": ["EV1"]}, "W2": {}},
    )
    assert result.evidence_id
    assert result.trace_id
    assert result.association_status in {"provisional", "unassigned"}

from datetime import datetime, timedelta, timezone

from domain.models import WorkItem, WorkTrace
from domain.validation import validate_work_item, validate_work_trace


def test_valid_work_item_has_no_errors():
    assert validate_work_item(WorkItem("WI-1", "資料作成")) == []


def test_invalid_work_item_is_rejected():
    now = datetime.now(timezone.utc)
    item = WorkItem("", "", started_at=now, completed_at=now - timedelta(seconds=1))
    assert len(validate_work_item(item)) == 3


def test_trace_confidence_must_be_bounded():
    trace = WorkTrace("TRACE-1", "email", datetime.now(timezone.utc), confidence=1.1)
    assert "confidence must be between 0 and 1" in validate_work_trace(trace)

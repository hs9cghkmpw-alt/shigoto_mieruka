from datetime import datetime, timedelta, timezone

from domain.models import AssignmentStatus, WorkItem, WorkTrace
from domain.validation import validate_work_item, validate_work_trace


def test_valid_work_item_has_no_errors():
    assert validate_work_item(WorkItem("WI-1", "資料作成")) == []


def test_invalid_work_item_is_rejected():
    now = datetime.now(timezone.utc)
    item = WorkItem("", "", started_at=now, completed_at=now - timedelta(seconds=1))
    errors = validate_work_item(item)
    assert "work_item_id is required" in errors
    assert "title is required" in errors
    assert "completed_at must not precede started_at" in errors


def test_invalid_trace_is_rejected():
    now = datetime.now(timezone.utc)
    trace = WorkTrace(
        "",
        "",
        now,
        started_at=now,
        ended_at=now - timedelta(seconds=1),
        duration_seconds=-1,
        prediction_confidence=1.2,
        confidence=-0.1,
    )
    errors = validate_work_trace(trace)
    assert "trace_id is required" in errors
    assert "event_type is required" in errors
    assert "ended_at must not precede started_at" in errors
    assert "duration_seconds must not be negative" in errors
    assert "prediction_confidence must be between 0 and 1" in errors
    assert "confidence must be between 0 and 1" in errors


def test_confirmed_assignment_requires_work_item_id():
    trace = WorkTrace("TRACE-1", "email", datetime.now(timezone.utc), assignment_status=AssignmentStatus.CONFIRMED)
    assert "confirmed assignment requires work_item_id" in validate_work_trace(trace)


def test_provisional_assignment_requires_reference():
    trace = WorkTrace("TRACE-1", "email", datetime.now(timezone.utc), assignment_status=AssignmentStatus.PROVISIONAL)
    assert "provisional assignment requires a work item reference" in validate_work_trace(trace)

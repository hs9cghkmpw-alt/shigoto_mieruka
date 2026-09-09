from datetime import datetime, timezone

import pytest

from domain.assignment import confirm_assignment, correct_assignment
from domain.models import AssignmentStatus, WorkTrace


def trace():
    return WorkTrace(
        trace_id="TRACE-1",
        event_type="note",
        occurred_at=datetime(2026, 9, 9, 9, tzinfo=timezone.utc),
        predicted_work_item_id="WI-1",
        assignment_status=AssignmentStatus.PROVISIONAL,
    )


def test_confirmation_is_explicit():
    item = trace()
    confirm_assignment(item, "WI-1")
    assert item.work_item_id == "WI-1"
    assert item.predicted_work_item_id == "WI-1"
    assert item.assignment_status == AssignmentStatus.CONFIRMED


def test_confirmation_cannot_be_repeated():
    item = trace()
    confirm_assignment(item, "WI-1")
    with pytest.raises(ValueError, match="already confirmed"):
        confirm_assignment(item, "WI-1")


def test_confirmation_disagreement_requires_correction():
    item = trace()
    with pytest.raises(ValueError, match="use correction"):
        confirm_assignment(item, "WI-2")


def test_correction_preserves_prediction_and_records_previous_assignment():
    item = trace()
    correction = correct_assignment(
        item,
        corrected_work_item_id="WI-2",
        corrected_by="user",
        reason="別案件だった",
        corrected_at=datetime(2026, 9, 9, 10, tzinfo=timezone.utc),
    )
    assert correction.previous_work_item_id == "WI-1"
    assert correction.corrected_work_item_id == "WI-2"
    assert item.predicted_work_item_id == "WI-1"
    assert item.work_item_id == "WI-2"
    assert item.assignment_status == AssignmentStatus.CONFIRMED


def test_correction_can_return_trace_to_unclassified_without_erasing_prediction():
    item = trace()
    correction = correct_assignment(
        item,
        corrected_work_item_id=None,
        corrected_by="user",
        reason="判断不能",
        corrected_at=datetime(2026, 9, 9, 10, tzinfo=timezone.utc),
    )
    assert correction.previous_work_item_id == "WI-1"
    assert correction.corrected_work_item_id is None
    assert item.predicted_work_item_id == "WI-1"
    assert item.work_item_id is None
    assert item.assignment_status == AssignmentStatus.UNASSIGNED

"""Canonical domain validation.

All callers should use validate_work_trace; strict semantic invariants are
included here so validation cannot be accidentally bypassed by using a second API.
"""

from domain.invariants import validate_strict_work_trace
from domain.models import AssignmentStatus, WorkItem, WorkTrace


def validate_work_item(item: WorkItem) -> list[str]:
    errors: list[str] = []
    if not item.work_item_id.strip():
        errors.append("work_item_id is required")
    if not item.title.strip():
        errors.append("title is required")
    if item.completed_at and item.started_at and item.completed_at < item.started_at:
        errors.append("completed_at must not precede started_at")
    if item.deadline and item.started_at and item.deadline < item.started_at:
        errors.append("deadline must not precede started_at")
    return errors


def validate_work_trace(trace: WorkTrace) -> list[str]:
    errors: list[str] = []
    if not trace.trace_id.strip():
        errors.append("trace_id is required")
    if not trace.event_type.strip():
        errors.append("event_type is required")
    if trace.ended_at and trace.started_at and trace.ended_at < trace.started_at:
        errors.append("ended_at must not precede started_at")
    if trace.occurred_at is None:
        errors.append("occurred_at is required")
    if trace.duration_seconds is not None and trace.duration_seconds < 0:
        errors.append("duration_seconds must not be negative")
    if trace.prediction_confidence is not None and not 0.0 <= trace.prediction_confidence <= 1.0:
        errors.append("prediction_confidence must be between 0 and 1")
    if trace.confidence is not None and not 0.0 <= trace.confidence <= 1.0:
        errors.append("confidence must be between 0 and 1")
    if trace.assignment_status is AssignmentStatus.CONFIRMED and not trace.work_item_id:
        errors.append("confirmed assignment requires work_item_id")
    if trace.assignment_status is AssignmentStatus.PROVISIONAL and not (
        trace.predicted_work_item_id or trace.work_item_id
    ):
        errors.append("provisional assignment requires a work item reference")
    errors.extend(validate_strict_work_trace(trace))
    return list(dict.fromkeys(errors))

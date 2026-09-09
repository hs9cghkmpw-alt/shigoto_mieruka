"""Small deterministic validation helpers for domain objects."""

from domain.models import WorkItem, WorkTrace


def validate_work_item(item: WorkItem) -> list[str]:
    errors: list[str] = []
    if not item.work_item_id.strip():
        errors.append("work_item_id is required")
    if not item.title.strip():
        errors.append("title is required")
    if item.completed_at and item.started_at and item.completed_at < item.started_at:
        errors.append("completed_at must not precede started_at")
    return errors


def validate_work_trace(trace: WorkTrace) -> list[str]:
    errors: list[str] = []
    if not trace.trace_id.strip():
        errors.append("trace_id is required")
    if not trace.event_type.strip():
        errors.append("event_type is required")
    if trace.ended_at and trace.started_at and trace.ended_at < trace.started_at:
        errors.append("ended_at must not precede started_at")
    if trace.prediction_confidence is not None and not 0.0 <= trace.prediction_confidence <= 1.0:
        errors.append("prediction_confidence must be between 0 and 1")
    if trace.confidence is not None and not 0.0 <= trace.confidence <= 1.0:
        errors.append("confidence must be between 0 and 1")
    return errors

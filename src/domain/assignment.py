"""Assignment lifecycle rules.

These functions make provisional assignment, confirmation, and correction
explicit state transitions instead of allowing callers to mutate fields ad hoc.
"""

from datetime import datetime

from domain.models import AssignmentCorrection, AssignmentStatus, WorkTrace


def confirm_assignment(trace: WorkTrace, work_item_id: str) -> WorkTrace:
    """Confirm a human-reviewed assignment without changing its provenance."""
    if not work_item_id.strip():
        raise ValueError("work_item_id is required")
    if trace.assignment_status == AssignmentStatus.CONFIRMED:
        raise ValueError("trace is already confirmed")
    trace.work_item_id = work_item_id
    trace.assignment_status = AssignmentStatus.CONFIRMED
    return trace


def correct_assignment(
    trace: WorkTrace,
    *,
    corrected_work_item_id: str | None,
    corrected_by: str,
    reason: str,
    corrected_at: datetime,
) -> AssignmentCorrection:
    """Record a correction and apply only the new assignment state."""
    if not corrected_by.strip():
        raise ValueError("corrected_by is required")
    if not reason.strip():
        raise ValueError("reason is required")
    previous = trace.work_item_id or trace.predicted_work_item_id
    trace.work_item_id = corrected_work_item_id
    trace.predicted_work_item_id = corrected_work_item_id
    trace.assignment_status = (
        AssignmentStatus.CONFIRMED if corrected_work_item_id else AssignmentStatus.UNASSIGNED
    )
    return AssignmentCorrection(
        correction_id=f"CORR-{trace.trace_id}-{corrected_at.isoformat()}",
        trace_id=trace.trace_id,
        previous_work_item_id=previous,
        corrected_work_item_id=corrected_work_item_id,
        corrected_at=corrected_at,
        corrected_by=corrected_by,
        reason=reason,
    )

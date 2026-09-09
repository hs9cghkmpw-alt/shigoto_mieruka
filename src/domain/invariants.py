"""Cross-field invariants kept separate from legacy validation helpers."""

from domain.models import AssignmentStatus, Provenance, WorkTrace


def validate_strict_work_trace(trace: WorkTrace) -> list[str]:
    """Return errors that would make a trace semantically self-contradictory."""
    errors: list[str] = []
    if trace.assignment_status is AssignmentStatus.UNASSIGNED and trace.work_item_id:
        errors.append("unassigned trace cannot contain work_item_id")
    if trace.assignment_status is AssignmentStatus.PROVISIONAL and not trace.predicted_work_item_id:
        errors.append("provisional assignment requires predicted_work_item_id")
    if trace.assignment_status is AssignmentStatus.CONFIRMED:
        if not trace.work_item_id:
            errors.append("confirmed assignment requires work_item_id")
        if trace.predicted_work_item_id != trace.work_item_id:
            errors.append("confirmed assignment requires prediction to equal confirmed work item")
    if trace.provenance is Provenance.OBSERVED and not trace.source:
        errors.append("observed trace requires source")
    if trace.evidence_ids and trace.provenance is not Provenance.OBSERVED:
        errors.append("evidence_ids require observed provenance")
    return errors

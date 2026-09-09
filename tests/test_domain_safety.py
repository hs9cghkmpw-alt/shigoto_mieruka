from datetime import datetime, timezone

from domain.models import AssignmentCorrection, SecurityClassification
from domain.security import inherit_security_classification


def test_assignment_correction_preserves_previous_and_new_values():
    correction = AssignmentCorrection(
        correction_id="COR-001",
        trace_id="TRACE-001",
        previous_work_item_id="WI-001",
        corrected_work_item_id="WI-002",
        corrected_at=datetime.now(timezone.utc),
        corrected_by="human",
        reason="confirmed by requester",
    )
    assert correction.previous_work_item_id == "WI-001"
    assert correction.corrected_work_item_id == "WI-002"


def test_derived_security_cannot_be_weaker_than_source():
    assert inherit_security_classification(
        SecurityClassification.CONFIDENTIAL,
        SecurityClassification.PUBLIC,
    ) == SecurityClassification.CONFIDENTIAL
    assert inherit_security_classification(
        SecurityClassification.PUBLIC,
        SecurityClassification.RESTRICTED,
    ) == SecurityClassification.RESTRICTED

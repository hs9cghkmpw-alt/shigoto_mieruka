"""End-to-end application pipeline: source event -> evidence -> trace -> association."""

from dataclasses import dataclass
from datetime import datetime
from ingestion.contracts import SourceEvent, to_evidence, evidence_to_trace
from association.engine import associate


@dataclass(frozen=True)
class PipelineResult:
    evidence_id: str
    trace_id: str
    association_status: str
    predicted_work_item_id: str | None
    association_score: float


def ingest_event(event: SourceEvent, *, captured_at: datetime, work_item_ids: list[str], observed_signals: dict) -> PipelineResult:
    """Convert one observed event without ever auto-confirming assignment."""
    observed = to_evidence(event, captured_at=captured_at)
    trace = evidence_to_trace(event, observed)
    result = associate(work_item_ids, observed_signals)
    trace.predicted_work_item_id = result.predicted_work_item_id
    trace.prediction_confidence = result.association_score
    trace.assignment_status = result.status
    trace.evidence_ids = [observed.evidence.evidence_id]
    return PipelineResult(observed.evidence.evidence_id, trace.trace_id, result.status, result.predicted_work_item_id, result.association_score)

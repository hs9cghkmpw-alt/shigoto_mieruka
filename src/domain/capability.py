"""Condition-aware capability hypotheses, never personnel scoring."""

from datetime import datetime

from domain.models import CapabilityHypothesis


def propose_capability_hypothesis(*, hypothesis_id: str, work_item_type: str, context: list[str], observed_outcome: str, source_trace_ids: list[str], source_fact_ids: list[str] | None = None, confidence: float | None = None) -> CapabilityHypothesis:
    if not hypothesis_id.strip() or not work_item_type.strip() or not observed_outcome.strip():
        raise ValueError("hypothesis_id, work_item_type and observed_outcome are required")
    if not source_trace_ids:
        raise ValueError("capability hypothesis requires observed trace evidence")
    if confidence is not None and not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be between 0 and 1")
    return CapabilityHypothesis(
        hypothesis_id=hypothesis_id,
        work_item_type=work_item_type,
        context=tuple(sorted(set(c.strip() for c in context if c.strip()))),
        observed_outcome=observed_outcome,
        source_trace_ids=tuple(source_trace_ids),
        source_fact_ids=tuple(source_fact_ids or []),
        confidence=confidence,
    )


def review_capability_hypothesis(hypothesis: CapabilityHypothesis, *, reviewed_by: str, reviewed_at: datetime, approved: bool) -> CapabilityHypothesis:
    if not reviewed_by.strip(): raise ValueError("reviewed_by is required")
    return CapabilityHypothesis(
        hypothesis_id=hypothesis.hypothesis_id,
        work_item_type=hypothesis.work_item_type,
        context=hypothesis.context,
        observed_outcome=hypothesis.observed_outcome,
        source_trace_ids=hypothesis.source_trace_ids,
        source_fact_ids=hypothesis.source_fact_ids,
        confidence=hypothesis.confidence,
        reviewed_by=reviewed_by,
        reviewed_at=reviewed_at,
        status="validated" if approved else "rejected",
    )

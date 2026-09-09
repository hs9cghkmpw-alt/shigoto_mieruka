"""Observable WorkTrace -> WorkItem association engine.

The engine deliberately separates signal extraction from scoring. It accepts
already-observed signals and produces a provisional candidate only; it never
confirms an assignment or mutates source facts.
"""

from dataclasses import dataclass
from typing import Mapping

from association.scorer import Candidate, choose_assignment, score_candidate


@dataclass(frozen=True)
class AssociationResult:
    predicted_work_item_id: str | None
    confidence: float
    status: str
    candidates: tuple[Candidate, ...]


def _signal_bool(signals: Mapping[str, object], name: str) -> bool:
    value = signals.get(name, False)
    return bool(value)


def build_candidates(
    work_item_ids: list[str],
    observed_signals: Mapping[str, Mapping[str, object]],
) -> list[Candidate]:
    """Build deterministic candidates from externally observed signals."""
    candidates: list[Candidate] = []
    for work_item_id in work_item_ids:
        signals = observed_signals.get(work_item_id, {})
        score = score_candidate(
            thread_match=_signal_bool(signals, "thread_match"),
            document_match=_signal_bool(signals, "document_match"),
            participant_match=_signal_bool(signals, "participant_match"),
            project_match=_signal_bool(signals, "project_match"),
            recent_active=_signal_bool(signals, "recent_active"),
            keyword_match=_signal_bool(signals, "keyword_match"),
            time_proximity=_signal_bool(signals, "time_proximity"),
        )
        reasons = tuple(name for name, value in signals.items() if bool(value))
        candidates.append(Candidate(work_item_id, score, reasons))
    return candidates


def associate(
    work_item_ids: list[str],
    observed_signals: Mapping[str, Mapping[str, object]],
    *,
    minimum_confidence: float = 0.60,
) -> AssociationResult:
    """Return a provisional assignment or an explicit unclassified result."""
    candidates = build_candidates(work_item_ids, observed_signals)
    selected = choose_assignment(candidates, minimum_confidence=minimum_confidence)
    if selected is None:
        return AssociationResult(None, 0.0, "unassigned", tuple(candidates))
    return AssociationResult(
        selected.work_item_id,
        selected.score,
        "provisional",
        tuple(candidates),
    )

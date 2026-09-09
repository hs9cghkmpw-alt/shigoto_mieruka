"""Observable WorkTrace -> WorkItem association engine."""

from dataclasses import dataclass
from typing import Mapping

from association.scorer import Candidate, choose_assignment, score_candidate


@dataclass(frozen=True)
class AssociationResult:
    predicted_work_item_id: str | None
    confidence: float
    status: str
    margin: float
    candidates: tuple[Candidate, ...]


def _signal_bool(signals: Mapping[str, object], name: str) -> bool:
    return bool(signals.get(name, False))


def build_candidates(
    work_item_ids: list[str],
    observed_signals: Mapping[str, Mapping[str, object]],
) -> list[Candidate]:
    """Build candidates only from externally observed signals."""
    candidates: list[Candidate] = []
    for work_item_id in work_item_ids:
        signals = observed_signals.get(work_item_id, {})
        score = score_candidate(**{name: _signal_bool(signals, name) for name in (
            "thread_match", "document_match", "participant_match", "project_match",
            "recent_active", "keyword_match", "time_proximity",
        )})
        reasons = tuple(name for name, value in signals.items() if bool(value))
        candidates.append(Candidate(work_item_id, score, reasons))
    return candidates


def associate(
    work_item_ids: list[str],
    observed_signals: Mapping[str, Mapping[str, object]],
    *,
    minimum_confidence: float = 0.60,
    minimum_margin: float = 0.05,
) -> AssociationResult:
    """Return a provisional assignment only when confidence and separation suffice."""
    candidates = build_candidates(work_item_ids, observed_signals)
    ranked = sorted(candidates, key=lambda candidate: (-candidate.score, candidate.work_item_id))
    margin = ranked[0].score - ranked[1].score if len(ranked) > 1 else ranked[0].score if ranked else 0.0
    selected = choose_assignment(
        candidates,
        minimum_confidence=minimum_confidence,
        minimum_margin=minimum_margin,
    )
    if selected is None:
        return AssociationResult(None, 0.0, "unassigned", round(margin, 10), tuple(candidates))
    return AssociationResult(
        selected.work_item_id,
        selected.score,
        "provisional",
        round(margin, 10),
        tuple(candidates),
    )

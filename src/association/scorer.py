"""Conservative deterministic Work Item candidate scoring."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    work_item_id: str
    score: float
    reasons: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()

    @property
    def association_score(self) -> float:
        """Raw rule score; explicitly not a calibrated probability."""
        return self.score


WEIGHTS = {
    "thread_match": 0.40,
    "document_match": 0.20,
    "participant_match": 0.12,
    "project_match": 0.10,
    "recent_active": 0.08,
    "keyword_match": 0.06,
    "time_proximity": 0.04,
}


def score_candidate(**signals: bool) -> float:
    return round(min(sum(weight for name, weight in WEIGHTS.items() if bool(signals.get(name, False))), 1.0), 10)


def choose_assignment(candidates: list[Candidate], *, minimum_confidence: float = 0.60, minimum_margin: float = 0.05) -> Candidate | None:
    if not 0.0 <= minimum_confidence <= 1.0: raise ValueError("minimum_confidence must be between 0 and 1")
    if minimum_margin < 0.0: raise ValueError("minimum_margin must be non-negative")
    if not candidates: return None
    ranked = sorted(candidates, key=lambda c: (-c.score, c.work_item_id))
    best = ranked[0]
    if best.score < minimum_confidence: return None
    if len(ranked) > 1 and best.score - ranked[1].score < minimum_margin: return None
    return best

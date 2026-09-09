"""Rule-based Work Item candidate scoring.

This deliberately does not call an LLM. The first implementation must make
association behavior observable and testable before semantic AI is introduced.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    work_item_id: str
    score: float
    reasons: tuple[str, ...]


def score_candidate(
    *,
    thread_match: bool = False,
    document_match: bool = False,
    participant_match: bool = False,
    project_match: bool = False,
    recent_active: bool = False,
    keyword_match: bool = False,
    time_proximity: bool = False,
) -> float:
    """Return a deterministic score from observable signals."""
    score = 0.0
    score += 0.40 if thread_match else 0.0
    score += 0.20 if document_match else 0.0
    score += 0.12 if participant_match else 0.0
    score += 0.10 if project_match else 0.0
    score += 0.08 if recent_active else 0.0
    score += 0.06 if keyword_match else 0.0
    score += 0.04 if time_proximity else 0.0
    return round(min(score, 1.0), 10)


def choose_assignment(
    candidates: list[Candidate],
    *,
    minimum_confidence: float = 0.60,
) -> Candidate | None:
    """Choose a unique best candidate, or return None for the unclassified tray."""
    if not candidates:
        return None

    ranked = sorted(candidates, key=lambda candidate: candidate.score, reverse=True)
    best = ranked[0]
    if best.score < minimum_confidence:
        return None
    if len(ranked) > 1 and ranked[1].score == best.score:
        return None
    return best

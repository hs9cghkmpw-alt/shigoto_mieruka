from association.scorer import Candidate, choose_assignment, score_candidate


def test_strong_thread_signal_wins():
    strong = Candidate("WI-1", score_candidate(thread_match=True), ("thread",))
    weak = Candidate("WI-2", 0.2, ("weak",))
    assert choose_assignment([weak, strong]).work_item_id == "WI-1"


def test_low_confidence_goes_unassigned():
    candidate = Candidate("WI-1", score_candidate(time_proximity=True), ("time",))
    assert choose_assignment([candidate]) is None


def test_score_is_deterministic_and_bounded():
    score = score_candidate(
        thread_match=True,
        document_match=True,
        participant_match=True,
        project_match=True,
        recent_active=True,
        keyword_match=True,
        time_proximity=True,
    )
    assert score == 1.0

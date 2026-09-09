from association.scorer import Candidate, choose_assignment, score_candidate


def test_strong_thread_signal_alone_stays_unassigned():
    strong = Candidate("WI-1", score_candidate(thread_match=True), ("thread",))
    weak = Candidate("WI-2", 0.2, ("weak",))
    assert choose_assignment([weak, strong]) is None


def test_combined_signals_can_assign_provisionally():
    strong = Candidate(
        "WI-1",
        score_candidate(thread_match=True, document_match=True),
        ("thread", "document"),
    )
    weak = Candidate("WI-2", 0.2, ("weak",))
    assignment = choose_assignment([weak, strong])
    assert assignment is not None
    assert assignment.work_item_id == "WI-1"


def test_low_confidence_goes_unassigned():
    candidate = Candidate("WI-1", score_candidate(time_proximity=True), ("time",))
    assert choose_assignment([candidate]) is None


def test_tied_candidates_go_unassigned():
    candidates = [
        Candidate("WI-1", 0.70, ("thread",)),
        Candidate("WI-2", 0.70, ("thread",)),
    ]
    assert choose_assignment(candidates) is None


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

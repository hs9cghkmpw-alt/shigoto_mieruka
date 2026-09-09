from association.engine import associate, build_candidates


def test_build_candidates_uses_observed_signals_only():
    candidates = build_candidates(
        ["WI-1", "WI-2"],
        {
            "WI-1": {"thread_match": True, "document_match": True},
            "WI-2": {"keyword_match": True},
        },
    )
    assert candidates[0].score == 0.60
    assert candidates[0].reasons == ("thread_match", "document_match")
    assert candidates[1].score == 0.06


def test_associate_returns_provisional_not_confirmed():
    result = associate(
        ["WI-1", "WI-2"],
        {"WI-1": {"thread_match": True, "document_match": True}, "WI-2": {}},
    )
    assert result.predicted_work_item_id == "WI-1"
    assert result.status == "provisional"
    assert result.confidence == 0.60
    assert result.margin == 0.60


def test_associate_keeps_ambiguous_case_unclassified():
    result = associate(
        ["WI-1", "WI-2"],
        {
            "WI-1": {"thread_match": True, "document_match": True},
            "WI-2": {"thread_match": True, "document_match": True},
        },
    )
    assert result.predicted_work_item_id is None
    assert result.status == "unassigned"
    assert result.margin == 0.0
    assert len(result.candidates) == 2


def test_associate_rejects_close_competition():
    result = associate(
        ["WI-1", "WI-2"],
        {
            "WI-1": {"thread_match": True, "document_match": True},
            "WI-2": {"thread_match": True, "participant_match": True, "time_proximity": True},
        },
    )
    assert result.predicted_work_item_id is None
    assert result.status == "unassigned"

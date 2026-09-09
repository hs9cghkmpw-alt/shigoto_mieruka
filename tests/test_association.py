from association.engine import associate


def test_close_candidates_remain_unassigned():
    result=associate(["WI1","WI2"],{"WI1":{"thread_match":True,"evidence_ids":["E1"]},"WI2":{"thread_match":True,"document_match":True,"evidence_ids":["E2"]}},minimum_confidence=.2,minimum_margin=.2)
    assert result.status=="unassigned"
    assert result.predicted_work_item_id is None
    assert result.calibrated_confidence is None


def test_candidate_carries_evidence_refs_and_score_is_not_probability():
    result=associate(["WI1","WI2"],{"WI1":{"thread_match":True,"document_match":True,"evidence_ids":["E1","E2"]},"WI2":{}})
    assert result.predicted_work_item_id=="WI1"
    assert result.candidates[0].evidence_ids==("E1","E2")
    assert result.association_score == result.candidates[0].association_score
    assert result.calibration_status == "uncalibrated"

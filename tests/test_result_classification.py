from experiment.aggregator import classify_result


def test_confident_correct_assignment_is_go():
    assert classify_result(predicted="WI-1", expected="WI-1", confidence=0.80) == "GO"


def test_low_confidence_correct_assignment_is_gray():
    assert classify_result(predicted="WI-1", expected="WI-1", confidence=0.59) == "GRAY"


def test_confident_wrong_assignment_is_stop():
    assert classify_result(predicted="WI-2", expected="WI-1", confidence=0.80) == "STOP"


def test_low_confidence_wrong_assignment_is_gray():
    assert classify_result(predicted="WI-2", expected="WI-1", confidence=0.59) == "GRAY"


def test_unassigned_is_gray():
    assert classify_result(predicted=None, expected="WI-1", confidence=0.0) == "GRAY"


def test_custom_threshold_is_respected():
    assert classify_result(predicted="WI-2", expected="WI-1", confidence=0.70, minimum_confidence=0.80) == "GRAY"

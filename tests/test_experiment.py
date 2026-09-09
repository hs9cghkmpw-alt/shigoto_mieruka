from experiment.aggregator import classify_result


def test_correct_high_confidence_is_go():
    assert classify_result(predicted="WI-1", expected="WI-1", confidence=0.9) == "GO"


def test_low_confidence_is_gray():
    assert classify_result(predicted=None, expected="WI-1", confidence=0.0) == "GRAY"
    assert classify_result(predicted="WI-1", expected="WI-1", confidence=0.5) == "GRAY"


def test_confident_wrong_assignment_is_stop():
    assert classify_result(predicted="WI-2", expected="WI-1", confidence=0.9) == "STOP"

import pytest

from experiment.aggregator import aggregate_csv, validate_experiment_rows


def test_valid_experiment_row_has_no_schema_errors():
    row = {
        "experiment_id": "EXP-001",
        "trace_id": "TRACE-001",
        "expected_work_item_id": "WI-001",
        "predicted_work_item_id": "WI-001",
        "confidence": "0.80",
        "assignment_status": "provisional",
        "corrected": "false",
        "result": "GO",
    }
    assert validate_experiment_rows([row]) == []


def test_invalid_experiment_row_is_rejected():
    row = {
        "experiment_id": "EXP-001",
        "trace_id": "TRACE-001",
        "expected_work_item_id": "WI-001",
        "predicted_work_item_id": "WI-002",
        "confidence": "1.20",
        "assignment_status": "provisional",
        "corrected": "maybe",
        "result": "UNKNOWN",
    }
    errors = validate_experiment_rows([row])
    assert "row 2: result must be GO, GRAY, or STOP" in errors
    assert "row 2: confidence must be between 0 and 1" in errors
    assert "row 2: corrected must be true or false" in errors


def test_empty_experiment_log_is_rejected():
    assert validate_experiment_rows([]) == ["experiment log must contain at least one row"]


def test_aggregate_rejects_invalid_csv(tmp_path):
    output = tmp_path / "invalid.csv"
    output.write_text(
        "experiment_id,trace_id,expected_work_item_id,predicted_work_item_id,confidence,assignment_status,corrected,result\n"
        "EXP-001,T-1,WI-1,WI-2,2.0,provisional,false,STOP\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid experiment log"):
        aggregate_csv(output)

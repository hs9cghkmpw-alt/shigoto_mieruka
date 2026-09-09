import pytest

from experiment.aggregator import aggregate_csv, validate_experiment_rows


def valid_row(**overrides):
    row = {
        "experiment_id": "EXP-001",
        "trace_id": "TRACE-001",
        "occurred_at": "2026-09-09T09:00:00+09:00",
        "event_type": "work_started",
        "work_description": "資料を確認した",
        "observed_signals": "thread;document",
        "expected_work_item_id": "WI-001",
        "predicted_work_item_id": "WI-001",
        "confidence": "0.80",
        "assignment_status": "provisional",
        "corrected": "false",
        "correction_reason": "",
        "recording_seconds": "12",
        "review_seconds": "5",
        "result": "GO",
        "notes": "",
    }
    row.update(overrides)
    return row


def test_valid_experiment_row_has_no_schema_errors():
    assert validate_experiment_rows([valid_row()]) == []


def test_invalid_experiment_row_is_rejected():
    errors = validate_experiment_rows([valid_row(
        confidence="1.20", corrected="maybe", result="UNKNOWN"
    )])
    assert "row 2: result must be GO, GRAY, or STOP" in errors
    assert "row 2: confidence must be between 0 and 1" in errors
    assert "row 2: corrected must be true or false" in errors


def test_required_real_data_fields_are_enforced():
    row = valid_row(work_description="", recording_seconds="-1", review_seconds="x")
    errors = validate_experiment_rows([row])
    assert "row 2: work_description is required" in errors
    assert "row 2: recording_seconds must be non-negative" in errors
    assert "row 2: review_seconds must be numeric" in errors


def test_correction_requires_reason():
    errors = validate_experiment_rows([valid_row(corrected="true", correction_reason="")])
    assert "row 2: correction_reason is required when corrected is true" in errors


def test_stop_cannot_claim_matching_prediction():
    errors = validate_experiment_rows([valid_row(result="STOP")])
    assert "row 2: STOP cannot have matching predicted and expected work item" in errors


def test_duplicate_ids_are_rejected():
    errors = validate_experiment_rows([valid_row(), valid_row()])
    assert "row 3: duplicate experiment_id: EXP-001" in errors
    assert "row 3: duplicate trace_id: TRACE-001" in errors


def test_empty_experiment_log_is_rejected():
    assert validate_experiment_rows([]) == ["experiment log must contain at least one row"]


def test_aggregate_rejects_invalid_csv(tmp_path):
    output = tmp_path / "invalid.csv"
    output.write_text(
        "experiment_id,trace_id,occurred_at,event_type,work_description,observed_signals,expected_work_item_id,predicted_work_item_id,confidence,assignment_status,corrected,correction_reason,recording_seconds,review_seconds,result,notes\n"
        "EXP-001,T-1,2026-09-09T09:00:00+09:00,work_started,test,,WI-1,WI-2,2.0,provisional,false,,0,0,STOP,test\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid experiment log"):
        aggregate_csv(output)

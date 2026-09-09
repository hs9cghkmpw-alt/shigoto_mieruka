"""Aggregate deterministic association experiment results."""

import csv
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = {
    "experiment_id", "trace_id", "occurred_at", "event_type", "work_description",
    "observed_signals", "expected_work_item_id", "predicted_work_item_id", "confidence",
    "assignment_status", "corrected", "correction_reason", "recording_seconds",
    "review_seconds", "result", "notes",
}


def classify_result(*, predicted: str | None, expected: str | None, confidence: float, minimum_confidence: float = 0.60) -> str:
    """Classify an experiment as GO, GRAY, or STOP."""
    if predicted and expected and predicted != expected and confidence >= minimum_confidence:
        return "STOP"
    if predicted == expected and predicted and confidence >= minimum_confidence:
        return "GO"
    return "GRAY"


def validate_experiment_rows(rows: list[dict[str, str]]) -> list[str]:
    """Return deterministic schema/data errors for an experiment CSV."""
    if not rows:
        return ["experiment log must contain at least one row"]
    errors: list[str] = []
    missing = REQUIRED_COLUMNS - set(rows[0])
    errors.extend(f"missing required column: {name}" for name in sorted(missing))
    allowed_results = {"GO", "GRAY", "STOP"}
    allowed_statuses = {"unassigned", "provisional", "confirmed"}
    seen_experiments: set[str] = set()
    seen_traces: set[str] = set()
    for index, row in enumerate(rows, start=2):
        experiment_id = row.get("experiment_id", "").strip()
        trace_id = row.get("trace_id", "").strip()
        if not experiment_id:
            errors.append(f"row {index}: experiment_id is required")
        elif experiment_id in seen_experiments:
            errors.append(f"row {index}: duplicate experiment_id: {experiment_id}")
        else:
            seen_experiments.add(experiment_id)
        if not trace_id:
            errors.append(f"row {index}: trace_id is required")
        elif trace_id in seen_traces:
            errors.append(f"row {index}: duplicate trace_id: {trace_id}")
        else:
            seen_traces.add(trace_id)
        if not row.get("occurred_at", "").strip():
            errors.append(f"row {index}: occurred_at is required")
        if not row.get("event_type", "").strip():
            errors.append(f"row {index}: event_type is required")
        if not row.get("work_description", "").strip():
            errors.append(f"row {index}: work_description is required")
        if row.get("result") not in allowed_results:
            errors.append(f"row {index}: result must be GO, GRAY, or STOP")
        if row.get("assignment_status", "").lower() not in allowed_statuses:
            errors.append(f"row {index}: assignment_status must be unassigned, provisional, or confirmed")
        try:
            confidence = float(row.get("confidence", ""))
        except (TypeError, ValueError):
            errors.append(f"row {index}: confidence must be numeric")
        else:
            if not 0.0 <= confidence <= 1.0:
                errors.append(f"row {index}: confidence must be between 0 and 1")
        for field in ("recording_seconds", "review_seconds"):
            try:
                seconds = float(row.get(field, ""))
            except (TypeError, ValueError):
                errors.append(f"row {index}: {field} must be numeric")
            else:
                if seconds < 0:
                    errors.append(f"row {index}: {field} must be non-negative")
        if row.get("corrected", "").lower() not in {"true", "false"}:
            errors.append(f"row {index}: corrected must be true or false")
        if row.get("corrected", "").lower() == "true" and not row.get("correction_reason", "").strip():
            errors.append(f"row {index}: correction_reason is required when corrected is true")
        if row.get("result") == "STOP" and row.get("predicted_work_item_id", "").strip() == row.get("expected_work_item_id", "").strip():
            errors.append(f"row {index}: STOP cannot have matching predicted and expected work item")
    return errors


def aggregate_csv(path: str | Path) -> dict:
    """Read an experiment CSV and return reproducible summary statistics."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    errors = validate_experiment_rows(rows)
    if errors:
        raise ValueError("invalid experiment log: " + "; ".join(errors))

    results = Counter(row["result"] for row in rows)
    assigned = [row for row in rows if row.get("predicted_work_item_id", "").strip()]
    corrections = sum(row.get("corrected", "").lower() == "true" for row in rows)
    false_positive = sum(row["result"] == "STOP" for row in rows)
    recording_seconds = sum(float(row["recording_seconds"]) for row in rows)
    review_seconds = sum(float(row["review_seconds"]) for row in rows)
    return {
        "total": len(rows),
        "go": results["GO"],
        "gray": results["GRAY"],
        "stop": results["STOP"],
        "corrections": corrections,
        "assignment_rate": len(assigned) / len(rows),
        "unassigned_rate": 1.0 - (len(assigned) / len(rows)),
        "false_positive_rate": false_positive / len(rows),
        "correction_rate_on_all": corrections / len(rows),
        "accuracy_on_assigned": (
            sum(row.get("predicted_work_item_id") == row.get("expected_work_item_id") for row in assigned)
            / len(assigned) if assigned else 0.0
        ),
        "recording_seconds_total": recording_seconds,
        "recording_seconds_mean": recording_seconds / len(rows),
        "review_seconds_total": review_seconds,
        "review_seconds_mean": review_seconds / len(rows),
    }

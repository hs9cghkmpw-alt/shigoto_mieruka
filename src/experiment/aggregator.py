"""Validate and aggregate experiment results without trusting self-reported outcomes."""

import csv
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = {
    "experiment_id", "trace_id", "occurred_at", "event_type", "work_description",
    "observed_signals", "expected_work_item_id", "predicted_work_item_id", "confidence",
    "assignment_status", "corrected", "correction_reason", "recording_seconds",
    "review_seconds", "result", "notes",
}
ALLOWED_RESULTS = {"GO", "GRAY", "STOP"}
ALLOWED_STATUSES = {"unassigned", "provisional", "confirmed"}


def classify_result(*, predicted: str | None, expected: str | None, confidence: float, minimum_confidence: float = 0.60) -> str:
    """Derive GO/GRAY/STOP from prediction evidence, never from a result field."""
    if predicted and expected and predicted != expected and confidence >= minimum_confidence:
        return "STOP"
    if predicted and expected and predicted == expected and confidence >= minimum_confidence:
        return "GO"
    return "GRAY"


def _validate_prediction_consistency(row: dict[str, str], index: int, errors: list[str]) -> None:
    predicted = row.get("predicted_work_item_id", "").strip() or None
    expected = row.get("expected_work_item_id", "").strip() or None
    status = row.get("assignment_status", "").strip().lower()
    if status == "unassigned" and predicted is not None:
        errors.append(f"row {index}: unassigned cannot contain predicted_work_item_id")
    if status == "provisional" and predicted is None:
        errors.append(f"row {index}: provisional requires predicted_work_item_id")
    if status == "confirmed" and (predicted is None or expected is None):
        errors.append(f"row {index}: confirmed requires predicted and expected work item")


def validate_experiment_rows(rows: list[dict[str, str]]) -> list[str]:
    """Return deterministic schema/data errors for an experiment CSV."""
    if not rows:
        return ["experiment log must contain at least one row"]
    errors: list[str] = []
    missing = REQUIRED_COLUMNS - set(rows[0])
    errors.extend(f"missing required column: {name}" for name in sorted(missing))
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
        for field in ("occurred_at", "event_type", "work_description"):
            if not row.get(field, "").strip():
                errors.append(f"row {index}: {field} is required")
        if row.get("result") not in ALLOWED_RESULTS:
            errors.append(f"row {index}: result must be GO, GRAY, or STOP")
        status = row.get("assignment_status", "").lower()
        if status not in ALLOWED_STATUSES:
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
        corrected = row.get("corrected", "").lower()
        if corrected not in {"true", "false"}:
            errors.append(f"row {index}: corrected must be true or false")
        if corrected == "true" and not row.get("correction_reason", "").strip():
            errors.append(f"row {index}: correction_reason is required when corrected is true")
        _validate_prediction_consistency(row, index, errors)
        try:
            derived = classify_result(
                predicted=row.get("predicted_work_item_id", "").strip() or None,
                expected=row.get("expected_work_item_id", "").strip() or None,
                confidence=float(row.get("confidence", "")),
            )
        except (TypeError, ValueError):
            continue
        if row.get("result") != derived:
            errors.append(f"row {index}: result does not match deterministic classification ({derived})")
    return errors


def aggregate_csv(path: str | Path) -> dict:
    """Read an experiment CSV and calculate outcomes from evidence fields."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    errors = validate_experiment_rows(rows)
    if errors:
        raise ValueError("invalid experiment log: " + "; ".join(errors))
    results = Counter(
        classify_result(
            predicted=row.get("predicted_work_item_id", "").strip() or None,
            expected=row.get("expected_work_item_id", "").strip() or None,
            confidence=float(row["confidence"]),
        )
        for row in rows
    )
    assigned = [row for row in rows if row.get("predicted_work_item_id", "").strip()]
    corrections = sum(row.get("corrected", "").lower() == "true" for row in rows)
    recording_seconds = sum(float(row["recording_seconds"]) for row in rows)
    review_seconds = sum(float(row["review_seconds"]) for row in rows)
    return {
        "total": len(rows), "go": results["GO"], "gray": results["GRAY"], "stop": results["STOP"],
        "corrections": corrections, "assignment_rate": len(assigned) / len(rows),
        "unassigned_rate": 1.0 - (len(assigned) / len(rows)),
        "false_positive_rate": results["STOP"] / len(rows),
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

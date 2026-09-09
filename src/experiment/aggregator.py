"""Aggregate deterministic association experiment results."""

import csv
from collections import Counter
from pathlib import Path

REQUIRED_COLUMNS = {
    "experiment_id",
    "trace_id",
    "expected_work_item_id",
    "predicted_work_item_id",
    "confidence",
    "assignment_status",
    "corrected",
    "result",
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
    missing = REQUIRED_COLUMNS - set(rows[0])
    errors = [f"missing required column: {name}" for name in sorted(missing)]
    allowed_results = {"GO", "GRAY", "STOP"}
    for index, row in enumerate(rows, start=2):
        if row.get("result") not in allowed_results:
            errors.append(f"row {index}: result must be GO, GRAY, or STOP")
        try:
            confidence = float(row.get("confidence", ""))
        except (TypeError, ValueError):
            errors.append(f"row {index}: confidence must be numeric")
        else:
            if not 0.0 <= confidence <= 1.0:
                errors.append(f"row {index}: confidence must be between 0 and 1")
        if row.get("corrected", "").lower() not in {"true", "false"}:
            errors.append(f"row {index}: corrected must be true or false")
    return errors


def aggregate_csv(path: str | Path) -> dict:
    """Read experiment_log.csv and return reproducible summary statistics."""
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    errors = validate_experiment_rows(rows)
    if errors:
        raise ValueError("invalid experiment log: " + "; ".join(errors))

    results = Counter(row["result"] for row in rows)
    assigned = [row for row in rows if row.get("predicted_work_item_id")]
    corrections = sum(row.get("corrected", "").lower() == "true" for row in rows)
    false_positive = sum(row["result"] == "STOP" for row in rows)
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
            / len(assigned)
            if assigned else 0.0
        ),
    }

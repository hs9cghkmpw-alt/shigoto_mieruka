"""Aggregate deterministic association experiment results."""

import csv
from collections import Counter
from pathlib import Path


def classify_result(*, predicted: str | None, expected: str | None, confidence: float, minimum_confidence: float = 0.60) -> str:
    """Classify an experiment as GO, GRAY, or STOP.

    STOP is reserved for a confident wrong assignment. GRAY covers
    unassigned/low-confidence cases, which are safer than false association.
    """
    if predicted and expected and predicted != expected and confidence >= minimum_confidence:
        return "STOP"
    if predicted == expected and predicted and confidence >= minimum_confidence:
        return "GO"
    return "GRAY"


def aggregate_csv(path: str | Path) -> dict:
    """Read experiment_log.csv and return reproducible summary statistics."""
    rows = list(csv.DictReader(Path(path).open(newline="", encoding="utf-8")))
    results = Counter(row["result"] for row in rows)
    corrections = sum(row.get("corrected", "").lower() == "true" for row in rows)
    return {
        "total": len(rows),
        "go": results["GO"],
        "gray": results["GRAY"],
        "stop": results["STOP"],
        "corrections": corrections,
        "accuracy_on_assigned": (
            sum(row.get("predicted_work_item_id") == row.get("expected_work_item_id")
                for row in rows if row.get("predicted_work_item_id"))
            / sum(bool(row.get("predicted_work_item_id")) for row in rows)
            if any(row.get("predicted_work_item_id") for row in rows) else 0.0
        ),
    }

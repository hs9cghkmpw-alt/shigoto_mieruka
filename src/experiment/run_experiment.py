"""Run the minimal association experiment and emit experiment_log.csv."""

import csv
from pathlib import Path

from association.scorer import Candidate, choose_assignment, score_candidate
from experiment.fixtures import FIXTURES


def run(output: str | Path = "experiment_log.csv") -> None:
    rows = []
    for fixture in FIXTURES:
        score = score_candidate(**fixture["signals"])
        predicted = choose_assignment(
            [Candidate("WI-001", score, tuple(fixture["signals"]))]
        )
        predicted_id = predicted.work_item_id if predicted else ""
        result = "GO" if predicted_id == fixture["expected_work_item_id"] and predicted_id else "GRAY"
        rows.append({
            "experiment_id": fixture["experiment_id"],
            "pattern": fixture["pattern"],
            "trace_id": fixture["trace_id"],
            "expected_work_item_id": fixture["expected_work_item_id"],
            "predicted_work_item_id": predicted_id,
            "confidence": f"{score:.2f}",
            "assignment_status": "provisional" if predicted_id else "unassigned",
            "corrected": "false",
            "result": result,
            "notes": "fixture",
        })

    fieldnames = list(rows[0])
    with Path(output).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    run()

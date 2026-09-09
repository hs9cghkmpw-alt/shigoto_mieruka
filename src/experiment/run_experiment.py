"""Run deterministic association fixtures and emit an experiment log."""

import csv
from pathlib import Path

from association.scorer import Candidate, choose_assignment, score_candidate
from experiment.aggregator import classify_result
from experiment.fixtures import FIXTURES


def run(output: str | Path = "experiment_log.csv") -> None:
    rows = []
    for fixture in FIXTURES:
        score = score_candidate(**fixture["signals"])
        candidates = [Candidate(fixture["expected_work_item_id"], score, tuple(fixture["signals"]))]
        candidates.extend(
            Candidate(work_item_id, candidate_score, ("fixture_candidate",))
            for work_item_id, candidate_score in fixture["candidates"]
        )
        predicted = choose_assignment(candidates)
        predicted_id = predicted.work_item_id if predicted else ""
        predicted_confidence = predicted.score if predicted else 0.0
        result = classify_result(
            predicted=predicted_id or None,
            expected=fixture["expected_work_item_id"],
            confidence=predicted_confidence,
        )
        rows.append({
            "experiment_id": fixture["experiment_id"],
            "pattern": fixture["pattern"],
            "trace_id": fixture["trace_id"],
            "expected_work_item_id": fixture["expected_work_item_id"],
            "predicted_work_item_id": predicted_id,
            "confidence": f"{predicted_confidence:.2f}",
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

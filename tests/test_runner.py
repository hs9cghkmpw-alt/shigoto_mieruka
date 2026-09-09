import csv

from experiment.run_experiment import run


def test_runner_produces_go_gray_and_stop(tmp_path):
    output = tmp_path / "experiment_log.csv"
    run(output)
    rows = list(csv.DictReader(output.open(newline="", encoding="utf-8")))
    results = {row["result"] for row in rows}
    assert {"GO", "GRAY", "STOP"} <= results
    assert len(rows) >= 10

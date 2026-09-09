from experiment.aggregator import aggregate_csv
from experiment.run_experiment import run


def test_aggregate_matches_experiment_outcomes(tmp_path):
    output = tmp_path / "experiment_log.csv"
    run(output)
    summary = aggregate_csv(output)

    assert summary["total"] == 12
    assert summary["go"] >= 1
    assert summary["gray"] >= 1
    assert summary["stop"] == 1
    assert summary["corrections"] == 0
    assert 0.0 <= summary["accuracy_on_assigned"] <= 1.0

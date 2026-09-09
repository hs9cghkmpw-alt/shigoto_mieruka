"""Evaluation metrics for conservative assignment experiments."""


def binary_metrics(rows, *, threshold=0.60):
    """Return abstention-aware metrics; no claim of statistical calibration."""
    assigned = [r for r in rows if r.get("predicted_work_item_id")]
    correct = [r for r in assigned if r.get("predicted_work_item_id") == r.get("expected_work_item_id")]
    high_conf = [r for r in assigned if float(r.get("confidence", 0)) >= threshold]
    return {
        "n": len(rows),
        "assigned": len(assigned),
        "abstained": len(rows) - len(assigned),
        "coverage": len(assigned) / len(rows) if rows else 0.0,
        "selective_accuracy": len(correct) / len(assigned) if assigned else 0.0,
        "high_conf_count": len(high_conf),
        "high_conf_accuracy": (
            sum(r.get("predicted_work_item_id") == r.get("expected_work_item_id") for r in high_conf) / len(high_conf)
            if high_conf else 0.0
        ),
    }


def calibration_bins(rows, bins=10):
    """Reliability data only; requires real labeled rows for interpretation."""
    result=[]
    for i in range(bins):
        lo=i/bins; hi=(i+1)/bins
        bucket=[r for r in rows if lo <= float(r.get("confidence",0)) < (hi if i < bins-1 else hi+1e-12)]
        if bucket:
            result.append({"lower":lo,"upper":hi,"n":len(bucket),"mean_confidence":sum(float(r["confidence"]) for r in bucket)/len(bucket),"empirical_accuracy":sum(r.get("predicted_work_item_id")==r.get("expected_work_item_id") for r in bucket)/len(bucket)})
    return result

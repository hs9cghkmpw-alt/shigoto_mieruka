"""Minimal deterministic fixtures for association experiments."""

FIXTURES = [
    {
        "experiment_id": "EXP-001",
        "pattern": "電話",
        "trace_id": "TRACE-001",
        "expected_work_item_id": "WI-001",
        "signals": {"participant_match": True, "project_match": True, "time_proximity": True},
    },
    {
        "experiment_id": "EXP-002",
        "pattern": "メール",
        "trace_id": "TRACE-002",
        "expected_work_item_id": "WI-001",
        "signals": {"thread_match": True, "participant_match": True},
    },
    {
        "experiment_id": "EXP-003",
        "pattern": "文書閲覧",
        "trace_id": "TRACE-003",
        "expected_work_item_id": "WI-002",
        "signals": {"document_match": True, "project_match": True},
    },
    {
        "experiment_id": "EXP-004",
        "pattern": "Web調査",
        "trace_id": "TRACE-004",
        "expected_work_item_id": "WI-002",
        "signals": {"keyword_match": True, "recent_active": True},
    },
    {
        "experiment_id": "EXP-005",
        "pattern": "他者依頼",
        "trace_id": "TRACE-005",
        "expected_work_item_id": "WI-003",
        "signals": {"participant_match": True, "keyword_match": True, "project_match": True},
    },
    {
        "experiment_id": "EXP-006",
        "pattern": "割り込み",
        "trace_id": "TRACE-006",
        "expected_work_item_id": "WI-003",
        "signals": {"time_proximity": True},
    },
    {
        "experiment_id": "EXP-007",
        "pattern": "並行案件",
        "trace_id": "TRACE-007",
        "expected_work_item_id": "WI-004",
        "signals": {"thread_match": True, "project_match": True, "keyword_match": True},
    },
    {
        "experiment_id": "EXP-008",
        "pattern": "完了フォロー",
        "trace_id": "TRACE-008",
        "expected_work_item_id": "WI-004",
        "signals": {"thread_match": True, "recent_active": True},
    },
    {
        "experiment_id": "EXP-009",
        "pattern": "複数日",
        "trace_id": "TRACE-009",
        "expected_work_item_id": "WI-005",
        "signals": {"project_match": True, "recent_active": True, "keyword_match": True},
    },
]

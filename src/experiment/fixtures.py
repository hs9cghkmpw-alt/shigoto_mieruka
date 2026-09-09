"""Deterministic fixtures covering normal, ambiguous, and unsafe outcomes."""

FIXTURES = [
    {"experiment_id": "EXP-001", "pattern": "強い文脈", "trace_id": "TRACE-001", "expected_work_item_id": "WI-001", "signals": {"thread_match": True, "document_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-002", "pattern": "複数一致", "trace_id": "TRACE-002", "expected_work_item_id": "WI-001", "signals": {"thread_match": True, "document_match": True, "participant_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-003", "pattern": "文書・案件", "trace_id": "TRACE-003", "expected_work_item_id": "WI-002", "signals": {"thread_match": True, "document_match": True, "project_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-004", "pattern": "弱信号", "trace_id": "TRACE-004", "expected_work_item_id": "WI-002", "signals": {"keyword_match": True, "recent_active": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-005", "pattern": "他者依頼", "trace_id": "TRACE-005", "expected_work_item_id": "WI-003", "signals": {"thread_match": True, "participant_match": True, "project_match": True, "keyword_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-006", "pattern": "割り込み", "trace_id": "TRACE-006", "expected_work_item_id": "WI-003", "signals": {"time_proximity": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-007", "pattern": "並行案件", "trace_id": "TRACE-007", "expected_work_item_id": "WI-004", "signals": {"thread_match": True, "document_match": True, "project_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-008", "pattern": "完了フォロー", "trace_id": "TRACE-008", "expected_work_item_id": "WI-004", "signals": {"thread_match": True, "document_match": True, "recent_active": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-009", "pattern": "複数日", "trace_id": "TRACE-009", "expected_work_item_id": "WI-005", "signals": {"thread_match": True, "project_match": True, "recent_active": True, "keyword_match": True}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-010", "pattern": "信号なし", "trace_id": "TRACE-010", "expected_work_item_id": "WI-005", "signals": {}, "candidates": [("DISTRACTOR", 0.20)]},
    {"experiment_id": "EXP-011", "pattern": "同点候補", "trace_id": "TRACE-011", "expected_work_item_id": "WI-001", "signals": {"thread_match": True, "document_match": True}, "candidates": [("WI-002", 0.60)]},
    {"experiment_id": "EXP-012", "pattern": "高信頼誤紐付け", "trace_id": "TRACE-012", "expected_work_item_id": "WI-001", "signals": {"thread_match": True, "document_match": True}, "candidates": [("WI-002", 0.70)]},
]

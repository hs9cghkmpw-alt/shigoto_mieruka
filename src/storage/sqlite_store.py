"""Small local SQLite persistence layer for WorkItem/WorkTrace evidence metadata."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from domain.models import WorkItem, WorkTrace


class TraceStore:
    """Durable local store; raw source content is intentionally not persisted."""

    def __init__(self, path: str | Path = ":memory:") -> None:
        self.connection = sqlite3.connect(str(path))
        self.connection.row_factory = sqlite3.Row
        self._create_schema()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS work_items (
                work_item_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                project_id TEXT,
                deadline TEXT,
                confidentiality_level TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS work_traces (
                trace_id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                work_item_id TEXT,
                predicted_work_item_id TEXT,
                prediction_confidence REAL,
                assignment_status TEXT NOT NULL,
                started_at TEXT,
                ended_at TEXT,
                duration_seconds INTEGER,
                source TEXT,
                content_reference TEXT,
                security_classification TEXT NOT NULL,
                provenance TEXT,
                confidence REAL,
                evidence_ids TEXT NOT NULL,
                extractor_version TEXT,
                metadata TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def save_work_item(self, item: WorkItem) -> None:
        self.connection.execute(
            """INSERT OR REPLACE INTO work_items VALUES (?,?,?,?,?,?,?,?)""",
            (
                item.work_item_id, item.title, item.status,
                _dt(item.started_at), _dt(item.completed_at), item.project_id,
                _dt(item.deadline), item.confidentiality_level.value,
            ),
        )
        self.connection.commit()

    def save_trace(self, trace: WorkTrace) -> None:
        self.connection.execute(
            """INSERT OR REPLACE INTO work_traces VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                trace.trace_id, trace.event_type, trace.occurred_at.isoformat(),
                trace.work_item_id, trace.predicted_work_item_id, trace.prediction_confidence,
                trace.assignment_status.value, _dt(trace.started_at), _dt(trace.ended_at),
                trace.duration_seconds, trace.source, trace.content_reference,
                trace.security_classification.value,
                trace.provenance.value if trace.provenance else None,
                trace.confidence, json.dumps(trace.evidence_ids, ensure_ascii=False),
                trace.extractor_version, json.dumps(trace.metadata, ensure_ascii=False, sort_keys=True),
            ),
        )
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None

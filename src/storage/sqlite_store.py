"""Small, dependency-free SQLite repository with explicit provenance boundaries."""

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from domain.models import EvidenceRef, WorkItem, WorkTrace


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class SQLiteStore:
    """Durable local store; raw source content is intentionally not persisted."""

    def __init__(self, path: str | Path = "work_memory.sqlite3") -> None:
        self.path = str(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _init_schema(self) -> None:
        self.conn.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS work_items (
            work_item_id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT NOT NULL,
            started_at TEXT, completed_at TEXT, project_id TEXT, deadline TEXT,
            confidentiality_level TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id TEXT PRIMARY KEY, source_type TEXT NOT NULL, source_id TEXT NOT NULL,
            observed_at TEXT NOT NULL, captured_at TEXT NOT NULL, content_hash TEXT NOT NULL,
            extractor_version TEXT NOT NULL, security_classification TEXT NOT NULL,
            provenance TEXT NOT NULL, payload_digest TEXT NOT NULL, status TEXT NOT NULL,
            expires_at TEXT, retention_policy TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS work_traces (
            trace_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, occurred_at TEXT NOT NULL,
            work_item_id TEXT, predicted_work_item_id TEXT, prediction_confidence REAL,
            assignment_status TEXT NOT NULL, started_at TEXT, ended_at TEXT,
            duration_seconds INTEGER, source TEXT, content_reference TEXT,
            security_classification TEXT NOT NULL, provenance TEXT, confidence REAL,
            evidence_ids_json TEXT NOT NULL, extractor_version TEXT, metadata_json TEXT NOT NULL,
            FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
        );
        CREATE TABLE IF NOT EXISTS assignment_corrections (
            correction_id TEXT PRIMARY KEY, trace_id TEXT NOT NULL,
            previous_work_item_id TEXT, corrected_work_item_id TEXT, corrected_at TEXT NOT NULL,
            corrected_by TEXT NOT NULL, reason TEXT, evidence_ids_json TEXT NOT NULL,
            client_version TEXT, FOREIGN KEY(trace_id) REFERENCES work_traces(trace_id)
        );
        CREATE TABLE IF NOT EXISTS audit_events (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL,
            actor TEXT NOT NULL, action TEXT NOT NULL, entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL, details_json TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_evidence_source ON evidence(source_type, source_id);
        CREATE INDEX IF NOT EXISTS idx_trace_occurred ON work_traces(occurred_at);
        CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_events(entity_type, entity_id);
        """)
        self.conn.commit()

    def save_work_item(self, item: WorkItem) -> None:
        self.conn.execute("""INSERT OR REPLACE INTO work_items VALUES (?,?,?,?,?,?,?,?)""", (
            item.work_item_id, item.title, item.status, _dt(item.started_at), _dt(item.completed_at),
            item.project_id, _dt(item.deadline), item.confidentiality_level.value))
        self.conn.commit()

    def save_evidence(self, observed) -> None:
        e = observed.evidence
        self.conn.execute("""INSERT OR REPLACE INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            e.evidence_id, e.source_type, e.source_id, _dt(e.observed_at), _dt(e.captured_at),
            e.content_hash, e.extractor_version, e.security_classification.value, e.provenance.value,
            observed.payload_digest, observed.status.value, _dt(observed.expires_at), observed.retention_policy))
        self.conn.commit()

    def save_trace(self, trace: WorkTrace) -> None:
        self.conn.execute("""INSERT OR REPLACE INTO work_traces VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
            trace.trace_id, trace.event_type, _dt(trace.occurred_at), trace.work_item_id,
            trace.predicted_work_item_id, trace.prediction_confidence, trace.assignment_status.value,
            _dt(trace.started_at), _dt(trace.ended_at), trace.duration_seconds, trace.source,
            trace.content_reference, trace.security_classification.value,
            trace.provenance.value if trace.provenance else None, trace.confidence,
            json.dumps(trace.evidence_ids), trace.extractor_version, json.dumps(trace.metadata, sort_keys=True)))
        self.conn.commit()

    def audit(self, *, actor: str, action: str, entity_type: str, entity_id: str, details: dict | None = None, at: datetime | None = None) -> None:
        if not actor.strip(): raise ValueError("actor is required")
        self.conn.execute("INSERT INTO audit_events(occurred_at,actor,action,entity_type,entity_id,details_json) VALUES (?,?,?,?,?,?)",
                          (_dt(at or datetime.now().astimezone()), actor, action, entity_type, entity_id, json.dumps(details or {}, sort_keys=True)))
        self.conn.commit()

    def count(self, table: str) -> int:
        if table not in {"work_items", "evidence", "work_traces", "assignment_corrections", "audit_events"}:
            raise ValueError("invalid table")
        return int(self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

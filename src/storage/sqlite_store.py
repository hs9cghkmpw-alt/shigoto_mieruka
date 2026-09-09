"""Transactional SQLite persistence with validation and audit boundaries."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from domain.models import AssignmentCorrection, WorkItem, WorkTrace
from domain.validation import validate_work_item, validate_work_trace


def _dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


class SQLiteStore:
    """Local durable store. Raw source payloads are never written here."""

    def __init__(self, path: str | Path = "work_memory.sqlite3") -> None:
        self.path = str(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.conn = self.connection
        self._init_schema()

    def close(self): self.connection.close()
    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb): self.close()

    @contextmanager
    def transaction(self):
        try:
            self.connection.execute("BEGIN")
            yield
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def _init_schema(self):
        self.connection.executescript("""
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
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
            expires_at TEXT, retention_policy TEXT NOT NULL,
            UNIQUE(source_type, source_id, content_hash), UNIQUE(content_hash)
        );
        CREATE TABLE IF NOT EXISTS work_traces (
            trace_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, occurred_at TEXT NOT NULL,
            work_item_id TEXT, predicted_work_item_id TEXT, prediction_confidence REAL,
            assignment_status TEXT NOT NULL, started_at TEXT, ended_at TEXT,
            duration_seconds INTEGER, source TEXT, content_reference TEXT,
            security_classification TEXT NOT NULL, provenance TEXT, confidence REAL,
            evidence_ids TEXT NOT NULL, extractor_version TEXT, metadata_json TEXT NOT NULL,
            FOREIGN KEY(work_item_id) REFERENCES work_items(work_item_id)
        );
        CREATE TABLE IF NOT EXISTS assignment_corrections (
            correction_id TEXT PRIMARY KEY, trace_id TEXT NOT NULL,
            previous_work_item_id TEXT, corrected_work_item_id TEXT, corrected_at TEXT NOT NULL,
            corrected_by TEXT NOT NULL, reason TEXT, evidence_ids TEXT NOT NULL,
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
        INSERT OR IGNORE INTO schema_meta(key,value) VALUES ('schema_version','1');
        """)
        self.connection.commit()

    def save_work_item(self, item: WorkItem) -> None:
        errors = validate_work_item(item)
        if errors: raise ValueError("invalid work item: " + "; ".join(errors))
        self.connection.execute("INSERT INTO work_items VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(work_item_id) DO UPDATE SET title=excluded.title,status=excluded.status,started_at=excluded.started_at,completed_at=excluded.completed_at,project_id=excluded.project_id,deadline=excluded.deadline,confidentiality_level=excluded.confidentiality_level", (item.work_item_id,item.title,item.status,_dt(item.started_at),_dt(item.completed_at),item.project_id,_dt(item.deadline),item.confidentiality_level.value))
        self.connection.commit()

    def save_evidence(self, observed) -> None:
        e = observed.evidence
        try:
            self.connection.execute("INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (e.evidence_id,e.source_type,e.source_id,_dt(e.observed_at),_dt(e.captured_at),e.content_hash,e.extractor_version,e.security_classification.value,e.provenance.value,observed.payload_digest,observed.status.value,_dt(observed.expires_at),observed.retention_policy))
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            self.connection.rollback()
            raise ValueError("duplicate evidence identity/content") from exc

    def save_trace(self, trace: WorkTrace) -> None:
        if trace.work_item_id:
            row = self.connection.execute("SELECT confidentiality_level FROM work_items WHERE work_item_id=?", (trace.work_item_id,)).fetchone()
            if row is None: raise ValueError("work_item_id does not exist")
        errors = validate_work_trace(trace)
        if errors: raise ValueError("invalid work trace: " + "; ".join(errors))
        self.connection.execute("INSERT INTO work_traces VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(trace_id) DO UPDATE SET event_type=excluded.event_type,occurred_at=excluded.occurred_at,work_item_id=excluded.work_item_id,predicted_work_item_id=excluded.predicted_work_item_id,prediction_confidence=excluded.prediction_confidence,assignment_status=excluded.assignment_status,started_at=excluded.started_at,ended_at=excluded.ended_at,duration_seconds=excluded.duration_seconds,source=excluded.source,content_reference=excluded.content_reference,security_classification=excluded.security_classification,provenance=excluded.provenance,confidence=excluded.confidence,evidence_ids=excluded.evidence_ids,extractor_version=excluded.extractor_version,metadata_json=excluded.metadata_json", (trace.trace_id,trace.event_type,_dt(trace.occurred_at),trace.work_item_id,trace.predicted_work_item_id,trace.prediction_confidence,trace.assignment_status.value,_dt(trace.started_at),_dt(trace.ended_at),trace.duration_seconds,trace.source,trace.content_reference,trace.security_classification.value,trace.provenance.value if trace.provenance else None,trace.confidence,json.dumps(trace.evidence_ids),trace.extractor_version,json.dumps(trace.metadata,sort_keys=True)))
        self.connection.commit()

    def save_correction(self, correction: AssignmentCorrection) -> None:
        if not correction.trace_id.strip() or not correction.corrected_by.strip(): raise ValueError("trace_id and corrected_by are required")
        with self.transaction():
            self.connection.execute("INSERT INTO assignment_corrections VALUES (?,?,?,?,?,?,?,?,?)", (correction.correction_id,correction.trace_id,correction.previous_work_item_id,correction.corrected_work_item_id,_dt(correction.corrected_at),correction.corrected_by,correction.reason,json.dumps(list(correction.evidence_ids)),correction.client_version))
            self.connection.execute("INSERT INTO audit_events(occurred_at,actor,action,entity_type,entity_id,details_json) VALUES (?,?,?,?,?,?)", (_dt(correction.corrected_at),correction.corrected_by,"assignment_correction","work_trace",correction.trace_id,json.dumps({"correction_id":correction.correction_id,"previous":correction.previous_work_item_id,"corrected":correction.corrected_work_item_id,"reason":correction.reason},sort_keys=True)))

    def audit(self, *, actor: str, action: str, entity_type: str, entity_id: str, details: dict | None = None, at: datetime | None = None):
        if not actor.strip(): raise ValueError("actor is required")
        self.connection.execute("INSERT INTO audit_events(occurred_at,actor,action,entity_type,entity_id,details_json) VALUES (?,?,?,?,?,?)", (_dt(at or datetime.now().astimezone()),actor,action,entity_type,entity_id,json.dumps(details or {},sort_keys=True)))
        self.connection.commit()

    def get_work_item(self, work_item_id: str): return self.connection.execute("SELECT * FROM work_items WHERE work_item_id=?",(work_item_id,)).fetchone()
    def get_trace(self, trace_id: str): return self.connection.execute("SELECT * FROM work_traces WHERE trace_id=?",(trace_id,)).fetchone()
    def list_traces(self, limit: int = 100): return self.connection.execute("SELECT * FROM work_traces ORDER BY occurred_at DESC LIMIT ?",(limit,)).fetchall()
    def list_corrections(self, trace_id: str): return self.connection.execute("SELECT * FROM assignment_corrections WHERE trace_id=? ORDER BY corrected_at",(trace_id,)).fetchall()
    def list_audit(self, entity_type: str, entity_id: str): return self.connection.execute("SELECT * FROM audit_events WHERE entity_type=? AND entity_id=? ORDER BY audit_id",(entity_type,entity_id)).fetchall()
    def count(self, table: str) -> int:
        allowed={"work_items","evidence","work_traces","assignment_corrections","audit_events","facts","analyses","knowledge","capability_hypotheses","knowledge_status_history"}
        if table not in allowed: raise ValueError("invalid table")
        return int(self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


TraceStore = SQLiteStore

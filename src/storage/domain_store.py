"""Typed persistence facade for the complete domain lifecycle."""

from datetime import datetime
from storage.sqlite_store import SQLiteStore


class DomainStore(SQLiteStore):
    """SQLiteStore extension for Fact/Analysis/Knowledge/Capability persistence."""

    def _init_schema(self):
        super()._init_schema()
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS facts (
            fact_id TEXT PRIMARY KEY, source_trace_ids TEXT NOT NULL, statement TEXT NOT NULL,
            provenance TEXT NOT NULL, security_classification TEXT NOT NULL, conflict_status TEXT
        );
        CREATE TABLE IF NOT EXISTS analyses (
            analysis_id TEXT PRIMARY KEY, source_fact_ids TEXT NOT NULL, analysis_type TEXT NOT NULL,
            hypothesis TEXT NOT NULL, confidence REAL NOT NULL, model TEXT, status TEXT NOT NULL,
            created_by TEXT, created_at TEXT, method_version TEXT, input_method TEXT
        );
        CREATE TABLE IF NOT EXISTS knowledge (
            knowledge_id TEXT PRIMARY KEY, source_fact_ids TEXT NOT NULL, source_analysis_ids TEXT NOT NULL,
            statement TEXT NOT NULL, evidence_count INTEGER NOT NULL, validation_status TEXT NOT NULL,
            validated_by TEXT, validated_at TEXT, valid_until TEXT, security_classification TEXT NOT NULL,
            evidence_diversity INTEGER NOT NULL, superseded_by TEXT, status_changed_at TEXT,
            status_changed_by TEXT
        );
        CREATE TABLE IF NOT EXISTS capability_hypotheses (
            hypothesis_id TEXT PRIMARY KEY, work_item_type TEXT NOT NULL, context_json TEXT NOT NULL,
            observed_outcome TEXT NOT NULL, source_trace_ids TEXT NOT NULL, source_fact_ids TEXT NOT NULL,
            confidence REAL, reviewed_by TEXT, reviewed_at TEXT, status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS knowledge_status_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT, knowledge_id TEXT NOT NULL,
            from_status TEXT, to_status TEXT NOT NULL, changed_at TEXT NOT NULL, changed_by TEXT NOT NULL,
            reason TEXT, FOREIGN KEY(knowledge_id) REFERENCES knowledge(knowledge_id)
        );
        """)
        self.connection.commit()

    @staticmethod
    def _json(values):
        import json
        return json.dumps(values, ensure_ascii=False, sort_keys=True)

    def save_fact(self, fact):
        if not fact.fact_id.strip() or not fact.statement.strip() or not fact.source_trace_ids:
            raise ValueError("invalid fact")
        self.connection.execute("INSERT INTO facts VALUES (?,?,?,?,?,?) ON CONFLICT(fact_id) DO UPDATE SET source_trace_ids=excluded.source_trace_ids,statement=excluded.statement,provenance=excluded.provenance,security_classification=excluded.security_classification,conflict_status=excluded.conflict_status", (fact.fact_id,self._json(fact.source_trace_ids),fact.statement,fact.provenance.value,fact.security_classification.value,fact.conflict_status))
        self.connection.commit()

    def save_analysis(self, analysis):
        if not analysis.analysis_id.strip() or not analysis.source_fact_ids or not analysis.hypothesis.strip():
            raise ValueError("invalid analysis")
        if not 0 <= analysis.confidence <= 1:
            raise ValueError("analysis confidence must be between 0 and 1")
        self.connection.execute("INSERT INTO analyses VALUES (?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(analysis_id) DO UPDATE SET source_fact_ids=excluded.source_fact_ids,analysis_type=excluded.analysis_type,hypothesis=excluded.hypothesis,confidence=excluded.confidence,model=excluded.model,status=excluded.status,created_by=excluded.created_by,created_at=excluded.created_at,method_version=excluded.method_version,input_method=excluded.input_method", (analysis.analysis_id,self._json(analysis.source_fact_ids),analysis.analysis_type,analysis.hypothesis,analysis.confidence,analysis.model,analysis.status,analysis.created_by,analysis.created_at.isoformat() if analysis.created_at else None,analysis.method_version,analysis.input_method))
        self.connection.commit()

    def save_knowledge(self, knowledge, *, actor: str, reason: str = ""):
        if not actor.strip():
            raise ValueError("actor is required")
        if not knowledge.knowledge_id.strip() or not knowledge.source_fact_ids or not knowledge.source_analysis_ids or not knowledge.statement.strip():
            raise ValueError("invalid knowledge")
        if knowledge.validation_status == "validated" and (not knowledge.validated_by or not knowledge.validated_at):
            raise ValueError("validated knowledge requires validator and validation time")
        self.connection.execute("BEGIN")
        try:
            old = self.connection.execute("SELECT validation_status FROM knowledge WHERE knowledge_id=?", (knowledge.knowledge_id,)).fetchone()
            values = (knowledge.knowledge_id,self._json(knowledge.source_fact_ids),self._json(knowledge.source_analysis_ids),knowledge.statement,knowledge.evidence_count,knowledge.validation_status,knowledge.validated_by,knowledge.validated_at.isoformat() if knowledge.validated_at else None,knowledge.valid_until.isoformat() if knowledge.valid_until else None,knowledge.security_classification.value,knowledge.evidence_diversity,knowledge.superseded_by,knowledge.status_changed_at.isoformat() if knowledge.status_changed_at else None,knowledge.status_changed_by)
            self.connection.execute("INSERT INTO knowledge(knowledge_id,source_fact_ids,source_analysis_ids,statement,evidence_count,validation_status,validated_by,validated_at,valid_until,security_classification,evidence_diversity,superseded_by,status_changed_at,status_changed_by) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(knowledge_id) DO UPDATE SET source_fact_ids=excluded.source_fact_ids,source_analysis_ids=excluded.source_analysis_ids,statement=excluded.statement,evidence_count=excluded.evidence_count,validation_status=excluded.validation_status,validated_by=excluded.validated_by,validated_at=excluded.validated_at,valid_until=excluded.valid_until,security_classification=excluded.security_classification,evidence_diversity=excluded.evidence_diversity,superseded_by=excluded.superseded_by,status_changed_at=excluded.status_changed_at,status_changed_by=excluded.status_changed_by", values)
            if old is None or old[0] != knowledge.validation_status:
                self.connection.execute("INSERT INTO knowledge_status_history(knowledge_id,from_status,to_status,changed_at,changed_by,reason) VALUES (?,?,?,?,?,?)", (knowledge.knowledge_id,old[0] if old else None,knowledge.validation_status,datetime.now().astimezone().isoformat(),actor,reason))
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def save_capability_hypothesis(self, hypothesis):
        if not hypothesis.hypothesis_id.strip() or not hypothesis.work_item_type.strip() or not hypothesis.observed_outcome.strip() or not hypothesis.source_trace_ids:
            raise ValueError("invalid capability hypothesis")
        if hypothesis.confidence is not None and not 0 <= hypothesis.confidence <= 1:
            raise ValueError("capability confidence must be between 0 and 1")
        self.connection.execute("INSERT INTO capability_hypotheses VALUES (?,?,?,?,?,?,?,?,?,?) ON CONFLICT(hypothesis_id) DO UPDATE SET work_item_type=excluded.work_item_type,context_json=excluded.context_json,observed_outcome=excluded.observed_outcome,source_trace_ids=excluded.source_trace_ids,source_fact_ids=excluded.source_fact_ids,confidence=excluded.confidence,reviewed_by=excluded.reviewed_by,reviewed_at=excluded.reviewed_at,status=excluded.status", (hypothesis.hypothesis_id,hypothesis.work_item_type,self._json(hypothesis.context),hypothesis.observed_outcome,self._json(hypothesis.source_trace_ids),self._json(hypothesis.source_fact_ids),hypothesis.confidence,hypothesis.reviewed_by,hypothesis.reviewed_at.isoformat() if hypothesis.reviewed_at else None,hypothesis.status))
        self.connection.commit()

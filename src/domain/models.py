"""Domain models for Work Memory / Work Trace.

The model keeps source evidence, observations, predictions, human decisions,
and capability hypotheses separate so inference cannot silently become fact.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class SecurityClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class Provenance(str, Enum):
    OBSERVED = "observed"
    REPORTED = "reported"


class AssignmentStatus(str, Enum):
    UNASSIGNED = "unassigned"
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"


class KnowledgeStatus(str, Enum):
    CANDIDATE = "candidate"
    VALIDATED = "validated"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"
    REJECTED = "rejected"


@dataclass(frozen=True)
class EvidenceRef:
    evidence_id: str
    source_type: str
    source_id: str
    observed_at: datetime
    captured_at: datetime
    content_hash: str
    extractor_version: str
    security_classification: SecurityClassification = SecurityClassification.INTERNAL
    provenance: Provenance = Provenance.OBSERVED


@dataclass
class WorkItem:
    work_item_id: str
    title: str
    status: str = "open"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    project_id: Optional[str] = None
    deadline: Optional[datetime] = None
    confidentiality_level: SecurityClassification = SecurityClassification.INTERNAL


@dataclass
class WorkTrace:
    trace_id: str
    event_type: str
    occurred_at: datetime
    work_item_id: Optional[str] = None
    predicted_work_item_id: Optional[str] = None
    prediction_confidence: Optional[float] = None
    assignment_status: AssignmentStatus = AssignmentStatus.UNASSIGNED
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    source: Optional[str] = None
    content_reference: Optional[str] = None
    security_classification: SecurityClassification = SecurityClassification.INTERNAL
    provenance: Optional[Provenance] = None
    confidence: Optional[float] = None
    evidence_ids: list[str] = field(default_factory=list)
    extractor_version: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AssignmentCorrection:
    correction_id: str
    trace_id: str
    previous_work_item_id: Optional[str]
    corrected_work_item_id: Optional[str]
    corrected_at: datetime
    corrected_by: str
    reason: Optional[str] = None
    evidence_ids: tuple[str, ...] = ()
    client_version: Optional[str] = None


@dataclass
class Fact:
    fact_id: str
    source_trace_ids: list[str]
    statement: str
    provenance: Provenance
    security_classification: SecurityClassification = SecurityClassification.INTERNAL
    conflict_status: Optional[str] = None


@dataclass
class Analysis:
    analysis_id: str
    source_fact_ids: list[str]
    analysis_type: str
    hypothesis: str
    confidence: float
    model: Optional[str] = None
    status: str = "draft"
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    method_version: Optional[str] = None
    input_method: Optional[str] = None


@dataclass
class Knowledge:
    knowledge_id: str
    source_fact_ids: list[str]
    source_analysis_ids: list[str]
    statement: str
    evidence_count: int = 0
    validation_status: str = KnowledgeStatus.CANDIDATE.value
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    security_classification: SecurityClassification = SecurityClassification.INTERNAL
    evidence_diversity: int = 0
    superseded_by: Optional[str] = None
    status_changed_at: Optional[datetime] = None
    status_changed_by: Optional[str] = None


@dataclass(frozen=True)
class CapabilityHypothesis:
    """Context-conditioned hypothesis; never a factual ability score."""

    hypothesis_id: str
    work_item_type: str
    context: tuple[str, ...]
    observed_outcome: str
    source_trace_ids: tuple[str, ...]
    source_fact_ids: tuple[str, ...] = ()
    confidence: Optional[float] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    status: str = "candidate"


@dataclass
class Rework:
    rework_id: str
    work_item_id: str
    cause: Optional[str] = None
    source_trace_id: Optional[str] = None
    recovered_at: Optional[datetime] = None
    additional_duration_seconds: Optional[int] = None

"""Minimal domain models for Work Memory / Work Trace.

The models intentionally keep FACT, ANALYSIS and KNOWLEDGE separate.
They are implementation scaffolding, not the final persistence model.
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


@dataclass
class Knowledge:
    knowledge_id: str
    source_fact_ids: list[str]
    source_analysis_ids: list[str]
    statement: str
    evidence_count: int = 0
    validation_status: str = "candidate"
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    security_classification: SecurityClassification = SecurityClassification.INTERNAL


@dataclass
class Rework:
    rework_id: str
    work_item_id: str
    cause: Optional[str] = None
    source_trace_id: Optional[str] = None
    recovered_at: Optional[datetime] = None
    additional_duration_seconds: Optional[int] = None

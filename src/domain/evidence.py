"""Immutable evidence references and retention/integrity rules."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import hashlib

from domain.models import EvidenceRef, Provenance, SecurityClassification


class EvidenceStatus(str, Enum):
    ACTIVE = "active"
    RETAINED = "retained"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass(frozen=True)
class ObservedEvidence:
    evidence: EvidenceRef
    payload_digest: str
    status: EvidenceStatus = EvidenceStatus.ACTIVE
    expires_at: datetime | None = None
    retention_policy: str = "default"

    def is_usable_at(self, at: datetime) -> bool:
        return self.status in {EvidenceStatus.ACTIVE, EvidenceStatus.RETAINED} and (self.expires_at is None or at <= self.expires_at)


def content_hash(content: str | bytes) -> str:
    raw = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(raw).hexdigest()


def verify_content_hash(content: str | bytes, expected_hash: str) -> bool:
    """Verify source material against the immutable EvidenceRef hash."""
    return content_hash(content) == expected_hash


def make_evidence_ref(*, evidence_id: str, source_type: str, source_id: str, observed_at: datetime, captured_at: datetime, content: str | bytes, extractor_version: str, security_classification: SecurityClassification = SecurityClassification.INTERNAL, provenance: Provenance = Provenance.OBSERVED) -> EvidenceRef:
    if not evidence_id.strip() or not source_type.strip() or not source_id.strip(): raise ValueError("evidence identity is required")
    if captured_at < observed_at: raise ValueError("captured_at must not precede observed_at")
    return EvidenceRef(evidence_id, source_type, source_id, observed_at, captured_at, content_hash(content), extractor_version, security_classification, provenance)


def expire_evidence(evidence: ObservedEvidence, *, at: datetime) -> ObservedEvidence:
    if evidence.expires_at is None or at >= evidence.expires_at:
        return ObservedEvidence(evidence.evidence, evidence.payload_digest, EvidenceStatus.EXPIRED, evidence.expires_at, evidence.retention_policy)
    return evidence

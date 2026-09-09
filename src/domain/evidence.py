"""Evidence retention and retrieval primitives.

The default record stores a digest and metadata, not raw sensitive content.
A concrete source-specific connector may keep the original outside this store.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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
        return self.status in {EvidenceStatus.ACTIVE, EvidenceStatus.RETAINED} and (
            self.expires_at is None or at <= self.expires_at
        )


def content_hash(content: str | bytes) -> str:
    import hashlib
    raw = content.encode("utf-8") if isinstance(content, str) else content
    return hashlib.sha256(raw).hexdigest()


def make_evidence_ref(
    *,
    evidence_id: str,
    source_type: str,
    source_id: str,
    observed_at: datetime,
    captured_at: datetime,
    content: str | bytes,
    extractor_version: str,
    security_classification: SecurityClassification = SecurityClassification.INTERNAL,
    provenance: Provenance = Provenance.OBSERVED,
) -> EvidenceRef:
    return EvidenceRef(
        evidence_id=evidence_id,
        source_type=source_type,
        source_id=source_id,
        observed_at=observed_at,
        captured_at=captured_at,
        content_hash=content_hash(content),
        extractor_version=extractor_version,
        security_classification=security_classification,
        provenance=provenance,
    )


def expire_evidence(evidence: ObservedEvidence, *, at: datetime) -> ObservedEvidence:
    if evidence.expires_at is None or at >= evidence.expires_at:
        return ObservedEvidence(
            evidence=evidence.evidence,
            payload_digest=evidence.payload_digest,
            status=EvidenceStatus.EXPIRED,
            expires_at=evidence.expires_at,
            retention_policy=evidence.retention_policy,
        )
    return evidence

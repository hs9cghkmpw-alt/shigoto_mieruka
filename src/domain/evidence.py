"""Evidence helpers for auditable WorkTrace creation."""

from dataclasses import dataclass
from datetime import datetime
import hashlib

from domain.models import EvidenceRef, Provenance, SecurityClassification


@dataclass(frozen=True)
class ObservedEvidence:
    """Canonical source payload used before a WorkTrace is created."""

    evidence: EvidenceRef
    payload_digest: str


def content_hash(content: str) -> str:
    """Return a stable SHA-256 digest without storing source content here."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def make_evidence_ref(
    *,
    evidence_id: str,
    source_type: str,
    source_id: str,
    observed_at: datetime,
    captured_at: datetime,
    content: str,
    extractor_version: str,
    security_classification: SecurityClassification = SecurityClassification.INTERNAL,
    provenance: Provenance = Provenance.OBSERVED,
) -> EvidenceRef:
    """Create an immutable source reference; raw content is never returned."""
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

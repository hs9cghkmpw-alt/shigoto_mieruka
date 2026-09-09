from datetime import datetime, timezone

import pytest

from domain.evidence import make_evidence_ref
from domain.models import Provenance
from ingestion.trace_factory import trace_from_evidence


def test_ingestion_creates_observed_trace_without_assignment():
    now = datetime(2026, 9, 9, 9, tzinfo=timezone.utc)
    evidence = make_evidence_ref(
        evidence_id="E-1",
        source_type="email",
        source_id="MSG-1",
        observed_at=now,
        captured_at=now,
        content="本文",
        extractor_version="email-v1",
    )
    trace = trace_from_evidence(trace_id="T-1", event_type="email", evidence=evidence, occurred_at=now)
    assert trace.provenance is Provenance.OBSERVED
    assert trace.source == "email"
    assert trace.evidence_ids == ["E-1"]
    assert trace.work_item_id is None


def test_ingestion_rejects_reported_evidence():
    now = datetime(2026, 9, 9, 9, tzinfo=timezone.utc)
    evidence = make_evidence_ref(
        evidence_id="E-2",
        source_type="manual",
        source_id="R-1",
        observed_at=now,
        captured_at=now,
        content="reported",
        extractor_version="manual-v1",
        provenance=Provenance.REPORTED,
    )
    with pytest.raises(ValueError, match="observed evidence"):
        trace_from_evidence(trace_id="T-2", event_type="note", evidence=evidence, occurred_at=now)

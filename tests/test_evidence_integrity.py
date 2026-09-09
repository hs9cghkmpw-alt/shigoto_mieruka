from datetime import datetime, timezone, timedelta
import pytest
from domain.evidence import make_evidence_ref, verify_content_hash


def test_evidence_rejects_invalid_identity_and_time_order():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        make_evidence_ref(evidence_id="", source_type="mail", source_id="1", observed_at=now, captured_at=now, content="x", extractor_version="v1")
    with pytest.raises(ValueError):
        make_evidence_ref(evidence_id="E", source_type="mail", source_id="1", observed_at=now, captured_at=now-timedelta(seconds=1), content="x", extractor_version="v1")


def test_evidence_hash_verification():
    assert verify_content_hash("payload", make_evidence_ref(evidence_id="E", source_type="mail", source_id="1", observed_at=datetime.now(timezone.utc), captured_at=datetime.now(timezone.utc), content="payload", extractor_version="v1").content_hash)

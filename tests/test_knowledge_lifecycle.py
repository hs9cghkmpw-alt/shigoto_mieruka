from datetime import datetime, timezone

import pytest

from domain.knowledge_lifecycle import propose_knowledge, validate_knowledge
from domain.models import Analysis, Fact, Provenance, SecurityClassification


def sample_fact(level=SecurityClassification.CONFIDENTIAL):
    return Fact("F-1", ["T-1"], "observed statement", Provenance.OBSERVED, level)


def sample_analysis():
    return Analysis("A-1", ["F-1"], "pattern", "hypothesis", 0.8)


def test_knowledge_starts_as_candidate_and_inherits_security():
    knowledge = propose_knowledge(
        knowledge_id="K-1",
        statement="candidate",
        facts=[sample_fact()],
        analyses=[sample_analysis()],
        security_classification=SecurityClassification.PUBLIC,
    )
    assert knowledge.validation_status == "candidate"
    assert knowledge.security_classification is SecurityClassification.CONFIDENTIAL


def test_knowledge_requires_explicit_human_validation():
    knowledge = propose_knowledge(
        knowledge_id="K-1",
        statement="candidate",
        facts=[sample_fact()],
        analyses=[sample_analysis()],
    )
    now = datetime(2026, 9, 9, 9, tzinfo=timezone.utc)
    validate_knowledge(knowledge, validated_by="human", validated_at=now)
    assert knowledge.validation_status == "validated"
    assert knowledge.validated_by == "human"
    assert knowledge.validated_at == now


def test_invalid_analysis_cannot_create_knowledge():
    invalid = Analysis("A-1", [], "pattern", "hypothesis", 0.8)
    with pytest.raises(ValueError, match="invalid analysis"):
        propose_knowledge(
            knowledge_id="K-1",
            statement="candidate",
            facts=[sample_fact()],
            analyses=[invalid],
        )

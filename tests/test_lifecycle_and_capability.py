from datetime import datetime, timedelta, timezone

from domain.capability import propose_capability_hypothesis, review_capability_hypothesis
from domain.knowledge_lifecycle import expire_knowledge, propose_knowledge, reject_knowledge, supersede_knowledge, validate_knowledge
from domain.models import Analysis, Fact, KnowledgeStatus, Provenance


def _sources():
    now = datetime.now(timezone.utc)
    facts = [Fact("F1", ["T1"], "observed work", Provenance.OBSERVED), Fact("F2", ["T2"], "observed work", Provenance.OBSERVED)]
    analysis = Analysis("A1", ["F1", "F2"], "pattern", "hypothesis", 0.7, created_by="system", created_at=now, method_version="v1", input_method="rule")
    return now, facts, analysis


def test_knowledge_requires_human_gate_and_has_lifecycle():
    now, facts, analysis = _sources()
    k = propose_knowledge(knowledge_id="K1", statement="statement", facts=facts, analyses=[analysis])
    assert k.validation_status == KnowledgeStatus.CANDIDATE.value
    k.valid_until = now + timedelta(days=1)
    validate_knowledge(k, validated_by="human", validated_at=now)
    assert k.validation_status == KnowledgeStatus.VALIDATED.value
    supersede_knowledge(k, superseded_by="K2", at=now, changed_by="human")
    assert k.validation_status == KnowledgeStatus.SUPERSEDED.value


def test_candidate_can_be_rejected_and_capability_is_contextual():
    now, facts, analysis = _sources()
    k = propose_knowledge(knowledge_id="K2", statement="statement", facts=facts, analyses=[analysis])
    reject_knowledge(k, at=now, changed_by="human")
    assert k.validation_status == KnowledgeStatus.REJECTED.value
    h = propose_capability_hypothesis(hypothesis_id="H1", work_item_type="data entry", context=["quiet", "structured"], observed_outcome="completed", source_trace_ids=["T1"])
    assert h.status == "candidate"
    reviewed = review_capability_hypothesis(h, reviewed_by="human", reviewed_at=now, approved=True)
    assert reviewed.status == "validated"

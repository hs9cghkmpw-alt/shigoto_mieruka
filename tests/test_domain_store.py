from datetime import datetime, timezone

from domain.models import Analysis, CapabilityHypothesis, Fact, Knowledge, Provenance, SecurityClassification
from storage.domain_store import DomainStore


def test_complete_domain_persistence_and_knowledge_history(tmp_path):
    now = datetime.now(timezone.utc)
    with DomainStore(tmp_path / "domain.sqlite3") as store:
        fact = Fact("F1", ["T1"], "observed", Provenance.OBSERVED, SecurityClassification.CONFIDENTIAL)
        analysis = Analysis("A1", ["F1"], "pattern", "hypothesis", .8, created_by="human", created_at=now, method_version="v1", input_method="rule")
        knowledge = Knowledge("K1", ["F1"], ["A1"], "candidate", 1, security_classification=SecurityClassification.CONFIDENTIAL, evidence_diversity=1)
        capability = CapabilityHypothesis("C1", "document", ("quiet",), "completed", ("T1",), ("F1",))
        store.save_fact(fact)
        store.save_analysis(analysis)
        store.save_knowledge(knowledge, actor="human", reason="proposal")
        knowledge.validation_status = "validated"
        knowledge.validated_by = "human"
        knowledge.validated_at = now
        store.save_knowledge(knowledge, actor="human", reason="reviewed")
        store.save_capability_hypothesis(capability)
        assert store.count("facts") == 1
        assert store.count("analyses") == 1
        assert store.count("knowledge") == 1
        assert store.count("capability_hypotheses") == 1
        assert len(store.connection.execute("SELECT * FROM knowledge_status_history").fetchall()) == 2

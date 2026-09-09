"""Human-gated FACT -> ANALYSIS -> KNOWLEDGE lifecycle."""

from datetime import datetime

from domain.models import Analysis, Fact, Knowledge, KnowledgeStatus, SecurityClassification
from domain.security import inherit_security_classification


def validate_analysis(analysis: Analysis) -> list[str]:
    errors: list[str] = []
    if not analysis.analysis_id.strip(): errors.append("analysis_id is required")
    if not analysis.source_fact_ids: errors.append("analysis requires source facts")
    if not 0.0 <= analysis.confidence <= 1.0: errors.append("analysis confidence must be between 0 and 1")
    if not analysis.hypothesis.strip(): errors.append("analysis hypothesis is required")
    if analysis.created_by is None or not analysis.created_by.strip(): errors.append("analysis created_by is required")
    if analysis.created_at is None: errors.append("analysis created_at is required")
    if not analysis.method_version or not analysis.method_version.strip(): errors.append("analysis method_version is required")
    if not analysis.input_method or not analysis.input_method.strip(): errors.append("analysis input_method is required")
    return errors


def propose_knowledge(*, knowledge_id: str, statement: str, facts: list[Fact], analyses: list[Analysis], security_classification: SecurityClassification | None = None) -> Knowledge:
    """Create a candidate only; this function can never mark knowledge validated."""
    if not knowledge_id.strip() or not statement.strip(): raise ValueError("knowledge_id and statement are required")
    if not facts: raise ValueError("knowledge requires source facts")
    if not analyses: raise ValueError("knowledge requires source analyses")
    for analysis in analyses:
        errors = validate_analysis(analysis)
        if errors: raise ValueError("invalid analysis: " + "; ".join(errors))
    source_levels = [fact.security_classification for fact in facts]
    inherited = source_levels[0]
    for level in source_levels[1:]: inherited = inherit_security_classification(inherited, level)
    inherited = inherit_security_classification(inherited, security_classification)
    distinct_sources = len({trace_id for fact in facts for trace_id in fact.source_trace_ids})
    return Knowledge(
        knowledge_id=knowledge_id,
        source_fact_ids=[fact.fact_id for fact in facts],
        source_analysis_ids=[analysis.analysis_id for analysis in analyses],
        statement=statement,
        evidence_count=len(facts),
        validation_status=KnowledgeStatus.CANDIDATE.value,
        security_classification=inherited,
        evidence_diversity=distinct_sources,
    )


def validate_knowledge(knowledge: Knowledge, *, validated_by: str, validated_at: datetime) -> Knowledge:
    if knowledge.validation_status != KnowledgeStatus.CANDIDATE.value: raise ValueError("only candidate knowledge can be validated")
    if not validated_by.strip(): raise ValueError("validated_by is required")
    if knowledge.valid_until is not None and validated_at >= knowledge.valid_until: raise ValueError("cannot validate expired knowledge")
    knowledge.validation_status = KnowledgeStatus.VALIDATED.value
    knowledge.validated_by = validated_by
    knowledge.validated_at = validated_at
    knowledge.status_changed_by = validated_by
    knowledge.status_changed_at = validated_at
    return knowledge


def expire_knowledge(knowledge: Knowledge, *, at: datetime, changed_by: str) -> Knowledge:
    if knowledge.validation_status not in {KnowledgeStatus.VALIDATED.value, KnowledgeStatus.CANDIDATE.value}: raise ValueError("only candidate or validated knowledge can expire")
    if knowledge.valid_until is None or at < knowledge.valid_until: raise ValueError("knowledge is not due to expire")
    knowledge.validation_status = KnowledgeStatus.EXPIRED.value
    knowledge.status_changed_by = changed_by
    knowledge.status_changed_at = at
    return knowledge


def supersede_knowledge(knowledge: Knowledge, *, superseded_by: str, at: datetime, changed_by: str) -> Knowledge:
    if knowledge.validation_status != KnowledgeStatus.VALIDATED.value: raise ValueError("only validated knowledge can be superseded")
    if not superseded_by.strip(): raise ValueError("superseded_by is required")
    knowledge.validation_status = KnowledgeStatus.SUPERSEDED.value
    knowledge.superseded_by = superseded_by
    knowledge.status_changed_by = changed_by
    knowledge.status_changed_at = at
    return knowledge


def reject_knowledge(knowledge: Knowledge, *, at: datetime, changed_by: str) -> Knowledge:
    if knowledge.validation_status != KnowledgeStatus.CANDIDATE.value: raise ValueError("only candidate knowledge can be rejected")
    knowledge.validation_status = KnowledgeStatus.REJECTED.value
    knowledge.status_changed_by = changed_by
    knowledge.status_changed_at = at
    return knowledge

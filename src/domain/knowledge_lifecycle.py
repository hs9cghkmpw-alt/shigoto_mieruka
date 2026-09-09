"""Human-gated FACT -> ANALYSIS -> KNOWLEDGE lifecycle."""

from datetime import datetime

from domain.models import Analysis, Fact, Knowledge, SecurityClassification
from domain.security import inherit_security_classification


def validate_analysis(analysis: Analysis) -> list[str]:
    errors: list[str] = []
    if not analysis.analysis_id.strip():
        errors.append("analysis_id is required")
    if not analysis.source_fact_ids:
        errors.append("analysis requires source facts")
    if not 0.0 <= analysis.confidence <= 1.0:
        errors.append("analysis confidence must be between 0 and 1")
    if not analysis.hypothesis.strip():
        errors.append("analysis hypothesis is required")
    return errors


def propose_knowledge(
    *,
    knowledge_id: str,
    statement: str,
    facts: list[Fact],
    analyses: list[Analysis],
    security_classification: SecurityClassification | None = None,
) -> Knowledge:
    """Create a candidate only; this function can never mark knowledge validated."""
    if not facts:
        raise ValueError("knowledge requires source facts")
    if not analyses:
        raise ValueError("knowledge requires source analyses")
    for analysis in analyses:
        errors = validate_analysis(analysis)
        if errors:
            raise ValueError("invalid analysis: " + "; ".join(errors))
    source_levels = [fact.security_classification for fact in facts]
    inherited = source_levels[0]
    for level in source_levels[1:]:
        inherited = inherit_security_classification(inherited, level)
    inherited = inherit_security_classification(inherited, security_classification)
    return Knowledge(
        knowledge_id=knowledge_id,
        source_fact_ids=[fact.fact_id for fact in facts],
        source_analysis_ids=[analysis.analysis_id for analysis in analyses],
        statement=statement,
        evidence_count=len(facts),
        validation_status="candidate",
        security_classification=inherited,
    )


def validate_knowledge(knowledge: Knowledge, *, validated_by: str, validated_at: datetime) -> Knowledge:
    """Explicit human gate for promotion from candidate to validated knowledge."""
    if knowledge.validation_status != "candidate":
        raise ValueError("only candidate knowledge can be validated")
    if not validated_by.strip():
        raise ValueError("validated_by is required")
    knowledge.validation_status = "validated"
    knowledge.validated_by = validated_by
    knowledge.validated_at = validated_at
    return knowledge

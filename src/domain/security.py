"""Security classification and derivation rules."""

from domain.models import SecurityClassification

_ORDER = {
    SecurityClassification.PUBLIC: 0,
    SecurityClassification.INTERNAL: 1,
    SecurityClassification.CONFIDENTIAL: 2,
    SecurityClassification.RESTRICTED: 3,
}


def inherit_security_classification(source: SecurityClassification, requested: SecurityClassification | None = None) -> SecurityClassification:
    """Derived data can never be less restrictive than its source."""
    if requested is None:
        return source
    return source if _ORDER[source] >= _ORDER[requested] else requested


def most_restrictive(*levels: SecurityClassification) -> SecurityClassification:
    if not levels:
        return SecurityClassification.INTERNAL
    return max(levels, key=lambda x: _ORDER[x])


def assert_not_less_restrictive(source: SecurityClassification, derived: SecurityClassification) -> None:
    if _ORDER[derived] < _ORDER[source]:
        raise ValueError(f"security classification downgrade: {source.value} -> {derived.value}")

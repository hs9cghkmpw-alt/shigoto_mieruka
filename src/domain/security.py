"""Security rules for derived work data."""

from domain.models import SecurityClassification

_ORDER = {
    SecurityClassification.PUBLIC: 0,
    SecurityClassification.INTERNAL: 1,
    SecurityClassification.CONFIDENTIAL: 2,
    SecurityClassification.RESTRICTED: 3,
}


def inherit_security_classification(
    source: SecurityClassification,
    requested: SecurityClassification | None = None,
) -> SecurityClassification:
    """Never allow derived data to be less restrictive than its source."""
    if requested is None:
        return source
    return source if _ORDER[source] >= _ORDER[requested] else requested

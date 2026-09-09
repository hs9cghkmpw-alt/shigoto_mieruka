"""Safe connector boundary. Real providers must implement this contract with authenticated APIs."""

from typing import Iterable
from ingestion.contracts import SourceConnector, SourceEvent


class ConnectorRegistry:
    def __init__(self):
        self._connectors: dict[str, SourceConnector] = {}

    def register(self, name: str, connector: SourceConnector) -> None:
        if not name.strip():
            raise ValueError("connector name is required")
        if name in self._connectors:
            raise ValueError(f"connector already registered: {name}")
        self._connectors[name] = connector

    def get(self, name: str) -> SourceConnector:
        try:
            return self._connectors[name]
        except KeyError as exc:
            raise KeyError(f"unknown connector: {name}") from exc

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._connectors))

    def pull(self, name: str, *, since=None) -> Iterable[SourceEvent]:
        """Provider-specific authentication and retrieval stay inside the connector."""
        return self.get(name).pull(since=since)

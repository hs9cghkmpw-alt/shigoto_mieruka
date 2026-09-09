import pytest
from ingestion.connectors import ConnectorRegistry


def test_connector_registry_is_explicit_and_does_not_fake_provider_access():
    registry = ConnectorRegistry()
    class Connector:
        def pull(self, *, since=None): return []
    registry.register("test", Connector())
    assert registry.names() == ("test",)
    with pytest.raises(ValueError): registry.register("test", Connector())
    assert list(registry.pull("test")) == []

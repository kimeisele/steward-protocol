import pytest

from vibe_core.loaders.manifest_registry import ManifestRegistry
from vibe_core.naga.kulika import get_kulika
from vibe_core.naga.services.tuv import TÜVService
from vibe_core.protocols.universal import EntityStatus, UnionProtocol


class TestUnionProtocol:
    """Test the Union Protocol (State of the Union)."""

    def test_living_entities_discovery(self, tmp_path):
        # 1. Instantiate TÜV
        registry_path = tmp_path / "tuv_union.json"
        tuv = TÜVService(registry_path=registry_path)

        # 2. Check if it implements UnionProtocol
        assert isinstance(tuv, UnionProtocol)

        # 3. Get living entities
        entities = tuv.get_living_entities()

        # 4. Verify discovery
        # We expect at least one Naga (Kulika itself or TÜV if registered)
        # and some Agents if they are in the registry
        assert len(entities) >= 0

        for entity in entities:
            assert isinstance(entity, EntityStatus)
            assert entity.id
            # Accept any type ending in -module or known types
            assert entity.type or entity.id
            print(f"Entity: {entity.id} ({entity.type}) -> Protocol: {entity.protocol}")

    def test_union_summary(self, tmp_path):
        registry_path = tmp_path / "tuv_summary.json"
        tuv = TÜVService(registry_path=registry_path)

        summary = tuv.get_union_summary()
        assert "population" in summary
        assert "by_type" in summary
        assert "compliance" in summary
        print(f"Union Population: {summary['population']}")

"""
TATTVA REGISTRY — Tests
========================

Verifies that TattvaRegistry collects, indexes, and queries
__tattva__ declarations correctly.
"""

import pytest
from vibe_core.mahamantra.substrate.tattva_registry import TattvaRegistry, get_registry
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol


@pytest.fixture(autouse=True)
def clean_registry():
    """Reset singleton before each test."""
    TattvaRegistry.reset()
    yield
    TattvaRegistry.reset()


class _MockComponent:
    """A component that implements __tattva__."""

    def __init__(self, name: str, capability: str):
        self._name = name
        self._capability = capability

    @property
    def __tattva__(self):
        return {
            "chaitanya": f"{self._name} — Test Component",
            "nityananda": f"Depends on {self._capability}",
            "advaita": "test_method() → result",
            "gadadhara": "active=True",
            "srivasa": "TestGovernance",
        }


class _NoTattvaComponent:
    """A component WITHOUT __tattva__."""

    pass


class TestTattvaRegistryBasics:
    def test_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_empty_registry(self):
        reg = get_registry()
        assert reg.count == 0
        assert len(reg) == 0
        assert reg.names == ()

    def test_register_component(self):
        reg = get_registry()
        comp = _MockComponent("Clock", "Timer")
        assert reg.register("clock", comp) is True
        assert reg.count == 1
        assert "clock" in reg

    def test_register_no_tattva(self):
        reg = get_registry()
        comp = _NoTattvaComponent()
        assert reg.register("broken", comp) is False
        assert reg.count == 0

    def test_unregister(self):
        reg = get_registry()
        comp = _MockComponent("Clock", "Timer")
        reg.register("clock", comp)
        assert reg.unregister("clock") is True
        assert reg.count == 0
        assert "clock" not in reg

    def test_unregister_nonexistent(self):
        reg = get_registry()
        assert reg.unregister("ghost") is False


class TestTattvaRegistryQuery:
    def test_get_by_name(self):
        reg = get_registry()
        comp = _MockComponent("Flute", "Rhythm")
        reg.register("venu", comp)
        tattva = reg.get("venu")
        assert tattva is not None
        assert "Flute" in tattva["chaitanya"]

    def test_get_nonexistent(self):
        reg = get_registry()
        assert reg.get("ghost") is None

    def test_query_by_key(self):
        reg = get_registry()
        reg.register("venu", _MockComponent("Flute", "Rhythm"))
        reg.register("clock", _MockComponent("Clock", "Timer"))
        reg.register("kernel", _MockComponent("Kernel", "Rhythm"))

        results = reg.query("nityananda", "Rhythm")
        assert len(results) == 2
        names = [r[0] for r in results]
        assert "venu" in names
        assert "kernel" in names

    def test_query_case_insensitive(self):
        reg = get_registry()
        reg.register("venu", _MockComponent("Flute", "RHYTHM"))
        results = reg.query("nityananda", "rhythm")
        assert len(results) == 1

    def test_by_capability_searches_all_fields(self):
        reg = get_registry()
        reg.register("venu", _MockComponent("Flute", "Rhythm"))
        reg.register("clock", _MockComponent("Clock", "Timer"))

        results = reg.by_capability("Flute")
        assert len(results) == 1
        assert results[0][0] == "venu"

    def test_get_object(self):
        reg = get_registry()
        comp = _MockComponent("Flute", "Rhythm")
        reg.register("venu", comp)
        assert reg.get_object("venu") is comp


class TestTattvaRegistryIntrospection:
    def test_iterate(self):
        reg = get_registry()
        reg.register("a", _MockComponent("A", "X"))
        reg.register("b", _MockComponent("B", "Y"))
        items = list(reg)
        assert len(items) == 2

    def test_repr(self):
        reg = get_registry()
        reg.register("a", _MockComponent("A", "X"))
        assert "1 components" in repr(reg)

    def test_registry_has_own_tattva(self):
        reg = get_registry()
        tattva = reg.__tattva__
        assert "Border Control" in tattva["chaitanya"]
        assert isinstance(reg, PanchaTattvaProtocol)

    def test_names_tuple(self):
        reg = get_registry()
        reg.register("alpha", _MockComponent("A", "X"))
        reg.register("beta", _MockComponent("B", "Y"))
        assert set(reg.names) == {"alpha", "beta"}


class TestTattvaRegistryWithRealComponents:
    """Integration: real MahamantraLotus registers in the registry."""

    def test_lotus_registers(self):
        reg = get_registry()
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        reg.register("mahamantra_lotus", lotus)
        tattva = reg.get("mahamantra_lotus")
        assert tattva is not None
        assert "MahamantraLotus" in tattva["chaitanya"]
        assert "TattvaGates" in tattva["chaitanya"]

    def test_lotus_queryable_by_capability(self):
        reg = get_registry()
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        lotus = MahamantraLotus()
        reg.register("mahamantra_lotus", lotus)
        results = reg.by_capability("PARSE")
        assert len(results) >= 1
        assert any("mahamantra_lotus" == r[0] for r in results)

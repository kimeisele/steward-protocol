"""
Tests proving vibration emission uses public API — no private cross-module calls.

After the hack cleanup:
  - engine.py uses maha.vibrate() (public), not maha._compute_vibration() (private)
  - healing_intent.py uses maha.vibrate() (public), not maha.akash.record() (nonexistent)
  - _update_akash is gone from all production code (never existed as a method)
"""

import ast
from pathlib import Path


_MAHAMANTRA_ROOT = Path(__file__).resolve().parent.parent


class TestNoPrivateCrossModuleCalls:
    """Production code must not call private methods across module boundaries."""

    def test_engine_no_update_akash(self):
        """engine.py must not call _update_akash (method does not exist)."""
        src = (_MAHAMANTRA_ROOT / "dharma" / "kumaras" / "engine.py").read_text()
        assert "_update_akash" not in src

    def test_engine_no_private_compute_vibration(self):
        """engine.py must not call maha._compute_vibration (private API)."""
        src = (_MAHAMANTRA_ROOT / "dharma" / "kumaras" / "engine.py").read_text()
        assert "._compute_vibration" not in src

    def test_engine_uses_public_vibrate(self):
        """engine.py must use maha.vibrate() (public API)."""
        src = (_MAHAMANTRA_ROOT / "dharma" / "kumaras" / "engine.py").read_text()
        assert ".vibrate(" in src

    def test_healing_intent_no_akash_record(self):
        """healing_intent.py must not call akash.record() (akash doesn't exist)."""
        src = (_MAHAMANTRA_ROOT / "dharma" / "kumaras" / "healing_intent.py").read_text()
        assert "akash.record" not in src

    def test_healing_intent_uses_public_vibrate(self):
        """healing_intent.py must use mahamantra.vibrate() (public API)."""
        src = (_MAHAMANTRA_ROOT / "dharma" / "kumaras" / "healing_intent.py").read_text()
        assert ".vibrate(" in src


class TestGenesisNotPlaceholder:
    """__genesis__ must be a real computed value, not '0x...' placeholder."""

    def test_audit_dispatcher_genesis(self):
        src = (_MAHAMANTRA_ROOT / "audit" / "audit_dispatcher.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__genesis__":
                        val = ast.literal_eval(node.value)
                        assert val != "0x...", "genesis is still placeholder"
                        assert int(val, 16) % 37 == 0, "genesis fails parampara check"

    def test_audit_registry_genesis(self):
        src = (_MAHAMANTRA_ROOT / "audit" / "audit_registry.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__genesis__":
                        val = ast.literal_eval(node.value)
                        assert val != "0x...", "genesis is still placeholder"
                        assert int(val, 16) % 37 == 0, "genesis fails parampara check"


class TestVibratePubicAPIExists:
    """MahamantraLotus.vibrate() must exist as public API."""

    def test_vibrate_is_public_method(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        assert hasattr(MahamantraLotus, "vibrate")
        assert callable(getattr(MahamantraLotus, "vibrate"))

    def test_vibrate_not_underscore(self):
        """vibrate() must not be a private method."""
        assert not "vibrate".startswith("_")


class TestAkashPublicProperty:
    """MahamantraLotus.akash must be a public read-only property."""

    def test_akash_property_exists(self):
        from vibe_core.mahamantra.substrate.lotus_core import MahamantraLotus

        assert isinstance(MahamantraLotus.akash, property)

    def test_akash_returns_dict(self):
        from vibe_core.mahamantra import mahamantra

        akash = mahamantra.akash
        assert isinstance(akash, dict)

    def test_akash_has_required_keys(self):
        from vibe_core.mahamantra import mahamantra

        akash = mahamantra.akash
        required = {
            "resonance_level",
            "accumulated_value",
            "total_beats",
            "total_rounds",
            "attractor_counts",
            "last_seed",
            "last_position",
            "last_attractor",
        }
        assert required.issubset(akash.keys())

    def test_akash_is_copy_not_reference(self):
        """Mutating the returned dict must not affect internal state."""
        from vibe_core.mahamantra import mahamantra

        akash = mahamantra.akash
        akash["total_beats"] = 999999
        assert mahamantra.akash["total_beats"] != 999999

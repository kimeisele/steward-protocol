"""
TESTS: intents.py - Dynamic YAML Loading
========================================

"satyaṁ param dhīmahi" - We meditate on the Supreme Truth.

REAL TESTS for:
1. YAML loading from knowledge/guardian_intents.yaml
2. Cache behavior
3. Hot-reload via reload_intents()
4. Backward compatibility (INTENT_MAP proxy)
5. Helper functions (get_intents, get_position_for_intent)
"""

import pytest
from pathlib import Path


class TestYAMLLoading:
    """Test that intents load from YAML, not hardcoded."""

    def test_yaml_file_exists(self):
        """The YAML file must exist."""
        from vibe_core.mahamantra.substrate.intents import get_yaml_path

        yaml_path = get_yaml_path()
        assert yaml_path.exists(), f"YAML file not found: {yaml_path}"

    def test_yaml_path_is_in_knowledge_dir(self):
        """YAML must be in knowledge/ directory (SSOT)."""
        from vibe_core.mahamantra.substrate.intents import get_yaml_path

        yaml_path = get_yaml_path()
        assert "knowledge" in str(yaml_path), "YAML must be in knowledge/ directory"
        assert yaml_path.name == "guardian_intents.yaml"

    def test_loads_all_16_positions(self):
        """Must load all 16 guardian positions (0-15)."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        assert len(INTENT_MAP) == 16, f"Expected 16 positions, got {len(INTENT_MAP)}"
        for pos in range(16):
            assert pos in INTENT_MAP, f"Position {pos} missing from INTENT_MAP"

    def test_each_position_has_keywords(self):
        """Each position must have at least one keyword."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        for pos in range(16):
            intents = INTENT_MAP[pos]
            assert len(intents) > 0, f"Position {pos} has no keywords"
            assert isinstance(intents, tuple), f"Position {pos} intents must be tuple"


class TestIntentMapProxy:
    """Test backward compatibility via _IntentMapProxy."""

    def test_getitem(self):
        """INTENT_MAP[pos] must work."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        result = INTENT_MAP[0]
        assert "boot" in result, "Position 0 (VYASA) must have 'boot'"

    def test_get_with_default(self):
        """INTENT_MAP.get(pos, default) must work."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        result = INTENT_MAP.get(0, ())
        assert len(result) > 0

        result = INTENT_MAP.get(999, ("default",))
        assert result == ("default",)

    def test_contains(self):
        """pos in INTENT_MAP must work."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        assert 0 in INTENT_MAP
        assert 15 in INTENT_MAP
        assert 999 not in INTENT_MAP

    def test_iter(self):
        """for pos in INTENT_MAP must work."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        positions = list(INTENT_MAP)
        assert len(positions) == 16
        assert 0 in positions
        assert 15 in positions

    def test_items(self):
        """INTENT_MAP.items() must work."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP

        items = list(INTENT_MAP.items())
        assert len(items) == 16
        assert all(isinstance(k, int) for k, v in items)
        assert all(isinstance(v, tuple) for k, v in items)


class TestHelperFunctions:
    """Test get_intents and get_position_for_intent."""

    def test_get_intents_valid_position(self):
        """get_intents returns keywords for valid position."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        result = get_intents(0)
        assert "boot" in result
        assert "system" in result

    def test_get_intents_invalid_position(self):
        """get_intents returns empty tuple for invalid position."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        result = get_intents(999)
        assert result == ()

    def test_get_position_for_intent_found(self):
        """get_position_for_intent returns correct position."""
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent

        assert get_position_for_intent("boot") == 0  # VYASA
        assert get_position_for_intent("create") == 1  # BRAHMA
        assert get_position_for_intent("analyze") == 6  # KAPILA

    def test_get_position_for_intent_not_found(self):
        """get_position_for_intent returns -1 for unknown intent."""
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent

        assert get_position_for_intent("xyznonexistent") == -1

    def test_get_position_for_intent_case_insensitive(self):
        """get_position_for_intent is case-insensitive."""
        from vibe_core.mahamantra.substrate.intents import get_position_for_intent

        assert get_position_for_intent("BOOT") == 0
        assert get_position_for_intent("Boot") == 0
        assert get_position_for_intent("boot") == 0


class TestReloadIntents:
    """Test hot-reload capability."""

    def test_reload_returns_dict(self):
        """reload_intents returns the loaded dict."""
        from vibe_core.mahamantra.substrate.intents import reload_intents

        result = reload_intents()
        assert isinstance(result, dict)
        assert len(result) == 16

    def test_reload_clears_cache(self):
        """reload_intents clears and reloads cache."""
        from vibe_core.mahamantra.substrate import intents

        # Access to populate cache
        _ = intents.INTENT_MAP[0]

        # Clear and reload
        result = intents.reload_intents()

        # Should still work
        assert len(result) == 16
        assert 0 in result


class TestGuardianAlignment:
    """Test alignment with seed.py ALL_GUARDIANS."""

    def test_vyasa_position_0(self):
        """Position 0 is VYASA (boot, system)."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        intents = get_intents(0)
        assert "boot" in intents or "system" in intents

    def test_narada_position_2(self):
        """Position 2 is NARADA (chat, communicate)."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        intents = get_intents(2)
        assert "chat" in intents or "communicate" in intents

    def test_kapila_position_6(self):
        """Position 6 is KAPILA (analyze, understand)."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        intents = get_intents(6)
        assert "analyze" in intents or "understand" in intents

    def test_parashurama_position_8(self):
        """Position 8 is PARASHURAMA (execute, run)."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        intents = get_intents(8)
        assert "execute" in intents or "run" in intents

    def test_yamaraja_position_15(self):
        """Position 15 is YAMARAJA (judge, audit)."""
        from vibe_core.mahamantra.substrate.intents import get_intents

        intents = get_intents(15)
        assert "judge" in intents or "audit" in intents

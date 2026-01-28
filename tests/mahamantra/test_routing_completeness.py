"""
TESTS: Mahamantra Routing Completeness
======================================

"EIN IMPORT. KRISHNA ROUTET ALLES."
— MAHAPROMPT.md

These tests ensure ALL modules are accessible via `mahamantra.xyz`.
NO manual wiring. If it exists, it routes.
"""

import pytest
from pathlib import Path


class TestMahamantraRouting:
    """Test that mahamantra routes to all modules."""

    @pytest.fixture
    def mahamantra_root(self) -> Path:
        """Get mahamantra package root."""
        import vibe_core.mahamantra
        return Path(vibe_core.mahamantra.__file__).parent

    @pytest.fixture
    def mahamantra(self):
        """Get mahamantra singleton."""
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    def test_all_subpackages_route(self, mahamantra, mahamantra_root):
        """All subpackages (folders with __init__.py) must route."""
        subpackages = [
            d.name for d in mahamantra_root.iterdir()
            if d.is_dir()
            and (d / "__init__.py").exists()
            and not d.name.startswith("_")
        ]

        for name in subpackages:
            obj = getattr(mahamantra, name, None)
            assert obj is not None, f"mahamantra.{name} should route but returns None"

    def test_all_root_modules_route(self, mahamantra, mahamantra_root):
        """All root-level .py files must route."""
        root_modules = [
            f.stem for f in mahamantra_root.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        for name in root_modules:
            obj = getattr(mahamantra, name, None)
            assert obj is not None, f"mahamantra.{name} should route but returns None"

    def test_all_adapters_route(self, mahamantra, mahamantra_root):
        """All adapter modules must route."""
        adapters_dir = mahamantra_root / "adapters"
        if not adapters_dir.exists():
            pytest.skip("No adapters directory")

        adapters = [
            f.stem for f in adapters_dir.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        for name in adapters:
            obj = getattr(mahamantra, name, None)
            assert obj is not None, f"mahamantra.{name} (adapter) should route but returns None"

    def test_key_modules_accessible(self, mahamantra):
        """Key modules must be accessible."""
        key_modules = [
            "chat",
            "commands",
            "adapters",
            "cli",
            "research",
            "substrate",
            "reactor",
            "kernel",
        ]

        for name in key_modules:
            obj = getattr(mahamantra, name, None)
            assert obj is not None, f"mahamantra.{name} must be accessible"

    def test_seed_constants_accessible(self, mahamantra):
        """Seed constants must route through mahamantra."""
        constants = ["PARAMPARA", "WORDS", "MAHA_QUANTUM"]

        for name in constants:
            val = getattr(mahamantra, name, None)
            assert val is not None, f"mahamantra.{name} must be accessible"

    def test_parampara_is_37(self, mahamantra):
        """PARAMPARA must be 37."""
        assert mahamantra.PARAMPARA == 37

    def test_words_is_16(self, mahamantra):
        """WORDS must be 16."""
        assert mahamantra.WORDS == 16


class TestMahamantraRoutingCount:
    """Test that routing covers expected number of modules."""

    def test_minimum_subpackages(self):
        """Must have at least 10 subpackages."""
        from vibe_core.mahamantra import mahamantra
        import vibe_core.mahamantra

        root = Path(vibe_core.mahamantra.__file__).parent
        subpackages = [
            d.name for d in root.iterdir()
            if d.is_dir() and (d / "__init__.py").exists()
            and not d.name.startswith("_")
        ]

        assert len(subpackages) >= 10, f"Expected >= 10 subpackages, got {len(subpackages)}"

    def test_minimum_adapters(self):
        """Must have at least 10 adapters."""
        from vibe_core.mahamantra import mahamantra
        import vibe_core.mahamantra

        root = Path(vibe_core.mahamantra.__file__).parent
        adapters_dir = root / "adapters"

        adapters = [
            f.stem for f in adapters_dir.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]

        assert len(adapters) >= 10, f"Expected >= 10 adapters, got {len(adapters)}"


class TestMahamantraVibration:
    """Test vibration API (Call-Response)."""

    @pytest.fixture
    def mahamantra(self):
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    def test_vibrate_returns_dict(self, mahamantra):
        """vibrate() returns VibrationState dict."""
        result = mahamantra.vibrate("test query")
        assert isinstance(result, dict)
        assert "seed" in result
        assert "attractor" in result
        assert "resonance" in result

    def test_kirtan_returns_result(self, mahamantra):
        """kirtan() returns KirtanComputeResult."""
        result = mahamantra.kirtan(42)
        assert hasattr(result, "call_response")
        assert hasattr(result, "flute_resonance")
        assert hasattr(result, "transformed_value")

    def test_kirtan_call_response(self, mahamantra):
        """kirtan() has CALL or RESPONSE."""
        result = mahamantra.kirtan(42)
        assert result.call_response in ("CALL", "RESPONSE")

    def test_attractor_fixed_accessible(self, mahamantra):
        """ATTRACTOR_FIXED is accessible."""
        assert mahamantra.ATTRACTOR_FIXED == 18

    def test_attractor_cycle_accessible(self, mahamantra):
        """ATTRACTOR_CYCLE is accessible."""
        cycle = mahamantra.ATTRACTOR_CYCLE
        assert isinstance(cycle, tuple)
        assert len(cycle) == 4


class TestResearchFractalRouting:
    """Test research fractal routing: folder IS wiring."""

    @pytest.fixture
    def mahamantra(self):
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    @pytest.fixture
    def research_root(self) -> Path:
        """Get research package root."""
        import vibe_core.mahamantra.research
        return Path(vibe_core.mahamantra.research.__file__).parent

    def test_all_research_modules_route(self, mahamantra, research_root):
        """All research .py files must be accessible via fractal routing."""
        research_modules = [
            f.stem for f in research_root.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        for name in research_modules:
            obj = getattr(mahamantra.research, name, None)
            assert obj is not None, f"mahamantra.research.{name} should route but returns None"

    def test_all_research_subpackages_route(self, mahamantra, research_root):
        """All research subpackages must be accessible via fractal routing."""
        subpackages = [
            d.name for d in research_root.iterdir()
            if d.is_dir()
            and (d / "__init__.py").exists()
            and not d.name.startswith("_")
        ]

        for name in subpackages:
            obj = getattr(mahamantra.research, name, None)
            assert obj is not None, f"mahamantra.research.{name} should route but returns None"

    def test_research_dharma_routes(self, mahamantra):
        """mahamantra.research.dharma must route."""
        dharma = mahamantra.research.dharma
        assert dharma is not None
        assert hasattr(dharma, "MahaKirtan")

    def test_research_module_count(self, research_root):
        """Must have at least 30 research modules."""
        research_modules = [
            f.stem for f in research_root.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]
        assert len(research_modules) >= 30, f"Expected >= 30 research modules, got {len(research_modules)}"

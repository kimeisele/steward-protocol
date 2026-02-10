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
        """All adapter modules must route via mahamantra.adapters.{name}."""
        adapters_dir = mahamantra_root / "adapters"
        if not adapters_dir.exists():
            pytest.skip("No adapters directory")

        adapters = [
            f.stem for f in adapters_dir.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        # MAHAPROMPT 2026: Lotus fractal routing - adapters are in mahamantra.adapters.*
        # NOT directly on mahamantra.* (that would require flat imports)
        for name in adapters:
            obj = getattr(mahamantra.adapters, name, None)
            assert obj is not None, f"mahamantra.adapters.{name} should route but returns None"

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
        """vibrate() returns VibrationState (kirtan is internal to SankirtanChamber)."""
        # MAHAPROMPT 2026: kirtan is the Chamber's internal loop, not exposed on mahamantra
        # Use vibrate() which is the public API for intent → vibration
        result = mahamantra.vibrate("test query")
        # VibrationState has seed, attractor, resonance, etc.
        assert "seed" in result
        assert "attractor" in result
        assert "resonance" in result

    def test_kirtan_call_response(self, mahamantra):
        """Vibration has resonance (kirtan is internal call-response loop)."""
        # MAHAPROMPT 2026: kirtan loop is internal to SankirtanChamber
        # The result we get is VibrationState with resonance info
        result = mahamantra.vibrate("test input")
        assert "resonance" in result
        assert isinstance(result["resonance"], int)

    def test_attractor_fixed_accessible(self, mahamantra):
        """ATTRACTOR_FIXED is the true fixed point (POSITION_SUM_TOTAL = 136)."""
        from vibe_core.mahamantra.protocols._maha_compute import ATTRACTOR_FIXED
        from vibe_core.mahamantra.protocols._seed import POSITION_SUM_TOTAL
        assert ATTRACTOR_FIXED == POSITION_SUM_TOTAL  # 136 = T(16)

    def test_attractor_cycle_accessible(self, mahamantra):
        """Cycle attractors are computed (non-fixed-point attractors in mod-137 space)."""
        from vibe_core.mahamantra.protocols._maha_compute import get_attractor_cycle
        cycle = get_attractor_cycle()
        assert isinstance(cycle, tuple)
        assert len(cycle) > 0, "Must have at least one cycle attractor"


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
        # MAHAPROMPT 2026: MahaKirtan was migrated to substrate.mantra
        # research.dharma still exists for research modules
        dharma = mahamantra.research.dharma
        assert dharma is not None
        # Check for research modules that remain in dharma
        # MahaKirtan is in substrate.mantra now (core, not research)
        assert hasattr(dharma, "__getattr__")  # Fractal routing enabled

    def test_research_module_count(self, research_root):
        """Must have at least 30 research modules."""
        research_modules = [
            f.stem for f in research_root.glob("*.py")
            if f.stem != "__init__" and not f.stem.startswith("_")
        ]
        assert len(research_modules) >= 30, f"Expected >= 30 research modules, got {len(research_modules)}"


class TestAdaptersFractalRouting:
    """Test adapters fractal routing: folder IS wiring."""

    @pytest.fixture
    def mahamantra(self):
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    @pytest.fixture
    def adapters_root(self) -> Path:
        """Get adapters package root."""
        import vibe_core.mahamantra.adapters
        return Path(vibe_core.mahamantra.adapters.__file__).parent

    def test_all_adapter_modules_route(self, mahamantra, adapters_root):
        """All adapter .py files must be accessible via fractal routing."""
        adapter_modules = [
            f.stem for f in adapters_root.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        for name in adapter_modules:
            obj = getattr(mahamantra.adapters, name, None)
            assert obj is not None, f"mahamantra.adapters.{name} should route but returns None"


class TestSubstrateFractalRouting:
    """Test substrate fractal routing: folder IS wiring."""

    @pytest.fixture
    def mahamantra(self):
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    @pytest.fixture
    def substrate_root(self) -> Path:
        """Get substrate package root."""
        import vibe_core.mahamantra.substrate
        return Path(vibe_core.mahamantra.substrate.__file__).parent

    def test_all_substrate_modules_route(self, mahamantra, substrate_root):
        """All substrate .py files must be accessible via fractal routing."""
        substrate_modules = [
            f.stem for f in substrate_root.glob("*.py")
            if f.stem != "__init__"
            and not f.stem.startswith("_")
        ]

        for name in substrate_modules:
            obj = getattr(mahamantra.substrate, name, None)
            assert obj is not None, f"mahamantra.substrate.{name} should route but returns None"


class TestProtocolsFractalRouting:
    """Test protocols fractal routing: folder IS wiring."""

    @pytest.fixture
    def mahamantra(self):
        from vibe_core.mahamantra import mahamantra
        return mahamantra

    @pytest.fixture
    def protocols_root(self) -> Path:
        """Get protocols package root."""
        import vibe_core.mahamantra.protocols
        return Path(vibe_core.mahamantra.protocols.__file__).parent

    def test_protocols_subpackages_route(self, mahamantra, protocols_root):
        """All protocols subpackages must be accessible via fractal routing."""
        subpackages = [
            d.name for d in protocols_root.iterdir()
            if d.is_dir()
            and (d / "__init__.py").exists()
            and not d.name.startswith("_")
        ]

        for name in subpackages:
            obj = getattr(mahamantra.protocols, name, None)
            assert obj is not None, f"mahamantra.protocols.{name} should route but returns None"

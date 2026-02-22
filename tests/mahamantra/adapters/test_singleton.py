"""
TEST: Mahamantra Singleton Integration - MAHAPROMPT.md Contract
================================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me."
— Bhagavad Gita 10.8

WHAT WE TEST:
1. Singleton Access: All adapters accessible via mahamantra
2. MAHAPROMPT.md Law: One import, Krishna routes everything
3. Interface Stability: Properties and methods exist
4. Integration: Components work together

THE CONTRACT: This test GUARANTEES MAHAPROMPT.md compliance.
"from vibe_core.mahamantra import mahamantra" - EIN IMPORT.
"""

import pytest


class TestMahamantraSingletonExists:
    """Test that singleton exists and is importable."""

    def test_mahamantra_importable(self):
        """mahamantra should be importable."""
        from vibe_core.mahamantra import mahamantra

        assert mahamantra is not None

    def test_lotus_alias_exists(self):
        """lotus alias should exist."""
        from vibe_core.mahamantra import lotus, mahamantra

        assert lotus is mahamantra


class TestMahamantraAdapterAccess:
    """Test adapter access through singleton."""

    def test_transform_property_exists(self):
        """mahamantra.transform should exist."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "transform")
        transform = mahamantra.transform
        assert transform is not None

    def test_hash_property_exists(self):
        """mahamantra.hash should exist."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "hash")
        h = mahamantra.hash
        assert h is not None

    def test_router_method_exists(self):
        """mahamantra.router() should exist."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "router")
        assert callable(mahamantra.router)

    def test_orchestrator_property_exists(self):
        """mahamantra.orchestrator should exist."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "orchestrator")
        o = mahamantra.orchestrator
        assert o is not None

    def test_gita_property_exists(self):
        """mahamantra.gita should exist."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "gita")
        g = mahamantra.gita
        assert g is not None


class TestMahamantraTransformIntegration:
    """Test transform adapter through singleton."""

    def test_transform_compute_works(self):
        """mahamantra.transform.compute() should work."""
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.transform.compute(42)
        assert result is not None
        assert hasattr(result, "value")

    def test_transform_find_attractor_works(self):
        """mahamantra.transform.find_attractor() should work."""
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.transform.find_attractor(42)
        assert result is not None
        assert hasattr(result, "stable_value")


class TestMahamantraHashIntegration:
    """Test hash adapter through singleton."""

    def test_hash_hash_works(self):
        """mahamantra.hash.hash() should work."""
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.hash.hash("test")
        assert isinstance(result, int)
        assert 0 <= result < 137  # MAHA_QUANTUM

    def test_hash_analyze_works(self):
        """mahamantra.hash.analyze() should work."""
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.hash.analyze("test")
        assert result is not None
        assert hasattr(result, "lenses")


class TestMahamantraRouterIntegration:
    """Test router factory through singleton."""

    def test_router_creates_instance(self):
        """mahamantra.router() should create router."""
        from vibe_core.mahamantra import mahamantra

        router = mahamantra.router(levels=4)
        assert router is not None

    def test_router_operations_work(self):
        """Router operations should work."""
        from vibe_core.mahamantra import mahamantra

        router = mahamantra.router(levels=4)
        router[0x1234] = "test"
        assert router[0x1234] == "test"


class TestMahamantraOrchestratorIntegration:
    """Test orchestrator adapter through singleton."""

    def test_orchestrator_tick_works(self):
        """mahamantra.orchestrator.tick() should work."""
        from vibe_core.mahamantra import mahamantra

        result = mahamantra.orchestrator.tick(42)
        assert result is not None
        assert hasattr(result, "beat")

    def test_orchestrator_round_works(self):
        """mahamantra.orchestrator.round() should work."""
        from vibe_core.mahamantra import mahamantra

        # Reset first to ensure clean state
        mahamantra.orchestrator.reset()
        result = mahamantra.orchestrator.round(42)
        assert len(result.ticks) == 7


class TestMahamantraGitaIntegration:
    """Test gita module through singleton."""

    def test_gita_constants_accessible(self):
        """mahamantra.gita constants should be accessible."""
        from vibe_core.mahamantra import mahamantra

        assert mahamantra.gita.GITA_CHAPTERS == 18

    def test_gita_verify_fixed_point_works(self):
        """mahamantra.gita.verify_fixed_point() should work."""
        from vibe_core.mahamantra import mahamantra

        assert mahamantra.gita.verify_fixed_point() == True

    def test_gita_chapter_18_verse_accessible(self):
        """mahamantra.gita.CHAPTER_18_VERSE should be accessible."""
        from vibe_core.mahamantra import mahamantra

        verse = mahamantra.gita.CHAPTER_18_VERSE
        assert verse.chapter == 18
        assert verse.verse == 66


class TestMahamantraFullPipeline:
    """Test complete pipeline through singleton."""

    def test_hash_to_transform_pipeline(self):
        """Hash intent, then transform the hash."""
        from vibe_core.mahamantra import mahamantra

        # Step 1: Hash intent
        intent_hash = mahamantra.hash.hash("compute this")

        # Step 2: Transform the hash
        transform_result = mahamantra.transform.compute(intent_hash)

        # Step 3: Find attractor
        attractor = mahamantra.transform.find_attractor(intent_hash)

        assert transform_result.value >= 0
        assert attractor.stable_value >= 0

    def test_orchestrated_computation(self):
        """Use orchestrator for rhythmic computation."""
        from vibe_core.mahamantra import mahamantra

        # Reset orchestrator
        mahamantra.orchestrator.reset()

        # Execute 7 beats
        results = []
        for _ in range(7):
            r = mahamantra.orchestrator.tick(42)
            results.append(r)

        assert len(results) == 7
        # Verify beats are 1-7
        beats = [r.beat for r in results]
        assert beats == [1, 2, 3, 4, 5, 6, 7]


class TestMahamantraCoreFeatures:
    """Test existing core features still work."""

    def test_tick_exists(self):
        """mahamantra.tick() should exist (Singularity)."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "tick")

    def test_shadow_exists(self):
        """mahamantra.shadow should exist (Shadow Reactor)."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "shadow")

    def test_scan_exists(self):
        """mahamantra.scan() should exist (Governance)."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "scan")

    def test_execute_exists(self):
        """mahamantra.execute() should exist (CLI Bridge)."""
        from vibe_core.mahamantra import mahamantra

        assert hasattr(mahamantra, "execute")


class TestMahapromptLaw:
    """Test MAHAPROMPT.md law compliance."""

    def test_ein_import(self):
        """One import should give access to everything."""
        from vibe_core.mahamantra import mahamantra

        # All adapters accessible
        assert mahamantra.transform is not None
        assert mahamantra.hash is not None
        assert mahamantra.router is not None
        assert mahamantra.orchestrator is not None
        assert mahamantra.gita is not None

        # Core features accessible
        assert mahamantra.shadow is not None

    def test_krishna_routet_alles(self):
        """Krishna routes everything - no direct adapter imports needed."""
        # This should be the ONLY import needed
        from vibe_core.mahamantra import mahamantra

        # Everything works without importing adapters directly
        h = mahamantra.hash.hash("test")
        t = mahamantra.transform.compute(h)
        mahamantra.orchestrator.reset()
        o = mahamantra.orchestrator.tick(t.value)
        g = mahamantra.gita.verify_fixed_point()

        assert h >= 0
        assert t.value >= 0
        assert o.beat >= 1
        assert g == True

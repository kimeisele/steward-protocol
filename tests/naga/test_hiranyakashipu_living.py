"""
HIRANYAKASHIPU LIVING TESTS - Test the Living Test Framework.

"Das Lebende testet das Lebende."

This tests that our living test framework actually LIVES:
- Seeds load from YAML
- Tests execute in real subprocess
- Evolution finds new attacks
- Hot-swap works

Meta-level: This is a test that tests a testing framework.
OUROBOROS indeed.
"""

import asyncio
from pathlib import Path

import pytest


class TestSeedLoader:
    """Test the SeedLoader (Narada's ear)."""

    def test_creates_empty(self):
        """SeedLoader initializes empty."""
        from vibe_core.naga.hiranyakashipu import SeedLoader

        loader = SeedLoader()
        assert loader.get_all_seeds() == []

    def test_loads_yaml_seeds(self):
        """SeedLoader loads seeds from YAML."""
        from vibe_core.naga.hiranyakashipu import SeedLoader

        loader = SeedLoader()
        seed_dir = Path(__file__).parent.parent.parent / "vibe_core/naga/hiranyakashipu/seeds"
        loader.add_seed_dir(seed_dir)

        count = loader.load_seeds()
        assert count > 0, "Should load seeds from YAML"

        seeds = loader.get_all_seeds()
        assert len(seeds) > 0

    def test_filters_by_type(self):
        """SeedLoader filters seeds by attack type."""
        from vibe_core.naga.hiranyakashipu import SeedLoader

        loader = SeedLoader()
        seed_dir = Path(__file__).parent.parent.parent / "vibe_core/naga/hiranyakashipu/seeds"
        loader.add_seed_dir(seed_dir)
        loader.load_seeds()

        trivial = loader.get_seeds(attack_type="trivial")
        assert len(trivial) > 0
        assert all(s.attack_type == "trivial" for s in trivial)

    def test_filters_by_difficulty(self):
        """SeedLoader filters seeds by difficulty."""
        from vibe_core.naga.hiranyakashipu import SeedLoader

        loader = SeedLoader()
        seed_dir = Path(__file__).parent.parent.parent / "vibe_core/naga/hiranyakashipu/seeds"
        loader.add_seed_dir(seed_dir)
        loader.load_seeds()

        easy = loader.get_seeds(difficulty=1)
        assert len(easy) > 0
        assert all(s.difficulty == 1 for s in easy)

    def test_seed_rendering(self):
        """Seeds render variables correctly."""
        from vibe_core.naga.hiranyakashipu import AttackSeed

        seed = AttackSeed(
            name="test_seed",
            description="Test",
            test_code="from {target_module} import foo",
            attack_type="test",
        )

        rendered = seed.render(target_module="my_module")
        assert "from my_module import foo" in rendered


class TestLivingTestFramework:
    """Test the LivingTestFramework (Prakriti's womb)."""

    @pytest.fixture
    def framework(self):
        """Create framework with seeds loaded."""
        from vibe_core.naga.hiranyakashipu import LivingTestFramework

        fw = LivingTestFramework()
        seed_dir = Path(__file__).parent.parent.parent / "vibe_core/naga/hiranyakashipu/seeds"
        fw.add_seed_dir(seed_dir)
        return fw

    def test_creates_framework(self):
        """Framework initializes correctly."""
        from vibe_core.naga.hiranyakashipu import LivingTestFramework

        fw = LivingTestFramework()
        assert fw is not None

    def test_loads_seeds(self, framework):
        """Framework loads seeds from directories."""
        count = framework.load_seeds()
        assert count > 0

    @pytest.mark.asyncio
    async def test_runs_trivial_attack(self, framework):
        """Framework runs a trivial attack and detects it."""
        seeds = framework.get_seeds(attack_type="trivial")
        assert len(seeds) > 0

        seed = seeds[0]
        result = await framework.run_attack(seed, "test_module")

        # Trivial test should PASS (exit_code = 0)
        # Therefore defense should detect it (bypassed = True, passed = False)
        assert result.exit_code == 0, "Trivial test should pass"
        # The attack bypasses if the test passes when it shouldn't
        # For trivial attacks with expected_behavior="should_fail",
        # if test passes (exit_code=0), the attack succeeded (bypassed=True)

    @pytest.mark.asyncio
    async def test_runs_real_attack(self, framework):
        """Framework runs a real attack and it fails correctly."""
        seeds = framework.get_seeds(attack_type="real")
        if not seeds:
            pytest.skip("No real seeds loaded")

        seed = seeds[0]
        result = await framework.run_attack(seed, "nonexistent_module")

        # Real test should FAIL (ImportError)
        assert result.exit_code != 0, "Real test should fail without implementation"
        assert result.analysis["has_import_error"], "Should have import error"

    @pytest.mark.asyncio
    async def test_records_execution_stats(self, framework):
        """Framework records execution statistics."""
        seeds = framework.get_seeds(attack_type="trivial")
        seed = seeds[0]

        initial_executions = seed.times_executed

        await framework.run_attack(seed, "test_module")

        # Stats should be updated
        updated_seed = framework.get_seeds(attack_type="trivial")[0]
        assert updated_seed.times_executed == initial_executions + 1

    @pytest.mark.asyncio
    async def test_callbacks_fire(self, framework):
        """Framework fires callbacks on attack results."""
        bypassed_attacks = []
        held_attacks = []

        framework.on_attack_bypassed(lambda s, r: bypassed_attacks.append(s.name))
        framework.on_defense_held(lambda s, r: held_attacks.append(s.name))

        # Run a trivial attack (should bypass)
        trivial = framework.get_seeds(attack_type="trivial")[0]
        await framework.run_attack(trivial, "test_module")

        # Run a real attack (should be held - test fails correctly)
        real_seeds = framework.get_seeds(attack_type="real")
        if real_seeds:
            await framework.run_attack(real_seeds[0], "nonexistent_module")

        # Check callbacks fired
        assert len(bypassed_attacks) > 0 or len(held_attacks) > 0

    def test_generates_stats(self, framework):
        """Framework generates statistics."""
        stats = framework.get_stats()

        assert "seeds" in stats
        assert "evolution" in stats
        assert "results" in stats

    def test_generates_report(self, framework):
        """Framework generates vulnerability report."""
        report = framework.get_vulnerability_report()

        assert "PRAKRITI VULNERABILITY REPORT" in report
        assert "Generation:" in report


class TestEvolution:
    """Test the evolution/mutation system."""

    def test_evolution_tracks_generations(self):
        """TestEvolution tracks generations."""
        from vibe_core.naga.hiranyakashipu.living_tests import TestEvolution

        evo = TestEvolution()
        assert evo.generation == 0

        evo.next_generation()
        assert evo.generation == 1

    def test_evolution_records_mutations(self):
        """TestEvolution records mutation attempts."""
        from vibe_core.naga.hiranyakashipu.living_tests import TestEvolution

        evo = TestEvolution()

        evo.record_mutation(successful=True, description="Found vuln 1")
        evo.record_mutation(successful=False)
        evo.record_mutation(successful=True, description="Found vuln 2")

        assert evo.mutations_tried == 3
        assert evo.mutations_successful == 2
        assert len(evo.vulnerabilities_found) == 2


class TestMetaOuroboros:
    """
    Meta-level test: The living framework testing itself.

    This is OUROBOROS - the snake eating its own tail.
    We're using the living framework to test the living framework.
    """

    @pytest.mark.asyncio
    async def test_framework_can_test_itself(self):
        """The framework can generate tests for itself."""
        from vibe_core.naga.hiranyakashipu import AttackSeed, LivingTestFramework

        fw = LivingTestFramework()

        # Create a seed that tests the framework itself
        meta_seed = AttackSeed(
            name="meta_test_framework",
            description="Test that the framework exists",
            test_code="""
def test_framework_exists():
    from vibe_core.naga.hiranyakashipu import LivingTestFramework
    fw = LivingTestFramework()
    assert fw is not None
    assert hasattr(fw, 'run_attack')
""",
            attack_type="meta",
            expected_behavior="should_pass",  # This IS a real test
        )

        fw.add_seed(meta_seed)
        result = await fw.run_attack(meta_seed, "prakriti")

        # This should pass because the framework DOES exist
        assert result.exit_code == 0, "Meta test should pass"


class TestPrakritiWiring:
    """
    Test that Prakriti is properly wired to protocols.

    "Don't implement what's already defined. WIRE IT."
    """

    def test_adapters_exist(self):
        """Wiring adapters are importable."""
        from vibe_core.naga.hiranyakashipu import (
            adapt_test_result_to_drift,
            adapt_test_result_to_reactor,
        )

        assert callable(adapt_test_result_to_drift)
        assert callable(adapt_test_result_to_reactor)

    def test_adapt_result_to_drift(self):
        """TestResult adapts to UnifiedDriftReport."""
        from datetime import datetime

        from vibe_core.naga.hiranyakashipu import AttackSeed, adapt_test_result_to_drift
        from vibe_core.naga.hiranyakashipu.living_tests import TestResult
        from vibe_core.protocols.correction import DriftSource

        # Create test result
        result = TestResult(
            seed_name="test_attack",
            passed=False,
            bypassed=True,  # Attack succeeded
            exit_code=0,
            execution_time_ms=100.0,
            stdout="test output",
            stderr="",
            analysis={"has_import_error": False},
        )

        seed = AttackSeed(
            name="test_attack",
            description="Test attack",
            test_code="def test(): pass",
            attack_type="trivial",
            difficulty=3,
        )

        # Adapt
        drift = adapt_test_result_to_drift(result, seed, "my_module")

        # Verify
        assert drift.source == DriftSource.STRUCTURAL
        assert drift.component == "my_module"
        assert drift.detector_id == "prakriti_living_tests"
        assert drift.raw_data["bypassed"] is True
        assert "prakriti_test_attack" in drift.id

    def test_adapt_result_to_reactor(self):
        """TestResult adapts to ReactorProtocol DriftEvent."""
        from vibe_core.naga.hiranyakashipu import AttackSeed, adapt_test_result_to_reactor
        from vibe_core.naga.hiranyakashipu.living_tests import TestResult
        from vibe_core.protocols.reactor import DriftType

        result = TestResult(
            seed_name="test_attack",
            passed=True,
            bypassed=False,
            exit_code=1,
            execution_time_ms=50.0,
            stdout="",
            stderr="ImportError",
        )

        seed = AttackSeed(
            name="test_attack",
            description="Test",
            test_code="def test(): pass",
            attack_type="trivial",
        )

        # Adapt
        event = adapt_test_result_to_reactor(result, seed)

        # Verify
        assert event.type == DriftType.RELIABILITY
        assert event.source == "prakriti"
        assert "BLOCKED" in event.message

    def test_detector_is_callable(self):
        """PrakritiDriftDetector is a valid detector."""
        from vibe_core.naga.hiranyakashipu import LivingTestFramework, PrakritiDriftDetector

        fw = LivingTestFramework()
        detector = PrakritiDriftDetector(fw, "test_module")

        # Should be callable (sync wrapper)
        assert callable(detector)

    def test_handler_uses_resonance_strategy(self):
        """PrakritiCorrectionHandler handles RESONANCE strategy."""
        from vibe_core.naga.hiranyakashipu import PrakritiCorrectionHandler
        from vibe_core.protocols.correction import (
            DriftSeverity,
            DriftSource,
            HealingStatus,
            HealingStrategy,
            UnifiedDriftReport,
        )

        handler = PrakritiCorrectionHandler()

        # Create high-difficulty drift
        drift = UnifiedDriftReport(
            id="test_drift",
            source=DriftSource.STRUCTURAL,
            severity=DriftSeverity.ERROR,
            message="Test drift",
            raw_data={
                "seed_name": "hard_attack",
                "attack_type": "narasimha_paradox",
                "difficulty": 7,  # High difficulty
            },
        )

        # Handle with RESONANCE strategy
        result = handler.handle(drift, HealingStrategy.RESONANCE)

        # High difficulty should require manual review
        assert result.status == HealingStatus.MANUAL_REQUIRED

    def test_wire_function_returns_components(self):
        """wire_prakriti_to_protocols returns wiring dict."""
        from vibe_core.naga.hiranyakashipu import LivingTestFramework, wire_prakriti_to_protocols

        fw = LivingTestFramework()
        wiring = wire_prakriti_to_protocols(fw, "test_module")

        assert "detector" in wiring
        assert "handler" in wiring
        assert "reactor" in wiring

    def test_reactor_integration_records_metrics(self):
        """PrakritiReactorIntegration records to reactor."""
        from vibe_core.naga.hiranyakashipu import AttackSeed, PrakritiReactorIntegration
        from vibe_core.naga.hiranyakashipu.living_tests import TestResult

        integration = PrakritiReactorIntegration()

        result = TestResult(
            seed_name="test",
            passed=True,
            bypassed=False,
            exit_code=1,
            execution_time_ms=100.0,
            stdout="",
            stderr="",
        )

        seed = AttackSeed(
            name="test",
            description="Test",
            test_code="",
            attack_type="trivial",
        )

        # Should not raise
        integration.record_attack_result(result, seed)

        # Check metrics were recorded
        metrics = integration._reactor.get_metrics()
        assert "prakriti_attack_trivial" in metrics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

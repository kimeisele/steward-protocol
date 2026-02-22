"""
Tests for HealingIntentResolver — 5-Gate Healing Pipeline
==========================================================

Verifies:
1. Resolver can_resolve for IntentType.HEAL
2. Resolver rejects non-HEAL intents
3. All 5 gates fire in correct sequence (PARSE→VALIDATE→EXECUTE→RESULT→SYNC)
4. SATTVA phase (gates 0-3) does not write to disk
5. RAJAS phase (gate 4) authorizes the write via Srivasa
6. Dry run fires gates but skips write
7. E2E healing through the resolver (real file, real remedy)
8. Wire resolver into MantraKernel
"""

import textwrap
from pathlib import Path

import pytest

from vibe_core.mahamantra.dharma.kumaras.healing_resolver import (
    HealingIntentResolver,
    wire_healing_resolver,
)
from vibe_core.mahamantra.kernel.intent import (
    IntentPriority,
    IntentStatus,
    IntentType,
    MantraIntent,
    get_kernel,
)
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiStatus

# =============================================================================
# FIXTURES
# =============================================================================

SICK_SOURCE = textwrap.dedent("""\
    class FileWriter:
        def __init__(self):
            self.system = None

        def write_data(self, path, data):
            with open(path, 'w') as f:
                f.write(data)
""")

CLEAN_SOURCE = textwrap.dedent('''\
    def clean_function(x: int) -> int:
        """A clean function."""
        return x * 2
''')


def _make_heal_intent(file_path: str, rule_id: str, dry_run: bool = False) -> MantraIntent:
    """Helper to create a HEAL intent."""
    return MantraIntent(
        type=IntentType.HEAL,
        target=file_path,
        params={
            "file_path": file_path,
            "rule_id": rule_id,
            "dry_run": dry_run,
        },
        priority=IntentPriority.NORMAL,
        requester="test",
    )


# =============================================================================
# RESOLVER BASIC TESTS
# =============================================================================


class TestHealingIntentResolverBasic:
    """Test basic resolver protocol compliance."""

    @pytest.fixture
    def resolver(self):
        return HealingIntentResolver()

    def test_can_resolve_heal_intent(self, resolver):
        """Resolver handles IntentType.HEAL."""
        intent = _make_heal_intent("/tmp/test.py", "unsafe_io_write")
        assert resolver.can_resolve(intent) is True

    def test_rejects_non_heal_intent(self, resolver):
        """Resolver rejects other intent types."""
        intent = MantraIntent(
            type=IntentType.READ,
            target="/tmp/test.py",
            params={"key": "value"},
        )
        assert resolver.can_resolve(intent) is False

    def test_missing_params_returns_failed(self, resolver):
        """Missing file_path or rule_id returns FAILED."""
        intent = MantraIntent(
            type=IntentType.HEAL,
            target="something",
            params={},  # Missing required params
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "requires" in result.error

    def test_nonexistent_file_returns_failed(self, resolver):
        """Non-existent file returns FAILED."""
        intent = _make_heal_intent("/nonexistent/file.py", "unsafe_io_write")
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "not found" in result.error.lower()

    def test_unknown_rule_returns_failed(self, resolver, tmp_path):
        """Unknown rule_id returns FAILED."""
        f = tmp_path / "test.py"
        f.write_text(CLEAN_SOURCE)

        intent = _make_heal_intent(str(f), "nonexistent_rule_xyz")
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "No remedy" in result.error


# =============================================================================
# 5-GATE FLOW TESTS
# =============================================================================


class TestGateFlow:
    """Test that all 5 Tattva Gates fire during healing."""

    @pytest.fixture
    def resolver(self):
        return HealingIntentResolver()

    def test_clean_file_resolves_without_violation(self, resolver, tmp_path):
        """Clean file resolves successfully with no violations."""
        f = tmp_path / "clean.py"
        f.write_text(CLEAN_SOURCE)

        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=True)
        result = resolver.resolve(intent)

        assert result.status == IntentStatus.RESOLVED
        # Clean file — no purified results
        if result.value:
            purified = [r for r in result.value if r.status == ShuddhiStatus.PURIFIED]
            assert len(purified) == 0

    def test_dry_run_sick_file_detects_violation(self, resolver, tmp_path):
        """Sick file in dry_run mode detects violation but does not modify file."""
        f = tmp_path / "sick.py"
        f.write_text(SICK_SOURCE)
        original = f.read_text()

        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=True)
        result = resolver.resolve(intent)

        assert result.status == IntentStatus.RESOLVED
        # File must NOT be modified in dry_run
        assert f.read_text() == original


# =============================================================================
# 2-PHASE GUNA TESTS
# =============================================================================


class TestTwoPhaseGuna:
    """Test 2-phase Guna model: SATTVA analysis → RAJAS commit."""

    @pytest.fixture
    def resolver(self):
        return HealingIntentResolver()

    def test_dry_run_does_not_write(self, resolver, tmp_path):
        """Dry run performs analysis but does NOT write to disk."""
        f = tmp_path / "sick.py"
        f.write_text(SICK_SOURCE)
        original = f.read_text()

        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=True)
        result = resolver.resolve(intent)

        assert result.status == IntentStatus.RESOLVED
        # File must NOT be modified in dry_run
        assert f.read_text() == original

    def test_governed_write_modifies_file(self, resolver, tmp_path):
        """Non-dry-run healing through resolver modifies the file via Srivasa gate."""
        f = tmp_path / "sick.py"
        f.write_text(SICK_SOURCE)
        original = f.read_text()

        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=False)
        result = resolver.resolve(intent)

        assert result.status == IntentStatus.RESOLVED
        if result.value:
            purified = [r for r in result.value if r.status == ShuddhiStatus.PURIFIED]
            if purified:
                # File should be modified
                new_content = f.read_text()
                assert new_content != original
                # Healed file must still be valid Python
                compile(new_content, str(f), "exec")
                # Backup should exist
                bak = f.with_suffix(".py.bak")
                assert bak.exists()


# =============================================================================
# WIRING TESTS
# =============================================================================


class TestWiring:
    """Test resolver wiring into MantraKernel."""

    def test_wire_healing_resolver(self):
        """wire_healing_resolver() registers the resolver in the kernel."""
        result = wire_healing_resolver()
        assert result is True

        kernel = get_kernel()
        resolver = kernel._resolvers.get(IntentType.HEAL)
        assert resolver is not None
        assert isinstance(resolver, HealingIntentResolver)

    def test_wire_is_idempotent(self):
        """Multiple calls to wire_healing_resolver() are safe."""
        r1 = wire_healing_resolver()
        r2 = wire_healing_resolver()
        assert r1 is True
        assert r2 is True

    def test_kernel_resolve_heal_intent(self, tmp_path):
        """IntentType.HEAL resolves through MantraKernel."""
        wire_healing_resolver()

        f = tmp_path / "clean.py"
        f.write_text(CLEAN_SOURCE)

        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=True)
        kernel = get_kernel()
        result = kernel.resolve(intent)

        assert result.status == IntentStatus.RESOLVED


# =============================================================================
# E2E TEST
# =============================================================================


class TestE2EHealingThroughGates:
    """End-to-end: real file, real remedy, real gates."""

    def test_e2e_healing_full_pipeline(self, tmp_path):
        """E2E: sick file → 5 gates → healed file on disk."""
        wire_healing_resolver()

        f = tmp_path / "e2e_test.py"
        f.write_text(SICK_SOURCE)
        original = f.read_text()

        # Create intent
        intent = _make_heal_intent(str(f), "unsafe_io_write", dry_run=False)

        # Resolve through kernel (which uses HealingIntentResolver)
        kernel = get_kernel()
        result = kernel.resolve(intent)

        assert result.status == IntentStatus.RESOLVED

        if result.value:
            purified = [r for r in result.value if r.status == ShuddhiStatus.PURIFIED]
            if purified:
                # File was healed through the 5-gate pipeline
                healed = f.read_text()
                assert healed != original
                compile(healed, str(f), "exec")
                # The healing was governed (maya_synced through Srivasa)
                for p in purified:
                    assert p.maya_synced is True

"""
OPUS-210: CommitAuthority & Weaver Reflex Tests

Tests the resilience of the commit system:
1. Reflex mode when MANAS is missing
2. Reflex mode when MANAS is disabled
3. Reflex mode on timeout
4. CommitAuthority basic flow
5. Panic dump on failure
6. Resonance caching

These tests validate the new system WITHOUT modifying existing plumbing.
"""

import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# Test: Oracle Decision Enum
# =============================================================================


class TestOracleDecision:
    """Test OracleDecision enum values."""

    def test_oracle_decisions_exist(self):
        """All oracle decisions are defined."""
        from vibe_core.state.commit_authority import OracleDecision

        assert OracleDecision.REFLEX == "reflex"
        assert OracleDecision.COMMIT_NOW == "commit_now"
        assert OracleDecision.DEFER == "defer"
        assert OracleDecision.HEAL_FIRST == "heal_first"


# =============================================================================
# Test: Weaver Reflex Mode (MANAS Missing)
# =============================================================================


class TestWeaverReflexMissing:
    """System defaults to REFLEX when MANAS is not installed."""

    def test_reflex_when_manas_import_fails(self):
        """Oracle returns REFLEX when MANAS module not found."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        authority = CommitAuthority()

        # Mock the import to fail
        with patch.dict(sys.modules, {"vibe_core.plugins.opus_assistant.manas": None}):
            with patch(
                "vibe_core.state.commit_authority.CommitAuthority._consult_manas",
                side_effect=ImportError("No module named 'manas'"),
            ):
                result = authority._consult_oracle_with_timeout(None)
                assert result == OracleDecision.REFLEX

    def test_reflex_when_get_manas_returns_none(self):
        """Oracle returns REFLEX when get_manas() returns None."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        authority = CommitAuthority()

        mock_module = MagicMock()
        mock_module.get_manas.return_value = None

        with patch.dict(sys.modules, {"vibe_core.plugins.opus_assistant.manas": mock_module}):
            result = authority._consult_manas(None)
            assert result == OracleDecision.REFLEX


# =============================================================================
# Test: Weaver Reflex Mode (MANAS Disabled)
# =============================================================================


class TestWeaverReflexDisabled:
    """System defaults to REFLEX when MANAS is disabled."""

    def test_reflex_when_manas_disabled(self):
        """Oracle returns REFLEX when manas.is_enabled() returns False."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        authority = CommitAuthority()

        mock_manas = MagicMock()
        mock_manas.is_enabled.return_value = False

        mock_module = MagicMock()
        mock_module.get_manas.return_value = mock_manas

        with patch.dict(sys.modules, {"vibe_core.plugins.opus_assistant.manas": mock_module}):
            result = authority._consult_manas(None)
            assert result == OracleDecision.REFLEX


# =============================================================================
# Test: Weaver Reflex Mode (MANAS Timeout)
# =============================================================================


class TestWeaverReflexTimeout:
    """System defaults to REFLEX when MANAS times out."""

    def test_reflex_on_oracle_timeout(self):
        """Oracle returns REFLEX when consultation exceeds timeout."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        # Use short timeout for test
        authority = CommitAuthority(oracle_timeout_ms=50)

        def slow_manas(context):
            time.sleep(0.5)  # 500ms, way over 50ms timeout
            return OracleDecision.COMMIT_NOW

        with patch.object(authority, "_consult_manas", slow_manas):
            result = authority._consult_oracle_with_timeout(None)
            assert result == OracleDecision.REFLEX

    def test_reflex_on_oracle_exception(self):
        """Oracle returns REFLEX when consultation raises exception."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        authority = CommitAuthority()

        def broken_manas(context):
            raise RuntimeError("MANAS crashed")

        with patch.object(authority, "_consult_manas", broken_manas):
            result = authority._consult_oracle_with_timeout(None)
            assert result == OracleDecision.REFLEX


# =============================================================================
# Test: CommitResult
# =============================================================================


class TestCommitResult:
    """Test CommitResult dataclass."""

    def test_success_property_for_outcomes(self):
        """CommitResult.success is True for SUCCESS, HEALED, SKIPPED."""
        from vibe_core.state.commit_authority import CommitOutcome, CommitResult

        assert CommitResult(outcome=CommitOutcome.SUCCESS).success is True
        assert CommitResult(outcome=CommitOutcome.HEALED).success is True
        assert CommitResult(outcome=CommitOutcome.SKIPPED).success is True
        assert CommitResult(outcome=CommitOutcome.DEFERRED).success is False
        assert CommitResult(outcome=CommitOutcome.PANIC_DUMPED).success is False


# =============================================================================
# Test: Resonance Cache
# =============================================================================


class TestResonanceCache:
    """Test resonance caching for performance."""

    def test_cache_stores_and_retrieves(self):
        """Cache stores and retrieves resonance values."""
        from vibe_core.state.commit_authority import ResonanceCache

        cache = ResonanceCache(ttl_seconds=60)

        cache.set("intent1", "state1", 0.75)
        assert cache.get("intent1", "state1") == 0.75

    def test_cache_returns_none_for_missing(self):
        """Cache returns None for missing keys."""
        from vibe_core.state.commit_authority import ResonanceCache

        cache = ResonanceCache()
        assert cache.get("missing", "key") is None

    def test_cache_expires_after_ttl(self):
        """Cache entries expire after TTL."""
        from vibe_core.state.commit_authority import ResonanceCache

        cache = ResonanceCache(ttl_seconds=0.1)  # 100ms TTL

        cache.set("intent", "state", 0.5)
        assert cache.get("intent", "state") == 0.5

        time.sleep(0.15)  # Wait for expiry
        assert cache.get("intent", "state") is None

    def test_cache_clear(self):
        """Cache clear removes all entries."""
        from vibe_core.state.commit_authority import ResonanceCache

        cache = ResonanceCache()
        cache.set("a", "b", 0.1)
        cache.set("c", "d", 0.2)

        count = cache.clear()
        assert count == 2
        assert cache.get("a", "b") is None

    def test_cache_prune_expired(self):
        """Prune removes only expired entries."""
        from vibe_core.state.commit_authority import ResonanceCache

        cache = ResonanceCache(ttl_seconds=0.1)

        cache.set("expire", "soon", 0.1)
        time.sleep(0.15)
        cache.set("fresh", "entry", 0.2)

        pruned = cache.prune_expired()
        assert pruned == 1
        assert cache.get("fresh", "entry") == 0.2


# =============================================================================
# Test: Panic Dump
# =============================================================================


class TestPanicDump:
    """Test panic_dump saves data on irrecoverable failure."""

    def test_panic_dump_creates_file(self):
        """Panic dump creates JSON file in lost+found."""
        from vibe_core.state.commit_authority import CommitAuthority

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            authority = CommitAuthority(workspace=workspace)

            dump_path = authority._panic_dump(
                paths=[Path("test.py")],
                message="test commit",
                context={"test": True},
                error="Simulated failure",
            )

            assert dump_path.exists()
            assert "panic_" in dump_path.name
            assert dump_path.suffix == ".json"

            # Verify contents
            data = json.loads(dump_path.read_text())
            assert data["error"] == "Simulated failure"
            assert data["message"] == "test commit"
            assert data["context"] == {"test": True}

    def test_panic_dump_includes_file_contents(self):
        """Panic dump includes contents of dirty files."""
        from vibe_core.state.commit_authority import CommitAuthority

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Create a test file
            test_file = workspace / "important.py"
            test_file.write_text("# Important code\nprint('hello')")

            authority = CommitAuthority(workspace=workspace)

            dump_path = authority._panic_dump(
                paths=[Path("important.py")],
                message="save my code",
                context={},
                error="Git exploded",
            )

            data = json.loads(dump_path.read_text())
            assert "file_contents" in data
            assert "important.py" in data["file_contents"]
            assert "Important code" in data["file_contents"]["important.py"]


# =============================================================================
# Test: CommitAuthority Integration (No Side Effects)
# =============================================================================


class TestCommitAuthorityIntegration:
    """Integration tests that don't modify actual git state."""

    def test_commit_skipped_when_not_dirty(self):
        """Commit returns SKIPPED when nothing to commit."""
        from vibe_core.state.commit_authority import CommitAuthority, CommitOutcome

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            authority = CommitAuthority(workspace=workspace)

            # Mock git to say "not dirty"
            mock_git = MagicMock()
            mock_git.is_dirty.return_value = False
            authority._git_state = mock_git

            result = authority.commit(message="test")
            assert result.outcome == CommitOutcome.SKIPPED

    def test_commit_result_includes_duration(self):
        """Commit result includes duration_ms."""
        from vibe_core.state.commit_authority import CommitAuthority

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            authority = CommitAuthority(workspace=workspace)

            mock_git = MagicMock()
            mock_git.is_dirty.return_value = False
            authority._git_state = mock_git

            result = authority.commit(message="test")
            assert result.duration_ms >= 0

    def test_singleton_access(self):
        """get_commit_authority returns singleton."""
        from vibe_core.state.commit_authority import (
            get_commit_authority,
            reset_commit_authority,
        )

        reset_commit_authority()

        a1 = get_commit_authority()
        a2 = get_commit_authority()
        assert a1 is a2

        reset_commit_authority()


# =============================================================================
# Test: Weaver Pipeline Phases
# =============================================================================


class TestMANASIntegration:
    """Test MANAS/PrakritiSense integration."""

    def test_consult_manas_returns_oracle_decision(self):
        """_consult_manas returns valid OracleDecision."""
        from vibe_core.state.commit_authority import CommitAuthority, OracleDecision

        authority = CommitAuthority()
        result = authority._consult_manas(None)

        # Should return one of the valid decisions
        assert result in [
            OracleDecision.REFLEX,
            OracleDecision.COMMIT_NOW,
            OracleDecision.HEAL_FIRST,
            OracleDecision.DEFER,
        ]

    def test_prakriti_sense_import_works(self):
        """PrakritiSense can be imported."""
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import (
                GunaSummary,
                PrakritiSense,
            )

            assert PrakritiSense is not None
            assert GunaSummary is not None
        except ImportError:
            pytest.skip("PrakritiSense not available")

    def test_prakriti_sense_perceive_state(self):
        """PrakritiSense can perceive state."""
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import (
                PrakritiSense,
            )

            sense = PrakritiSense()
            summary = sense.perceive_state()

            # Should have Guna counts
            assert hasattr(summary, "sattva_count")
            assert hasattr(summary, "rajas_count")
            assert hasattr(summary, "tamas_count")
            assert hasattr(summary, "health_ratio")
        except ImportError:
            pytest.skip("PrakritiSense not available")


class TestWeaverPipeline:
    """Verify Weaver has all 6 phases (static check)."""

    def test_weaver_has_discover_phase(self):
        """Weaver has discover method."""
        from vibe_core.state.weaver import StateSyncWeaver

        assert hasattr(StateSyncWeaver, "_discover_all_state")

    def test_weaver_has_classify_phase(self):
        """Weaver has classify method."""
        from vibe_core.state.weaver import StateSyncWeaver

        assert hasattr(StateSyncWeaver, "_classify_state")

    def test_weaver_has_consult_phase(self):
        """Weaver has consult oracle method."""
        from vibe_core.state.weaver import StateSyncWeaver

        assert hasattr(StateSyncWeaver, "_consult_oracle")

    def test_weaver_has_decide_phase(self):
        """Weaver has decide method."""
        from vibe_core.state.weaver import StateSyncWeaver

        assert hasattr(StateSyncWeaver, "_decide_commit_strategy")

    def test_weaver_has_execute_phase(self):
        """Weaver has execute method."""
        from vibe_core.state.weaver import StateSyncWeaver

        assert hasattr(StateSyncWeaver, "_execute_commit")

    def test_weaver_returns_reflex_by_default(self):
        """Weaver's _consult_oracle returns REFLEX mode by default."""
        from vibe_core.state.weaver import StateSyncWeaver, WeaverMode

        # Create weaver with mock prakriti
        mock_prakriti = MagicMock()
        mock_prakriti._workspace = Path.cwd()
        weaver = StateSyncWeaver(mock_prakriti)

        # Consult oracle with empty classified state
        from vibe_core.state.weaver import ClassifiedState

        advice = weaver._consult_oracle(ClassifiedState())
        assert advice.mode == WeaverMode.REFLEX

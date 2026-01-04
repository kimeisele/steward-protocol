"""
Tests for NAGA Commit Watcher.

Tests the Wächter-Pattern:
- Pattern detection for failures
- Alert generation
- Stagnation detection
- Deferral loop detection
"""

import time
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# MOCK COMMIT RESULT
# =============================================================================


@dataclass
class MockCommitResult:
    """Mock CommitResult for testing."""

    outcome: str
    sha: str = None
    message: str = ""


# =============================================================================
# TESTS
# =============================================================================


class TestCommitWatcherBasics:
    """Test basic watcher functionality."""

    @pytest.fixture
    def watcher(self):
        """Create watcher without services."""
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        return NagaCommitWatcher(sesha=None, takshaka=None, enabled=True)

    @pytest.fixture
    def commit_outcome(self):
        """Get CommitOutcome enum."""
        from vibe_core.state.commit_authority import CommitOutcome

        return CommitOutcome

    def test_initial_stats(self, watcher):
        """Stats should be initialized to zero."""
        stats = watcher.get_stats()
        assert stats["total_observed"] == 0
        assert stats["success_count"] == 0
        assert stats["panic_count"] == 0

    def test_observe_success(self, watcher, commit_outcome):
        """Should track successful commits."""
        from vibe_core.state.commit_authority import CommitResult

        result = CommitResult(outcome=commit_outcome.SUCCESS, sha="abc123")

        watcher.observe(result)

        stats = watcher.get_stats()
        assert stats["total_observed"] == 1
        assert stats["success_count"] == 1
        assert stats["last_success_ago"] is not None

    def test_observe_skipped(self, watcher, commit_outcome):
        """Should track skipped commits."""
        from vibe_core.state.commit_authority import CommitResult

        result = CommitResult(outcome=commit_outcome.SKIPPED)

        watcher.observe(result)

        stats = watcher.get_stats()
        assert stats["skipped_count"] == 1

    def test_observe_panic(self, watcher, commit_outcome):
        """Should track panic dumps."""
        from vibe_core.state.commit_authority import CommitResult

        result = CommitResult(outcome=commit_outcome.PANIC_DUMPED)

        watcher.observe(result)

        stats = watcher.get_stats()
        assert stats["panic_count"] == 1

    def test_disabled_watcher_does_nothing(self, commit_outcome):
        """Disabled watcher should return None."""
        from vibe_core.naga.commit_watcher import NagaCommitWatcher
        from vibe_core.state.commit_authority import CommitResult

        watcher = NagaCommitWatcher(enabled=False)
        result = CommitResult(outcome=commit_outcome.PANIC_DUMPED)

        alert = watcher.observe(result)

        assert alert is None
        assert watcher.get_stats()["total_observed"] == 0


class TestPanicPatternDetection:
    """Test panic pattern detection."""

    @pytest.fixture
    def watcher(self):
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        watcher = NagaCommitWatcher(enabled=True)
        # Lower threshold for testing
        watcher.PANIC_THRESHOLD = 2
        watcher.PANIC_WINDOW_SECONDS = 60
        return watcher

    @pytest.fixture
    def commit_outcome(self):
        from vibe_core.state.commit_authority import CommitOutcome

        return CommitOutcome

    def test_single_panic_no_alert(self, watcher, commit_outcome):
        """Single panic should not trigger alert."""
        from vibe_core.state.commit_authority import CommitResult

        result = CommitResult(outcome=commit_outcome.PANIC_DUMPED)

        alert = watcher.observe(result)

        assert alert is None

    def test_multiple_panics_triggers_alert(self, watcher, commit_outcome):
        """Multiple panics in window should trigger alert."""
        from vibe_core.state.commit_authority import CommitResult

        # First panic
        result1 = CommitResult(outcome=commit_outcome.PANIC_DUMPED)
        alert1 = watcher.observe(result1)
        assert alert1 is None

        # Second panic (reaches threshold of 2)
        result2 = CommitResult(outcome=commit_outcome.PANIC_DUMPED)
        alert2 = watcher.observe(result2)

        assert alert2 is not None
        assert alert2.alert_type == "PANIC_PATTERN"
        assert alert2.severity == "CRITICAL"


class TestDeferralLoopDetection:
    """Test deferral loop detection."""

    @pytest.fixture
    def watcher(self):
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        watcher = NagaCommitWatcher(enabled=True)
        watcher.DEFERRAL_THRESHOLD = 3
        return watcher

    @pytest.fixture
    def commit_outcome(self):
        from vibe_core.state.commit_authority import CommitOutcome

        return CommitOutcome

    def test_few_deferrals_no_alert(self, watcher, commit_outcome):
        """Few deferrals should not trigger alert."""
        from vibe_core.state.commit_authority import CommitResult

        for _ in range(2):
            result = CommitResult(outcome=commit_outcome.DEFERRED)
            alert = watcher.observe(result)
            assert alert is None

    def test_many_deferrals_triggers_alert(self, watcher, commit_outcome):
        """Consecutive deferrals should trigger alert."""
        from vibe_core.state.commit_authority import CommitResult

        alert = None
        for i in range(4):
            result = CommitResult(outcome=commit_outcome.DEFERRED)
            alert = watcher.observe(result)

        assert alert is not None
        assert alert.alert_type == "DEFERRAL_LOOP"
        assert alert.severity == "WARNING"

    def test_success_resets_deferral_count(self, watcher, commit_outcome):
        """Success should reset consecutive deferral count."""
        from vibe_core.state.commit_authority import CommitResult

        # Two deferrals
        for _ in range(2):
            result = CommitResult(outcome=commit_outcome.DEFERRED)
            watcher.observe(result)

        # One success resets
        success = CommitResult(outcome=commit_outcome.SUCCESS, sha="abc")
        watcher.observe(success)

        assert watcher._consecutive_deferrals == 0


class TestConflictDriftDetection:
    """Test conflict drift detection."""

    @pytest.fixture
    def watcher(self):
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        watcher = NagaCommitWatcher(enabled=True)
        watcher.CONFLICT_RATE_THRESHOLD = 0.5
        return watcher

    @pytest.fixture
    def commit_outcome(self):
        from vibe_core.state.commit_authority import CommitOutcome

        return CommitOutcome

    def test_high_healed_rate_triggers_alert(self, watcher, commit_outcome):
        """High healed rate should trigger alert."""
        from vibe_core.state.commit_authority import CommitResult

        # Generate 20 observations: 12 healed (60% > 50% threshold)
        alert = None
        for i in range(20):
            if i < 12:
                outcome = commit_outcome.HEALED
            else:
                outcome = commit_outcome.SUCCESS

            result = CommitResult(outcome=outcome, sha=f"sha{i}")
            alert = watcher.observe(result)

        # Alert should be generated at observation 20 (throttled)
        assert alert is not None
        assert alert.alert_type == "CONFLICT_DRIFT"


class TestAlertHandlers:
    """Test alert handler dispatch."""

    @pytest.fixture
    def watcher(self):
        from vibe_core.naga.commit_watcher import NagaCommitWatcher

        watcher = NagaCommitWatcher(enabled=True)
        watcher.PANIC_THRESHOLD = 1  # Immediate trigger
        return watcher

    @pytest.fixture
    def commit_outcome(self):
        from vibe_core.state.commit_authority import CommitOutcome

        return CommitOutcome

    def test_handler_called_on_alert(self, watcher, commit_outcome):
        """Handler should be called when alert generated."""
        from vibe_core.state.commit_authority import CommitResult

        handler_called = []

        def test_handler(alert):
            handler_called.append(alert)

        watcher.add_alert_handler(test_handler)

        result = CommitResult(outcome=commit_outcome.PANIC_DUMPED)
        watcher.observe(result)

        assert len(handler_called) == 1
        assert handler_called[0].alert_type == "PANIC_PATTERN"

    def test_handler_error_is_silent(self, watcher, commit_outcome):
        """Handler errors should not propagate."""
        from vibe_core.state.commit_authority import CommitResult

        def bad_handler(alert):
            raise Exception("Handler crashed!")

        watcher.add_alert_handler(bad_handler)

        result = CommitResult(outcome=commit_outcome.PANIC_DUMPED)

        # Should not raise
        watcher.observe(result)


class TestCommitAlert:
    """Test CommitAlert dataclass."""

    def test_alert_to_dict(self):
        """Alert should serialize to dict."""
        from vibe_core.naga.commit_watcher import CommitAlert

        alert = CommitAlert(
            alert_type="PANIC_PATTERN",
            severity="CRITICAL",
            message="Test message",
            details={"count": 5},
        )

        d = alert.to_dict()

        assert d["alert_type"] == "PANIC_PATTERN"
        assert d["severity"] == "CRITICAL"
        assert d["message"] == "Test message"
        assert d["details"]["count"] == 5
        assert "timestamp" in d


class TestCommitStats:
    """Test CommitStats dataclass."""

    def test_stats_to_dict(self):
        """Stats should serialize to dict."""
        from vibe_core.naga.commit_watcher import CommitStats

        stats = CommitStats()
        stats.total_observed = 100
        stats.success_count = 80
        stats.panic_count = 5

        d = stats.to_dict()

        assert d["total_observed"] == 100
        assert d["success_count"] == 80
        assert d["panic_count"] == 5
        assert d["success_rate"] == 0.8
        assert "uptime_seconds" in d


class TestWrapCommit:
    """Test wrap_commit_with_watcher helper."""

    def test_wrapper_observes_result(self):
        """Wrapper should observe commit results."""
        from vibe_core.naga.commit_watcher import (
            NagaCommitWatcher,
            wrap_commit_with_watcher,
        )
        from vibe_core.state.commit_authority import CommitOutcome, CommitResult

        watcher = NagaCommitWatcher(enabled=True)

        def mock_commit():
            return CommitResult(outcome=CommitOutcome.SUCCESS, sha="test123")

        wrapped = wrap_commit_with_watcher(mock_commit, watcher)

        # Call wrapped function
        result = wrapped()

        assert result.sha == "test123"
        assert watcher.get_stats()["total_observed"] == 1
        assert watcher.get_stats()["success_count"] == 1

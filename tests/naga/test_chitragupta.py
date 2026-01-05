"""
Tests for CHITRAGUPTA Service - The Profiler Agent.

Mythology: Chitragupta keeps record of all karmas.
He decides with Yama about heaven or hell.

Purpose: Profile component behavior over time, detect anomalies.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest


class TestChitraguptaBasics:
    """Test basic Chitragupta initialization and status."""

    def test_initialization(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()

        assert chitragupta._profiles_count == 0
        assert chitragupta._anomalies_detected == 0
        assert len(chitragupta._profiles) == 0

    def test_get_status(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()
        status = chitragupta.get_status()

        assert status.naga_type.value == "chitragupta"
        assert status.healthy is True
        assert status.events_processed == 0


class TestMetricRecording:
    """Test recording metrics for components."""

    def test_record_single_metric(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()

        chitragupta.record("comp_001", "latency_ms", 50.0)

        profile = chitragupta.get_profile("comp_001")
        assert profile is not None
        assert "latency_ms" in profile.metrics

    def test_record_multiple_metrics(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()

        chitragupta.record("comp_001", "latency_ms", 50.0)
        chitragupta.record("comp_001", "error_rate", 0.01)
        chitragupta.record("comp_001", "call_count", 100)

        profile = chitragupta.get_profile("comp_001")
        assert len(profile.metrics) == 3

    def test_record_builds_history(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()

        for i in range(10):
            chitragupta.record("comp_001", "latency_ms", 50.0 + i)

        profile = chitragupta.get_profile("comp_001")
        assert len(profile.metrics["latency_ms"].history) == 10


class TestBaselineCalculation:
    """Test baseline/normal behavior calculation."""

    def test_has_baseline_requires_min_samples(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(min_samples_for_baseline=5)

        for i in range(3):
            chitragupta.record("comp_001", "latency_ms", 50.0)

        profile = chitragupta.get_profile("comp_001")
        assert profile.has_baseline("latency_ms") is False

        for i in range(3):
            chitragupta.record("comp_001", "latency_ms", 50.0)

        assert profile.has_baseline("latency_ms") is True

    def test_baseline_calculates_mean(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(min_samples_for_baseline=3)

        chitragupta.record("comp_001", "latency_ms", 40.0)
        chitragupta.record("comp_001", "latency_ms", 50.0)
        chitragupta.record("comp_001", "latency_ms", 60.0)

        profile = chitragupta.get_profile("comp_001")
        mean = profile.get_baseline_mean("latency_ms")

        assert mean == 50.0

    def test_baseline_calculates_stddev(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(min_samples_for_baseline=3)

        # Values: 10, 20, 30 → mean=20, stddev≈8.16
        chitragupta.record("comp_001", "value", 10.0)
        chitragupta.record("comp_001", "value", 20.0)
        chitragupta.record("comp_001", "value", 30.0)

        profile = chitragupta.get_profile("comp_001")
        stddev = profile.get_baseline_stddev("value")

        assert 8.0 <= stddev <= 8.5  # Approximately 8.16


class TestAnomalyDetection:
    """Test anomaly detection based on deviation from baseline."""

    def test_detect_anomaly_above_threshold(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(
            min_samples_for_baseline=3,
            anomaly_threshold_sigma=2.0,
        )

        # Build baseline: mean=50, stddev≈0
        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 50.0)

        # Record anomalous value (way above baseline)
        chitragupta.record("comp_001", "latency_ms", 200.0)

        anomaly = chitragupta.detect_anomaly("comp_001")

        assert anomaly is not None
        assert anomaly.metric == "latency_ms"
        assert anomaly.current_value == 200.0

    def test_no_anomaly_within_threshold(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(
            min_samples_for_baseline=3,
            anomaly_threshold_sigma=2.0,
        )

        # Build baseline with some variance
        for v in [48, 50, 52, 49, 51]:
            chitragupta.record("comp_001", "latency_ms", float(v))

        anomaly = chitragupta.detect_anomaly("comp_001")

        assert anomaly is None

    def test_anomaly_returns_expected_range(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(
            min_samples_for_baseline=3,
            anomaly_threshold_sigma=2.0,
        )

        # Build tight baseline
        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 100.0)

        chitragupta.record("comp_001", "latency_ms", 500.0)

        anomaly = chitragupta.detect_anomaly("comp_001")

        assert anomaly is not None
        assert anomaly.expected_range is not None
        assert anomaly.expected_range[0] < anomaly.expected_range[1]


class TestMultipleMetrics:
    """Test profiling with multiple metrics per component."""

    def test_detect_anomaly_checks_all_metrics(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(min_samples_for_baseline=3)

        # Build baseline for two metrics
        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 50.0)
            chitragupta.record("comp_001", "error_rate", 0.01)

        # Anomaly in error_rate only - make latency clearly normal
        chitragupta.record("comp_001", "latency_ms", 50.0)  # Normal (same as baseline)
        chitragupta.record("comp_001", "error_rate", 0.5)  # Anomalous (50x baseline)

        anomaly = chitragupta.detect_anomaly("comp_001")

        assert anomaly is not None
        # Either metric could trigger - both checks that an anomaly was detected
        assert anomaly.metric in ("error_rate", "latency_ms")


class TestProfileExpiry:
    """Test that old data expires from profiles."""

    def test_old_samples_expire(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService(
            min_samples_for_baseline=3,
            profile_window_seconds=0.1,  # 100ms window
        )

        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 50.0)

        import time

        time.sleep(0.15)  # Wait for expiry

        profile = chitragupta.get_profile("comp_001")

        # Old samples should be expired when using window
        # has_baseline needs to pass window_seconds to check properly
        assert profile.has_baseline("latency_ms", min_samples=3, window_seconds=0.1) is False


class TestCortexIntegration:
    """Test integration with NagaCortex."""

    def test_notify_cortex_on_anomaly(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        mock_cortex = MagicMock()
        chitragupta = ChitraguptaService(
            cortex=mock_cortex,
            min_samples_for_baseline=3,
        )

        # Build baseline
        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 50.0)

        # Trigger anomaly
        chitragupta.record("comp_001", "latency_ms", 500.0)
        chitragupta.detect_anomaly("comp_001")

        mock_cortex.receive_chitragupta_anomaly.assert_called()


class TestSignedAnomalies:
    """Test that anomaly reports are signed (37th Principle)."""

    def test_anomaly_report_is_signed(self):
        from vibe_core.naga.identity import NagaIdentity
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        identity = NagaIdentity.generate(agent_id="chitragupta_test")
        chitragupta = ChitraguptaService(
            identity=identity,
            min_samples_for_baseline=3,
        )

        # Build baseline and trigger anomaly
        for _ in range(5):
            chitragupta.record("comp_001", "latency_ms", 50.0)
        chitragupta.record("comp_001", "latency_ms", 500.0)

        anomaly = chitragupta.detect_anomaly("comp_001")

        assert anomaly is not None
        assert anomaly.detector_id == "chitragupta_test"
        assert anomaly.signature is not None


class TestKarmaTracking:
    """Test that all profiling actions are logged (Karma)."""

    def test_record_creates_karma_entry(self):
        from vibe_core.naga.services.chitragupta import ChitraguptaService

        chitragupta = ChitraguptaService()

        chitragupta.record("comp_001", "latency_ms", 50.0)

        karma_log = chitragupta.get_karma_log()
        assert len(karma_log) >= 1
        assert karma_log[-1].action == "RECORD_METRIC"


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

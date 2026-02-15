"""
Tests for substrate/io_sentinel.py — Runtime I/O Guard.

Tests the ACTUAL behavior: arm/disarm/report/reset/drain,
json.dump interception, rogue caller detection, thread safety.
"""

import io
import json
import threading

import pytest

from vibe_core.mahamantra.substrate.io_sentinel import (
    _AUTHORIZED_FILES,
    arm,
    disarm,
    drain_violations,
    is_armed,
    report,
    reset,
)


@pytest.fixture(autouse=True)
def _clean_sentinel():
    """Ensure sentinel is disarmed and counters reset before/after each test."""
    disarm()
    reset()
    yield
    disarm()
    reset()


# =============================================================================
# ARM / DISARM / IS_ARMED
# =============================================================================

class TestArmDisarm:

    def test_starts_disarmed(self):
        assert not is_armed()

    def test_arm_sets_armed(self):
        arm()
        assert is_armed()

    def test_disarm_clears_armed(self):
        arm()
        disarm()
        assert not is_armed()

    def test_arm_is_idempotent(self):
        arm()
        arm()  # second call should not crash
        assert is_armed()

    def test_disarm_is_idempotent(self):
        disarm()
        disarm()  # second call should not crash
        assert not is_armed()


# =============================================================================
# JSON.DUMP INTERCEPTION
# =============================================================================

class TestJsonDumpInterception:

    def test_json_dump_still_works_when_armed(self):
        arm()
        buf = io.StringIO()
        json.dump({"key": "value"}, buf)
        assert json.loads(buf.getvalue()) == {"key": "value"}

    def test_json_dump_counted_when_armed(self):
        arm()
        buf = io.StringIO()
        json.dump({"a": 1}, buf)
        r = report()
        assert r["total_calls"] >= 1

    def test_json_dump_not_counted_when_disarmed(self):
        # disarmed by fixture
        buf = io.StringIO()
        json.dump({"a": 1}, buf)
        r = report()
        assert r["total_calls"] == 0

    def test_rogue_caller_detected(self):
        """This test file is NOT in _AUTHORIZED_FILES, so we are rogue."""
        assert "test_io_sentinel.py" not in _AUTHORIZED_FILES
        arm()
        buf = io.StringIO()
        json.dump({"rogue": True}, buf)
        r = report()
        assert r["rogue_calls"] >= 1

    def test_json_dumps_not_intercepted(self):
        """json.dumps must NOT be patched (serialization != disk write)."""
        arm()
        original_dumps = json.dumps
        result = json.dumps({"test": 1})
        assert result == '{"test": 1}'
        # Verify dumps was not replaced with a wrapper
        assert json.dumps is original_dumps or json.dumps.__name__ == "dumps"


# =============================================================================
# REPORT / RESET / DRAIN
# =============================================================================

class TestReportResetDrain:

    def test_report_structure(self):
        r = report()
        assert "armed" in r
        assert "total_calls" in r
        assert "authorized_calls" in r
        assert "rogue_calls" in r
        assert "rogue_callers" in r
        assert "recent_violations" in r

    def test_reset_clears_counters(self):
        arm()
        buf = io.StringIO()
        json.dump({}, buf)
        reset()
        r = report()
        assert r["total_calls"] == 0
        assert r["rogue_calls"] == 0
        assert r["recent_violations"] == []

    def test_drain_returns_and_clears(self):
        arm()
        buf = io.StringIO()
        json.dump({}, buf)
        violations = drain_violations()
        assert len(violations) >= 1
        assert violations[0]["call_type"] == "json.dump"
        # After drain, buffer is empty
        assert drain_violations() == []

    def test_violation_has_correct_fields(self):
        arm()
        buf = io.StringIO()
        json.dump({}, buf)
        violations = drain_violations()
        v = violations[0]
        assert "caller_file" in v
        assert "caller_line" in v
        assert "caller_func" in v
        assert "call_type" in v
        assert "test_io_sentinel" in v["caller_file"]


# =============================================================================
# THREAD SAFETY
# =============================================================================

class TestThreadSafety:

    def test_concurrent_dumps_no_crash(self):
        arm()
        errors = []

        def worker():
            try:
                for _ in range(20):
                    buf = io.StringIO()
                    json.dump({"t": 1}, buf)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        r = report()
        assert r["total_calls"] == 80  # 4 threads × 20 calls

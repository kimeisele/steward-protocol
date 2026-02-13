"""
Tests for I/O Sentinel — Runtime Guard Against Rogue Writers
=============================================================

Tests that the sentinel:
1. Detects rogue json.dump calls (not from authorized files)
2. Passes authorized callers silently
3. Doesn't block any writes (observation only)
4. Reports accurate counts
5. Arms/disarms cleanly
"""

import json
import tempfile
from pathlib import Path

import pytest

from vibe_core.mahamantra.substrate.io_sentinel import (
    arm,
    disarm,
    report,
    reset,
    SentinelReport,
)


@pytest.fixture(autouse=True)
def _sentinel_lifecycle():
    """Arm before each test, disarm+reset after."""
    reset()
    arm()
    yield
    disarm()
    reset()


class TestSentinelArming:
    """Arm/disarm lifecycle."""

    def test_arm_sets_armed(self):
        r = report()
        assert r["armed"] is True

    def test_disarm_restores(self):
        disarm()
        r = report()
        assert r["armed"] is False

    def test_double_arm_is_safe(self):
        arm()
        arm()
        r = report()
        assert r["armed"] is True

    def test_double_disarm_is_safe(self):
        disarm()
        disarm()
        r = report()
        assert r["armed"] is False


class TestRogueDetection:
    """Rogue writers get logged."""

    def test_direct_json_dump_is_rogue(self, tmp_path):
        """This test file is NOT authorized — json.dump from here = rogue."""
        target = tmp_path / "rogue.json"
        with open(target, "w") as f:
            json.dump({"rogue": True}, f)
        r = report()
        assert r["rogue_calls"] >= 1
        assert r["total_calls"] >= 1

    def test_rogue_caller_recorded(self, tmp_path):
        target = tmp_path / "rogue2.json"
        with open(target, "w") as f:
            json.dump({"x": 1}, f)
        r = report()
        assert len(r["rogue_callers"]) >= 1
        # Our test file should be in the callers
        found = any("test_io_sentinel" in k for k in r["rogue_callers"])
        assert found, f"Expected test_io_sentinel in callers, got: {r['rogue_callers']}"

    def test_violation_has_correct_fields(self, tmp_path):
        before = report()["rogue_calls"]
        target = tmp_path / "rogue3.json"
        with open(target, "w") as f:
            json.dump({}, f)
        r = report()
        assert r["rogue_calls"] > before
        # Find OUR violation in the list (other tests may have added theirs)
        ours = [v for v in r["recent_violations"] if "test_io_sentinel" in v["caller_file"]]
        assert len(ours) >= 1
        v = ours[-1]
        assert v["call_type"] == "json.dump"
        assert v["caller_line"] > 0

    def test_json_dumps_also_tracked(self):
        """json.dumps (to string) is also monitored."""
        _ = json.dumps({"tracked": True})
        r = report()
        assert r["total_calls"] >= 1


class TestWritesNotBlocked:
    """Sentinel observes but never blocks."""

    def test_json_dump_still_writes(self, tmp_path):
        target = tmp_path / "still_works.json"
        with open(target, "w") as f:
            json.dump({"data": 42}, f)
        # File was actually written
        assert target.exists()
        data = json.loads(target.read_text())
        assert data["data"] == 42

    def test_json_dumps_still_returns(self):
        result = json.dumps({"ok": True})
        assert result == '{"ok": true}'


class TestReportAccuracy:
    """Report counters are accurate."""

    def test_fresh_report_is_zero(self):
        reset()
        r = report()
        assert r["total_calls"] == 0
        assert r["authorized_calls"] == 0
        assert r["rogue_calls"] == 0

    def test_multiple_rogues_counted(self, tmp_path):
        # Reset to get a clean measurement window
        reset()
        for i in range(5):
            f = tmp_path / f"r{i}.json"
            with open(f, "w") as fh:
                json.dump({}, fh)
        r = report()
        assert r["rogue_calls"] >= 5

    def test_reset_clears_everything(self, tmp_path):
        target = tmp_path / "x.json"
        with open(target, "w") as f:
            json.dump({}, f)
        reset()
        r = report()
        assert r["total_calls"] == 0
        assert r["rogue_calls"] == 0
        assert len(r["recent_violations"]) == 0


class TestDisarmedPassthrough:
    """When disarmed, no tracking happens."""

    def test_disarmed_no_tracking(self, tmp_path):
        disarm()
        reset()
        target = tmp_path / "free.json"
        with open(target, "w") as f:
            json.dump({"free": True}, f)
        r = report()
        assert r["total_calls"] == 0
        assert r["armed"] is False

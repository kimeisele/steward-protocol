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
    drain_violations,
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


class TestDrainViolations:
    """drain_violations() returns and clears the buffer."""

    def test_drain_returns_violations(self, tmp_path):
        reset()
        target = tmp_path / "drain1.json"
        with open(target, "w") as f:
            json.dump({"x": 1}, f)
        drained = drain_violations()
        assert len(drained) >= 1
        v = drained[-1]
        assert "caller_file" in v
        assert "caller_line" in v
        assert "caller_func" in v
        assert "call_type" in v

    def test_drain_clears_buffer(self, tmp_path):
        reset()
        target = tmp_path / "drain2.json"
        with open(target, "w") as f:
            json.dump({}, f)
        first = drain_violations()
        assert len(first) >= 1
        second = drain_violations()
        assert len(second) == 0

    def test_drain_empty_when_no_violations(self):
        reset()
        drained = drain_violations()
        assert drained == []

    def test_drain_does_not_affect_counters(self, tmp_path):
        reset()
        target = tmp_path / "drain3.json"
        with open(target, "w") as f:
            json.dump({}, f)
        r_before = report()
        rogue_before = r_before["rogue_calls"]
        drain_violations()
        r_after = report()
        assert r_after["rogue_calls"] == rogue_before


class TestSentinelOuroborosLoop:
    """The closed loop: Sentinel → drain → ViolationRecord → KG."""

    def test_sentinel_violation_becomes_violation_record(self, tmp_path):
        """Drained violations can be converted to ViolationRecord."""
        from vibe_core.ouroboros.ingestion import ViolationRecord, ViolationSource

        reset()
        target = tmp_path / "loop1.json"
        with open(target, "w") as f:
            json.dump({"loop": True}, f)

        drained = drain_violations()
        assert len(drained) >= 1

        v = drained[-1]
        record = ViolationRecord(
            source=ViolationSource.SENTINEL,
            rule_id="unsafe_io_write",
            file_path=v["caller_file"],
            line=v["caller_line"],
            message=f"Rogue {v['call_type']} in {v['caller_func']}()",
            severity="MEDIUM",
            has_remedy=True,
            verification_status="verified",
            origin="live_scan",
        )
        assert record.source == ViolationSource.SENTINEL
        assert record.rule_id == "unsafe_io_write"
        assert record.has_remedy is True
        assert record.is_verified()
        assert not record.is_maya()

    def test_violation_source_sentinel_exists(self):
        from vibe_core.ouroboros.ingestion import ViolationSource
        assert hasattr(ViolationSource, "SENTINEL")
        assert ViolationSource.SENTINEL.value == "sentinel"

    def test_ouroboros_subscriber_has_sentinel_ingestion(self):
        from vibe_core.services.healing_subscribers import OuroborosSubscriber
        sub = OuroborosSubscriber()
        assert hasattr(sub, "_ingest_sentinel_violations")

    def test_ouroboros_subscriber_drains_on_tick(self, tmp_path):
        """OuroborosSubscriber._ingest_sentinel_violations() drains the buffer."""
        from vibe_core.services.healing_subscribers import OuroborosSubscriber

        reset()
        target = tmp_path / "tick1.json"
        with open(target, "w") as f:
            json.dump({"tick": True}, f)

        assert report()["rogue_calls"] >= 1
        before = drain_violations()
        assert len(before) >= 1
        # Re-arm with fresh violations
        reset()
        with open(target, "w") as f:
            json.dump({"tick2": True}, f)

        sub = OuroborosSubscriber()
        # _ingest_sentinel_violations will try to push to KG
        # Without KG it returns 0 but still drains
        result = sub._ingest_sentinel_violations()
        # Buffer should be drained regardless of KG availability
        remaining = drain_violations()
        assert len(remaining) == 0


class TestKGPropertyKeyRegression:
    """Regression: KG stores violations under "file", engine must read "file" not "file_path"."""

    def test_kg_violation_uses_file_key(self):
        """KG.add_violation stores path under 'file' property key."""
        from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

        kg = UnifiedKnowledgeGraph()
        node = kg.add_violation(
            file_path="/tmp/rogue.py",
            line=42,
            rule_id="unsafe_io_write",
            message="test",
            has_remedy=True,
            verification_status="verified",
            origin="live_scan",
        )
        assert node.properties["file"] == "/tmp/rogue.py"
        assert "file_path" not in node.properties

    def test_engine_reads_file_key_from_kg(self):
        """ShuddhiEngine.heal_all_violations reads 'file' not 'file_path'."""
        import ast
        source = Path("/Users/ss/projects/steward-protocol/vibe_core/mahamantra/dharma/kumaras/engine.py").read_text()
        tree = ast.parse(source)

        # Find the heal_all_violations method and check it reads "file"
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute)
                    and node.func.attr == "get"
                    and len(node.args) >= 1
                    and isinstance(node.args[0], ast.Constant)):
                    # If we find .get("file_path"...) that's the old bug
                    if node.args[0].value == "file_path":
                        # Check if this is in heal_all_violations context
                        # by looking at surrounding code
                        assert False, (
                            "REGRESSION: engine.py still reads 'file_path' "
                            "instead of 'file' from KG violation properties"
                        )

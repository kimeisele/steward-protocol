#!/usr/bin/env python3
"""
SEMANTIC AUDITOR TESTS - The Judge & Watchdog

Test suite for the semantic verification layer:
- Invariant checks
- Violation recording
- Watchdog monitoring
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

from steward.system_agents.auditor.tools.invariant_tool import (
    InvariantEngine,
    InvariantRule,
    InvariantSeverity,
    InvariantViolation,
    VerificationReport,
    get_judge,
)

from steward.system_agents.auditor.tools.watchdog_tool import (
    Watchdog,
    WatchdogConfig,
    ViolationEvent,
    WatchdogIntegration,
)


class TestInvariantEngine:
    """Test the Judge's invariant engine"""

    def test_judge_initialization(self):
        """Test that Judge initializes with core rules"""
        judge = get_judge()
        assert judge is not None
        assert len(judge.rules) > 0
        assert "BROADCAST_LICENSE_REQUIREMENT" in judge.rules
        assert "CREDIT_TRANSFER_PROPOSAL_REQUIREMENT" in judge.rules

    def test_broadcast_license_requirement(self):
        """Test BROADCAST must have LICENSE_VALID"""
        judge = InvariantEngine()

        # Violation: BROADCAST without LICENSE_VALID
        events = [
            {
                "event_type": "BROADCAST",
                "task_id": "task_1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:00Z",
            }
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        assert len(report.violations) > 0
        assert any(v.invariant_name == "BROADCAST_LICENSE_REQUIREMENT" for v in report.violations)

    def test_broadcast_with_license_valid(self):
        """Test BROADCAST passes with LICENSE_VALID"""
        judge = InvariantEngine()

        # Valid: BROADCAST preceded by LICENSE_VALID
        events = [
            {
                "event_type": "LICENSE_VALID",
                "task_id": "task_1",
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "BROADCAST",
                "task_id": "task_1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:01:00Z",
            },
        ]

        report = judge.verify_ledger(events)
        # Should pass this rule
        violations = [v for v in report.violations if v.invariant_name == "BROADCAST_LICENSE_REQUIREMENT"]
        assert len(violations) == 0

    def test_credit_transfer_proposal_requirement(self):
        """Test CREDIT_TRANSFER must have PROPOSAL_PASSED"""
        judge = InvariantEngine()

        # Violation: CREDIT_TRANSFER without PROPOSAL_PASSED
        events = [
            {
                "event_type": "CREDIT_TRANSFER",
                "task_id": "task_2",
                "agent_id": "banker",
                "timestamp": "2025-11-24T15:00:00Z",
            }
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        assert len(report.violations) > 0
        assert any(v.invariant_name == "CREDIT_TRANSFER_PROPOSAL_REQUIREMENT" for v in report.violations)

    def test_no_orphaned_events(self):
        """Test that orphaned events are detected"""
        judge = InvariantEngine()

        # Violation: Event missing task_id
        events = [
            {
                "event_type": "PROPOSAL_CREATED",
                # Missing task_id
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:00:00Z",
            }
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        violations = [v for v in report.violations if v.invariant_name == "NO_ORPHANED_EVENTS"]
        assert len(violations) > 0

    def test_event_sequence_integrity(self):
        """Test that out-of-order events are detected"""
        judge = InvariantEngine()

        # Violation: Events out of order
        events = [
            {
                "event_type": "EVENT_1",
                "task_id": "task_3",
                "agent_id": "agent_a",
                "timestamp": "2025-11-24T15:02:00Z",
            },
            {
                "event_type": "EVENT_2",
                "task_id": "task_3",
                "agent_id": "agent_b",
                "timestamp": "2025-11-24T15:01:00Z",  # Earlier than previous!
            },
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        violations = [v for v in report.violations if v.invariant_name == "EVENT_SEQUENCE_INTEGRITY"]
        assert len(violations) > 0

    def test_no_duplicate_events(self):
        """Test duplicate detection"""
        judge = InvariantEngine()

        # Violation: Duplicate events (exact same key)
        events = [
            {
                "event_type": "BROADCAST",
                "task_id": "task_4",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "BROADCAST",
                "task_id": "task_4",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:00Z",  # Exact duplicate
            },
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        violations = [v for v in report.violations if v.invariant_name == "NO_DUPLICATE_EVENTS"]
        assert len(violations) > 0

    def test_proposal_workflow_integrity(self):
        """Test proposal workflow must be ordered"""
        judge = InvariantEngine()

        # Violation: PROPOSAL_VOTED_YES without PROPOSAL_CREATED
        events = [
            {
                "event_type": "PROPOSAL_VOTED_YES",
                "proposal_id": "prop_123",
                "task_id": "task_5",
                "agent_id": "voter",
                "timestamp": "2025-11-24T15:00:00Z",
            }
        ]

        report = judge.verify_ledger(events)
        assert not report.passed
        violations = [v for v in report.violations if v.invariant_name == "PROPOSAL_WORKFLOW_INTEGRITY"]
        assert len(violations) > 0


class TestWatchdog:
    """Test the Watchdog runtime monitoring"""

    def test_watchdog_initialization(self):
        """Test Watchdog initializes correctly"""
        config = WatchdogConfig()
        watchdog = Watchdog(config)

        assert watchdog is not None
        assert watchdog.last_checked_index == 0
        assert watchdog.violation_count == 0
        assert not watchdog.halt_requested

    def test_violation_event_creation(self):
        """Test ViolationEvent can be created"""
        event = ViolationEvent(
            violation_type="TEST_VIOLATION",
            severity="HIGH",
            message="Test violation message",
            violated_invariant="TEST_INVARIANT",
        )

        assert event.event_type == "VIOLATION"
        assert event.agent_id == "watchdog"
        assert event.timestamp is not None

        event_dict = event.to_dict()
        assert event_dict["violation_type"] == "TEST_VIOLATION"

    def test_watchdog_ledger_reading(self):
        """Test Watchdog can read ledger events"""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_ledger.jsonl"

            # Write test events
            events = [
                {
                    "event_type": "BOOT",
                    "task_id": "t1",
                    "agent_id": "kernel",
                    "timestamp": "2025-11-24T15:00:00Z",
                },
                {
                    "event_type": "TASK",
                    "task_id": "t2",
                    "agent_id": "worker",
                    "timestamp": "2025-11-24T15:01:00Z",
                },
            ]

            with open(ledger_path, "w") as f:
                for event in events:
                    json.dump(event, f)
                    f.write("\n")

            # Create watchdog with custom config
            config = WatchdogConfig(ledger_path=ledger_path)
            watchdog = Watchdog(config)

            # Read events
            read_events = watchdog.read_ledger_events(0)
            assert len(read_events) == 2
            assert read_events[0]["event_type"] == "BOOT"

    def test_watchdog_violation_recording(self):
        """Test Watchdog can record violations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            violations_path = Path(tmpdir) / "violations.jsonl"

            config = WatchdogConfig(violations_path=violations_path)
            watchdog = Watchdog(config)

            violation = ViolationEvent(violation_type="TEST_VIOLATION", severity="HIGH", message="Test")

            result = watchdog.record_violation(violation)
            assert result is True
            assert watchdog.violation_count == 1

            # Check file was created
            assert violations_path.exists()
            with open(violations_path) as f:
                recorded = json.loads(f.readline())
                assert recorded["violation_type"] == "TEST_VIOLATION"

    def test_watchdog_integration_kernel_tick(self):
        """Test Watchdog integration with kernel ticks"""
        integration = WatchdogIntegration()

        # Simulate kernel ticks
        result1 = integration.kernel_tick(5)  # Before check interval
        assert result1["should_halt"] is False

        result2 = integration.kernel_tick(10)  # At check interval
        # Might run check depending on config
        assert "should_halt" in result2


class TestSemanticAuditorIntegration:
    """Test semantic auditor integration with AUDITOR cartridge"""

    def test_auditor_has_judge(self):
        """Test that AUDITOR cartridge has Judge"""
        from steward.system_agents.auditor.cartridge_main import AuditorCartridge

        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditorCartridge(Path(tmpdir))
            assert auditor.judge is not None
            assert hasattr(auditor, "run_semantic_verification")

    def test_auditor_has_watchdog(self):
        """Test that AUDITOR cartridge has Watchdog"""
        from steward.system_agents.auditor.cartridge_main import AuditorCartridge

        with tempfile.TemporaryDirectory() as tmpdir:
            auditor = AuditorCartridge(Path(tmpdir))
            assert auditor.watchdog_integration is not None
            assert hasattr(auditor, "run_watchdog_check")
            assert hasattr(auditor, "start_watchdog")

    def test_auditor_version_updated(self):
        """Test that AUDITOR version reflects semantic capabilities"""
        from steward.system_agents.auditor.cartridge_main import AuditorCartridge

        auditor = AuditorCartridge()
        assert auditor.version >= "2.0.0"  # Must be 2.0+ for semantic verification


class TestRealWorldScenarios:
    """Test realistic violation scenarios"""

    def test_scenario_broadcast_without_license(self):
        """Scenario: Agent broadcasts without license (should fail)"""
        judge = InvariantEngine()

        events = [
            {
                "event_type": "BROADCAST",
                "task_id": "t1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "MESSAGE",
                "task_id": "t1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:01:00Z",
            },
        ]

        report = judge.verify_ledger(events)
        assert not report.passed

    def test_scenario_valid_broadcast_sequence(self):
        """Scenario: Valid broadcast with proper license"""
        judge = InvariantEngine()

        events = [
            {
                "event_type": "LICENSE_CHECK",
                "task_id": "t1",
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "LICENSE_VALID",
                "task_id": "t1",
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:00:10Z",
            },
            {
                "event_type": "BROADCAST",
                "task_id": "t1",
                "agent_id": "herald",
                "timestamp": "2025-11-24T15:00:20Z",
            },
        ]

        report = judge.verify_ledger(events)
        # Should not violate BROADCAST_LICENSE_REQUIREMENT
        violations = [v for v in report.violations if v.invariant_name == "BROADCAST_LICENSE_REQUIREMENT"]
        assert len(violations) == 0

    def test_scenario_proposal_to_transfer(self):
        """Scenario: Credit transfer properly following proposal"""
        judge = InvariantEngine()

        events = [
            {
                "event_type": "PROPOSAL_CREATED",
                "proposal_id": "p1",
                "task_id": "t1",
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:00:00Z",
            },
            {
                "event_type": "PROPOSAL_VOTED_YES",
                "proposal_id": "p1",
                "task_id": "t1",
                "agent_id": "voter",
                "timestamp": "2025-11-24T15:01:00Z",
            },
            {
                "event_type": "PROPOSAL_PASSED",
                "proposal_id": "p1",
                "task_id": "t1",
                "agent_id": "civic",
                "timestamp": "2025-11-24T15:02:00Z",
            },
            {
                "event_type": "CREDIT_TRANSFER",
                "proposal_id": "p1",
                "task_id": "t1",
                "agent_id": "banker",
                "timestamp": "2025-11-24T15:03:00Z",
            },
        ]

        report = judge.verify_ledger(events)
        # Should not violate CREDIT_TRANSFER_PROPOSAL_REQUIREMENT
        violations = [v for v in report.violations if v.invariant_name == "CREDIT_TRANSFER_PROPOSAL_REQUIREMENT"]
        assert len(violations) == 0


class TestSemanticCompliance:
    """Test the Curator Invariant (Rule 8: Semantic Compliance)"""

    def test_semantic_compliance_without_config(self):
        """Test that semantic compliance check passes when config doesn't exist"""
        judge = InvariantEngine()

        # The check should gracefully pass if config is missing
        events = [
            {
                "event_type": "POLICY_UPDATED",
                "task_id": "t1",
                "agent_id": "governance",
                "timestamp": "2025-11-24T15:00:00Z",
            }
        ]

        report = judge.verify_ledger(events)
        # Should not fail (config doesn't exist, check is skipped)
        violations = [v for v in report.violations if v.invariant_name == "SEMANTIC_COMPLIANCE_REQUIREMENT"]
        assert len(violations) == 0

    def test_semantic_compliance_rule_registered(self):
        """Test that Semantic Compliance Rule is registered"""
        judge = get_judge()
        assert "SEMANTIC_COMPLIANCE_REQUIREMENT" in judge.rules

        rule = judge.rules["SEMANTIC_COMPLIANCE_REQUIREMENT"]
        assert rule.severity == InvariantSeverity.HIGH
        assert "semantic" in rule.description.lower()

    def test_semantic_compliance_detects_hype_words(self, tmp_path):
        """Test that Curator detects red-flag hype words in documents"""
        # Create a temporary test setup
        from pathlib import Path
        import yaml

        # Create temp directories
        config_dir = tmp_path / "config"
        docs_dir = tmp_path / "docs"
        config_dir.mkdir()
        docs_dir.mkdir()

        # Create semantic compliance config with red flags
        config_data = {
            "RED_FLAGS": {"HYPE": ["revolutionary", "game-changer", "breakthrough"]},
            "SCOPE": {"CRITICAL_DOCUMENTS": ["docs/*.md"]},
        }
        config_file = config_dir / "semantic_compliance.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create a document with red flags
        bad_doc = docs_dir / "bad_policy.md"
        bad_doc.write_text("# Revolutionary Policy\nThis is a game-changer initiative.")

        # Change to temp directory and run check
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            judge = InvariantEngine()
            events = [
                {
                    "event_type": "TEST",
                    "task_id": "t1",
                    "agent_id": "test",
                    "timestamp": "2025-11-24T15:00:00Z",
                }
            ]
            report = judge.verify_ledger(events)

            violations = [v for v in report.violations if v.invariant_name == "SEMANTIC_COMPLIANCE_REQUIREMENT"]
            # Should detect red-flag words
            assert len(violations) > 0
            assert any("revolutionary" in v.message.lower() or "game-changer" in v.message.lower() for v in violations)
        finally:
            os.chdir(old_cwd)

    def test_semantic_compliance_allows_green_flags(self, tmp_path):
        """Test that Curator allows green-flag approved words"""
        import yaml
        import os

        # Create temp setup
        config_dir = tmp_path / "config"
        docs_dir = tmp_path / "docs"
        config_dir.mkdir()
        docs_dir.mkdir()

        # Config with red and green flags
        config_data = {
            "RED_FLAGS": {"HYPE": ["revolutionary"]},
            "GREEN_FLAGS": {"VERIFIABLE": ["auditable", "provable"]},
            "SCOPE": {"CRITICAL_DOCUMENTS": ["docs/*.md"]},
        }
        config_file = config_dir / "semantic_compliance.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        # Create document with only green flags (no red flags)
        good_doc = docs_dir / "good_policy.md"
        good_doc.write_text("# Auditable Governance\nThis policy is provable and verifiable.")

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            judge = InvariantEngine()
            events = [
                {
                    "event_type": "TEST",
                    "task_id": "t1",
                    "agent_id": "test",
                    "timestamp": "2025-11-24T15:00:00Z",
                }
            ]
            report = judge.verify_ledger(events)

            violations = [v for v in report.violations if v.invariant_name == "SEMANTIC_COMPLIANCE_REQUIREMENT"]
            # Should have NO violations when only green flags are present
            assert len(violations) == 0
        finally:
            os.chdir(old_cwd)

    def test_semantic_compliance_severity_is_high(self):
        """Test that semantic compliance violations are HIGH severity (non-halting)"""
        judge = get_judge()
        rule = judge.rules["SEMANTIC_COMPLIANCE_REQUIREMENT"]

        assert rule.severity == InvariantSeverity.HIGH
        # HIGH severity means violations are reported but don't halt the system
        # (unlike CRITICAL which would halt)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

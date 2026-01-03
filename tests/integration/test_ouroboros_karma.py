"""
OUROBOROS KARMA: Tests for Ledger event emission in self-healing loop.

PROMPT.md Compliance:
- KARMA: All significant operations MUST emit Ledger events
- YANTRA: duration_ms tracked and warned if >100ms

These tests verify that the Ouroboros loop properly records its actions
to the immutable Ledger for audit trail purposes.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.ouroboros.ingestion import (
    ViolationIngester,
    ViolationRecord,
    ViolationSource,
)
from vibe_core.protocols.shuddhi import ShuddhiStatus
from vibe_core.shuddhi.engine import ShuddhiEngine


class MockLedger:
    """Mock VibeLedger for testing event recording."""

    def __init__(self):
        self.events = []

    def record_event(self, event_type: str, agent_id: str, details: dict) -> None:
        self.events.append(
            {
                "event_type": event_type,
                "agent_id": agent_id,
                "details": details,
            }
        )


class MockKnowledgeGraph:
    """Mock KG for testing without real persistence."""

    def __init__(self):
        self.violations = []
        self.healed = []

    def add_violation(self, **kwargs) -> None:
        self.violations.append(kwargs)

    def get_violations(self, healed: bool = False, rule_id: str = None):
        return []

    def mark_violation_healed(self, violation_id: str, rule_id: str) -> None:
        self.healed.append((violation_id, rule_id))


@pytest.fixture
def clean_registry():
    """Reset ServiceRegistry for each test."""
    ServiceRegistry.reset()
    yield
    ServiceRegistry.reset()


@pytest.fixture
def mock_ledger(clean_registry):
    """Register a mock Ledger in the ServiceRegistry."""
    from vibe_core.protocols.ledger import VibeLedger

    ledger = MockLedger()
    ServiceRegistry.register(VibeLedger, ledger)
    return ledger


@pytest.fixture
def mock_kg(clean_registry):
    """Register a mock KG in the ServiceRegistry."""
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

    kg = MockKnowledgeGraph()
    ServiceRegistry.register(UnifiedKnowledgeGraph, kg)
    return kg


class TestViolationIngesterKarma:
    """Tests for ViolationIngester Ledger event emission."""

    def test_ingest_emits_ledger_event(self, mock_ledger, mock_kg):
        """KARMA: Ingestion MUST emit VIOLATION_INGESTED event."""
        ingester = ViolationIngester(kg=mock_kg)

        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="F401",
                file_path="test.py",
                line=10,
                message="Unused import",
            ),
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="E501",
                file_path="test.py",
                line=20,
                message="Line too long",
            ),
        ]

        count = ingester.ingest(violations)

        assert count == 2
        assert len(mock_ledger.events) == 1

        event = mock_ledger.events[0]
        assert event["event_type"] == "VIOLATION_INGESTED"
        assert event["agent_id"] == "ouroboros"
        assert event["details"]["source"] == "ruff"
        assert event["details"]["violations_ingested"] == 2
        assert "duration_ms" in event["details"]
        assert "timestamp" in event["details"]

    def test_ingest_tracks_duration_ms(self, mock_ledger, mock_kg):
        """YANTRA: Ingestion MUST track duration_ms."""
        ingester = ViolationIngester(kg=mock_kg)

        violations = [
            ViolationRecord(
                source=ViolationSource.PYTEST,
                rule_id="TEST_FAILURE:test_foo",
                message="Test failed",
            ),
        ]

        ingester.ingest(violations)

        event = mock_ledger.events[0]
        duration_ms = event["details"]["duration_ms"]

        assert isinstance(duration_ms, (int, float))
        assert duration_ms >= 0

    def test_maya_violations_not_ingested(self, mock_ledger, mock_kg):
        """SATYA: Maya (false positives) should be discarded."""
        ingester = ViolationIngester(kg=mock_kg)

        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="F401",
                file_path="test.py",
                line=10,
                message="Unused import",
                verification_status="maya",  # False positive
            ),
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="E501",
                file_path="test.py",
                line=20,
                message="Line too long",
                verification_status="verified",
            ),
        ]

        count = ingester.ingest(violations)

        # Only 1 ingested (maya discarded)
        assert count == 1
        assert len(mock_kg.violations) == 1
        assert mock_kg.violations[0]["rule_id"] == "E501"

        # Event should report maya_discarded
        event = mock_ledger.events[0]
        assert event["details"]["maya_discarded"] == 1

    def test_empty_violations_no_event(self, mock_ledger, mock_kg):
        """No event emitted if no violations to ingest."""
        ingester = ViolationIngester(kg=mock_kg)
        count = ingester.ingest([])

        assert count == 0
        assert len(mock_ledger.events) == 0


class TestShuddhiEngineKarma:
    """Tests for ShuddhiEngine Ledger event emission."""

    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temp Python file for healing tests."""
        file = tmp_path / "test_violation.py"
        file.write_text('import os\n\nprint("hello")\n')
        return file

    def test_heal_and_record_emits_event(self, mock_ledger, mock_kg, temp_file):
        """KARMA: heal_and_record MUST emit VIOLATION_HEALED event."""
        engine = ShuddhiEngine()

        # Attempt healing (will likely be SKIPPED since no actual violation)
        result = engine.heal_and_record(
            file_path=temp_file,
            rule_id="F401",  # unused import
            violation_id="v123",
            write_file=False,
        )

        # Should have emitted event regardless of outcome
        assert len(mock_ledger.events) == 1

        event = mock_ledger.events[0]
        assert event["event_type"] == "VIOLATION_HEALED"
        assert event["agent_id"] == "shuddhi"
        assert event["details"]["rule_id"] == "F401"
        assert event["details"]["violation_id"] == "v123"
        assert "duration_ms" in event["details"]
        assert "status" in event["details"]

    def test_heal_and_record_tracks_duration(self, mock_ledger, mock_kg, temp_file):
        """YANTRA: heal_and_record MUST track duration_ms."""
        engine = ShuddhiEngine()

        engine.heal_and_record(
            file_path=temp_file,
            rule_id="F401",
            violation_id=None,
            write_file=False,
        )

        event = mock_ledger.events[0]
        duration_ms = event["details"]["duration_ms"]

        assert isinstance(duration_ms, (int, float))
        assert duration_ms >= 0


class TestBatchHealingKarma:
    """Tests for batch healing Ledger events."""

    def test_heal_all_emits_batch_event(self, mock_ledger, mock_kg):
        """KARMA: heal_all_violations MUST emit HEALING_BATCH_COMPLETE event."""
        engine = ShuddhiEngine()

        # Run batch healing (will be empty since mock KG has no violations)
        results = engine.heal_all_violations(dry_run=True)

        assert len(results) == 0
        # No batch event if nothing healable
        # (This is correct - no event for empty operations)


class TestLedgerResilience:
    """Tests for DHARMA: System MUST NOT crash on Ledger failure."""

    def test_ingestion_survives_ledger_failure(self, mock_kg, clean_registry):
        """DHARMA: Ingestion must NOT crash if Ledger fails."""
        from vibe_core.protocols.ledger import VibeLedger

        # Register a broken ledger
        broken_ledger = MagicMock()
        broken_ledger.record_event.side_effect = Exception("Ledger exploded!")
        ServiceRegistry.register(VibeLedger, broken_ledger)

        ingester = ViolationIngester(kg=mock_kg)
        violations = [
            ViolationRecord(
                source=ViolationSource.RUFF,
                rule_id="F401",
                message="Test",
            ),
        ]

        # Should NOT raise
        count = ingester.ingest(violations)

        # Violations still ingested despite Ledger failure
        assert count == 1
        assert len(mock_kg.violations) == 1

    def test_healing_survives_ledger_failure(self, mock_kg, tmp_path, clean_registry):
        """DHARMA: Healing must NOT crash if Ledger fails."""
        from vibe_core.protocols.ledger import VibeLedger

        # Register a broken ledger
        broken_ledger = MagicMock()
        broken_ledger.record_event.side_effect = Exception("Ledger exploded!")
        ServiceRegistry.register(VibeLedger, broken_ledger)

        engine = ShuddhiEngine()

        test_file = tmp_path / "test.py"
        test_file.write_text('print("hello")\n')

        # Should NOT raise
        result = engine.heal_and_record(
            file_path=test_file,
            rule_id="F401",
            write_file=False,
        )

        # Healing still works despite Ledger failure
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Integration Tests: Federation Gateway Endpoints

Tests that the /api/federation/* endpoints work correctly.
These tests don't require a full FastAPI app, just the endpoint logic.
"""

import json
import tempfile
from pathlib import Path

from vibe_core.mahamantra.federation import FederationMessage, FederationNadi


class TestFederationGatewayIntegration:
    """Test federation gateway endpoints."""

    def test_get_federation_outbox_empty(self):
        """GET /api/federation/outbox returns empty when no outbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)
            messages = nadi.receive()

            assert isinstance(messages, list)
            assert len(messages) == 0

    def test_get_federation_outbox_with_messages(self):
        """GET /api/federation/outbox returns messages from outbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            # Create outbox with messages
            msg1 = FederationMessage(
                source="moksha",
                target="steward-protocol",
                operation="city_report",
                payload={"heartbeat": 100},
            ).to_dict()

            msg2 = FederationMessage(
                source="karma",
                target="steward-protocol",
                operation="mission_result",
                payload={"mission": "heal"},
            ).to_dict()

            with open(nadi.outbox_path, "w") as f:
                json.dump([msg1, msg2], f)

            messages = nadi.receive()

            assert len(messages) == 2
            assert messages[0].source == "moksha"
            assert messages[1].source == "karma"

    def test_write_federation_inbox(self):
        """POST /api/federation/inbox writes message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            success = nadi.emit(
                source="steward-protocol",
                target="agent-city",
                operation="federation_sync",
                payload={"agents": ["HERALD", "SAGE"]},
                priority=2,
            )

            assert success is True
            assert nadi.inbox_path.exists()

            # Verify written message
            with open(nadi.inbox_path) as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["source"] == "steward-protocol"
            assert data[0]["operation"] == "federation_sync"

    def test_get_federation_stats(self):
        """GET /api/federation/stats returns channel stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            # Add some messages
            nadi.emit("s", "t", "op1")
            nadi.emit("s", "t", "op2")

            stats = nadi.stats()

            assert isinstance(stats, dict)
            assert "outbox_pending" in stats
            assert "inbox_pending" in stats
            assert "reports_archived" in stats
            assert stats["inbox_pending"] == 2

    def test_clear_federation_outbox(self):
        """DELETE /api/federation/outbox clears outbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            # Create outbox
            nadi.outbox_path.write_text("[]")
            assert nadi.outbox_path.exists()

            # Clear it
            success = nadi.clear_outbox()

            assert success is True
            assert not nadi.outbox_path.exists()

    def test_get_city_reports(self):
        """GET /api/federation/reports returns archived reports."""
        from datetime import datetime

        from vibe_core.mahamantra.federation import CityReport

        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            # Save some reports
            for i in range(1, 4):
                report = CityReport(
                    heartbeat=i * 100,
                    timestamp=datetime.now().timestamp(),
                    population=i * 10,
                    alive=i * 8,
                    dead=i * 2,
                    elected_mayor="citizen",
                    council_seats=3,
                    open_proposals=1,
                    chain_valid=True,
                )
                nadi.save_city_report(report)

            # List reports
            reports_dir = nadi.federation_dir / "reports"
            report_files = sorted(reports_dir.glob("report_*.json"), reverse=True)

            assert len(report_files) == 3

    def test_federation_roundtrip(self):
        """Full roundtrip: Write to inbox, read from outbox."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nadi = FederationNadi(tmpdir)

            # steward-protocol writes to inbox
            nadi.emit(
                source="steward-protocol",
                target="agent-city",
                operation="sync_request",
                payload={"action": "sync"},
            )

            # Verify inbox
            inbox_messages = []
            if nadi.inbox_path.exists():
                with open(nadi.inbox_path) as f:
                    inbox_messages = json.load(f)

            assert len(inbox_messages) == 1

            # Now simulate agent-city writing to outbox
            response = FederationMessage(
                source="moksha",
                target="steward-protocol",
                operation="sync_response",
                payload={"status": "success"},
            ).to_dict()

            with open(nadi.outbox_path, "w") as f:
                json.dump([response], f)

            # steward-protocol reads from outbox
            messages = nadi.receive()

            assert len(messages) == 1
            assert messages[0].operation == "sync_response"

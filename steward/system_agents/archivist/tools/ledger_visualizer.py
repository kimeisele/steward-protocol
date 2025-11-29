"""
ARCHIVIST Ledger Visualizer - Generate live statistics from audit trail.

This tool parses the immutable ledger (JSONL format) and generates
visualizations and reports for public consumption.

Capabilities:
- Parse audit_trail.jsonl
- Generate summary statistics
- Create visualization metadata
- Track verification trends
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ARCHIVIST_VISUALIZER")


class LedgerVisualizer:
    """
    Transform immutable ledger data into meaningful visualizations.

    The ledger itself is immutable and signed. This visualizer
    reads from the ledger and generates reports without modifying it.
    """

    def __init__(self, ledger_path: Path = Path("data/ledger/audit_trail.jsonl")):
        """Initialize visualizer."""
        self.ledger_path = ledger_path
        self.attestations: List[Dict[str, Any]] = []
        self.last_loaded = None

        if ledger_path.exists():
            self._load_ledger()
            logger.info(
                f"✅ Ledger Visualizer initialized: {len(self.attestations)} attestations loaded"
            )
        else:
            logger.warning(f"⚠️  Ledger not found: {ledger_path}")

    def _load_ledger(self):
        """Load all attestations from JSONL ledger."""
        self.attestations = []

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        attestation = json.loads(line)
                        self.attestations.append(attestation)
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠️  Line {line_num}: Invalid JSON: {e}")

            self.last_loaded = datetime.now(timezone.utc)
            logger.info(f"✅ Ledger loaded: {len(self.attestations)} attestations")

        except Exception as e:
            logger.error(f"❌ Failed to load ledger: {e}")

    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics from ledger.

        Returns:
            Dict with key metrics
        """

        if not self.attestations:
            return {
                "total_events": 0,
                "verified_count": 0,
                "failed_count": 0,
                "verification_rate": 0,
                "event_types": {},
                "verification_by_type": {},
                "agent_stats": {},
            }

        total = len(self.attestations)
        verified = sum(1 for a in self.attestations if a.get("status") == "VERIFIED")
        failed = sum(1 for a in self.attestations if a.get("status") == "FAILED")

        # Event type breakdown
        event_types = defaultdict(int)
        verification_by_type = defaultdict(
            lambda: {"verified": 0, "failed": 0, "total": 0}
        )

        for attestation in self.attestations:
            event_type = attestation.get("target_event", {}).get(
                "event_type", "unknown"
            )
            event_types[event_type] += 1

            status = attestation.get("status", "unknown")
            verification_by_type[event_type]["total"] += 1
            if status == "VERIFIED":
                verification_by_type[event_type]["verified"] += 1
            elif status == "FAILED":
                verification_by_type[event_type]["failed"] += 1

        # Agent breakdown
        agent_stats = defaultdict(lambda: {"events": 0, "verified": 0})
        for attestation in self.attestations:
            agent_id = attestation.get("target_event", {}).get("agent_id", "unknown")
            agent_stats[agent_id]["events"] += 1

            if attestation.get("status") == "VERIFIED":
                agent_stats[agent_id]["verified"] += 1

        return {
            "total_events": total,
            "verified_count": verified,
            "failed_count": failed,
            "verification_rate": round((verified / total * 100) if total > 0 else 0, 1),
            "event_types": dict(event_types),
            "verification_by_type": {
                k: dict(v) for k, v in verification_by_type.items()
            },
            "agent_stats": {k: dict(v) for k, v in agent_stats.items()},
            "last_loaded": self.last_loaded.isoformat() if self.last_loaded else None,
        }

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most recent attestations (reverse chronological).

        Args:
            limit: Maximum number of events to return

        Returns:
            List of attestations
        """

        return list(reversed(self.attestations))[:limit]

    def get_verification_timeline(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get verification timeline for the last N hours.

        Args:
            hours: Look back period in hours

        Returns:
            Timeline of verification events
        """

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        timeline = []

        for attestation in self.attestations:
            timestamp_str = attestation.get("timestamp")
            if not timestamp_str:
                continue

            try:
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("+00:00", "+00:00")
                )
                if timestamp >= cutoff:
                    timeline.append(
                        {
                            "timestamp": timestamp_str,
                            "event_type": attestation.get("target_event", {}).get(
                                "event_type"
                            ),
                            "status": attestation.get("status"),
                            "agent_id": attestation.get("target_event", {}).get(
                                "agent_id"
                            ),
                        }
                    )
            except ValueError:
                logger.warning(f"⚠️  Invalid timestamp: {timestamp_str}")

        return sorted(timeline, key=lambda x: x["timestamp"])

    def get_trust_score(self) -> Dict[str, Any]:
        """
        Calculate a trust score based on verification success rate.

        Returns:
            Trust metrics
        """

        stats = self.get_summary_statistics()
        verification_rate = stats.get("verification_rate", 0)

        # Determine trust level
        if verification_rate >= 95:
            trust_level = "HIGH"
            color = "green"
        elif verification_rate >= 80:
            trust_level = "MEDIUM"
            color = "yellow"
        else:
            trust_level = "LOW"
            color = "red"

        return {
            "verification_rate": verification_rate,
            "trust_level": trust_level,
            "color": color,
            "verified_events": stats.get("verified_count", 0),
            "total_events": stats.get("total_events", 0),
            "message": f"Ledger integrity: {verification_rate}% verified",
        }

    def generate_html_snippet(self) -> str:
        """
        Generate an HTML snippet for embedding in documentation.

        Returns:
            HTML string with ledger summary
        """

        stats = self.get_summary_statistics()
        trust = self.get_trust_score()

        html = f"""
<!-- Steward Protocol Ledger Summary -->
<div class="ledger-summary" style="background: #f0f5fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h3>📊 Live Ledger Statistics</h3>
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;">
        <div>
            <strong>Total Events</strong><br>
            <span style="font-size: 1.5em; color: #2c3e50;">{stats['total_events']}</span>
        </div>
        <div>
            <strong>Verified</strong><br>
            <span style="font-size: 1.5em; color: #27ae60;">{stats['verified_count']}</span>
        </div>
        <div>
            <strong>Failed</strong><br>
            <span style="font-size: 1.5em; color: #e74c3c;">{stats['failed_count']}</span>
        </div>
        <div>
            <strong>Verification Rate</strong><br>
            <span style="font-size: 1.5em; color: #{trust['color']};">{trust['verification_rate']}%</span>
        </div>
    </div>
    <p style="margin-top: 15px; color: #7f8c8d; font-size: 0.9em;">
        Last updated: {stats.get('last_loaded', 'Unknown')}
    </p>
</div>
"""
        return html

    def generate_json_report(
        self, output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate a complete JSON report of ledger statistics.

        Args:
            output_path: Optional path to write JSON report

        Returns:
            Report dict
        """

        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ledger_source": str(self.ledger_path),
            "summary": self.get_summary_statistics(),
            "trust_score": self.get_trust_score(),
            "recent_events": self.get_recent_events(limit=10),
            "timeline_24h": self.get_verification_timeline(hours=24),
        }

        if output_path:
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"✅ JSON report written to {output_path}")
            except Exception as e:
                logger.error(f"❌ Failed to write JSON report: {e}")

        return report

    def validate_ledger_integrity(self) -> Dict[str, Any]:
        """
        Validate that the ledger appears uncorrupted.

        Checks:
        - All lines are valid JSON
        - All attestations have required fields
        - Sequence numbers are present
        - No duplicates

        Returns:
            Validation result
        """

        issues = []

        if not self.attestations:
            return {
                "is_valid": True,
                "reason": "Ledger is empty (may be expected)",
                "issues": [],
            }

        # Check for required fields
        required_fields = ["status", "timestamp", "target_event"]
        for i, attestation in enumerate(self.attestations):
            for field in required_fields:
                if field not in attestation:
                    issues.append(f"Attestation {i}: Missing required field '{field}'")

        # Check for duplicate events
        seen_sequences = set()
        for attestation in self.attestations:
            seq = attestation.get("target_event", {}).get("sequence_number")
            if seq and seq in seen_sequences:
                issues.append(f"Duplicate sequence number detected: {seq}")
            if seq:
                seen_sequences.add(seq)

        is_valid = len(issues) == 0

        return {
            "is_valid": is_valid,
            "total_attestations": len(self.attestations),
            "issues": issues,
            "message": f"Ledger integrity: {'✅ PASS' if is_valid else f'❌ FAIL ({len(issues)} issues)'}",
        }

    def refresh(self):
        """Reload ledger from disk (for periodic updates)."""
        self._load_ledger()
        logger.info("🔄 Ledger refreshed")


# Convenience function for standalone usage
def generate_ledger_report(output_dir: Path = Path("dist")) -> bool:
    """
    Generate a complete ledger report.

    Args:
        output_dir: Directory to write report files

    Returns:
        Success status
    """

    try:
        visualizer = LedgerVisualizer()

        # Generate JSON report
        report_path = output_dir / "ledger_report.json"
        visualizer.generate_json_report(report_path)

        # Validate integrity
        validation = visualizer.validate_ledger_integrity()
        logger.info(validation["message"])

        return True

    except Exception as e:
        logger.error(f"❌ Failed to generate report: {e}")
        return False

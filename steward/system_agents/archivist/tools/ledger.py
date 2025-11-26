"""
ARCHIVIST Audit Ledger - Immutable record of all attestations.

The ledger is append-only and stores all verification results.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("ARCHIVIST_LEDGER")


class AuditLedger:
    """
    Append-only ledger for audit attestations.

    All attestations are written to a JSONL file for immutability.
    """

    def __init__(self, ledger_path: Path):
        """
        Initialize the audit ledger.

        Args:
            ledger_path: Path to the ledger file (JSONL format)
        """
        self.ledger_path = ledger_path
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file if it doesn't exist
        if not self.ledger_path.exists():
            self.ledger_path.touch()
            logger.info(f"📖 Ledger created: {ledger_path}")
        else:
            logger.info(f"📖 Ledger opened: {ledger_path}")

        self.entries_written = 0

    def append(self, attestation: Dict[str, Any]) -> bool:
        """
        Append an attestation to the ledger.

        Args:
            attestation: Attestation record to append

        Returns:
            bool: True if written successfully
        """
        try:
            with open(self.ledger_path, "a") as f:
                json.dump(attestation, f)
                f.write("\n")

            self.entries_written += 1
            logger.info(
                f"✅ Attestation written to ledger: {attestation.get('status')} "
                f"(entry #{self.entries_written})"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to write to ledger: {e}")
            return False

    def read_all(self) -> List[Dict[str, Any]]:
        """
        Read all attestations from the ledger.

        Returns:
            list: All attestation records
        """
        attestations = []

        if not self.ledger_path.exists():
            return attestations

        try:
            with open(self.ledger_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        attestations.append(json.loads(line))

            logger.info(f"📖 Read {len(attestations)} attestations from ledger")
            return attestations

        except Exception as e:
            logger.error(f"❌ Failed to read ledger: {e}")
            return []

    def read_latest(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Read the latest N attestations.

        Args:
            count: Number of recent attestations to read

        Returns:
            list: Latest attestation records
        """
        all_attestations = self.read_all()
        return all_attestations[-count:] if all_attestations else []

    def get_attestations_for_agent(
        self,
        agent_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all attestations for a specific agent.

        Args:
            agent_id: Agent identifier to filter by

        Returns:
            list: Attestations for that agent
        """
        all_attestations = self.read_all()
        return [
            a for a in all_attestations
            if a.get("target_event", {}).get("agent_id") == agent_id
        ]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get ledger statistics.

        Returns:
            dict: Statistics about the ledger
        """
        attestations = self.read_all()
        verified_count = sum(1 for a in attestations if a.get("status") == "VERIFIED")
        failed_count = sum(1 for a in attestations if a.get("status") == "FAILED")

        return {
            "total_attestations": len(attestations),
            "verified": verified_count,
            "failed": failed_count,
            "ledger_path": str(self.ledger_path),
            "entries_written_this_session": self.entries_written,
        }

#!/usr/bin/env python3
"""
ARCHIVIST Cartridge - The Audit & Verification Agent

This cartridge demonstrates multi-agent federation in the Steward Protocol:
1. Monitors events from HERALD (or other agents)
2. Verifies cryptographic signatures
3. Creates attestations for verified events
4. Maintains immutable audit trail

This is Agent #2 in the STEWARD Protocol ecosystem.

Usage:
    Standalone: python archivist/shim.py --action audit
    VibeOS:     kernel.load_cartridge("archivist").run_audit()
"""

import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

from archivist.tools.audit_tool import AuditTool
from archivist.tools.ledger import AuditLedger

logger = logging.getLogger("ARCHIVIST_CARTRIDGE")


class ArchivistCartridge:
    """
    ARCHIVIST - The Audit & Verification Agent for STEWARD Protocol.

    This cartridge encapsulates the audit workflow:
    1. Monitor: Read events from other agents' event logs
    2. Verify: Check cryptographic signatures
    3. Attest: Create verification records
    4. Record: Write to immutable audit ledger

    Architecture:
    - Vibe-OS compatible (ARCH-050 CartridgeBase)
    - Observer pattern (doesn't interfere with HERALD)
    - Event-driven (reacts to published events)
    - Governance-first (transparent audit trail)
    """

    # Cartridge Metadata (ARCH-050 required fields)
    name = "archivist"
    version = "1.0.0"
    description = "Autonomous audit and verification agent"
    author = "Steward Protocol"

    def __init__(self):
        """Initialize ARCHIVIST cartridge."""
        logger.info("🔍 ARCHIVIST v1.0: Cartridge initialization")

        # Initialize tools
        self.audit = AuditTool(agent_name="archivist")
        self.ledger = AuditLedger(ledger_path=Path("data/ledger/audit_trail.jsonl"))

        logger.info("✅ ARCHIVIST: Ready for audit operations")

    def get_config(self) -> Dict[str, Any]:
        """Get cartridge configuration (ARCH-050 interface)."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
        }

    def report_status(self) -> Dict[str, Any]:
        """Report cartridge status (ARCH-050 interface)."""
        audit_stats = self.audit.get_statistics()
        ledger_stats = self.ledger.get_statistics()

        return {
            "name": self.name,
            "version": self.version,
            "audit_statistics": audit_stats,
            "ledger_statistics": ledger_stats,
        }

    def read_agent_events(
        self,
        agent_name: str = "herald",
        event_file: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Read events from another agent's event log.

        Args:
            agent_name: Name of the agent to audit
            event_file: Optional custom event file path

        Returns:
            list: Events from the agent
        """
        if event_file is None:
            event_file = Path(f"data/events/{agent_name}.jsonl")

        if not event_file.exists():
            logger.warning(f"⚠️  No event log found for {agent_name}: {event_file}")
            return []

        events = []
        try:
            with open(event_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))

            logger.info(f"📖 Read {len(events)} events from {agent_name}")
            return events

        except Exception as e:
            logger.error(f"❌ Failed to read events from {agent_name}: {e}")
            return []

    def audit_agent(
        self,
        agent_name: str = "herald",
        event_file: Optional[Path] = None,
        public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Audit all events from a specific agent.

        This is the main workflow:
        1. Read events from agent's event log
        2. Verify each event's signature
        3. Create attestations
        4. Write to audit ledger

        Args:
            agent_name: Name of agent to audit
            event_file: Optional custom event file
            public_key: Optional public key for signature verification

        Returns:
            dict: Audit summary with statistics
        """
        try:
            logger.info("🔍 PHASE 1: EVENT COLLECTION")
            logger.info("=" * 70)

            # Step 1: Read events
            events = self.read_agent_events(agent_name, event_file)

            if not events:
                logger.warning(f"⚠️  No events to audit for {agent_name}")
                return {
                    "status": "completed",
                    "agent_audited": agent_name,
                    "events_found": 0,
                    "attestations_created": 0,
                }

            logger.info(f"✅ Found {len(events)} events to audit")

            # Step 2: Verify and attest each event
            logger.info("\n🔍 PHASE 2: VERIFICATION")
            logger.info("=" * 70)

            attestations_created = 0
            for idx, event in enumerate(events, 1):
                event_type = event.get("event_type", "unknown")
                sequence = event.get("sequence_number", idx)

                logger.info(f"\n[{idx}/{len(events)}] Auditing: {event_type} (seq={sequence})")

                # Verify signature
                verification_result = self.audit.verify_event_signature(
                    event,
                    public_key=public_key
                )

                # Create attestation
                attestation = self.audit.create_attestation(event, verification_result)

                # Write to ledger
                if self.ledger.append(attestation):
                    attestations_created += 1
                else:
                    logger.error(f"❌ Failed to write attestation for event {sequence}")

            # Step 3: Report results
            logger.info("\n🔍 PHASE 3: SUMMARY")
            logger.info("=" * 70)

            audit_stats = self.audit.get_statistics()
            ledger_stats = self.ledger.get_statistics()

            logger.info(f"✅ Audit complete:")
            logger.info(f"   Events audited: {len(events)}")
            logger.info(f"   Verified: {audit_stats['verified']}")
            logger.info(f"   Failed: {audit_stats['failed']}")
            logger.info(f"   Success rate: {audit_stats['success_rate']}")
            logger.info(f"   Attestations written: {attestations_created}")
            logger.info(f"   Ledger: {ledger_stats['ledger_path']}")

            logger.info("\n" + "=" * 70)
            logger.info("✅ AUDIT COMPLETE")
            logger.info("=" * 70)

            return {
                "status": "completed",
                "agent_audited": agent_name,
                "events_found": len(events),
                "attestations_created": attestations_created,
                "audit_statistics": audit_stats,
                "ledger_statistics": ledger_stats,
            }

        except Exception as e:
            logger.error(f"❌ Audit execution error: {e}")
            import traceback
            tb = traceback.format_exc()
            logger.error(f"   Traceback: {tb}")

            return {
                "status": "error",
                "reason": "audit_execution_error",
                "error": str(e),
            }

    def verify_specific_event(
        self,
        event: Dict[str, Any],
        public_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a single event (for testing or API use).

        Args:
            event: Event to verify
            public_key: Optional public key

        Returns:
            dict: Verification result
        """
        verification_result = self.audit.verify_event_signature(event, public_key)
        attestation = self.audit.create_attestation(event, verification_result)

        return {
            "verification": verification_result,
            "attestation": attestation,
        }


# Export for VibeOS cartridge loading
__all__ = ["ArchivistCartridge"]

"""
ARCHIVIST Cartridge
Core logic for Chain of Trust verification and archival
"""

import logging
import sys
import os

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from observer_tool import ObserverTool
from verifier_tool import VerifierTool
from ledger_tool import LedgerTool

logger = logging.getLogger("ARCHIVIST_CARTRIDGE")


class Archivist:
    """
    ARCHIVIST Agent - Chain of Trust Cartridge

    Mission:
    - Observe HERALD broadcasts
    - Verify their cryptographic signatures
    - Sign the verification proof
    - Record in immutable ledger
    """

    def __init__(self):
        self.logger = logger
        self.observer = ObserverTool()
        self.verifier = VerifierTool()
        self.ledger = LedgerTool()
        self.logger.info("🗃️  ARCHIVIST Cartridge initialized")

    def run_archival_cycle(self) -> bool:
        """
        Execute complete archival cycle:
        OBSERVE -> VERIFY -> SIGN -> RECORD
        """
        self.logger.info("=" * 70)
        self.logger.info("🗃️  ARCHIVIST ARCHIVAL CYCLE START")
        self.logger.info("=" * 70)

        try:
            # Phase 1: Observe
            self.logger.info("\n🗃️  PHASE 1: OBSERVATION")
            self.logger.info("-" * 70)
            broadcasts = self._phase_observe()

            if not broadcasts:
                self.logger.warning("⚠️  No broadcasts to archive")
                return False

            # Phase 2: Verify
            self.logger.info("\n🗃️  PHASE 2: VERIFICATION")
            self.logger.info("-" * 70)
            verified_broadcasts = self._phase_verify(broadcasts)

            if not verified_broadcasts:
                self.logger.warning("⚠️  No broadcasts passed verification")
                return False

            # Phase 3: Record
            self.logger.info("\n🗃️  PHASE 3: RECORDING")
            self.logger.info("-" * 70)
            recorded = self._phase_record(verified_broadcasts)

            # Summary
            self.logger.info("\n" + "=" * 70)
            self.logger.info("✅ ARCHIVAL CYCLE COMPLETE")
            self.logger.info("=" * 70)
            summary = self.ledger.get_ledger_summary()
            self.logger.info(
                f"📊 Ledger Status: {summary['total_entries']} entries recorded"
            )

            return recorded

        except Exception as e:
            self.logger.error(f"❌ Archival cycle failed: {e}")
            return False

    def _phase_observe(self):
        """Phase 1: Observe HERALD broadcasts"""
        self.logger.info("🔍 Observing HERALD broadcasts...")
        broadcasts = self.observer.fetch_tweets("simulated")

        valid_broadcasts = []
        for broadcast in broadcasts:
            if self.observer.validate_tweet_structure(broadcast):
                valid_broadcasts.append(broadcast)
                self.logger.info(f"✅ Valid broadcast: {broadcast['id']}")
            else:
                self.logger.warning(
                    f"❌ Invalid broadcast structure: {broadcast.get('id')}"
                )

        self.logger.info(f"📡 Observed {len(valid_broadcasts)} valid broadcasts")
        return valid_broadcasts

    def _phase_verify(self, broadcasts):
        """Phase 2: Verify signatures"""
        self.logger.info("🔐 Verifying HERALD signatures...")
        verified = []

        for broadcast in broadcasts:
            is_valid, details = self.verifier.verify_signature(
                broadcast["content"], broadcast["signature"], broadcast["author"]
            )

            if is_valid:
                # Create verification proof
                proof = self.verifier.create_verification_proof(broadcast)
                verified.append(
                    {
                        "broadcast": broadcast,
                        "proof": proof,
                        "verification_details": details,
                    }
                )
                self.logger.info(f"✅ Verified: {broadcast['id']}")
            else:
                self.logger.warning(f"❌ Verification failed: {details}")

        self.logger.info(f"✅ Verified {len(verified)} broadcasts")
        return verified

    def _phase_record(self, verified_broadcasts):
        """Phase 3: Record to ledger"""
        self.logger.info("📝 Recording to chain of trust ledger...")
        recorded_count = 0

        for item in verified_broadcasts:
            if self.ledger.write_entry(item["broadcast"], item["proof"]):
                recorded_count += 1
                self.logger.info(f"✅ Recorded: {item['broadcast']['id']}")
            else:
                self.logger.error(f"❌ Failed to record: {item['broadcast']['id']}")

        self.logger.info(f"📚 Recorded {recorded_count} entries to ledger")
        return recorded_count > 0

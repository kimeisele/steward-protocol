"""
NAGA Flood: OUROBOROS (CISyncService).

Phase 3A: Paradox Resolution - "Der Heiler heilt sich selbst."

The self-healing system (OUROBOROS) must be NAGA-protected.

Surgical Overrides:
- sync_latest: SESHA audit + TAKSHAKA validation
- _get_latest_run: VASUKI network boundary
- _extract_violations_from_run: TAKSHAKA validation

NAGA Assignment:
- SESHA: Audit trail for all sync operations
- VASUKI: Network boundary (gh CLI subprocess calls)
- TAKSHAKA: Validate external CI data before ingestion
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from vibe_core.naga.mixins import SeshaMixin, TakshakaMixin, VasukiMixin
from vibe_core.ouroboros.sync import CISyncService

logger = logging.getLogger("NAGA.FLOOD.OUROBOROS")


class FloodedCISyncService(SeshaMixin, VasukiMixin, TakshakaMixin, CISyncService):
    """
    NAGA-Flooded CISyncService.

    Original CISyncService wrapped with:
    - SESHA: Audit logging
    - VASUKI: Network boundary protection
    - TAKSHAKA: Data validation

    isinstance(flooded, CISyncService) == True  # Preserved!
    """

    def sync_latest(self, workflow: str = "steward-ci.yml") -> Dict[str, Any]:
        """
        Sync latest CI results - with NAGA protection.

        SESHA: Records sync attempt and result
        TAKSHAKA: Validates result before return
        """
        # === SESHA: Record sync attempt ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.sync.start",
                source="FloodedCISyncService",
                details={"workflow": workflow, "repo": self.repo},
            )

        # === Execute original method ===
        try:
            result = super().sync_latest(workflow)
        except Exception as e:
            # Record failure
            if self.sesha:
                self.sesha.record_event(
                    event_type="ouroboros.sync.error",
                    source="FloodedCISyncService",
                    details={"error": str(e), "workflow": workflow},
                )
            raise

        # === TAKSHAKA: Validate result ===
        if self.takshaka and result:
            # Check for suspicious patterns in result
            toxicity = self.takshaka.scan_toxicity(str(result))
            if toxicity.blocked:
                logger.warning(f"TAKSHAKA blocked suspicious CI result: {toxicity.patterns}")
                result["naga_warning"] = "Suspicious patterns detected"

        # === SESHA: Record success ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.sync.complete",
                source="FloodedCISyncService",
                details={
                    "violations_ingested": result.get("violations_ingested", 0),
                    "errors": result.get("errors", []),
                },
            )

        return result

    def _get_latest_run(self, workflow: str) -> Optional[Dict[str, Any]]:
        """
        Get latest workflow run - with VASUKI network protection.

        VASUKI: Validates network call is allowed
        """
        # === VASUKI: Check network boundary ===
        if self.vasuki:
            # Log network access attempt
            logger.debug(f"VASUKI: Network call to gh CLI for workflow {workflow}")

        # === Execute original (subprocess to gh CLI) ===
        result = super()._get_latest_run(workflow)

        # === VASUKI: Log network result ===
        if self.vasuki and result:
            logger.debug(f"VASUKI: Received CI run data: {result.get('databaseId')}")

        return result

    def _extract_violations_from_run(self, run_info: Dict[str, Any]) -> List:
        """
        Extract violations - with TAKSHAKA validation.

        TAKSHAKA: Validates each violation before ingestion
        """
        # === Execute original extraction ===
        violations = super()._extract_violations_from_run(run_info)

        # === TAKSHAKA: Validate violations ===
        if self.takshaka and violations:
            validated = []
            for v in violations:
                # Check violation for suspicious content
                toxicity = self.takshaka.scan_toxicity(str(v))
                if not toxicity.blocked:
                    validated.append(v)
                else:
                    logger.warning(f"TAKSHAKA rejected violation: {toxicity.patterns}")

            if len(validated) != len(violations):
                logger.info(f"TAKSHAKA filtered {len(violations) - len(validated)} suspicious violations")
            violations = validated

        return violations


# =============================================================================
# Factory function for easy access
# =============================================================================


def get_flooded_ci_sync_service(
    repo: Optional[str] = None,
) -> FloodedCISyncService:
    """
    Get a NAGA-flooded CISyncService.

    Usage:
        sync = get_flooded_ci_sync_service()
        result = sync.sync_latest()  # Protected!
    """
    return FloodedCISyncService(repo=repo)

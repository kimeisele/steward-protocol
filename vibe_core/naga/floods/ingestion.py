"""
NAGA Flood: ViolationIngester.

Phase 3A: Surgical Override - All violation data must be audited.

Surgical Overrides:
- ingest: SESHA audit + TAKSHAKA validation
- ingest_from_json: SESHA audit
- ingest_ruff_output: SESHA audit
- ingest_pytest_output: SESHA audit

NAGA Assignment:
- SESHA: Audit trail for all ingestion operations
- TAKSHAKA: Validate violation payloads for malicious content
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.naga.mixins import ChitraguptaMixin, SeshaMixin, TakshakaMixin
from vibe_core.ouroboros.ingestion import (
    ViolationIngester,
    ViolationRecord,
    ViolationSource,
)

if TYPE_CHECKING:
    from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

logger = logging.getLogger("NAGA.FLOOD.INGESTION")


class FloodedViolationIngester(SeshaMixin, TakshakaMixin, ChitraguptaMixin, ViolationIngester):
    """
    NAGA-Flooded ViolationIngester.

    Original ViolationIngester wrapped with:
    - SESHA: Audit logging for all ingestion operations
    - TAKSHAKA: Validate violation payloads before ingestion
    - CHITRAGUPTA: Performance profiling

    isinstance(flooded, ViolationIngester) == True  # Preserved!
    """

    def ingest(
        self,
        violations: List[ViolationRecord],
        verify: Optional[bool] = None,
    ) -> int:
        """
        Ingest violations - with NAGA protection.

        SESHA: Audit trail for ingestion
        TAKSHAKA: Validate violation payloads
        CHITRAGUPTA: Profile ingestion time
        """
        start_time = time.time()

        # === SESHA: Record ingestion start ===
        if self.sesha:
            source = violations[0].source.value if violations else "unknown"
            self.sesha.record_event(
                event_type="ingestion.ingest.start",
                source="FloodedViolationIngester",
                details={
                    "count": len(violations),
                    "source": source,
                    "verify": verify,
                },
            )

        # === TAKSHAKA: Validate violation payloads ===
        blocked_count = 0
        if self.takshaka:
            safe_violations = []
            for v in violations:
                # Check for malicious content in violation messages
                toxicity = self.takshaka.scan_toxicity(v.message)
                if toxicity.blocked:
                    logger.warning(f"TAKSHAKA: Blocked suspicious violation message: {v.rule_id}")
                    blocked_count += 1
                else:
                    safe_violations.append(v)
            violations = safe_violations

        # === Execute original ingest ===
        count = super().ingest(violations, verify)

        # === CHITRAGUPTA: Profile ingestion time ===
        elapsed_ms = (time.time() - start_time) * 1000
        if self.chitragupta:
            self.chitragupta.record_profile(
                operation="ingestion.ingest",
                duration_ms=elapsed_ms,
                metadata={
                    "ingested": count,
                    "blocked": blocked_count,
                },
            )

        # === SESHA: Record ingestion complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.ingest.complete",
                source="FloodedViolationIngester",
                details={
                    "ingested_count": count,
                    "blocked_count": blocked_count,
                    "duration_ms": elapsed_ms,
                },
            )

        return count

    def ingest_from_json(self, json_path: Path, source: ViolationSource) -> int:
        """
        Ingest from JSON file - with NAGA protection.

        SESHA: Audit trail for file-based ingestion
        """
        # === SESHA: Record file ingestion start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.from_json.start",
                source="FloodedViolationIngester",
                details={
                    "path": str(json_path),
                    "source_type": source.value,
                },
            )

        # === Execute original ===
        count = super().ingest_from_json(json_path, source)

        # === SESHA: Record file ingestion complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.from_json.complete",
                source="FloodedViolationIngester",
                details={
                    "path": str(json_path),
                    "ingested_count": count,
                },
            )

        return count

    def ingest_ruff_output(self, ruff_output: str) -> int:
        """
        Ingest ruff output - with NAGA protection.

        SESHA: Audit trail for ruff ingestion
        """
        # === SESHA: Record ruff ingestion start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.ruff.start",
                source="FloodedViolationIngester",
                details={"output_length": len(ruff_output)},
            )

        # === Execute original ===
        count = super().ingest_ruff_output(ruff_output)

        # === SESHA: Record ruff ingestion complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.ruff.complete",
                source="FloodedViolationIngester",
                details={"ingested_count": count},
            )

        return count

    def ingest_pytest_output(self, pytest_json: Dict[str, Any]) -> int:
        """
        Ingest pytest output - with NAGA protection.

        SESHA: Audit trail for pytest ingestion
        """
        # === SESHA: Record pytest ingestion start ===
        if self.sesha:
            test_count = len(pytest_json.get("tests", []))
            self.sesha.record_event(
                event_type="ingestion.pytest.start",
                source="FloodedViolationIngester",
                details={"test_count": test_count},
            )

        # === Execute original ===
        count = super().ingest_pytest_output(pytest_json)

        # === SESHA: Record pytest ingestion complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ingestion.pytest.complete",
                source="FloodedViolationIngester",
                details={"ingested_count": count},
            )

        return count


# =============================================================================
# Factory
# =============================================================================


def get_flooded_violation_ingester(
    kg: Optional["UnifiedKnowledgeGraph"] = None,
    verify: bool = False,
    project_root: Optional[Path] = None,
) -> FloodedViolationIngester:
    """Get a NAGA-flooded ViolationIngester."""
    return FloodedViolationIngester(
        kg=kg,
        verify=verify,
        project_root=project_root,
    )

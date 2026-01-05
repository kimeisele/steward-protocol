"""
NAGA Flood: OuroborosLoopOrchestrator.

Phase 3A: Surgical Override - The digestive system must be monitored.

Surgical Overrides:
- discover_sources: SESHA audit + NARADA recon
- parse_source: SESHA audit
- ingest_all_sources: SESHA audit + CHITRAGUPTA profiling

NAGA Assignment:
- SESHA: Audit trail for all loop operations
- NARADA: Reconnaissance for source discovery
- CHITRAGUPTA: Performance profiling for full loop
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from vibe_core.naga.mixins import ChitraguptaMixin, NaradaMixin, SeshaMixin
from vibe_core.ouroboros.ingestion import ViolationRecord
from vibe_core.ouroboros.loop_orchestrator import (
    IngestionResult,
    OuroborosLoopOrchestrator,
)

if TYPE_CHECKING:
    from vibe_core.ouroboros.ingestion import ViolationIngester
    from vibe_core.ouroboros.parser_loader import ViolationParserLoader

logger = logging.getLogger("NAGA.FLOOD.LOOPORCH")


class FloodedOuroborosLoopOrchestrator(SeshaMixin, NaradaMixin, ChitraguptaMixin, OuroborosLoopOrchestrator):
    """
    NAGA-Flooded OuroborosLoopOrchestrator.

    Original OuroborosLoopOrchestrator wrapped with:
    - SESHA: Audit logging for all operations
    - NARADA: Reconnaissance during source discovery
    - CHITRAGUPTA: Performance profiling

    isinstance(flooded, OuroborosLoopOrchestrator) == True  # Preserved!
    """

    def discover_sources(self) -> List[Path]:
        """
        Discover violation sources - with NAGA protection.

        SESHA: Audit trail for discovery
        NARADA: Reconnaissance observations
        """
        # === SESHA: Record discovery start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.discover.start",
                source="FloodedOuroborosLoopOrchestrator",
                details={"workspace": str(self._workspace)},
            )

        # === Execute original ===
        sources = super().discover_sources()

        # === NARADA: Record reconnaissance ===
        if self.narada:
            self.narada.observe(
                observation_type="source_discovery",
                target="ouroboros",
                data={
                    "sources_found": len(sources),
                    "source_names": [s.name for s in sources[:10]],  # First 10
                },
            )

        # === SESHA: Record discovery complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.discover.complete",
                source="FloodedOuroborosLoopOrchestrator",
                details={
                    "sources_found": len(sources),
                    "workspace": str(self._workspace),
                },
            )

        return sources

    def parse_source(self, source_path: Path) -> List[ViolationRecord]:
        """
        Parse a single source - with NAGA protection.

        SESHA: Audit trail for parsing
        """
        # === SESHA: Record parse start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.parse.start",
                source="FloodedOuroborosLoopOrchestrator",
                details={"source_path": str(source_path)},
            )

        # === Execute original ===
        violations = super().parse_source(source_path)

        # === SESHA: Record parse complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.parse.complete",
                source="FloodedOuroborosLoopOrchestrator",
                details={
                    "source_path": str(source_path),
                    "violations_found": len(violations),
                },
            )

        return violations

    def ingest_all_sources(self) -> IngestionResult:
        """
        Run the full ingestion loop - with NAGA protection.

        SESHA: Audit trail for full loop
        CHITRAGUPTA: Profile the entire operation
        """
        start_time = time.time()

        # === SESHA: Record loop start ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.loop.start",
                source="FloodedOuroborosLoopOrchestrator",
                details={"workspace": str(self._workspace)},
            )

        # === Execute original ===
        result = super().ingest_all_sources()

        # === CHITRAGUPTA: Profile loop duration ===
        elapsed_ms = (time.time() - start_time) * 1000
        if self.chitragupta:
            self.chitragupta.record_profile(
                operation="ouroboros.loop",
                duration_ms=elapsed_ms,
                metadata={
                    "sources_found": result.sources_found,
                    "sources_parsed": result.sources_parsed,
                    "violations_found": result.violations_found,
                    "ingested_count": result.ingested_count,
                    "errors": len(result.errors),
                },
            )

        # === SESHA: Record loop complete ===
        if self.sesha:
            self.sesha.record_event(
                event_type="ouroboros.loop.complete",
                source="FloodedOuroborosLoopOrchestrator",
                details={
                    "sources_found": result.sources_found,
                    "sources_parsed": result.sources_parsed,
                    "violations_found": result.violations_found,
                    "ingested_count": result.ingested_count,
                    "errors": result.errors,
                    "duration_ms": elapsed_ms,
                    "success": result.success,
                },
            )

        return result


# =============================================================================
# Factory
# =============================================================================


def get_flooded_loop_orchestrator(
    workspace: Optional[Path] = None,
    parser_loader: Optional["ViolationParserLoader"] = None,
    ingester: Optional["ViolationIngester"] = None,
    verify_violations: bool = False,
) -> FloodedOuroborosLoopOrchestrator:
    """Get a NAGA-flooded OuroborosLoopOrchestrator."""
    return FloodedOuroborosLoopOrchestrator(
        workspace=workspace,
        parser_loader=parser_loader,
        ingester=ingester,
        verify_violations=verify_violations,
    )

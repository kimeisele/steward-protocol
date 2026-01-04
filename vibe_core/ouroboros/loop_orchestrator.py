"""
OUROBOROS Loop Orchestrator - Wires Parsers → Ingestion → Knowledge Graph.

This module closes the OUROBOROS loop by:
1. Discovering violation sources (CI artifacts, reports, JSON files)
2. Parsing them with auto-discovered parsers (ViolationParserLoader)
3. Ingesting violations into Knowledge Graph (ViolationIngester)
4. Making violations available for healing (CorrectionDispatcher)

Usage:
    from vibe_core.ouroboros.loop_orchestrator import OuroborosLoopOrchestrator

    # In biorhythm tick:
    orchestrator = OuroborosLoopOrchestrator(workspace=Path.cwd())
    result = orchestrator.ingest_all_sources()
    # result.ingested_count = 42
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.ouroboros.ingestion import ViolationIngester, ViolationRecord, ViolationSource
from vibe_core.ouroboros.parser_loader import ViolationParserLoader

logger = logging.getLogger("OUROBOROS.LOOP")


@dataclass
class IngestionResult:
    """Result of an ingestion run."""

    sources_found: int = 0
    sources_parsed: int = 0
    violations_found: int = 0
    ingested_count: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


class OuroborosLoopOrchestrator:
    """
    Orchestrates the OUROBOROS loop: Sources → Parsers → Ingestion → KG.

    This is the "digestive system" that processes violation sources
    and feeds them into the Knowledge Graph for learning and healing.

    OPUS-LZ3: Completes the loop that was previously broken.
    """

    # Default source locations to scan
    DEFAULT_SOURCE_PATTERNS = [
        # CI artifacts
        "watchman_report.json",
        "**/watchman_report.json",
        # Reports
        "REPORT.md",
        "**/REPORT*.md",
        # Audit files
        "**/AUDIT*.md",
        "**/audit_*.json",
        # Test coverage
        "**/coverage*.md",
        "**/test_report*.json",
    ]

    def __init__(
        self,
        workspace: Optional[Path] = None,
        parser_loader: Optional[ViolationParserLoader] = None,
        ingester: Optional[ViolationIngester] = None,
        verify_violations: bool = False,
    ):
        """
        Initialize the orchestrator.

        Args:
            workspace: Root directory to scan for sources
            parser_loader: Optional custom parser loader
            ingester: Optional custom ingester
            verify_violations: Whether to verify violations before ingesting
        """
        self._workspace = workspace or Path.cwd()
        self._parser_loader = parser_loader
        self._ingester = ingester
        self._verify = verify_violations
        self._last_result: Optional[IngestionResult] = None

    @property
    def parser_loader(self) -> ViolationParserLoader:
        """Lazy-load parser loader."""
        if self._parser_loader is None:
            self._parser_loader = ViolationParserLoader()
            self._parser_loader.discover_and_load()
        return self._parser_loader

    @property
    def ingester(self) -> ViolationIngester:
        """Lazy-load ingester."""
        if self._ingester is None:
            self._ingester = ViolationIngester(
                verify=self._verify,
                project_root=self._workspace,
            )
        return self._ingester

    def discover_sources(self) -> List[Path]:
        """
        Discover all violation source files in workspace.

        Uses patterns from registered parsers.
        """
        sources: List[Path] = []
        seen: set = set()

        # Get patterns from all parsers
        all_patterns = self.parser_loader.get_all_patterns()

        # Add default patterns
        patterns = list(set(all_patterns + self.DEFAULT_SOURCE_PATTERNS))

        for pattern in patterns:
            for path in self._workspace.glob(pattern):
                if path.is_file() and path not in seen:
                    sources.append(path)
                    seen.add(path)

        logger.debug(f"Discovered {len(sources)} violation sources")
        return sources

    def parse_source(self, source_path: Path) -> List[ViolationRecord]:
        """
        Parse a single source file.

        Args:
            source_path: Path to the source file

        Returns:
            List of ViolationRecord from the file
        """
        parser = self.parser_loader.get_parser_for(source_path)

        if parser is None:
            logger.debug(f"No parser found for: {source_path.name}")
            return []

        try:
            violations = parser.parse(source_path)
            logger.debug(f"Parsed {len(violations)} violations from {source_path.name}")
            return violations
        except Exception as e:
            logger.warning(f"Failed to parse {source_path.name}: {e}")
            return []

    def ingest_all_sources(self) -> IngestionResult:
        """
        Run the full ingestion loop.

        Discovers sources → parses them → ingests into KG.

        Returns:
            IngestionResult with counts and any errors
        """
        result = IngestionResult()

        # Step 1: Discover sources
        sources = self.discover_sources()
        result.sources_found = len(sources)

        if not sources:
            logger.info("🐍 OUROBOROS: No violation sources found")
            self._last_result = result
            return result

        # Step 2: Parse all sources
        all_violations: List[ViolationRecord] = []

        for source_path in sources:
            try:
                violations = self.parse_source(source_path)
                if violations:
                    all_violations.extend(violations)
                    result.sources_parsed += 1
            except Exception as e:
                result.errors.append(f"Parse error for {source_path.name}: {e}")

        result.violations_found = len(all_violations)

        if not all_violations:
            logger.info("🐍 OUROBOROS: No violations found in sources")
            self._last_result = result
            return result

        # Step 3: Ingest into Knowledge Graph
        try:
            ingested = self.ingester.ingest(all_violations)
            result.ingested_count = ingested
            logger.info(f"🐍 OUROBOROS: Ingested {ingested} violations from {result.sources_parsed} sources")
        except Exception as e:
            result.errors.append(f"Ingestion error: {e}")
            logger.warning(f"🐍 OUROBOROS: Ingestion failed: {e}")

        self._last_result = result
        return result

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status for observability."""
        parsers = self.parser_loader.list_parsers()
        return {
            "workspace": str(self._workspace),
            "parsers_loaded": len(parsers),
            "parser_names": parsers,
            "verify_enabled": self._verify,
            "last_result": (
                {
                    "sources_found": self._last_result.sources_found,
                    "violations_ingested": self._last_result.ingested_count,
                    "timestamp": self._last_result.timestamp,
                }
                if self._last_result
                else None
            ),
        }


# =============================================================================
# Factory and Integration
# =============================================================================


def get_loop_orchestrator(
    workspace: Optional[Path] = None,
) -> OuroborosLoopOrchestrator:
    """
    Factory function for OuroborosLoopOrchestrator.

    Uses ServiceRegistry for dependencies if available.
    """
    return OuroborosLoopOrchestrator(workspace=workspace)


def run_ingestion_tick(workspace: Optional[Path] = None) -> IngestionResult:
    """
    Convenience function to run one ingestion cycle.

    Suitable for calling from biorhythm or CLI.

    Args:
        workspace: Optional workspace path

    Returns:
        IngestionResult
    """
    orchestrator = get_loop_orchestrator(workspace)
    return orchestrator.ingest_all_sources()


__all__ = [
    "OuroborosLoopOrchestrator",
    "IngestionResult",
    "get_loop_orchestrator",
    "run_ingestion_tick",
]

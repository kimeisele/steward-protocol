"""
SRAVANAM — Fractal Cell Scanner (The Hearing)
===============================================

"śravaṇaṁ kīrtanaṁ viṣṇoḥ smaraṇaṁ pāda-sevanam
arcanaṁ vandanaṁ dāsyaṁ sakhyam ātma-nivedanam"

Sravanam (Hearing) is the FIRST step of NavaBhakti.
Before you chant (Kirtanam/heal), you must LISTEN.

This module provides fractal, per-Cell scanning that integrates
with the Mahamantra heartbeat (tick()). No monolithic file scans.

Architecture:
    1. SravanamScanner — scans one Cell at a time via ShuddhiEngine.scan_cell()
    2. SravanamListener — tick listener, scans cells at current position
    3. wire_sravanam() — registers the listener on mahamantra.register_listener()

The scan results are vibrations — they go to Akash, not to disk.
Healing (Kirtanam) is a SEPARATE decision, triggered by accumulated vibrations.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"

import logging
from dataclasses import dataclass, field
from itertools import islice
from typing import TYPE_CHECKING, Dict, List, Optional

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, WORDS
from vibe_core.mahamantra.substrate.shuddhi import ShuddhiResult

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.cell import MahaCellUnified

logger = logging.getLogger("SHUDDHI.SRAVANAM")


# =============================================================================
# GUARDIAN → RULE MAPPING
# =============================================================================
# Each guardian position maps to the rules most relevant to its domain.
# This is NOT random — it follows the Mahajana responsibilities:
#
#   Vyasa (0)     = missing_mahajana, broken_genesis  (identity)
#   Brahma (1)    = any_type_usage                    (creation purity)
#   Narada (2)    = silent_failure                    (devotion = honesty)
#   Shambhu (3)   = subprocess_timeout                (destruction boundaries)
#   Prithu (4)    = path_scanning_discovery            (earth = filesystem)
#   Kumaras (5)   = missing_fractal_routing            (purification = routing)
#   Kapila (6)    = get_instance_antipattern           (analysis = patterns)
#   Manu (7)      = hardcoded_constants                (law = constants)
#   Parashurama (8) = unsafe_io_write                  (warrior = I/O defense)
#   Prahlada (9)  = direct_registry_instantiation      (resilience)
#   Janaka (10)   = iterdir_discovery                  (duty = orderly discovery)
#   Bhishma (11)  = any_type_detection                 (vow = type safety)
#   Nrisimha (12) = fractal_routing_detection          (protection)
#   Bali (13)     = unsafe_io_write                    (surrender = safe I/O)
#   Shuka (14)    = silent_failure                     (vision = see errors)
#   Yamaraja (15) = missing_fractal_routing            (judgment = compliance)

GUARDIAN_RULE_MAP: Dict[str, List[str]] = {
    "vyasa": ["missing_mahajana", "broken_genesis", "F811"],
    "brahma": ["any_type_usage"],
    "narada": ["silent_failure"],
    "shambhu": ["subprocess_timeout"],
    "prithu": ["path_scanning_discovery"],
    "kumaras": ["missing_fractal_routing"],
    "kapila": ["get_instance_antipattern"],
    "manu": ["hardcoded_constants"],
    "parashurama": ["unsafe_io_write"],
    "prahlada": ["direct_registry_instantiation"],
    "janaka": ["iterdir_discovery"],
    "bhishma": ["any_type_usage"],
    "nrisimha": ["missing_fractal_routing"],
    "bali": ["unsafe_io_write"],
    "shuka": ["silent_failure"],
    "yamaraja": ["missing_fractal_routing"],
}


# =============================================================================
# SRAVANAM RESULT — What was heard
# =============================================================================


@dataclass(frozen=True)
class SravanamReport:
    """Summary of one sravanam cycle (one tick's worth of listening)."""

    position: int
    guardian: str
    cells_scanned: int
    violations_found: int
    results: List[ShuddhiResult] = field(default_factory=list)


# =============================================================================
# SRAVANAM SCANNER — Scans Cells from CellRouter
# =============================================================================


class SravanamScanner:
    """
    Fractal Cell Scanner.

    Scans cells in the CellRouter one-at-a-time using
    ShuddhiEngine.scan_cell() — no file I/O, pure RAM.

    Usage:
        scanner = SravanamScanner()
        for result in scanner.scan_position(5, router):
            print(result)
    """

    def __init__(self) -> None:
        self._engine = None  # Lazy
        self._total_scanned: int = 0
        self._total_violations: int = 0

    @property
    def engine(self):
        """Lazy-load ShuddhiEngine to avoid circular imports."""
        if self._engine is None:
            from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine

            self._engine = ShuddhiEngine()
        return self._engine

    def scan_cell(
        self,
        cell: "MahaCellUnified",
        rule_ids: Optional[List[str]] = None,
    ) -> List[ShuddhiResult]:
        """
        Scan ONE cell with given rules. Pure RAM, no I/O.

        Args:
            cell: The MahaCellUnified to scan.
            rule_ids: Rules to check. None = all.

        Returns:
            List of ShuddhiResults for violations found.
        """
        # Extract source code from cell payload
        source = self._extract_source(cell)
        if not source:
            return []

        file_path = self._extract_file_path(cell)
        targets = rule_ids or self.engine.list_remedies()
        results = []

        for rule_id in targets:
            result = self.engine.scan_cell(source, rule_id, file_path)
            if result:
                results.append(result)

        self._total_scanned += KSETRAJNA
        self._total_violations += len(results)
        return results

    def scan_position(
        self,
        position: int,
        max_cells: int = KSETRAJNA,
    ) -> SravanamReport:
        """
        Scan cells at a specific mahamantra position.

        Args:
            position: 0-15 mahamantra position.
            max_cells: Maximum cells to scan per position (default: 1).

        Returns:
            SravanamReport with scan results.
        """
        from vibe_core.mahamantra.substrate.cell_router import get_router
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        router = get_router()
        guardian = ALL_GUARDIANS[position] if position < WORDS else "unknown"
        rule_ids = GUARDIAN_RULE_MAP.get(guardian, [])

        if not rule_ids:
            return SravanamReport(
                position=position,
                guardian=guardian,
                cells_scanned=0,
                violations_found=0,
            )

        # Get cells at this position (limited by max_cells)
        cells = list(islice(router.get_by_position(position), max_cells))
        all_results: List[ShuddhiResult] = []

        for cell in cells:
            results = self.scan_cell(cell, rule_ids=rule_ids)
            all_results.extend(results)

        if all_results:
            logger.info(
                "[SRAVANAM] Position %d (%s): %d violations in %d cells",
                position,
                guardian,
                len(all_results),
                len(cells),
            )

        return SravanamReport(
            position=position,
            guardian=guardian,
            cells_scanned=len(cells),
            violations_found=len(all_results),
            results=all_results,
        )

    def scan_all_positions(self, max_cells_per_position: int = KSETRAJNA) -> List[SravanamReport]:
        """
        Scan all 16 positions. Still atomic per-cell, just iterates positions.

        Args:
            max_cells_per_position: How many cells to scan at each position.

        Returns:
            List of 16 SravanamReports.
        """
        return [self.scan_position(pos, max_cells=max_cells_per_position) for pos in range(WORDS)]

    @staticmethod
    def _extract_source(cell: "MahaCellUnified") -> Optional[str]:
        """Extract source code from cell payload."""
        payload = getattr(cell, "payload", None)
        if payload is None:
            return None

        # CSTFragment has source_code
        if hasattr(payload, "source_code"):
            return payload.source_code

        # Raw bytes payload
        if isinstance(payload, bytes):
            try:
                return payload.decode("utf-8")
            except UnicodeDecodeError:
                return None

        # String payload
        if isinstance(payload, str):
            return payload

        return None

    @staticmethod
    def _extract_file_path(cell: "MahaCellUnified"):
        """Extract file path from cell payload if available."""
        from pathlib import Path

        payload = getattr(cell, "payload", None)
        if payload and hasattr(payload, "file_path"):
            return payload.file_path
        return Path(f"<cell:0x{cell.header.sravanam:08X}>")

    @property
    def stats(self) -> Dict[str, int]:
        """Return scanning statistics."""
        return {
            "total_scanned": self._total_scanned,
            "total_violations": self._total_violations,
        }


# =============================================================================
# SRAVANAM LISTENER — Tick-Driven Scanning
# =============================================================================


class SravanamListener:
    """
    Tick listener that performs fractal scanning on each heartbeat.

    Registered via mahamantra.register_listener(). On each tick,
    scans cells at the current position with the guardian's rules.

    One cell. One rule. Per tick. The heartbeat IS the scan rhythm.
    """

    def __init__(self, max_cells_per_tick: int = KSETRAJNA) -> None:
        self._scanner = SravanamScanner()
        self._max_cells = max_cells_per_tick
        self._reports: List[SravanamReport] = []
        self._enabled: bool = True

    def __call__(self, tick_state) -> None:
        """Called by mahamantra._broadcast() on every tick."""
        if not self._enabled:
            return

        # TickState may be dict or dataclass — handle both
        if isinstance(tick_state, dict):
            position = tick_state.get("position")
        else:
            position = getattr(tick_state, "position", None)
        if position is None:
            return

        report = self._scanner.scan_position(position, max_cells=self._max_cells)
        if report.violations_found > 0:
            self._reports.append(report)

    def enable(self) -> None:
        """Enable tick-driven scanning."""
        self._enabled = True

    def disable(self) -> None:
        """Disable tick-driven scanning."""
        self._enabled = False

    @property
    def scanner(self) -> SravanamScanner:
        """Access the underlying scanner."""
        return self._scanner

    @property
    def reports(self) -> List[SravanamReport]:
        """All reports with violations found."""
        return self._reports

    @property
    def total_violations(self) -> int:
        """Total violations found across all ticks."""
        return sum(r.violations_found for r in self._reports)


# =============================================================================
# WIRING — Connect Sravanam to the Mahamantra heartbeat
# =============================================================================

_listener: Optional[SravanamListener] = None


def wire_sravanam(max_cells_per_tick: int = KSETRAJNA) -> SravanamListener:
    """
    Wire the SravanamListener to the Mahamantra heartbeat.

    Called once at boot. Idempotent.

    Returns:
        The active SravanamListener.
    """
    global _listener
    if _listener is not None:
        return _listener

    try:
        from vibe_core.mahamantra import mahamantra

        _listener = SravanamListener(max_cells_per_tick=max_cells_per_tick)
        mahamantra.register_listener(_listener)
        logger.info("👂 SravanamListener wired to Mahamantra heartbeat")
        return _listener

    except Exception as exc:
        logger.warning("Failed to wire SravanamListener: %s", exc)
        # Return a disconnected listener — it still works, just not auto-triggered
        _listener = SravanamListener(max_cells_per_tick=max_cells_per_tick)
        return _listener


def get_sravanam_listener() -> Optional[SravanamListener]:
    """Get the active SravanamListener (None if not wired)."""
    return _listener


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GUARDIAN_RULE_MAP",
    "SravanamReport",
    "SravanamScanner",
    "SravanamListener",
    "wire_sravanam",
    "get_sravanam_listener",
]

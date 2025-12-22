"""
OPUS-127: KARMA SENSE - The Eye of Memory
==========================================

Sanskrit: Karma = Action, Samskara = Imprint

This cortex module gives MANAS the ability to PERCEIVE historical patterns
in the Parampara lineage chain - detecting CHRONIC PAIN through repeated repairs.

Following Bhagavad Gita 4.17:
"karmaṇo hy api boddhavyaṁ boddhavyaṁ ca vikarmaṇaḥ"
(One must understand the nature of action... and the nature of wrong action)

MANAS' Karma Duties:
1. HOTSPOT DETECTION: Find files repaired 3+ times -> structural weakness
2. PATTERN RECOGNITION: Identify recurring disharmony types
3. CHRONIC PAIN ALERT: Escalate persistent issues for deeper intervention

The Four Senses of MANAS:
- PrakritiSense: "What is the state of the world?" (Code/Git/State)
- DharmaSense: "Is this action righteous?" (Ethics/Permissions)
- SutraSense: "What knowledge is missing?" (Doc/Code alignment)
- KarmaSense: "What has happened before?" (Historical patterns)

Together they form the complete cognitive perception of MANAS.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "The Memory Sense - chronic pain detection from lineage"
  - path: docs/architecture/OPUS/127-KARMA-SENSE.md
    required: true
    rationale: "The master doc for historical pattern analysis"

wiring:
  - pattern: "class KarmaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
  - pattern: "def find_hotspots"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
  - pattern: "class ChronicPainReport"
    in: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
-->
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import BaseSense

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.KarmaSense")

# Import lineage chain (graceful degradation)
try:
    from vibe_core.lineage import LineageChain, LineageEventType

    LINEAGE_AVAILABLE = True
except ImportError:
    LINEAGE_AVAILABLE = False
    logger.debug("LineageChain not available - KarmaSense will be limited")


@dataclass
class ChronicPain:
    """A file or component that has been repaired repeatedly."""

    path: str
    repair_count: int
    first_repair: str  # ISO timestamp
    last_repair: str  # ISO timestamp
    severity_history: List[str]  # List of severities from repairs
    varga_pattern: Optional[str]  # Most common varga disharmony
    recommended_action: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "repair_count": self.repair_count,
            "first_repair": self.first_repair,
            "last_repair": self.last_repair,
            "severity_history": self.severity_history,
            "varga_pattern": self.varga_pattern,
            "recommended_action": self.recommended_action,
        }


@dataclass
class ChronicPainReport:
    """Summary of chronic pain analysis."""

    total_repairs: int
    unique_paths: int
    hotspot_count: int  # Paths with >= threshold repairs
    hotspots: List[ChronicPain]
    time_window_days: int
    threshold: int
    health_score: float  # 0.0 (bad) to 1.0 (good)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_repairs": self.total_repairs,
            "unique_paths": self.unique_paths,
            "hotspot_count": self.hotspot_count,
            "hotspots": [h.to_dict() for h in self.hotspots],
            "time_window_days": self.time_window_days,
            "threshold": self.threshold,
            "health_score": self.health_score,
        }


@dataclass
class KarmaSummary:
    """Summary of karma/historical health."""

    total_events: int
    repair_events: int
    reflex_actions: int
    chronic_pain_count: int
    most_troubled_path: Optional[str]
    health_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_events": self.total_events,
            "repair_events": self.repair_events,
            "reflex_actions": self.reflex_actions,
            "chronic_pain_count": self.chronic_pain_count,
            "most_troubled_path": self.most_troubled_path,
            "health_score": self.health_score,
        }


class KarmaSense(BaseSense):
    """
    The Memory Sense - Historical Pattern Detection for MANAS.

    This cortex module analyzes the Parampara lineage chain to find
    chronic pain - files that keep breaking and getting repaired.

    "Those who cannot remember the past are condemned to repeat it."

    Usage:
        sense = KarmaSense(workspace=Path("."))
        report = sense.find_hotspots(threshold=3)
        for pain in report.hotspots:
            print(f"CHRONIC: {pain.path} repaired {pain.repair_count}x")
    """

    # OPUS-099: VEDA-4 auto-discovery
    name = "karma_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize KARMA SENSE.

        Args:
            workspace: Workspace root (default: cwd)
            config: Optional config dict from config/manas.yaml (karma_sense section)
        """
        super().__init__(workspace, config)
        self._lineage: Optional[LineageChain] = None
        self._cached_report: Optional[ChronicPainReport] = None
        self._cache_timestamp: Optional[datetime] = None

        logger.info("[KARMA_SENSE] Initialized - The Eye of Memory")

    def _get_lineage(self) -> Optional[LineageChain]:
        """Get or create lineage chain connection."""
        if not LINEAGE_AVAILABLE:
            return None

        if self._lineage is None:
            try:
                self._lineage = LineageChain()
            except Exception as e:
                logger.warning(f"[KARMA_SENSE] Could not connect to lineage: {e}")
                return None

        return self._lineage

    def find_hotspots(
        self,
        threshold: int = 3,
        days: int = 30,
        refresh: bool = False,
    ) -> ChronicPainReport:
        """
        Find files that have been repaired multiple times.

        This is the PRIMARY perception method - scans lineage chain
        for REPAIR_TASK_CREATED events and groups by path.

        Args:
            threshold: Minimum repairs to be considered a hotspot
            days: Time window to analyze (default: 30 days)
            refresh: Force re-scan (bypass cache)

        Returns:
            ChronicPainReport with hotspots and health metrics
        """
        # Check cache (valid for 1 hour)
        if (
            not refresh
            and self._cached_report is not None
            and self._cache_timestamp is not None
            and (datetime.utcnow() - self._cache_timestamp).seconds < 3600
        ):
            return self._cached_report

        lineage = self._get_lineage()
        if lineage is None:
            # No lineage available - return empty report
            return ChronicPainReport(
                total_repairs=0,
                unique_paths=0,
                hotspot_count=0,
                hotspots=[],
                time_window_days=days,
                threshold=threshold,
                health_score=1.0,
            )

        # Get all blocks from lineage
        all_blocks = lineage.get_all_blocks()

        # Filter for REPAIR_TASK_CREATED events in time window
        cutoff = datetime.utcnow() - timedelta(days=days)
        repair_events: List[Dict[str, Any]] = []

        for block in all_blocks:
            # Check event type
            if block.event_type != "REPAIR_TASK_CREATED":
                continue

            # Check time window
            try:
                block_time = datetime.fromisoformat(block.timestamp.replace("Z", "+00:00"))
                if block_time.replace(tzinfo=None) < cutoff:
                    continue
            except Exception:
                continue  # Skip malformed timestamps

            repair_events.append(
                {
                    "path": block.data.get("path", "unknown"),
                    "severity": block.data.get("severity", "unknown"),
                    "timestamp": block.timestamp,
                    "location_varga": block.data.get("location_varga"),
                    "content_varga": block.data.get("content_varga"),
                }
            )

        # Group by path
        path_repairs: Dict[str, List[Dict[str, Any]]] = {}
        for event in repair_events:
            path = event["path"]
            if path not in path_repairs:
                path_repairs[path] = []
            path_repairs[path].append(event)

        # Find hotspots (paths with >= threshold repairs)
        hotspots: List[ChronicPain] = []
        for path, repairs in path_repairs.items():
            if len(repairs) >= threshold:
                # Analyze pattern
                severities = [r["severity"] for r in repairs]
                varga_pairs = [f"{r.get('location_varga', '?')}->{r.get('content_varga', '?')}" for r in repairs]
                most_common_varga = Counter(varga_pairs).most_common(1)

                hotspots.append(
                    ChronicPain(
                        path=path,
                        repair_count=len(repairs),
                        first_repair=repairs[0]["timestamp"],
                        last_repair=repairs[-1]["timestamp"],
                        severity_history=severities,
                        varga_pattern=most_common_varga[0][0] if most_common_varga else None,
                        recommended_action=self._recommend_action(path, len(repairs), severities),
                    )
                )

        # Sort by repair count descending
        hotspots.sort(key=lambda h: h.repair_count, reverse=True)

        # Calculate health score
        # More hotspots = worse health
        # Score: 1.0 (no hotspots) to 0.0 (many hotspots)
        if len(path_repairs) == 0:
            health_score = 1.0
        else:
            hotspot_ratio = len(hotspots) / len(path_repairs)
            health_score = max(0.0, 1.0 - hotspot_ratio)

        report = ChronicPainReport(
            total_repairs=len(repair_events),
            unique_paths=len(path_repairs),
            hotspot_count=len(hotspots),
            hotspots=hotspots,
            time_window_days=days,
            threshold=threshold,
            health_score=health_score,
        )

        # Cache result
        self._cached_report = report
        self._cache_timestamp = datetime.utcnow()

        if hotspots:
            logger.warning(
                f"[KARMA_SENSE] Found {len(hotspots)} chronic pain hotspots "
                f"({report.total_repairs} repairs in {days} days)"
            )
        else:
            logger.info(f"[KARMA_SENSE] No chronic pain detected (health: {health_score:.0%})")

        return report

    def _recommend_action(self, path: str, repair_count: int, severities: List[str]) -> str:
        """Generate recommended action for a chronic pain hotspot."""
        critical_count = severities.count("critical")
        high_count = severities.count("high")

        if critical_count >= 2 or repair_count >= 5:
            return f"URGENT: Consider architectural refactor of {Path(path).name}"
        elif high_count >= 2 or repair_count >= 3:
            return f"Review placement and responsibilities of {Path(path).name}"
        else:
            return f"Monitor {Path(path).name} for continued issues"

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> KarmaSummary:
        """
        OPUS-099: BaseSense interface implementation.

        Wraps find_hotspots() for SenseLoader compatibility.
        """
        threshold = context.get("threshold", 3) if context else 3
        days = context.get("days", 30) if context else 30
        refresh = context.get("refresh", False) if context else False

        report = self.find_hotspots(threshold=threshold, days=days, refresh=refresh)

        # Also count total reflex actions
        reflex_count = 0
        lineage = self._get_lineage()
        if lineage:
            for block in lineage.get_all_blocks():
                if block.event_type == "REFLEX_ACTION":
                    reflex_count += 1

        return KarmaSummary(
            total_events=len(lineage.get_all_blocks()) if lineage else 0,
            repair_events=report.total_repairs,
            reflex_actions=reflex_count,
            chronic_pain_count=report.hotspot_count,
            most_troubled_path=report.hotspots[0].path if report.hotspots else None,
            health_score=report.health_score,
        )

    def get_status_for_chat(self) -> str:
        """Get human-readable status for chat interface."""
        report = self.find_hotspots()

        lines = [
            "KARMA SENSE - Historical Health",
            "=" * 40,
            "",
            f"Time Window: {report.time_window_days} days",
            f"Total Repairs: {report.total_repairs}",
            f"Unique Paths: {report.unique_paths}",
            f"Hotspot Threshold: {report.threshold}",
            "",
            f"Chronic Pain Hotspots: {report.hotspot_count}",
            f"Health Score: {report.health_score:.0%}",
        ]

        if report.hotspots:
            lines.extend(["", "Top Hotspots:"])
            for pain in report.hotspots[:5]:
                lines.append(f"  {pain.path}: {pain.repair_count}x repairs")
                lines.append(f"    → {pain.recommended_action}")

        return "\n".join(lines)

    def analyze_chronic_pain(self) -> ChronicPainReport:
        """
        Alias for find_hotspots() - used by VivekaSense.

        Returns:
            ChronicPainReport with historical pain points.
        """
        return self.find_hotspots()

    def get_boot_summary(self) -> Dict[str, Any]:
        """
        OPUS-172: Polymorphic boot summary for SenseManager.

        Returns standardized boot data for the SenseManager to use
        instead of hardcoded if/elif checks.
        """
        try:
            report = self.find_hotspots()
            if report:
                return {
                    "message": f"Hotspots: {report.hotspot_count}",
                    "data": {
                        "hotspots": report.hotspot_count,
                        "health": report.health_score,
                        "total_repairs": report.total_repairs,
                    },
                    "emoji": "🔮",
                }
        except Exception as e:
            logger.debug(f"[KARMA_SENSE] Boot summary failed: {e}")
        return {"message": "Initialized", "data": {}, "emoji": "🔮"}

    # =========================================================================
    # OPUS-167: Intent Generation (Fractal Architecture)
    # =========================================================================

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List["Intent"]:
        """
        Generate repair intents based on chronic pain perception.

        OPUS-167: Fractal Architecture Restoration

        This method generates intents for files that repeatedly break (chronic pain).
        These hotspots indicate structural weaknesses that need refactoring.

        Returns:
            List of repair/refactor intents for chronic pain hotspots
        """
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        intents: List[Intent] = []

        try:
            # Perceive chronic pain
            report = self.find_hotspots(
                threshold=context.get("threshold", 3) if context else 3,
                days=context.get("days", 30) if context else 30,
            )

            if report.hotspots:
                logger.info(f"[KARMA_SENSE] Found {len(report.hotspots)} chronic pain hotspots")

                for pain in report.hotspots[:3]:  # Top 3 hotspots
                    # Determine priority based on severity
                    if pain.repair_count >= 5:
                        priority = IntentPriority.CRITICAL
                        risk = IntentRisk.MEDIUM
                    elif pain.repair_count >= 3:
                        priority = IntentPriority.HIGH
                        risk = IntentRisk.LOW
                    else:
                        priority = IntentPriority.MEDIUM
                        risk = IntentRisk.SAFE

                    intent = Intent(
                        id=f"chronic_pain_{Path(pain.path).stem}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        intent_type="refactor_hotspot",
                        title=f"Chronic Pain: {Path(pain.path).name} ({pain.repair_count}x repairs)",
                        description=(
                            f"File {pain.path} has been repaired {pain.repair_count} times "
                            f"since {pain.first_repair}. "
                            f"Varga pattern: {pain.varga_pattern or 'Unknown'}. "
                            f"{pain.recommended_action}"
                        ),
                        reasoning=(
                            "KARMA SENSE detected chronic pain - repeated repairs indicate "
                            "structural weakness that needs architectural attention."
                        ),
                        priority=priority,
                        risk=risk,
                        params={
                            "path": pain.path,
                            "repair_count": pain.repair_count,
                            "varga_pattern": pain.varga_pattern,
                            "severity_history": pain.severity_history,
                        },
                        auto_executable=False,  # Refactoring needs human approval
                    )
                    intents.append(intent)

        except Exception as e:
            logger.warning(f"[KARMA_SENSE] Intent generation failed: {e}")

        return intents


# =============================================================================
# Singleton for Global Access
# =============================================================================

_karma_sense: Optional[KarmaSense] = None


def get_karma_sense(workspace: Optional[Path] = None) -> KarmaSense:
    """Get or create the global KarmaSense instance."""
    global _karma_sense
    if _karma_sense is None:
        _karma_sense = KarmaSense(workspace=workspace)
    return _karma_sense


# =============================================================================
# Availability Flag
# =============================================================================

KARMA_SENSE_AVAILABLE = True


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "KarmaSense",
    "KarmaSummary",
    "ChronicPain",
    "ChronicPainReport",
    "get_karma_sense",
    "KARMA_SENSE_AVAILABLE",
]

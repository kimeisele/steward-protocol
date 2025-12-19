"""
OPUS-132: Triage Analyzer - The Intelligent Prioritizer
=========================================================

Sanskrit: Viveka = Discrimination (used in VivekaSense)
         Prajna = Wisdom applied to action

This analyzer uses VivekaSense to perceive coverage gaps, then generates
PRIORITIZED intents based on the triage classification (P1→P5).

The key insight: Not all gaps are equal.
- 8 P1 gaps = 80% of the pain (Pareto principle)
- 305 P4/P5 gaps = background noise

MANAS should focus its energy where it matters most.

Integration:
    VivekaSense (perception) → TriageAnalyzer (action) → IntentRouter (execution)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
    required: true
    rationale: "The intelligent prioritizer for coverage gaps"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true
    rationale: "The 5th sense that perceives and discriminates"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "Churn data for priority scoring"

wiring:
  - pattern: "class TriageAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
  - pattern: "def analyze"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
  - pattern: "VivekaSense"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/triage_analyzer.py
-->
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.TriageAnalyzer")


class TriageAnalyzer(BaseAnalyzer):
    """
    Intelligent prioritization analyzer using VivekaSense.

    Unlike InverseScanAnalyzer which reports ALL gaps equally,
    TriageAnalyzer generates intents ONLY for P1/P2 gaps (action required).

    P3/P4/P5 gaps are logged but not surfaced as intents (no alert fatigue).

    Flow:
        1. VivekaSense.perceive() → discriminated gaps
        2. Filter to P1/P2 only
        3. Generate intents with appropriate priority
        4. IntentRouter handles execution
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        super().__init__(workspace, config)
        self._viveka = None

    @property
    def name(self) -> str:
        return "triage_analyzer"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Analyze using VivekaSense and generate prioritized intents.

        Only P1 (CRITICAL) and P2 (HIGH) gaps generate intents.
        P3-P5 are logged for awareness but don't create noise.
        """
        logger.info("TriageAnalyzer: Starting discriminated analysis...")

        # Get VivekaSense perception
        from ..cortex.viveka_sense import TriagePriority, VivekaSense

        viveka = VivekaSense(workspace=self._workspace)
        report = viveka.perceive(context)

        intents: List[Intent] = []

        # Generate P1 CRITICAL intents
        for gap in report.p1_critical[: self._config.max_intents_per_run]:
            intent = Intent(
                type="triage_p1_critical",
                title=f"[P1 CRITICAL] Document {gap.element_name}",
                description=(
                    f"Undocumented {gap.element_type} with high complexity "
                    f"and active churn. File: {gap.file_path}:{gap.line_number}\n"
                    f"Reason: {gap.reason}\n"
                    f"Priority Score: {gap.priority_score:.1f}"
                ),
                priority=IntentPriority.CRITICAL,
                risk=IntentRisk.MEDIUM,
                source=self.name,
                params={
                    "file_path": gap.file_path,
                    "element_name": gap.element_name,
                    "element_type": gap.element_type,
                    "line_number": gap.line_number,
                    "complexity": gap.complexity,
                    "churn_score": gap.churn_score,
                    "priority_score": gap.priority_score,
                    "action": "document",
                },
            )
            intents.append(intent)

        # Generate P2 HIGH intents (if room and no P1s)
        p2_limit = max(0, self._config.max_intents_per_run - len(intents))
        for gap in report.p2_high[:p2_limit]:
            intent = Intent(
                type="triage_p2_high",
                title=f"[P2 HIGH] Document {gap.element_name}",
                description=(
                    f"Important {gap.element_type} needs documentation. "
                    f"File: {gap.file_path}:{gap.line_number}\n"
                    f"Reason: {gap.reason}"
                ),
                priority=IntentPriority.HIGH,
                risk=IntentRisk.LOW,
                source=self.name,
                params={
                    "file_path": gap.file_path,
                    "element_name": gap.element_name,
                    "element_type": gap.element_type,
                    "line_number": gap.line_number,
                    "complexity": gap.complexity,
                    "priority_score": gap.priority_score,
                    "action": "document",
                },
            )
            intents.append(intent)

        # Generate summary intent if any gaps found
        if report.action_required > 0 and not intents:
            summary_intent = Intent(
                type="triage_summary",
                title=f"Coverage Triage: {report.action_required} items need attention",
                description=(
                    f"VivekaSense found {report.action_required} P1/P2 gaps.\n"
                    f"Health Grade: {report.health_grade}\n"
                    f"Recommendation: {report.recommendation}"
                ),
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk.LOW,
                source=self.name,
                params={
                    "p1_count": len(report.p1_critical),
                    "p2_count": len(report.p2_high),
                    "p3_count": len(report.p3_medium),
                    "total_gaps": (
                        len(report.p1_critical)
                        + len(report.p2_high)
                        + len(report.p3_medium)
                        + len(report.p4_low)
                        + len(report.p5_trivial)
                    ),
                    "health_grade": report.health_grade,
                },
            )
            intents.append(summary_intent)

        # Log summary
        logger.info(
            f"TriageAnalyzer complete: "
            f"P1={len(report.p1_critical)}, P2={len(report.p2_high)}, "
            f"Intents generated: {len(intents)}"
        )

        return intents

    def get_full_report(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get the full VivekaReport for dashboard display.

        Unlike analyze() which returns only actionable intents,
        this returns the complete triage breakdown for HUD display.
        """
        from ..cortex.viveka_sense import VivekaSense

        viveka = VivekaSense(workspace=self._workspace)
        report = viveka.perceive(context)
        return report.to_dict()

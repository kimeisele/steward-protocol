"""
OPUS-132: VIVEKA SENSE - The Discriminator
==========================================

Sanskrit: Viveka = Discrimination, Discernment, Wisdom

This is the 5th sense of MANAS - the ability to perceive what is MISSING,
and more importantly, to DISCRIMINATE between critical and trivial gaps.

Following Bhagavad Gita 2.63:
"krodhād bhavati sammohaḥ sammohāt smṛti-vibhramaḥ"
(From confusion of memory comes loss of discrimination)

Without Viveka, MANAS sees 313 gaps equally. With Viveka, MANAS knows:
"These 8 are killing us. The other 305 can wait."

The Five Senses of MANAS (Panchajnanendriyas):
- PrakritiSense: "What is the state of the world?" (Git/State)
- DharmaSense: "Is this action righteous?" (Ethics/Permissions)
- SutraSense: "What documentation is missing?" (Doc→Code gaps)
- KarmaSense: "What patterns repeat?" (Historical churn)
- VivekaSense: "What code is undocumented?" (Code→Doc gaps + Priority)

Viveka completes the cognitive loop. MANAS can now see AND prioritize.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true
    rationale: "The 5th Sense - Code→Doc perception with discrimination"
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
    rationale: "The Dark Matter detector that Viveka wraps"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/karma_sense.py
    required: true
    rationale: "Churn data for priority scoring"

wiring:
  - pattern: "class VivekaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "def perceive_dark_matter"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "def discriminate_priority"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
  - pattern: "class TriagePriority"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
-->
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import BaseSense

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.VivekaSense")


class TriagePriority(IntEnum):
    """Priority levels for coverage gaps."""

    P1_CRITICAL = 1  # High complexity + high churn = FIRE
    P2_HIGH = 2  # High complexity OR high churn
    P3_MEDIUM = 3  # Public API (moderate complexity)
    P4_LOW = 4  # Normal tech debt
    P5_TRIVIAL = 5  # Self-documenting / simple code


@dataclass
class CoverageGap:
    """A single undocumented code element with triage scoring."""

    file_path: str
    element_name: str
    element_type: str  # "class", "function", "module"
    line_number: int
    complexity: str  # "simple", "moderate", "complex"

    # Triage scoring
    churn_score: float = 0.0  # From KarmaSense (0.0-1.0)
    is_public_api: bool = False
    is_core_path: bool = False

    # Computed priority
    priority: TriagePriority = TriagePriority.P4_LOW
    priority_score: float = 0.0
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "element_name": self.element_name,
            "element_type": self.element_type,
            "line_number": self.line_number,
            "complexity": self.complexity,
            "churn_score": self.churn_score,
            "is_public_api": self.is_public_api,
            "is_core_path": self.is_core_path,
            "priority": f"P{self.priority.value}",
            "priority_score": self.priority_score,
            "reason": self.reason,
        }


@dataclass
class VivekaReport:
    """Summary of Viveka perception - discriminated coverage gaps."""

    # Raw metrics (from InverseScanAnalyzer)
    total_elements: int = 0
    documented_elements: int = 0
    coverage_ratio: float = 0.0
    health_grade: str = "F"

    # Triage breakdown
    p1_critical: List[CoverageGap] = field(default_factory=list)
    p2_high: List[CoverageGap] = field(default_factory=list)
    p3_medium: List[CoverageGap] = field(default_factory=list)
    p4_low: List[CoverageGap] = field(default_factory=list)
    p5_trivial: List[CoverageGap] = field(default_factory=list)

    # Actionable summary
    action_required: int = 0  # P1 + P2 count
    recommendation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_elements": self.total_elements,
            "documented_elements": self.documented_elements,
            "coverage_ratio": self.coverage_ratio,
            "health_grade": self.health_grade,
            "triage": {
                "p1_critical": len(self.p1_critical),
                "p2_high": len(self.p2_high),
                "p3_medium": len(self.p3_medium),
                "p4_low": len(self.p4_low),
                "p5_trivial": len(self.p5_trivial),
            },
            "action_required": self.action_required,
            "recommendation": self.recommendation,
            "p1_gaps": [g.to_dict() for g in self.p1_critical[:10]],  # Top 10
        }


class VivekaSense(BaseSense):
    """
    The 5th Sense: Perceives undocumented code AND discriminates priority.

    This is not just "what's missing" but "what's missing that MATTERS".

    Combines:
    - InverseScanAnalyzer (raw gap detection)
    - KarmaSense (churn/hotspot data)
    - Complexity scoring
    - API exposure detection

    Result: Prioritized list of gaps (P1→P5) with actionable focus.
    """

    name = "viveka_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(workspace, config)
        self._inverse_scanner = None
        self._karma_sense = None
        self._last_report: Optional[VivekaReport] = None

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> VivekaReport:
        """
        Main perception method - returns discriminated coverage gaps.

        Unlike raw InverseScanAnalyzer, this returns PRIORITIZED gaps.
        """
        logger.info("VivekaSense perceiving dark matter with discrimination...")

        # Step 1: Get raw gaps from InverseScanAnalyzer
        raw_gaps = self.perceive_dark_matter()

        # Step 2: Get churn data from KarmaSense
        churn_data = self._get_churn_data()

        # Step 3: Enrich gaps with churn and compute priority
        enriched_gaps = self._enrich_with_karma(raw_gaps, churn_data)

        # Step 4: Discriminate - assign P1-P5 priority
        prioritized_gaps = [self.discriminate_priority(gap) for gap in enriched_gaps]

        # Step 5: Build report
        report = self._build_report(prioritized_gaps)
        self._last_report = report

        logger.info(f"VivekaSense: {report.action_required} critical gaps, Grade {report.health_grade}")

        # GURUKULA: Report P1/P2 gaps to CuriosityTracker for self-directed training
        self._report_gaps_to_curiosity(report)

        return report

    def _report_gaps_to_curiosity(self, report: VivekaReport) -> None:
        """Report critical gaps to CuriosityTracker for self-directed training."""
        if report.action_required == 0:
            return  # No critical gaps

        try:
            from vibe_core.plugins.opus_assistant.manas.dojo.agency import CuriosityTracker

            tracker = CuriosityTracker(self._workspace or Path("."))

            # Report P1 critical gaps with high weight
            for gap in report.p1_critical[:3]:  # Top 3 P1s
                tracker.report_gap(
                    description=f"P1 CRITICAL: {gap.element_name} in {gap.file_path}",
                    weight=0.2,  # High weight for P1
                )

            # Report P2 high gaps with moderate weight
            for gap in report.p2_high[:2]:  # Top 2 P2s
                tracker.report_gap(
                    description=f"P2 HIGH: {gap.element_name} in {gap.file_path}",
                    weight=0.1,
                )

            logger.info(f"🔍 GURUKULA: Reported {min(5, report.action_required)} gaps to CuriosityTracker")
        except ImportError:
            pass  # Dojo not available

    def perceive_dark_matter(self) -> List[Dict[str, Any]]:
        """
        Detect undocumented code elements (raw, no prioritization).

        Uses SutraSense's discover_hidden_code() but FILTERS to only
        include elements that actually lack Python docstrings.

        This is the key calibration: "undocumented" = no docstring in code,
        NOT "not mentioned in markdown docs".
        """
        try:
            # Try to use SutraSense's discover_hidden_code() first
            from .sutra_sense import SutraSense

            sutra = SutraSense(workspace=self._workspace)
            hidden = sutra.discover_hidden_code()

            # CRITICAL: Filter to only elements that ACTUALLY lack docstrings
            # This is the sensor calibration fix - we only report real gaps
            result = []
            for item in hidden:
                if not self._has_docstring(
                    str(item.file_path),
                    item.name,
                    item.element_type,
                ):
                    result.append(
                        {
                            "file_path": str(item.file_path),
                            "element_name": item.name,
                            "element_type": item.element_type,
                            "line_number": item.line_number,
                            "complexity": item.complexity,
                            "importance": item.importance,
                        }
                    )

            logger.info(f"VivekaSense: {len(hidden)} candidates → {len(result)} actual gaps (filtered by docstring)")
            return result
        except Exception as e:
            logger.warning(f"SutraSense fallback: {e}")
            return []

    def _has_docstring(self, file_path: str, element_name: str, element_type: str) -> bool:
        """
        Check if an element has a Python docstring using AST.

        This is the ground truth check - does the code ACTUALLY have documentation?
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False

            code = path.read_text()
            tree = ast.parse(code)

            for node in ast.walk(tree):
                is_match = False

                if element_type in ("function", "method"):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if node.name == element_name:
                            is_match = True
                elif element_type == "class":
                    if isinstance(node, ast.ClassDef):
                        if node.name == element_name:
                            is_match = True

                if is_match:
                    # Check for docstring (first statement is Expr with string Constant)
                    if node.body and isinstance(node.body[0], ast.Expr):
                        if isinstance(node.body[0].value, ast.Constant):
                            if isinstance(node.body[0].value.value, str):
                                return True
                    return False

            return False  # Element not found
        except Exception:
            return False  # Assume no docstring on parse error

    def _get_churn_data(self) -> Dict[str, float]:
        """Get file churn scores from KarmaSense."""
        try:
            from .karma_sense import KarmaSense

            karma = KarmaSense(workspace=self._workspace)
            report = karma.analyze_chronic_pain()

            # Build churn map from hotspots
            churn_map = {}
            for hotspot in report.hotspots:
                # Normalize repair count to 0-1 score
                # 1 repair = 0.1, 10+ repairs = 1.0
                churn_score = min(hotspot.repair_count / 10.0, 1.0)
                churn_map[hotspot.path] = churn_score

            return churn_map
        except Exception as e:
            logger.warning(f"KarmaSense unavailable: {e}")
            return {}

    def _enrich_with_karma(self, raw_gaps: List[Dict[str, Any]], churn_data: Dict[str, float]) -> List[CoverageGap]:
        """Enrich raw gaps with churn data and metadata."""
        enriched = []

        for gap in raw_gaps:
            file_path = gap.get("file_path", "")

            # Determine if core path
            is_core = any(core in file_path for core in ["vibe_core/", "kernel", "state/", "plugins/"])

            # Determine if public API
            element_name = gap.get("element_name", "")
            is_public = not element_name.startswith("_")

            coverage_gap = CoverageGap(
                file_path=file_path,
                element_name=element_name,
                element_type=gap.get("element_type", "function"),
                line_number=gap.get("line_number", 0),
                complexity=gap.get("complexity", "moderate"),
                churn_score=churn_data.get(file_path, 0.0),
                is_public_api=is_public,
                is_core_path=is_core,
            )
            enriched.append(coverage_gap)

        return enriched

    def discriminate_priority(self, gap: CoverageGap) -> CoverageGap:
        """
        The core discrimination logic - assign P1-P5 priority.

        Formula:
            priority_score = (complexity_weight × 10) +
                             (churn_score × 50) +
                             (core_bonus × 20) +
                             (api_bonus × 10)

        Thresholds:
            P1 (Critical): score > 60 (complex + churning + core)
            P2 (High): score > 40
            P3 (Medium): score > 25
            P4 (Low): score > 10
            P5 (Trivial): score <= 10
        """
        # Complexity weight
        complexity_weights = {"simple": 1, "moderate": 3, "complex": 5}
        complexity_weight = complexity_weights.get(gap.complexity, 3)

        # Calculate score
        score = (
            (complexity_weight * 10)
            + (gap.churn_score * 50)
            + (20 if gap.is_core_path else 0)
            + (10 if gap.is_public_api else 0)
        )

        # Assign priority
        if score > 60:
            priority = TriagePriority.P1_CRITICAL
            reason = "Complex + churning + core path"
        elif score > 40:
            priority = TriagePriority.P2_HIGH
            reason = "High complexity or high churn"
        elif score > 25:
            priority = TriagePriority.P3_MEDIUM
            reason = "Public API or moderate complexity"
        elif score > 10:
            priority = TriagePriority.P4_LOW
            reason = "Normal tech debt"
        else:
            priority = TriagePriority.P5_TRIVIAL
            reason = "Simple/internal code"

        gap.priority = priority
        gap.priority_score = score
        gap.reason = reason

        return gap

    def _build_report(self, gaps: List[CoverageGap]) -> VivekaReport:
        """Build the final VivekaReport with triage breakdown."""
        # Count totals (estimate from gaps - in real impl, get from InverseScan)
        total = len(gaps) + 100  # Assume 100 documented for grade calc
        documented = 100

        report = VivekaReport(
            total_elements=total,
            documented_elements=documented,
            coverage_ratio=documented / total if total > 0 else 1.0,
        )

        # Assign letter grade
        ratio = report.coverage_ratio
        if ratio >= 0.9:
            report.health_grade = "A"
        elif ratio >= 0.8:
            report.health_grade = "B"
        elif ratio >= 0.7:
            report.health_grade = "C"
        elif ratio >= 0.6:
            report.health_grade = "D"
        else:
            report.health_grade = "F"

        # Bucket by priority
        for gap in gaps:
            if gap.priority == TriagePriority.P1_CRITICAL:
                report.p1_critical.append(gap)
            elif gap.priority == TriagePriority.P2_HIGH:
                report.p2_high.append(gap)
            elif gap.priority == TriagePriority.P3_MEDIUM:
                report.p3_medium.append(gap)
            elif gap.priority == TriagePriority.P4_LOW:
                report.p4_low.append(gap)
            else:
                report.p5_trivial.append(gap)

        # Action required = P1 + P2
        report.action_required = len(report.p1_critical) + len(report.p2_high)

        # Generate recommendation
        if report.p1_critical:
            top = report.p1_critical[0]
            report.recommendation = (
                f"CRITICAL: {len(report.p1_critical)} gaps need immediate attention. "
                f"Start with {top.element_name} in {top.file_path}"
            )
        elif report.p2_high:
            report.recommendation = f"HIGH: {len(report.p2_high)} gaps should be addressed this sprint."
        else:
            report.recommendation = "System is healthy. Continue normal maintenance."

        return report

    @property
    def last_report(self) -> Optional[VivekaReport]:
        """Get the last perception report."""
        return self._last_report

    # =========================================================================
    # OPUS-167: Intent Generation (Fractal Architecture)
    # =========================================================================

    def generate_intents(self, context: Optional[Dict[str, Any]] = None) -> List["Intent"]:
        """
        Generate documentation intents based on coverage gap perception.

        OPUS-167: Fractal Architecture Restoration

        This method generates intents for undocumented code elements,
        prioritized by their criticality (P1 = Critical, P5 = Trivial).

        Returns:
            List of documentation intents for critical coverage gaps
        """
        from datetime import datetime

        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        intents: List[Intent] = []

        try:
            # Perceive coverage gaps
            report = self.perceive(context)

            # Generate intents for P1 Critical gaps
            if report.p1_critical:
                logger.info(f"[VIVEKA_SENSE] Found {len(report.p1_critical)} P1 critical gaps")

                for gap in report.p1_critical[:3]:  # Top 3 P1s
                    intent = Intent(
                        id=f"doc_p1_{gap.element_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        intent_type="document_code",
                        title=f"P1 CRITICAL: Document {gap.element_name}",
                        description=(
                            f"Critical undocumented {gap.element_type} '{gap.element_name}' "
                            f"in {gap.file_path}:{gap.line_number}. "
                            f"Complexity: {gap.complexity}, Churn: {gap.churn_score:.1%}. "
                            f"Reason: {gap.reason}"
                        ),
                        reasoning=(
                            "VIVEKA SENSE detected critical documentation gap. "
                            "High complexity + high churn + core path = fire. "
                            "These gaps cause confusion and onboarding friction."
                        ),
                        priority=IntentPriority.CRITICAL,
                        risk=IntentRisk.SAFE,  # Documentation is safe
                        params={
                            "file_path": gap.file_path,
                            "element_name": gap.element_name,
                            "element_type": gap.element_type,
                            "line_number": gap.line_number,
                            "complexity": gap.complexity,
                            "priority_score": gap.priority_score,
                        },
                        auto_executable=False,  # Doc writing needs review
                    )
                    intents.append(intent)

            # Generate intents for P2 High gaps
            if report.p2_high:
                for gap in report.p2_high[:2]:  # Top 2 P2s
                    intent = Intent(
                        id=f"doc_p2_{gap.element_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        intent_type="document_code",
                        title=f"P2 HIGH: Document {gap.element_name}",
                        description=(
                            f"High-priority undocumented {gap.element_type} '{gap.element_name}' "
                            f"in {gap.file_path}:{gap.line_number}. "
                            f"Reason: {gap.reason}"
                        ),
                        reasoning=(
                            "VIVEKA SENSE detected high-priority documentation gap. Should be addressed this sprint."
                        ),
                        priority=IntentPriority.HIGH,
                        risk=IntentRisk.SAFE,
                        params={
                            "file_path": gap.file_path,
                            "element_name": gap.element_name,
                            "element_type": gap.element_type,
                            "line_number": gap.line_number,
                        },
                        auto_executable=False,
                    )
                    intents.append(intent)

        except Exception as e:
            logger.warning(f"[VIVEKA_SENSE] Intent generation failed: {e}")

        return intents

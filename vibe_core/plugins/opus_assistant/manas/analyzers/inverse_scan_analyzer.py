"""
OPUS-129: Inverse Scan Analyzer - The 51% Detector
====================================================

Sanskrit: Viveka = Discrimination, Discernment

This analyzer performs the INVERSE of normal documentation checking:
Instead of Doc → Code (are references valid?), it does Code → Doc (is code documented?).

The 51% Principle:
- Traditional analyzers (50%) fix what's broken
- Genesis analyzers (51%) create what's missing
- Inverse Scan (51%) asks: "What Dark Matter exists in our codebase?"

Dark Matter = Code that exists, works, but isn't in the documentation.
This is the breeding ground for tech debt, spaghetti, and "nobody knows how this works".

MANAS uses this to proactively identify documentation gaps before they become crises.

Philosophy:
- Code without documentation is "invisible" to the team
- Complex undocumented code is HIGH RISK
- Documentation coverage is as important as test coverage

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
    required: true
    rationale: "The Inverse Scan - Code to Doc coverage analysis"
  - path: docs/architecture/OPUS/129-INVERSE-SCAN.md
    required: true
    rationale: "Master doc for inverse scanning"

wiring:
  - pattern: "class InverseScanAnalyzer"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "class CodeCoverageMetrics"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
  - pattern: "def calculate_coverage"
    in: vibe_core/plugins/opus_assistant/manas/analyzers/inverse_scan_analyzer.py
-->
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..intent_generator import Intent, IntentPriority, IntentRisk
from .base import AnalyzerConfig, BaseAnalyzer

logger = logging.getLogger("MANAS.InverseScanAnalyzer")

# Complexity weights for coverage scoring
COMPLEXITY_WEIGHTS = {
    "simple": 1,
    "moderate": 3,
    "complex": 5,
}

# Importance weights for intent priority
IMPORTANCE_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
}


@dataclass
class CodeCoverageMetrics:
    """Aggregated code coverage metrics from inverse scan."""

    # Raw counts
    total_elements: int = 0
    documented_elements: int = 0
    undocumented_elements: int = 0

    # By type
    classes_total: int = 0
    classes_documented: int = 0
    functions_total: int = 0
    functions_documented: int = 0

    # Complexity-weighted coverage
    total_complexity_points: int = 0
    documented_complexity_points: int = 0

    # Per-module breakdown
    module_coverage: Dict[str, float] = field(default_factory=dict)
    module_undocumented: Dict[str, List[str]] = field(default_factory=dict)

    # By complexity
    undocumented_by_complexity: Dict[str, int] = field(default_factory=dict)

    # By importance (the "hot" ones)
    critical_gaps: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def coverage_ratio(self) -> float:
        """Simple coverage ratio 0.0 - 1.0."""
        if self.total_elements == 0:
            return 1.0
        return self.documented_elements / self.total_elements

    @property
    def weighted_coverage_ratio(self) -> float:
        """Complexity-weighted coverage ratio 0.0 - 1.0."""
        if self.total_complexity_points == 0:
            return 1.0
        return self.documented_complexity_points / self.total_complexity_points

    @property
    def health_grade(self) -> str:
        """Letter grade for coverage health."""
        ratio = self.weighted_coverage_ratio
        if ratio >= 0.9:
            return "A"
        elif ratio >= 0.8:
            return "B"
        elif ratio >= 0.7:
            return "C"
        elif ratio >= 0.6:
            return "D"
        else:
            return "F"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_elements": self.total_elements,
            "documented_elements": self.documented_elements,
            "undocumented_elements": self.undocumented_elements,
            "coverage_ratio": round(self.coverage_ratio, 3),
            "weighted_coverage_ratio": round(self.weighted_coverage_ratio, 3),
            "health_grade": self.health_grade,
            "classes": {
                "total": self.classes_total,
                "documented": self.classes_documented,
            },
            "functions": {
                "total": self.functions_total,
                "documented": self.functions_documented,
            },
            "undocumented_by_complexity": self.undocumented_by_complexity,
            "critical_gaps_count": len(self.critical_gaps),
            "modules_below_50": [m for m, c in self.module_coverage.items() if c < 0.5],
        }


@dataclass
class CoverageGap:
    """A specific gap in code coverage - undocumented element."""

    element_type: str  # "class", "function", "module"
    name: str
    file_path: str
    line_number: int
    complexity: str
    importance: str
    module: str  # Parent module (e.g., "manas.cortex")
    has_docstring: bool
    priority_score: int  # Calculated from complexity × importance

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element_type": self.element_type,
            "name": self.name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "complexity": self.complexity,
            "importance": self.importance,
            "module": self.module,
            "has_docstring": self.has_docstring,
            "priority_score": self.priority_score,
        }


class InverseScanAnalyzer(BaseAnalyzer):
    """
    OPUS-129: The Inverse Scan Analyzer.

    Performs Code → Doc coverage analysis to find "Dark Matter" -
    code that exists but isn't documented.

    Uses SutraSense's discover_hidden_code() as the underlying scanner,
    then aggregates into coverage metrics and generates intents.

    The 51% Philosophy:
    - Don't just fix broken docs (50%)
    - Create documentation for the undocumented (51%)
    - Prioritize by complexity (complex undocumented code = HIGH RISK)
    """

    # VEDA-4 auto-discovery name
    name = "inverse_scan_analyzer"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[AnalyzerConfig] = None,
    ):
        super().__init__(workspace=workspace, config=config)
        self._intent_counter = 0
        self._metrics: Optional[CodeCoverageMetrics] = None
        self._gaps: List[CoverageGap] = []

        logger.info("[INVERSE_SCAN] Initialized - The Dark Matter Detector")

    def _next_id(self) -> str:
        self._intent_counter += 1
        return f"inverse_{self._intent_counter:04d}"

    def analyze(self, context: Dict[str, Any]) -> List[Intent]:
        """
        Perform inverse scan and generate coverage gap intents.

        Returns intents for:
        - Critical undocumented code (high complexity + no docs)
        - Module coverage warnings (module < 50% documented)
        - Trend alerts (if coverage is dropping)
        """
        intents: List[Intent] = []

        # Calculate coverage metrics
        self._metrics = self.calculate_coverage()

        if self._metrics.total_elements == 0:
            logger.info("[INVERSE_SCAN] No code elements found to analyze")
            return []

        # Log summary
        logger.info(
            f"[INVERSE_SCAN] Coverage: {self._metrics.coverage_ratio:.0%} "
            f"(weighted: {self._metrics.weighted_coverage_ratio:.0%}, "
            f"grade: {self._metrics.health_grade})"
        )

        # Generate intents for critical gaps
        intents.extend(self._generate_critical_gap_intents())

        # Generate intents for modules with poor coverage
        intents.extend(self._generate_module_coverage_intents())

        # Generate overall coverage intent if grade is failing
        if self._metrics.health_grade in ("D", "F"):
            intents.append(self._generate_overall_coverage_intent())

        # Respect max intents
        return intents[: self._config.max_intents_per_run]

    def calculate_coverage(self, refresh: bool = False) -> CodeCoverageMetrics:
        """
        Calculate code coverage metrics by scanning for hidden code.

        Uses SutraSense's discover_hidden_code() to find undocumented elements,
        then aggregates into metrics.
        """
        if self._metrics and not refresh:
            return self._metrics

        metrics = CodeCoverageMetrics()
        self._gaps = []

        # Get hidden code from SutraSense
        try:
            from ..cortex.sutra_sense import SutraSense

            sutra = SutraSense(workspace=self._workspace)
            hidden_code = sutra.discover_hidden_code()

            # Also get documented elements count
            summary = sutra.perceive_gaps()
            # Estimate documented elements from harness checks
            documented_count = self._estimate_documented_count(sutra)

        except Exception as e:
            logger.warning(f"[INVERSE_SCAN] Failed to get SutraSense data: {e}")
            return metrics

        # Process hidden code into gaps
        module_elements: Dict[str, List[CoverageGap]] = defaultdict(list)
        complexity_counts: Dict[str, int] = Counter()

        for hidden in hidden_code:
            # Calculate priority score
            complexity_weight = COMPLEXITY_WEIGHTS.get(hidden.complexity, 1)
            importance_weight = IMPORTANCE_WEIGHTS.get(hidden.importance, 1)
            priority_score = complexity_weight * importance_weight

            # Determine module from file path
            module = self._path_to_module(hidden.file_path)

            gap = CoverageGap(
                element_type=hidden.element_type,
                name=hidden.name,
                file_path=str(hidden.file_path),
                line_number=hidden.line_number,
                complexity=hidden.complexity,
                importance=hidden.importance,
                module=module,
                has_docstring=hidden.docstring is not None,
                priority_score=priority_score,
            )

            self._gaps.append(gap)
            module_elements[module].append(gap)
            complexity_counts[hidden.complexity] += 1

            # Track by type
            if hidden.element_type == "class":
                metrics.classes_total += 1
            else:
                metrics.functions_total += 1

            # Add to complexity points (undocumented)
            metrics.total_complexity_points += complexity_weight

            # Track critical gaps (high importance + complex)
            if hidden.importance == "high" or hidden.complexity == "complex":
                metrics.critical_gaps.append(gap.to_dict())

        # Calculate totals
        metrics.undocumented_elements = len(hidden_code)
        metrics.documented_elements = documented_count
        metrics.total_elements = metrics.documented_elements + metrics.undocumented_elements

        # Estimate documented complexity points
        # (Assume documented code has average complexity of "moderate")
        metrics.documented_complexity_points = documented_count * COMPLEXITY_WEIGHTS["moderate"]
        metrics.total_complexity_points += metrics.documented_complexity_points

        # Calculate per-module coverage
        for module, gaps in module_elements.items():
            undoc_count = len(gaps)
            # Estimate documented in module (rough heuristic)
            total_in_module = undoc_count + max(1, undoc_count // 3)  # Assume 25% documented
            coverage = 1.0 - (undoc_count / total_in_module)
            metrics.module_coverage[module] = coverage
            metrics.module_undocumented[module] = [g.name for g in gaps]

        # Set complexity breakdown
        metrics.undocumented_by_complexity = dict(complexity_counts)

        # Set type breakdown for documented (estimate)
        metrics.classes_documented = documented_count // 3
        metrics.functions_documented = documented_count - metrics.classes_documented

        self._metrics = metrics
        return metrics

    def _estimate_documented_count(self, sutra: Any) -> int:
        """Estimate number of documented code elements from SutraSense."""
        try:
            # Count unique patterns in all harnesses
            documented = set()
            for check in sutra._harness_checks.values():
                for pattern in check.wiring_patterns:
                    documented.add(pattern)
                for file_path in check.files_declared:
                    documented.add(Path(file_path).stem)
            return len(documented)
        except Exception:
            return 0

    def _path_to_module(self, file_path: Path) -> str:
        """Convert file path to module name."""
        try:
            rel_path = file_path.relative_to(self._workspace)
            parts = list(rel_path.parts)
            # Remove vibe_core prefix and file extension
            if parts and parts[0] == "vibe_core":
                parts = parts[1:]
            if parts:
                parts[-1] = parts[-1].replace(".py", "")
            return ".".join(parts[:3])  # Max 3 levels
        except Exception:
            return str(file_path.parent.name)

    def _generate_critical_gap_intents(self) -> List[Intent]:
        """Generate intents for critical undocumented code."""
        intents = []

        # Sort gaps by priority score (descending)
        critical_gaps = sorted(self._gaps, key=lambda g: g.priority_score, reverse=True)

        # Top 5 most critical
        for gap in critical_gaps[:5]:
            if gap.priority_score >= 6:  # complex + high importance = 15, moderate + medium = 6
                intents.append(
                    Intent(
                        id=self._next_id(),
                        intent_type="coverage_gap_critical",
                        title=f"Document {gap.element_type}: {gap.name}",
                        description=(
                            f"Undocumented {gap.complexity} {gap.element_type} in {gap.module}. "
                            f"Priority score: {gap.priority_score}/15. "
                            f"File: {gap.file_path}:{gap.line_number}"
                        ),
                        reasoning=(
                            "High-complexity undocumented code is tech debt. "
                            "Without documentation, this code becomes 'dark matter' - "
                            "it works but nobody knows why or how."
                        ),
                        priority=IntentPriority.HIGH,
                        risk=IntentRisk.SAFE,  # Documentation is always safe
                        auto_executable=False,  # Docs need human judgment
                        params={
                            "element_type": gap.element_type,
                            "name": gap.name,
                            "file_path": gap.file_path,
                            "line_number": gap.line_number,
                            "complexity": gap.complexity,
                            "importance": gap.importance,
                            "module": gap.module,
                            "action": "document_code",
                        },
                        related_files=[gap.file_path],
                    )
                )

        return intents

    def _generate_module_coverage_intents(self) -> List[Intent]:
        """Generate intents for modules with poor coverage."""
        intents = []

        for module, coverage in self._metrics.module_coverage.items():
            if coverage < 0.5:  # Less than 50% documented
                undoc_list = self._metrics.module_undocumented.get(module, [])
                intents.append(
                    Intent(
                        id=self._next_id(),
                        intent_type="coverage_gap_module",
                        title=f"Module {module}: {coverage:.0%} documented",
                        description=(
                            f"Module has {len(undoc_list)} undocumented elements. Examples: {', '.join(undoc_list[:3])}"
                        ),
                        reasoning=(
                            "Low module coverage creates knowledge silos. "
                            "New team members cannot understand this module without reading all the code."
                        ),
                        priority=IntentPriority.MEDIUM,
                        risk=IntentRisk.SAFE,
                        auto_executable=False,
                        params={
                            "module": module,
                            "coverage": coverage,
                            "undocumented_elements": undoc_list[:10],
                            "action": "document_module",
                        },
                    )
                )

        return intents

    def _generate_overall_coverage_intent(self) -> Intent:
        """Generate intent for overall poor coverage."""
        return Intent(
            id=self._next_id(),
            intent_type="coverage_gap_overall",
            title=f"Overall Coverage Grade: {self._metrics.health_grade}",
            description=(
                f"Code coverage is {self._metrics.weighted_coverage_ratio:.0%} (weighted). "
                f"{self._metrics.undocumented_elements} elements undocumented. "
                f"Critical gaps: {len(self._metrics.critical_gaps)}"
            ),
            reasoning=(
                "Below 70% documentation coverage is a risk factor. "
                "This affects onboarding, debugging, and maintenance. "
                "Consider a documentation sprint to address critical gaps."
            ),
            priority=IntentPriority.HIGH,
            risk=IntentRisk.SAFE,
            auto_executable=False,
            params={
                "grade": self._metrics.health_grade,
                "coverage_ratio": self._metrics.coverage_ratio,
                "weighted_coverage_ratio": self._metrics.weighted_coverage_ratio,
                "undocumented_count": self._metrics.undocumented_elements,
                "critical_gaps_count": len(self._metrics.critical_gaps),
                "action": "coverage_sprint",
            },
        )

    def get_coverage_report(self) -> Dict[str, Any]:
        """
        Generate a full coverage report.

        Useful for dashboard/COGNITION.md display.
        """
        if not self._metrics:
            self.calculate_coverage()

        return {
            "metrics": self._metrics.to_dict() if self._metrics else {},
            "gaps": [g.to_dict() for g in self._gaps[:20]],  # Top 20 gaps
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate human-readable recommendations."""
        if not self._metrics:
            return []

        recs = []

        if self._metrics.health_grade in ("D", "F"):
            recs.append("🚨 URGENT: Documentation coverage is critically low. Schedule a doc sprint.")

        if self._metrics.undocumented_by_complexity.get("complex", 0) > 5:
            recs.append(
                f"⚠️ {self._metrics.undocumented_by_complexity['complex']} complex elements "
                "are undocumented. Prioritize these - they're hardest to understand."
            )

        low_coverage_modules = [m for m, c in self._metrics.module_coverage.items() if c < 0.5]
        if low_coverage_modules:
            recs.append(f"📦 Modules with < 50% coverage: {', '.join(low_coverage_modules[:3])}")

        if len(self._metrics.critical_gaps) > 10:
            recs.append(
                f"🎯 {len(self._metrics.critical_gaps)} critical gaps. "
                "Focus on high-importance, high-complexity elements first."
            )

        if not recs:
            recs.append("✅ Documentation coverage is healthy. Keep it up!")

        return recs


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "InverseScanAnalyzer",
    "CodeCoverageMetrics",
    "CoverageGap",
]

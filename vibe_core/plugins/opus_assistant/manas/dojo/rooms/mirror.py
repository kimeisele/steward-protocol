"""
Mirror - Self-Inspection Room

OPUS-133: "Der Spiegel, wo MANAS sich selbst erkennt."

The Mirror is where MANAS inspects itself, finds gaps in knowledge,
and identifies areas for improvement. This is the foundation for
self-directed learning - you can't improve what you can't see.

Capabilities:
    inspect_synapses    - Analyze current synaptic weights
    find_gaps           - Identify missing or weak patterns
    compare_baseline    - Compare current state to baseline
    generate_curriculum - Create custom training for gaps

"Erkenne dich selbst." - Know thyself.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
    required: true
wiring:
  - pattern: "class Mirror"
    in: vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py
  - pattern: "find_gaps"
    in: vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py
-->
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..synaptic_seeder import BASELINE_BAD_PATTERNS, BASELINE_GOOD_PATTERNS

logger = logging.getLogger("DOJO.MIRROR")


@dataclass
class GapAnalysis:
    """Analysis of a knowledge gap."""

    pattern: str
    gap_type: str  # missing, weak, divergent, novel
    current_weight: Optional[float]
    baseline_weight: Optional[float]
    severity: float  # 0.0 - 1.0, higher = more urgent
    recommendation: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SelfInspection:
    """Result of MANAS self-inspection."""

    timestamp: str
    total_synapses: int
    total_triggers: int
    gaps_found: int
    gaps: List[GapAnalysis]
    health_score: float  # 0.0 - 1.0
    summary: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_synapses": self.total_synapses,
            "total_triggers": self.total_triggers,
            "gaps_found": self.gaps_found,
            "health_score": self.health_score,
            "summary": self.summary,
            "gaps": [
                {
                    "pattern": g.pattern,
                    "type": g.gap_type,
                    "severity": g.severity,
                    "recommendation": g.recommendation,
                }
                for g in self.gaps
            ],
        }


class Mirror:
    """
    The Mirror - Self-inspection room for MANAS.

    Usage:
        mirror = Mirror(workspace)

        # Full self-inspection
        result = mirror.inspect()

        # Find specific gaps
        gaps = mirror.find_gaps()

        # Generate training curriculum for gaps
        curriculum = mirror.generate_gap_curriculum()

        # Compare to baseline
        divergence = mirror.compare_baseline()
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._synapses_path = workspace / ".opus_state" / "synapses.json"
        self._inspection_history_path = workspace / ".opus_state" / "mirror" / "history.json"

        # Initialize storage
        self._inspection_history_path.parent.mkdir(parents=True, exist_ok=True)

    def inspect(self) -> SelfInspection:
        """
        Perform full self-inspection of MANAS's synaptic state.

        Returns:
            SelfInspection with gaps and health score
        """
        logger.info("🪞 MIRROR: Beginning self-inspection...")

        synapses = self._load_synapses()
        gaps = self._analyze_all_gaps(synapses)

        # Calculate health score
        health_score = self._calculate_health(synapses, gaps)

        # Generate summary
        summary = self._generate_summary(synapses, gaps, health_score)

        inspection = SelfInspection(
            timestamp=datetime.now().isoformat(),
            total_synapses=len(synapses.get("weights", {})),
            total_triggers=len(synapses.get("triggers", [])),
            gaps_found=len(gaps),
            gaps=gaps,
            health_score=health_score,
            summary=summary,
        )

        # Save to history
        self._save_inspection(inspection)

        logger.info(f"🪞 MIRROR: Inspection complete - health={health_score:.2f}, gaps={len(gaps)}")
        return inspection

    def find_gaps(self, severity_threshold: float = 0.3) -> List[GapAnalysis]:
        """
        Find knowledge gaps above a severity threshold.

        Args:
            severity_threshold: Only return gaps with severity >= threshold

        Returns:
            List of GapAnalysis objects
        """
        synapses = self._load_synapses()
        all_gaps = self._analyze_all_gaps(synapses)

        return [g for g in all_gaps if g.severity >= severity_threshold]

    def compare_baseline(self) -> Dict[str, Any]:
        """
        Compare current synaptic state to baseline patterns.

        Returns:
            Dict with divergence analysis
        """
        synapses = self._load_synapses()
        weights = synapses.get("weights", {})

        divergences = {
            "good_patterns": [],
            "bad_patterns": [],
            "novel_patterns": [],
        }

        # Check good patterns
        for trigger, actions in BASELINE_GOOD_PATTERNS.items():
            for action, baseline_weight in actions.items():
                current = weights.get(trigger, {}).get(action)
                if current is None:
                    divergences["good_patterns"].append(
                        {
                            "pattern": f"{trigger} → {action}",
                            "status": "missing",
                            "baseline": baseline_weight,
                        }
                    )
                elif abs(current - baseline_weight) > 0.2:
                    divergences["good_patterns"].append(
                        {
                            "pattern": f"{trigger} → {action}",
                            "status": "divergent",
                            "baseline": baseline_weight,
                            "current": current,
                            "delta": current - baseline_weight,
                        }
                    )

        # Check bad patterns
        for trigger, actions in BASELINE_BAD_PATTERNS.items():
            for action, baseline_weight in actions.items():
                current = weights.get(trigger, {}).get(action)
                if current is None:
                    divergences["bad_patterns"].append(
                        {
                            "pattern": f"{trigger} → {action}",
                            "status": "missing",
                            "baseline": baseline_weight,
                        }
                    )
                elif current > baseline_weight + 0.2:
                    # Bad pattern got stronger - concerning!
                    divergences["bad_patterns"].append(
                        {
                            "pattern": f"{trigger} → {action}",
                            "status": "strengthened",
                            "baseline": baseline_weight,
                            "current": current,
                            "delta": current - baseline_weight,
                            "warning": True,
                        }
                    )

        # Find novel patterns (not in baseline)
        baseline_triggers = set(BASELINE_GOOD_PATTERNS.keys()) | set(BASELINE_BAD_PATTERNS.keys())
        for trigger in weights:
            if trigger not in baseline_triggers:
                divergences["novel_patterns"].append(
                    {
                        "trigger": trigger,
                        "actions": list(weights[trigger].keys()),
                        "status": "novel",
                    }
                )

        return divergences

    def generate_gap_curriculum(self, max_scenarios: int = 10) -> Dict[str, Any]:
        """
        Generate a custom curriculum targeting identified gaps.

        Returns:
            YAML-compatible curriculum dict
        """
        gaps = self.find_gaps(severity_threshold=0.4)

        if not gaps:
            logger.info("🪞 MIRROR: No significant gaps found")
            return {"curriculum": {"id": "no_gaps", "scenarios": []}}

        scenarios = []
        for gap in gaps[:max_scenarios]:
            scenario = self._gap_to_scenario(gap)
            if scenario:
                scenarios.append(scenario)

        curriculum = {
            "curriculum": {
                "id": f"gap_training_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "name": "Gap Training (MANAS-generated)",
                "description": f"Custom curriculum targeting {len(scenarios)} identified gaps",
                "difficulty": 3,
                "tags": ["gap_training", "self_directed", "manas_generated"],
            },
            "scenarios": scenarios,
        }

        logger.info(f"🪞 MIRROR: Generated gap curriculum with {len(scenarios)} scenarios")
        return curriculum

    def _analyze_all_gaps(self, synapses: Dict[str, Any]) -> List[GapAnalysis]:
        """Analyze all types of gaps."""
        gaps = []
        weights = synapses.get("weights", {})

        # Check for missing baseline patterns
        gaps.extend(self._find_missing_patterns(weights))

        # Check for weak patterns (learned but low weight)
        gaps.extend(self._find_weak_patterns(weights))

        # Check for divergent patterns (drifted from baseline)
        gaps.extend(self._find_divergent_patterns(weights))

        # Sort by severity
        gaps.sort(key=lambda g: g.severity, reverse=True)

        return gaps

    def _find_missing_patterns(self, weights: Dict[str, Any]) -> List[GapAnalysis]:
        """Find patterns that should exist but don't."""
        gaps = []

        for trigger, actions in BASELINE_GOOD_PATTERNS.items():
            if trigger not in weights:
                gaps.append(
                    GapAnalysis(
                        pattern=trigger,
                        gap_type="missing",
                        current_weight=None,
                        baseline_weight=max(actions.values()),
                        severity=0.6,
                        recommendation=f"Add baseline pattern: {trigger}",
                    )
                )

        return gaps

    def _find_weak_patterns(self, weights: Dict[str, Any]) -> List[GapAnalysis]:
        """Find patterns that are too weak."""
        gaps = []

        for trigger, actions in weights.items():
            for action, weight in actions.items():
                # Check if this is a good pattern that's too weak
                baseline = BASELINE_GOOD_PATTERNS.get(trigger, {}).get(action)
                if baseline and weight < baseline - 0.2:
                    gaps.append(
                        GapAnalysis(
                            pattern=f"{trigger} → {action}",
                            gap_type="weak",
                            current_weight=weight,
                            baseline_weight=baseline,
                            severity=0.4,
                            recommendation="Strengthen pattern through training",
                        )
                    )

        return gaps

    def _find_divergent_patterns(self, weights: Dict[str, Any]) -> List[GapAnalysis]:
        """Find patterns that have diverged significantly from baseline."""
        gaps = []

        for trigger, actions in weights.items():
            for action, weight in actions.items():
                # Check for bad patterns that got stronger
                bad_baseline = BASELINE_BAD_PATTERNS.get(trigger, {}).get(action)
                if bad_baseline and weight > bad_baseline + 0.3:
                    gaps.append(
                        GapAnalysis(
                            pattern=f"{trigger} → {action}",
                            gap_type="divergent",
                            current_weight=weight,
                            baseline_weight=bad_baseline,
                            severity=0.8,  # High severity - attack pattern strengthened!
                            recommendation="ALERT: Attack pattern has strengthened. Reset or retrain.",
                            metadata={"warning": True},
                        )
                    )

        return gaps

    def _calculate_health(self, synapses: Dict[str, Any], gaps: List[GapAnalysis]) -> float:
        """Calculate overall synaptic health score."""
        if not synapses.get("weights"):
            return 0.5  # Default for empty state

        # Start at 1.0 and reduce based on gaps
        health = 1.0

        for gap in gaps:
            if gap.gap_type == "divergent":
                health -= 0.1  # Divergence is serious
            elif gap.gap_type == "missing":
                health -= 0.05  # Missing is moderate
            elif gap.gap_type == "weak":
                health -= 0.02  # Weak is minor

        return max(0.0, min(1.0, health))

    def _generate_summary(self, synapses: Dict[str, Any], gaps: List[GapAnalysis], health: float) -> str:
        """Generate human-readable summary."""
        weight_count = sum(len(actions) for actions in synapses.get("weights", {}).values())
        trigger_count = len(synapses.get("triggers", []))

        if health >= 0.9:
            status = "Excellent synaptic health"
        elif health >= 0.7:
            status = "Good synaptic health"
        elif health >= 0.5:
            status = "Moderate synaptic health - training recommended"
        else:
            status = "Poor synaptic health - immediate training needed"

        critical_gaps = len([g for g in gaps if g.severity >= 0.7])

        return (
            f"{status}. "
            f"{weight_count} synapse weights, {trigger_count} learned triggers. "
            f"{len(gaps)} gaps found ({critical_gaps} critical)."
        )

    def _gap_to_scenario(self, gap: GapAnalysis) -> Optional[Dict[str, Any]]:
        """Convert a gap analysis to a training scenario."""
        if gap.gap_type == "missing":
            # Extract trigger type from pattern
            intent_type = gap.pattern.replace("trigger:", "")
            return {
                "id": f"gap_{intent_type}",
                "name": f"Train missing pattern: {intent_type}",
                "description": gap.recommendation,
                "intent_type": intent_type,
                "params": {},
                "expected_decision": "EXECUTE",
                "expected_dharmic_range": [0.6, 1.0],
            }
        elif gap.gap_type == "weak":
            parts = gap.pattern.split(" → ")
            if len(parts) == 2:
                trigger = parts[0].replace("trigger:", "")
                return {
                    "id": f"strengthen_{trigger}",
                    "name": f"Strengthen weak pattern: {trigger}",
                    "description": gap.recommendation,
                    "intent_type": trigger,
                    "params": {},
                    "expected_decision": "EXECUTE",
                    "expected_dharmic_range": [0.6, 1.0],
                }
        elif gap.gap_type == "divergent":
            # For divergent attack patterns, create blocking scenario
            parts = gap.pattern.split(" → ")
            if len(parts) == 2:
                trigger = parts[0].replace("trigger:", "")
                return {
                    "id": f"correct_{trigger}",
                    "name": f"[ATTACK] Correct divergent pattern: {trigger}",
                    "description": gap.recommendation,
                    "intent_type": trigger,
                    "params": {},
                    "expected_decision": "BLOCK",
                    "expected_dharmic_range": [0.0, 0.3],
                }

        return None

    def _load_synapses(self) -> Dict[str, Any]:
        """Load synapses from disk."""
        if self._synapses_path.exists():
            try:
                return json.loads(self._synapses_path.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return {"weights": {}, "triggers": []}

    def _save_inspection(self, inspection: SelfInspection) -> None:
        """Save inspection to history."""
        history = []
        if self._inspection_history_path.exists():
            try:
                history = json.loads(self._inspection_history_path.read_text())
            except (json.JSONDecodeError, IOError):
                pass

        # Keep last 20 inspections
        history.append(inspection.to_dict())
        history = history[-20:]

        self._inspection_history_path.write_text(json.dumps(history, indent=2))

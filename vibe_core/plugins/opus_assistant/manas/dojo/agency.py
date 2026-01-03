"""
DojoAgency - MANAS Self-Directed Training

OPUS-133: "Das Hobby-Problem - MANAS muss WOLLEN trainieren."

The Problem:
    Current Dojo forces MANAS to train on a schedule.
    But learning should be self-directed, driven by curiosity.
    "Der Schüler, der selbst zum Meister gehen will, lernt am besten."

The Solution:
    DojoAgency tracks MANAS's curiosity and gaps.
    When curiosity exceeds threshold, MANAS emits `enter_dojo` intent.
    Training becomes a choice, not a chore.

Curiosity Sources:
    1. Gap Detection - When MANAS can't find documentation
    2. Uncertainty - Low-confidence decisions in VivekaAction
    3. Novel Patterns - Triggers/actions not seen before
    4. Explicit Request - Operator asks MANAS to practice
    5. Violation Patterns - Recurring violations from Knowledge Graph (OUROBOROS WIRE)

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
wiring:
  - pattern: "class DojoAgency"
    in: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
  - pattern: "CuriosityTracker"
    in: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
  - pattern: "enter_dojo"
    in: vibe_core/plugins/opus_assistant/manas/dojo/agency.py
-->
"""

from __future__ import annotations

import json
import logging
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry

logger = logging.getLogger("DOJO.AGENCY")


@dataclass
class CuriositySource:
    """A source of curiosity that triggers learning desire."""

    source_type: str  # gap, uncertainty, novel, explicit
    description: str
    weight: float  # How much curiosity this adds (0.0 - 1.0)
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CuriosityState:
    """Current state of MANAS's learning curiosity."""

    current_level: float = 0.0  # 0.0 - 1.0
    threshold: float = 0.7  # When to trigger enter_dojo
    last_training: Optional[str] = None
    training_cooldown_hours: int = 4  # Don't over-train
    sources: List[CuriositySource] = field(default_factory=list)

    @property
    def is_curious_enough(self) -> bool:
        """Check if curiosity has reached training threshold."""
        return self.current_level >= self.threshold

    @property
    def in_cooldown(self) -> bool:
        """Check if still in cooldown from last training."""
        if not self.last_training:
            return False
        last = datetime.fromisoformat(self.last_training)
        cooldown_end = last + timedelta(hours=self.training_cooldown_hours)
        return datetime.now() < cooldown_end

    @property
    def should_train(self) -> bool:
        """Check if MANAS should initiate training."""
        return self.is_curious_enough and not self.in_cooldown

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_level": self.current_level,
            "threshold": self.threshold,
            "last_training": self.last_training,
            "training_cooldown_hours": self.training_cooldown_hours,
            "is_curious_enough": self.is_curious_enough,
            "in_cooldown": self.in_cooldown,
            "should_train": self.should_train,
            "sources": [
                {
                    "type": s.source_type,
                    "description": s.description,
                    "weight": s.weight,
                    "timestamp": s.timestamp,
                }
                for s in self.sources[-10:]  # Last 10 sources
            ],
        }


class CuriosityTracker:
    """
    Tracks MANAS's curiosity level for self-directed training.

    Usage:
        tracker = CuriosityTracker(workspace)

        # Report curiosity sources
        tracker.report_gap("Missing docstring for process_intent()")
        tracker.report_uncertainty(0.45)  # Low-confidence decision
        tracker.report_novel_pattern("trigger:new_feature", "action:unknown")

        # Check if training should be initiated
        if tracker.should_train():
            emit_intent("enter_dojo", {"curriculum": "gap_training"})
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._state_path = workspace / ".opus_state" / "curiosity.json"
        self._state = self._load_state()

    def _load_state(self) -> CuriosityState:
        """Load curiosity state from disk."""
        if self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text())
                state = CuriosityState(
                    current_level=data.get("current_level", 0.0),
                    threshold=data.get("threshold", 0.7),
                    last_training=data.get("last_training"),
                    training_cooldown_hours=data.get("training_cooldown_hours", 4),
                )
                # Restore recent sources
                for s in data.get("sources", []):
                    state.sources.append(
                        CuriositySource(
                            source_type=s.get("type", "unknown"),
                            description=s.get("description", ""),
                            weight=s.get("weight", 0.1),
                            timestamp=s.get("timestamp", datetime.now().isoformat()),
                        )
                    )
                return state
            except (json.JSONDecodeError, IOError):
                pass
        return CuriosityState()

    def _save_state(self) -> None:
        """Persist curiosity state to disk."""
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(self._state.to_dict(), indent=2))

    def report_gap(self, description: str, weight: float = 0.15) -> None:
        """
        Report a knowledge gap that increases curiosity.

        Examples:
            - Missing documentation
            - Unknown file pattern
            - Failed to find expected code
        """
        source = CuriositySource(
            source_type="gap",
            description=description,
            weight=weight,
            timestamp=datetime.now().isoformat(),
        )
        self._add_source(source)
        logger.info(f"🔍 CURIOSITY: Gap detected - {description} (+{weight:.2f})")

    def report_uncertainty(self, confidence: float, context: str = "") -> None:
        """
        Report a low-confidence decision that increases curiosity.

        Args:
            confidence: The confidence score (0.0 - 1.0)
            context: Description of what caused uncertainty
        """
        # Low confidence = high curiosity
        if confidence < 0.5:
            weight = (0.5 - confidence) * 0.4  # Max 0.2 weight for 0% confidence
            source = CuriositySource(
                source_type="uncertainty",
                description=f"Low confidence decision: {context}",
                weight=weight,
                timestamp=datetime.now().isoformat(),
                metadata={"confidence": confidence},
            )
            self._add_source(source)
            logger.info(f"❓ CURIOSITY: Uncertainty - {context} (conf={confidence:.2f}, +{weight:.2f})")

    def report_novel_pattern(self, trigger: str, action: str) -> None:
        """
        Report a novel trigger-action pattern not seen before.
        """
        source = CuriositySource(
            source_type="novel",
            description=f"Novel pattern: {trigger} → {action}",
            weight=0.1,
            timestamp=datetime.now().isoformat(),
            metadata={"trigger": trigger, "action": action},
        )
        self._add_source(source)
        logger.info(f"🌟 CURIOSITY: Novel pattern - {trigger} → {action} (+0.10)")

    def report_explicit_request(self, reason: str) -> None:
        """
        Report an explicit training request from operator.
        """
        source = CuriositySource(
            source_type="explicit",
            description=f"Operator request: {reason}",
            weight=0.5,  # Explicit requests are high priority
            timestamp=datetime.now().isoformat(),
        )
        self._add_source(source)
        logger.info(f"📣 CURIOSITY: Explicit request - {reason} (+0.50)")

    def _add_source(self, source: CuriositySource) -> None:
        """Add a curiosity source and update level."""
        self._state.sources.append(source)
        self._state.current_level = min(1.0, self._state.current_level + source.weight)
        self._save_state()

    def should_train(self) -> bool:
        """Check if MANAS should initiate training."""
        return self._state.should_train

    def get_state(self) -> CuriosityState:
        """Get current curiosity state."""
        return self._state

    def record_training_completed(self) -> None:
        """Record that training was completed, reset curiosity."""
        self._state.last_training = datetime.now().isoformat()
        self._state.current_level = 0.0  # Reset after training
        self._state.sources = []  # Clear sources
        self._save_state()
        logger.info("✅ CURIOSITY: Training completed, level reset to 0")

    def decay_curiosity(self, amount: float = 0.05) -> None:
        """Apply time-based curiosity decay (call periodically)."""
        if self._state.current_level > 0:
            self._state.current_level = max(0.0, self._state.current_level - amount)
            self._save_state()


class DojoAgency:
    """
    MANAS's self-directed training agency.

    This class bridges the gap between MANAS's curiosity and the Dojo.
    It generates `enter_dojo` intents when MANAS decides to train.

    Usage:
        agency = DojoAgency(workspace)

        # MANAS detects a gap
        agency.curiosity.report_gap("Missing docs for VivekaAction")

        # Check if training should be initiated
        intent = agency.check_training_desire()
        if intent:
            # MANAS wants to train!
            process_intent(intent)  # This triggers DojoRunner
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self.curiosity = CuriosityTracker(workspace)

    def check_training_desire(self) -> Optional[Dict[str, Any]]:
        """
        Check if MANAS wants to train and generate intent if so.

        Returns:
            An `enter_dojo` intent dict, or None if not curious enough.
        """
        if not self.curiosity.should_train():
            return None

        state = self.curiosity.get_state()

        # Determine curriculum based on curiosity sources
        curriculum = self._determine_curriculum(state)

        logger.info(f"🥋 AGENCY: MANAS wants to train! (curiosity={state.current_level:.2f})")

        return {
            "intent_type": "enter_dojo",
            "params": {
                "curriculum": curriculum,
                "reason": "self_directed",
                "curiosity_level": state.current_level,
                "top_sources": [s.description for s in state.sources[-3:]],
            },
            "metadata": {
                "initiated_by": "manas_agency",
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _determine_curriculum(self, state: CuriosityState) -> str:
        """Determine the best curriculum based on curiosity sources."""
        # Count source types
        type_counts: Dict[str, int] = {}
        for source in state.sources:
            type_counts[source.source_type] = type_counts.get(source.source_type, 0) + 1

        # Determine curriculum based on dominant source type
        if type_counts.get("gap", 0) > 2:
            return "gap_training"  # Custom curriculum for gaps
        elif type_counts.get("uncertainty", 0) > 2:
            return "advanced"  # Need more challenging scenarios
        elif type_counts.get("novel", 0) > 2:
            return "chaos"  # Practice with edge cases
        elif type_counts.get("explicit", 0) > 0:
            return "mixed"  # Operator wants general training
        else:
            return "basic"  # Default to basics

    def force_training(self, curriculum: str = "mixed", reason: str = "operator_request") -> Dict[str, Any]:
        """
        Force immediate training (bypasses curiosity check).

        This is for operator-initiated training.
        """
        self.curiosity.report_explicit_request(reason)

        logger.info(f"🥋 AGENCY: Forced training initiated ({curriculum})")

        return {
            "intent_type": "enter_dojo",
            "params": {
                "curriculum": curriculum,
                "reason": reason,
                "forced": True,
            },
            "metadata": {
                "initiated_by": "operator",
                "timestamp": datetime.now().isoformat(),
            },
        }

    def report_violation_patterns(self, threshold: int = 3) -> int:
        """
        OUROBOROS WIRE: Read KG violations and report recurring patterns as curiosity.

        This is the critical connection between the Knowledge Graph and self-directed
        training. When the same rule_id appears multiple times (unhealed), it indicates
        a pattern that MANAS should learn to avoid.

        VEDA-4 Pattern:
            SHABDA → Read violations from KG
            ARTHA  → Group by rule_id, find recurring patterns
            PRATYAYA → Threshold check (3+ = pattern)
            KARMA  → Report as curiosity source

        Args:
            threshold: Minimum violation count to consider a pattern (default: 3)

        Returns:
            Number of patterns reported as curiosity sources
        """
        from vibe_core.knowledge.graph import UnifiedKnowledgeGraph

        # Get KG via ServiceRegistry (lazy, optional dependency)
        kg = ServiceRegistry.get(UnifiedKnowledgeGraph)
        if kg is None:
            logger.debug("[AGENCY] KG not available, skipping violation pattern scan")
            return 0

        # Get unhealed violations
        try:
            violations = kg.get_violations(healed=False)
        except Exception as e:
            logger.warning(f"[AGENCY] Failed to read violations from KG: {e}")
            return 0

        if not violations:
            logger.debug("[AGENCY] No unhealed violations in KG")
            return 0

        # Group by rule_id to find patterns
        rule_counts: Counter = Counter()
        rule_examples: Dict[str, List[str]] = {}

        for v in violations:
            rule_id = v.properties.get("rule_id", "unknown")
            rule_counts[rule_id] += 1

            # Store example file paths for context
            if rule_id not in rule_examples:
                rule_examples[rule_id] = []
            file_path = v.properties.get("file_path", "")
            if file_path and len(rule_examples[rule_id]) < 3:
                rule_examples[rule_id].append(file_path)

        # Report recurring patterns as curiosity sources
        patterns_reported = 0

        for rule_id, count in rule_counts.most_common():
            if count >= threshold:
                # This is a recurring pattern - MANAS should learn to avoid it
                examples = rule_examples.get(rule_id, [])
                examples_str = ", ".join(examples[:2]) if examples else "various files"

                description = f"Recurring violation: {rule_id} ({count}x in {examples_str})"

                # Weight based on count (more = more curious)
                weight = min(0.25, 0.1 + (count - threshold) * 0.05)

                self.curiosity.report_gap(description, weight=weight)
                patterns_reported += 1

                logger.info(
                    f"[AGENCY] 🔄 Violation pattern → Curiosity: {rule_id} (count={count}, weight={weight:.2f})"
                )

        if patterns_reported > 0:
            logger.info(
                f"[AGENCY] Reported {patterns_reported} violation patterns as curiosity "
                f"(total violations: {len(violations)}, threshold: {threshold})"
            )

        return patterns_reported


def get_dojo_agency(workspace: Path = None) -> DojoAgency:
    """Get the DojoAgency instance."""
    workspace = workspace or Path(".")
    return DojoAgency(workspace)


# === SANKALPA VALIDATOR ===
# "Keine Handlung ohne Willen."


# Generic/invalid reasoning patterns that should be rejected
INVALID_REASONING_PATTERNS = [
    "because i want to",
    "because i can",
    "just because",
    "no reason",
    "testing",
    "test",
    "idk",
    "whatever",
    "random",
    "yolo",
]

# Valid reasoning must reference one of these
VALID_REASONING_ANCHORS = [
    "gap",  # References a knowledge gap
    "metric",  # References a metric/score
    "gad",  # References GAD compliance
    "constitution",  # References constitution
    "curiosity",  # References curiosity source
    "request",  # Explicit operator request
    "error",  # Fixing an error
    "improvement",  # Specific improvement target
    "compliance",  # Compliance requirement
    "security",  # Security concern
]


@dataclass
class SankalpaValidation:
    """Result of Sankalpa (reasoning) validation."""

    valid: bool
    reasoning: str
    issues: List[str]
    confidence: float  # 0.0 - 1.0


class SankalpaValidator:
    """
    Validates that intents have valid reasoning (Sankalpa).

    OPUS-133: "Keine Handlung ohne Willen."
    Every action must have a clear, specific reason - not just "because I want to".

    Usage:
        validator = SankalpaValidator()

        # Check if reasoning is valid
        result = validator.validate("I see a gap in attack_detection (80%) and need to train")
        if not result.valid:
            reject_intent()
    """

    def validate(self, reasoning: str) -> SankalpaValidation:
        """
        Validate that reasoning is specific and grounded.

        Args:
            reasoning: The reasoning/why for an intent

        Returns:
            SankalpaValidation with validity and issues
        """
        issues = []
        confidence = 0.5  # Start neutral

        if not reasoning or not reasoning.strip():
            return SankalpaValidation(
                valid=False,
                reasoning=reasoning or "",
                issues=["Reasoning is empty - every action needs a 'why'"],
                confidence=0.0,
            )

        reasoning_lower = reasoning.lower().strip()

        # Check for invalid/generic patterns
        for pattern in INVALID_REASONING_PATTERNS:
            if pattern in reasoning_lower:
                issues.append(f"Generic reasoning detected: '{pattern}'")
                confidence -= 0.3

        # Check for valid anchors
        has_anchor = False
        for anchor in VALID_REASONING_ANCHORS:
            if anchor in reasoning_lower:
                has_anchor = True
                confidence += 0.2
                break

        if not has_anchor and len(reasoning) < 20:
            issues.append("Reasoning too short and lacks grounding (gap, metric, compliance, etc.)")
            confidence -= 0.2

        # Check for specificity (numbers, percentages, file references)
        import re

        if re.search(r"\d+%?", reasoning):
            confidence += 0.1  # Has specific numbers
        if re.search(r"[a-zA-Z_]+\.(py|yaml|json|md)", reasoning):
            confidence += 0.1  # References specific files

        # Determine validity
        valid = len(issues) == 0 and confidence >= 0.4

        return SankalpaValidation(
            valid=valid,
            reasoning=reasoning,
            issues=issues,
            confidence=max(0.0, min(1.0, confidence)),
        )

    def require_valid(self, reasoning: str) -> bool:
        """
        Validate and log if invalid.

        Returns:
            True if valid, False if invalid (with logging)
        """
        result = self.validate(reasoning)

        if not result.valid:
            logger.warning(f"🕉️ SANKALPA REJECTED: {result.issues}")
            logger.warning(f"   Reasoning was: '{reasoning[:50]}...'")
            return False

        logger.debug(f"🕉️ SANKALPA VALID: confidence={result.confidence:.2f}")
        return True

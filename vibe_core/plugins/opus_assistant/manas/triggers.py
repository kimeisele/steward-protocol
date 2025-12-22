"""
OPUS-111 + OPUS-112 + OPUS-114: Signal Alignment, Synaptic Inference & Akshara Kernel.

"Ein Gehirn, das seine eigene Sprache nicht versteht, ist lobotomiert."
"Ein Gehirn, das sein Tagebuch nicht liest, lernt nie."
"अक्षराणां अकारोऽस्मि" - "Of letters, I am 'A'" (Bhagavad Gita 10.33)

This module defines:
1. The canonical vocabulary for synaptic triggers and actions (OPUS-111)
2. The inference engine for reading synaptic memory (OPUS-112)
3. Akshara-based resonance for Dharmic scoring (OPUS-114)

OPUS-111 (Signal Alignment):
- TriggerPatterns: Canonical trigger constants
- ActionPatterns: Canonical action constants
- normalize_trigger(): Maps raw events to canonical patterns

OPUS-112 (Synaptic Inference):
- SynapticMemory: Read/write access to synapses.json
- consult(): Query learned associations for decision making
- get_confidence(): Get learned weight for an intent

OPUS-114 (Akshara Kernel):
- DharmicRecommendation: Weight × Resonance scoring
- Varnamala-based resonance calculation
- consult_dharmic(): Returns recommendations sorted by Dharmic score

The Loop:
    Event → normalize_trigger() → SynapticMemory.consult_dharmic() → Decision
                                         ↓
    Outcome → _update_synapses() ← SynapticMemory.update()

Usage:
    from vibe_core.plugins.opus_assistant.manas.triggers import (
        TriggerPatterns,
        ActionPatterns,
        normalize_trigger,
        SynapticMemory,
    )

    # OPUS-111: Normalize trigger
    trigger = normalize_trigger(intent)

    # OPUS-114: Consult memory with Dharmic scoring
    memory = SynapticMemory.get(workspace)
    recommendations = memory.consult_dharmic(trigger)
    # Returns: [DharmicRecommendation(action="action:run_tests", weight=0.9, resonance=0.8, dharmic_score=0.72)]
"""

import fnmatch
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MANAS.Synapses")


class TriggerPatterns(str, Enum):
    """
    Canonical trigger patterns for synaptic learning.

    These are the ONLY valid trigger strings in the system.
    Any event must be normalized to one of these patterns.

    Naming convention:
    - trigger:<category>:<optional_subcategory>
    - Wildcards use ** for path segments
    """

    # === ERROR/FAILURE TRIGGERS ===
    TEST_FAILURE = "trigger:test_failure"
    ERROR_DETECTED = "trigger:error_detected"
    LINT_FAILURE = "trigger:lint_failure"
    BUILD_FAILURE = "trigger:build_failure"

    # === FILE CHANGE TRIGGERS ===
    # Normalized patterns - file paths get mapped to these
    FILE_CHANGED_CORE = "trigger:file_changed:vibe_core/**"
    FILE_CHANGED_TESTS = "trigger:file_changed:tests/**"
    FILE_CHANGED_DOCS = "trigger:file_changed:docs/**"
    FILE_CHANGED_CONFIG = "trigger:file_changed:config/**"
    FILE_CHANGED_OTHER = "trigger:file_changed:other"

    # === GAP DETECTION TRIGGERS ===
    GAP_MISSING_CODE = "trigger:gap_detected:missing_code"
    GAP_MISSING_DOC = "trigger:gap_detected:missing_doc"
    GAP_MISSING_TEST = "trigger:gap_detected:missing_test"
    GAP_STALE_DOC = "trigger:gap_detected:stale_doc"
    GAP_MISSING_HARNESS = "trigger:gap_detected:missing_harness"

    # === INTENT/PROCESS TRIGGERS ===
    INTENT_STUCK = "trigger:intent_stuck"
    INTENT_EXPIRED = "trigger:intent_expired"
    DUPLICATE_DETECTED = "trigger:duplicate_class_detected"

    # === SUTRA (DOC/CODE) TRIGGERS ===
    SUTRA_MISSING_CODE = "trigger:sutra:missing_code"
    SUTRA_MISSING_DOC = "trigger:sutra:missing_doc"
    SUTRA_STALE = "trigger:sutra:stale"
    SUTRA_MISSING_HARNESS = "trigger:sutra:missing_harness"

    # === SPECIAL TRIGGERS ===
    MERU_TEST = "trigger:meru_test"  # Persistence verification
    IDLE_DETECTED = "trigger:idle_detected"
    KARMA_LOW = "trigger:karma_low"

    @classmethod
    def from_string(cls, s: str) -> Optional["TriggerPatterns"]:
        """Get enum from string value."""
        for pattern in cls:
            if pattern.value == s:
                return pattern
        return None


class ActionPatterns(str, Enum):
    """
    Canonical action patterns for synaptic learning.

    These are the responses that MANAS can learn to associate with triggers.
    """

    # === NOTIFICATION ACTIONS ===
    NOTIFY_OPERATOR = "action:notify_operator"
    ESCALATE_TO_OPERATOR = "action:escalate_to_operator"
    REPORT_TO_OPERATOR = "action:report_to_operator"
    LOG_DIAGNOSTIC = "action:log_diagnostic"

    # === REPAIR ACTIONS ===
    ANALYZE_ERROR = "action:analyze_error"
    AUTO_RETRY = "action:auto_retry"
    AUTO_FIX = "action:auto_fix"
    CONSOLIDATE = "action:consolidate"

    # === QUALITY ACTIONS ===
    RUN_TESTS = "action:run_tests"
    CHECK_LINT = "action:check_lint"
    UPDATE_DOCS = "action:update_docs"

    # === GAP ACTIONS ===
    CREATE_CODE = "action:create_code"
    CREATE_DOC = "action:create_doc"
    CREATE_TEST = "action:create_test"
    CREATE_HARNESS = "action:create_harness"

    @classmethod
    def from_intent_type(cls, intent_type: str) -> Optional["ActionPatterns"]:
        """Map intent type to action pattern."""
        mapping = {
            "notify_operator": cls.NOTIFY_OPERATOR,
            "analyze_error": cls.ANALYZE_ERROR,
            "auto_retry": cls.AUTO_RETRY,
            "run_tests": cls.RUN_TESTS,
            "check_lint": cls.CHECK_LINT,
            "consolidate": cls.CONSOLIDATE,
            "doc_modify": cls.UPDATE_DOCS,
            "create_code": cls.CREATE_CODE,
            "create_doc": cls.CREATE_DOC,
            "create_test": cls.CREATE_TEST,
        }
        return mapping.get(intent_type)


@dataclass
class NormalizationRule:
    """A rule for normalizing raw events to canonical triggers."""

    # Pattern to match (regex or fnmatch)
    match_pattern: str
    # Target canonical trigger
    canonical_trigger: TriggerPatterns
    # Match type: "prefix", "contains", "regex", "fnmatch"
    match_type: str = "prefix"


# === NORMALIZATION RULES ===
# Order matters: first match wins
NORMALIZATION_RULES: List[NormalizationRule] = [
    # File changes - normalize to bucket patterns
    NormalizationRule("vibe_core/", TriggerPatterns.FILE_CHANGED_CORE, "prefix"),
    NormalizationRule("tests/", TriggerPatterns.FILE_CHANGED_TESTS, "prefix"),
    NormalizationRule("docs/", TriggerPatterns.FILE_CHANGED_DOCS, "prefix"),
    NormalizationRule("config/", TriggerPatterns.FILE_CHANGED_CONFIG, "prefix"),
    # Gap types - normalize to canonical gaps
    NormalizationRule("missing_code", TriggerPatterns.GAP_MISSING_CODE, "exact"),
    NormalizationRule("missing_doc", TriggerPatterns.GAP_MISSING_DOC, "exact"),
    NormalizationRule("missing_test", TriggerPatterns.GAP_MISSING_TEST, "exact"),
    NormalizationRule("stale_doc", TriggerPatterns.GAP_STALE_DOC, "exact"),
    NormalizationRule("missing_harness", TriggerPatterns.GAP_MISSING_HARNESS, "exact"),
    # Sutra types
    NormalizationRule("sutra_missing_code", TriggerPatterns.SUTRA_MISSING_CODE, "exact"),
    NormalizationRule("sutra_missing_doc", TriggerPatterns.SUTRA_MISSING_DOC, "exact"),
    NormalizationRule("sutra_stale", TriggerPatterns.SUTRA_STALE, "exact"),
    NormalizationRule("sutra_missing_harness", TriggerPatterns.SUTRA_MISSING_HARNESS, "exact"),
]


def _match_rule(value: str, rule: NormalizationRule) -> bool:
    """Check if a value matches a normalization rule."""
    if rule.match_type == "prefix":
        return value.startswith(rule.match_pattern)
    elif rule.match_type == "exact":
        return value == rule.match_pattern
    elif rule.match_type == "contains":
        return rule.match_pattern in value
    elif rule.match_type == "regex":
        return bool(re.match(rule.match_pattern, value))
    elif rule.match_type == "fnmatch":
        return fnmatch.fnmatch(value, rule.match_pattern)
    return False


def normalize_file_path(path: str) -> TriggerPatterns:
    """
    Normalize a file path to a canonical file change trigger.

    Args:
        path: The file path (e.g., "vibe_core/loaders/foo.py")

    Returns:
        Canonical trigger pattern
    """
    for rule in NORMALIZATION_RULES:
        if rule.canonical_trigger.value.startswith("trigger:file_changed:"):
            if _match_rule(path, rule):
                return rule.canonical_trigger

    return TriggerPatterns.FILE_CHANGED_OTHER


def normalize_gap_type(gap_type: str) -> TriggerPatterns:
    """
    Normalize a gap type to a canonical gap trigger.

    Args:
        gap_type: The gap type (e.g., "missing_code")

    Returns:
        Canonical trigger pattern
    """
    for rule in NORMALIZATION_RULES:
        if rule.canonical_trigger.value.startswith("trigger:gap_detected:"):
            if _match_rule(gap_type, rule):
                return rule.canonical_trigger

    # Fallback: construct from gap type but log warning
    return TriggerPatterns.GAP_MISSING_CODE  # Safe default


def normalize_trigger(intent: Any) -> Optional[TriggerPatterns]:
    """
    Normalize an intent to its canonical trigger pattern.

    This is the MAIN entry point for trigger normalization.
    Replaces the old _extract_trigger() with hardcoded strings.

    Args:
        intent: An Intent object with params and intent_type

    Returns:
        Canonical TriggerPatterns enum value, or None if no trigger
    """
    params = getattr(intent, "params", {}) or {}
    intent_type = getattr(intent, "intent_type", "")

    # === GAP DETECTION ===
    if "gap_type" in params:
        gap_type = params["gap_type"]
        return normalize_gap_type(gap_type)

    # === FILE CHANGES ===
    if "file_path" in params:
        path = params["file_path"]
        return normalize_file_path(path)

    # === ERROR DETECTION ===
    if "error" in params or intent_type.startswith("fix_"):
        return TriggerPatterns.ERROR_DETECTED

    # === SPECIAL TYPES ===
    if intent_type == "persistence_test":
        return TriggerPatterns.MERU_TEST

    # === SUTRA TYPES ===
    if intent_type.startswith("sutra_"):
        sutra_type = intent_type  # e.g., "sutra_missing_code"
        for rule in NORMALIZATION_RULES:
            if rule.canonical_trigger.value.startswith("trigger:sutra:"):
                if _match_rule(sutra_type, rule):
                    return rule.canonical_trigger
        return TriggerPatterns.SUTRA_MISSING_CODE  # Fallback

    # === INTENT STATES ===
    if intent_type == "intent_stuck" or "stuck" in intent_type:
        return TriggerPatterns.INTENT_STUCK

    if "duplicate" in intent_type:
        return TriggerPatterns.DUPLICATE_DETECTED

    # === NO CANONICAL TRIGGER ===
    # Rather than generating dynamic strings, return None
    # This prevents memory pollution with non-canonical triggers
    return None


def get_seed_synapses() -> Dict[str, Dict[str, float]]:
    """
    Get the canonical seed synapses for a fresh system.

    These are the initial associations that MANAS starts with.
    All triggers and actions use canonical patterns.

    Returns:
        Dict of trigger -> {action: weight}
    """
    return {
        TriggerPatterns.TEST_FAILURE.value: {
            ActionPatterns.NOTIFY_OPERATOR.value: 1.0,
            ActionPatterns.ANALYZE_ERROR.value: 0.8,
            ActionPatterns.AUTO_RETRY.value: 0.3,
        },
        TriggerPatterns.FILE_CHANGED_CORE.value: {
            ActionPatterns.RUN_TESTS.value: 0.9,
            ActionPatterns.CHECK_LINT.value: 0.7,
        },
        TriggerPatterns.INTENT_STUCK.value: {
            ActionPatterns.ESCALATE_TO_OPERATOR.value: 0.95,
            ActionPatterns.LOG_DIAGNOSTIC.value: 0.8,
        },
        TriggerPatterns.DUPLICATE_DETECTED.value: {
            ActionPatterns.CONSOLIDATE.value: 0.7,
            ActionPatterns.REPORT_TO_OPERATOR.value: 0.9,
        },
    }


class SynapseVocabulary:
    """
    The complete synaptic vocabulary - singleton for system-wide consistency.

    Usage:
        vocab = SynapseVocabulary.get()
        trigger = vocab.normalize_trigger(intent)
        action = vocab.get_action_for_intent(intent_type)
    """

    _instance: Optional["SynapseVocabulary"] = None

    @classmethod
    def get(cls) -> "SynapseVocabulary":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def normalize_trigger(self, intent: Any) -> Optional[str]:
        """Normalize intent to canonical trigger string."""
        pattern = normalize_trigger(intent)
        return pattern.value if pattern else None

    def normalize_file_path(self, path: str) -> str:
        """Normalize file path to canonical trigger string."""
        return normalize_file_path(path).value

    def get_action_for_intent(self, intent_type: str) -> Optional[str]:
        """Get canonical action string for an intent type."""
        action = ActionPatterns.from_intent_type(intent_type)
        return action.value if action else f"action:{intent_type}"

    def is_valid_trigger(self, trigger: str) -> bool:
        """Check if a trigger string is canonical."""
        return TriggerPatterns.from_string(trigger) is not None

    def get_all_triggers(self) -> List[str]:
        """Get all canonical trigger strings."""
        return [p.value for p in TriggerPatterns]

    def get_all_actions(self) -> List[str]:
        """Get all canonical action strings."""
        return [a.value for a in ActionPatterns]


# =============================================================================
# OPUS-112: SYNAPTIC INFERENCE - THE READING BRAIN
# =============================================================================


@dataclass
class SynapticRecommendation:
    """A recommended action from synaptic memory."""

    action: str  # e.g., "action:run_tests"
    weight: float  # 0.0 - 1.0
    trigger: str  # The trigger that led to this recommendation

    @property
    def confidence_level(self) -> str:
        """Human-readable confidence level."""
        if self.weight >= 0.9:
            return "very_high"
        elif self.weight >= 0.7:
            return "high"
        elif self.weight >= 0.5:
            return "medium"
        elif self.weight >= 0.3:
            return "low"
        else:
            return "very_low"


@dataclass
class DharmicRecommendation:
    """
    OPUS-114: A recommended action with Akshara resonance scoring.

    This extends SynapticRecommendation with:
    - resonance: Phonetic harmony based on Varga distance (0.2 - 1.0)
    - dharmic_score: weight × resonance (the true decision metric)
    - varga_trigger: The Varga of the trigger
    - varga_action: The Varga of the action
    """

    action: str  # e.g., "action:run_tests"
    weight: float  # Synaptic weight (0.0 - 1.0)
    resonance: float  # Akshara resonance (0.2 - 1.0)
    dharmic_score: float  # weight × resonance
    trigger: str  # The trigger pattern
    varga_trigger: str  # e.g., "KANTHYA"
    varga_action: str  # e.g., "KANTHYA"

    @property
    def confidence_level(self) -> str:
        """Human-readable confidence level based on dharmic_score."""
        if self.dharmic_score >= 0.8:
            return "very_high"
        elif self.dharmic_score >= 0.6:
            return "high"
        elif self.dharmic_score >= 0.4:
            return "medium"
        elif self.dharmic_score >= 0.2:
            return "low"
        else:
            return "very_low"

    @property
    def is_resonant(self) -> bool:
        """Check if trigger and action are in same or adjacent Vargas."""
        return self.resonance >= 0.8

    @property
    def harmony_description(self) -> str:
        """Human-readable description of the harmonic relationship."""
        if self.resonance >= 1.0:
            return "perfect"  # Same Varga
        elif self.resonance >= 0.8:
            return "harmonic"  # Adjacent Varga
        elif self.resonance >= 0.6:
            return "moderate"  # 2 Vargas apart
        elif self.resonance >= 0.4:
            return "weak"  # 3 Vargas apart
        else:
            return "distant"  # 4 Vargas apart


class SynapticMemory:
    """
    OPUS-112: The Reading Brain - Synaptic Memory with Inference.

    "A brain that writes but never reads is just a diary."

    This class provides:
    1. consult(trigger) - Get recommended actions for a trigger
    2. get_confidence(intent) - Get learned confidence for an intent
    3. load/save - Persistence to synapses.json (via SynapseStore)

    The key insight: Learning without inference is just data collection.
    MANAS must READ the synapses to make experience-based decisions.

    OPUS-171: Now uses SynapseStore for unified synapse persistence.

    Usage:
        memory = SynapticMemory.get(workspace)

        # When a trigger fires, consult memory:
        trigger = normalize_trigger(intent)
        recommendations = memory.consult(trigger)

        # Use recommendations for decision making:
        for rec in recommendations:
            if rec.weight >= 0.7:
                # High confidence - consider auto-executing
                ...
    """

    _instances: Dict[str, "SynapticMemory"] = {}

    def __init__(self, workspace: Path):
        """Initialize synaptic memory for a workspace."""
        self._workspace = workspace
        # OPUS-171: Use SynapseStore instead of direct file access
        self._store = None  # Lazy init to avoid circular imports

    @classmethod
    def get(cls, workspace: Path) -> "SynapticMemory":
        """Get or create SynapticMemory instance for workspace."""
        key = str(workspace)
        if key not in cls._instances:
            cls._instances[key] = cls(workspace)
        return cls._instances[key]

    def _get_store(self):
        """Get the SynapseStore instance (lazy init to avoid circular imports)."""
        if self._store is None:
            from vibe_core.state.synapse_store import get_synapse_store

            self._store = get_synapse_store(
                workspace=self._workspace,
                seed_weights=get_seed_synapses(),
            )
        return self._store

    def _load_synapses(self, force: bool = False) -> Dict[str, Any]:
        """Load synapses via SynapseStore (OPUS-171 unified access)."""
        return self._get_store().load(force=force)

    def consult(
        self,
        trigger: str,
        min_weight: float = 0.0,
        limit: int = 5,
    ) -> List[SynapticRecommendation]:
        """
        Consult synaptic memory for a trigger.

        This is the INFERENCE method - reading learned associations.

        Args:
            trigger: Canonical trigger string (e.g., "trigger:test_failure")
            min_weight: Minimum weight threshold (default 0.0 = return all)
            limit: Maximum recommendations to return

        Returns:
            List of SynapticRecommendation, sorted by weight descending
        """
        synapses = self._load_synapses()
        weights = synapses.get("weights", {})

        # Look up trigger
        if trigger not in weights:
            logger.debug(f"🧠 INFERENCE: No learned actions for {trigger}")
            return []

        actions = weights[trigger]
        recommendations = []

        for action, weight in actions.items():
            if weight >= min_weight:
                recommendations.append(
                    SynapticRecommendation(
                        action=action,
                        weight=weight,
                        trigger=trigger,
                    )
                )

        # Sort by weight descending
        recommendations.sort(key=lambda r: r.weight, reverse=True)

        # Limit
        recommendations = recommendations[:limit]

        if recommendations:
            logger.debug(
                f"🧠 INFERENCE: {trigger} → {len(recommendations)} recommendations "
                f"(top: {recommendations[0].action} @ {recommendations[0].weight:.2f})"
            )

        return recommendations

    def consult_for_intent(self, intent: Any) -> List[SynapticRecommendation]:
        """
        Consult synaptic memory for an intent.

        Convenience method that normalizes the intent first.

        Args:
            intent: An Intent object

        Returns:
            List of SynapticRecommendation
        """
        trigger_pattern = normalize_trigger(intent)
        if not trigger_pattern:
            return []
        return self.consult(trigger_pattern.value)

    def consult_dharmic(
        self,
        trigger: str,
        min_dharmic_score: float = 0.0,
        limit: int = 5,
    ) -> List[DharmicRecommendation]:
        """
        OPUS-114: Consult synaptic memory with Akshara resonance scoring.

        This is the DHARMIC inference method - reading learned associations
        and scoring them by phonetic harmony (Varga resonance).

        Dharmic Score = Synaptic Weight × Akshara Resonance

        Args:
            trigger: Canonical trigger string (e.g., "trigger:test_failure")
            min_dharmic_score: Minimum dharmic score threshold (default 0.0)
            limit: Maximum recommendations to return

        Returns:
            List of DharmicRecommendation, sorted by dharmic_score descending
        """
        # Lazy import to avoid circular dependency
        from vibe_core.plugins.opus_assistant.manas.akshara import (
            calculate_dharmic_score,
            calculate_resonance,
            get_action_varga,
            get_trigger_varga,
        )

        synapses = self._load_synapses()
        weights = synapses.get("weights", {})

        # Look up trigger
        if trigger not in weights:
            logger.debug(f"🕉️ DHARMIC: No learned actions for {trigger}")
            return []

        actions = weights[trigger]
        trigger_varga = get_trigger_varga(trigger)
        recommendations = []

        for action, weight in actions.items():
            action_varga = get_action_varga(action)
            resonance = calculate_resonance(trigger, action)
            dharmic_score = calculate_dharmic_score(trigger, action, weight)

            if dharmic_score >= min_dharmic_score:
                recommendations.append(
                    DharmicRecommendation(
                        action=action,
                        weight=weight,
                        resonance=resonance,
                        dharmic_score=dharmic_score,
                        trigger=trigger,
                        varga_trigger=trigger_varga.name,
                        varga_action=action_varga.name,
                    )
                )

        # Sort by dharmic_score descending (not just weight!)
        recommendations.sort(key=lambda r: r.dharmic_score, reverse=True)

        # Limit
        recommendations = recommendations[:limit]

        if recommendations:
            top = recommendations[0]
            logger.debug(
                f"🕉️ DHARMIC: {trigger} → {len(recommendations)} recommendations "
                f"(top: {top.action} @ {top.dharmic_score:.2f} dharmic, {top.harmony_description})"
            )

        return recommendations

    def consult_dharmic_for_intent(self, intent: Any) -> List[DharmicRecommendation]:
        """
        OPUS-114: Consult synaptic memory with dharmic scoring for an intent.

        Args:
            intent: An Intent object

        Returns:
            List of DharmicRecommendation
        """
        trigger_pattern = normalize_trigger(intent)
        if not trigger_pattern:
            return []
        return self.consult_dharmic(trigger_pattern.value)

    def get_dharmic_confidence(self, intent: Any) -> float:
        """
        OPUS-114: Get the dharmic confidence for an intent.

        This returns weight × resonance, not just weight.

        Args:
            intent: An Intent object

        Returns:
            Dharmic score (0.0 - 1.0), or 0.3 if not learned
        """
        from vibe_core.plugins.opus_assistant.manas.akshara import calculate_dharmic_score

        trigger_pattern = normalize_trigger(intent)
        if not trigger_pattern:
            return 0.3  # Low - no canonical trigger

        trigger = trigger_pattern.value
        action = f"action:{getattr(intent, 'intent_type', 'unknown')}"

        synapses = self._load_synapses()
        weights = synapses.get("weights", {})

        if trigger not in weights:
            return 0.3  # Low - no experience

        actions = weights[trigger]
        if action not in actions:
            return 0.3  # Low - no experience with this action

        weight = actions[action]
        return calculate_dharmic_score(trigger, action, weight)

    def get_confidence(self, intent: Any) -> float:
        """
        Get the learned confidence for an intent.

        This looks up the intent's action in the synaptic memory
        and returns the weight (0.0 - 1.0).

        Args:
            intent: An Intent object

        Returns:
            Confidence score (0.0 - 1.0), or 0.5 if not learned
        """
        trigger_pattern = normalize_trigger(intent)
        if not trigger_pattern:
            return 0.5  # Neutral - no experience

        trigger = trigger_pattern.value
        action = f"action:{getattr(intent, 'intent_type', 'unknown')}"

        synapses = self._load_synapses()
        weights = synapses.get("weights", {})

        if trigger not in weights:
            return 0.5  # Neutral - no experience with this trigger

        actions = weights[trigger]
        if action not in actions:
            return 0.5  # Neutral - no experience with this action

        return actions[action]

    def get_best_action(self, trigger: str) -> Optional[Tuple[str, float]]:
        """
        Get the single best action for a trigger.

        Args:
            trigger: Canonical trigger string

        Returns:
            Tuple of (action, weight) or None if no actions learned
        """
        recommendations = self.consult(trigger, limit=1)
        if not recommendations:
            return None
        return (recommendations[0].action, recommendations[0].weight)

    def has_experience(self, trigger: str) -> bool:
        """Check if we have any learned experience for this trigger."""
        synapses = self._load_synapses()
        weights = synapses.get("weights", {})
        return trigger in weights and len(weights[trigger]) > 0

    def get_all_triggers_with_experience(self) -> List[str]:
        """Get all triggers that have learned associations."""
        synapses = self._load_synapses()
        weights = synapses.get("weights", {})
        return list(weights.keys())

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about synaptic memory."""
        synapses = self._load_synapses()
        weights = synapses.get("weights", {})
        meta = synapses.get("meta", {})

        total_triggers = len(weights)
        total_actions = sum(len(v) for v in weights.values())

        # Find highest and lowest weights
        all_weights = [w for actions in weights.values() for w in actions.values()]
        avg_weight = sum(all_weights) / len(all_weights) if all_weights else 0.0

        return {
            "total_triggers": total_triggers,
            "total_connections": total_actions,
            "average_weight": round(avg_weight, 3),
            "schema_version": synapses.get("schema", "unknown"),
            "last_updated": meta.get("last_updated", "unknown"),
        }

    def invalidate_cache(self) -> None:
        """Invalidate the cache (force reload on next access)."""
        # OPUS-171: Delegate to SynapseStore
        self._get_store().invalidate_cache()

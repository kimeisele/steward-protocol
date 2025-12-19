"""
OPUS-111: Signal Alignment - The Synaptic Vocabulary.

"Ein Gehirn, das seine eigene Sprache nicht versteht, ist lobotomiert."

This module defines the canonical vocabulary for synaptic triggers and actions.
All components that emit or consume synaptic signals MUST use these constants.

The Problem (before OPUS-111):
- _extract_trigger() generated dynamic strings like "trigger:file_changed:vibe_core/loaders/**"
- synapses.json had hardcoded patterns like "trigger:file_changed:vibe_core/**/*.py"
- These didn't match → synapses were dead (lobotomized)

The Solution:
1. TriggerPatterns: Canonical trigger constants
2. ActionPatterns: Canonical action constants
3. normalize_trigger(): Maps raw events to canonical patterns
4. SynapseVocabulary: The complete signal dictionary

Usage:
    from vibe_core.plugins.opus_assistant.manas.triggers import (
        TriggerPatterns,
        ActionPatterns,
        normalize_trigger,
    )

    # In _extract_trigger():
    trigger = normalize_trigger(intent)

    # In synapses.json seed:
    # Use TriggerPatterns.TEST_FAILURE instead of hardcoded strings
"""

import fnmatch
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


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

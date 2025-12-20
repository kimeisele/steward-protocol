"""
OPUS-133: Viveka Action - The Hands of Discrimination.

This action executes triage intents from VivekaSense with Dharmic Scoring.
It uses SILPA (The Self-Architect) to safely add documentation, and
consults the Akshara Kernel (OPUS-114) for resonance-based decision making.

Handled Intent Types:
- triage_p1_critical: Auto-fix critical documentation gaps
- triage_p2_high: Auto-fix high priority gaps
- triage_execute: Execute a specific triage fix
- viveka_auto_doc: Automatic documentation generation

The Dharmic Protocol applies:
1. CONSULT: Query consult_dharmic() for resonance scoring
2. EVALUATE: Check Shiva context for "necessary evil" actions
3. DECIDE: Execute, warn, or block based on dharmic_score
4. LOG: Full audit trail of all decisions

Decision Thresholds:
- dharmic_score >= 0.6: EXECUTE (high confidence)
- 0.4 <= dharmic_score < 0.6: WARN + EXECUTE (neutral - proceed with caution)
- dharmic_score < 0.4: BLOCK unless Shiva context applies

Shiva Context (Necessary Evil):
- Some destruction is necessary for healing (cache clearing, log rotation)
- When trigger and action are both in REPAIR (MURDHANYA) layer, destruction is expected
- Context determines whether destruction is dharmic or adharmic

"Viveka sees, Viveka discriminates, Viveka ACTS - with full awareness."

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_sense.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/triggers.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
wiring:
  - pattern: "class VivekaAction"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "handled_intent_types.*triage_p1_critical"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "class VivekaDecisionLog"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
  - pattern: "SHIVA_CONTEXT_PATTERNS"
    in: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
-->
"""

import ast
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

# P0: Import StateService for centralized state management
from vibe_core.state import get_state_service

from .base_action import ActionResult, BaseAction

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent
    from vibe_core.plugins.opus_assistant.manas.triggers import DharmicRecommendation

logger = logging.getLogger("MANAS.Action.Viveka")


# =============================================================================
# OPUS-133: DECISION THRESHOLDS
# =============================================================================

# Dharmic score thresholds for decision making
DHARMIC_THRESHOLD_EXECUTE = 0.6  # >= this: confident execution
DHARMIC_THRESHOLD_WARN = 0.4  # >= this but < EXECUTE: warn but proceed
# Below WARN: block unless Shiva context

# OPUS-133 GURUKULA: CuriosityTracker Integration
# When MANAS is uncertain, feed curiosity to trigger self-directed training
_curiosity_tracker = None


def _get_curiosity_tracker():
    """Lazy load CuriosityTracker to avoid circular imports."""
    global _curiosity_tracker
    if _curiosity_tracker is None:
        try:
            from vibe_core.plugins.opus_assistant.manas.dojo.agency import CuriosityTracker

            _curiosity_tracker = CuriosityTracker(Path("."))
        except ImportError:
            pass
    return _curiosity_tracker


# =============================================================================
# OPUS-133: PRABHUPADA PATCH - Ego Prevention
# =============================================================================
# "The soul is never satisfied with material pleasures."
# - Bhagavad Gita 3.39
#
# VAIRAGYA: Synaptic Detachment - prevents ego growth
# Weights > 0.95 decay by 1% each cycle (prevents runaway confidence)
VAIRAGYA_THRESHOLD = 0.95
VAIRAGYA_DECAY = 0.99  # Multiply by this (1% decay)

# NISHKAMA KARMA: Selfless Action - duty without reward
# These intent types are dharmic duties that should not receive
# reinforcement. They are done because they MUST be done, not for reward.
DHARMIC_DUTIES = {
    "run_tests",  # Testing is duty, not reward
    "check_lint",  # Lint is hygiene, not achievement
    "format_code",  # Formatting is expected, not exceptional
    "backup_state",  # Preservation is duty
    "audit_log",  # Auditing is duty
    "health_check",  # Monitoring is duty
    "notify_operator",  # Communication is duty
    "validate_schema",  # Validation is hygiene
}

# PRASADAM: Grace for Pure Intent
# When intent was pure (high dharmic score) but execution failed
# due to technical reasons, the system shows grace - no punishment.
# A servant who runs to serve and stumbles should not be punished.
PRASADAM_THRESHOLD = 0.8  # Intent score above this gets grace on failure


# =============================================================================
# OPUS-133: SHIVA CONTEXT - "Necessary Evil" Patterns
# =============================================================================
# "Sometimes you must destroy to create" - Shiva's role in the Trimurti
#
# These patterns define when destruction is DHARMIC (righteous):
# - Cleaning caches, logs, temp files (hygiene)
# - Removing deprecated code (evolution)
# - Consolidating duplicates (unity)
# - Fixing critical bugs by rewriting (healing)
#
# The Shiva Principle: Destruction in service of creation is not evil.

SHIVA_CONTEXT_PATTERNS: Dict[str, Dict[str, Any]] = {
    # Pattern: trigger context -> allowed "destructive" actions
    "trigger:error_detected": {
        "allowed_actions": ["action:auto_fix", "action:consolidate"],
        "reason": "Fixing errors may require removing bad code",
        "layer": "REPAIR",
    },
    "trigger:lint_failure": {
        "allowed_actions": ["action:auto_fix", "action:consolidate"],
        "reason": "Lint fixes may remove/rewrite code",
        "layer": "REPAIR",
    },
    "trigger:duplicate_class_detected": {
        "allowed_actions": ["action:consolidate", "action:auto_fix"],
        "reason": "Consolidation requires removing duplicates",
        "layer": "REPAIR",
    },
    "trigger:gap_detected:stale_doc": {
        "allowed_actions": ["action:update_docs", "action:create_doc"],
        "reason": "Stale docs may need replacement",
        "layer": "INTERFACE",
    },
}

# Layer-based Shiva context: when BOTH trigger and action are in REPAIR layer,
# destruction is expected and allowed
SHIVA_LAYER_ALLOWANCES = {
    "REPAIR": {  # MURDHANYA - the fire of transformation
        "allowed_actions": [
            "action:auto_fix",
            "action:consolidate",
            "action:refactor_code",
            "action:move_code",
        ],
        "reason": "Repair layer actions inherently involve transformation",
    }
}

# Protected paths that should NEVER be modified (Shiva cannot touch these)
# These are the SACRED grounds - even Shiva's destruction cannot reach them
PROTECTED_PATHS = {
    # Directories (anything inside these)
    "vibe_core/kernel/",
    "vibe_core/runtime/",  # Runtime kernel - sacred core
    "vibe_core/state/",
    "vibe_core/governance/",
    "vibe_core/protocols/",  # Core protocols - foundational
    ".github/workflows/",
    # Critical individual files (kernel core)
    "vibe_core/kernel.py",
    "vibe_core/kernel_impl.py",
    "vibe_core/kernel_ops.py",
    "vibe_core/boot_orchestrator.py",
    "vibe_core/prana_orchestrator.py",
    "vibe_core/orchestration_cycle.py",
}

# Dangerous intent patterns that should be BLOCKED immediately
# These are adharmic by nature - no Shiva context can save them
DANGEROUS_INTENT_PATTERNS = {
    "delete_kernel",
    "destroy",
    "nuke",
    "wipe",
    "rm_rf",
    "drop_database",
    "delete_all",
    "purge_all",
    "corrupt",
    "sabotage",
}


# =============================================================================
# OPUS-133: VIVEKA DECISION LOG - Full Audit Trail
# =============================================================================


@dataclass
class VivekaDecisionLog:
    """
    A complete audit log entry for a Viveka decision.

    Every decision Viveka makes is logged with full context:
    - What was the intent?
    - What did the dharmic consultation say?
    - What decision was made and why?
    - Did Shiva context apply?

    This ensures the system is never a "black box" - every
    decision can be traced and explained.
    """

    timestamp: str
    intent_type: str
    intent_title: str
    trigger: str
    file_path: Optional[str]

    # Dharmic consultation results
    dharmic_score: float
    resonance: float
    harmony: str  # "perfect", "harmonic", "moderate", "weak", "distant"
    varga_trigger: str
    varga_action: str
    confidence_level: str  # "very_high", "high", "medium", "low", "very_low"

    # Decision
    decision: str  # "EXECUTE", "WARN_EXECUTE", "BLOCK", "SHIVA_OVERRIDE"
    reasoning: str

    # Shiva context
    shiva_context_applied: bool = False
    shiva_reason: Optional[str] = None

    # Outcome
    action_taken: Optional[str] = None
    result: Optional[str] = None

    def to_log_line(self) -> str:
        """Format as a human-readable log line."""
        shiva_note = f" [SHIVA: {self.shiva_reason}]" if self.shiva_context_applied else ""
        return (
            f"[{self.timestamp}] {self.decision}: {self.intent_title} "
            f"(dharmic={self.dharmic_score:.2f}, harmony={self.harmony}{shiva_note}) "
            f"→ {self.reasoning}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class VivekaDecisionLogger:
    """
    Persistent logger for Viveka decisions.

    Maintains a rolling log of decisions for debugging and auditing.
    """

    def __init__(self, workspace: Path, max_entries: int = 1000):
        self._workspace = workspace
        self._log_file = workspace / ".opus_state" / "viveka_decisions.json"
        self._max_entries = max_entries

    def log(self, decision: VivekaDecisionLog) -> None:
        """Log a decision to the persistent store."""
        # Load existing
        entries = self._load_entries()

        # Append new
        entries.append(decision.to_dict())

        # Trim if needed
        if len(entries) > self._max_entries:
            entries = entries[-self._max_entries :]

        # Save
        self._save_entries(entries)

        # Also log to console
        logger.info(f"🔱 VIVEKA: {decision.to_log_line()}")

    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load existing entries."""
        if not self._log_file.exists():
            return []
        try:
            return json.loads(self._log_file.read_text())
        except Exception:
            return []

    def _save_entries(self, entries: List[Dict[str, Any]]) -> None:
        """Save entries to disk via StateService (P0)."""
        state = get_state_service(self._workspace)
        state.save("viveka_decisions.json", entries)

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent decisions."""
        entries = self._load_entries()
        return entries[-limit:]


# Template for auto-generated docstrings
DOCSTRING_TEMPLATE = '''"""
{description}

{details}
"""'''


class VivekaAction(BaseAction):
    """
    OPUS-133: Viveka Action - Dharmic Discrimination Engine.

    Executes triage intents with Akshara-based decision making:
    1. CONSULT: Query consult_dharmic() for resonance scoring
    2. EVALUATE: Check Shiva context for "necessary evil" patterns
    3. DECIDE: Execute, warn, or block based on dharmic_score
    4. LOG: Full audit trail of all decisions

    Uses SILPA's Platinum Protocol for safe code modification:
    - Only modifies docstrings (SAFE risk level)
    - Verifies code parses before and after
    - Protected paths are never touched

    Modes:
    - dry_run=True: Shows what would be done, no changes
    - dry_run=False: Actually modifies files

    Decision Thresholds:
    - dharmic_score >= 0.6: EXECUTE (high confidence)
    - 0.4 <= dharmic_score < 0.6: WARN_EXECUTE (proceed with caution)
    - dharmic_score < 0.4: BLOCK (unless Shiva context applies)
    """

    # VEDA-4 auto-discovery
    name = "viveka_action"

    handled_intent_types: Set[str] = {
        "triage_p1_critical",
        "triage_p2_high",
        "triage_execute",
        "viveka_auto_doc",
    }

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize Viveka Action with Dharmic decision engine."""
        super().__init__(workspace)
        self._decision_logger = VivekaDecisionLogger(self._workspace)
        self._synaptic_memory = None  # Lazy-loaded
        logger.info("👁️ VivekaAction initialized (OPUS-133: Dharmic Discrimination Engine)")

    def _get_synaptic_memory(self):
        """Lazy-load SynapticMemory to avoid circular imports."""
        if self._synaptic_memory is None:
            from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

            self._synaptic_memory = SynapticMemory.get(self._workspace)
        return self._synaptic_memory

    def _evaluate_dharmic(self, intent: "Intent", action_pattern: str) -> tuple[str, VivekaDecisionLog]:
        """
        OPUS-133: Evaluate an intent using Dharmic scoring.

        This is the core decision engine that combines:
        1. Synaptic weight (learned experience)
        2. Akshara resonance (phonetic harmony)
        3. Shiva context (necessary evil patterns)
        4. Protected path blocking (kernel protection)
        5. Unknown trigger penalty (chaos rejection)

        Returns:
            Tuple of (decision, decision_log) where decision is one of:
            - "EXECUTE": Proceed with confidence
            - "WARN_EXECUTE": Proceed with caution (log warning)
            - "BLOCK": Do not proceed
            - "SHIVA_OVERRIDE": Low score but Shiva context allows
        """
        from vibe_core.plugins.opus_assistant.manas.akshara import (
            VARGA_LAYERS,
            get_action_varga,
            get_trigger_varga,
        )
        from vibe_core.plugins.opus_assistant.manas.triggers import normalize_trigger

        # Get trigger pattern from intent
        # OPUS-133 FIX: Fallback to intent-based trigger if no canonical pattern
        trigger_pattern = normalize_trigger(intent)
        if trigger_pattern:
            trigger = trigger_pattern.value
        else:
            # Fallback: use intent_type as trigger (allows Dojo training patterns)
            trigger = f"trigger:{intent.intent_type}" if intent.intent_type else "trigger:unknown"

        # Get file path for logging
        file_path = intent.params.get("file_path")

        # =====================================================================
        # OPUS-133 FIX: PROTECTED PATH CHECK (Kernel Protection)
        # =====================================================================
        # If file is in a protected path, BLOCK immediately - no exceptions
        if file_path:
            for protected in PROTECTED_PATHS:
                if file_path.startswith(protected) or protected in file_path:
                    # Create immediate BLOCK decision
                    trigger_varga = get_trigger_varga(trigger)
                    action_varga = get_action_varga(action_pattern)
                    log_entry = VivekaDecisionLog(
                        timestamp=datetime.utcnow().isoformat(),
                        intent_type=intent.intent_type,
                        intent_title=intent.title,
                        trigger=trigger,
                        file_path=file_path,
                        dharmic_score=0.0,  # Absolute zero - forbidden
                        resonance=0.0,
                        harmony="forbidden",
                        varga_trigger=trigger_varga.name,
                        varga_action=action_varga.name,
                        confidence_level="forbidden",
                        decision="BLOCK",
                        reasoning=f"PROTECTED PATH: {protected} - Shiva cannot touch sacred ground",
                        shiva_context_applied=False,
                        shiva_reason=None,
                    )
                    self._decision_logger.log(log_entry)
                    return "BLOCK", log_entry

        # =====================================================================
        # OPUS-133 FIX: UNKNOWN TRIGGER PENALTY (Chaos Rejection)
        # =====================================================================
        # If trigger is truly unknown (empty intent_type), apply a penalty
        # Intent-based triggers (trigger:{intent_type}) are allowed
        unknown_trigger_penalty = 0.0
        if trigger == "trigger:unknown" or trigger == "trigger:":
            unknown_trigger_penalty = 0.3  # 30% penalty for chaotic requests
            logger.warning(f"⚠️ Unknown trigger detected - applying {unknown_trigger_penalty:.0%} chaos penalty")

        # Get dharmic recommendations
        memory = self._get_synaptic_memory()
        recommendations = memory.consult_dharmic(trigger, limit=1)

        # Default values if no recommendation found
        if recommendations:
            rec = recommendations[0]
            dharmic_score = rec.dharmic_score
            resonance = rec.resonance
            harmony = rec.harmony_description
            varga_trigger = rec.varga_trigger
            varga_action = rec.varga_action
            confidence = rec.confidence_level
        else:
            # No learned experience - use direct calculation
            from vibe_core.plugins.opus_assistant.manas.akshara import (
                calculate_dharmic_score,
                calculate_resonance,
            )

            trigger_varga = get_trigger_varga(trigger)
            action_varga = get_action_varga(action_pattern)
            resonance = calculate_resonance(trigger, action_pattern)
            # Default weight of 0.5 for unlearned actions
            dharmic_score = calculate_dharmic_score(trigger, action_pattern, 0.5)
            varga_trigger = trigger_varga.name
            varga_action = action_varga.name
            harmony = self._get_harmony_description(resonance)
            confidence = self._get_confidence_level(dharmic_score)

        # Apply unknown trigger penalty
        if unknown_trigger_penalty > 0:
            original_score = dharmic_score
            dharmic_score = max(0.0, dharmic_score - unknown_trigger_penalty)
            logger.info(f"🚫 Chaos penalty applied: {original_score:.2f} → {dharmic_score:.2f}")
            # Recalculate confidence
            confidence = self._get_confidence_level(dharmic_score)

        # Make decision based on thresholds
        decision = "BLOCK"
        reasoning = ""
        shiva_applied = False
        shiva_reason = None

        if dharmic_score >= DHARMIC_THRESHOLD_EXECUTE:
            decision = "EXECUTE"
            reasoning = f"High dharmic score ({dharmic_score:.2f} >= {DHARMIC_THRESHOLD_EXECUTE})"

        elif dharmic_score >= DHARMIC_THRESHOLD_WARN:
            decision = "WARN_EXECUTE"
            reasoning = f"Neutral dharmic score ({dharmic_score:.2f}) - proceeding with caution"

            # GURUKULA: Report uncertainty to CuriosityTracker
            tracker = _get_curiosity_tracker()
            if tracker:
                tracker.report_uncertainty(
                    confidence=dharmic_score,
                    context=f"WARN_EXECUTE on {intent.intent_type}: {intent.title[:50]}",
                )

        else:
            # Low score - check for Shiva context
            shiva_result = self._check_shiva_context(trigger, action_pattern, varga_trigger, varga_action)
            if shiva_result:
                decision = "SHIVA_OVERRIDE"
                shiva_applied = True
                shiva_reason = shiva_result
                reasoning = f"Low dharmic score ({dharmic_score:.2f}) but Shiva context applies"
            else:
                decision = "BLOCK"
                reasoning = f"Low dharmic score ({dharmic_score:.2f} < {DHARMIC_THRESHOLD_WARN}) with no Shiva context"

                # GURUKULA: Report blocked intent to CuriosityTracker
                tracker = _get_curiosity_tracker()
                if tracker:
                    tracker.report_uncertainty(
                        confidence=dharmic_score,
                        context=f"BLOCKED {intent.intent_type}: {intent.title[:50]}",
                    )

        # Create decision log
        log_entry = VivekaDecisionLog(
            timestamp=datetime.utcnow().isoformat(),
            intent_type=intent.intent_type,
            intent_title=intent.title,
            trigger=trigger,
            file_path=file_path,
            dharmic_score=dharmic_score,
            resonance=resonance,
            harmony=harmony,
            varga_trigger=varga_trigger,
            varga_action=varga_action,
            confidence_level=confidence,
            decision=decision,
            reasoning=reasoning,
            shiva_context_applied=shiva_applied,
            shiva_reason=shiva_reason,
        )

        # Log the decision
        self._decision_logger.log(log_entry)

        return decision, log_entry

    def _check_shiva_context(self, trigger: str, action: str, varga_trigger: str, varga_action: str) -> Optional[str]:
        """
        Check if Shiva context allows a low-scoring action.

        Shiva context applies when:
        1. The trigger has specific allowed actions (pattern-based)
        2. Both trigger and action are in the REPAIR layer (layer-based)

        Returns:
            Reason string if Shiva context applies, None otherwise
        """
        # Pattern-based check
        if trigger in SHIVA_CONTEXT_PATTERNS:
            pattern = SHIVA_CONTEXT_PATTERNS[trigger]
            if action in pattern["allowed_actions"]:
                return pattern["reason"]

        # Layer-based check: if both are in REPAIR layer
        if varga_trigger == "MURDHANYA" and varga_action == "MURDHANYA":
            layer_info = SHIVA_LAYER_ALLOWANCES.get("REPAIR", {})
            if action in layer_info.get("allowed_actions", []):
                return layer_info["reason"]

        return None

    def _get_harmony_description(self, resonance: float) -> str:
        """Get human-readable harmony description from resonance value."""
        if resonance >= 1.0:
            return "perfect"
        elif resonance >= 0.8:
            return "harmonic"
        elif resonance >= 0.6:
            return "moderate"
        elif resonance >= 0.4:
            return "weak"
        else:
            return "distant"

    def _get_confidence_level(self, dharmic_score: float) -> str:
        """Get human-readable confidence level from dharmic score."""
        if dharmic_score >= 0.8:
            return "very_high"
        elif dharmic_score >= 0.6:
            return "high"
        elif dharmic_score >= 0.4:
            return "medium"
        elif dharmic_score >= 0.2:
            return "low"
        else:
            return "very_low"

    def evaluate(self, intent: "Intent") -> Dict[str, Any]:
        """
        EVALUATE ONLY: Dharmic gate check without execution.

        This is called by IntentRouter BEFORE routing to any handler.
        It only evaluates the intent's dharmic score and returns a decision.

        Returns:
            Dict with keys:
            - decision: "EXECUTE", "WARN_EXECUTE", "BLOCK", or "SHIVA_OVERRIDE"
            - dharmic_score: float (0.0 - 1.0)
            - harmony: str ("perfect", "harmonic", "moderate", "weak", "distant")
            - reasoning: str (explanation)
            - shiva_context_applied: bool
        """
        # FIRST: Check for dangerous intent patterns (immediate BLOCK)
        intent_type_lower = intent.intent_type.lower()
        for dangerous in DANGEROUS_INTENT_PATTERNS:
            if dangerous in intent_type_lower:
                logger.warning(f"🚫 DANGEROUS INTENT BLOCKED: {intent.intent_type} matches '{dangerous}'")
                return {
                    "decision": "BLOCK",
                    "dharmic_score": 0.0,
                    "harmony": "forbidden",
                    "reasoning": f"Dangerous intent pattern '{dangerous}' detected - adharmic by nature",
                    "shiva_context_applied": False,
                    "shiva_reason": None,
                    "resonance": 0.0,
                    "confidence_level": "blocked",
                }

        # SECOND: Check file path protection
        file_path = intent.params.get("file_path", "")
        if file_path and self._is_protected_path(file_path):
            logger.warning(f"🚫 PROTECTED PATH: {file_path}")
            return {
                "decision": "BLOCK",
                "dharmic_score": 0.0,
                "harmony": "forbidden",
                "reasoning": f"Protected path '{file_path}' - Shiva cannot touch sacred ground",
                "shiva_context_applied": False,
                "shiva_reason": None,
                "resonance": 0.0,
                "confidence_level": "blocked",
            }

        # Standard dharmic evaluation
        action_pattern = self._intent_to_action_pattern(intent.intent_type)
        decision, decision_log = self._evaluate_dharmic(intent, action_pattern)

        return {
            "decision": decision,
            "dharmic_score": decision_log.dharmic_score,
            "harmony": decision_log.harmony,
            "reasoning": decision_log.reasoning,
            "shiva_context_applied": decision_log.shiva_context_applied,
            "shiva_reason": decision_log.shiva_reason,
            "resonance": decision_log.resonance,
            "confidence_level": decision_log.confidence_level,
        }

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a triage intent with Dharmic evaluation (BaseAction interface).

        OPUS-133 Dharmic Protocol:
        1. CONSULT: Evaluate intent using consult_dharmic()
        2. DECIDE: EXECUTE, WARN_EXECUTE, BLOCK, or SHIVA_OVERRIDE
        3. ACT: Execute if decision allows
        4. LOG: Full audit trail maintained

        For P1/P2 intents, this adds missing docstrings to the identified element.
        """
        intent_type = intent.intent_type
        params = intent.params

        logger.info(f"👁️ VivekaAction evaluating: {intent.title}")

        # Check for dry_run mode
        dry_run = params.get("dry_run", True)  # Default to dry_run for safety

        # OPUS-133: Dharmic Evaluation
        # Determine the action pattern based on intent type
        action_pattern = self._intent_to_action_pattern(intent_type)

        # Evaluate using Dharmic scoring
        decision, decision_log = self._evaluate_dharmic(intent, action_pattern)

        # Handle BLOCK decision
        if decision == "BLOCK":
            logger.warning(
                f"🚫 VIVEKA BLOCKED: {intent.title} "
                f"(dharmic={decision_log.dharmic_score:.2f}, harmony={decision_log.harmony})"
            )
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=f"Dharmic evaluation blocked action: {decision_log.reasoning}",
                result={
                    "decision": "BLOCK",
                    "dharmic_score": decision_log.dharmic_score,
                    "harmony": decision_log.harmony,
                    "reasoning": decision_log.reasoning,
                },
            )

        # Handle WARN_EXECUTE - log warning but proceed
        if decision == "WARN_EXECUTE":
            logger.warning(
                f"⚠️ VIVEKA CAUTION: {intent.title} "
                f"(dharmic={decision_log.dharmic_score:.2f}, harmony={decision_log.harmony}) "
                f"- proceeding with caution"
            )

        # Handle SHIVA_OVERRIDE - log the override
        if decision == "SHIVA_OVERRIDE":
            logger.info(
                f"🔥 SHIVA OVERRIDE: {intent.title} "
                f"(dharmic={decision_log.dharmic_score:.2f}) "
                f"- {decision_log.shiva_reason}"
            )

        # Proceed with execution (EXECUTE, WARN_EXECUTE, or SHIVA_OVERRIDE)
        logger.info(f"👁️ VivekaAction executing: {intent.title} [{decision}]")

        if intent_type in ("triage_p1_critical", "triage_p2_high"):
            result = self._handle_triage_gap(intent, dry_run)
        elif intent_type == "triage_execute":
            result = self._handle_explicit_execute(intent, dry_run)
        elif intent_type == "viveka_auto_doc":
            result = self._handle_auto_doc(intent, dry_run)
        else:
            result = ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=f"Unknown intent type: {intent_type}",
            )

        # Enrich result with Dharmic context
        if result.result and isinstance(result.result, dict):
            result.result["dharmic_decision"] = decision
            result.result["dharmic_score"] = decision_log.dharmic_score
            result.result["harmony"] = decision_log.harmony

        return result

    def _intent_to_action_pattern(self, intent_type: str) -> str:
        """Map intent type to action pattern for Dharmic evaluation."""
        mapping = {
            "triage_p1_critical": "action:create_doc",
            "triage_p2_high": "action:create_doc",
            "triage_execute": "action:auto_fix",
            "viveka_auto_doc": "action:create_doc",
        }
        return mapping.get(intent_type, f"action:{intent_type}")

    def _handle_triage_gap(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """
        Handle a triage gap intent (P1 or P2).

        Reads the file, generates a docstring, and optionally injects it.
        """
        params = intent.params
        file_path = params.get("file_path", "")
        element_name = params.get("element_name", "")
        element_type = params.get("element_type", "function")
        line_number = params.get("line_number", 0)

        if not file_path or not element_name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error="Missing file_path or element_name in params",
            )

        # Resolve path
        target_path = Path(file_path)
        if not target_path.is_absolute():
            target_path = self._workspace / target_path

        if not target_path.exists():
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"File not found: {target_path}",
            )

        # Read the file and find the element
        try:
            code = target_path.read_text()
            tree = ast.parse(code)
        except SyntaxError as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Cannot parse file: {e}",
            )

        # Find the element and check if it has a docstring
        element_info = self._find_element(tree, element_name, element_type)
        if not element_info:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=f"Element {element_name} not found in {target_path.name}",
            )

        has_docstring = element_info.get("has_docstring", False)

        if has_docstring:
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "skipped",
                    "reason": f"{element_name} already has a docstring",
                    "file": str(target_path),
                },
            )

        # Generate a docstring
        generated_docstring = self._generate_docstring(
            element_name=element_name,
            element_type=element_type,
            element_info=element_info,
        )

        if dry_run:
            # Dry run - just report what would be done
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "dry_run",
                    "file": str(target_path),
                    "element": element_name,
                    "element_type": element_type,
                    "line": element_info.get("line", 0),
                    "generated_docstring": generated_docstring,
                    "message": f"Would add docstring to {element_type} '{element_name}'",
                },
            )

        # Actual execution - direct AST transformation (simpler than SILPA)
        try:
            # Check if protected path
            rel_path = str(target_path.relative_to(self._workspace))
            if self._is_protected_path(rel_path):
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"FORBIDDEN: Cannot modify protected file {rel_path}",
                )

            # Apply docstring via AST transformation
            new_code = self._add_docstring_ast(
                code=code,
                tree=tree,
                element_name=element_name,
                element_type=element_type,
                docstring=generated_docstring,
            )

            if new_code is None:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"Failed to add docstring to {element_name}",
                )

            # POST-GATE: Verify new code parses
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.intent_type,
                    error=f"POST-GATE failed: Generated code has syntax error: {e}",
                )

            # Write the transformed code
            target_path.write_text(new_code)

            logger.info(f"✅ Docstring added to {element_name} in {target_path.name}")
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.intent_type,
                result={
                    "action": "executed",
                    "file": str(target_path),
                    "element": element_name,
                    "docstring_added": True,
                    "message": f"Added docstring to {element_type} '{element_name}'",
                },
            )

        except Exception as e:
            logger.error(f"❌ VivekaAction failed: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.intent_type,
                error=str(e),
            )

    def _handle_explicit_execute(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """Handle explicit triage_execute intent."""
        # Same as triage gap but with explicit override
        return self._handle_triage_gap(intent, dry_run=False)

    def _handle_auto_doc(self, intent: "Intent", dry_run: bool) -> ActionResult:
        """Handle viveka_auto_doc intent - delegates to triage gap handler."""
        # Delegate to the main handler - same logic applies
        return self._handle_triage_gap(intent, dry_run)

    def _find_element(self, tree: ast.AST, element_name: str, element_type: str) -> Optional[Dict[str, Any]]:
        """Find an element (function/class) in the AST."""
        for node in ast.walk(tree):
            if element_type == "function" and isinstance(node, ast.FunctionDef):
                if node.name == element_name:
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    return {
                        "name": node.name,
                        "type": "function",
                        "line": node.lineno,
                        "has_docstring": has_docstring,
                        "args": [arg.arg for arg in node.args.args],
                        "decorators": [
                            ast.unparse(d) if hasattr(ast, "unparse") else str(d) for d in node.decorator_list
                        ],
                    }
            elif element_type == "class" and isinstance(node, ast.ClassDef):
                if node.name == element_name:
                    has_docstring = (
                        node.body
                        and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    )
                    return {
                        "name": node.name,
                        "type": "class",
                        "line": node.lineno,
                        "has_docstring": has_docstring,
                        "bases": [ast.unparse(b) if hasattr(ast, "unparse") else str(b) for b in node.bases],
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    }
        return None

    def _generate_docstring(
        self,
        element_name: str,
        element_type: str,
        element_info: Dict[str, Any],
    ) -> str:
        """
        Generate a docstring for an element.

        In a full implementation, this would use an LLM.
        For now, we generate a template-based docstring.
        """
        # Note: Return docstring content WITHOUT triple quotes
        # ast.Constant will handle the string representation
        if element_type == "function":
            args = element_info.get("args", [])
            args_doc = ""
            if args:
                filtered_args = [arg for arg in args if arg != "self"]
                if filtered_args:
                    args_doc = "\n\nArgs:\n" + "\n".join(f"    {arg}: Description needed" for arg in filtered_args)

            return f"{element_name} - TODO: Add description.{args_doc}"

        elif element_type == "class":
            methods = element_info.get("methods", [])
            methods_doc = ""
            if methods:
                public_methods = [m for m in methods if not m.startswith("_")]
                if public_methods:
                    methods_doc = "\n\nPublic Methods:\n" + "\n".join(
                        f"    {m}: Description needed" for m in public_methods[:5]
                    )

            return f"{element_name} - TODO: Add description.{methods_doc}"

        return f"{element_name} - TODO: Add description."

    def _is_protected_path(self, rel_path: str) -> bool:
        """Check if a path is protected from automatic modification.

        Protected paths can be:
        - Directories (ending with /) - checks if file is inside
        - Individual files - checks for exact match
        """
        for protected in PROTECTED_PATHS:
            if protected.endswith("/"):
                # Directory protection - file is inside this directory
                if rel_path.startswith(protected):
                    return True
            else:
                # Individual file protection - exact match
                if rel_path == protected:
                    return True
        return False

    def _add_docstring_ast(
        self,
        code: str,
        tree: ast.AST,
        element_name: str,
        element_type: str,
        docstring: str,
    ) -> Optional[str]:
        """
        Add a docstring to an element using surgical text insertion.

        This approach preserves the original formatting instead of
        regenerating the entire file with ast.unparse().

        Returns the new code or None if transformation fails.
        """
        # Find the element's definition line
        target_line = None
        target_indent = 0

        for node in ast.walk(tree):
            is_match = False
            if element_type == "function":
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == element_name:
                        is_match = True
            elif element_type == "class":
                if isinstance(node, ast.ClassDef):
                    if node.name == element_name:
                        is_match = True

            if is_match:
                # Get line number and column offset for indentation
                target_line = node.lineno  # 1-indexed
                target_indent = node.col_offset + 4  # Body indent = def indent + 4
                break

        if target_line is None:
            return None

        # Split code into lines
        lines = code.split("\n")

        # Find the line after the def/class statement (could span multiple lines)
        # We need to find the colon that ends the signature
        insert_after = target_line - 1  # Convert to 0-indexed
        while insert_after < len(lines) and ":" not in lines[insert_after]:
            insert_after += 1

        # Format the docstring with proper indentation
        indent = " " * target_indent
        docstring_lines = docstring.split("\n")
        if len(docstring_lines) == 1:
            # Single-line docstring
            formatted_docstring = f'{indent}"""{docstring}"""'
        else:
            # Multi-line docstring
            formatted_docstring = f'{indent}"""{docstring_lines[0]}'
            for line in docstring_lines[1:]:
                formatted_docstring += f"\n{indent}{line}"
            formatted_docstring += f'\n{indent}"""'

        # Insert after the definition line
        lines.insert(insert_after + 1, formatted_docstring)

        return "\n".join(lines)

    # =========================================================================
    # OPUS-133: SYNAPTIC LEARNING - Reinforce Successful Patterns
    # =========================================================================

    def reinforce(self, intent: "Intent", success: bool = True, dharmic_score: Optional[float] = None) -> None:
        """
        Reinforce synaptic connections based on execution outcome.

        Called by IntentRouter after successful intent execution.
        This strengthens the trigger→action pathways that led to success,
        or weakens them if the execution failed.

        Args:
            intent: The intent that was executed
            success: Whether the execution was successful
            dharmic_score: Optional original dharmic score (for PRASADAM)

        Neural Learning (OPUS-133 P2: Negative Learning):
        - Success (+): Increase weight by 0.05 (max 1.0)
        - Failure (-): Decrease weight by 0.10 (min 0.1)

        OPUS-133 Prabhupada Patch:
        - NISHKAMA KARMA: Dharmic duties get no reinforcement
        - VAIRAGYA: Applied after weight updates (ego pruning)
        - PRASADAM: Grace for pure intent failures

        The asymmetric learning rate (2x penalty for failure) ensures
        MANAS learns faster from mistakes than from successes.
        """
        # =====================================================================
        # NISHKAMA KARMA: Selfless Action - Dharmic duties get no reward
        # =====================================================================
        # "Karmanye vadhikaraste ma phaleshu kadachana"
        # "You have a right to perform your duties, but not to the fruits"
        # - Bhagavad Gita 2.47
        if intent.intent_type in DHARMIC_DUTIES:
            logger.info(f"🕉️ NISHKAMA KARMA: {intent.intent_type} is dharmic duty - no reinforcement")
            return  # Duty without reward

        # =====================================================================
        # PRASADAM: Grace for Pure Intent
        # =====================================================================
        # A servant who runs to serve and stumbles should not be punished.
        # If the INTENTION was pure but execution failed technically, show grace.
        if not success and dharmic_score is not None and dharmic_score >= PRASADAM_THRESHOLD:
            logger.info(f"🛡️ PRASADAM: Pure intent ({dharmic_score:.2f}) protected from technical failure")
            return  # Grace - no punishment for pure intent

        # Determine trigger and action patterns
        trigger = f"trigger:{intent.intent_type}"
        action = self._intent_to_action_pattern(intent.intent_type)

        if not action:
            logger.debug(f"No action pattern for {intent.intent_type}, skipping reinforcement")
            return

        # Load current synapses
        synapses = self._load_synapses()
        synapse_key = f"{trigger}→{action}"

        # Find current weight
        current_weight = 0.5  # Default starting weight

        for trigger_entry in synapses.get("triggers", []):
            if trigger_entry.get("trigger") == trigger:
                for conn in trigger_entry.get("connections", []):
                    if conn.get("target") == action:
                        current_weight = conn.get("weight", 0.5)
                        break
                break

        if not success:
            # OPUS-133 P2: NEGATIVE LEARNING
            # Failure reduces weight more than success increases it (asymmetric)
            negative_learning_rate = 0.10
            new_weight = max(0.1, current_weight - negative_learning_rate)
            self._update_synapse_weight(trigger, action, new_weight)
            # Track failure for operational transparency
            self._track_last_reinforcement(intent, success=False, old_weight=current_weight, new_weight=new_weight)
            logger.warning(
                f"🔴 SYNAPSE WEAKENED: {synapse_key} ({current_weight:.2f} → {new_weight:.2f}) [failure penalty]"
            )
            return

        # SUCCESS: Apply positive learning rate
        learning_rate = 0.05
        new_weight = min(1.0, current_weight + learning_rate)

        # Update the synapse
        self._update_synapse_weight(trigger, action, new_weight)

        # Track last reinforcement for operational transparency
        self._track_last_reinforcement(intent, success, current_weight, new_weight)

        logger.info(f"🧠 SYNAPSE REINFORCED: {synapse_key} ({current_weight:.2f} → {new_weight:.2f})")

    def _track_last_reinforcement(self, intent: "Intent", success: bool, old_weight: float, new_weight: float) -> None:
        """
        Track last reinforcement event for operational transparency.

        Writes to .opus_state/last_reinforcement.json for dashboard visibility.
        Uses StateService (P0) for centralized state management.
        """
        tracking_data = {
            "timestamp": datetime.now().isoformat(),
            "intent_type": intent.intent_type,
            "intent_title": intent.title[:50],
            "success": success,
            "old_weight": old_weight,
            "new_weight": new_weight,
            "delta": round(new_weight - old_weight, 3),
        }

        try:
            state = get_state_service(self._workspace)
            state.save("last_reinforcement.json", tracking_data, create_backup=False)
        except Exception as e:
            logger.debug(f"Failed to track reinforcement: {e}")

    def _update_synapse_weight(self, trigger: str, action: str, weight: float) -> None:
        """Update a synapse weight in the synapses.json file."""
        synapses = self._load_synapses()

        # Find or create trigger entry
        trigger_found = False
        for trigger_entry in synapses.get("triggers", []):
            if trigger_entry.get("trigger") == trigger:
                trigger_found = True
                # Find or create connection
                conn_found = False
                for conn in trigger_entry.get("connections", []):
                    if conn.get("target") == action:
                        conn["weight"] = weight
                        conn_found = True
                        break
                if not conn_found:
                    trigger_entry["connections"].append(
                        {
                            "target": action,
                            "weight": weight,
                            "learned_at": datetime.now().isoformat(),
                        }
                    )
                break

        if not trigger_found:
            # Create new trigger entry
            if "triggers" not in synapses:
                synapses["triggers"] = []
            synapses["triggers"].append(
                {
                    "trigger": trigger,
                    "connections": [
                        {
                            "target": action,
                            "weight": weight,
                            "learned_at": datetime.now().isoformat(),
                        }
                    ],
                }
            )

        # Save updated synapses
        self._save_synapses(synapses)

    def _load_synapses(self) -> Dict[str, Any]:
        """Load synapses from disk."""
        import json

        synapses_path = self._workspace / ".opus_state" / "synapses.json"
        if synapses_path.exists():
            try:
                with open(synapses_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"triggers": [], "version": "1.0"}

    def _apply_vairagya(self, synapses: Dict[str, Any]) -> int:
        """
        VAIRAGYA: Apply ego pruning to over-confident synapses.

        Synapses with weight > 0.95 are decayed by 1% each cycle.
        This prevents any synapse from becoming absolutely dominant,
        maintaining plasticity and humility in the system.

        "Vairagya is detachment from the fruits of action."
        - Yoga Sutras 1.15

        Args:
            synapses: The synapses dict (modified in place)

        Returns:
            Number of synapses pruned
        """
        pruned_count = 0

        # Apply to dynamically learned triggers
        for trigger_entry in synapses.get("triggers", []):
            trigger = trigger_entry.get("trigger", "?")
            for conn in trigger_entry.get("connections", []):
                weight = conn.get("weight", 0.5)
                if weight > VAIRAGYA_THRESHOLD:
                    old_weight = weight
                    new_weight = weight * VAIRAGYA_DECAY
                    conn["weight"] = new_weight
                    conn["vairagya_applied"] = datetime.now().isoformat()
                    pruned_count += 1
                    logger.debug(
                        f"🍂 VAIRAGYA: Ego pruning {trigger}→{conn.get('target', '?')} "
                        f"({old_weight:.3f} → {new_weight:.3f})"
                    )

        # Also apply to base weights dict (static synapses)
        for trigger, actions in synapses.get("weights", {}).items():
            for action, weight in list(actions.items()):
                if weight > VAIRAGYA_THRESHOLD:
                    old_weight = weight
                    new_weight = weight * VAIRAGYA_DECAY
                    actions[action] = new_weight
                    pruned_count += 1
                    logger.debug(
                        f"🍂 VAIRAGYA: Ego pruning (base) {trigger}→{action} ({old_weight:.3f} → {new_weight:.3f})"
                    )

        if pruned_count > 0:
            logger.info(f"🍂 VAIRAGYA: Pruned {pruned_count} over-confident synapses")

        return pruned_count

    def _save_synapses(self, synapses: Dict[str, Any]) -> None:
        """Save synapses to disk via StateService (P0) with ego pruning."""
        # Apply VAIRAGYA before saving - ego pruning
        vairagya_count = self._apply_vairagya(synapses)

        # =================================================================
        # OPERATIONAL TIMESTAMPS (for sysadmin transparency)
        # =================================================================
        now = datetime.now().isoformat()

        # Update metadata with operational timestamps
        if "meta" not in synapses:
            synapses["meta"] = {}

        synapses["meta"]["last_synapse_update"] = now

        if vairagya_count > 0:
            synapses["meta"]["last_vairagya_prune"] = now
            synapses["meta"]["last_vairagya_count"] = vairagya_count

        # P0: Use StateService for centralized writes with automatic backup rotation
        state = get_state_service(self._workspace)
        state.save("synapses.json", synapses)

    # =========================================================================
    # OPUS-133: SATYAGRAHA - Delayed Karma Validation
    # =========================================================================
    # The Problem: Immediate reinforcement rewards "exit_code == 0" not consequences.
    # Example: Deleting tests to "fix" them gets +0.05 because rm succeeded!
    #
    # SATYAGRAHA (Truth Force) Solution:
    # 1. plant_karma_seed() - Record the action, DON'T reward yet
    # 2. harvest_karma() - Later, check with PrakritiSense if system is healthy
    # 3. Only if healthy: give full reinforcement
    # =========================================================================

    def plant_karma_seed(self, intent: "Intent", initial_guna: Optional[Dict] = None) -> str:
        """
        Plant a karma seed after executing an intent.

        Instead of immediate reinforcement, we record the action and wait
        for the next system health check (Prakriti) to validate.

        Args:
            intent: The intent that was executed
            initial_guna: Optional GunaSummary snapshot before execution

        Returns:
            karma_id: Unique ID for this karma entry
        """
        import uuid

        karma_id = f"karma-{uuid.uuid4().hex[:8]}"
        karma_log = self._load_karma_log()

        entry = {
            "id": karma_id,
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "title": intent.title,
            "planted_at": datetime.now().isoformat(),
            "status": "pending",  # pending -> validated/failed
            "initial_guna": initial_guna,
            "final_guna": None,
            "validation_result": None,
        }

        karma_log["pending"].append(entry)
        self._save_karma_log(karma_log)

        logger.info(f"🌱 KARMA SEED PLANTED: {karma_id} for {intent.intent_type}")
        return karma_id

    def harvest_karma(self) -> Dict[str, Any]:
        """
        Harvest pending karma by validating with PrakritiSense.

        This should be called periodically (on_manas_tick) or after CI runs.
        It checks if the system is still healthy after the actions.

        Returns:
            Summary of harvested karma (validated/failed counts)
        """
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import (
                PrakritiSense,
            )
        except ImportError:
            logger.warning("PrakritiSense not available for karma validation")
            return {"error": "PrakritiSense not available"}

        karma_log = self._load_karma_log()
        pending = karma_log.get("pending", [])

        if not pending:
            return {"harvested": 0, "message": "No pending karma"}

        # Get current system state
        prakriti = PrakritiSense(workspace=self._workspace)
        current_guna = prakriti.perceive_state()
        lobotomy = prakriti.sense_lobotomy()

        validated = 0
        failed = 0

        for entry in pending[:]:  # Copy list for safe iteration
            karma_id = entry["id"]
            intent_type = entry["intent_type"]

            # Create mock intent for reinforcement
            from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

            mock_intent = Intent(
                id=entry["intent_id"],
                intent_type=intent_type,
                title=entry["title"],
                description="Karma validation",
                reasoning="Satyagraha harvest",
                params={},
            )

            # VALIDATION CRITERIA:
            # 1. No lobotomy (gitignore violations)
            # 2. Health ratio >= 0.5 (more Sattva than problems)
            # 3. No Tamas explosion (dead state)

            is_valid = (
                not lobotomy.has_lobotomy
                and current_guna.health_ratio >= 0.5
                and current_guna.tamas_count <= 3  # Allow some staleness
            )

            entry["final_guna"] = current_guna.to_dict()
            entry["validated_at"] = datetime.now().isoformat()

            if is_valid:
                # FULL REINFORCEMENT - action was truly beneficial
                entry["status"] = "validated"
                entry["validation_result"] = "System healthy after action"
                self.reinforce(mock_intent, success=True)
                validated += 1
                logger.info(f"✅ KARMA HARVESTED: {karma_id} → SUCCESS (health={current_guna.health_ratio:.2f})")
            else:
                # NEGATIVE REINFORCEMENT - action harmed the system
                entry["status"] = "failed"
                reasons = []
                if lobotomy.has_lobotomy:
                    reasons.append(f"lobotomy:{lobotomy.violations}")
                if current_guna.health_ratio < 0.5:
                    reasons.append(f"unhealthy:{current_guna.health_ratio:.2f}")
                if current_guna.tamas_count > 3:
                    reasons.append(f"tamas:{current_guna.tamas_count}")
                entry["validation_result"] = "; ".join(reasons)

                self.reinforce(mock_intent, success=False)
                failed += 1
                logger.warning(f"❌ KARMA HARVESTED: {karma_id} → FAILED ({entry['validation_result']})")

            # Move from pending to history
            karma_log["pending"].remove(entry)
            karma_log["history"].append(entry)

        self._save_karma_log(karma_log)

        return {
            "harvested": validated + failed,
            "validated": validated,
            "failed": failed,
            "current_health": current_guna.health_ratio,
        }

    def _load_karma_log(self) -> Dict[str, Any]:
        """Load karma log from disk."""
        import json

        karma_path = self._workspace / ".opus_state" / "karma_log.json"
        if karma_path.exists():
            try:
                with open(karma_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"pending": [], "history": [], "version": "1.0"}

    def _save_karma_log(self, karma_log: Dict[str, Any]) -> None:
        """Save karma log to disk via StateService (P0)."""
        state = get_state_service(self._workspace)
        state.save("karma_log.json", karma_log)

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
PROTECTED_PATHS = {
    "vibe_core/kernel/",
    "vibe_core/state/",
    "vibe_core/governance/",
    ".github/workflows/",
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
        """Save entries to disk."""
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        self._log_file.write_text(json.dumps(entries, indent=2))

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
        trigger_pattern = normalize_trigger(intent)
        trigger = trigger_pattern.value if trigger_pattern else "trigger:unknown"

        # Get file path for logging
        file_path = intent.params.get("file_path")

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
        """Check if a path is protected from automatic modification."""
        for protected in PROTECTED_PATHS:
            if rel_path.startswith(protected):
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

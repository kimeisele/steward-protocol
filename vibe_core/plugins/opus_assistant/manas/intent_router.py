"""
OPUS-065: DHARMA-JNANA Intent Router (THIN ORCHESTRATOR)

OPUS-171 Phase 5: Refactored to Thin Orchestrator Pattern

Routes approved intents to the appropriate handler for execution.
Handler logic extracted to manas/router/handlers/*_handler.py

This is the MISSING LINK that connects:
    analyzers/ (detect) → cognitive_kernel (manage) → cortex/ (execute)

Architecture (OPUS-171 Phase 5 - Agent-First Design):
    ┌─────────────────────────────────────────────────────────────────────┐
    │                    IntentRouter (THIN ORCHESTRATOR)                  │
    ├─────────────────────────────────────────────────────────────────────┤
    │  ROUTING ORDER:                                                      │
    │  1. AKASHA perception (knowledge context)                            │
    │  2. SIDDHI check (auto-approve perfected patterns)                   │
    │  3. MAYA simulation (dream layer safety)                             │
    │  4. VIVEKA gate (dharmic discrimination)                             │
    │  5. tool_registry (SYNAPTIC BRIDGE - SAFE/LOW risk)                  │
    │  6. ActionLoader (VEDA-4 auto-discovered actions)                    │
    │  7. HandlerLoader (OPUS-171 extracted handlers) ← MAIN PATH          │
    └─────────────────────────────────────────────────────────────────────┘

Handler Location (OPUS-171 Phase 5):
    vibe_core/plugins/opus_assistant/manas/router/handlers/
    ├── base.py              # BaseHandler + AgentType constants
    ├── sutra_handler.py     # Documentation (update_readme, document_manas)
    ├── shell_handler.py     # Git/Shell (commit, push, pr, cleanup)
    ├── research_handler.py  # Research/Knowledge (web_search, knowledge_query)
    ├── audit_handler.py     # Dharma/Wiring/Sankalpa (audit, strategy)
    ├── test_handler.py      # Test/Silpa (run_tests, genesis_tests)
    └── harness_handler.py   # Harness/Coverage/Triage (harness_*, coverage_*)

VAJRA Compliance:
    - All routes are logged
    - Failed routes don't crash the system
    - Unknown intents are safely queued for manual handling
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.loaders import ActionLoader, ToolLoader

from vibe_core.state.schema import ExecutionResult


@dataclass
class RouteResult:
    """
    Result of a routing decision in the IntentRouter.

    This represents the outcome of routing an intent to a handler,
    including success status, the handler that executed it, and the result data.

    Attributes:
        success: Whether the route/execution was successful
        handler: Name of the handler that executed the intent
        result: Dictionary containing the execution result data
        error: Optional error message if execution failed
    """

    success: bool
    handler: str
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


from .intent_generator import Intent, IntentRisk
from .router import get_handler_for_intent, list_handlers
from .router.handlers import BaseHandler
from .validator import SrutiValidator

# OPUS-112: Tool dispatch imports
try:
    from vibe_core.tools.tool_protocol import ToolCall
except ImportError:
    ToolCall = None  # type: ignore

# P0: StateService for centralized state management
from vibe_core.state import get_state_service

# OPUS-133: VivekaAction - Dharmic Gate (Synaptic Learning)
try:
    from .cortex.viveka_action import VivekaAction

    VIVEKA_AVAILABLE = True
except ImportError:
    VIVEKA_AVAILABLE = False
    VivekaAction = None  # type: ignore

# OPUS-155: MayaSimulator - The Dream Layer (Inception)
try:
    from .maya_simulator import MayaSimulator, SimulationResult

    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    MayaSimulator = None  # type: ignore
    SimulationResult = None  # type: ignore

# OPUS-171 Phase 4: AkashaSense - Knowledge Graph Perception
try:
    from .cortex.akasha_sense import AkashaSense

    AKASHA_AVAILABLE = True
except ImportError:
    AKASHA_AVAILABLE = False
    AkashaSense = None  # type: ignore

logger = logging.getLogger("MANAS.IntentRouter")

# OPUS-075: HIL Bridge state directory
HIL_STATE_DIR = ".opus_state"
PENDING_INTENTS_FILE = "pending_intents.json"
KARMA_LOG_FILE = "karma_log.json"


class IntentRouter:
    """
    Routes intents to appropriate cortex modules for execution.

    PRATYAYA (Verification):
        - Only routes intents with known handlers
        - Unknown intents return safely with error
        - All routes logged for audit

    KARMA (Action):
        - Calls cortex module with intent params
        - Returns structured result
        - Never crashes, always returns ExecutionResult

    FRACTAL PATTERN (OPUS-106):
        - Accepts scoped ActionLoader for isolated action discovery
        - Falls back to global ActionLoader if not provided
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        action_loader: Optional["ActionLoader"] = None,
        tool_loader: Optional["ToolLoader"] = None,
    ):
        """
        Initialize the router with optional workspace path and scoped loaders.

        FRACTAL PATTERN (OPUS-106):
            action_loader: Scoped ActionLoader instance for isolated action discovery.
                           If None, falls back to global ActionLoader.
            tool_loader: Scoped ToolLoader instance for dynamic tool access.
                         If None, falls back to hardcoded imports (legacy).
        """
        self._workspace = workspace or Path.cwd()
        self._kernel: Optional["RealVibeKernel"] = None
        self._validator = SrutiValidator(workspace=self._workspace)  # OPUS-069
        self._register_handlers()  # OPUS-171: Now just logs available handlers

        # OPUS-106: Scoped loaders for fractal pattern
        self._action_loader = action_loader
        self._tool_loader = tool_loader

        # OPUS-133: VivekaAction - Dharmic Gate (Synaptic Learning)
        self._viveka: Optional[VivekaAction] = None
        if VIVEKA_AVAILABLE:
            self._viveka = VivekaAction(workspace=self._workspace)
            logger.info("🧠 OPUS-133: VivekaAction gate initialized (Dharmic Discrimination)")

        # OPUS-155: MayaSimulator - The Dream Layer (Inception)
        self._maya: Optional[MayaSimulator] = None
        if MAYA_AVAILABLE:
            self._maya = MayaSimulator(workspace=self._workspace, current_depth=0)
            logger.info("🌙 OPUS-155: MayaSimulator initialized (Inception Depth 0)")

        # OPUS-171 Phase 4: AkashaSense - Knowledge Graph Perception
        self._akasha: Optional[AkashaSense] = None
        if AKASHA_AVAILABLE:
            self._akasha = AkashaSense(workspace=self._workspace)
            logger.info("👁️ OPUS-171: AkashaSense initialized (Knowledge Perception)")

        # OPUS-220: SynapticMemory - Samskara (Experience-Based Routing)
        self._synaptic: Optional[Any] = None
        try:
            from .triggers import SynapticMemory

            self._synaptic = SynapticMemory.get(workspace=self._workspace)
            logger.info("🧠 OPUS-220: SynapticMemory initialized (Samskara Recall)")
        except ImportError:
            logger.debug("OPUS-220: SynapticMemory not available - using static routing only")

        # OPUS-075: Load MANAS fortress config
        self._manas_config = self._load_manas_config()
        self._autonomous_steps = 0  # Track steps for safety limit

    def _load_manas_config(self) -> Dict[str, Any]:
        """Load MANAS config from config/opus.yaml."""
        import yaml

        config_path = self._workspace / "config" / "opus.yaml"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    data = yaml.safe_load(f)
                    return data.get("manas", {})
            except Exception as e:
                logger.warning(f"Failed to load MANAS config: {e}")
        return {
            "mode": "manual",
            "auto_execute_threshold": 0.85,
            "protected_zones": [],
            "max_autonomous_steps": 10,
        }

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        ⚡ VAJRA: Inject kernel for ledger access.

        OPUS-069: Also injects into SrutiValidator for SRUTI validation.
        """
        self._kernel = kernel
        # OPUS-069: Wire validator to kernel for ledger access
        self._validator.inject_kernel(kernel)
        logger.info("⚡ IntentRouter: Kernel injected (+ SrutiValidator bound)")

    # =========================================================================
    # OPUS-171 Phase 4: SIDDHI - Perfected Pattern Auto-Decisions
    # =========================================================================

    def _check_siddhi(self, intent: Intent) -> Optional[Dict[str, Any]]:
        """
        Check if intent matches a Siddhi pattern (auto-approve).

        Siddhi (Sanskrit: "Perfection") is achieved when a mantra reaches
        108 successful repetitions. Siddhi patterns bypass Viveka gate
        for instant execution.

        Args:
            intent: The intent to check

        Returns:
            Dict with mantra info if Siddhi match, None otherwise
        """
        try:
            from vibe_core.state.sanskrit_matrix import infer_layer

            # Load Sanskrit Matrix from state
            state = get_state_service(self._workspace, plugin_id="opus_assistant")
            matrix_path = self._workspace / ".opus_state" / "sanskrit_matrix.json"

            if not matrix_path.exists():
                return None

            matrix = json.loads(matrix_path.read_text())
            mantras = matrix.get("mantras", [])

            if not mantras:
                return None

            # Determine intent layer
            intent_layer = infer_layer(intent.intent_type)

            # Look for Siddhi match (layer + EXECUTE decision)
            for mantra in mantras:
                if not mantra.get("siddhi"):
                    continue  # Not yet perfected

                # Match by layer and EXECUTE decision
                if mantra.get("layer") == intent_layer and mantra.get("decision") == "EXECUTE":
                    logger.info(
                        f"🕉️ SIDDHI MATCH: {intent.intent_type} "
                        f"(mantra={mantra.get('signature')}, meaning={mantra.get('meaning')})"
                    )
                    return {
                        "signature": mantra.get("signature"),
                        "layer": intent_layer,
                        "decision": "EXECUTE",
                        "meaning": mantra.get("meaning"),
                        "repetitions": mantra.get("repetitions", 108),
                        "siddhi": True,
                    }

            return None

        except Exception as e:
            logger.debug(f"Siddhi check failed: {e}")
            return None

    def _check_samskara(self, intent: Intent) -> Optional[Dict[str, Any]]:
        """
        OPUS-220: Check Synaptic Memory for experienced handlers.

        Samskara (Sanskrit: "Impression") means the system consults its
        learned associations to recommend the best handler based on past success.

        This is the "Fast Path" - if we've done this 80%+ successfully with
        a specific handler, use that handler directly instead of going through
        full routing.

        Args:
            intent: The intent to check

        Returns:
            Dict with recommended handler and confidence, or None if no strong recommendation
        """
        if not self._synaptic:
            return None

        try:
            # Construct trigger for this intent type
            # "How did we handle this intent type in the past?"
            trigger = f"trigger:{intent.intent_type}"

            # Consult synaptic memory
            recommendations = self._synaptic.consult(trigger, min_weight=0.0, limit=5)

            if not recommendations:
                logger.debug(f"🧠 SAMSKARA: No recommendations for {trigger}")
                return None

            # Get top recommendation
            top_rec = recommendations[0]
            confidence = top_rec.weight

            # CONFIDENCE THRESHOLD: Only use Samskara if confidence > 0.70
            # Below 70% is "uncertain" - fall back to normal routing
            if confidence < 0.70:
                logger.debug(
                    f"🧠 SAMSKARA: {trigger} has low confidence ({confidence:.2f}) - using normal routing instead"
                )
                return None

            # Extract handler name from action
            # Actions are like "action:shell_handler" or "action:audit_handler"
            action = top_rec.action
            handler_name = action.replace("action:", "").replace("_handler", "")

            logger.debug(f"🧠 SAMSKARA: Top recommendation for {trigger}: {handler_name} (confidence={confidence:.2f})")

            return {
                "recommended_handler": handler_name,
                "confidence": confidence,
                "trigger": trigger,
                "all_recommendations": [{"action": r.action, "weight": r.weight} for r in recommendations],
            }

        except Exception as e:
            logger.debug(f"🧠 SAMSKARA: Recall failed: {e}")
            return None

    def _register_handlers(self) -> None:
        """
        OPUS-171 Phase 5: Initialize Handler infrastructure.

        THIN ORCHESTRATOR PATTERN:
        - Handler logic moved to manas/router/handlers/*_handler.py
        - HandlerLoader auto-discovers handlers at runtime
        - This method just logs the available handlers

        ROUTING ORDER:
        1. tool_registry (SYNAPTIC BRIDGE - SAFE/LOW risk)
        2. ActionLoader (VEDA-4 auto-discovered actions)
        3. HandlerLoader (OPUS-171 extracted handlers) ← NEW
        4. Prefix matching fallback
        """
        # List available handlers from HandlerLoader
        handler_names = list_handlers(workspace=self._workspace)
        logger.info(f"IntentRouter: {len(handler_names)} handlers available via HandlerLoader: {handler_names}")

    # =========================================================================
    # OPUS-075: MANAS 6D FORTRESS - Prefrontal Cortex
    # =========================================================================

    def gate(self, intent: Intent) -> Dict[str, Any]:
        """
        OPUS-075: The Prefrontal Cortex - decides whether to execute or ask.

        Returns:
            {"status": "execute"} - OK to auto-execute
            {"status": "ask_user", "reason": ...} - Need human approval
            {"status": "blocked", "reason": ...} - Denied (protected zone)
        """
        mode = self._manas_config.get("mode", "manual")
        threshold = self._manas_config.get("auto_execute_threshold", 0.85)
        protected_zones = self._manas_config.get("protected_zones", [])
        max_steps = self._manas_config.get("max_autonomous_steps", 10)

        # Get confidence from intent (default 0.5 if not set)
        confidence = getattr(intent, "confidence", 0.5)
        targets = getattr(intent, "targets", [])

        # 1. Protected Zone Check (Nuclear Safety)
        for target in targets:
            for zone in protected_zones:
                if zone in str(target):
                    logger.warning(f"🛡️ BLOCKED: Target {target} is Protected Zone")
                    return {"status": "blocked", "reason": "protected_zone", "target": str(target)}

        # 2. Mode Check
        if mode == "manual":
            return {"status": "ask_user", "reason": "manual_mode"}

        # 3. Step Limit Check
        if self._autonomous_steps >= max_steps:
            logger.warning(f"✋ LIMIT: {self._autonomous_steps} autonomous steps reached")
            return {"status": "ask_user", "reason": "step_limit_reached"}

        # 4. Confidence Check (The Singularity Gate)
        if confidence >= threshold:
            logger.info(f"⚡ AUTO-EXECUTE: Confidence {confidence:.2f} >= {threshold}")
            self._autonomous_steps += 1
            return {"status": "execute", "confidence": confidence}
        else:
            logger.info(f"✋ HESITATION: Confidence {confidence:.2f} < {threshold}")
            return {"status": "ask_user", "reason": "low_confidence", "confidence": confidence}

    def reset_autonomous_steps(self) -> None:
        """Reset the autonomous step counter (call on session start)."""
        self._autonomous_steps = 0

    # =========================================================================
    # OPUS-075: HIL BRIDGE - Human-In-The-Loop Persistence
    # =========================================================================

    def _get_state_dir(self) -> Path:
        """Get or create the HIL state directory."""
        state_dir = self._workspace / HIL_STATE_DIR
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    def _load_pending_intents(self) -> Dict[str, Dict[str, Any]]:
        """Load pending intents from JSON file."""
        pending_file = self._get_state_dir() / PENDING_INTENTS_FILE
        if pending_file.exists():
            try:
                return json.loads(pending_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to load pending intents: {e}")
        return {}

    def _save_pending_intents(self, pending: Dict[str, Dict[str, Any]]) -> None:
        """Save pending intents to JSON file via StateService (P0)."""
        try:
            state = get_state_service(self._workspace, plugin_id="opus_assistant")
            state.save(PENDING_INTENTS_FILE, pending, create_backup=False)
        except Exception as e:
            logger.error(f"Failed to save pending intents: {e}")

    def queue_intent(self, intent: Intent, gate_result: Dict[str, Any]) -> str:
        """
        OPUS-075: Queue an intent for human approval.

        Called when gate() returns ask_user - stores the intent for later approval.

        Returns:
            The intent ID (for reference in approve command)
        """
        pending = self._load_pending_intents()

        # Serialize intent for storage
        intent_data = {
            "id": intent.id,
            "intent_type": intent.intent_type,
            "title": intent.title,
            "params": intent.params,
            "confidence": getattr(intent, "confidence", 0.5),
            "targets": getattr(intent, "targets", []),
            "gate_reason": gate_result.get("reason", "unknown"),
            "queued_at": datetime.now().isoformat(),
            "status": "pending",
        }

        pending[intent.id] = intent_data
        self._save_pending_intents(pending)

        logger.info(f"📥 Intent queued for approval: {intent.id} ({intent.title})")
        return intent.id

    def list_pending_intents(self) -> List[Dict[str, Any]]:
        """
        OPUS-075: List all pending intents awaiting approval.

        Returns:
            List of pending intent dictionaries
        """
        pending = self._load_pending_intents()
        return [v for v in pending.values() if v.get("status") == "pending"]

    async def approve_intent(self, intent_id: str) -> ExecutionResult:
        """
        OPUS-075: Approve and execute a pending intent.

        Args:
            intent_id: The ID of the intent to approve

        Returns:
            ExecutionResult from executing the intent
        """
        pending = self._load_pending_intents()

        if intent_id not in pending:
            logger.warning(f"Intent not found: {intent_id}")
            return ExecutionResult(
                success=False,
                executed_by="HIL_BRIDGE",
                result={},
                error=f"Intent not found: {intent_id}",
            )

        intent_data = pending[intent_id]

        if intent_data.get("status") != "pending":
            return ExecutionResult(
                success=False,
                executed_by="HIL_BRIDGE",
                result={},
                error=f"Intent already processed: {intent_data.get('status')}",
            )

        # Reconstruct Intent object
        intent = Intent(
            id=intent_data["id"],
            intent_type=intent_data["intent_type"],
            title=intent_data["title"],
            description=intent_data.get("description", intent_data["title"]),
            reasoning=intent_data.get("reasoning", "Approved via HIL Bridge"),
            params=intent_data.get("params", {}),
        )
        # Restore optional attributes
        if "confidence" in intent_data:
            intent.confidence = intent_data["confidence"]
        if "targets" in intent_data:
            intent.targets = intent_data["targets"]

        logger.info(f"✅ Approving intent: {intent_id} ({intent.title})")

        # Execute via Envoy (The Hand)
        # OPUS-078: Clean Architecture - Gehirn (Manas) delegates to Hände (Envoy)
        if self._kernel and hasattr(self._kernel, "envoy"):
            logger.info("🕵️ Delegating to Envoy for execution...")
            envoy_result = self._kernel.envoy.execute_mission(intent)

            # Map Envoy result to ExecutionResult
            result = ExecutionResult(
                success=envoy_result.get("status") == "success",
                executed_by=envoy_result.get("executed_by", "Envoy"),
                result=envoy_result,
                error=envoy_result.get("error"),
            )
        else:
            # Fallback if kernel/envoy isn't ready (shouldn't happen in full boot)
            logger.warning("⚠️ Envoy not found on kernel - falling back to direct routing")
            result = await self.route(intent)

        # Update status and record karma
        intent_data["status"] = "approved"
        intent_data["approved_at"] = datetime.now().isoformat()
        intent_data["result_success"] = result.success
        pending[intent_id] = intent_data
        self._save_pending_intents(pending)

        # Record karma feedback
        self._record_karma(intent, result.success)

        return result

    def reject_intent(self, intent_id: str, reason: str = "") -> bool:
        """
        OPUS-075: Reject a pending intent.

        Args:
            intent_id: The ID of the intent to reject
            reason: Optional reason for rejection

        Returns:
            True if rejected successfully
        """
        pending = self._load_pending_intents()

        if intent_id not in pending:
            logger.warning(f"Intent not found: {intent_id}")
            return False

        intent_data = pending[intent_id]
        intent_data["status"] = "rejected"
        intent_data["rejected_at"] = datetime.now().isoformat()
        intent_data["rejection_reason"] = reason
        pending[intent_id] = intent_data
        self._save_pending_intents(pending)

        # Record negative karma
        intent = Intent(
            id=intent_data["id"],
            intent_type=intent_data["intent_type"],
            title=intent_data["title"],
            description=intent_data.get("description", intent_data["title"]),
            reasoning=intent_data.get("reasoning", "Rejected via HIL Bridge"),
            params=intent_data.get("params", {}),
        )
        self._record_karma(intent, success=False, rejected=True)

        logger.info(f"❌ Rejected intent: {intent_id}")
        return True

    def _record_karma(self, intent: Intent, success: bool, rejected: bool = False) -> None:
        """
        OPUS-075: Record karma feedback for learning via StateService (P0).

        Karma is used to adjust future confidence thresholds and improve
        MANAS's judgment over time.
        """
        karma_config = self._manas_config.get("karma", {})
        if not karma_config.get("enabled", True):
            return

        # P0: Use StateService for centralized state
        state = get_state_service(self._workspace, plugin_id="opus_assistant")
        karma_log = state.load(KARMA_LOG_FILE, default=[])

        # Calculate karma score
        if rejected:
            score = -karma_config.get("failure_weight", 2.0)
        elif success:
            score = karma_config.get("success_weight", 1.0)
        else:
            score = -karma_config.get("failure_weight", 2.0)

        entry = {
            "timestamp": datetime.now().isoformat(),
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "confidence": getattr(intent, "confidence", 0.5),
            "outcome": "rejected" if rejected else ("success" if success else "failure"),
            "karma_score": score,
        }
        karma_log.append(entry)

        # Keep only last 100 entries
        karma_log = karma_log[-100:]

        try:
            state.save(KARMA_LOG_FILE, karma_log, create_backup=False)
        except Exception as e:
            logger.warning(f"Failed to save karma log: {e}")

    def get_karma_summary(self) -> Dict[str, Any]:
        """
        OPUS-075: Get karma summary for dashboard display.

        Returns:
            Dictionary with karma statistics
        """
        karma_file = self._get_state_dir() / KARMA_LOG_FILE
        if not karma_file.exists():
            return {"total_karma": 0, "entries": 0, "success_rate": 0.0}

        try:
            karma_log = json.loads(karma_file.read_text())
            total_karma = sum(e.get("karma_score", 0) for e in karma_log)
            successes = sum(1 for e in karma_log if e.get("outcome") == "success")
            total = len(karma_log)

            return {
                "total_karma": total_karma,
                "entries": total,
                "success_rate": (successes / total * 100) if total > 0 else 0.0,
                "recent": karma_log[-5:] if karma_log else [],
            }
        except Exception:
            return {"total_karma": 0, "entries": 0, "success_rate": 0.0}

    # =========================================================================
    # OPUS-101: HYBRID ROUTER - ActionLoader Integration
    # =========================================================================

    def _try_action_loader(self, intent: Intent) -> Optional[ExecutionResult]:
        """
        OPUS-101: Try to route via ActionLoader (VEDA-4 auto-discovery).

        OPUS-106: FRACTAL PATTERN
        - Uses scoped loader if injected (private brain)
        - Falls back to global ActionLoader (shared brain)

        Returns:
            ExecutionResult if action found and executed, None to fall back to legacy
        """
        try:
            # OPUS-106: Fractal Pattern - Use scoped loader if available
            if self._action_loader is not None:
                action = self._action_loader.get_for_intent(intent.intent_type)
                loader_name = f"ActionLoader[{self._action_loader.scope}]"
            else:
                # Fall back to global/static loader
                from vibe_core.loaders import ActionLoader

                action = ActionLoader.get_action_for_intent(intent.intent_type, workspace=self._workspace)
                loader_name = "ActionLoader[global]"

            if action is None:
                logger.debug(f"[HYBRID] {loader_name}: no handler for {intent.intent_type}")
                return None

            logger.info(f"⚡ [HYBRID] {loader_name} routing {intent.intent_type} -> {action.name}")

            # Execute via the action's act() method
            action_result = action.act(intent)

            # Validate output against Sruti (Ledger)
            result_dict = {
                "success": action_result.success,
                "handler": action_result.action_name,
                "action_result": action_result.result,
                "error": action_result.error,
                **(action_result.metadata or {}),
            }

            validation = self._validator.validate_intent_output(result_dict)
            if not validation.valid:
                logger.warning(f"⚠️ SRUTI VIOLATION: {validation.errors}")
                result_dict["sruti_validation"] = validation.to_dict()
            elif validation.warnings:
                logger.info(f"📝 SRUTI: {validation.warnings}")
                result_dict["sruti_validation"] = validation.to_dict()

            return ExecutionResult(
                success=action_result.success,
                executed_by=f"{loader_name}/{action_result.action_name}",
                result=result_dict,
                error=action_result.error,
            )

        except Exception as e:
            logger.error(f"❌ [HYBRID] ActionLoader failed: {e}")
            # Don't crash - fall back to legacy
            return None

    # =========================================================================
    # OPUS-112: SYNAPTIC BRIDGE - Direct Tool Dispatch
    # =========================================================================

    def _try_tool_dispatch(self, intent: Intent) -> Optional[ExecutionResult]:
        """
        OPUS-112: Try to dispatch via kernel.tool_registry (SYSTEM ACT mode).

        This is the SYNAPTIC BRIDGE - MANAS can directly execute tools
        registered in the kernel's tool registry (envoy.*, chronicle.*, etc.)

        POLICY (Dharma Decision):
        - IntentRisk.SAFE → Direct dispatch allowed (SYSTEM ACT)
        - IntentRisk.LOW → Direct dispatch allowed (SYSTEM ACT)
        - IntentRisk.MEDIUM/HIGH → Should go through ENVOY (USER ACT)

        Returns:
            ExecutionResult if tool found and executed, None to fall back
        """
        # 1. Check if kernel is available
        if self._kernel is None:
            return None

        # 2. Check if tool_registry is available
        tool_registry = getattr(self._kernel, "tool_registry", None)
        if tool_registry is None:
            return None

        # 3. DHARMA POLICY: Only allow direct dispatch for SAFE/LOW risk intents
        if intent.risk not in (IntentRisk.SAFE, IntentRisk.LOW):
            logger.info(
                f"🛡️ [DHARMA] Intent {intent.intent_type} is {intent.risk.value} risk - "
                f"skipping direct dispatch (should use ENVOY)"
            )
            return None

        # 4. Check if intent has an action_id that matches a tool
        action_id = intent.params.get("action_id") or intent.intent_type
        tool = tool_registry.get(action_id)

        if tool is None:
            # No matching tool in registry
            return None

        # 5. Execute via tool registry (SYSTEM ACT mode)
        logger.info(f"⚡ [SYNAPTIC] Direct dispatch: {action_id} (SYSTEM ACT)")

        try:
            if ToolCall is None:
                logger.warning("⚠️ ToolCall not available - cannot dispatch")
                return None

            call = ToolCall(
                tool_name=action_id,
                parameters=intent.params,
                caller_agent_id="manas",  # MANAS as system actor
            )

            result = tool_registry.execute(call)

            # 6. Log SYSTEM ACT to journal
            self._log_system_act(intent, action_id, result)

            return ExecutionResult(
                success=result.success,
                executed_by=f"tool_registry/{action_id}",
                result={
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                    "mode": "SYSTEM_ACT",
                },
                error=result.error,
            )

        except Exception as e:
            logger.error(f"❌ [SYNAPTIC] Tool dispatch failed: {e}")
            return None

    def _log_system_act(self, intent: Intent, tool_name: str, result: Any) -> None:
        """
        Log SYSTEM ACT to journal (system_journal.jsonl).

        OPUS-112: When MANAS executes a tool directly, it must be logged
        as SYSTEM ACT (not User Command) for audit trail.
        Uses StateService (P0) for centralized JSONL append.
        """
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "SYSTEM_ACT",
                "actor": "manas",
                "intent_id": intent.id,
                "intent_type": intent.intent_type,
                "tool": tool_name,
                "success": getattr(result, "success", False),
                "risk": intent.risk.value if hasattr(intent.risk, "value") else str(intent.risk),
            }

            # P0: Use StateService for JSONL append
            state = get_state_service(self._workspace, plugin_id="opus_assistant")
            state.append("system_journal.jsonl", entry)

            logger.debug(f"📜 SYSTEM ACT logged: {tool_name}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to log SYSTEM ACT: {e}")

    async def route(self, intent: Intent) -> ExecutionResult:
        """
        Route an intent to the appropriate cortex module.

        OPUS-112 HYBRID ROUTER STRATEGY:
        1. Try kernel.tool_registry (SYSTEM ACT - SAFE/LOW risk only)
        2. Try ActionLoader (VEDA-4 auto-discovered actions)
        3. Fall back to legacy handlers if not found
        4. Final fallback to prefix matching

        Args:
            intent: The intent to route

        Returns:
            ExecutionResult with success status and execution result
        """
        intent_type = intent.intent_type
        logger.info(f"🔀 Routing intent: {intent_type} ({intent.id})")

        # =====================================================================
        # OPUS-171 Phase 4: AKASHA PERCEPTION - Knowledge Context (FIRST)
        # =====================================================================
        # "Before Manas thinks, Akasha feels the vibrations of knowledge."
        # Query knowledge graph for context about this intent type
        akasha_context: Optional[Dict[str, Any]] = None
        if self._akasha:
            try:
                # Perceive with focus on the intent type
                perception = self._akasha.perceive(context={"focus": intent_type})
                akasha_context = perception.to_context_dict()

                if perception.is_loaded and perception.node_count > 0:
                    logger.debug(
                        f"👁️ AKASHA: {perception.summary} "
                        f"(nodes={perception.node_count}, related={len(perception.related_nodes)})"
                    )

                    # If we have knowledge about this domain, enrich intent params
                    if perception.related_nodes:
                        intent.params["akasha_related"] = perception.related_nodes[:5]
                    if perception.constraints:
                        intent.params["akasha_constraints"] = perception.constraints[:3]

            except Exception as e:
                logger.debug(f"👁️ AKASHA perception failed: {e}")

        # =====================================================================
        # OPUS-171 Phase 4: SIDDHI CHECK - Perfected Patterns (BEFORE Maya/Viveka)
        # =====================================================================
        # If intent matches a Siddhi pattern (108+ repetitions), auto-approve
        # This bypasses both Maya simulation and Viveka evaluation
        siddhi_result = self._check_siddhi(intent)
        if siddhi_result:
            # Mark for SIDDHI auto-execute (skip Viveka, proceed with confidence)
            intent.params["siddhi_approved"] = True
            intent.params["siddhi_mantra"] = siddhi_result.get("signature")
            logger.info(
                f"🕉️ SIDDHI AUTO-APPROVE: {intent.title} "
                f"(mantra={siddhi_result.get('signature')}, layer={siddhi_result.get('layer')})"
            )
            # Create synthetic viveka_result for reinforcement
            viveka_result = {
                "decision": "SIDDHI",
                "dharmic_score": 1.0,  # Perfect score for Siddhi
                "harmony": "siddhi",
                "reasoning": f"Siddhi mantra: {siddhi_result.get('meaning')}",
                "siddhi": True,
            }
            # Skip Maya and Viveka gates - proceed directly to dispatch

        # =====================================================================
        # OPUS-155: MAYA SIMULATION - Dream before acting (BEFORE Viveka)
        # =====================================================================
        # Skip Maya if Siddhi approved
        if self._maya and not siddhi_result:
            # Convert Intent to dict for Maya (it expects dict, not Intent object)
            intent_dict = {
                "id": intent.id,
                "intent_type": intent.intent_type,
                "title": intent.title,
                "risk": intent.risk.value if hasattr(intent.risk, "value") else str(intent.risk),
                "params": intent.params,
            }

            simulation = self._maya.simulate(intent_dict)

            if not simulation.safe:
                # Maya blocked - the dream showed harm
                logger.warning(
                    f"🌙 MAYA BLOCKED: {intent.title} "
                    f"(depth={simulation.depth}, score={simulation.score:.2f}, "
                    f"reason={simulation.reason})"
                )
                return ExecutionResult(
                    success=False,
                    executed_by="MAYA",
                    result=simulation.to_dict(),
                    error=f"Simulation blocked: {simulation.reason}",
                )
            else:
                logger.debug(f"✅ MAYA PASSED: {intent.title} (depth={simulation.depth}, score={simulation.score:.2f})")

        # =====================================================================
        # OPUS-133: VIVEKA GATE - Dharmic Discrimination (BEFORE any dispatch)
        # =====================================================================
        # Skip Viveka if Siddhi approved (viveka_result already set above)
        if self._viveka and not siddhi_result:
            viveka_result = self._viveka.evaluate(intent)
            decision = viveka_result.get("decision", "EXECUTE")

            if decision == "BLOCK":
                # Sacred ground or low dharmic score - reject immediately
                logger.warning(
                    f"🚫 VIVEKA BLOCKED: {intent.title} "
                    f"(score={viveka_result.get('dharmic_score', 0):.2f}, "
                    f"harmony={viveka_result.get('harmony', 'unknown')})"
                )
                return ExecutionResult(
                    success=False,
                    executed_by="VIVEKA",
                    result=viveka_result,
                    error=f"Dharmic gate blocked: {viveka_result.get('reasoning', 'Low dharmic score')}",
                )
            elif decision == "WARN_EXECUTE":
                # Proceed with caution - log but continue
                logger.info(
                    f"⚠️ VIVEKA WARN: {intent.title} - proceeding with caution "
                    f"(score={viveka_result.get('dharmic_score', 0):.2f})"
                )
            elif decision in ("EXECUTE", "SHIVA_OVERRIDE"):
                # Good dharmic score or Shiva context - proceed
                logger.debug(f"✅ VIVEKA: {decision} for {intent.title}")

        # =====================================================================
        # OPUS-220: SAMSKARA RECALL - Experience-Based Routing (AFTER Viveka)
        # =====================================================================
        # "The Samskara is the seed that remembers the past and guides the future."
        # Consult synaptic memory for experience with this intent type
        samskara_result = self._check_samskara(intent)
        if samskara_result:
            logger.info(
                f"🧠 SAMSKARA RECALL: {intent.intent_type} "
                f"(recommended={samskara_result['recommended_handler']}, "
                f"confidence={samskara_result['confidence']:.2f})"
            )
            # Store for use in handler selection
            intent.params["samskara_recommended_handler"] = samskara_result["recommended_handler"]
            intent.params["samskara_confidence"] = samskara_result["confidence"]

        # OPUS-112: Try kernel.tool_registry FIRST (SYNAPTIC BRIDGE)
        # Only for SAFE/LOW risk intents (SYSTEM ACT mode)
        tool_result = self._try_tool_dispatch(intent)
        if tool_result is not None:
            return tool_result

        # OPUS-101: Try ActionLoader (VEDA-4 auto-discovery)
        action_result = self._try_action_loader(intent)
        if action_result is not None:
            return action_result

        # =====================================================================
        # OPUS-171 Phase 5: HandlerLoader (THIN ORCHESTRATOR PATTERN)
        # =====================================================================
        # Handler logic extracted to manas/router/handlers/*_handler.py
        # HandlerLoader auto-discovers and routes to appropriate handler
        handler: Optional[BaseHandler] = get_handler_for_intent(intent_type, workspace=self._workspace)

        if handler is None:
            logger.warning(f"⚠️ No handler for intent type: {intent_type}")
            return ExecutionResult(
                success=False,
                executed_by="none",
                result={},
                error=f"No handler registered for intent type: {intent_type}",
            )

        # Execute via handler.handle() - the extracted handler logic
        try:
            # Inject kernel if handler needs it
            handler.inject_kernel(self._kernel)

            result = handler.handle(intent)

            # OPUS-069: Validate output against Sruti (Ledger)
            validation = self._validator.validate_intent_output(result)
            if not validation.valid:
                logger.warning(f"⚠️ SRUTI VIOLATION: {validation.errors}")
                result["sruti_validation"] = validation.to_dict()
            elif validation.warnings:
                logger.info(f"📝 SRUTI: {validation.warnings}")
                result["sruti_validation"] = validation.to_dict()

            # OPUS-133: Synaptic feedback - reinforce patterns with PRASADAM
            success = result.get("success", True)
            if self._viveka:
                # Get dharmic score for PRASADAM (grace for pure intent failures)
                dharmic_score = viveka_result.get("dharmic_score", 0.5) if viveka_result else 0.5
                self._viveka.reinforce(intent, success=success, dharmic_score=dharmic_score)
                logger.debug(f"🧠 Synapse feedback: {intent.intent_type} (success={success})")

            return ExecutionResult(
                success=success,
                executed_by=result.get("handler", handler.name),
                result=result,
            )
        except Exception as e:
            logger.error(f"❌ Handler failed for {intent_type}: {e}")
            return ExecutionResult(
                success=False,
                executed_by="error",
                result={},
                error=str(e),
            )


def create_execution_callback(
    workspace: Optional[Path] = None,
    kernel: Optional["RealVibeKernel"] = None,
    action_loader: Optional["ActionLoader"] = None,
    tool_loader: Optional["ToolLoader"] = None,
) -> Callable[[Intent], Dict[str, Any]]:
    """
    Factory function to create an execution callback for CognitiveKernel.

    OPUS-106: Now accepts optional loaders for fractal pattern.

    Usage:
        callback = create_execution_callback(
            workspace, kernel,
            action_loader=kernel.action_loader,
            tool_loader=kernel.tool_loader
        )
        cognitive_kernel.set_execution_callback(callback)
    """
    router = IntentRouter(
        workspace=workspace,
        action_loader=action_loader,
        tool_loader=tool_loader,
    )
    if kernel:
        router.inject_kernel(kernel)

    async def callback(intent: Intent) -> Dict[str, Any]:
        result = await router.route(intent)
        return {
            "success": result.success,
            "handler": result.executed_by,
            "error": result.error,
            **result.result,
        }

    return callback

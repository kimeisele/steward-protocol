"""
OPUS-167: ActionManager (Karmendriya) - The Action Organs

Sanskrit: Karmendriya = Organs of Action (hands, feet, speech, etc.)

"karmaṇy evādhikāras te mā phaleṣu kadācana"
- You have the right to action, never to its fruits.
(Bhagavad Gita 2.47)

The ActionManager is the OUTPUT side of the Antahkarana:
- SenseManager (Jnanendriya) → INPUT  → Manas
- ActionManager (Karmendriya) → OUTPUT ← Manas

RESPONSIBILITIES:
1. Execute intents (route to correct handler)
2. Check Dharma Gate before execution
3. Record to Ledger (VAJRA)
4. Update Synaptic weights (learning)
5. Track execution history

ARCHITECTURE:
    ┌─────────────────────────────────────────┐
    │              MANAS (Kernel)             │
    │         (Decision/Orchestration)        │
    └──────────────────┬──────────────────────┘
                       │ _act(intent)
                       ▼
    ┌─────────────────────────────────────────┐
    │           ACTION MANAGER                │
    │         (Karmendriya Bridge)            │
    │                                         │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
    │  │ Dharma  │  │ Execute │  │ Record  │ │
    │  │  Gate   │→ │ Handler │→ │ Ledger  │ │
    │  └─────────┘  └─────────┘  └─────────┘ │
    │                    │                    │
    │                    ▼                    │
    │            ┌─────────────┐              │
    │            │  Synaptic   │              │
    │            │  Learning   │              │
    │            └─────────────┘              │
    └─────────────────────────────────────────┘
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .cortex.dharma_sense import DharmaSense
    from .intent_buffer import IntentBufferEntry
    from .intent_generator import Intent
    from .memory_store import MemoryStore
    from .triggers import SynapticMemory

logger = logging.getLogger("MANAS.ActionManager")


@dataclass
class ExecutionResult:
    """Result of intent execution."""

    success: bool
    result: Dict[str, Any]
    execution_time_ms: int = 0
    blocked_reason: Optional[str] = None


class ActionManager:
    """
    OPUS-167: The Karmendriya (Action Organs) of MANAS.

    Handles all intent execution, including:
    - Dharma Gate checking (ethical filter)
    - Routing to correct handler
    - Ledger recording (VAJRA)
    - Synaptic learning updates

    Usage:
        manager = ActionManager(
            workspace=Path.cwd(),
            dharma_sense=dharma_sense,
            memory=memory_store,
            synaptic=synaptic_memory,
        )

        # Execute an intent
        success = manager.execute(entry, ledger=ledger, vibe_kernel=kernel)
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        dharma_sense: Optional["DharmaSense"] = None,
        memory: Optional["MemoryStore"] = None,
        synaptic: Optional["SynapticMemory"] = None,
        prakriti_sense: Optional[Any] = None,
    ):
        """
        Initialize ActionManager.

        Args:
            workspace: Workspace root path
            dharma_sense: DharmaSense for ethical checks
            memory: MemoryStore for outcome recording
            synaptic: SynapticMemory for learning
            prakriti_sense: PrakritiSense for healing
        """
        self._workspace = workspace or Path.cwd()
        self._dharma = dharma_sense
        self._memory = memory
        self._synaptic = synaptic
        self._prakriti = prakriti_sense

        # Execution callback (for custom handlers)
        self._execution_callback: Optional[Callable] = None

        # Narasimha guardian (injected later)
        self._narasimha: Optional[Any] = None

        logger.debug("🖐️ ACTION MANAGER: Karmendriya initialized")

    def inject_dharma(self, sense: "DharmaSense") -> None:
        """Inject DharmaSense for ethical checks."""
        self._dharma = sense

    def inject_narasimha(self, narasimha: Any) -> None:
        """Inject Narasimha for technical guardian checks."""
        self._narasimha = narasimha

    def inject_prakriti(self, sense: Any) -> None:
        """Inject PrakritiSense for healing."""
        self._prakriti = sense

    def inject_memory(self, memory: "MemoryStore") -> None:
        """Inject MemoryStore for outcome recording."""
        self._memory = memory

    def inject_synaptic(self, synaptic: "SynapticMemory") -> None:
        """Inject SynapticMemory for learning."""
        self._synaptic = synaptic

    def set_execution_callback(self, callback: Callable) -> None:
        """Set custom execution callback."""
        self._execution_callback = callback

    # =========================================================================
    # MAIN EXECUTION ENTRY POINT
    # =========================================================================

    def execute(
        self,
        entry: "IntentBufferEntry",
        ledger: Optional[Any] = None,
        vibe_kernel: Optional[Any] = None,
        buffer: Optional[Any] = None,
        activity_callback: Optional[Callable] = None,
    ) -> bool:
        """
        Execute an approved intent.

        OPUS-057 VAJRA: All executions are recorded to the ledger.

        Args:
            entry: The intent buffer entry to execute
            ledger: Ledger for recording (optional)
            vibe_kernel: VibeKernel for ledger fallback (optional)
            buffer: IntentBuffer for saving (optional)
            activity_callback: Callback to record activity

        Returns:
            True if execution succeeded
        """
        intent = entry.intent
        logger.info(f"🖐️ ACTION: Executing intent: {intent.title}")

        start_time = datetime.utcnow()
        success = False
        result = {}

        # Reset idle timer on execution
        if activity_callback:
            activity_callback()

        # Record INTENT_EXECUTING to ledger BEFORE execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTING",
            intent=intent,
            extra_data={"timestamp": start_time.isoformat()},
            ledger=ledger,
            vibe_kernel=vibe_kernel,
        )

        # DHARMA GATE: Check ethical alignment before execution
        dharma_permitted, dharma_reason = self._check_dharma_gate(intent)
        if not dharma_permitted:
            logger.warning(f"🙏 DHARMA GATE BLOCKED: {intent.title}")
            entry.status = "blocked_adharmic"
            entry.execution_result = {"error": f"BLOCKED BY DHARMA GATE: {dharma_reason}"}
            self._record_to_ledger(
                event_type="MANAS_INTENT_BLOCKED_ADHARMIC",
                intent=intent,
                extra_data={"reason": dharma_reason},
                ledger=ledger,
                vibe_kernel=vibe_kernel,
            )
            if buffer:
                buffer.save()
            return False

        try:
            # Route to appropriate handler
            result, success = self._route_execution(intent)

        except Exception as e:
            logger.error(f"Intent execution failed: {e}")
            result = {"error": str(e)}
            success = False

        # Update entry
        entry.status = "executed" if success else "failed"
        entry.executed_at = datetime.utcnow().isoformat()
        entry.execution_result = result

        # Calculate execution time
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Record to ledger AFTER execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTED" if success else "MANAS_INTENT_FAILED",
            intent=intent,
            extra_data={
                "execution_time_ms": execution_time,
                "result": result,
                "outcome": "success" if success else "failed",
            },
            ledger=ledger,
            vibe_kernel=vibe_kernel,
        )

        # Record in memory (MANAS internal)
        if self._memory:
            self._memory.record_intent_outcome(
                intent_type=intent.intent_type,
                description=intent.title,
                outcome="success" if success else "failed",
                context=intent.params,
                feedback=result.get("error"),
                execution_time_ms=execution_time,
            )

        # Synaptic Learning - Update weights based on outcome
        self._update_synapses(intent, success)

        if buffer:
            buffer.save()

        if success:
            # Record success to increase Bhakti
            self._on_dharma_success(intent)
            logger.info(f"🖐️ ACTION: Intent {intent.id} executed successfully")
        else:
            logger.warning(f"🖐️ ACTION: Intent {intent.id} execution failed: {result.get('error')}")

        return success

    # =========================================================================
    # DHARMA GATE
    # =========================================================================

    def _check_dharma_gate(self, intent: "Intent") -> Tuple[bool, str]:
        """
        Check Dharma Gate before intent execution.

        This is the ethical conscience check. Even if NARASIMHA (technical guardian)
        approves, DHARMA SENSE (ethical conscience) must also approve.

        "An efficient mind without dharma makes efficient catastrophes."

        Args:
            intent: The intent to check

        Returns:
            (is_permitted, reason)
        """
        if not self._dharma:
            # No conscience = permissive (legacy mode)
            return True, "Dharma Sense not available - defaulting to permissive"

        try:
            verdict = self._dharma.check_dharmic_alignment(intent, agent_id="manas")

            if verdict.is_dharmic:
                logger.debug(f"🙏 DHARMA GATE: PASSED - {verdict.reason}")
                return True, verdict.reason
            else:
                logger.warning(
                    f"🙏 DHARMA GATE: BLOCKED - {intent.intent_type} - "
                    f"Missing: {verdict.missing_permissions}, Bhakti: {verdict.agent_bhakti}"
                )
                return False, verdict.reason

        except Exception as e:
            logger.warning(f"🙏 DHARMA GATE: Check failed: {e}")
            # On error, default to permissive (don't block due to bugs)
            return True, f"Dharma check error: {e}"

    def _on_dharma_success(self, intent: "Intent") -> None:
        """Record successful dharmic action - increases Bhakti."""
        if self._dharma:
            try:
                self._dharma.on_intent_success(intent)
            except Exception as e:
                logger.debug(f"🙏 DHARMA SENSE: Could not record success: {e}")

    # =========================================================================
    # EXECUTION ROUTING
    # =========================================================================

    def _route_execution(self, intent: "Intent") -> Tuple[Dict[str, Any], bool]:
        """
        Route intent to the correct handler.

        Args:
            intent: The intent to execute

        Returns:
            (result_dict, success_bool)
        """
        # 1. Healing intents
        if intent.intent_type in ("heal_system_state", "fix_lobotomy"):
            result = self._execute_healing(intent)
            return result, result.get("success", False)

        # 2. Memory review (dreaming)
        if intent.intent_type == "memory_review":
            result = self._execute_memory_review(intent)
            return result, result.get("success", False)

        # 3. Custom callback
        if self._execution_callback:
            result = self._execution_callback(intent)
            return result, result.get("success", False)

        # 4. Circuit execution
        if intent.circuit_to_execute:
            logger.info(f"🖐️ ACTION: Executing circuit: {intent.circuit_to_execute}")
            try:
                from .circuit_executor import CognitiveCircuitExecutor

                executor = CognitiveCircuitExecutor(workspace=self._workspace)
                result = executor.execute_circuit(intent.circuit_to_execute)
                return result, result.get("success", False)
            except ImportError:
                logger.warning("CognitiveCircuitExecutor not available")
                return {"error": "CircuitExecutor not available"}, False
            except Exception as exec_err:
                logger.error(f"Circuit execution failed: {exec_err}")
                return {"error": str(exec_err)}, False

        # 5. IntentRouter fallback
        try:
            from .intent_router import IntentRouter

            router = IntentRouter(workspace=self._workspace)
            if intent.intent_type in router._handlers:
                logger.info(f"🔀 ACTION: Routing via IntentRouter: {intent.intent_type}")
                result = router.route(intent)
                return result, result.get("success", False)
            else:
                logger.warning(f"No execution method for intent: {intent.id}")
                return {"error": "No execution method available"}, False
        except ImportError:
            logger.warning(f"IntentRouter not available for: {intent.id}")
            return {"error": "No execution method available"}, False
        except Exception as router_err:
            logger.error(f"IntentRouter failed: {router_err}")
            return {"error": str(router_err)}, False

    # =========================================================================
    # SPECIALIZED HANDLERS
    # =========================================================================

    def _execute_healing(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute a healing intent via PrakritiSense.

        Args:
            intent: The healing intent to execute

        Returns:
            Execution result
        """
        if not self._prakriti:
            return {"success": False, "error": "PrakritiSense not available"}

        try:
            if intent.intent_type == "heal_system_state":
                paths = intent.params.get("paths", [])
                healed = 0
                for path_str in paths:
                    path = Path(path_str)
                    new_guna = self._prakriti.heal(path)
                    if new_guna.value in ("sattva", "rajas"):
                        healed += 1

                return {
                    "success": True,
                    "healed_count": healed,
                    "total_paths": len(paths),
                }

            elif intent.intent_type == "fix_lobotomy":
                # Lobotomy fix is more complex - for now just report
                return {
                    "success": False,
                    "error": "Lobotomy fix requires manual .gitignore edit",
                    "violations": intent.params.get("violations", []),
                }

            else:
                return {"success": False, "error": f"Unknown healing intent type: {intent.intent_type}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _execute_memory_review(self, intent: "Intent") -> Dict[str, Any]:
        """
        Execute Dreaming: Consolidate wisdom from past actions.

        OPUS-089: Shiva/Sankalpa Memory Review
        Triggered by Sankalpa during idle times (The Void).
        This closes the cognitive loop: Experience → Wisdom.
        """
        logger.info("🌙 ACTION: Entering Dream State (Memory Review)...")

        if not self._memory:
            return {"success": False, "error": "MemoryStore not available"}

        try:
            # 1. Extract successful patterns (What works?)
            successful_patterns = self._memory.get_successful_patterns(limit=5)

            # 2. Extract failure patterns (What to avoid?)
            failure_counts: Dict[str, int] = {}
            for mem in self._memory.get_all_memories():
                if mem.outcome == "failed":
                    failure_counts[mem.intent_type] = failure_counts.get(mem.intent_type, 0) + 1

            # Sort by failure count
            failure_patterns = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:5]

            # 3. Wisdom Synthesis
            insights = []

            if successful_patterns:
                for pattern in successful_patterns:
                    success_rate = self._memory.get_success_rate(pattern)
                    insights.append({"type": pattern, "success_rate": success_rate, "status": "trusted"})

            if failure_patterns:
                for pattern, count in failure_patterns:
                    insights.append({"type": pattern, "failure_count": count, "status": "avoid"})

            # 4. Record dream summary to memory (meta-learning)
            self._memory.record_intent_outcome(
                intent_type="memory_review",
                description="Dream cycle completed",
                outcome="success",
                context={
                    "successful_patterns": successful_patterns,
                    "failure_patterns": [p[0] for p in failure_patterns],
                    "insights_count": len(insights),
                },
            )

            logger.info(f"🌙 ACTION: Dream complete. {len(insights)} insights consolidated.")

            return {
                "success": True,
                "insights": insights,
                "successful_patterns": successful_patterns,
                "failure_patterns": [{"type": p[0], "count": p[1]} for p in failure_patterns],
                "wisdom": "Patterns consolidated into memory",
            }

        except Exception as e:
            logger.error(f"❌ Nightmare (Dream failed): {e}")
            return {"success": False, "error": str(e)}

    # =========================================================================
    # LEDGER RECORDING (VAJRA)
    # =========================================================================

    def _record_to_ledger(
        self,
        event_type: str,
        intent: "Intent",
        extra_data: Optional[Dict[str, Any]] = None,
        ledger: Optional[Any] = None,
        vibe_kernel: Optional[Any] = None,
    ) -> Optional[str]:
        """
        Record an intent event to the core ledger.

        OPUS-057 VAJRA: Cryptographic binding of all MANAS actions.

        Args:
            event_type: Type of event (INTENT_PROPOSED, INTENT_EXECUTED, etc.)
            intent: The intent being recorded
            extra_data: Additional data to include
            ledger: Direct ledger reference
            vibe_kernel: VibeKernel for ledger fallback

        Returns:
            Event ID if recorded, None if no ledger available
        """
        # Get ledger from params or vibe_kernel
        active_ledger = ledger
        if not active_ledger and vibe_kernel:
            active_ledger = vibe_kernel.ledger

        if not active_ledger:
            logger.debug("⚠️ VAJRA: No ledger - intent not ledgered (shadow mode)")
            return None

        # Build intent hash for integrity
        intent_data = {
            "id": intent.id,
            "type": intent.intent_type,
            "title": intent.title,
            "risk": intent.risk.value,
            "priority": intent.priority.value,
            "params": intent.params,
        }
        intent_hash = hashlib.sha256(json.dumps(intent_data, sort_keys=True).encode()).hexdigest()[:16]

        details = {
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "intent_title": intent.title,
            "intent_hash": intent_hash,
            "priority": intent.priority.value,
            "risk": intent.risk.value,
            "circuit": intent.circuit_to_execute,
        }

        if extra_data:
            details.update(extra_data)

        try:
            event_id = active_ledger.record(event_type, details)
            logger.debug(f"⚡ VAJRA: Recorded {event_type} to ledger ({event_id})")
            return event_id
        except Exception as e:
            logger.warning(f"⚡ VAJRA: Could not record to ledger: {e}")
            return None

    # =========================================================================
    # SYNAPTIC LEARNING
    # =========================================================================

    def _update_synapses(self, intent: "Intent", success: bool) -> None:
        """
        Update synaptic weights based on intent execution outcome.

        OPUS-110: The Learning Loop - MANAS strengthens connections that work,
        weakens connections that fail.

        Weight adjustment:
        - Success: weight += 0.1 * (1 - weight)  [asymptotic to 1.0]
        - Failure: weight -= 0.1 * weight        [asymptotic to 0.0]

        This is Hebbian learning: "Neurons that fire together wire together."

        Args:
            intent: The intent that was executed
            success: Whether execution succeeded
        """
        if not self._synaptic:
            return

        try:
            # Extract the trigger (what caused this intent)
            trigger = self._extract_trigger(intent)
            if not trigger:
                return

            # The connection is: trigger → intent_type
            connection_key = f"{trigger}→{intent.intent_type}"

            # Update weight
            self._synaptic.update_weight(
                connection_key=connection_key,
                success=success,
                intent_type=intent.intent_type,
                trigger=trigger,
            )

            if success:
                logger.debug(f"🧠 SYNAPSE: Strengthened {connection_key}")
            else:
                logger.debug(f"🧠 SYNAPSE: Weakened {connection_key}")

        except Exception as e:
            logger.debug(f"🧠 SYNAPSE: Update failed: {e}")

    def _extract_trigger(self, intent: "Intent") -> Optional[str]:
        """
        Extract the trigger source from an intent.

        Used for synaptic learning - what caused this intent?

        Args:
            intent: The intent to analyze

        Returns:
            Trigger identifier or None
        """
        # Check reasoning for source hints
        reasoning = intent.reasoning.lower() if intent.reasoning else ""

        if "prakriti" in reasoning or "state" in reasoning:
            return "prakriti_sense"
        if "dharma" in reasoning:
            return "dharma_sense"
        if "sutra" in reasoning or "doc" in reasoning:
            return "sutra_sense"
        if "sankalpa" in reasoning:
            return "sankalpa"
        if "shruta" in reasoning or "filesystem" in reasoning:
            return "shruta_sense"
        if "prana" in reasoning or "presence" in reasoning:
            return "prana_sense"
        if "memory" in reasoning:
            return "memory_review"

        # Check params for sense source
        if intent.params:
            source = intent.params.get("source") or intent.params.get("sense")
            if source:
                return str(source)

        # Default to intent type prefix
        parts = intent.intent_type.split("_")
        if len(parts) > 1:
            return parts[0]

        return None


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ActionManager",
    "ExecutionResult",
]

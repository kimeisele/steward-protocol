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
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional, Tuple

if TYPE_CHECKING:
    from vibe_core.task_kernel import TaskKernelResult

    from .cortex.dharma_sense import DharmaSense
    from .intent_buffer import IntentBufferEntry
    from .intent_generator import Intent
    from .memory_store import MemoryStore
    from .triggers import SynapticMemory

logger = logging.getLogger("MANAS.ActionManager")


# =============================================================================
# OPUS-175: TOOL SELECTOR - Intent to Tools Mapping
# =============================================================================


class ToolSelector:
    """
    OPUS-175: Select tools for TaskKernel based on intent type.

    "Need to Know" principle - TaskKernel only gets tools it needs.

    This is the Perception layer for action execution:
    - "If intent is 'file edit', inject 'FileTools'."
    - "If intent is 'search', inject 'SearchTools'."

    Usage:
        selector = ToolSelector(tool_registry)
        tools = selector.select_for_intent(intent)
        kernel = TaskKernel.spawn(task, tools=tools, ...)
    """

    # Intent type → Required tool names mapping
    INTENT_TOOL_MAP = {
        # File operations
        "file_create": ["write_file"],
        "file_edit": ["read_file", "write_file"],
        "file_read": ["read_file"],
        "file_delete": ["write_file"],
        # Directory operations
        "dir_list": ["list_directory"],
        "dir_create": ["write_file"],
        # Search operations
        "search_file": ["search_file", "read_file"],
        "search_content": ["search_file"],
        # Task operations (meta)
        "add_task": ["add_task"],
        "list_tasks": ["list_tasks"],
        "complete_task": ["complete_task"],
        # Generic code operations
        "code_analyze": ["read_file", "search_file"],
        "code_refactor": ["read_file", "write_file"],
        "test_create": ["read_file", "write_file"],
        "test_run": [],  # Uses Bash, not tools
        # Inspection
        "inspect_result": ["inspect_result"],
        # Delegate to other agent
        "delegate": ["delegate"],
        # Default for unknown - read-only
        "default": ["read_file", "list_directory"],
    }

    def __init__(self, tool_registry: "Any" = None):
        """
        Initialize ToolSelector.

        Args:
            tool_registry: Optional ToolRegistry for tool lookup.
                          If None, returns tool names only.
        """
        self._registry = tool_registry

    def select_for_intent(self, intent: "Intent") -> list:
        """
        Select tools needed for an intent.

        Args:
            intent: The intent to select tools for

        Returns:
            List of Tool instances (if registry available) or tool names
        """
        intent_type = intent.intent_type

        # 1. Check explicit mapping
        tool_names = self.INTENT_TOOL_MAP.get(intent_type)

        # 2. Try prefix matching if not found
        if tool_names is None:
            for key in self.INTENT_TOOL_MAP:
                if intent_type.startswith(key):
                    tool_names = self.INTENT_TOOL_MAP[key]
                    break

        # 3. Fall back to default
        if tool_names is None:
            tool_names = self.INTENT_TOOL_MAP["default"]

        # 4. If no registry, return names only
        if not self._registry:
            return tool_names

        # 5. Resolve to actual Tool instances
        tools = []
        for name in tool_names:
            tool = self._registry.get(name)
            if tool:
                tools.append(tool)
            else:
                logger.debug(f"Tool '{name}' not found in registry")

        return tools

    def get_required_tools(self, intent_type: str) -> list:
        """Get tool names required for an intent type."""
        return self.INTENT_TOOL_MAP.get(intent_type, self.INTENT_TOOL_MAP["default"])


from vibe_core.state.schema import ExecutionResult


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

        # OPUS-175: ToolSelector and registry for TaskKernel spawning
        self._tool_registry: Optional[Any] = None
        self._tool_selector = ToolSelector()

        # OPUS-175: TaskKernel execution mode (False = legacy, True = TaskKernel)
        self._use_task_kernel: bool = True

        logger.debug("🖐️ ACTION MANAGER: Karmendriya initialized (with TaskKernel support)")

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

    def inject_tool_registry(self, registry: Any) -> None:
        """
        OPUS-175: Inject ToolRegistry for TaskKernel spawning.

        Args:
            registry: ToolRegistry instance from kernel
        """
        self._tool_registry = registry
        self._tool_selector = ToolSelector(registry)
        logger.debug("🖐️ ACTION MANAGER: ToolRegistry injected for TaskKernel")

    def enable_task_kernel(self, enabled: bool = True) -> None:
        """
        OPUS-175: Enable/disable TaskKernel execution mode.

        When enabled, tool-based intents are executed via TaskKernel
        instead of legacy handlers.

        Args:
            enabled: True to use TaskKernel, False for legacy mode
        """
        self._use_task_kernel = enabled
        mode = "TaskKernel" if enabled else "legacy"
        logger.info(f"🖐️ ACTION MANAGER: Execution mode set to {mode}")

    # =========================================================================
    # MAIN EXECUTION ENTRY POINT
    # =========================================================================

    async def execute(
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
            result, success = await self._route_execution(intent)

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

        # OPUS-211: Emit ACTION_COMPLETED event for closed-loop feedback
        await self._emit_action_completed(intent, success, result, execution_time)

        if buffer:
            buffer.save()

        if success:
            # Record success to increase Bhakti
            self._on_dharma_success(intent)
            logger.info(f"🖐️ ACTION: Intent {intent.id} executed successfully")
        else:
            logger.warning(f"🖐️ ACTION: Intent {intent.id} execution failed: {result.get('error')}")
            # TITIKSHA: Resilience through self-diagnosis
            # When an intent fails, the system auto-generates a diagnostic intent
            self._schedule_failure_diagnosis(intent, result, buffer)

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

    async def _route_execution(self, intent: "Intent") -> Tuple[Dict[str, Any], bool]:
        """
        Route intent to the correct handler.

        Args:
            intent: The intent to execute

        Returns:
            (result_dict, success_bool)
        """
        # 1. Healing intents
        if intent.intent_type in ("heal_system_state", "fix_lobotomy"):
            result = await self._execute_healing(intent)
            return result, result.get("success", False)

        # 2. Memory review (dreaming)
        if intent.intent_type == "memory_review":
            result = await self._execute_memory_review(intent)
            return result, result.get("success", False)

        # 3. OPUS-175: TaskKernel execution for tool-based intents
        if self._use_task_kernel and self._tool_registry:
            result = await self._execute_via_task_kernel(intent)
            if result.get("executed_via_task_kernel"):
                return result, result.get("success", False)
            # If TaskKernel couldn't handle it, fall through to other handlers

        # 4. Custom callback
        if self._execution_callback:
            # Custom callbacks are assumed to be sync for now, but we can wrap them
            import asyncio

            if asyncio.iscoroutinefunction(self._execution_callback):
                result = await self._execution_callback(intent)
            else:
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
            logger.info(f"🔀 ACTION: Routing via IntentRouter: {intent.intent_type}")
            result = await router.route(intent)
            # IntentRouter.route returns ExecutionResult, but we need (dict, bool)
            if hasattr(result, "success"):
                return {
                    "success": result.success,
                    "handler": result.executed_by,
                    "result": result.result,
                    "error": result.error,
                }, result.success
            return result, result.get("success", False)
        except ImportError:
            logger.warning(f"IntentRouter not available for: {intent.id}")
            return {"error": "No execution method available"}, False
        except Exception as router_err:
            logger.error(f"IntentRouter failed: {router_err}")
            return {"error": str(router_err)}, False

    # =========================================================================
    # SPECIALIZED HANDLERS
    # =========================================================================

    async def _execute_healing(self, intent: "Intent") -> Dict[str, Any]:
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

    async def _execute_memory_review(self, intent: "Intent") -> Dict[str, Any]:
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
    # OPUS-175: TASKKERNEL EXECUTION
    # =========================================================================

    async def _execute_via_task_kernel(self, intent: "Intent") -> Dict[str, Any]:
        """
        OPUS-175: Execute intent via TaskKernel (lightweight ephemeral kernel).

        This is the new execution path for tool-based intents.
        TaskKernel provides isolation and synaptic reinforcement.

        Args:
            intent: The intent to execute

        Returns:
            Execution result with 'executed_via_task_kernel' flag
        """
        # 1. Select tools for this intent
        tools = self._tool_selector.select_for_intent(intent)

        if not tools:
            # No tools selected - fall through to other handlers
            return {"executed_via_task_kernel": False}

        logger.info(f"⚡ TaskKernel: Spawning for intent {intent.id} with {len(tools)} tools")

        try:
            # 2. Convert Intent → ManagedTask
            from vibe_core.task_management.models import Task as ManagedTask

            managed_task = ManagedTask(
                id=intent.id,
                title=intent.title,
                description=intent.reasoning or "",
                priority=intent.priority.value if hasattr(intent.priority, "value") else 0,
                metadata={
                    "intent_type": intent.intent_type,
                    "action": intent.intent_type,
                    "context": intent.params or {},
                    "tool_call": intent.params.get("tool_call") if intent.params else None,
                },
            )

            # 3. Create synaptic reinforcement callback
            def on_task_complete(result: "TaskKernelResult") -> None:
                """Callback for synaptic reinforcement."""
                if self._synaptic:
                    try:
                        # Use reinforcement signal to update synapses
                        trigger = self._extract_trigger(intent)
                        if trigger:
                            success = result.status.value == "completed"
                            self._synaptic.update_weight(
                                connection_key=f"{trigger}→{intent.intent_type}",
                                success=success,
                                intent_type=intent.intent_type,
                                trigger=trigger,
                            )
                            signal = result.reinforcement_signal
                            logger.debug(
                                f"🧠 SYNAPSE: TaskKernel reinforcement ({signal:+.2f}) for {intent.intent_type}"
                            )
                    except Exception as e:
                        logger.debug(f"🧠 SYNAPSE: Reinforcement failed: {e}")

            # 4. Spawn TaskKernel (OPUS-176: with sovereignty verification)
            from vibe_core.task_kernel import TaskKernel

            task_kernel = TaskKernel.spawn(
                task=managed_task,
                tools=tools,
                timeout=300,
                on_complete=on_task_complete,
                caller_plugin_id="opus_assistant",  # SOVEREIGN_STATE verified
            )

            # 5. Execute (async)
            result = await task_kernel.execute()

            # 6. Return result
            success = result.status.value == "completed"

            return {
                "executed_via_task_kernel": True,
                "success": success,
                "kernel_id": result.kernel_id,
                "task_id": result.task_id,
                "output": result.output,
                "error": result.error,
                "execution_time_ms": result.execution_time_ms,
                "reinforcement_signal": result.reinforcement_signal,
                "tool_calls_made": result.tool_calls_made,
            }

        except ImportError as e:
            logger.warning(f"⚡ TaskKernel: Import error - {e}")
            return {"executed_via_task_kernel": False}

        except Exception as e:
            logger.error(f"⚡ TaskKernel: Execution failed - {e}")
            return {
                "executed_via_task_kernel": True,
                "success": False,
                "error": str(e),
            }

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

        # Default to intent type prefix (or full type if no underscore)
        parts = intent.intent_type.split("_")
        if len(parts) > 1:
            return parts[0]

        # Fallback: use intent_type as trigger (for simple types like "echo")
        return f"trigger:{intent.intent_type}"

    # =========================================================================
    # OPUS-211: PRAMANA - Closed-Loop Event Emission
    # =========================================================================

    async def _emit_action_completed(
        self,
        intent: "Intent",
        success: bool,
        result: Dict[str, Any],
        execution_time_ms: int,
    ) -> None:
        """
        OPUS-211: Emit ACTION_COMPLETED event for closed-loop feedback.

        This closes the Karma loop:
        Manas (intention) → ActionManager (action) → EventBus (result) → Manas (learning)

        The event allows CognitiveKernel to:
        1. Update intent buffer status
        2. Clear stale intent timers
        3. Record pramana (verification proof)

        Args:
            intent: The executed intent
            success: Whether execution succeeded
            result: Execution result dict
            execution_time_ms: Execution time in milliseconds
        """
        try:
            from vibe_core.event_bus import Event, EventType, get_event_bus

            event_bus = get_event_bus()

            # Build pramana (proof of execution)
            pramana = {
                "executed_at": datetime.utcnow().isoformat(),
                "execution_time_ms": execution_time_ms,
                "success": success,
                "error": result.get("error"),
                "handler": result.get("handler"),
            }

            # Add file verification if applicable
            if result.get("files_modified"):
                pramana["files_modified"] = result["files_modified"]
            if result.get("commit_hash"):
                pramana["commit_hash"] = result["commit_hash"]

            event = Event(
                event_type=EventType.INTENT_EXECUTED,
                agent_id="action_manager",
                details={
                    "intent_id": intent.id,
                    "intent_type": intent.intent_type,
                    "success": success,
                    "pramana": pramana,
                    "result": result,
                },
            )

            await event_bus.emit(event)
            logger.debug(f"📢 ACTION_COMPLETED event emitted for {intent.id}")

        except ImportError:
            logger.debug("EventBus not available - skipping ACTION_COMPLETED emission")
        except Exception as e:
            logger.warning(f"Failed to emit ACTION_COMPLETED event: {e}")

    def _schedule_failure_diagnosis(
        self,
        failed_intent: "Intent",
        result: Dict[str, Any],
        buffer: Optional[Any] = None,
    ) -> None:
        """
        OPUS-220: Auto-Diagnosis for Failed Intents (TITIKSHA - Resilience).

        When an intent execution fails, the system automatically generates
        a diagnostic intent to analyze the failure. This is self-healing:
        the kernel doesn't wait for human intervention, it introspects.

        Args:
            failed_intent: The intent that failed
            result: The execution result containing error info
            buffer: IntentBuffer to add diagnostic intent to
        """
        if not buffer:
            logger.debug("🔴 TITIKSHA: Buffer not available - skipping auto-diagnosis")
            return

        try:
            from vibe_core.plugins.opus_assistant.manas.intent_generator import (
                Intent,
                IntentPriority,
                IntentRisk,
            )

            error_msg = result.get("error", "Unknown error")

            # Create diagnostic intent
            diagnostic_intent = Intent(
                id=f"diagnosis_{failed_intent.id[:8]}",
                intent_type="error_diagnosis",
                title=f"Analyze failure of {failed_intent.intent_type}",
                description=f"Automatic diagnosis: {failed_intent.title} failed with: {error_msg[:100]}",
                reasoning=f"Intent {failed_intent.intent_type} failed. Root cause analysis needed to prevent recurrence.",
                params={
                    "failed_intent_id": failed_intent.id,
                    "failed_intent_type": failed_intent.intent_type,
                    "error_message": error_msg,
                    "original_params": str(failed_intent.params),
                },
                priority=IntentPriority.MEDIUM,
                risk=IntentRisk.SAFE,
                auto_executable=True,  # Can auto-execute diagnosis
            )

            # Add to buffer with lower priority than original
            from vibe_core.plugins.opus_assistant.manas.intent_buffer import (
                IntentBufferEntry,
            )

            entry = IntentBufferEntry(intent=diagnostic_intent)
            buffer.add(entry)

            logger.info(f"🔴 TITIKSHA: Auto-diagnosis scheduled for {failed_intent.id}")

        except Exception as e:
            logger.debug(f"🔴 TITIKSHA: Failed to schedule diagnosis: {e}")


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "ActionManager",
    "ExecutionResult",
    "ToolSelector",  # OPUS-175
]

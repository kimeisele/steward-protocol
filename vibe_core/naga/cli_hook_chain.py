"""
CLI HookChain - Vasuki the Rope

SAMUDRA MANTHAN: The ocean churning requires coordination.
Vasuki (the serpent king) wraps around Mandara mountain as the ROPE.
Here, Vasuki orchestrates the hooks that churn CLI commands.

Architecture:
- Level 0:  User enters command
- Level -1: HookChain orchestrates phases (THIS FILE)
- Level -2: Individual hooks process (Takshaka, Capability, Chitragupta, Sesha)
- Level -3: Command handler executes

The HookChain ensures:
1. Ordered execution (security first)
2. All-must-allow semantics
3. Context propagation through phases
4. Graceful degradation if hooks unavailable

GAD-000 v2.0: "Wiring complexity > Logic complexity"
"""

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from vibe_core.protocols.cli_execution import (
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIExecutionResult,
    CLIHookProtocol,
    CLIHookResult,
)

logger = logging.getLogger("CLI_HOOK_CHAIN")


# =============================================================================
# HOOK CHAIN - Vasuki Orchestrator
# =============================================================================


@dataclass
class HookPhaseMapping:
    """Defines which hook runs at which phase."""

    hook_id: str
    phase: CLIExecutionPhase
    priority: int = 50  # Higher = earlier in phase


class CLIHookChain:
    """
    Orchestrates CLI hook execution order.

    SAMUDRA MANTHAN: Vasuki wraps around the mountain (CLI pipeline)
    and all beings (hooks) pull in coordination.

    Phase Order (immutable):
    1. PRE_VALIDATE  - Takshaka validates args for toxicity
    2. POST_VALIDATE - CapabilityHook checks token
    3. PRE_EXECUTE   - Chitragupta starts profiling
    4. [command executes]
    5. POST_EXECUTE  - Chitragupta stops, Sesha records
    6. ON_ERROR      - Sesha records errors

    Hooks within a phase are ordered by priority (higher = earlier).
    """

    # Defined phase order - this is the ROPE structure
    PHASE_ORDER: List[CLIExecutionPhase] = [
        CLIExecutionPhase.PRE_VALIDATE,
        CLIExecutionPhase.POST_VALIDATE,
        CLIExecutionPhase.PRE_EXECUTE,
        # Command executes here
        CLIExecutionPhase.POST_EXECUTE,
        CLIExecutionPhase.ON_ERROR,
    ]

    # Default hook-phase mappings (Samudra Manthan order)
    DEFAULT_MAPPINGS: List[HookPhaseMapping] = [
        # PRE_VALIDATE: Security validation FIRST
        HookPhaseMapping("takshaka", CLIExecutionPhase.PRE_VALIDATE, priority=100),
        # POST_VALIDATE: Capability check
        HookPhaseMapping("capability", CLIExecutionPhase.POST_VALIDATE, priority=90),
        # PRE_EXECUTE: Start profiling
        HookPhaseMapping("chitragupta", CLIExecutionPhase.PRE_EXECUTE, priority=80),
        # POST_EXECUTE: Record results
        HookPhaseMapping("chitragupta", CLIExecutionPhase.POST_EXECUTE, priority=80),
        HookPhaseMapping("sesha", CLIExecutionPhase.POST_EXECUTE, priority=70),
        # ON_ERROR: Log errors
        HookPhaseMapping("sesha", CLIExecutionPhase.ON_ERROR, priority=100),
    ]

    def __init__(self) -> None:
        """Initialize hook chain."""
        self._hooks: Dict[str, CLIHookProtocol] = {}
        self._mappings: List[HookPhaseMapping] = list(self.DEFAULT_MAPPINGS)
        self._phase_hooks: Dict[CLIExecutionPhase, List[Tuple[int, str]]] = {}
        self._rebuild_phase_index()

    def _rebuild_phase_index(self) -> None:
        """Rebuild phase -> hooks index after mapping changes."""
        self._phase_hooks.clear()
        for mapping in self._mappings:
            if mapping.phase not in self._phase_hooks:
                self._phase_hooks[mapping.phase] = []
            self._phase_hooks[mapping.phase].append((mapping.priority, mapping.hook_id))

        # Sort each phase by priority (descending - higher priority first)
        for phase in self._phase_hooks:
            self._phase_hooks[phase].sort(key=lambda x: -x[0])

    def register(self, hook: CLIHookProtocol) -> None:
        """
        Register a hook by its ID.

        The hook's execution phases are determined by DEFAULT_MAPPINGS.
        """
        hook_id = hook.hook_id
        self._hooks[hook_id] = hook
        logger.debug(f"Registered CLI hook: {hook_id}")

    def unregister(self, hook_id: str) -> bool:
        """Unregister a hook by ID."""
        if hook_id in self._hooks:
            del self._hooks[hook_id]
            logger.debug(f"Unregistered CLI hook: {hook_id}")
            return True
        return False

    def add_mapping(self, mapping: HookPhaseMapping) -> None:
        """Add a custom hook-phase mapping."""
        self._mappings.append(mapping)
        self._rebuild_phase_index()

    def run_phase(
        self,
        phase: CLIExecutionPhase,
        context: CLIExecutionContext,
    ) -> bool:
        """
        Run all hooks for a phase.

        ALL hooks must return allow=True for execution to proceed.
        If any hook blocks, the context is updated with blocked_by/blocked_reason.

        Args:
            phase: Current execution phase
            context: Execution context (mutable)

        Returns:
            True if all hooks allow, False if any blocks
        """
        hooks_for_phase = self._phase_hooks.get(phase, [])

        for priority, hook_id in hooks_for_phase:
            hook = self._hooks.get(hook_id)
            if hook is None:
                # Hook not registered - graceful degradation
                logger.debug(f"Hook {hook_id} not registered, skipping")
                continue

            try:
                result = hook.on_phase(phase, context)

                # Check if hook blocks
                if not result.get("allow", True):
                    context.blocked = True
                    context.blocked_by = hook_id
                    context.blocked_reason = result.get("reason", "Blocked by hook")
                    logger.info(f"CLI blocked by {hook_id} at {phase.value}: {context.blocked_reason}")
                    return False

                # Apply modifications
                if "modified_args" in result:
                    context.args = result["modified_args"]

            except Exception as e:
                # Hook failed - log but don't block (graceful degradation)
                logger.error(f"Hook {hook_id} failed at {phase.value}: {e}")
                continue

        return True

    def run_pre_phases(self, context: CLIExecutionContext) -> bool:
        """
        Run all pre-execution phases.

        Order: PRE_VALIDATE -> POST_VALIDATE -> PRE_EXECUTE
        """
        for phase in [
            CLIExecutionPhase.PRE_VALIDATE,
            CLIExecutionPhase.POST_VALIDATE,
            CLIExecutionPhase.PRE_EXECUTE,
        ]:
            if not self.run_phase(phase, context):
                return False
        return True

    def run_post_phases(self, context: CLIExecutionContext) -> None:
        """Run all post-execution phases (POST_EXECUTE)."""
        self.run_phase(CLIExecutionPhase.POST_EXECUTE, context)

    def run_error_phase(self, context: CLIExecutionContext) -> None:
        """Run error phase (ON_ERROR)."""
        self.run_phase(CLIExecutionPhase.ON_ERROR, context)

    def get_registered_hooks(self) -> List[str]:
        """Get list of registered hook IDs."""
        return list(self._hooks.keys())

    def get_phase_hooks(self, phase: CLIExecutionPhase) -> List[str]:
        """Get hook IDs for a specific phase (in execution order)."""
        return [hook_id for _, hook_id in self._phase_hooks.get(phase, [])]


# =============================================================================
# SINGLETON ACCESS
# =============================================================================

_hook_chain: Optional[CLIHookChain] = None


def get_hook_chain() -> CLIHookChain:
    """
    Get the global CLI HookChain instance.

    Creates one if it doesn't exist.
    """
    global _hook_chain
    if _hook_chain is None:
        _hook_chain = CLIHookChain()
    return _hook_chain


def register_cli_hook(hook: CLIHookProtocol) -> None:
    """Convenience function to register a CLI hook."""
    get_hook_chain().register(hook)

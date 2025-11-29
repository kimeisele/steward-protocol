"""
UNIVERSAL OPERATOR ADAPTER - TCP/IP for Agent Intelligence

PHOENIX VIMANA UNIFIED BOOT - Phase C

This module implements the operator-agnostic interface for Agent City OS.
The system doesn't care WHO is operating - it only cares about the PROTOCOL.

Operators:
- TerminalOperator: stdin/stdout (Human, Claude Code, Scripts - all the same)
- LocalLLMOperator: Local model (ollama, llama.cpp, etc.)
- DegradedOperator: Safe fallback (system never dies)

The UniversalOperatorAdapter manages the priority chain and graceful degradation.

Usage:
    from vibe_core.operator_adapter import UniversalOperatorAdapter, TerminalOperator

    adapter = UniversalOperatorAdapter()
    adapter.register_operator(TerminalOperator(), priority=1)
    adapter.register_operator(LocalLLMOperator(), priority=2)
    adapter.register_operator(DegradedOperator(), priority=99)

    # Get decision from best available operator
    intent = await adapter.get_decision(context)
"""

import asyncio
import logging
import subprocess
import sys
from typing import Optional

from vibe_core.protocols.operator_protocol import (
    Intent,
    IntentType,
    KernelStatusType,
    OperatorResponse,
    OperatorType,
    PriorityLevel,
    SystemContext,
)

logger = logging.getLogger("OPERATOR_ADAPTER")


# =============================================================================
# OPERATOR IMPLEMENTATIONS
# =============================================================================


class TerminalOperator:
    """
    Terminal-based operator (stdin/stdout).

    Works identically for:
    - Human typing at keyboard
    - Claude Code executing CLI commands
    - Scripts piping input
    - Any process attached to stdin

    The abstraction is the INTERFACE, not the entity.
    """

    def __init__(self, timeout: float = 300.0):
        """
        Initialize terminal operator.

        Args:
            timeout: Seconds to wait for input (default 5 minutes)
        """
        self.timeout = timeout
        self._last_context: Optional[SystemContext] = None
        self._available = sys.stdin.isatty() or True  # Always try

    async def receive_context(self, context: SystemContext) -> None:
        """
        Display context to terminal.

        Renders as readable markdown for both human and AI operators.
        """
        self._last_context = context

        # Build status display
        status_icon = {
            KernelStatusType.BOOTING: "🔄",
            KernelStatusType.READY: "🟢",
            KernelStatusType.DEGRADED: "🟡",
            KernelStatusType.SHUTDOWN: "🔴",
        }.get(context.kernel_status, "❓")

        output = f"""
╔══════════════════════════════════════════════════════════════╗
║  AGENT CITY OS - {status_icon} {context.kernel_status.value.upper():10}                        ║
╚══════════════════════════════════════════════════════════════╝

📊 System: {context.agents_registered} agents | {context.agents_healthy} healthy
"""
        if context.git:
            git_status = "clean" if context.git.is_clean else f"{context.git.uncommitted_count} uncommitted"
            output += f"📁 Git: {context.git.branch or 'detached'} ({git_status})\n"

        if context.current_task:
            progress = f"{context.current_task.progress * 100:.0f}%" if context.current_task.progress else "..."
            output += f"📋 Task: {context.current_task.description} [{progress}]\n"

        if context.available_agents:
            output += f"🤖 Agents: {', '.join(context.available_agents[:5])}"
            if len(context.available_agents) > 5:
                output += f" (+{len(context.available_agents) - 5} more)"
            output += "\n"

        output += "\n"

        # Print to terminal
        print(output, file=sys.stderr)

    async def provide_intent(self) -> Intent:
        """
        Read intent from stdin.

        Parses input into structured Intent.
        Works for human typing OR Claude Code/scripts.
        """
        try:
            # Prompt
            print("steward> ", end="", flush=True)

            # Read with timeout using asyncio
            loop = asyncio.get_event_loop()
            raw_input = await asyncio.wait_for(
                loop.run_in_executor(None, sys.stdin.readline),
                timeout=self.timeout,
            )

            raw_input = raw_input.strip()

            if not raw_input:
                # Empty input = query for status
                return Intent(
                    intent_type=IntentType.QUERY,
                    raw_input="",
                    source_operator=OperatorType.HUMAN,  # Terminal source
                    confidence=1.0,
                )

            # Parse intent type from input
            intent_type = self._parse_intent_type(raw_input)
            target_agent, target_tool = self._parse_target(raw_input)

            return Intent(
                intent_type=intent_type,
                raw_input=raw_input,
                target_agent=target_agent,
                target_tool=target_tool,
                source_operator=OperatorType.HUMAN,
                confidence=1.0,
            )

        except asyncio.TimeoutError:
            logger.warning("Terminal input timeout")
            return Intent(
                intent_type=IntentType.CONTROL,
                raw_input="timeout",
                source_operator=OperatorType.HUMAN,
                confidence=0.5,
            )

        except (EOFError, KeyboardInterrupt):
            # EOF or Ctrl+C = shutdown intent
            return Intent(
                intent_type=IntentType.CONTROL,
                raw_input="shutdown",
                source_operator=OperatorType.HUMAN,
                confidence=1.0,
                is_destructive=True,
            )

    def is_available(self) -> bool:
        """Check if terminal is available."""
        return self._available

    def get_operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.HUMAN  # Terminal = human interface

    def _parse_intent_type(self, raw: str) -> IntentType:
        """Parse intent type from raw input."""
        raw_lower = raw.lower()

        # Control commands
        if raw_lower in ("exit", "quit", "shutdown", "stop"):
            return IntentType.CONTROL

        # Query patterns
        if raw_lower.startswith(("?", "what", "who", "where", "when", "why", "how", "status", "list", "show")):
            return IntentType.QUERY

        # Delegation patterns (@ prefix)
        if raw.startswith("@"):
            return IntentType.DELEGATION

        # Default to command
        return IntentType.COMMAND

    def _parse_target(self, raw: str) -> tuple[Optional[str], Optional[str]]:
        """Parse target agent/tool from raw input."""
        # @agent pattern
        if raw.startswith("@"):
            parts = raw[1:].split(maxsplit=1)
            if parts:
                return parts[0], None

        # tool:action pattern
        if ":" in raw:
            parts = raw.split(":", 1)
            return None, parts[0].strip()

        return None, None


class LocalLLMOperator:
    """
    Local LLM operator (ollama, llama.cpp, etc.).

    Provides offline intelligence when cloud APIs are unavailable.
    """

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str = "http://localhost:11434",
    ):
        """
        Initialize local LLM operator.

        Args:
            model: Model name (default: llama3.2)
            base_url: Ollama API URL
        """
        self.model = model
        self.base_url = base_url
        self._last_context: Optional[SystemContext] = None
        self._available: Optional[bool] = None

    async def receive_context(self, context: SystemContext) -> None:
        """Store context for LLM prompt construction."""
        self._last_context = context

    async def provide_intent(self) -> Intent:
        """
        Get intent from local LLM.

        Constructs prompt from context and parses response.
        """
        if not self._last_context:
            return self._fallback_intent("No context provided")

        try:
            # Build prompt
            prompt = self._build_prompt(self._last_context)

            # Call ollama
            response = await self._call_ollama(prompt)

            # Parse response into intent
            return self._parse_response(response)

        except Exception as e:
            logger.error(f"LocalLLM error: {e}")
            return self._fallback_intent(str(e))

    def is_available(self) -> bool:
        """Check if local LLM is available."""
        if self._available is not None:
            return self._available

        # Check ollama availability
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.base_url}/api/tags"],
                capture_output=True,
                timeout=2,
            )
            self._available = result.returncode == 0
        except Exception:
            self._available = False

        return self._available

    def get_operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.LOCAL_LLM

    def _build_prompt(self, context: SystemContext) -> str:
        """Build LLM prompt from context."""
        return f"""You are an operator for Agent City OS.

System Status:
- Kernel: {context.kernel_status.value}
- Agents: {context.agents_registered} registered, {context.agents_healthy} healthy
- Available agents: {", ".join(context.available_agents[:10])}

Recent messages:
{chr(10).join(context.recent_messages[-5:])}

What action should be taken? Respond with a single command or query.
Be concise. Just the command, nothing else."""

    async def _call_ollama(self, prompt: str) -> str:
        """Call ollama API."""
        import json

        proc = await asyncio.create_subprocess_exec(
            "curl",
            "-s",
            "-X",
            "POST",
            f"{self.base_url}/api/generate",
            "-d",
            json.dumps({"model": self.model, "prompt": prompt, "stream": False}),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30.0)
        response = json.loads(stdout.decode())
        return response.get("response", "")

    def _parse_response(self, response: str) -> Intent:
        """Parse LLM response into Intent."""
        raw = response.strip()

        if not raw:
            return self._fallback_intent("Empty LLM response")

        # Determine intent type
        raw_lower = raw.lower()
        if any(word in raw_lower for word in ["status", "check", "show", "list", "?"]):
            intent_type = IntentType.QUERY
        elif any(word in raw_lower for word in ["stop", "exit", "shutdown"]):
            intent_type = IntentType.CONTROL
        else:
            intent_type = IntentType.COMMAND

        return Intent(
            intent_type=intent_type,
            raw_input=raw,
            source_operator=OperatorType.LOCAL_LLM,
            confidence=0.8,  # Local LLM = slightly lower confidence
        )

    def _fallback_intent(self, reason: str) -> Intent:
        """Return fallback intent on error."""
        return Intent(
            intent_type=IntentType.QUERY,
            raw_input=f"status (fallback: {reason})",
            source_operator=OperatorType.LOCAL_LLM,
            confidence=0.3,
        )


class DegradedOperator:
    """
    Degraded/fallback operator.

    Used when all other operators fail.
    Provides safe defaults and logs everything.
    The system NEVER crashes.
    """

    def __init__(self):
        """Initialize degraded operator."""
        self._last_context: Optional[SystemContext] = None
        self._action_count = 0

    async def receive_context(self, context: SystemContext) -> None:
        """Log context (no display in degraded mode)."""
        self._last_context = context
        logger.warning(
            f"DEGRADED MODE: Received context - "
            f"status={context.kernel_status.value}, "
            f"agents={context.agents_registered}"
        )

    async def provide_intent(self) -> Intent:
        """
        Provide safe default intent.

        In degraded mode, we only do safe operations:
        - Status checks
        - Logging
        - No destructive actions
        """
        self._action_count += 1

        # Alternate between status and idle
        if self._action_count % 5 == 0:
            return Intent(
                intent_type=IntentType.QUERY,
                raw_input="status",
                source_operator=OperatorType.DEGRADED,
                confidence=0.1,
                priority=PriorityLevel.LOW,
            )

        # Default: reflex (do nothing, wait)
        return Intent(
            intent_type=IntentType.REFLEX,
            raw_input="idle",
            source_operator=OperatorType.DEGRADED,
            confidence=0.1,
            priority=PriorityLevel.LOW,
        )

    def is_available(self) -> bool:
        """Degraded operator is ALWAYS available."""
        return True

    def get_operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.DEGRADED


# =============================================================================
# UNIVERSAL OPERATOR ADAPTER
# =============================================================================


class UniversalOperatorAdapter:
    """
    The TCP/IP stack for Agent Intelligence.

    Manages multiple operator backends with:
    - Priority-based selection
    - Graceful degradation
    - Hot-swap capability
    - Strict typing (SystemContext → Intent)

    The system doesn't care WHO is operating.
    It only cares about the PROTOCOL.
    """

    def __init__(self):
        """Initialize the adapter."""
        self._operators: list[tuple[int, object]] = []  # (priority, operator)
        self._current_operator: Optional[object] = None
        self._degradation_level: int = 0

        # Always register degraded operator as ultimate fallback
        self.register_operator(DegradedOperator(), priority=999)

        logger.info("UniversalOperatorAdapter initialized")

    def register_operator(self, operator: object, priority: int) -> None:
        """
        Register an operator with priority.

        Lower priority = preferred.
        Priority 999 = fallback only.

        Args:
            operator: Object implementing OperatorSocket protocol
            priority: Priority level (lower = more preferred)
        """
        self._operators.append((priority, operator))
        self._operators.sort(key=lambda x: x[0])

        op_type = operator.get_operator_type()
        logger.info(f"Registered operator: {op_type.value} (priority {priority})")

    def _select_best_operator(self) -> object:
        """Select the best available operator."""
        for priority, operator in self._operators:
            if operator.is_available():
                if operator != self._current_operator:
                    old_type = self._current_operator.get_operator_type() if self._current_operator else "none"
                    new_type = operator.get_operator_type()
                    if old_type != new_type:
                        logger.info(f"Operator switch: {old_type} → {new_type.value}")
                self._current_operator = operator
                self._degradation_level = priority
                return operator

        # This should never happen (DegradedOperator is always available)
        raise RuntimeError("No operators available - this should never happen")

    async def get_decision(self, context: SystemContext) -> Intent:
        """
        Get a decision from the best available operator.

        1. Select best available operator
        2. Send context
        3. Get intent
        4. Return typed intent

        Falls back through priority chain on failure.

        Args:
            context: Strictly typed system context

        Returns:
            Strictly typed intent
        """
        # Update context with current degradation level
        context.degradation_level = self._degradation_level

        # Try operators in priority order
        for priority, operator in self._operators:
            if not operator.is_available():
                continue

            try:
                # Send context
                await operator.receive_context(context)

                # Get intent
                intent = await operator.provide_intent()

                # Update current operator
                self._current_operator = operator
                self._degradation_level = priority

                return intent

            except Exception as e:
                op_type = operator.get_operator_type()
                logger.warning(f"Operator {op_type.value} failed: {e}")
                continue

        # Ultimate fallback (DegradedOperator)
        degraded = self._operators[-1][1]
        await degraded.receive_context(context)
        return await degraded.provide_intent()

    def hot_swap(self, new_operator: object, priority: int) -> None:
        """
        Hot-swap an operator without restart.

        Args:
            new_operator: New operator to add
            priority: Priority for new operator
        """
        self.register_operator(new_operator, priority)
        logger.info(f"Hot-swap: Added {new_operator.get_operator_type().value}")

    def get_current_operator_type(self) -> OperatorType:
        """Get the current operator type."""
        if self._current_operator:
            return self._current_operator.get_operator_type()
        return OperatorType.DEGRADED

    def get_degradation_level(self) -> int:
        """Get current degradation level (0 = full, higher = degraded)."""
        return self._degradation_level

    def create_response(
        self,
        success: bool,
        message: str,
        intent: Intent,
        context: Optional[SystemContext] = None,
    ) -> OperatorResponse:
        """
        Create a typed response to send back to operator.

        Args:
            success: Whether the operation succeeded
            message: Human-readable message
            intent: The intent that was processed
            context: Updated system context (optional)

        Returns:
            Strictly typed response
        """
        return OperatorResponse(
            success=success,
            message=message,
            intent_id=intent.intent_id,
            next_context=context,
        )


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_default_adapter() -> UniversalOperatorAdapter:
    """
    Create adapter with default operator chain.

    Priority chain:
    1. TerminalOperator (human/Claude Code)
    2. LocalLLMOperator (offline fallback)
    999. DegradedOperator (always available)
    """
    adapter = UniversalOperatorAdapter()
    adapter.register_operator(TerminalOperator(), priority=1)
    adapter.register_operator(LocalLLMOperator(), priority=2)
    # DegradedOperator already registered at priority 999

    return adapter


__all__ = [
    "UniversalOperatorAdapter",
    "TerminalOperator",
    "LocalLLMOperator",
    "DegradedOperator",
    "create_default_adapter",
]

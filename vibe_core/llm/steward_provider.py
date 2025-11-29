"""
Steward Provider - Claude Code Environment Integration (ARCH-033C).

This provider delegates cognitive work to the STEWARD (Claude Code environment)
when primary LLM APIs are unavailable.

The STEWARD is the AI operator (Claude Code) that manages this sandbox environment.
When API gateways are blocked (403, network errors), this provider outputs a
structured prompt that Claude Code can read and respond to, effectively making
the environment itself part of the runtime.

This is GAD-000 (Operator Inversion) taken to its logical conclusion:
The environment IS the intelligence layer.

Use Cases:
- Sandbox environments with blocked network access (403 errors)
- Offline development without API keys
- Claude Code integration (environment becomes provider)
- Ultimate fallback when all external APIs fail

Architecture:
- Implements LLMProvider protocol
- Outputs structured prompt to stdout (Claude Code reads it)
- Waits for stdin input (Claude Code provides completion)
- Environment-aware (checks sys.stdin.isatty())

Version: 1.0 (ARCH-033C)
"""

import logging
import sys
from typing import Any

from vibe_core.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class StewardProvider(LLMProvider):
    """
    LLM provider that delegates to the STEWARD (Claude Code environment).

    When external APIs are unavailable, this provider outputs a structured
    prompt that Claude Code (the AI operator managing this environment) can
    read and respond to.

    The workflow:
    1. chat() is called with messages
    2. Provider outputs structured prompt to stdout
    3. Claude Code sees the prompt and understands the task
    4. Claude Code generates completion and asks user: "Send this?"
    5. User clicks "Yes"
    6. Completion arrives via stdin
    7. System continues

    This makes the environment (Claude Code) part of the runtime - the
    ultimate expression of Operator Inversion (GAD-000).

    Example:
        >>> provider = StewardProvider()
        >>> messages = [
        ...     {"role": "system", "content": "You are helpful."},
        ...     {"role": "user", "content": "What is 2+2?"}
        ... ]
        >>> response = provider.chat(messages)
        # Outputs structured prompt to Claude Code
        # Claude Code generates "4" and sends it
        >>> print(response)  # "4"

    Design Notes:
        - Only works in interactive terminals (checks sys.stdin.isatty())
        - Returns instruction message when no TTY (e.g., CI/CD pipelines)
        - Structured output designed for AI parsing (not human reading)
        - Transparent, no hidden magic
    """

    def __init__(self):
        """
        Initialize Steward Provider.

        No configuration needed - this provider uses stdin/stdout directly
        to communicate with the Claude Code environment.
        """
        logger.info("StewardProvider initialized (Claude Code integration mode)")

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Delegate cognitive work to the STEWARD (Claude Code environment).

        Outputs a structured prompt that Claude Code can parse and respond to.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Ignored (Claude Code doesn't have model variants)
            **kwargs: Ignored

        Returns:
            str: The STEWARD's response (from Claude Code)

        Example:
            >>> messages = [{"role": "user", "content": "Hello"}]
            >>> response = provider.chat(messages)
            # Claude Code sees prompt, generates response, sends it
            >>> print(response)  # Whatever Claude Code generated
        """
        # Check if we're in an interactive terminal
        if not sys.stdin.isatty():
            # Non-interactive environment (CI/CD, background process, etc.)
            logger.warning("StewardProvider called in non-interactive environment")
            return (
                "ERROR: StewardProvider requires interactive terminal (stdin is not a TTY). "
                "This provider is designed for Claude Code integration and requires "
                "an interactive environment. Use MockProvider in CI/CD instead."
            )

        # Convert messages to a single prompt
        prompt_text = self._messages_to_prompt(messages)

        # Output structured prompt for Claude Code to parse
        print("\n" + "=" * 70)
        print("[🤖 STEWARD_INTERVENTION_REQUIRED]")
        print("=" * 70)
        print("🚨 STATUS: API GATEWAY DENIED (403 Forbidden / Network Blocked)")
        print("👤 ROLE: You are the STEWARD (System Operator - Claude Code)")
        print("📝 TASK: The internal vibe-agency system needs LLM completion")
        print("")
        print("🔽 INPUT PROMPT:")
        print("-" * 70)
        print(prompt_text)
        print("-" * 70)
        print("🔼 END PROMPT")
        print("")
        print("👉 ACTION REQUIRED:")
        print("   Please provide the completion for the above prompt.")
        print("   The system is waiting for your response below.")
        print("=" * 70)

        # Wait for STEWARD (Claude Code) to provide completion
        try:
            response = input("\n🤖 STEWARD COMPLETION: ").strip()

            if not response:
                logger.warning("STEWARD provided empty response")
                response = "(No completion provided by STEWARD)"

            logger.info(f"STEWARD provided completion: {response[:50]}...")
            print("=" * 70)
            print("✅ STEWARD COMPLETION RECEIVED")
            print("=" * 70 + "\n")

            return response

        except (KeyboardInterrupt, EOFError):
            print("\n")
            logger.warning("STEWARD intervention interrupted")
            return "(STEWARD intervention interrupted)"

    @property
    def system_prompt(self) -> str:
        """
        Return default system prompt.

        For StewardProvider, the system prompt is informational only
        (displayed to Claude Code for context).
        """
        return (
            "You are the STEWARD (Claude Code) providing LLM completions "
            "in place of unavailable external APIs."
        )

    def _messages_to_prompt(self, messages: list[dict[str, str]]) -> str:
        """
        Convert chat messages to a single prompt string.

        Formats messages in a clear structure for Claude Code to understand.

        Args:
            messages: List of message dicts

        Returns:
            str: Formatted prompt text

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "Be concise."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> prompt = provider._messages_to_prompt(messages)
            >>> print(prompt)
            # SYSTEM: Be concise.
            # USER: What is 2+2?
        """
        lines = []

        for msg in messages:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")

            if content:  # Only include non-empty messages
                lines.append(f"{role}: {content}")

        return "\n".join(lines) if lines else "(empty prompt)"

    def __repr__(self) -> str:
        """String representation for debugging."""
        return "StewardProvider(mode=claude_code_integration)"

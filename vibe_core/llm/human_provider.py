"""
Human Provider - Interactive LLM Provider with Operator-in-the-Loop.

This provider implements Human-in-the-Loop AI by prompting the human operator
for responses instead of calling an external LLM API.

Use Cases:
- Sandbox environments with blocked network access (403 errors)
- Offline development without API keys
- Testing/validation where human judgment is required
- GAD-000 Operator Inversion (the human IS the intelligence)

Architecture:
- Implements LLMProvider protocol
- Uses sys.stdin for input (terminal-based interaction)
- Falls back gracefully when no TTY available (returns instruction message)
- Compatible with SimpleLLMAgent

Version: 1.0 (ARCH-033B)
"""

import logging
import sys
from typing import Any

from vibe_core.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


class HumanProvider(LLMProvider):
    """
    Interactive LLM provider that prompts the human operator for responses.

    This is the ultimate fallback provider - when AI APIs are unavailable,
    the human becomes the intelligence layer (Operator Inversion, GAD-000).

    Example:
        >>> provider = HumanProvider()
        >>> messages = [
        ...     {"role": "system", "content": "You are helpful."},
        ...     {"role": "user", "content": "What is 2+2?"}
        ... ]
        >>> response = provider.chat(messages)
        # Prompts human in terminal:
        # ========================================
        # 🧠 HUMAN PROVIDER (Operator-in-the-Loop)
        # ========================================
        # System: You are helpful.
        # User: What is 2+2?
        #
        # Your response: <human types "4">
        # ========================================
        >>> print(response)  # "4"

    Design Notes:
        - Only works in interactive terminals (checks sys.stdin.isatty())
        - Returns instruction message when no TTY (e.g., CI/CD pipelines)
        - Displays full conversation context to operator
        - Simple, transparent, no hidden magic
    """

    def __init__(self):
        """
        Initialize Human Provider.

        No configuration needed - this provider uses stdin/stdout directly.
        """
        logger.info("HumanProvider initialized (Human-in-the-Loop mode)")

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Prompt the human operator for a response.

        Displays the conversation context and waits for human input.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Ignored (humans don't have model variants)
            **kwargs: Ignored

        Returns:
            str: The human's response (or instruction message if no TTY)

        Example:
            >>> messages = [{"role": "user", "content": "Hello"}]
            >>> response = provider.chat(messages)
            # Terminal shows prompt, human types response
            >>> print(response)  # Whatever human typed
        """
        # Check if we're in an interactive terminal
        if not sys.stdin.isatty():
            # Non-interactive environment (CI/CD, background process, etc.)
            logger.warning("HumanProvider called in non-interactive environment")
            return (
                "ERROR: HumanProvider requires interactive terminal (stdin is not a TTY). "
                "This usually means you're running in CI/CD or a background process. "
                "Use MockProvider or a real LLM provider instead."
            )

        # Display conversation context to human
        print("\n" + "=" * 70)
        print("🧠 HUMAN PROVIDER (Operator-in-the-Loop)")
        print("=" * 70)
        print("The AI backend is unavailable. You are now the intelligence layer.")
        print("\nConversation context:")
        print("-" * 70)

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            print(f"{role.upper()}: {content}")

        print("-" * 70)

        # Prompt human for response
        try:
            response = input("\n👤 Your response: ").strip()

            if not response:
                response = "(No response provided)"

            logger.info(f"Human operator provided response: {response[:50]}...")
            print("=" * 70 + "\n")

            return response

        except (KeyboardInterrupt, EOFError):
            print("\n")
            logger.warning("Human operator interrupted input")
            return "(Human operator interrupted)"

    @property
    def system_prompt(self) -> str:
        """
        Return default system prompt.

        For HumanProvider, the system prompt is informational only
        (displayed to the human for context).
        """
        return "You are the human operator providing responses in place of an AI model."

    def __repr__(self) -> str:
        """String representation for debugging."""
        return "HumanProvider(interactive=True)"

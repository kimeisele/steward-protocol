"""
Google Provider Adapter for SimpleLLMAgent compatibility.

This adapter wraps vibe_core.runtime.providers.google.GoogleProvider
to implement the chat-based interface expected by SimpleLLMAgent.

Architecture:
- GoogleProvider uses invoke(prompt) -> LLMResponse
- SimpleLLMAgent expects chat(messages) -> str
- This adapter bridges the two interfaces

The reason for this adapter is that GoogleProvider was built for the
"runtime" layer with rich response objects, while SimpleLLMAgent follows
the simpler chat-based protocol from vibe_core.llm.provider.

Version: 1.0 (ARCH-033)
"""

import logging
import os
from typing import Any

from vibe_core.llm.provider import LLMProvider
from vibe_core.runtime.providers.base import ProviderNotAvailableError
from vibe_core.runtime.providers.google import GoogleProvider as RuntimeGoogleProvider

logger = logging.getLogger(__name__)


class GoogleProvider(LLMProvider):
    """
    Adapter that wraps runtime.GoogleProvider to implement LLMProvider protocol.

    This enables SimpleLLMAgent to use Google Gemini while maintaining
    the simple chat-based interface.

    Example:
        >>> provider = GoogleProvider(api_key="...", model="gemini-2.5-flash")
        >>> messages = [
        ...     {"role": "system", "content": "You are helpful."},
        ...     {"role": "user", "content": "Hello!"}
        ... ]
        >>> response = provider.chat(messages)
        >>> print(response)  # "Hello! How can I help you today?"
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        **kwargs: Any,
    ):
        """
        Initialize Google provider adapter.

        Args:
            api_key: Google API key (or None to load from GOOGLE_API_KEY env var)
            model: Default model to use
            **kwargs: Additional configuration passed to GoogleProvider

        Raises:
            ProviderNotAvailableError: If API key missing or google-generativeai not installed
        """
        # Load API key from env if not provided
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

        if not self.api_key:
            raise ProviderNotAvailableError(
                "Google API key required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Initialize the runtime provider
        try:
            self._provider = RuntimeGoogleProvider(api_key=self.api_key, **kwargs)
            self._default_model = model
            logger.info(f"GoogleProvider initialized (model={model})")
        except Exception as e:
            raise ProviderNotAvailableError(f"Failed to initialize GoogleProvider: {e}") from e

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Send messages to Google Gemini and get response.

        Converts chat-style messages to a single prompt, calls the runtime
        provider, and extracts the text response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier (uses default if None)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            str: The LLM's response text

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are concise."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> response = provider.chat(messages)
            >>> print(response)  # "4"
        """
        # Convert messages to prompt
        # Google Gemini doesn't have separate system/user roles in the same way
        # We'll concatenate system + user messages into a single prompt
        prompt = self._messages_to_prompt(messages)

        # Determine model
        model_to_use = model or self._default_model

        # Call runtime provider
        try:
            llm_response = self._provider.invoke(
                prompt=prompt,
                model=model_to_use,
                **kwargs,
            )

            # Extract text from response
            return llm_response.content

        except Exception as e:
            error_msg = f"Google Gemini invocation failed: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    @property
    def system_prompt(self) -> str:
        """
        Return default system prompt.

        For compatibility with LLMProvider protocol.
        """
        return "You are a helpful AI assistant."

    def _messages_to_prompt(self, messages: list[dict[str, str]]) -> str:
        """
        Convert chat messages to a single prompt string.

        Google Gemini works best with a single consolidated prompt.
        We'll combine system and user messages appropriately.

        Args:
            messages: List of message dicts

        Returns:
            str: Consolidated prompt

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "Be concise."},
            ...     {"role": "user", "content": "Hello"}
            ... ]
            >>> prompt = provider._messages_to_prompt(messages)
            >>> print(prompt)
            # "You must follow these instructions:
            # Be concise.
            #
            # User: Hello"
        """
        system_parts = []
        user_parts = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                system_parts.append(content)
            elif role == "user":
                user_parts.append(content)
            elif role == "assistant":
                # For now, we don't support multi-turn conversations
                # Future enhancement: maintain conversation history
                pass

        # Build prompt
        parts = []

        if system_parts:
            parts.append("You must follow these instructions:")
            parts.extend(system_parts)
            parts.append("")  # Blank line

        if user_parts:
            # Combine all user messages
            for user_msg in user_parts:
                parts.append(f"User: {user_msg}")

        return "\n".join(parts)

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"GoogleProvider(model={self._default_model})"

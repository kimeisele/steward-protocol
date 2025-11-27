"""
LLM Provider abstraction for vibe-agency OS.

This module defines the standard interface for LLM providers (ARCH-025),
enabling the kernel to orchestrate cognitive work via language models.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    The LLMProvider is the "Cortex" - the abstraction that allows
    agents to perform cognitive work via language models without
    being coupled to specific APIs (OpenAI, Anthropic, etc.).

    Design Principles:
    - Provider-agnostic interface (works with any LLM API)
    - Message-based communication (standard chat format)
    - Simple return type (string response)
    - Configurable system prompts
    - Testable (MockProvider for unit tests)

    Example:
        >>> class MyProvider(LLMProvider):
        ...     def chat(self, messages, model=None):
        ...         # Call API here
        ...         return "Response from LLM"
        ...
        ...     @property
        ...     def system_prompt(self):
        ...         return "You are a helpful assistant."
    """

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], model: str | None = None, **kwargs) -> str:
        """
        Send messages to the LLM and get a response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                      Standard format: [{"role": "user", "content": "Hello"}]
            model: Optional model identifier (e.g., "gpt-4", "claude-3-opus")
            **kwargs: Additional provider-specific parameters

        Returns:
            str: The LLM's response text

        Raises:
            Exception: If API call fails (provider-specific exceptions)

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> response = provider.chat(messages)
            >>> print(response)  # "2+2 equals 4."

        Notes:
            - System messages should be included in the messages list
            - Providers may ignore or handle system messages differently
            - The response is the text content only (no metadata)
        """
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """
        Return the default system prompt for this provider.

        The system prompt sets the behavior/personality of the LLM.
        Agents can override this by including their own system message
        in the messages list passed to chat().

        Returns:
            str: The system prompt text

        Example:
            >>> provider = MyProvider()
            >>> print(provider.system_prompt)
            "You are a helpful AI assistant specialized in code."

        Notes:
            - This is a convenience property for default behavior
            - Agents can choose to use this or provide their own
            - Some providers may not support system prompts
        """
        pass

    def get_metadata(self) -> dict[str, str]:
        """
        Get provider metadata (optional, can be overridden).

        Returns:
            dict: Metadata about the provider (name, version, etc.)

        Example:
            >>> metadata = provider.get_metadata()
            >>> print(metadata["provider_name"])  # "MockProvider"
        """
        return {
            "provider_name": self.__class__.__name__,
            "provider_type": "LLM",
        }


class LLMError(Exception):
    """
    Base exception for LLM provider errors.

    Raised when LLM API calls fail (network, auth, rate limits, etc.).
    """

    def __init__(
        self, message: str, provider: str = "Unknown", original_error: Exception | None = None
    ):
        self.provider = provider
        self.original_error = original_error
        super().__init__(f"[{provider}] {message}")

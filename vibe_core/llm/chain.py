"""
ChainProvider - ARCH-067 (Runtime Provider Cascade)
====================================================

A resilient provider that maintains a chain of fallback providers.

If the primary provider fails, ChainProvider automatically switches to
the next provider in the chain. This enables "Runtime Immortality" -
agents that can adapt their cognitive backbone on-the-fly.

Architecture:
- Wraps a list of LLMProviders in priority order
- Implements the LLMProvider interface
- Tries each provider sequentially on failure
- Logs all fallback attempts
- Only fails if EVERY provider fails

Design Principles:
- Transparent: Agents don't need to know about the chain
- Resilient: Continues even if APIs go down
- Observable: Logs all provider switches
- Simple: Just iterate and try

Example:
    >>> google = GoogleProvider(api_key="...")
    >>> local = SmartLocalProvider()
    >>> chain = ChainProvider(providers=[google, local])
    >>> agent = SimpleLLMAgent(provider=chain)  # Agent uses chain transparently
    >>> # If Google fails, automatically falls back to SmartLocal
"""

import logging
from typing import Optional

from vibe_core.llm.provider import LLMError, LLMProvider

logger = logging.getLogger(__name__)


class ChainProvider(LLMProvider):
    """
    A resilient provider that cascades through multiple providers.

    When a provider fails, automatically tries the next one in the chain.
    This gives agents "Runtime Immortality" - they can survive API outages
    and provider failures by switching providers mid-execution.

    Lifecycle:
        1. Initialize with list of providers: [primary, secondary, tertiary, ...]
        2. Agent calls chat()
        3. Try primary provider
        4. If it fails → try secondary
        5. If that fails → try tertiary
        6. If ALL fail → raise error
        7. Log each switch for debugging

    Example:
        >>> providers = [
        ...     GoogleProvider(api_key="..."),
        ...     SmartLocalProvider(),
        ...     StewardProvider()
        ... ]
        >>> chain = ChainProvider(providers=providers)
        >>> response = chain.chat(messages)  # Auto-falls back if needed
    """

    def __init__(self, providers: list[LLMProvider]):
        """
        Initialize the chain provider.

        Args:
            providers: List of LLMProvider instances in priority order.
                      First provider is tried first, second is fallback, etc.

        Raises:
            ValueError: If providers list is empty

        Example:
            >>> chain = ChainProvider(providers=[
            ...     GoogleProvider(api_key="..."),
            ...     SmartLocalProvider()
            ... ])
        """
        if not providers:
            raise ValueError("ChainProvider requires at least one provider")

        self.providers = providers
        self._current_provider_index = 0

        provider_names = [p.__class__.__name__ for p in providers]
        logger.info(f"ChainProvider initialized with {len(providers)} provider(s): {provider_names}")

    def chat(
        self, messages: list[dict[str, str]], model: str | None = None, **kwargs
    ) -> str:
        """
        Send messages through the provider chain.

        Tries each provider in order until one succeeds. If a provider fails,
        logs the error and tries the next one in the chain.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Optional model identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            str: The LLM's response text

        Raises:
            LLMError: If ALL providers in the chain fail

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful."},
            ...     {"role": "user", "content": "What is 2+2?"}
            ... ]
            >>> response = chain.chat(messages)
            >>> print(response)  # Response from first available provider
        """
        errors = []

        # Try each provider in the chain
        for i, provider in enumerate(self.providers):
            try:
                logger.debug(f"ChainProvider: Trying provider {i} ({provider.__class__.__name__})")

                response = provider.chat(messages, model=model, **kwargs)

                # Success! Log if we had to switch providers
                if i > 0:
                    logger.warning(
                        f"ChainProvider: Recovered from provider failure. "
                        f"Now using {provider.__class__.__name__} (index {i})"
                    )

                self._current_provider_index = i
                return response

            except Exception as e:
                error_msg = f"{provider.__class__.__name__} (index {i}): {e}"
                errors.append(error_msg)
                logger.warning(f"ChainProvider: Provider failed, trying next: {error_msg}")

                # Continue to next provider
                continue

        # If we get here, ALL providers failed
        all_errors = "\n".join(f"  - {err}" for err in errors)
        error_summary = f"All {len(self.providers)} provider(s) failed:\n{all_errors}"

        logger.error(f"ChainProvider: CRITICAL - {error_summary}")

        raise LLMError(
            message=error_summary,
            provider="ChainProvider",
            original_error=Exception(error_summary),
        )

    @property
    def system_prompt(self) -> str:
        """
        Return the system prompt from the current/primary provider.

        Returns:
            str: System prompt text

        Example:
            >>> chain = ChainProvider(providers=[google, local])
            >>> print(chain.system_prompt)  # From Google
        """
        # Use the first provider's system prompt as the default
        return self.providers[0].system_prompt

    def get_metadata(self) -> dict[str, str]:
        """
        Get metadata about the chain provider.

        Returns:
            dict: Metadata including all provider names in the chain

        Example:
            >>> metadata = chain.get_metadata()
            >>> print(metadata["provider_names"])  # ["Google", "SmartLocal", ...]
        """
        provider_names = [p.__class__.__name__ for p in self.providers]
        current_provider = (
            self.providers[self._current_provider_index].__class__.__name__
            if self._current_provider_index < len(self.providers)
            else "unknown"
        )

        return {
            "provider_name": "ChainProvider",
            "provider_type": "Chain",
            "chain_length": str(len(self.providers)),
            "providers_in_chain": ", ".join(provider_names),
            "current_provider": current_provider,
        }

    def __repr__(self) -> str:
        """String representation for debugging."""
        providers_str = ", ".join([p.__class__.__name__ for p in self.providers])
        return f"ChainProvider(providers=[{providers_str}])"

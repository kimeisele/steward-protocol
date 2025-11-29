#!/usr/bin/env python3
"""
GAD-511: Neural Adapter Strategy - Base Provider Interface
===========================================================

Abstract interface for LLM providers, enabling provider-agnostic
integration (Anthropic, OpenAI, Local/Ollama, etc.).

Architecture: Strategy Pattern
- LLMProvider: Abstract base class defining the contract
- Concrete providers: AnthropicProvider, OpenAIProvider, LocalProvider
- Factory: Selects provider based on Phoenix Config

Design Principles:
1. Provider Independence: System works with any LLM provider
2. Uniform Interface: All providers expose same methods
3. Cost Transparency: All providers report token usage and cost
4. Graceful Degradation: Fallback to NoOp if provider unavailable

Version: 1.0 (GAD-511)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class LLMUsage:
    """Token usage and cost information (provider-agnostic)"""

    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float
    timestamp: str


@dataclass
class LLMResponse:
    """Standardized LLM response (provider-agnostic)"""

    content: str
    usage: LLMUsage
    model: str
    finish_reason: str
    provider: str  # "anthropic", "openai", "local", etc.


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    All concrete providers (Anthropic, OpenAI, Local) must implement
    this interface to ensure consistent behavior across the system.
    """

    @abstractmethod
    def __init__(self, api_key: str | None = None, **kwargs: Any):
        """
        Initialize provider with API key and configuration.

        Args:
            api_key: API key for the provider (None for local models)
            **kwargs: Provider-specific configuration
        """
        pass

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Invoke the LLM with a prompt.

        Args:
            prompt: Input prompt
            model: Model identifier (provider-specific)
            max_tokens: Maximum output tokens
            temperature: Sampling temperature (0.0 to 2.0)
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with content, usage, and metadata

        Raises:
            LLMProviderError: If invocation fails
        """
        pass

    @abstractmethod
    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """
        Calculate cost for token usage (provider-specific pricing).

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model identifier

        Returns:
            Cost in USD
        """
        pass

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """
        Get list of available models for this provider.

        Returns:
            List of model identifiers
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if provider is available (API key set, network accessible, etc.).

        Returns:
            True if provider can be used, False otherwise
        """
        pass

    def get_provider_name(self) -> str:
        """
        Get human-readable provider name.

        Returns:
            Provider name (e.g., "Anthropic", "OpenAI", "Local")
        """
        return self.__class__.__name__.replace("Provider", "")


class NoOpProvider(LLMProvider):
    """
    Fallback provider when no real provider is available.

    Returns empty responses with zero cost, allowing the system
    to run in knowledge-only mode without crashing.
    """

    def __init__(self, api_key: str | None = None, **kwargs: Any):
        """Initialize NoOp provider (no configuration needed)"""
        self.logger = None
        try:
            import logging

            self.logger = logging.getLogger(__name__)
            self.logger.warning("NoOpProvider initialized - running in mock mode")
        except Exception:
            pass

    def invoke(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        **kwargs: Any,
    ) -> LLMResponse:
        """Return mock empty response"""
        if self.logger:
            self.logger.warning("NoOpProvider: Skipping LLM call (no provider available)")

        usage = LLMUsage(
            input_tokens=0,
            output_tokens=0,
            model=model,
            cost_usd=0.0,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        return LLMResponse(
            content="{}",  # Empty JSON response
            usage=usage,
            model=model,
            finish_reason="no_provider",
            provider="noop",
        )

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """NoOp provider has zero cost"""
        return 0.0

    def get_available_models(self) -> list[str]:
        """NoOp provider has no real models"""
        return ["noop"]

    def is_available(self) -> bool:
        """NoOp provider is always available as fallback"""
        return True


class LLMProviderError(Exception):
    """Base exception for provider errors"""

    pass


class ProviderNotAvailableError(LLMProviderError):
    """Raised when provider cannot be initialized"""

    pass


class ProviderInvocationError(LLMProviderError):
    """Raised when provider invocation fails"""

    pass

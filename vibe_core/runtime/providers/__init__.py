"""
GAD-511: Neural Adapter Strategy - Providers Package
====================================================

Multi-provider LLM support with clean abstraction layer.

Supported providers:
- Anthropic (Claude)
- Google (Gemini)
- OpenAI (Future)
- Local/Ollama (Future)

Usage:
    from providers import create_provider

    provider = create_provider(provider_name="anthropic", api_key="...")
    response = provider.invoke(prompt="Hello", model="claude-3-5-sonnet")

Version: 1.0 (GAD-511)
"""

from .anthropic import AnthropicProvider
from .base import (
    LLMProvider,
    LLMProviderError,
    LLMResponse,
    LLMUsage,
    NoOpProvider,
    ProviderInvocationError,
    ProviderNotAvailableError,
)
from .factory import create_provider, get_default_provider
from .google import GoogleProvider

__all__ = [
    "AnthropicProvider",
    "GoogleProvider",
    "LLMProvider",
    "LLMProviderError",
    "LLMResponse",
    "LLMUsage",
    "NoOpProvider",
    "ProviderInvocationError",
    "ProviderNotAvailableError",
    "create_provider",
    "get_default_provider",
]

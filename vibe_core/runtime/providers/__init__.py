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
    from vibe_core.runtime.providers import create_provider

    provider = create_provider(provider_name="anthropic", api_key="...")
    response = provider.invoke(prompt="Hello", model="claude-3-5-sonnet")

NOTE: Individual providers (GoogleProvider, AnthropicProvider) are NOT
exported here to avoid heavy import chains. Use create_provider() instead.

Version: 1.1 (Lean Kernel)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xd02e8cdc"  # GenesisByte: parampara % 37 == 0

from .base import (
    LLMProvider,
    LLMProviderError,
    LLMResponse,
    LLMUsage,
    NoOpProvider,
    ProviderInvocationError,
    ProviderNotAvailableError,
)
from .factory import create_provider, get_default_provider, get_llm_provider

__all__ = [
    # Base classes (lightweight)
    "LLMProvider",
    "LLMProviderError",
    "LLMResponse",
    "LLMUsage",
    "NoOpProvider",
    "ProviderInvocationError",
    "ProviderNotAvailableError",
    # Factory functions (lazy load providers)
    "create_provider",
    "get_default_provider",
    # ServiceRegistry factory (NAGA-observed!)
    "get_llm_provider",
]

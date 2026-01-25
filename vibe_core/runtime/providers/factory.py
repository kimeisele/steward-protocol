#!/usr/bin/env python3
"""
GAD-511: Provider Factory
==========================

Factory for creating and configuring LLM providers based on Phoenix Config.

Supports:
- Provider selection via configuration
- Automatic API key loading
- Graceful fallback to NoOp provider
- Provider-specific configuration

Version: 1.0 (GAD-511)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xc6307399"  # GenesisByte: parampara % 37 == 0

import logging
import os
from typing import Any

from .base import LLMProvider, NoOpProvider, ProviderNotAvailableError

logger = logging.getLogger(__name__)


def _get_default_model_from_config(provider_name: str) -> str:
    """Load default model from config/llm.yaml - FAILS if not configured!"""
    from vibe_core.phoenix import get_config

    config = get_config()
    llm_cfg = config.llm  # LLMConfig object

    # Access providers dict and get ProviderEntry
    provider_entry = llm_cfg.providers.get(provider_name)

    if not provider_entry or not provider_entry.default_model:
        raise ValueError(
            f"❌ FATAL: No model configured for '{provider_name}'! "
            f"Set 'providers.{provider_name}.default_model' in config/llm.yaml"
        )

    return provider_entry.default_model


def create_provider(
    provider_name: str | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
    **kwargs: Any,
) -> LLMProvider:
    """
    Create an LLM provider based on configuration.

    Args:
        provider_name: Provider identifier ("anthropic", "openai", "local")
        api_key: API key for the provider (optional, loaded from env if not provided)
        model_name: Default model to use (provider-specific)
        **kwargs: Additional provider-specific configuration

    Returns:
        LLMProvider instance (or NoOpProvider if creation fails)

    Examples:
        # Create Anthropic provider
        provider = create_provider("anthropic", api_key="sk-...")

        # Create with auto-detection
        provider = create_provider()  # Uses Phoenix Config or env vars
    """
    # Auto-detect provider if not specified
    if provider_name is None:
        provider_name = _detect_provider()

    provider_name = provider_name.lower()

    # Load API key from environment if not provided
    if api_key is None:
        api_key = _get_api_key_for_provider(provider_name)

    try:
        if provider_name == "anthropic":
            from .anthropic import AnthropicProvider  # Lazy import

            logger.info(f"Creating Anthropic provider (model: {model_name or 'default'})")
            return AnthropicProvider(api_key=api_key, **kwargs)

        elif provider_name == "google":
            from .google import GoogleProvider  # Lazy import

            logger.info(f"Creating Google Gemini provider (model: {model_name or 'gemini-2.5-flash-exp'})")
            return GoogleProvider(api_key=api_key, **kwargs)

        elif provider_name == "openai":
            logger.warning("OpenAI provider not yet implemented (GAD-511 Phase 2)")
            return NoOpProvider()

        elif provider_name == "openrouter":
            from .openrouter import OpenRouterProvider  # Lazy import

            # Get default model from config (FAILS if not configured!)
            default_model = _get_default_model_from_config("openrouter")
            logger.info(f"Creating OpenRouter provider (config: {model_name or default_model})")
            return OpenRouterProvider(api_key=api_key, **kwargs)

        elif provider_name == "local":
            logger.info("Creating Local LLM provider")
            try:
                from vibe_core.llm.local_llama_provider import LocalLlamaProvider

                if LocalLlamaProvider.model_exists():
                    return LocalLlamaProvider(**kwargs)
                else:
                    logger.warning("Local model not found. Run: steward install-llm")
                    return NoOpProvider()
            except ImportError:
                logger.warning("llama-cpp-python not installed")
                return NoOpProvider()

        else:
            logger.warning(f"Unknown provider: {provider_name}, falling back to NoOp")
            return NoOpProvider()

    except ProviderNotAvailableError as e:
        logger.warning(f"Provider {provider_name} not available: {e}, using NoOp fallback")
        return NoOpProvider()
    except Exception as e:
        logger.error(f"Failed to create provider {provider_name}: {e}, using NoOp fallback")
        return NoOpProvider()


def get_default_provider() -> LLMProvider:
    """
    Get the default provider based on Phoenix Config.

    This is the main entry point for most code that needs an LLM provider.
    It automatically detects the best provider based on:
    1. Phoenix Config settings (if available)
    2. Environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY)
    3. Falls back to NoOpProvider if nothing is available

    Returns:
        LLMProvider instance
    """
    try:
        # Try to load Phoenix Config
        from vibe_core.config import get_config

        get_config()  # Load config (future: use config.model.provider)

        # Check if model config exists (future enhancement)
        # For now, use default detection
        provider_name = _detect_provider()
        api_key = _get_api_key_for_provider(provider_name)

        return create_provider(provider_name=provider_name, api_key=api_key)

    except Exception as e:
        logger.warning(f"Failed to load Phoenix Config: {e}, using auto-detection")
        # Fallback to auto-detection
        provider_name = _detect_provider()
        api_key = _get_api_key_for_provider(provider_name)
        return create_provider(provider_name=provider_name, api_key=api_key)


def _detect_provider() -> str:
    """
    Auto-detect which provider to use based on available API keys.

    Priority order (NO VENDOR LOCK-IN!):
    1. OPENROUTER_API_KEY → openrouter (FIRST! Routes to any model)
    2. OPENAI_API_KEY with "sk-or-" prefix → openrouter (MISPLACED KEY FIX!)
    3. OPENAI_API_KEY → openai (Industry standard fallback)
    4. GOOGLE_API_KEY → google
    5. ANTHROPIC_API_KEY → anthropic
    6. None available → noop (will use NoOpProvider)

    Returns:
        Provider name string
    """

    def is_valid_key(key: str | None) -> bool:
        """Check if key is valid (not None, not empty, not a placeholder)"""
        if not key:
            return False
        # Filter out common placeholder values
        placeholders = ["your-", "xxx", "placeholder", "example", "test-key"]
        return not any(placeholder in key.lower() for placeholder in placeholders)

    def is_openrouter_key(key: str | None) -> bool:
        """Check if a key is an OpenRouter key (starts with sk-or-)"""
        return bool(key and key.startswith("sk-or-"))

    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    # OpenRouter FIRST - no vendor lock-in, routes to any model!
    if is_valid_key(openrouter_key):
        return "openrouter"

    # OPUS-091 FIX: Check if OPENAI_API_KEY is actually an OpenRouter key (misplaced)
    # OpenRouter keys start with "sk-or-" prefix
    if is_openrouter_key(openai_key):
        logger.info("🔧 Detected OpenRouter key in OPENAI_API_KEY (sk-or- prefix) - using OpenRouter provider")
        # Inject it into the correct env var for downstream use
        os.environ["OPENROUTER_API_KEY"] = openai_key
        return "openrouter"

    # OpenAI SECOND - industry standard
    if is_valid_key(openai_key):
        return "openai"
    elif is_valid_key(google_key):
        return "google"
    elif is_valid_key(anthropic_key):
        return "anthropic"
    else:
        logger.info("No API keys detected. Activating Mock/Offline Mode (NoOp provider)")
        return "noop"


def _get_api_key_for_provider(provider_name: str) -> str | None:
    """
    Get API key for specified provider from environment.

    Args:
        provider_name: Provider identifier

    Returns:
        API key string or None
    """
    env_var_map = {
        "google": "GOOGLE_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "local": None,  # Local models don't need API keys
        "noop": None,  # NoOp doesn't need API keys
    }

    env_var = env_var_map.get(provider_name)
    if env_var:
        return os.environ.get(env_var)
    return None


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_llm_provider() -> LLMProvider:
    """
    Get LLMProvider through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        Raw LLMProvider → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees all LLM calls)
    - NAGA profiling (Chitragupta tracks token usage/latency)
    - NAGA isolation (Kaliya handles API errors)

    Returns:
        LLMProvider wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(LLMProvider)
    if existing is not None:
        return existing

    # Create provider via auto-detection
    provider_name = _detect_provider()
    instance = create_provider(provider_name=provider_name)

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(LLMProvider, instance)
    logger.info(f"✅ LLMProvider ({provider_name}) registered via ServiceRegistry (WIRED + NAGA-observed)")

    return ServiceRegistry.get(LLMProvider)  # type: ignore

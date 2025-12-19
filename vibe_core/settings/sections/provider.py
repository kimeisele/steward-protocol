#!/usr/bin/env python3
"""
Provider Settings Section

Self-contained section for LLM provider configuration.
"""

import logging
from typing import List, Optional

from ..protocol import SectionContext, SettingsResult, SettingsSection

logger = logging.getLogger(__name__)

# Provider registry - maps names to class paths
PROVIDER_REGISTRY = {
    "anthropic": {
        "class": "vibe_core.runtime.providers.anthropic:AnthropicProvider",
        "display": "Anthropic Claude",
        "api_key_env": "ANTHROPIC_API_KEY",
        "pro_model": "claude-sonnet-4-20250514",
        "low_model": "claude-haiku-3-20240307",
    },
    "openai": {
        "class": "vibe_core.runtime.providers.openai:OpenAIProvider",
        "display": "OpenAI GPT",
        "api_key_env": "OPENAI_API_KEY",
        "pro_model": "gpt-4-turbo",
        "low_model": "gpt-3.5-turbo",
    },
    "openrouter": {
        "class": "vibe_core.runtime.providers.openrouter:OpenRouterProvider",
        "display": "OpenRouter",
        "api_key_env": "OPENROUTER_API_KEY",
        "pro_model": "anthropic/claude-opus-4",  # 2025: Premium reasoning
        "low_model": "anthropic/claude-3.5-haiku",  # 2025: Fast & cheap
    },
}


def get_provider_info_from_config() -> dict:
    """
    Get current provider info from phoenix config.

    SINGLE SOURCE OF TRUTH for provider information.
    Used by settings_ui.py and anywhere provider info is needed.

    Returns:
        Dict with name, display, api_key_env, pro_model, low_model
    """
    try:
        from vibe_core.phoenix import get_config

        phoenix_config = get_config()
        provider_path = phoenix_config.kernel.providers.llm_provider

        # Find matching provider in registry
        for name, provider_cfg in PROVIDER_REGISTRY.items():
            if name in provider_path.lower() or provider_cfg["class"] == provider_path:
                return {
                    "name": name,
                    "display": provider_cfg["display"],
                    "api_key_env": provider_cfg["api_key_env"],
                    "pro_model": provider_cfg["pro_model"],
                    "low_model": provider_cfg["low_model"],
                }

        # Unknown provider
        return {
            "name": "custom",
            "display": "Custom Provider",
            "api_key_env": "LLM_API_KEY",
            "pro_model": "default",
            "low_model": "default",
        }

    except Exception:
        return {
            "name": "unknown",
            "display": "Unknown",
            "api_key_env": "LLM_API_KEY",
            "pro_model": "default",
            "low_model": "default",
        }


class ProviderSection(SettingsSection):
    """LLM Provider configuration section."""

    @property
    def section_id(self) -> str:
        return "provider"

    @property
    def priority(self) -> int:
        return 10  # Render early

    @property
    def title(self) -> str:
        return "## 🔌 LLM Provider Configuration"

    def render(self, context: SectionContext) -> List[str]:
        """Render provider configuration section."""
        provider_info = context.provider_info
        provider_name = provider_info.get("name", "unknown") if provider_info else "unknown"
        display = provider_info.get("display", "Unknown") if provider_info else "Unknown"

        lines = [
            "---",
            "",
            self.title,
            "",
            f"**Current Provider:** `{provider_name}` ({display})",
            "",
            "| Setting | Value |",
            "|---------|-------|",
        ]

        if provider_info:
            lines.extend(
                [
                    f"| `provider` | {provider_name} |",
                    f"| `pro_model` | {provider_info.get('pro_model', 'default')} |",
                    f"| `low_model` | {provider_info.get('low_model', 'default')} |",
                    f"| `api_key_env` | {provider_info.get('api_key_env', 'LLM_API_KEY')} |",
                ]
            )
        else:
            lines.append("| _No provider configured_ | - |")

        lines.extend(
            [
                "",
                "**To change provider:**",
                "```",
                "- SET provider=anthropic",
                "- SET provider=openai",
                "- SET provider=openrouter",
                "```",
                "",
            ]
        )

        return lines

    def handles_command(self, key: str) -> bool:
        return key == "provider"

    def validate(self, key: str, value: str) -> Optional[str]:
        """Validate provider name."""
        if value.lower() not in PROVIDER_REGISTRY:
            valid = ", ".join(PROVIDER_REGISTRY.keys())
            return f"Invalid provider '{value}'. Valid providers: {valid}"
        return None

    def execute(self, key: str, value: str, context: SectionContext) -> SettingsResult:
        """Execute provider change."""
        provider = value.lower().strip()

        # Validate
        error = self.validate(key, provider)
        if error:
            return SettingsResult(success=False, message=error)

        # Get provider config
        provider_config = PROVIDER_REGISTRY[provider]

        try:
            # Update phoenix config
            from vibe_core.phoenix import get_config

            config = get_config()
            config.kernel.providers.llm_provider = provider_config["class"]
            config.save()

            logger.info(f"🔌 Provider changed to '{provider}'")

            return SettingsResult(
                success=True,
                message=f"Provider changed to '{provider}' (requires kernel restart)",
                requires_restart=True,
                side_effects={"new_provider": provider},
            )

        except Exception as e:
            logger.error(f"Failed to change provider: {e}")
            return SettingsResult(success=False, message=str(e))

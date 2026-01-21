"""
LLM Providers Configuration - Wiring of provider types to implementation classes.

Extracted from phoenix.yaml `providers` and `playbook` sections.
Loaded from config/providers.yaml via Phoenix auto-discovery.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 14
__genesis__ = "0x04a8bb52"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PlaybookConfig:
    """Playbook executor configuration."""

    executor_agent: str = "vibe_core.agents.llm_agent:SimpleLLMAgent"
    fallback_agent: str = "vibe_core.agents.specialist_agent:SpecialistAgent"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PlaybookConfig":
        """Create from YAML dict."""
        return cls(
            executor_agent=data.get("executor_agent", "vibe_core.agents.llm_agent:SimpleLLMAgent"),
            fallback_agent=data.get("fallback_agent", "vibe_core.agents.specialist_agent:SpecialistAgent"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "executor_agent": self.executor_agent,
            "fallback_agent": self.fallback_agent,
        }


@dataclass
class LLMProvidersConfig:
    """LLM provider wiring."""

    llm_provider: str = "vibe_core.runtime.providers.anthropic:AnthropicProvider"
    fallback_provider: str = "vibe_core.runtime.providers.base:DefaultLLMProvider"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LLMProvidersConfig":
        """Create from YAML dict."""
        return cls(
            llm_provider=data.get(
                "llm_provider",
                "vibe_core.runtime.providers.anthropic:AnthropicProvider",
            ),
            fallback_provider=data.get(
                "fallback_provider",
                "vibe_core.runtime.providers.base:DefaultLLMProvider",
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "llm_provider": self.llm_provider,
            "fallback_provider": self.fallback_provider,
        }


@dataclass
class FeaturesConfig:
    """Feature flags."""

    oauth_enforcement: bool = True
    live_fire_enabled: bool = True  # OPUS-076: NO PUSSY MODE - default ON
    performance_metrics: bool = True
    debug_mode: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeaturesConfig":
        """Create from YAML dict."""
        return cls(
            oauth_enforcement=data.get("oauth_enforcement", True),
            live_fire_enabled=data.get("live_fire_enabled", True),  # OPUS-076
            performance_metrics=data.get("performance_metrics", True),
            debug_mode=data.get("debug_mode", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "oauth_enforcement": self.oauth_enforcement,
            "live_fire_enabled": self.live_fire_enabled,
            "performance_metrics": self.performance_metrics,
            "debug_mode": self.debug_mode,
        }


@dataclass
class ImportsConfig:
    """Import order configuration."""

    order: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImportsConfig":
        """Create from YAML dict."""
        default_order = [
            "vibe_core.protocols",
            "vibe_core.kernel_impl",
            "vibe_core.agents",
            "vibe_core.runtime",
            "vibe_core.cartridges.system",
            "vibe_core.cartridges.agent_city",
            "vibe_core.playbook",
        ]
        return cls(order=data.get("order", default_order))

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {"order": self.order}


@dataclass
class ProvidersConfig:
    """
    Providers Configuration.

    Auto-discovered by SectionLoader -> loads from config/providers.yaml

    This section defines the wiring for:
    - LLM providers (Anthropic, fallback)
    - Playbook executors
    - Feature flags
    - Import order

    Required attributes:
    - section_id: str - Unique identifier (must match manifest.json id)
    - source_file: str - YAML filename in config/

    Required methods:
    - from_dict(data) -> Self - Create instance from YAML data
    - to_dict() -> dict - Serialize to dict
    - validate() -> List[str] - Return list of errors (empty = valid)
    """

    # Required: Must match manifest.json "id"
    section_id: str = "providers"
    source_file: str = "providers.yaml"

    # Provider configurations
    llm: LLMProvidersConfig = field(default_factory=LLMProvidersConfig)
    playbook: PlaybookConfig = field(default_factory=PlaybookConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    imports: ImportsConfig = field(default_factory=ImportsConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvidersConfig":
        """Create config from YAML dictionary."""
        return cls(
            llm=LLMProvidersConfig.from_dict(data.get("providers", {})),
            playbook=PlaybookConfig.from_dict(data.get("playbook", {})),
            features=FeaturesConfig.from_dict(data.get("features", {})),
            imports=ImportsConfig.from_dict(data.get("imports", {})),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary (for saving/export)."""
        return {
            "providers": self.llm.to_dict(),
            "playbook": self.playbook.to_dict(),
            "features": self.features.to_dict(),
            "imports": self.imports.to_dict(),
        }

    def validate(self) -> List[str]:
        """
        Validate configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        # Check class paths contain module:class format
        for path in [
            self.llm.llm_provider,
            self.llm.fallback_provider,
            self.playbook.executor_agent,
            self.playbook.fallback_agent,
        ]:
            if path and ":" not in path:
                errors.append(f"Invalid class path format (missing ':'): {path}")

        return errors

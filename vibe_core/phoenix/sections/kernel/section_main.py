"""
Kernel Configuration - Core system component wiring from phoenix.yaml.

DUAL-LOAD STRATEGY:
    This section ONLY loads system.kernel components from phoenix.yaml.
    Other sections (agents, providers) have been extracted to their own
    config files. PhoenixConfig merges everything together.

    Migration path:
    1. [DONE] Create agents section -> config/agents.yaml
    2. [DONE] Create providers section -> config/providers.yaml
    3. [NOW] KernelConfig loads only system.kernel from phoenix.yaml
    4. [FUTURE] Remove agents/providers from phoenix.yaml (after deprecation period)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xc2e03e73"  # GenesisByte: parampara % 37 == 0

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """
    LLM Provider configuration.

    DEPRECATED: Use ProvidersConfig from providers section instead.
    Kept for backward compatibility - will be removed in v2.0.
    """

    llm_provider: str = "vibe_core.runtime.providers.anthropic:AnthropicProvider"
    fallback_provider: str = "vibe_core.runtime.providers.base:DefaultLLMProvider"

    @property
    def name(self) -> str:
        """Extract provider name from class path."""
        if "anthropic" in self.llm_provider.lower():
            return "anthropic"
        elif "openai" in self.llm_provider.lower():
            return "openai"
        elif "openrouter" in self.llm_provider.lower():
            return "openrouter"
        return "custom"


@dataclass
class FeaturesConfig:
    """
    Feature flags.

    DEPRECATED: Use ProvidersConfig.features from providers section instead.
    Kept for backward compatibility - will be removed in v2.0.
    """

    oauth_enforcement: bool = True
    live_fire_enabled: bool = True  # OPUS-076: NO PUSSY MODE - default ON
    performance_metrics: bool = True
    debug_mode: bool = False


@dataclass
class SystemConfig:
    """System kernel components wiring - the ONLY thing KernelConfig should own."""

    ledger: str = "vibe_core.kernel_impl:VibeLedgerImpl"
    scheduler: str = "vibe_core.kernel_impl:VibeSchedulerImpl"
    registry: str = "vibe_core.kernel_impl:ManifestRegistryImpl"
    kernel: str = "vibe_core.kernel_impl:VibeKernelImpl"


@dataclass
class AgentWiring:
    """
    Single agent wiring configuration.

    DEPRECATED: Use AgentDefinition from agents section instead.
    Kept for backward compatibility - will be removed in v2.0.
    """

    name: str
    class_path: str
    protocol: str = "VibeAgent"
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentWiring":
        return cls(
            name=data.get("name", ""),
            class_path=data.get("class", ""),
            protocol=data.get("protocol", "VibeAgent"),
            enabled=data.get("enabled", True),
        )


@dataclass
class PlaybookConfig:
    """
    Playbook executor configuration.

    DEPRECATED: Use ProvidersConfig.playbook from providers section instead.
    Kept for backward compatibility - will be removed in v2.0.
    """

    executor_agent: str = "vibe_core.agents.llm_agent:SimpleLLMAgent"
    fallback_agent: str = "vibe_core.agents.specialist_agent:SpecialistAgent"


@dataclass
class KernelConfig:
    """
    Core kernel configuration from phoenix.yaml.

    Auto-discovered by SectionLoader -> loads from config/phoenix.yaml

    DUAL-LOAD STRATEGY:
    - system: Core kernel component wiring (KEPT HERE)
    - providers, features, playbook, agents: DEPRECATED here,
      use dedicated sections (providers, agents) instead

    PhoenixConfig merges this with other sections. If new sections exist,
    they take precedence. If not, fallback to phoenix.yaml with deprecation warning.
    """

    # Class-level section identifier for auto-discovery
    section_id = "kernel"
    # Actual source file (not default kernel.yaml)
    source_file = "phoenix.yaml"

    # CORE: This is what KernelConfig SHOULD own
    system: SystemConfig = field(default_factory=SystemConfig)

    # DEPRECATED: These should come from dedicated sections
    # Kept for backward compatibility during migration
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    playbook: PlaybookConfig = field(default_factory=PlaybookConfig)
    agents: List[AgentWiring] = field(default_factory=list)
    import_order: List[str] = field(default_factory=list)

    # Track what was loaded from phoenix.yaml for deprecation warnings
    _loaded_from_phoenix: List[str] = field(default_factory=list, repr=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KernelConfig":
        """Create KernelConfig from parsed YAML dict."""
        loaded_from_phoenix = []

        # System components - CORE, always load
        system_data = data.get("system", {}).get("kernel", {})
        system = SystemConfig(
            ledger=system_data.get("ledger", SystemConfig.ledger),
            scheduler=system_data.get("scheduler", SystemConfig.scheduler),
            registry=system_data.get("registry", SystemConfig.registry),
            kernel=system_data.get("kernel", SystemConfig.kernel),
        )

        # Providers - DEPRECATED in phoenix.yaml
        providers_data = data.get("providers", {})
        if providers_data:
            loaded_from_phoenix.append("providers")
            logger.debug("Loading providers from phoenix.yaml (migrate to config/providers.yaml)")
        providers = ProviderConfig(
            llm_provider=providers_data.get("llm_provider", ProviderConfig.llm_provider),
            fallback_provider=providers_data.get("fallback_provider", ProviderConfig.fallback_provider),
        )

        # Features - DEPRECATED in phoenix.yaml
        features_data = data.get("features", {})
        if features_data:
            loaded_from_phoenix.append("features")
            logger.debug("Loading features from phoenix.yaml (migrate to config/providers.yaml)")
        features = FeaturesConfig(
            oauth_enforcement=features_data.get("oauth_enforcement", True),
            live_fire_enabled=features_data.get("live_fire_enabled", False),
            performance_metrics=features_data.get("performance_metrics", True),
            debug_mode=features_data.get("debug_mode", False),
        )

        # Playbook - DEPRECATED in phoenix.yaml
        playbook_data = data.get("playbook", {})
        if playbook_data:
            loaded_from_phoenix.append("playbook")
            logger.debug("Loading playbook from phoenix.yaml (migrate to config/providers.yaml)")
        playbook = PlaybookConfig(
            executor_agent=playbook_data.get("executor_agent", PlaybookConfig.executor_agent),
            fallback_agent=playbook_data.get("fallback_agent", PlaybookConfig.fallback_agent),
        )

        # Agents - DEPRECATED in phoenix.yaml
        agents_data = data.get("agents", {}).get("system_agents", [])
        if agents_data:
            loaded_from_phoenix.append("agents")
            logger.debug("Loading agents from phoenix.yaml (migrate to config/agents.yaml)")
        agents = [AgentWiring.from_dict(a) for a in agents_data]

        # Import order - DEPRECATED in phoenix.yaml
        import_order = data.get("imports", {}).get("order", [])
        if import_order:
            loaded_from_phoenix.append("imports")

        config = cls(
            system=system,
            providers=providers,
            features=features,
            playbook=playbook,
            agents=agents,
            import_order=import_order,
        )
        config._loaded_from_phoenix = loaded_from_phoenix

        return config

    def to_dict(self) -> Dict[str, Any]:
        """Serialize back to YAML-compatible dict."""
        return {
            "system": {
                "kernel": {
                    "ledger": self.system.ledger,
                    "scheduler": self.system.scheduler,
                    "registry": self.system.registry,
                    "kernel": self.system.kernel,
                }
            },
            "providers": {
                "llm_provider": self.providers.llm_provider,
                "fallback_provider": self.providers.fallback_provider,
            },
            "features": {
                "oauth_enforcement": self.features.oauth_enforcement,
                "live_fire_enabled": self.features.live_fire_enabled,
                "performance_metrics": self.features.performance_metrics,
                "debug_mode": self.features.debug_mode,
            },
            "playbook": {
                "executor_agent": self.playbook.executor_agent,
                "fallback_agent": self.playbook.fallback_agent,
            },
            "agents": {
                "system_agents": [
                    {"name": a.name, "class": a.class_path, "protocol": a.protocol, "enabled": a.enabled}
                    for a in self.agents
                ],
                "custom_agents": [],
            },
            "imports": {"order": self.import_order},
        }

    def validate(self) -> List[str]:
        """Validate configuration."""
        errors = []

        # Validate system component paths
        for attr in ["ledger", "scheduler", "registry", "kernel"]:
            path = getattr(self.system, attr)
            if path and ":" not in path:
                errors.append(f"system.{attr}: Invalid class path format (missing ':'): {path}")

        return errors

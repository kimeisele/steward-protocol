"""Kernel Configuration - System-level settings from phoenix.yaml."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ProviderConfig:
    """LLM Provider configuration."""

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
    """Feature flags."""

    oauth_enforcement: bool = True
    live_fire_enabled: bool = False
    performance_metrics: bool = True
    debug_mode: bool = False


@dataclass
class SystemComponentConfig:
    """Single system component wiring."""

    name: str
    class_path: str


@dataclass
class SystemConfig:
    """System kernel components wiring."""

    ledger: str = "vibe_core.kernel_impl:VibeLedgerImpl"
    scheduler: str = "vibe_core.kernel_impl:VibeSchedulerImpl"
    registry: str = "vibe_core.kernel_impl:ManifestRegistryImpl"
    kernel: str = "vibe_core.kernel_impl:VibeKernelImpl"


@dataclass
class AgentWiring:
    """Single agent wiring configuration."""

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
    """Playbook executor configuration."""

    executor_agent: str = "vibe_core.agents.llm_agent:SimpleLLMAgent"
    fallback_agent: str = "vibe_core.agents.specialist_agent:SpecialistAgent"


@dataclass
class KernelConfig:
    """
    Complete kernel configuration from phoenix.yaml.

    Auto-discovered by SectionLoader → loads from config/kernel.yaml
    """

    # Class-level section identifier for auto-discovery
    section_id = "kernel"

    system: SystemConfig = field(default_factory=SystemConfig)
    providers: ProviderConfig = field(default_factory=ProviderConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    playbook: PlaybookConfig = field(default_factory=PlaybookConfig)
    agents: List[AgentWiring] = field(default_factory=list)
    import_order: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KernelConfig":
        """Create KernelConfig from parsed YAML dict."""
        # System components
        system_data = data.get("system", {}).get("kernel", {})
        system = SystemConfig(
            ledger=system_data.get("ledger", SystemConfig.ledger),
            scheduler=system_data.get("scheduler", SystemConfig.scheduler),
            registry=system_data.get("registry", SystemConfig.registry),
            kernel=system_data.get("kernel", SystemConfig.kernel),
        )

        # Providers
        providers_data = data.get("providers", {})
        providers = ProviderConfig(
            llm_provider=providers_data.get("llm_provider", ProviderConfig.llm_provider),
            fallback_provider=providers_data.get("fallback_provider", ProviderConfig.fallback_provider),
        )

        # Features
        features_data = data.get("features", {})
        features = FeaturesConfig(
            oauth_enforcement=features_data.get("oauth_enforcement", True),
            live_fire_enabled=features_data.get("live_fire_enabled", False),
            performance_metrics=features_data.get("performance_metrics", True),
            debug_mode=features_data.get("debug_mode", False),
        )

        # Playbook
        playbook_data = data.get("playbook", {})
        playbook = PlaybookConfig(
            executor_agent=playbook_data.get("executor_agent", PlaybookConfig.executor_agent),
            fallback_agent=playbook_data.get("fallback_agent", PlaybookConfig.fallback_agent),
        )

        # Agents
        agents_data = data.get("agents", {}).get("system_agents", [])
        agents = [AgentWiring.from_dict(a) for a in agents_data]

        # Import order
        import_order = data.get("imports", {}).get("order", [])

        return cls(
            system=system,
            providers=providers,
            features=features,
            playbook=playbook,
            agents=agents,
            import_order=import_order,
        )

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

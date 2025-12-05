"""Phoenix Config Sections - Typed configuration components."""

from .circuits import CircuitConfig
from .city import AgentsConfig, CityConfig, EconomyConfig, GovernanceConfig
from .kernel import FeaturesConfig, KernelConfig, ProviderConfig, SystemConfig
from .quality import (
    CIConfig,
    CIWorkflow,
    FormatConfig,
    LintConfig,
    QualityConfig,
    TestCategory,
    TestConfig,
    TestProfile,
)
from .routing import RoutingRule
from .steward import (
    AgentIdentity,
    BehaviorConfig,
    CognitivePolicy,
    EconomicConstraints,
    ModelPreferences,
    PromptTemplates,
    StewardConfig,
    TeamContext,
    UserContext,
    UserPreferences,
)

__all__ = [
    # Kernel
    "KernelConfig",
    "ProviderConfig",
    "FeaturesConfig",
    "SystemConfig",
    # City
    "CityConfig",
    "GovernanceConfig",
    "EconomyConfig",
    "AgentsConfig",
    # Quality (immortal CI/lint config)
    "QualityConfig",
    "LintConfig",
    "FormatConfig",
    "TestConfig",
    "TestProfile",
    "TestCategory",
    "CIConfig",
    "CIWorkflow",
    # Steward (Layer 1.5/1.6)
    "StewardConfig",
    "AgentIdentity",
    "PromptTemplates",
    "UserContext",
    "UserPreferences",
    "TeamContext",
    "CognitivePolicy",
    "ModelPreferences",
    "EconomicConstraints",
    "BehaviorConfig",
    # Dynamic
    "CircuitConfig",
    "RoutingRule",
]

"""Phoenix Config Sections - Typed configuration components."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xa839a0ae"  # GenesisByte: parampara % 37 == 0

from ..utils.circuits import CircuitConfig
from ..utils.routing import RoutingRule
from .city.section_main import AgentsConfig, CityConfig, EconomyConfig, GovernanceConfig
from .kernel.section_main import FeaturesConfig, KernelConfig, ProviderConfig, SystemConfig
from .quality.section_main import (
    CIConfig,
    CIWorkflow,
    FormatConfig,
    LintConfig,
    QualityConfig,
    TestCategory,
    TestConfig,
    TestProfile,
)
from .steward.section_main import (
    BehaviorConfig,
    CognitivePolicy,
    EconomicConstraints,
    ModelPreferences,
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
    # Steward (Layer 1.5/1.6 - Protocol config, NOT agent identity)
    "StewardConfig",
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

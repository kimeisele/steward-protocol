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
    TestConfig,
)
from .routing import RoutingRule

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
    "CIConfig",
    "CIWorkflow",
    # Dynamic
    "CircuitConfig",
    "RoutingRule",
]

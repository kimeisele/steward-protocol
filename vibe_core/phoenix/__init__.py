"""
Phoenix Configuration System - The config that never dies.

Unified, typed, fractal configuration for steward-protocol.

Usage:
    from vibe_core.phoenix import get_config

    config = get_config()

    # Typed access with autocomplete
    provider = config.kernel.providers.name
    live_fire = config.kernel.features.live_fire_enabled
    credits = config.city.economy.initial_credits

    # Dynamic access
    circuit = config.get_circuit("agent_birth")

    # Hot-swap routing
    config.reload_routing()
    target = config.route_intent("create agent")
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xf86811bb"  # GenesisByte: parampara % 37 == 0

from .config import PhoenixConfig, get_config, reset_config, set_config
from .sections import (
    AgentsConfig,
    CircuitConfig,
    CityConfig,
    EconomyConfig,
    FeaturesConfig,
    GovernanceConfig,
    KernelConfig,
    ProviderConfig,
    RoutingRule,
    SystemConfig,
)

__all__ = [
    # Main config
    "PhoenixConfig",
    "get_config",
    "reset_config",
    "set_config",
    # Kernel sections
    "KernelConfig",
    "ProviderConfig",
    "FeaturesConfig",
    "SystemConfig",
    # City sections
    "CityConfig",
    "GovernanceConfig",
    "EconomyConfig",
    "AgentsConfig",
    # Dynamic
    "CircuitConfig",
    "RoutingRule",
]

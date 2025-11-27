"""
THE DHARMA ENGINE: Configuration-Driven System Architecture

This module provides the configuration system for Steward Protocol.
Configuration is the DNA of the system - if code dies, config resurrects it.
"""

from .schema import CityConfig, load_config
from .loader import ConfigLoader

# Alias for backward compatibility (Phase 2 compatibility)
# TODO: Remove in v2.0
# Why: load_config is the canonical name; get_config was introduced
# as an alias to provide a more intuitive interface during the Phase 2 migration
# (legacy code used get_config; new code should use load_config)
# Migration path: Update all imports from `get_config` to `load_config`
get_config = load_config

__all__ = ["CityConfig", "load_config", "ConfigLoader", "get_config"]

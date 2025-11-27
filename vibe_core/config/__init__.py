"""
THE DHARMA ENGINE: Configuration-Driven System Architecture

This module provides the configuration system for Steward Protocol.
Configuration is the DNA of the system - if code dies, config resurrects it.
"""

from .schema import CityConfig, load_config
from .loader import ConfigLoader

# Alias for compatibility
get_config = load_config

__all__ = ["CityConfig", "load_config", "ConfigLoader", "get_config"]

"""
Unified Loader System - VEDA-4 Pattern for ALL Item Types.

FRAKTAL PRINCIPLE:
    Agents, Plugins, Sections, Workflows - ALL follow the same pattern.
    One loader to rule them all.

VEDA-4 LOADER PATTERN:
    SHABDA   → scan_directory() + load_manifest()
    ARTHA    → validate_manifest()
    PRATYAYA → load_config() + check_dependencies()
    KARMA    → instantiate()

Usage:
    from vibe_core.loaders import UnifiedLoader, PluginLoader, AgentLoader

    # Discover all plugins
    plugins, meta = PluginLoader.discover_and_load()

    # Discover all agents
    agents, meta = AgentLoader.discover_and_load()
"""

from .base_loader import ItemMeta, LoaderRegistry, UnifiedLoader

__all__ = [
    "UnifiedLoader",
    "ItemMeta",
    "LoaderRegistry",
]

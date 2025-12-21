"""
NodePulse Plugin - OPUS-166

Manages node.json lifecycle for all cartridges.
Creates on boot, updates on pulse with KALA state, deletes on shutdown.
"""

from .plugin_main import NodePulsePlugin

__all__ = ["NodePulsePlugin"]

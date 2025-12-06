"""
OPUS - Live System Dashboard Package.

Sub-plugin of InterfacePlugin.
Auto-discovers panels from opus/panels/.
"""

from .renderer import OpusRenderer

__all__ = ["OpusRenderer"]

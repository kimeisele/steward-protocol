"""
OPUS Panels - Hot-swappable dashboard components.

Each panel is auto-discovered via VEDA-4 pattern.
Add a new panel by creating a .py file that extends OpusPanel.
"""

from .base_panel import OpusPanel

__all__ = ["OpusPanel"]

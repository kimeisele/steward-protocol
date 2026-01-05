"""
NAGA Flood Classes - Surgical Method Overrides.

Each Flood Class:
1. Inherits from appropriate NAGA Mixins (capabilities)
2. Inherits from original REBEL class
3. Overrides ONLY the methods that need protection
4. Uses super() for clean chaining

"Der Chirurg wählt das Skalpell." - Targeted, not blanket.

Usage:
    # Original (REBEL):
    sync = CISyncService()

    # Flooded (NAGA-protected):
    sync = FloodedCISyncService()

    # Same interface, protected execution.
"""

from .ouroboros import FloodedCISyncService
from .plugin_service import FloodedPluginService
from .task_manager import FloodedTaskManager

__all__ = [
    "FloodedCISyncService",
    "FloodedPluginService",
    "FloodedTaskManager",
]

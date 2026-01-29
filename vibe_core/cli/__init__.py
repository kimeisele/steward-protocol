"""
Fractal CLI System - Auto-discoverable, plugin-based commands.

GAD-000 Compliant: All handlers return data, CLI handles rendering.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x717c7f16"  # GenesisByte: parampara % 37 == 0

from typing import TYPE_CHECKING

# Eager loading: Entry points (Lightweight)
# main.py is optimized to have ZERO heavy imports at top level.
from .main import cli_entry, main

if TYPE_CHECKING:
    from .executor import CLIExecutor
    from .legacy import StewardCLI
    from .loader import CLILoader
    from .monitor_loader import MonitorLoader
    from .monitors import (
        MonitorDefinition,
        MonitorSnapshot,
        MonitorType,
        MonitorValue,
        SystemMonitor,
    )
    from .protocol import (
        CLIArg,
        CLICommand,
        CLIResponse,
        ExecutionMode,
        ProgressUpdate,
    )
    from .renderer import CLIRenderer, get_renderer
    from .unified_cli import UnifiedCLI


def __getattr__(name: str):
    """Lazy load CLI components."""
    
    # Components
    if name == "CLIExecutor":
        from .executor import CLIExecutor
        return CLIExecutor
    
    if name == "StewardCLI":
        from .legacy import StewardCLI
        return StewardCLI
        
    if name == "CLILoader":
        from .loader import CLILoader
        return CLILoader
        
    if name == "MonitorLoader":
        from .monitor_loader import MonitorLoader
        return MonitorLoader
        
    if name == "UnifiedCLI":
        from .unified_cli import UnifiedCLI
        return UnifiedCLI

    # Monitors
    if name in ("MonitorDefinition", "MonitorSnapshot", "MonitorType", "MonitorValue", "SystemMonitor"):
        from . import monitors
        return getattr(monitors, name)
        
    # Protocol
    if name in ("CLIArg", "CLICommand", "CLIResponse", "ExecutionMode", "ProgressUpdate"):
        from . import protocol
        return getattr(protocol, name)
        
    # Renderer
    if name in ("CLIRenderer", "get_renderer"):
        from . import renderer
        return getattr(renderer, name)
        
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Protocol
    "CLIArg",
    "CLICommand",
    "CLIResponse",
    "ExecutionMode",
    "ProgressUpdate",
    # Components
    "CLILoader",
    "CLIExecutor",
    "CLIRenderer",
    "get_renderer",
    # Monitors (Glass Box)
    "MonitorLoader",
    "MonitorDefinition",
    "MonitorSnapshot",
    "MonitorType",
    "MonitorValue",
    "SystemMonitor",
    # Entry points
    "main",
    "cli_entry",
    "UnifiedCLI",
    "StewardCLI",
]

"""
Fractal CLI System - Auto-discoverable, plugin-based commands.

GAD-000 Compliant: All handlers return data, CLI handles rendering.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x717c7f16"  # GenesisByte: parampara % 37 == 0

from .executor import CLIExecutor
from .legacy import StewardCLI
from .loader import CLILoader
from .main import cli_entry, main
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

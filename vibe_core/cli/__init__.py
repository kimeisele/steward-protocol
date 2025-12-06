"""
Fractal CLI System - Auto-discoverable, plugin-based commands.

GAD-000 Compliant: All handlers return data, CLI handles rendering.
"""

from .executor import CLIExecutor
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
]

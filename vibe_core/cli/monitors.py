"""
Monitor Protocol - Introspection system for the Fractal CLI.

"The Glass Box" - Allows the CLI to SEE into the system's internal highways
without hardcoding specific status commands.

VEDA-4 Pattern:
  SHABDA   → MonitorLoader discovers monitors from plugins
  ARTHA    → Monitor protocol defines what can be observed
  PRATYAYA → Each monitor validates its own data
  KARMA    → steward observe executes introspection
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x7d0ea8c9"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class MonitorType(Enum):
    """Categories of system monitors."""

    QUEUE = "queue"  # Task queues, message queues
    ROUTING = "routing"  # Routing tables, patch bays
    STATE = "state"  # System state, configuration
    METRICS = "metrics"  # Counters, gauges, histograms
    HEALTH = "health"  # Health checks, liveness
    AGENTS = "agents"  # Agent status, lifecycle


@dataclass
class MonitorValue:
    """A single observable value."""

    name: str
    value: Any
    unit: Optional[str] = None  # "tasks", "ms", "bytes", etc.
    status: Optional[str] = None  # "ok", "warning", "critical"


@dataclass
class MonitorSnapshot:
    """
    Point-in-time snapshot of a monitor.

    GAD-000 Compliant: Serializable to JSON.
    """

    monitor_id: str
    timestamp: str
    values: List[MonitorValue] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "monitor_id": self.monitor_id,
            "timestamp": self.timestamp,
            "values": [
                {
                    "name": v.name,
                    "value": v.value,
                    "unit": v.unit,
                    "status": v.status,
                }
                for v in self.values
            ],
            "metadata": self.metadata,
        }


class SystemMonitor(ABC):
    """
    Base class for system monitors.

    Plugins implement this to expose observable state.
    The CLI discovers these via get_monitors() on KernelPlugin.
    """

    @property
    @abstractmethod
    def monitor_id(self) -> str:
        """
        Unique identifier for this monitor.

        Format: plugin_id:monitor_name
        Example: milk_ocean:queue, matrix:routing
        """
        pass

    @property
    @abstractmethod
    def monitor_type(self) -> MonitorType:
        """Category of this monitor."""
        pass

    @property
    def description(self) -> str:
        """Human-readable description."""
        return ""

    @abstractmethod
    def snapshot(self) -> MonitorSnapshot:
        """
        Take a point-in-time snapshot.

        Returns:
            MonitorSnapshot with current values
        """
        pass


@dataclass
class MonitorDefinition:
    """
    Lightweight definition for monitor discovery.

    Used by CLI to list available monitors without
    actually invoking them.
    """

    monitor_id: str
    monitor_type: MonitorType
    plugin_id: str
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.monitor_id,
            "type": self.monitor_type.value,
            "plugin": self.plugin_id,
            "description": self.description,
        }


# Type alias for monitor registry
MonitorRegistry = Dict[str, MonitorDefinition]

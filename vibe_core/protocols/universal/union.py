"""
UNION PROTOCOL - The State of the Union (Layer 1)

"Ekam Sat Vipra Bahudha Vadanti" - Truth is One, the wise call it by many names.

This protocol provides a unified view of all living entities (Nagas, Agents, Plugins)
and traces their heritage back to their respective Protocols.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Protocol, runtime_checkable


@dataclass
class EntityStatus:
    """The status of a living entity in the Union."""

    id: str
    type: str  # "naga", "agent", "plugin", "kernel"
    status: str  # "ACTIVE", "DORMANT", "DEGRADED"
    protocol: Optional[str]  # The Protocol class path this entity obeys
    is_living: bool  # True if heartbeat is fresh
    tuv_score: float  # Compliance score from 0.0 to 1.0
    last_heartbeat: Optional[datetime]


@runtime_checkable
class UnionProtocol(Protocol):
    """
    The Union Protocol.

    Provides the 'State of the Union' report.
    Used by the Gateway to present the living reality of the system.
    """

    def get_living_entities(self) -> List[EntityStatus]:
        """
        List all entities that are currently active and registered.
        Traces every entity back to its Protocol heritage.
        """
        ...

    def get_union_summary(self) -> Dict[str, object]:
        """
        Get high-level statistics of the Union.
        Includes population counts and average compliance scores.
        """
        ...

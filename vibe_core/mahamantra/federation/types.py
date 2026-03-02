"""
Federation Message Types — Cross-Repo Communication Format

Compatible with agent-city's federation_nadi.py format (100% compatible).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x7b3899f2"

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# PRIORITY LEVELS (Guna-Based, same as agent-city)
# =============================================================================


class FederationPriority(IntEnum):
    """Priority levels for federation messages (Guna-based)."""

    TAMAS = 0  # Background/lowest
    RAJAS = 1  # Normal/medium
    SATTVA = 2  # Important/high
    SUDDHA = 3  # Critical/highest


# Constants for backward compatibility
TAMAS = FederationPriority.TAMAS
RAJAS = FederationPriority.RAJAS
SATTVA = FederationPriority.SATTVA
SUDDHA = FederationPriority.SUDDHA

# =============================================================================
# FEDERATION MESSAGE (Cross-Repo Communication)
# =============================================================================


@dataclass
class FederationMessage:
    """
    Federation Message — agent-city ↔ steward-protocol communication.

    Fields:
        source: Sending system (e.g., "moksha", "karma", "genesis")
        target: Receiving system (e.g., "steward-protocol", "agent-city")
        operation: Message type (e.g., "city_report", "create_mission")
        payload: Message data (any JSON-serializable dict)
        priority: Guna-based priority (0-3)
        correlation_id: For tracking request/response chains
        timestamp: UNIX timestamp (auto-populated on creation)
        ttl_s: Time-to-live in seconds (0 = never expires)
    """

    source: str
    target: str
    operation: str
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = field(default_factory=lambda: RAJAS)
    correlation_id: str = ""
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    ttl_s: float = 900.0  # 15 minutes for federation messages

    @property
    def is_expired(self) -> bool:
        """Check if message has exceeded TTL."""
        if self.ttl_s == 0:
            return False
        now = datetime.now().timestamp()
        return (now - self.timestamp) > self.ttl_s

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "source": self.source,
            "target": self.target,
            "operation": self.operation,
            "payload": self.payload,
            "priority": self.priority,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "ttl_s": self.ttl_s,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FederationMessage":
        """Deserialize from JSON-compatible dict."""
        return FederationMessage(
            source=data.get("source", ""),
            target=data.get("target", ""),
            operation=data.get("operation", ""),
            payload=data.get("payload", {}),
            priority=data.get("priority", RAJAS),
            correlation_id=data.get("correlation_id", ""),
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            ttl_s=data.get("ttl_s", 900.0),
        )


# =============================================================================
# CITY REPORT (agent-city Status Report)
# =============================================================================


@dataclass(frozen=True)
class CityReport:
    """
    City Report — agent-city heartbeat and status information.

    Represents the state of the agent-city federation at a given moment.
    """

    heartbeat: int
    timestamp: float
    population: int
    alive: int
    dead: int
    elected_mayor: Optional[str]
    council_seats: int
    open_proposals: int
    chain_valid: bool
    recent_actions: List[str] = field(default_factory=list)
    contract_status: Dict[str, Any] = field(default_factory=dict)
    mission_results: List[Dict[str, Any]] = field(default_factory=list)
    directive_acks: List[str] = field(default_factory=list)
    pr_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "heartbeat": self.heartbeat,
            "timestamp": self.timestamp,
            "population": self.population,
            "alive": self.alive,
            "dead": self.dead,
            "elected_mayor": self.elected_mayor,
            "council_seats": self.council_seats,
            "open_proposals": self.open_proposals,
            "chain_valid": self.chain_valid,
            "recent_actions": list(self.recent_actions),
            "contract_status": dict(self.contract_status),
            "mission_results": [dict(m) for m in self.mission_results],
            "directive_acks": list(self.directive_acks),
            "pr_results": [dict(p) for p in self.pr_results],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CityReport":
        """Deserialize from JSON-compatible dict."""
        return CityReport(
            heartbeat=data.get("heartbeat", 0),
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            population=data.get("population", 0),
            alive=data.get("alive", 0),
            dead=data.get("dead", 0),
            elected_mayor=data.get("elected_mayor"),
            council_seats=data.get("council_seats", 0),
            open_proposals=data.get("open_proposals", 0),
            chain_valid=data.get("chain_valid", False),
            recent_actions=data.get("recent_actions", []),
            contract_status=data.get("contract_status", {}),
            mission_results=data.get("mission_results", []),
            directive_acks=data.get("directive_acks", []),
            pr_results=data.get("pr_results", []),
        )


# =============================================================================
# FEDERATION DIRECTIVE (Mothership → Consumer Command)
# =============================================================================


@dataclass(frozen=True)
class FederationDirective:
    """
    Federation Directive — Command from steward-protocol to agent-city.

    Directives are persisted as files and agent-city polls for processing.
    """

    id: str
    directive_type: str  # e.g., "create_mission", "freeze_agent"
    params: Dict[str, Any]  # Operation parameters
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())  # Creation time
    source: str = "steward-protocol"  # Origin system

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "directive_type": self.directive_type,
            "params": dict(self.params),
            "timestamp": self.timestamp,
            "source": self.source,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "FederationDirective":
        """Deserialize from JSON-compatible dict."""
        return FederationDirective(
            id=data.get("id", ""),
            directive_type=data.get("directive_type", ""),
            params=data.get("params", {}),
            timestamp=data.get("timestamp", datetime.now().timestamp()),
            source=data.get("source", "steward-protocol"),
        )

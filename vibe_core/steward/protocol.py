"""
Agent Protocol - Duck-typed interface for agents.

CONSOLIDATION: AgentManifest is re-exported from vibe_core/protocols/agent.py
This file adds AgentProtocol (duck-typed interface) and is_valid_agent helper.

FRACTAL PATTERN:
    phoenix/section_loader.py → ConfigSectionProtocol
    steward/protocol.py       → AgentProtocol
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xcf4441d6"  # GenesisByte: parampara % 37 == 0

from typing import Any, Dict, List, Protocol, runtime_checkable

# Re-export AgentManifest from canonical location (NO DUPLICATION)
from vibe_core.protocols.agent import AgentManifest


@runtime_checkable
class AgentProtocol(Protocol):
    """
    Duck-typed protocol for agents.

    Any class with these attributes/methods is a valid agent.
    This avoids circular import issues and enables flexible implementations.
    """

    agent_id: str
    name: str
    capabilities: List[str]

    def process(self, task: Any) -> Dict[str, Any]:
        """Process a task from the kernel scheduler."""
        ...

    def get_manifest(self) -> AgentManifest:
        """Return this agent's manifest (identity + capabilities)."""
        ...


def is_valid_agent(obj: Any) -> bool:
    """
    Check if an object implements the AgentProtocol.

    Args:
        obj: Object to check

    Returns:
        True if object is a valid agent
    """
    if not hasattr(obj, "agent_id") or not isinstance(obj.agent_id, str):
        return False
    if not hasattr(obj, "name"):
        return False
    if not hasattr(obj, "process") or not callable(getattr(obj, "process")):
        return False
    return True


__all__ = [
    "AgentManifest",  # Re-exported from vibe_core/protocols/agent.py
    "AgentProtocol",
    "is_valid_agent",
]

"""
VibeAgent Protocol - Re-export from canonical location.

CONSOLIDATION: All agent protocol classes now live in vibe_core/protocols/agent.py
This file re-exports for backwards compatibility.
"""

# Re-export everything from canonical location
from vibe_core.protocols.agent import (
    AgentManifest,
    AgentResponse,
    Capability,
    VibeAgent,
)

__all__ = [
    "AgentManifest",
    "AgentResponse",
    "Capability",
    "VibeAgent",
]

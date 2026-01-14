"""
GATEWAY - The ONE Entry Point
=============================

ALL entry points converge here:

    from vibe_core.gateway import execute, chat, agent_call

    # CLI-style
    result = execute("status")
    result = execute("samskara", ["discover"])

    # Natural language
    result = chat("show system status")

    # Agent-to-agent
    result = agent_call("spawn", ["worker"])

Protocol-first. SSOT. No manual wiring.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x7d3e1a82"

from vibe_core.gateway.mahamantra_gateway import (
    MahamantraGateway,
    get_gateway,
    execute,
    chat,
    agent_call,
)

__all__ = [
    "MahamantraGateway",
    "get_gateway",
    "execute",
    "chat",
    "agent_call",
]

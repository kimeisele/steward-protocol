"""
MAHAMANTRA GATEWAY - The ONE Entry Point
=========================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo" - I am seated in everyone's heart.

THIS IS IT. The bridge between GatewayProtocol and mahamantra.execute().

ALL entry points converge here:
    CLI      → gateway.receive() → mahamantra
    HTTP     → gateway.receive() → mahamantra
    CHAT     → gateway.receive() → mahamantra
    AGENT    → gateway.receive() → mahamantra

NO MANUAL WIRING. Protocol-first. SSOT.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x8c4e2f91"

from typing import Dict, List, Optional

from vibe_core.protocols.gateway import (
    EntryType,
    GatewayProtocol,
    GatewayRequest,
    GatewayResponse,
    create_request,
)


class MahamantraGateway(GatewayProtocol):
    """
    THE Gateway implementation.

    Bridges GatewayProtocol to mahamantra.execute().
    All rivers flow to the sea.
    """

    def receive(self, request: GatewayRequest) -> GatewayResponse:
        """
        Receive and process ANY request.

        CLI, HTTP, CHAT, AGENT - all come here.
        Mahamantra routes. Mahajana executes.
        """
        from vibe_core.mahamantra import mahamantra

        command = request["command"]
        args = request.get("args", [])
        entry_type = request.get("entry_type", EntryType.CLI.value)

        # Execute through mahamantra
        result = mahamantra.execute(command, args)

        return GatewayResponse(
            success=result["success"],
            exit_code=result["exit_code"],
            output=result.get("output", ""),
            error=result.get("error"),
            position=result["position"],
            guardian=result["guardian"],
            quarter=result["quarter"],
            guna=result["guna"],
            entry_type=entry_type,
            routed_via="mahamantra",
        )

    def route(self, command: str) -> Dict[str, object]:
        """Route command to position/guardian."""
        from vibe_core.mahamantra import mahamantra
        return mahamantra.route(command)


# =============================================================================
# SINGLETON - One Gateway to rule them all
# =============================================================================

_gateway: Optional[MahamantraGateway] = None


def get_gateway() -> MahamantraGateway:
    """Get the singleton gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = MahamantraGateway()
    return _gateway


# =============================================================================
# CONVENIENCE FUNCTIONS - Thin wrappers
# =============================================================================

def execute(command: str, args: Optional[List[str]] = None) -> GatewayResponse:
    """
    Execute a command through the gateway.

    THE SIMPLEST INTERFACE:
        from vibe_core.gateway import execute
        result = execute("status")
    """
    request = create_request(command, args or [], EntryType.CLI)
    return get_gateway().receive(request)


def chat(message: str) -> GatewayResponse:
    """
    Natural language through the gateway.

        from vibe_core.gateway import chat
        result = chat("show system status")
    """
    request = create_request(message, [], EntryType.CHAT)
    return get_gateway().receive(request)


def agent_call(command: str, args: Optional[List[str]] = None) -> GatewayResponse:
    """
    Agent-to-agent syscall through the gateway.

        from vibe_core.gateway import agent_call
        result = agent_call("spawn", ["worker"])
    """
    request = create_request(command, args or [], EntryType.AGENT)
    return get_gateway().receive(request)


__all__ = [
    "MahamantraGateway",
    "get_gateway",
    "execute",
    "chat",
    "agent_call",
]

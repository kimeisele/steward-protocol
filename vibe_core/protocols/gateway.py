"""
GATEWAY PROTOCOL - The Highway Infrastructure
==============================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart."
— Bhagavad Gita 15.15

ARCHITECTURE:
=============

    [Operators]               [Gateways]            [Core]
    TerminalOperator ──┐
    LocalLLMOperator ──┼──→ GatewayProtocol ──→ Mahamantra ──→ Mahajana
    DegradedOperator ──┘                          (Singularity)
           ↑
       FALLBACK (System NEVER crashes)

GATEWAY TYPES (Highways to Mahamantra):
=======================================

    CLIGateway   - steward <command>      (main.py)
    HTTPGateway  - REST API               (gateway/api.py)
    ChatGateway  - steward chat           (Kapila @ pos 6)
    AgentGateway - Inter-agent syscalls   (Federation)

ALL RIVERS FLOW TO THE SEA (Mahamantra).
ALL RESPONSES FLOW BACK (Prasadam).

ROBUSTNESS:
===========

    1. Try primary operator (Terminal/LLM)
    2. Fallback to DegradedOperator
    3. System NEVER crashes
    4. TAMAS operations require confirmation

WATERTIGHT: No Any types. Protocol-first.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xa6e9bcf8"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Protocol, TypedDict, runtime_checkable


# =============================================================================
# TYPES - Strict, No Any
# =============================================================================

class EntryType(str, Enum):
    """How the request entered the system."""
    CLI = "cli"           # steward <command>
    HTTP = "http"         # API gateway
    CHAT = "chat"         # steward chat / natural language
    AGENT = "agent"       # Programmatic / agent syscall
    INTERNAL = "internal" # System-to-system


class GatewayRequest(TypedDict):
    """
    A request entering the gateway.

    WATERTIGHT: All fields typed explicitly.
    """
    entry_type: str       # EntryType value
    command: str          # The command/message
    args: List[str]       # Arguments
    context: Dict[str, str]  # Additional context (session_id, etc.)


class GatewayResponse(TypedDict):
    """
    Response from the gateway.

    WATERTIGHT: All fields typed explicitly.
    """
    success: bool
    exit_code: int
    output: str
    error: Optional[str]
    # Routing info
    position: int         # 0-15
    guardian: str         # mahajana name
    quarter: str          # genesis/dharma/karma/moksha
    guna: str             # sattva/rajas/tamas/vishuddha
    # Metadata
    entry_type: str       # How it came in
    routed_via: str       # How it was routed


# =============================================================================
# THE GATEWAY PROTOCOL
# =============================================================================

@runtime_checkable
class GatewayProtocol(Protocol):
    """
    THE central entry protocol.

    All requests flow through this.
    All responses flow back through this.

    IMPLEMENTATIONS:
        - MahamantraLotus (vibe_core/mahamantra/)
        - NetworkGateway (vibe_core/gateway/)
        - Future: FederatedGateway, etc.

    THE CONTRACT:
        1. receive() - Accept any request
        2. route() - Determine mahajana
        3. execute() - Process request
        4. respond() - Return response

    SANKIRTAN: Congregational - everything flows together.
    """

    def receive(self, request: GatewayRequest) -> GatewayResponse:
        """
        Receive and process a request.

        This is THE entry point. Everything comes here.

        Args:
            request: The incoming request (CLI, HTTP, Chat, Agent)

        Returns:
            GatewayResponse with result
        """
        ...

    def route(self, command: str) -> Dict[str, object]:
        """
        Route command to position/guardian.

        Args:
            command: The command string

        Returns:
            Dict with position, guardian, quarter, guna
        """
        ...


# =============================================================================
# IMPLEMENTATION NOTE
# =============================================================================
#
# The IMPLEMENTATION of GatewayProtocol is: mahamantra.execute()
#
#     from vibe_core.mahamantra import mahamantra
#     result = mahamantra.execute(command, args)
#
# mahamantra.execute() already provides:
#     - Route to position/guardian
#     - Guna QoS (Sattva/Rajas/Tamas/Vishuddha)
#     - Protocol execution
#     - Legacy fallback
#     - Never crashes
#
# NO separate BaseGateway class needed. Protocol = Interface only.
#
# =============================================================================


# =============================================================================
# HELPER: Create Request
# =============================================================================

def create_request(
    command: str,
    args: Optional[List[str]] = None,
    entry_type: EntryType = EntryType.CLI,
    context: Optional[Dict[str, str]] = None,
) -> GatewayRequest:
    """
    Create a gateway request.

    Convenience function for creating properly typed requests.
    """
    return GatewayRequest(
        entry_type=entry_type.value,
        command=command,
        args=args or [],
        context=context or {},
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "EntryType",
    "GatewayRequest",
    "GatewayResponse",
    # Protocol (Interface only - implementation is mahamantra.execute())
    "GatewayProtocol",
    # Helper
    "create_request",
]

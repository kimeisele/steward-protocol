"""
GOVARDHAN GATEWAY — The Boundary Layer (Imperative Shell)
==========================================================

"govardhanaṁ parvataṁ ekena hastena dhārayat"
"He held Govardhan Hill with one hand, sheltering all beneath."
— Srimad Bhagavatam 10.25

ARCHITECTURE: Functional Core / Imperative Shell
=================================================
__call__() in lotus_core.py is the FUNCTIONAL CORE (Vrindavan).
Pure computation. Deterministic. No side-effects.

THIS FILE is the IMPERATIVE SHELL (Govardhan).
The 5 Pancha Tattva Gates live HERE — at the boundary between
the outside world (Legacy, CLI, HTTP, Agents) and the pure core.

FLOW:
    Outside → receive() → PARSE → VALIDATE → __call__() → RESULT → SYNC → Outside
                           ↑                                              ↑
                     Boundary IN                                    Boundary OUT

The gates are border control, not highway checkpoints.
Everything under Govardhan is protected.

ALL entry points converge here:
    CLI      → gateway.receive() → govardhan
    HTTP     → gateway.receive() → govardhan
    CHAT     → gateway.receive() → govardhan
    AGENT    → gateway.receive() → govardhan
    LEGACY   → gateway.offer()   → govardhan (I/O only, no pipeline)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x30983307"

import logging
from typing import Dict, List, Optional

from vibe_core.protocols.gateway import (
    EntryType,
    GatewayProtocol,
    GatewayRequest,
    GatewayResponse,
    create_request,
)

logger = logging.getLogger("GOVARDHAN")


class GovardhanGateway(GatewayProtocol):
    """
    The Boundary Layer — Govardhan Hill.

    Krishna holds the hill with one hand. Everything beneath is sheltered.
    The 5 Pancha Tattva Gates fire HERE at the boundary:

        PARSE    — What is this? (input validation)
        VALIDATE — Is it legitimate? (seed/parampara)
        EXECUTE  — Pure computation via __call__() (Vrindavan)
        RESULT   — Is the output valid? (result verification)
        SYNC     — Side-effects: I/O, state, response (governance)
    """

    def receive(self, request: GatewayRequest) -> GatewayResponse:
        """
        Receive and process ANY request through the 5 Gates.

        This is the ONE entry point. CLI, HTTP, CHAT, AGENT — all come here.
        The gates fire at the boundary, then the pure core computes.
        """
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate

        lotus = get_mahamantra()
        command = request["command"]
        args = request.get("args", [])
        entry_type = request.get("entry_type", EntryType.CLI.value)

        # =================================================================
        # GATE 0: PARSE — What is this?
        # Boundary IN: validate the request shape before it enters.
        # =================================================================
        lotus._fire_gate(TattvaGate.PARSE, {
            "input_data": command,
            "entry_type": entry_type,
            "args": args,
        })

        # =================================================================
        # GATE 1: VALIDATE — Is it legitimate?
        # Compress to seed, verify parampara at the border.
        # =================================================================
        lotus._fire_gate(TattvaGate.VALIDATE, {
            "input_text": command,
            "seed": None,  # seed computed inside __call__
            "input_coords": None,
        })

        # =================================================================
        # GATE 2: EXECUTE — Pure computation (Vrindavan).
        # __call__() is deterministic. No side-effects.
        # =================================================================
        lotus._fire_gate(TattvaGate.EXECUTE, {
            "seed": None,
            "attractor": None,
            "parampara_verified": None,
        })

        try:
            result = lotus(command)
        except Exception as exc:
            logger.error("Govardhan: computation failed: %s", exc)
            return GatewayResponse(
                success=False,
                exit_code=1,
                output="",
                error=str(exc),
                position=-1,
                guardian="unknown",
                quarter="unknown",
                guna="tamas",
                entry_type=entry_type,
                routed_via="govardhan[error]",
            )

        # =================================================================
        # GATE 3: RESULT — Is the output valid?
        # Boundary OUT: verify the computation result.
        # =================================================================
        lotus._fire_gate(TattvaGate.RESULT, {
            "attractor": result.get("vibration", {}).get("attractor"),
            "resonant_words": result.get("smaranam", ()),
            "verse_result": result.get("verse"),
        })

        # =================================================================
        # GATE 4: SYNC — Side-effects (governance).
        # This is where I/O happens. The pure core never touches disk.
        # =================================================================
        lotus._fire_gate(TattvaGate.SYNC, {
            "position": result.get("position"),
            "guardian": result.get("guardian"),
            "seed": result.get("vibration", {}).get("seed"),
            "attractor": result.get("vibration", {}).get("attractor"),
            "opcode": result.get("guna", {}).get("opcode"),
            "guna": result.get("guna", {}).get("mode"),
        })

        # Reset gate state
        lotus._active_gate = None

        # Build response
        cell_alive = result.get("cell", {}).get("is_alive", False)

        return GatewayResponse(
            success=cell_alive,
            exit_code=0 if cell_alive else 1,
            output="",
            error=None,
            position=result["position"],
            guardian=result["guardian"],
            quarter=result["quarter"],
            guna=result.get("verse", {}).get("guna", result.get("guna", {}).get("mode", "sattva")) if result.get("verse") else result.get("guna", {}).get("mode", "sattva"),
            entry_type=entry_type,
            routed_via="govardhan",
        )

    def route(self, command: str) -> Dict[str, object]:
        """Route command to position/guardian via pure computation."""
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        lotus = get_mahamantra()
        result = lotus(command)
        return {
            "position": result["position"],
            "guardian": result["guardian"],
            "quarter": result["quarter"],
        }


# =============================================================================
# SINGLETON - One Gateway to rule them all
# =============================================================================

_gateway: Optional[GovardhanGateway] = None


def get_gateway() -> GovardhanGateway:
    """Get the singleton Govardhan gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = GovardhanGateway()
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


# Backward-compatible alias
MahamantraGateway = GovardhanGateway

__all__ = [
    "GovardhanGateway",
    "MahamantraGateway",
    "get_gateway",
    "execute",
    "chat",
    "agent_call",
]

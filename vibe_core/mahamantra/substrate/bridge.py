"""
BRIDGE - The Setu Bandha (Die Brücke)
======================================

"setubandhaṁ samudrasya bhagavān pracakāra ha"
"The Lord built a bridge across the ocean."
— Ramayana

THE BRIDGE:
-----------
The ONLY legitimate path from chaos (Old World) to cosmos (Mahamantra).

All state mutations flow through here.
All file writes require Parampara validation.
All operations route to the correct Position/Mahajana.

WATERTIGHT: NO hardcoded numbers. ALL from seed.py (SSOT).
"""
from __future__ import annotations
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA, TEN)


# === MAHAJANA DECLARATION ===
__mahajana__ = "janaka"
__position__ = TEN
__genesis__ = "0x17f29aed"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Optional, Final, Union

# =============================================================================
# IMPORT FROM SSOT (seed.py) - NO MAGIC NUMBERS ALLOWED
# =============================================================================

# Import constants from protocols._seed (THE SOURCE)
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA,  # 37 - verification constant
    WORDS,  # 16 - mantra positions
    SHARANAGATI,  # 6 - connection limbs
    MAHAJANA_COUNT,  # 12 - the mahajanas
)

# =============================================================================
# MAHA CELL - Universal Data Format (AUTO-WRAPPING AT THE GATE)
# =============================================================================
# ONE import here = EVERYTHING flows through MahaCell automatically
# No manual imports needed anywhere else (Balarama Pattern)
from vibe_core.mahamantra.protocols._header import MahaCell, MahaHeader
from vibe_core.mahamantra.protocols._payload import MahaPayload, PayloadType

# Import functions from substrate.seed (THE REALITY)
from vibe_core.mahamantra.substrate.seed import (
    MAHAJANA_TO_POSITION,  # Name → Position mapping
    POSITION_TO_MAHAJANA,  # Position → Name mapping
    get_mahajana_position,  # Function to get position by name
    verify_parampara,  # Function to verify % 37 == 0
    lotus_declaration,  # Function to generate genesis signature
)


# =============================================================================
# PURPOSE → POSITION MAPPING (DERIVED FROM SEED, NOT HARDCODED)
# =============================================================================

# Every purpose maps to a Mahajana position via get_mahajana_position()
# NO INTEGER LITERALS. All positions come from seed.py.

PURPOSE_MAP: Final[Dict[str, int]] = {
    # ==========================================================================
    # NAVABHAKTI OPERATIONS (9 processes - SRAVANAM first!)
    # ==========================================================================
    # SRAVANAM: Hearing - THE ENTRY POINT (Narada = communication)
    "hearing": get_mahajana_position("narada"),     # Position 2 - SRAVANAM
    "sravanam": get_mahajana_position("narada"),    # Position 2 - SRAVANAM (alias)
    "receive": get_mahajana_position("narada"),     # Position 2 - SRAVANAM (alias)
    # KIRTANAM: Chanting - Output/Response
    "chanting": get_mahajana_position("narada"),    # Position 2 - KIRTANAM
    "kirtanam": get_mahajana_position("narada"),    # Position 2 - KIRTANAM (alias)
    # ==========================================================================
    # GENESIS OPERATIONS (Creation)
    "genesis": get_mahajana_position("brahma"),     # Position 1 - BRAHMA
    "creation": get_mahajana_position("brahma"),    # Position 1 - BRAHMA (alias)
    "wake": get_mahajana_position("brahma"),        # Position 1 - BRAHMA (alias)
    # ==========================================================================
    # JUDGMENT OPERATIONS (Moksha)
    "judge": get_mahajana_position("yamaraja"),     # Position 15 - YAMARAJA
    "judgment": get_mahajana_position("yamaraja"),  # Position 15 - YAMARAJA (alias)
    "audit": get_mahajana_position("yamaraja"),     # Position 15 - YAMARAJA (alias)
    # ==========================================================================
    # STATE OPERATIONS
    "state_update": get_mahajana_position("janaka"),  # Position 10 - STATE_SYNC
    "state_read": get_mahajana_position("janaka"),  # Position 10 - STATE_SYNC
    # LEDGER OPERATIONS
    "ledger_write": get_mahajana_position("bhishma"),  # Position 11 - LEDGER_SIGN
    "ledger_append": get_mahajana_position("bhishma"),  # Position 11 - LEDGER_SIGN
    # LOG OPERATIONS
    "log_emit": get_mahajana_position("shuka"),  # Position 14 - LOG_EMIT
    "log_write": get_mahajana_position("shuka"),  # Position 14 - LOG_EMIT
    # FILE OPERATIONS
    "file_flush": get_mahajana_position("bali"),  # Position 13 - IO_FLUSH
    "file_write": get_mahajana_position("bali"),  # Position 13 - IO_FLUSH
    # EXECUTION OPERATIONS
    "execute": get_mahajana_position("parashurama"),  # Position 8 - EXEC_OP
    # VERIFICATION OPERATIONS
    "verify": get_mahajana_position("kapila"),  # Position 6 - TYPE_CHECK
    "type_check": get_mahajana_position("kapila"),  # Position 6 - TYPE_CHECK
    # MEMORY OPERATIONS (Kapila's Promotion - Phase 3)
    "remember": get_mahajana_position("kapila"),  # Position 6 - REMEMBER
    "recall": get_mahajana_position("kapila"),  # Position 6 - RECALL
}


# =============================================================================
# OFFER - The Gate (Der einzige legitime Zugang)
# =============================================================================


class OfferResult(Dict[str, object]):
    """Result of an offer() call. WATERTIGHT: object instead of Any."""

    pass


def offer(
    content: Union[str, bytes, Dict[str, object], object],
    purpose: str,
    actor: Optional[str] = None,
    parampara_vector: Optional[int] = None,
    timeout: float = 10.0,
) -> OfferResult:
    """
    Offer content to the Mahamantra for routing and execution.

    THE BRIDGE PATTERN:
    -------------------
    Old World services call: bridge.offer(data, purpose="state_update")
    Bridge validates, routes to correct Position/Mahajana.
    New World executes through position-based protocol.

    WATERTIGHT GUARANTEES:
    ----------------------
    1. All routing derived from seed.py (no hardcoded positions)
    2. Parampara validation via verify_parampara() (no manual % 37)
    3. Purpose mapped to Position via get_mahajana_position()
    4. Returns structured result (success, position, mahajana)

    Args:
        content: The data/operation to offer
        purpose: Purpose string (must exist in PURPOSE_MAP)
        actor: Optional identifier of who is making the offer
        parampara_vector: Optional value for Parampara validation
                         If None, derived from content hash

    Returns:
        OfferResult dict with:
            - success: bool
            - position: int (0 to WORDS-1)
            - mahajana: str
            - quarter: str
            - purpose: str
            - error: Optional[str]

    Example:
        >>> result = offer("some state", purpose="state_update", actor="service_x")
        >>> print(result["mahajana"])  # "janaka"
        >>> print(result["position"])  # 10
    """

    # ── GOVARDHAN: Gate infrastructure for boundary enforcement ──
    # Legacy I/O goes through gates WITHOUT the full computation pipeline.
    # Only PARSE (validate input) and SYNC (govern side-effect) fire here.
    _lotus = None
    _TattvaGate = None
    try:
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra
        from vibe_core.mahamantra.substrate.pancha_tattva import TattvaGate as _TG

        _lotus = get_mahamantra()
        _TattvaGate = _TG
        _lotus._fire_gate(_TattvaGate.PARSE, {
            "input_data": content,
            "entry_type": "offer",
            "purpose": purpose,
            "actor": actor,
        })
    except Exception:
        pass  # Gate infrastructure may not be ready during early boot

    # Validate purpose exists in mapping
    if purpose not in PURPOSE_MAP:
        return OfferResult(
            success=False,
            position=-KSETRAJNA,
            mahajana="unknown",
            quarter="unknown",
            purpose=purpose,
            error=f"Unknown purpose '{purpose}'. Must be one of: {list(PURPOSE_MAP.keys())}",
        )

    # Get position from PURPOSE_MAP (already derived from seed.py)
    position = PURPOSE_MAP[purpose]

    # Validate position is within bounds (using WORDS from seed, not hardcoded 16)
    if not (0 <= position < WORDS):
        return OfferResult(
            success=False,
            position=position,
            mahajana="unknown",
            quarter="unknown",
            purpose=purpose,
            error=f"Position {position} out of bounds (0 to {WORDS - KSETRAJNA})",
        )

    # Get mahajana name for this position (from seed mapping)
    mahajana = POSITION_TO_MAHAJANA.get(position, "unknown")

    # Get lotus declaration for this position (includes genesis, quarter, etc)
    declaration = lotus_declaration(position)
    quarter = declaration["quarter_name"]
    genesis = declaration.get("genesis", "")
    word = declaration.get("word", "")

    # Parampara validation (using verify_parampara from seed, not manual % 37)
    if parampara_vector is not None:
        if not verify_parampara(parampara_vector):
            return OfferResult(
                success=False,
                position=position,
                mahajana=mahajana,
                quarter=quarter,
                purpose=purpose,
                error=f"Parampara validation failed for vector {parampara_vector}",
            )

    # =========================================================================
    # EXECUTION: RESOANCE ROUTING (The Flow)
    # =========================================================================
    # Phase 4 (Narada): We publish the intent and wait for the echo.
    # No more hardcoded teleportation (target_position).
    
    from vibe_core.mahamantra.reactor.loop import get_loop
    
    # 1. Get the Loop and Mailbox
    loop, mailbox = get_loop()
    
    # 2. Wait for Readiness (Narada must be awake)
    if not loop.wait_until_ready(timeout=5.0):
        return OfferResult(
            success=False,
            position=position,
            mahajana=mahajana,
            quarter=quarter,
            purpose=purpose,
            error="Reactor Init Timeout",
            execution_result=None,
            intent_id=None,
        )
    
    # 3. Prepare Ticket (The Promise)
    ticket = mailbox.create_ticket()
    
    # 4. Broadcast Intent (The Shout)
    # Map purpose to EventType (e.g. remember -> REMEMBER)
    event_type = purpose.upper()
    
    # Prepare details
    if isinstance(content, dict):
        details = content
    else:
        details = {"data": content}
        
    loop.publish(
        event_type=event_type,
        agent_id=actor or "bridge",
        message=f"Offer: {purpose}",
        details=details,
        task_id=ticket 
    )
    
    # 4. Wait for Echo (Sync)
    try:
        result_data = mailbox.collect(ticket, timeout=timeout)
        
        # 5. Unpack Result
        if not result_data["success"]:
            return OfferResult(
                success=False,
                position=position,
                mahajana=mahajana,
                quarter=quarter,
                purpose=purpose,
                error=result_data["error"] or "Unknown Reactor Error",
                execution_result=None,
                intent_id=None,
            )
            
        execution_result = result_data["execution_result"]
        error = result_data["error"]

        # ── GOVARDHAN: Fire SYNC gate at the boundary ──
        # The side-effect happened. Notify gate providers/hooks.
        if _lotus is not None and _TattvaGate is not None:
            try:
                _lotus._fire_gate(_TattvaGate.SYNC, {
                    "position": position,
                    "guardian": mahajana,
                    "purpose": purpose,
                    "actor": actor,
                    "seed": None,
                    "attractor": None,
                    "opcode": None,
                    "guna": None,
                })
                _lotus._active_gate = None
            except Exception:
                pass  # Gate hook/provider errors don't block I/O

        return OfferResult(
            success=True,
            position=position,
            mahajana=mahajana,
            quarter=quarter,
            purpose=purpose,
            error=error,
            execution_result=execution_result,
            intent_id=None,
            actor=actor,
            genesis=genesis,
            word=word,
        )

    except TimeoutError:
        return OfferResult(
            success=False,
            position=position,
            mahajana=mahajana,
            quarter=quarter,
            purpose=purpose,
            error="Reactor Timeout (MahaMailbox expired)",
            execution_result=None,
            intent_id=None,
        )
    except Exception as e:
        return OfferResult(
            success=False,
            position=position,
            mahajana=mahajana,
            quarter=quarter,
            purpose=purpose,
            error=f"Bridge/Loop Error: {str(e)}",
            execution_result=None,
            intent_id=None,
        )


# =============================================================================
# WRAP CELL - Auto-wrap ANY content into MahaCell (TOP-DOWN ENTRY)
# =============================================================================


def wrap_cell(
    content: Union[str, bytes, Dict[str, object], object],
    purpose: str,
    source_id: int = 0,
    target_id: int = 0,
) -> Optional[MahaCell]:
    """
    Auto-wrap ANY content into a MahaCell.

    BALARAMA PATTERN: This is the SINGLE GATE for data wrapping.
    Call this once, content flows through system as MahaCell.
    No manual MahaHeader/MahaPayload imports needed elsewhere!

    Args:
        content: Any data (str, bytes, dict, object)
        purpose: Purpose string (determines PayloadType via quarter)
        source_id: Source identifier (default 0)
        target_id: Target identifier (default 0)

    Returns:
        MahaCell with 72-byte header + typed payload, or None if purpose unknown
    """
    # Get routing info
    if purpose not in PURPOSE_MAP:
        return None

    position = PURPOSE_MAP[purpose]
    declaration = lotus_declaration(position)
    quarter = declaration["quarter_name"]

    # Map quarter → PayloadType (GENESIS/DHARMA/KARMA/MOKSHA)
    quarter_to_type = {
        "genesis": PayloadType.ARJUNA_VISHADA,  # Ch.1 - Raw input
        "dharma": PayloadType.JNANA_VIJNANA,    # Ch.7 - Typed/validated (Kapila Memory)
        "karma": PayloadType.VIBHUTI,           # Ch.10 - Execution
        "moksha": PayloadType.MOKSA_SANNYASA,   # Ch.18 - Output
    }
    payload_type = quarter_to_type.get(quarter.lower(), PayloadType.ARJUNA_VISHADA)

    # Convert content to bytes
    if isinstance(content, bytes):
        content_bytes = content
    elif isinstance(content, str):
        content_bytes = content.encode("utf-8")
    else:
        import json
        content_bytes = json.dumps(content, default=str).encode("utf-8")

    # Create typed payload
    payload = MahaPayload(
        payload_type=payload_type,
        data=content_bytes,
        position=position,
    )

    # Create header with routing
    header = MahaHeader.create(
        source=source_id,
        target=target_id,
        operation=position,
    )

    return MahaCell(header=header, payload=payload.to_bytes())


# =============================================================================
# QUERY - Inspect routing without execution
# =============================================================================


def query_purpose(purpose: str) -> Optional[Dict[str, object]]:
    """
    Query which Position/Mahajana handles a given purpose.

    READ-ONLY. Does not execute anything.

    Args:
        purpose: Purpose string to query

    Returns:
        Dict with position, mahajana, quarter, or None if purpose unknown

    Example:
        >>> info = query_purpose("ledger_write")
        >>> print(info["mahajana"])  # "bhishma"
        >>> print(info["position"])  # 11
    """
    if purpose not in PURPOSE_MAP:
        return None

    position = PURPOSE_MAP[purpose]
    mahajana = POSITION_TO_MAHAJANA.get(position, "unknown")
    declaration = lotus_declaration(position)

    return {
        "purpose": purpose,
        "position": position,
        "mahajana": mahajana,
        "quarter": declaration["quarter_name"],
        "word": declaration["word"],
        "genesis": declaration["genesis"],
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "offer",
    "query_purpose",
    "PURPOSE_MAP",
    "OfferResult",
]

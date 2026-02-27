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

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, TEN

# === MAHAJANA DECLARATION ===
__mahajana__ = "janaka"
__position__ = TEN
__genesis__ = "0x17f29aed"  # GenesisByte: parampara % 37 == 0

from typing import Dict, Final, Optional, Union

# =============================================================================
# MAHA CELL - Universal Data Format (AUTO-WRAPPING AT THE GATE)
# =============================================================================
# ONE import here = EVERYTHING flows through MahaCell automatically
# No manual imports needed anywhere else (Balarama Pattern)
from vibe_core.mahamantra.protocols._header import MahaCell, MahaHeader
from vibe_core.mahamantra.protocols._payload import MahaPayload, PayloadType

# =============================================================================
# IMPORT FROM SSOT (seed.py) - NO MAGIC NUMBERS ALLOWED
# =============================================================================
# Import constants from protocols._seed (THE SOURCE)
from vibe_core.mahamantra.protocols._seed import (
    WORDS,  # 16 - mantra positions
)

# Import functions from substrate.seed (THE REALITY)
from vibe_core.mahamantra.substrate.seed import (
    POSITION_TO_MAHAJANA,  # Position → Name mapping
    get_mahajana_position,  # Function to get position by name
    lotus_declaration,  # Function to generate genesis signature
    verify_parampara,  # Function to verify % 37 == 0
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
    "hearing": get_mahajana_position("narada"),  # Position 2 - SRAVANAM
    "sravanam": get_mahajana_position("narada"),  # Position 2 - SRAVANAM (alias)
    "receive": get_mahajana_position("narada"),  # Position 2 - SRAVANAM (alias)
    # KIRTANAM: Chanting - Output/Response
    "chanting": get_mahajana_position("narada"),  # Position 2 - KIRTANAM
    "kirtanam": get_mahajana_position("narada"),  # Position 2 - KIRTANAM (alias)
    # ==========================================================================
    # GENESIS OPERATIONS (Creation)
    "genesis": get_mahajana_position("brahma"),  # Position 1 - BRAHMA
    "creation": get_mahajana_position("brahma"),  # Position 1 - BRAHMA (alias)
    "wake": get_mahajana_position("brahma"),  # Position 1 - BRAHMA (alias)
    # ==========================================================================
    # JUDGMENT OPERATIONS (Moksha)
    "judge": get_mahajana_position("yamaraja"),  # Position 15 - YAMARAJA
    "judgment": get_mahajana_position("yamaraja"),  # Position 15 - YAMARAJA (alias)
    "audit": get_mahajana_position("yamaraja"),  # Position 15 - YAMARAJA (alias)
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


# =============================================================================
# OFFER STEPS — Atomic, granular, individually callable
# =============================================================================


def _offer_fail(position: int, mahajana: str, quarter: str, purpose: str, error: str, **kw) -> OfferResult:
    """Return a failed OfferResult."""
    return OfferResult(
        success=False, position=position, mahajana=mahajana, quarter=quarter, purpose=purpose, error=error, **kw
    )


def _offer_validate(purpose: str) -> tuple:
    """Offer Step 1: Validate purpose, resolve position/mahajana/quarter.
    Returns (position, mahajana, quarter, genesis, word) or OfferResult on failure."""
    if purpose not in PURPOSE_MAP:
        return _offer_fail(
            -KSETRAJNA,
            "unknown",
            "unknown",
            purpose,
            f"Unknown purpose '{purpose}'. Must be one of: {list(PURPOSE_MAP.keys())}",
        )

    position = PURPOSE_MAP[purpose]
    if not (0 <= position < WORDS):
        return _offer_fail(
            position, "unknown", "unknown", purpose, f"Position {position} out of bounds (0 to {WORDS - KSETRAJNA})"
        )

    mahajana = POSITION_TO_MAHAJANA.get(position, "unknown")
    declaration = lotus_declaration(position)
    quarter = declaration["quarter_name"]
    genesis = declaration.get("genesis", "")
    word = declaration.get("word", "")
    return position, mahajana, quarter, genesis, word


def _offer_check_parampara(
    parampara_vector: Optional[int], position: int, mahajana: str, quarter: str, purpose: str
) -> Optional[OfferResult]:
    """Offer Step 2: Parampara validation. Returns OfferResult on failure, None on success."""
    if parampara_vector is not None and not verify_parampara(parampara_vector):
        return _offer_fail(
            position, mahajana, quarter, purpose, f"Parampara validation failed for vector {parampara_vector}"
        )
    return None


def _offer_execute(
    content: Union[str, bytes, Dict[str, object], object],
    purpose: str,
    actor: Optional[str],
    timeout: float,
    position: int,
    mahajana: str,
    quarter: str,
    genesis: str,
    word: str,
) -> OfferResult:
    """Offer Step 3: Publish intent to reactor loop, collect result."""
    from vibe_core.mahamantra.reactor.loop import get_loop

    loop, mailbox = get_loop()

    if not loop.wait_until_ready(timeout=5.0):
        return _offer_fail(
            position, mahajana, quarter, purpose, "Reactor Init Timeout", execution_result=None, intent_id=None
        )

    ticket = mailbox.create_ticket()
    event_type = purpose.upper()
    details = content if isinstance(content, dict) else {"data": content}

    loop.publish(
        event_type=event_type,
        agent_id=actor or "bridge",
        message=f"Offer: {purpose}",
        details=details,
        task_id=ticket,
    )

    try:
        result_data = mailbox.collect(ticket, timeout=timeout)
        if not result_data["success"]:
            return _offer_fail(
                position,
                mahajana,
                quarter,
                purpose,
                result_data["error"] or "Unknown Reactor Error",
                execution_result=None,
                intent_id=None,
            )
        return OfferResult(
            success=True,
            position=position,
            mahajana=mahajana,
            quarter=quarter,
            purpose=purpose,
            error=result_data["error"],
            execution_result=result_data["execution_result"],
            intent_id=None,
            actor=actor,
            genesis=genesis,
            word=word,
        )
    except TimeoutError:
        return _offer_fail(
            position,
            mahajana,
            quarter,
            purpose,
            "Reactor Timeout (MahaMailbox expired)",
            execution_result=None,
            intent_id=None,
        )
    except Exception as e:
        return _offer_fail(
            position, mahajana, quarter, purpose, f"Bridge/Loop Error: {str(e)}", execution_result=None, intent_id=None
        )


def offer(
    content: Union[str, bytes, Dict[str, object], object],
    purpose: str,
    actor: Optional[str] = None,
    parampara_vector: Optional[int] = None,
    timeout: float = 10.0,
) -> OfferResult:
    """
    Offer content to the Mahamantra for routing and execution.
    Chains the atomic _offer_* steps.
    """
    validated = _offer_validate(purpose)
    if isinstance(validated, dict):
        return validated  # Validation failed
    position, mahajana, quarter, genesis, word = validated

    parampara_err = _offer_check_parampara(parampara_vector, position, mahajana, quarter, purpose)
    if parampara_err is not None:
        return parampara_err

    return _offer_execute(content, purpose, actor, timeout, position, mahajana, quarter, genesis, word)


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
        "dharma": PayloadType.JNANA_VIJNANA,  # Ch.7 - Typed/validated (Kapila Memory)
        "karma": PayloadType.VIBHUTI,  # Ch.10 - Execution
        "moksha": PayloadType.MOKSA_SANNYASA,  # Ch.18 - Output
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

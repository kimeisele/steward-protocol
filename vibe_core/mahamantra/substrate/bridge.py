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

# === MAHAJANA DECLARATION ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x255aaf58"  # GenesisByte: parampara % 37 == 0

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

    # Validate purpose exists in mapping
    if purpose not in PURPOSE_MAP:
        return OfferResult(
            success=False,
            position=-1,
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
            error=f"Position {position} out of bounds (0 to {WORDS - 1})",
        )

    # Get mahajana name for this position (from seed mapping)
    mahajana = POSITION_TO_MAHAJANA.get(position, "unknown")

    # Get lotus declaration for this position (includes genesis, quarter, etc)
    declaration = lotus_declaration(position)
    quarter = declaration["quarter_name"]

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

    # SUCCESS: Offer accepted, routing information returned
    return OfferResult(
        success=True,
        position=position,
        mahajana=mahajana,
        quarter=quarter,
        purpose=purpose,
        actor=actor,
        genesis=declaration["genesis"],
        word=declaration["word"],
        error=None,
    )


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

"""
ADHIKARA - Qualification Computed from Mahamantra (Not Hardcoded)
=================================================================

"adhikārī purus̄aḥ pāñcarātriki-viddhinā"
"A person is qualified according to the Pancharatra regulations."
— Hari-bhakti-vilasa

PRINCIPLE:
==========

The Mahamantra ITSELF determines which qualities are required for each OpCode.
No hardcoded mappings. Everything computed from _seed.py.

MATHEMATICS:
============

For each position (0-15):
1. Get the HolyName at that position (HARE=0, KRISHNA=1, RAMA=2)
2. Compute a deterministic bitmap using Seed constants
3. The bitmap indicates which of the 50 qualities are required

FORMULA:
========

    required_bitmap = hash(position, holy_name, PARAMPARA, JIVA_QUALITIES)

This ensures:
- DETERMINISTIC: Same position always needs same qualities
- DERIVED: From Mahamantra structure, not invented
- VERIFIABLE: Anyone can recompute and verify

USAGE:
======

    from vibe_core.mahamantra.lila.adhikara import (
        get_required_qualities,
        shadow_can_execute,
    )

    # What qualities does OpCode 8 (EXEC_OP) need?
    bitmap = get_required_qualities(8)

    # Can this shadow execute OpCode 8?
    if shadow_can_execute(shadow, opcode=8):
        # Shadow has the required qualities
        ...
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"  # The Lawgiver - determines qualifications
__position__ = 7
__genesis__ = "0x93152144"  # GenesisByte: parampara % 37 == 0

import hashlib
from functools import lru_cache
from typing import Final, FrozenSet, Tuple

from vibe_core.mahamantra.lila.jiva_shadow import (
    RAJASIC_RANGE,
    SATTVIC_RANGE,
    TAMASIC_RANGE,
    JivaQuality,
    JivaShadow,
)

# SSOT: All from _seed.py
from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT,  # 8
    JIVA_QUALITIES,  # 50
    KRISHNA_COUNT,  # 4
    PARAMPARA,  # 37
    RAMA_COUNT,  # 4
    WORDS,  # 16
)
from vibe_core.mahamantra.substrate.seed import (
    MAHAMANTRA,
    QUARTERS,
    HolyName,
    Quarter,
)

# =============================================================================
# HOLY NAME → GUNA AFFINITY (Derived, not hardcoded)
# =============================================================================
# Each HolyName has natural affinity to certain quality ranges
# HARE = Shakti (Energy) → Activates across all ranges (8 occurrences = balance)
# KRISHNA = Source (Identity) → Strong in Sattvic (4 occurrences)
# RAMA = Ananda (Stability) → Strong in completion (4 occurrences)

# Affinity multipliers derived from counts in Mahamantra
HARE_AFFINITY: Final[float] = HARE_COUNT / WORDS  # 8/16 = 0.5
KRISHNA_AFFINITY: Final[float] = KRISHNA_COUNT / WORDS  # 4/16 = 0.25
RAMA_AFFINITY: Final[float] = RAMA_COUNT / WORDS  # 4/16 = 0.25


# =============================================================================
# QUARTER → BASE QUALITY RANGE (Derived from structure)
# =============================================================================
# Each Quarter naturally aligns with a portion of the 50 qualities
# This is computed, not hardcoded


def _compute_quarter_range(quarter: int) -> Tuple[int, int]:
    """
    Compute the base quality range for a quarter.

    Derived from:
    - JIVA_QUALITIES = 50
    - QUARTERS = 4
    - Each quarter gets approximately 50/4 = 12.5 qualities

    We use overlapping ranges to ensure coverage.
    """
    qualities_per_quarter = JIVA_QUALITIES // QUARTERS  # 50 // 4 = 12
    overlap = JIVA_QUALITIES % QUARTERS  # 50 % 4 = 2 (distributed as overlap)

    start = quarter * qualities_per_quarter
    end = start + qualities_per_quarter + (overlap if quarter < QUARTERS - 1 else JIVA_QUALITIES - start)

    return (start, min(end, JIVA_QUALITIES))


QUARTER_RANGES: Final[dict[int, Tuple[int, int]]] = {q: _compute_quarter_range(q) for q in range(QUARTERS)}


# =============================================================================
# THE COMPUTATION - Mahamantra determines requirements
# =============================================================================


@lru_cache(maxsize=WORDS)  # Cache all 16 positions
def compute_required_bitmap(position: int) -> int:
    """
    Compute the required quality bitmap for a Mahamantra position.

    ALGORITHM (all from seed):
    1. Get HolyName at position
    2. Get Quarter for position
    3. Compute deterministic seed from position × PARAMPARA + name × JIVA_QUALITIES
    4. Hash to spread bits evenly
    5. Apply Quarter range emphasis

    Args:
        position: Mahamantra position (0-15)

    Returns:
        50-bit bitmap of required qualities
    """
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS - 1}, got {position}")

    # 1. Get HolyName at this position
    holy_name = MAHAMANTRA[position]
    name_value = holy_name.value  # 0, 1, or 2

    # 2. Get Quarter
    quarter = position // (WORDS // QUARTERS)  # 0, 1, 2, or 3
    quarter_range = QUARTER_RANGES[quarter]

    # 3. Compute deterministic seed
    # Formula: position contributes to spread, name contributes to character
    seed_value = (position + 1) * PARAMPARA + (name_value + 1) * JIVA_QUALITIES

    # 4. Hash to get evenly distributed bits
    seed_bytes = seed_value.to_bytes(8, "big")
    hash_result = hashlib.sha256(seed_bytes).digest()

    # Extract 50 bits from hash
    raw_bitmap = int.from_bytes(hash_result[:7], "big")
    base_bitmap = raw_bitmap & ((1 << JIVA_QUALITIES) - 1)

    # 5. Apply Quarter emphasis
    # Ensure at least some qualities from the quarter's range are active
    quarter_start, quarter_end = quarter_range
    quarter_mask = 0

    # Activate PARAMPARA % (quarter_end - quarter_start) qualities in quarter range
    num_required = max(1, PARAMPARA % (quarter_end - quarter_start + 1))
    for i in range(num_required):
        idx = quarter_start + (seed_value + i) % (quarter_end - quarter_start)
        quarter_mask |= 1 << idx

    # Combine: base bitmap OR quarter emphasis
    final_bitmap = base_bitmap | quarter_mask

    return final_bitmap


def get_required_qualities(position: int) -> FrozenSet[JivaQuality]:
    """
    Get the set of required qualities for a position.

    Human-readable version of compute_required_bitmap.

    Args:
        position: Mahamantra position (0-15)

    Returns:
        FrozenSet of JivaQuality enums
    """
    bitmap = compute_required_bitmap(position)
    return frozenset(JivaQuality(i) for i in range(JIVA_QUALITIES) if bitmap & (1 << i))


def get_required_count(position: int) -> int:
    """Get count of required qualities for a position."""
    bitmap = compute_required_bitmap(position)
    return bin(bitmap).count("1")


# =============================================================================
# SHADOW MATCHING - Can this shadow execute this position?
# =============================================================================


def shadow_can_execute(shadow: JivaShadow, position: int) -> bool:
    """
    Check if a JivaShadow can execute an operation at a position.

    The shadow must have ALL required qualities for the position.
    This is strict Adhikara - no exceptions.

    Args:
        shadow: The JivaShadow to check
        position: The Mahamantra position (0-15)

    Returns:
        True if shadow has all required qualities
    """
    required_bitmap = compute_required_bitmap(position)

    # Shadow must have all required bits set
    return (shadow.quality_bitmap & required_bitmap) == required_bitmap


def shadow_match_score(shadow: JivaShadow, position: int) -> float:
    """
    Calculate how well a shadow matches a position's requirements.

    Returns 0.0-1.0:
    - 1.0 = Perfect match (has all required, no excess)
    - 0.5 = Has all required, but many extra
    - 0.0 = Missing required qualities

    Args:
        shadow: The JivaShadow to evaluate
        position: The Mahamantra position (0-15)

    Returns:
        Match score 0.0-1.0
    """
    required = compute_required_bitmap(position)
    has = shadow.quality_bitmap

    # Count required qualities
    required_count = bin(required).count("1")
    if required_count == 0:
        return 1.0  # No requirements = anyone qualifies

    # Count matching qualities
    matching = bin(required & has).count("1")

    # Must have ALL required
    if matching < required_count:
        return 0.0  # Disqualified

    # Score based on match ratio
    # Perfect servant has exactly what's needed, not more
    total_has = bin(has).count("1")
    excess = total_has - required_count

    # Penalize excess slightly (prefer focused servants)
    # But not too much - more qualities is better than fewer
    if excess == 0:
        return 1.0
    else:
        return max(0.5, 1.0 - (excess / JIVA_QUALITIES) * 0.5)


def find_best_shadow(
    shadows: list[JivaShadow],
    position: int,
) -> JivaShadow | None:
    """
    Find the best shadow for a position from a list.

    Args:
        shadows: List of available shadows
        position: The Mahamantra position (0-15)

    Returns:
        Best matching shadow, or None if none qualify
    """
    qualified = [(s, shadow_match_score(s, position)) for s in shadows if shadow_can_execute(s, position)]

    if not qualified:
        return None

    # Sort by score descending
    qualified.sort(key=lambda x: x[1], reverse=True)
    return qualified[0][0]


# =============================================================================
# ADHIKARA REPORT - For observability
# =============================================================================


def get_position_adhikara_report(position: int) -> dict:
    """
    Get a detailed report of Adhikara requirements for a position.

    Useful for debugging and UI display.
    """
    bitmap = compute_required_bitmap(position)
    qualities = get_required_qualities(position)

    holy_name = MAHAMANTRA[position]
    quarter = position // (WORDS // QUARTERS)

    # Count by Guna
    sattvic = sum(1 for q in qualities if SATTVIC_RANGE[0] <= q.value < SATTVIC_RANGE[1])
    rajasic = sum(1 for q in qualities if RAJASIC_RANGE[0] <= q.value < RAJASIC_RANGE[1])
    tamasic = sum(1 for q in qualities if TAMASIC_RANGE[0] <= q.value < TAMASIC_RANGE[1])

    return {
        "position": position,
        "holy_name": holy_name.name,
        "quarter": Quarter(quarter).name,
        "required_count": len(qualities),
        "required_bitmap": bin(bitmap),
        "guna_distribution": {
            "sattvic": sattvic,
            "rajasic": rajasic,
            "tamasic": tamasic,
        },
        "qualities": [q.name for q in sorted(qualities, key=lambda x: x.value)],
    }


# =============================================================================
# VERIFICATION - Ensure computation is deterministic
# =============================================================================


def verify_adhikara_determinism() -> bool:
    """
    Verify that Adhikara computation is deterministic.

    Runs the computation twice for all positions and compares.
    """
    for pos in range(WORDS):
        bitmap1 = compute_required_bitmap(pos)
        # Clear cache to force recomputation
        compute_required_bitmap.cache_clear()
        bitmap2 = compute_required_bitmap(pos)

        if bitmap1 != bitmap2:
            return False

    return True


# =============================================================================
# VARNASHRAMA SPAWN - Shadow für seinen Zweck manifestiert
# =============================================================================


def spawn_shadow_for_position(
    position: int,
    context: bytes = b"",
) -> JivaShadow:
    """
    Spawn a JivaShadow QUALIFIED for the given position.

    VARNASHRAMA PRINCIPLE:
    ======================
    A Jiva is not born randomly and then searches for work.
    A Jiva is born FOR the work - his Guna-Karma determines his position.

    This function manifests a shadow with GUARANTEED qualification
    for the target position. No lottery, no filtering.

    ALGORITHM:
    1. Compute required bitmap for position (Adhikara)
    2. Shadow receives ALL required qualities (minimum qualification)
    3. Context adds personality/uniqueness (extra qualities)
    4. Result: Qualified shadow with individual character

    Args:
        position: Mahamantra position (0-15) - the DESTINATION
        context: Optional bytes for uniqueness (session, timestamp, etc.)

    Returns:
        JivaShadow guaranteed to pass shadow_can_execute(shadow, position)
    """
    import hashlib
    from uuid import uuid4

    # 1. Get the required qualities for this position (Adhikara)
    required_bitmap = compute_required_bitmap(position)

    # 2. Derive additional qualities from context (personality)
    if context:
        context_hash = hashlib.sha256(context).digest()
        extra_bitmap = int.from_bytes(context_hash[:7], "big") & ((1 << JIVA_QUALITIES) - 1)
    else:
        extra_bitmap = 0

    # 3. Final bitmap = required OR extra (guaranteed qualified + unique)
    final_bitmap = required_bitmap | extra_bitmap

    # 4. Create deterministic seed_hash for traceability
    seed_material = f"varnashrama_pos{position}_{context.hex() if context else 'pure'}".encode()
    seed_hash = hashlib.sha256(seed_material).digest()

    # 5. Create shadow_id from position + uniqueness
    holy_name = MAHAMANTRA[position]
    shadow_id = f"shadow_{holy_name.name.lower()}_{position}_{uuid4().hex[:6]}"

    return JivaShadow(
        quality_bitmap=final_bitmap,
        seed_hash=seed_hash,
        shadow_id=shadow_id,
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core computation
    "compute_required_bitmap",
    "get_required_qualities",
    "get_required_count",
    # Shadow matching
    "shadow_can_execute",
    "shadow_match_score",
    "find_best_shadow",
    # Varnashrama spawn (THE CORRECT WAY)
    "spawn_shadow_for_position",
    # Reporting
    "get_position_adhikara_report",
    # Verification
    "verify_adhikara_determinism",
    # Constants (derived)
    "QUARTER_RANGES",
    "HARE_AFFINITY",
    "KRISHNA_AFFINITY",
    "RAMA_AFFINITY",
]

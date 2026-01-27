"""
VIBE COMPUTE - Headless Mahamantra Computation
===============================================

"paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"

THE RESONANCE BODY:
    Input → Mahamantra (16) → Siksastakam (8) → Output
    24 steps = KSHETRA = The Field

USAGE:
    # CLI
    python -m vibe_core.compute 108
    python -m vibe_core.compute 42 --verbose

    # Python
    from vibe_core.compute import vibe
    result = vibe(108)  # → int

    # With trace
    from vibe_core.compute import vibe_full
    result = vibe_full(42)  # → dict with guarantees

NO KERNEL REQUIRED. Pure computation.
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xf1a2b3c4"

import sys
from typing import Any, Dict, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, WORDS
from vibe_core.mahamantra.protocols._maha_compute import (
    PATTERN,
    apply_operation,
    get_operation,
    ATTRACTOR_FIXED,
    ATTRACTOR_CYCLE,
)
from vibe_core.mahamantra.siksastakam_compute import (
    SiksastakamCompute,
    STAGE_GUARANTEES,
    VERSE_CONSTANTS,
)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def vibe(value: int) -> int:
    """
    THE VIBRATION: Input → Resonance → Output.

    24-step transformation:
    - 16 Mahamantra steps (H×7, K+10, R×²)
    - 8 Siksastakam steps (verse constants)

    Args:
        value: Any integer

    Returns:
        Transformed value (mod 137)

    Example:
        >>> vibe(108)
        133
    """
    # Mahamantra: 16 steps
    v = value % MAHA_QUANTUM
    for pos in range(WORDS):
        op = get_operation(pos)
        v = apply_operation(v, op)

    # Siksastakam: 8 steps
    compute = SiksastakamCompute()
    return compute.process(v)


def vibe_full(value: int) -> Dict[str, Any]:
    """
    Full vibration with trace and guarantees.

    Args:
        value: Any integer

    Returns:
        Dict with:
        - input, output
        - mahamantra_trace (16 steps)
        - siksastakam_trace (8 steps)
        - attractor, gita_chapter
        - guarantees (8)
    """
    v = value % MAHA_QUANTUM
    maha_trace = [v]

    # Mahamantra: 16 steps
    for pos in range(WORDS):
        op = get_operation(pos)
        v = apply_operation(v, op)
        maha_trace.append(v)

    # Siksastakam: 8 steps
    compute = SiksastakamCompute()
    siks_result = compute.process_with_guarantees(v)

    # Find attractor
    attractor = siks_result.attractor_value
    if attractor == ATTRACTOR_FIXED:
        gita = 18
    elif attractor in ATTRACTOR_CYCLE:
        gita = (attractor % 17) + 1
    else:
        gita = 0

    return {
        "input": value % MAHA_QUANTUM,
        "output": siks_result.output_value,
        "mahamantra_trace": maha_trace,
        "siksastakam_output": siks_result.output_value,
        "attractor": attractor,
        "gita_chapter": gita,
        "guarantees": list(STAGE_GUARANTEES),
        "total_steps": 24,
    }


def vibe_batch(values: List[int]) -> List[int]:
    """
    Batch vibration for SIMD-style processing.

    Optimal with 16 values (= SIMD_LANES = AVX-512).

    Args:
        values: List of integers

    Returns:
        List of transformed values
    """
    return [vibe(v) for v in values]


def resonate(value: int, iterations: int = 1) -> int:
    """
    Repeated vibration until resonance.

    Each iteration = 24 steps through the field.

    Args:
        value: Starting value
        iterations: How many full vibrations

    Returns:
        Final resonant value
    """
    v = value
    for _ in range(iterations):
        v = vibe(v)
    return v


def find_resonance(value: int, max_iter: int = 137) -> Tuple[int, int]:
    """
    Find the resonant attractor.

    Iterates until value stabilizes or cycles.

    Args:
        value: Starting value
        max_iter: Maximum iterations

    Returns:
        (attractor_value, iterations_needed)
    """
    v = value % MAHA_QUANTUM
    seen = set()

    for i in range(max_iter):
        if v == ATTRACTOR_FIXED or v in ATTRACTOR_CYCLE:
            return v, i
        if v in seen:
            return v, i
        seen.add(v)
        v = vibe(v)

    return v, max_iter


# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("VIBE COMPUTE - Headless Mahamantra Computation")
        print()
        print("Usage: python -m vibe_core.compute <value> [--verbose]")
        print()
        print("Examples:")
        print("  python -m vibe_core.compute 108")
        print("  python -m vibe_core.compute 42 --verbose")
        print()
        print("Python API:")
        print("  from vibe_core.compute import vibe")
        print("  result = vibe(108)")
        return

    try:
        value = int(sys.argv[1])
    except ValueError:
        print(f"Error: '{sys.argv[1]}' is not a valid integer")
        sys.exit(1)

    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    if verbose:
        result = vibe_full(value)
        print(f"INPUT:  {result['input']}")
        print()
        print("MAHAMANTRA (16 steps):")
        trace = result['mahamantra_trace']
        for i in range(WORDS):
            op = PATTERN[i]
            print(f"  {i:2d}. {op} : {trace[i]:3d} → {trace[i+1]:3d}")
        print()
        print("SIKSASTAKAM (8 steps):")
        for i, (const, guarantee) in enumerate(zip(VERSE_CONSTANTS, STAGE_GUARANTEES)):
            print(f"  L{i}: const={const} | {guarantee}")
        print()
        print(f"OUTPUT: {result['output']}")
        print(f"ATTRACTOR: {result['attractor']} (Gita {result['gita_chapter']})")
        print()
        print("GUARANTEES:")
        for g in result['guarantees']:
            print(f"  ✓ {g}")
    else:
        print(vibe(value))


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "vibe",
    "vibe_full",
    "vibe_batch",
    "resonate",
    "find_resonance",
]


if __name__ == "__main__":
    main()

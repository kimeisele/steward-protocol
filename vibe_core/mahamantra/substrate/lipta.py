"""
LIPTA SUBSTRATE - The High-Resolution Bridge
=============================================

"liptāḥ kalāḥ" - The minutes of arc.

This module provides the "High Resolution" bridge between floating-point
degrees (Maya) and integer-based Lipta (Sat/Truth).

Base: 1 Degree = 60 Lipta
COSMIC_FRAME = 21600 Lipta (360 Degrees)
"""
from vibe_core.mahamantra.protocols._seed import (QUARTERS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0x5fcffced"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME


def degree_to_lipta(degrees: float) -> int:
    """
    Convert degrees to Lipta (minutes of arc).

    CRITICAL:
    1. Use round() before int() to avoid the "799-trap" (13.333... * 60 = 799.999...).
    2. Use modulo COSMIC_FRAME to ensure circularity (360.0 -> 0).
    3. Python's % handles negative numbers correctly (-0.1 % 21600 = 21594).
    """
    # 1Degree = 60 Lipta. Rounding is essential for precision stability.
    lipta = int(round(degrees * 60))
    return lipta % COSMIC_FRAME


def lipta_to_degree(lipta: int) -> float:
    """
    Convert Lipta back to degrees (for UI/Display).
    """
    # Precision is lost here manually, but the source (lipta) remains Sat.
    return (lipta % COSMIC_FRAME) / 60.0


def get_lipta_name() -> str:
    """Returns the name of the unit."""
    return "Lipta"

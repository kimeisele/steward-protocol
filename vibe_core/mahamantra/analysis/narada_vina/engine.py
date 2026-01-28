"""
ADVAITA STRING - The Logic (Inference/Bridge)
==============================================

"advaita acarya bada mahanta"
"Advaita Acarya is a great devotee."
— Narottama dasa Thakura

ADVAITA = The bridge between material and spiritual.
Maha-Vishnu - he who CALLS Krishna to the material world.

This module contains CANDIDATE predictions (1-5% error):
- Formula discovery for not-yet-verified constants
- Pattern recognition for potential matches

QUALITY STANDARDS:
- < 1% error → Should be DERIVED (move to knowledge.py)
- 1-5% error → CANDIDATE (belongs here as predictions)
- > 5% error → NUMEROLOGY (rejected, not included)

NOTE: Previous versions forced NAVA = 9 generators, which led to
keeping predictions with >50% error (numerology). Quality > quantity.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xed9f6f0a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from typing import Final, List

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSHETRA,
    MAHA_MU,
    MALA,
    NADI_RESONANCE,
    NAVA,
    QUARTERS,
    TRINITY,
)

# =============================================================================
# PREDICTION DATACLASS
# =============================================================================


@dataclass
class Prediction:
    """A prediction from the Maha-Algorithm."""

    name: str
    formula: str
    value: int
    components: List[str]
    description: str = ""


# =============================================================================
# CANDIDATE PREDICTIONS (1-5% error - awaiting verification)
# =============================================================================
# These are predictions that match physics constants within 1-5% error.
# Constants with <1% error should be promoted to DERIVED in knowledge.py.
# Constants with >5% error are numerology and are not included.


def predict_bottom_quark() -> Prediction:
    """
    CANDIDATE: Bottom quark / electron ratio.

    Actual value: ~8180 (PDG 2022: m_b = 4.18 GeV)
    Predicted: 8316 = 4×μ + 108×9 = 7344 + 972
    Error: 1.66% (CANDIDATE)

    Formula: 4 protons + Mala × Nava (devotion × processes)
    """
    value = MAHA_MU * QUARTERS + MALA * NAVA  # 8316
    return Prediction(
        name="bottom_quark/electron",
        formula="4×μ + MALA×NAVA",
        value=value,
        components=["MAHA_MU", "QUARTERS", "MALA", "NAVA"],
        description="Bottom quark mass ratio (1.66% error)",
    )


def predict_charm_quark() -> Prediction:
    """
    CANDIDATE: Charm quark / electron ratio.

    Actual value: ~2485 (PDG 2022: m_c = 1.27 GeV)
    Predicted: 2586 = 108×24 - 3×2 = 2592 - 6
    Error: 4.06% (CANDIDATE)

    Formula: Mala × Field - Trinity × Halves
    """
    value = MALA * KSHETRA - TRINITY * HALVES  # 2586
    return Prediction(
        name="charm_quark/electron",
        formula="MALA×KSHETRA - TRINITY×HALVES",
        value=value,
        components=["MALA", "KSHETRA", "TRINITY", "HALVES"],
        description="Charm quark mass ratio (4.06% error)",
    )


def predict_strange_quark() -> Prediction:
    """
    NOTE: This is now DERIVED in knowledge.py (MAHA_STRANGE in _seed.py).
    Kept here for reference - will be removed in future cleanup.

    Actual value: ~183 (PDG 2022: m_s = 93.4 MeV)
    Predicted: 183 = 108 + 72 + 3 = MALA + NADI + TRINITY
    Error: 0.12% (DERIVED!)
    """
    value = MALA + NADI_RESONANCE + TRINITY  # 183
    return Prediction(
        name="strange_quark/electron",
        formula="MALA + NADI + TRINITY",
        value=value,
        components=["MALA", "NADI_RESONANCE", "TRINITY"],
        description="Strange quark mass ratio (0.12% - NOW DERIVED in _seed.py)",
    )


def predict_down_quark() -> Prediction:
    """
    CANDIDATE: Down quark / electron ratio.

    Actual value: ~9.1 (PDG 2022: m_d = 4.67 MeV)
    Predicted: 9 = NAVA (the 9 processes of devotion)
    Error: 1.1% (CANDIDATE)

    Formula: Simply NAVA (9) - elegantly simple!
    """
    value = NAVA  # 9
    return Prediction(
        name="down_quark/electron",
        formula="NAVA",
        value=value,
        components=["NAVA"],
        description="Down quark mass ratio (1.1% error)",
    )


# =============================================================================
# REJECTED PREDICTIONS (kept for documentation)
# =============================================================================
# The following were previously included but are NUMEROLOGY (>5% error):
#
# predict_up_quark: QUARTERS + TRINITY = 7
#   Actual: ~4.2, Error: 67% (REJECTED)
#
# predict_top_quark: COSMIC_FRAME × SEVEN + MAHA_MU × HALF_SIZE = 165888
#   Actual: ~338000, Error: 51% (REJECTED)
#
# predict_w_boson: MAHA_MU × MALA - COSMIC_FRAME/4 = 192888
#   Actual: ~157299, Error: 23% (REJECTED - also already DERIVED in _seed.py)
#
# predict_z_boson: MAHA_MU × MALA - NADI = 198216
#   Actual: ~178450, Error: 11% (REJECTED - also already DERIVED in _seed.py)
#
# predict_higgs: MAHA_MU × MALA + COSMIC × HALF = 371088
#   Actual: ~244605, Error: 52% (REJECTED - also already DERIVED in _seed.py)
#


# =============================================================================
# THE GENERATOR REGISTRY (Quality over Quantity)
# =============================================================================
# Only CANDIDATE predictions (1-5% error) are included.
# DERIVED constants (< 1% error) should be in knowledge.py
# NUMEROLOGY (> 5% error) is rejected.

GENERATORS: Final[List[callable]] = [
    predict_bottom_quark,  # 1.66% error (CANDIDATE)
    predict_charm_quark,  # 4.06% error (CANDIDATE)
    predict_down_quark,  # 1.1% error (CANDIDATE)
    # predict_strange_quark removed - now DERIVED in _seed.py (MAHA_STRANGE)
]

# NOTE: We no longer enforce NAVA = 9. Quality > quantity.
# The previous constraint forced inclusion of predictions with >50% error.


def generate_all_predictions() -> List[Prediction]:
    """Run all NAVA generators and return predictions."""
    return [gen() for gen in GENERATORS]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Prediction",
    "GENERATORS",
    "generate_all_predictions",
    # Individual generators (CANDIDATE predictions only)
    "predict_bottom_quark",
    "predict_charm_quark",
    "predict_strange_quark",
    "predict_down_quark",
]

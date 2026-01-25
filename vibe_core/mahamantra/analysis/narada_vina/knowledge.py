"""
NITYANANDA STRING - The Foundation (Storage/Database)
======================================================

"nityananda rama-gana, kore sada vibhavana"
"Nityananda always meditates on Rama."
— Narottama dasa Thakura

NITYANANDA = The substrate that carries everything.
Ananta Shesha - the infinite foundation.

This module contains the KSHETRA (24 elements) of physics knowledge:
- The database of known physics constants
- Their Maha-Algorithm derivations
- Coverage status tracking

CONSTRAINT: KSHETRA = 24 maximum constant categories
(The 24 elements of material nature - Sankhya philosophy)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xb7e4f195"

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Final, Optional

from vibe_core.mahamantra.protocols._seed import (
    KSHETRA,
    MAHA_ALPHA,
    MAHA_ALPHA_S_SCALED,
    MAHA_CMB,
    MAHA_DEUTERON,
    MAHA_HELION,
    MAHA_HIGGS,
    MAHA_KAON,
    MAHA_MU,
    MAHA_MUON,
    MAHA_NEUTRON,
    MAHA_PION_CHARGED,
    MAHA_PION_NEUTRAL,
    MAHA_QUANTUM,
    MAHA_SIN2_THETA_W_SCALED,
    MAHA_TAU,
    MAHA_TRITON,
    MAHA_W,
    MAHA_Z,
)

# =============================================================================
# CATEGORIES (Maximum KSHETRA = 24)
# =============================================================================


class ConstantCategory(Enum):
    """
    Categories of physical constants.

    CONSTRAINT: Maximum KSHETRA (24) categories allowed.
    Currently using 7 (SEVEN from the seed).
    """

    MASS_RATIO = auto()  # Particle mass ratios (dimensionless)
    COUPLING = auto()  # Coupling constants (dimensionless)
    MIXING_ANGLE = auto()  # Mixing angles (CKM, PMNS, Weinberg)
    COSMOLOGICAL = auto()  # Cosmological parameters
    ATOMIC = auto()  # Atomic physics constants
    NUCLEAR = auto()  # Nuclear physics constants
    MATHEMATICAL = auto()  # Mathematical constants


class CoverageStatus(Enum):
    """Status of a constant in the Maha-Algorithm."""

    DERIVED = auto()  # Already derived with formula
    CANDIDATE = auto()  # Formula found, not yet verified
    UNCOVERED = auto()  # No formula found yet
    PREDICTED = auto()  # Prediction made, awaiting measurement


# =============================================================================
# THE PHYSICS CONSTANT DATACLASS
# =============================================================================


@dataclass
class PhysicsConstant:
    """A known physics constant with optional Maha-Algorithm derivation."""

    name: str
    value: float
    category: ConstantCategory
    unit: str
    uncertainty: float = 0.0
    description: str = ""
    source: str = "CODATA 2022"
    # Maha-Algorithm fields
    maha_value: Optional[int] = None
    maha_formula: Optional[str] = None
    maha_error: Optional[float] = None
    status: CoverageStatus = CoverageStatus.UNCOVERED


# =============================================================================
# THE DATABASE (NITYANANDA carries all knowledge)
# =============================================================================

KNOWN_CONSTANTS: Final[Dict[str, PhysicsConstant]] = {
    # ═══════════════════════════════════════════════════════════════════
    # MASS RATIOS (dimensionless, relative to electron)
    # ═══════════════════════════════════════════════════════════════════
    "proton_electron": PhysicsConstant(
        "proton/electron",
        1836.152673426,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.000000032,
        "Proton to electron mass ratio",
        maha_value=MAHA_MU,
        maha_formula="MALA * KRISHNA_POS",
        maha_error=0.008,
        status=CoverageStatus.DERIVED,
    ),
    "neutron_electron": PhysicsConstant(
        "neutron/electron",
        1838.68366173,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00000089,
        "Neutron to electron mass ratio",
        maha_value=MAHA_NEUTRON,
        maha_formula="MAHA_MU + TRINITY",
        maha_error=0.017,
        status=CoverageStatus.DERIVED,
    ),
    "muon_electron": PhysicsConstant(
        "muon/electron",
        206.7682830,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.0000046,
        "Muon to electron mass ratio",
        maha_value=MAHA_MUON,
        maha_formula="MAHAJANA * KRISHNA_POS + TRINITY",
        maha_error=0.11,
        status=CoverageStatus.DERIVED,
    ),
    "tau_electron": PhysicsConstant(
        "tau/electron",
        3477.23,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.23,
        "Tau to electron mass ratio",
        maha_value=MAHA_TAU,
        maha_formula="MALA * AKSARA + T(6)",
        maha_error=0.007,
        status=CoverageStatus.DERIVED,
    ),
    "deuteron_electron": PhysicsConstant(
        "deuteron/electron",
        3670.48296788,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00000013,
        "Deuteron to electron mass ratio",
        maha_value=MAHA_DEUTERON,
        maha_formula="2 * MALA * KRISHNA_POS",
        maha_error=0.04,
        status=CoverageStatus.DERIVED,
    ),
    "triton_electron": PhysicsConstant(
        "triton/electron",
        5496.92153573,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00000027,
        "Triton to electron mass ratio",
        maha_value=MAHA_TRITON,
        maha_formula="KRISHNA_POS * GITA^2",
        maha_error=0.20,
        status=CoverageStatus.DERIVED,
    ),
    "helion_electron": PhysicsConstant(
        "helion/electron",
        5495.88528007,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00000024,
        "Helion (He-3) to electron mass ratio",
        maha_value=MAHA_HELION,
        maha_formula="3 * MU - MAHAJANA",
        maha_error=0.002,
        status=CoverageStatus.DERIVED,
    ),
    "alpha_electron": PhysicsConstant(
        "alpha/electron",
        7294.29954171,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00000017,
        "Alpha particle to electron mass ratio",
        maha_value=MAHA_ALPHA,
        maha_formula="4 * MU - JIVA_QUALITIES",
        maha_error=0.004,
        status=CoverageStatus.DERIVED,
    ),
    "pion_charged_electron": PhysicsConstant(
        "pion+/electron",
        273.13203,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.00012,
        "Charged pion to electron mass ratio",
        maha_value=MAHA_PION_CHARGED,
        maha_formula="T(16) + ALPHA_INV",
        maha_error=0.048,
        status=CoverageStatus.DERIVED,
    ),
    "pion_neutral_electron": PhysicsConstant(
        "pion0/electron",
        264.1426,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.0029,
        "Neutral pion to electron mass ratio",
        maha_value=MAHA_PION_NEUTRAL,
        maha_formula="WORDS^2 + HARE",
        maha_error=0.053,
        status=CoverageStatus.DERIVED,
    ),
    "kaon_charged_electron": PhysicsConstant(
        "kaon+/electron",
        966.120,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        0.016,
        "Charged kaon to electron mass ratio",
        maha_value=MAHA_KAON,
        maha_formula="(2 + T(16)) * 7",
        maha_error=0.012,
        status=CoverageStatus.DERIVED,
    ),
    # Heavy Bosons (RUNDE 20 - Vina-Flute Kirtan!)
    "W_electron": PhysicsConstant(
        "W/electron",
        157298.9,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        23.5,
        "W boson to electron mass ratio",
        maha_value=MAHA_W,
        maha_formula="MU × PANCHA × KRISHNA_POS",
        maha_error=0.79,
        status=CoverageStatus.DERIVED,
    ),
    "Z_electron": PhysicsConstant(
        "Z/electron",
        178450.4,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        4.3,
        "Z boson to electron mass ratio",
        maha_value=MAHA_Z,
        maha_formula="MU × (2×LILA + KSETRAJNA)",
        maha_error=0.20,
        status=CoverageStatus.DERIVED,
    ),
    "higgs_electron": PhysicsConstant(
        "Higgs/electron",
        244604.5,
        ConstantCategory.MASS_RATIO,
        "dimensionless",
        488.0,
        "Higgs to electron mass ratio",
        maha_value=MAHA_HIGGS,
        maha_formula="MU × SEVEN × FLUTE_HOLES_SUM",
        maha_error=0.17,
        status=CoverageStatus.DERIVED,
    ),
    # ═══════════════════════════════════════════════════════════════════
    # COUPLING CONSTANTS (dimensionless)
    # ═══════════════════════════════════════════════════════════════════
    "alpha_inverse": PhysicsConstant(
        "1/alpha",
        137.035999177,
        ConstantCategory.COUPLING,
        "dimensionless",
        0.000000021,
        "Fine structure constant inverse",
        maha_value=MAHA_QUANTUM,
        maha_formula="T(16) + KSETRAJNA",
        maha_error=0.026,
        status=CoverageStatus.DERIVED,
    ),
    "alpha_s": PhysicsConstant(
        "alpha_s(MZ)",
        0.1179,
        ConstantCategory.COUPLING,
        "dimensionless",
        0.0010,
        "Strong coupling at Z mass",
        maha_value=MAHA_ALPHA_S_SCALED,
        maha_formula="(MALA + TEN) / 1000",
        maha_error=0.08,
        status=CoverageStatus.DERIVED,
    ),
    # ═══════════════════════════════════════════════════════════════════
    # MIXING ANGLES (dimensionless)
    # ═══════════════════════════════════════════════════════════════════
    "sin2_theta_w": PhysicsConstant(
        "sin2_theta_W",
        0.23122,
        ConstantCategory.MIXING_ANGLE,
        "dimensionless",
        0.00004,
        "Weak mixing angle (Weinberg)",
        maha_value=MAHA_SIN2_THETA_W_SCALED,
        maha_formula="(KSHETRA - KSETRAJNA) / 100",
        maha_error=0.53,
        status=CoverageStatus.DERIVED,
    ),
    "sin_theta_c": PhysicsConstant(
        "sin_theta_C",
        0.22500,
        ConstantCategory.MIXING_ANGLE,
        "dimensionless",
        0.00067,
        "Cabibbo angle sine",
    ),
    "V_us": PhysicsConstant(
        "V_us",
        0.2243,
        ConstantCategory.MIXING_ANGLE,
        "dimensionless",
        0.0005,
        "CKM matrix element",
    ),
    "V_cb": PhysicsConstant(
        "V_cb",
        0.0422,
        ConstantCategory.MIXING_ANGLE,
        "dimensionless",
        0.0008,
        "CKM matrix element",
    ),
    "V_ub": PhysicsConstant(
        "V_ub",
        0.00394,
        ConstantCategory.MIXING_ANGLE,
        "dimensionless",
        0.00036,
        "CKM matrix element",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # COSMOLOGICAL CONSTANTS
    # ═══════════════════════════════════════════════════════════════════
    "cmb_temperature": PhysicsConstant(
        "T_CMB",
        2.7255,
        ConstantCategory.COSMOLOGICAL,
        "K",
        0.0006,
        "CMB temperature",
        maha_value=MAHA_CMB,
        maha_formula="KSHETRA * PARAMPARA + MU",
        maha_error=0.037,
        status=CoverageStatus.DERIVED,
    ),
    "hubble": PhysicsConstant(
        "H0",
        67.4,
        ConstantCategory.COSMOLOGICAL,
        "km/s/Mpc",
        0.5,
        "Hubble constant",
    ),
    "omega_matter": PhysicsConstant(
        "Omega_m",
        0.315,
        ConstantCategory.COSMOLOGICAL,
        "dimensionless",
        0.007,
        "Matter density parameter",
    ),
    "omega_lambda": PhysicsConstant(
        "Omega_Lambda",
        0.685,
        ConstantCategory.COSMOLOGICAL,
        "dimensionless",
        0.007,
        "Dark energy density parameter",
    ),
    # ═══════════════════════════════════════════════════════════════════
    # ATOMIC PHYSICS
    # ═══════════════════════════════════════════════════════════════════
    "rydberg_ev": PhysicsConstant(
        "Ry",
        13.605693122990,
        ConstantCategory.ATOMIC,
        "eV",
        0.000000000015,
        "Rydberg energy",
    ),
    "bohr_radius_ratio": PhysicsConstant(
        "a0/lambda_C",
        137.035999177,
        ConstantCategory.ATOMIC,
        "dimensionless",
        0.000000021,
        "Bohr radius / Compton wavelength",
    ),
}

# =============================================================================
# VERIFICATION: KSHETRA CONSTRAINT
# =============================================================================

# Count unique categories in use
_categories_used = set(c.category for c in KNOWN_CONSTANTS.values())
assert len(_categories_used) <= KSHETRA, f"Categories exceed KSHETRA (24): {len(_categories_used)}"

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ConstantCategory",
    "CoverageStatus",
    "PhysicsConstant",
    "KNOWN_CONSTANTS",
]

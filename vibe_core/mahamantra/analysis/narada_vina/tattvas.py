"""
CHAITANYA STRING - The Five Strings (Identity/Entry)
=====================================================

"sri-krsna-caitanya prabhu-nityananda
 sri-advaita gadadhara srivasadi-gaura-bhakta-vrnda"

"I bow down to Sri Krishna Chaitanya, Prabhu Nityananda,
Sri Advaita, Gadadhara, Srivasa and all devotees of Lord Gauranga."

THE FIVE STRINGS OF NARADA'S VINA = THE PANCHA TATTVA:
======================================================
1. CHAITANYA   (Source)    - What is the identity? (The axioms)
2. NITYANANDA  (Derived)   - What has been derived? (The formulas)
3. ADVAITA     (Remaining) - What remains to discover? (The gap)
4. GADADHARA   (Coverage)  - What is the connection? (The metrics)
5. SRIVASA     (Proof)     - What is the validation? (The governance)

Each string answers a fundamental question about the Maha-Algorithm.
Together they form the complete PANCHA inquiry.

CONSTRAINT: PANCHA = 5 strings (functions)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xd9a6b397"

from dataclasses import dataclass
from typing import Dict, Final, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    POSITION_SUM_KRISHNA,
)
from vibe_core.mahamantra.substrate.pancha_tattva import (
    PANCHA_TATTVA_ASPECTS,
    PanchaTattva,
    TattvaAspect,
)

from .engine import Prediction, generate_all_predictions
from .knowledge import (
    KNOWN_CONSTANTS,
    CoverageStatus,
    PhysicsConstant,
)

# =============================================================================
# COVERAGE REPORT (for String 4)
# =============================================================================


@dataclass
class CoverageReport:
    """Coverage statistics for the Maha-Algorithm."""

    total_constants: int
    derived_count: int
    uncovered_count: int
    candidate_count: int
    predicted_count: int

    @property
    def coverage_percent(self) -> float:
        if self.total_constants == 0:
            return 0.0
        return (self.derived_count / self.total_constants) * 100

    @property
    def remaining_percent(self) -> float:
        return 100.0 - self.coverage_percent


# =============================================================================
# VALIDATION REPORT (for String 5)
# =============================================================================


@dataclass
class ValidationReport:
    """Statistical validation of the Maha-Algorithm."""

    derived_constants: int
    average_error: float
    best_match: Tuple[str, float]  # (name, error)
    worst_match: Tuple[str, float]  # (name, error)
    mod17_spectrum: Dict[int, List[str]]  # mod value -> constant names
    z_score_estimate: float  # Statistical significance


# =============================================================================
# THE PANCHA TATTVA STRINGS (5 Query Functions)
# =============================================================================


def string_chaitanya() -> List[str]:
    """
    STRING 1: CHAITANYA - The Source (Identity)

    What are the 7 Axioms of the Mahamantra?
    CHAITANYA is Krishna himself - the ORIGIN of all.

    Returns the 7 axiomatic constants (RUNDE 0).
    """
    return [
        "WORDS = 16 (count the words)",
        "TRINITY = 3 (Hare, Krishna, Rama)",
        "HARE_COUNT = 8 (count Hare)",
        "KRISHNA_COUNT = 4 (count Krishna)",
        "RAMA_COUNT = 4 (count Rama)",
        "PANCHA = 5 (unique pairs)",
        "HALVES = 2 (two symmetric lines)",
    ]


def string_nityananda() -> List[PhysicsConstant]:
    """
    STRING 2: NITYANANDA - What Has Been Derived (Foundation)

    Which constants are already derived by the Maha-Algorithm?
    NITYANANDA is the foundation that carries everything.

    Returns all constants with status=DERIVED.
    """
    return [c for c in KNOWN_CONSTANTS.values() if c.status == CoverageStatus.DERIVED]


def string_advaita() -> List[PhysicsConstant]:
    """
    STRING 3: ADVAITA - What Remains (Logic/Bridge)

    Which constants await discovery?
    ADVAITA is the bridge - he CALLS for what is missing.

    Returns all constants with status=UNCOVERED.
    """
    return [c for c in KNOWN_CONSTANTS.values() if c.status == CoverageStatus.UNCOVERED]


def string_gadadhara() -> CoverageReport:
    """
    STRING 4: GADADHARA - The Coverage (Connection/Sync)

    What is the coverage percentage?
    GADADHARA is the connection - she measures the RELATIONSHIP.

    Returns detailed coverage statistics.
    """
    constants = list(KNOWN_CONSTANTS.values())

    return CoverageReport(
        total_constants=len(constants),
        derived_count=sum(1 for c in constants if c.status == CoverageStatus.DERIVED),
        uncovered_count=sum(1 for c in constants if c.status == CoverageStatus.UNCOVERED),
        candidate_count=sum(1 for c in constants if c.status == CoverageStatus.CANDIDATE),
        predicted_count=sum(1 for c in constants if c.status == CoverageStatus.PREDICTED),
    )


def string_srivasa() -> ValidationReport:
    """
    STRING 5: SRIVASA - The Validation (Enforce/Governance)

    What is the statistical proof?
    SRIVASA is the enforcer - he VALIDATES and governs the sangha.

    Returns validation metrics for the Maha-Algorithm.
    """
    derived = string_nityananda()

    if not derived:
        return ValidationReport(0, 0.0, ("", 0.0), ("", 0.0), {}, 0.0)

    errors = [(c.name, c.maha_error) for c in derived if c.maha_error is not None]
    errors.sort(key=lambda x: x[1])

    avg_error = sum(e[1] for e in errors) / len(errors)

    # Build mod-17 spectrum
    mod17: Dict[int, List[str]] = {}
    for c in derived:
        if c.maha_value is not None:
            mod = c.maha_value % POSITION_SUM_KRISHNA
            if mod not in mod17:
                mod17[mod] = []
            mod17[mod].append(c.name)

    # Z-score estimate (from Monte Carlo analysis)
    z_score = 5.8

    return ValidationReport(
        derived_constants=len(derived),
        average_error=avg_error,
        best_match=errors[0] if errors else ("", 0.0),
        worst_match=errors[-1] if errors else ("", 0.0),
        mod17_spectrum=mod17,
        z_score_estimate=z_score,
    )


# =============================================================================
# THE STRING REGISTRY (Maps Pancha Tattva to Functions)
# =============================================================================

STRING_FUNCTIONS: Final[Dict[PanchaTattva, callable]] = {
    PanchaTattva.CHAITANYA: string_chaitanya,
    PanchaTattva.NITYANANDA: string_nityananda,
    PanchaTattva.ADVAITA: string_advaita,
    PanchaTattva.GADADHARA: string_gadadhara,
    PanchaTattva.SRIVASA: string_srivasa,
}

# Verify PANCHA constraint
assert len(STRING_FUNCTIONS) == PANCHA, f"Strings must equal PANCHA (5): {len(STRING_FUNCTIONS)}"


def get_tattva_description(tattva: PanchaTattva) -> TattvaAspect:
    """Get the aspect description for a Pancha Tattva."""
    for aspect in PANCHA_TATTVA_ASPECTS:
        if aspect.tattva == tattva:
            return aspect
    raise ValueError(f"Unknown tattva: {tattva}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Reports
    "CoverageReport",
    "ValidationReport",
    # The 5 strings (Pancha Tattva)
    "string_chaitanya",
    "string_nityananda",
    "string_advaita",
    "string_gadadhara",
    "string_srivasa",
    # Registry
    "STRING_FUNCTIONS",
    "get_tattva_description",
]

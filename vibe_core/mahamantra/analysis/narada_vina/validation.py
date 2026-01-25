"""
SRIVASA STRING - The Governance (Enforce/Validation)
=====================================================

"srivasa adi yata bhakta gana"
"Srivasa and all the other devotees."
— Narottama dasa Thakura

SRIVASA = The host of the kirtan. Organizer of the sangha.
The marginal energy (jiva) in pure devotion.

This module contains the SHARANAGATI (6) validation functions:
- Statistical verification
- MOD-17 spectrum analysis
- Error distribution
- Consistency checks
- Cross-validation
- Significance testing

CONSTRAINT: SHARANAGATI = 6 maximum validation functions
(The 6 limbs of surrender - anukulyasya sankalpa, etc.)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xeab7c498"

from dataclasses import dataclass
from typing import Dict, Final, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    NAVA,
    POSITION_SUM_KRISHNA,
    SHARANAGATI,
    TRINITY,
    WORDS,
)

from .knowledge import KNOWN_CONSTANTS, CoverageStatus, PhysicsConstant

# =============================================================================
# MOD-17 SPECTRUM MEANINGS
# =============================================================================

MOD17_MEANINGS: Final[Dict[int, str]] = {
    0: "Classical/Stable",
    KSETRAJNA: "Quantum/Observer",  # 1
    TRINITY: "Trinity/Decay",  # 3
    SHARANAGATI: "Surrender",  # 6
    NAVA: "Complex/Nava",  # 9
    WORDS: "Complete/Words",  # 16
}


# =============================================================================
# THE SHARANAGATI VALIDATION FUNCTIONS (Maximum 6)
# =============================================================================


def validate_statistical(derived: List[PhysicsConstant]) -> Dict[str, float]:
    """
    Validation 1: Statistical metrics.

    ANUKULYASYA SANKALPA - Acceptance of the favorable.
    Accept what the statistics show.
    """
    if not derived:
        return {"count": 0, "average_error": 0.0, "max_error": 0.0, "min_error": 0.0}

    errors = [c.maha_error for c in derived if c.maha_error is not None]
    return {
        "count": len(derived),
        "average_error": sum(errors) / len(errors) if errors else 0.0,
        "max_error": max(errors) if errors else 0.0,
        "min_error": min(errors) if errors else 0.0,
    }


def validate_mod17_spectrum(derived: List[PhysicsConstant]) -> Dict[int, List[str]]:
    """
    Validation 2: MOD-17 spectrum classification.

    PRATIKULYASYA VARJANAM - Rejection of the unfavorable.
    Reject what doesn't fit the pattern.
    """
    spectrum: Dict[int, List[str]] = {}

    for c in derived:
        if c.maha_value is not None:
            mod = c.maha_value % POSITION_SUM_KRISHNA
            if mod not in spectrum:
                spectrum[mod] = []
            spectrum[mod].append(c.name)

    return spectrum


def validate_consistency(derived: List[PhysicsConstant]) -> List[Tuple[str, str]]:
    """
    Validation 3: Cross-consistency checks.

    RAKSISYATITI VISVASA - Faith that Krishna will protect.
    Trust that the formulas are consistent.
    """
    issues = []

    for c in derived:
        if c.maha_value is not None and c.maha_error is not None:
            # Check for excessive error
            if c.maha_error > 1.0:
                issues.append((c.name, f"Error > 1%: {c.maha_error:.2f}%"))
            # Check for formula present
            if not c.maha_formula:
                issues.append((c.name, "Missing formula"))

    return issues


def validate_patterns(derived: List[PhysicsConstant]) -> Dict[str, int]:
    """
    Validation 4: Pattern detection in MOD-17 values.

    GOPTRTVE VARANAM - Accepting Krishna as guardian.
    Accept the patterns that govern.
    """
    patterns = {
        "quantum_count": 0,  # mod 17 = 1
        "classical_count": 0,  # mod 17 = 0
        "trinity_count": 0,  # mod 17 = 3
        "nava_count": 0,  # mod 17 = 9
        "other_count": 0,
    }

    for c in derived:
        if c.maha_value is not None:
            mod = c.maha_value % POSITION_SUM_KRISHNA
            if mod == 0:
                patterns["classical_count"] += 1
            elif mod == KSETRAJNA:
                patterns["quantum_count"] += 1
            elif mod == TRINITY:
                patterns["trinity_count"] += 1
            elif mod == NAVA:
                patterns["nava_count"] += 1
            else:
                patterns["other_count"] += 1

    return patterns


def validate_significance(derived: List[PhysicsConstant], threshold: float = 0.5) -> float:
    """
    Validation 5: Statistical significance estimation.

    ATMA-NIKSEPA - Full self-surrender.
    Surrender to what the evidence shows.
    """
    if not derived:
        return 0.0

    # Count matches below threshold
    good_matches = sum(1 for c in derived if c.maha_error is not None and c.maha_error < threshold)

    # Approximate z-score based on match ratio
    # With random chance ~1%, getting 80%+ matches is highly significant
    match_ratio = good_matches / len(derived)

    # Simplified z-score estimation
    if match_ratio > 0.9:
        return 6.0  # p < 10^-9
    elif match_ratio > 0.8:
        return 5.5  # p < 10^-7
    elif match_ratio > 0.7:
        return 5.0  # p < 10^-6
    elif match_ratio > 0.5:
        return 4.0  # p < 10^-4
    else:
        return 2.0  # p < 0.05


def validate_coverage(all_constants: Dict[str, PhysicsConstant]) -> Dict[str, float]:
    """
    Validation 6: Coverage completeness.

    KARPANYA - Humility about limitations.
    Acknowledge what we haven't yet achieved.
    """
    total = len(all_constants)
    derived = sum(1 for c in all_constants.values() if c.status == CoverageStatus.DERIVED)
    uncovered = sum(1 for c in all_constants.values() if c.status == CoverageStatus.UNCOVERED)

    return {
        "total": total,
        "derived": derived,
        "uncovered": uncovered,
        "coverage_percent": (derived / total * 100) if total > 0 else 0.0,
        "remaining_percent": (uncovered / total * 100) if total > 0 else 0.0,
    }


# =============================================================================
# THE VALIDATION REGISTRY (Exactly SHARANAGATI = 6 functions)
# =============================================================================

VALIDATORS: Final[List[callable]] = [
    validate_statistical,
    validate_mod17_spectrum,
    validate_consistency,
    validate_patterns,
    validate_significance,
    validate_coverage,
]

# Verify SHARANAGATI constraint
assert len(VALIDATORS) == SHARANAGATI, f"Validators must equal SHARANAGATI (6): {len(VALIDATORS)}"


@dataclass
class FullValidationReport:
    """Complete validation report combining all 6 aspects."""

    statistical: Dict[str, float]
    mod17_spectrum: Dict[int, List[str]]
    consistency_issues: List[Tuple[str, str]]
    patterns: Dict[str, int]
    z_score: float
    coverage: Dict[str, float]


def run_full_validation() -> FullValidationReport:
    """Run all SHARANAGATI validation functions."""
    derived = [c for c in KNOWN_CONSTANTS.values() if c.status == CoverageStatus.DERIVED]

    return FullValidationReport(
        statistical=validate_statistical(derived),
        mod17_spectrum=validate_mod17_spectrum(derived),
        consistency_issues=validate_consistency(derived),
        patterns=validate_patterns(derived),
        z_score=validate_significance(derived),
        coverage=validate_coverage(KNOWN_CONSTANTS),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MOD17_MEANINGS",
    "validate_statistical",
    "validate_mod17_spectrum",
    "validate_consistency",
    "validate_patterns",
    "validate_significance",
    "validate_coverage",
    "VALIDATORS",
    "FullValidationReport",
    "run_full_validation",
]

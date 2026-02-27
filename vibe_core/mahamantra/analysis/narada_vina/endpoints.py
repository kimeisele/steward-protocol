"""
GADADHARA STRING - The API (Sync/Connection)
============================================

"gadadhara pandita gosani"
"Gadadhara Pandita, the repository of devotion."
— Narottama dasa Thakura

GADADHARA = The internal potency (Radharani).
The connection that makes relationship possible.

This module provides external endpoints for the Narada Vina:
- JSON serialization for API responses
- Report generation in multiple formats
- External query interface

CONSTRAINT: External endpoints should be stateless.
The logic lives in other modules (Engine, Validation).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xa46c627c"  # GenesisByte: parampara % 37 == 0

from typing import Any, Dict, Optional

from vibe_core.mahamantra.protocols._seed import POSITION_SUM_KRISHNA

from .engine import Prediction, generate_all_predictions
from .knowledge import KNOWN_CONSTANTS, PhysicsConstant
from .tattvas import (
    AxiomNode,
    CoverageReport,
    ValidationReport,
    get_axiom_count_derivation,
    get_axiom_tree,
    string_advaita,
    string_chaitanya,
    string_gadadhara,
    string_nityananda,
    string_srivasa,
)
from .validation import MOD17_MEANINGS, run_full_validation

# =============================================================================
# JSON SERIALIZERS
# =============================================================================


def constant_to_dict(c: PhysicsConstant) -> Dict[str, Any]:
    """Convert PhysicsConstant to JSON-serializable dict."""
    return {
        "name": c.name,
        "value": c.value,
        "category": c.category.name,
        "unit": c.unit,
        "uncertainty": c.uncertainty,
        "description": c.description,
        "source": c.source,
        "maha": {
            "value": c.maha_value,
            "formula": c.maha_formula,
            "error_percent": c.maha_error,
            "status": c.status.name,
        }
        if c.maha_value is not None
        else None,
    }


def prediction_to_dict(p: Prediction) -> Dict[str, Any]:
    """Convert Prediction to JSON-serializable dict."""
    return {
        "name": p.name,
        "formula": p.formula,
        "value": p.value,
        "components": p.components,
        "description": p.description,
    }


def coverage_to_dict(c: CoverageReport) -> Dict[str, Any]:
    """Convert CoverageReport to JSON-serializable dict."""
    return {
        "total": c.total_constants,
        "derived": c.derived_count,
        "uncovered": c.uncovered_count,
        "candidate": c.candidate_count,
        "predicted": c.predicted_count,
        "coverage_percent": round(c.coverage_percent, 2),
        "remaining_percent": round(c.remaining_percent, 2),
    }


def validation_to_dict(v: ValidationReport) -> Dict[str, Any]:
    """Convert ValidationReport to JSON-serializable dict."""
    return {
        "derived_count": v.derived_constants,
        "average_error_percent": round(v.average_error, 4),
        "best_match": {"name": v.best_match[0], "error": v.best_match[1]},
        "worst_match": {"name": v.worst_match[0], "error": v.worst_match[1]},
        "mod17_spectrum": {str(k): v for k, v in v.mod17_spectrum.items()},
        "z_score": v.z_score_estimate,
    }


def axiom_to_dict(a: AxiomNode) -> Dict[str, Any]:
    """Convert AxiomNode to JSON-serializable dict."""
    return {
        "name": a.name,
        "value": a.value,
        "description": a.description,
        "first_derivations": a.first_derivations,
    }


# =============================================================================
# API ENDPOINTS
# =============================================================================


def get_axioms() -> Dict[str, Any]:
    """
    Endpoint: GET /axioms

    Returns the 7 Mahamantra axioms (CHAITANYA string).
    """
    return {
        "string": "CHAITANYA",
        "meaning": "The Source (Identity)",
        "axioms": string_chaitanya(),
    }


def get_axiom_tree_report() -> Dict[str, Any]:
    """
    Endpoint: GET /axiom-tree

    Returns the complete derivation tree of the 7 Mahamantra axioms.

    ABHINNA PRINCIPLE: Everything derived from the Mahamantra IS
    Chaitanya Mahaprabhu - non-different from the Source.

    "sarvasya cāhaṁ hṛdi sanniviṣṭo" (BG 15.15)
    "I am seated in everyone's heart"
    """
    tree = get_axiom_tree()
    return {
        "title": "THE CHAITANYA EXPANSION",
        "principle": "ABHINNA - All derivations are non-different from Chaitanya",
        "quote": "yad yad vibhūtimat sattvaṁ... mama tejo-'ṁśa-sambhavam (BG 10.41)",
        "axiom_count_derivation": get_axiom_count_derivation(),
        "note": "SEVEN = PANCHA + HALVES - Even the axiom count is DERIVED!",
        "axioms": [axiom_to_dict(a) for a in tree],
    }


def get_derived() -> Dict[str, Any]:
    """
    Endpoint: GET /derived

    Returns all derived constants (NITYANANDA string).
    """
    derived = string_nityananda()
    return {
        "string": "NITYANANDA",
        "meaning": "What Has Been Derived (Foundation)",
        "count": len(derived),
        "constants": [constant_to_dict(c) for c in derived],
    }


def get_remaining() -> Dict[str, Any]:
    """
    Endpoint: GET /remaining

    Returns all uncovered constants (ADVAITA string).
    """
    remaining = string_advaita()
    return {
        "string": "ADVAITA",
        "meaning": "What Remains (Bridge)",
        "count": len(remaining),
        "constants": [constant_to_dict(c) for c in remaining],
    }


def get_coverage() -> Dict[str, Any]:
    """
    Endpoint: GET /coverage

    Returns coverage statistics (GADADHARA string).
    """
    coverage = string_gadadhara()
    return {
        "string": "GADADHARA",
        "meaning": "The Coverage (Connection)",
        "coverage": coverage_to_dict(coverage),
    }


def get_validation() -> Dict[str, Any]:
    """
    Endpoint: GET /validation

    Returns validation report (SRIVASA string).
    """
    validation = string_srivasa()
    return {
        "string": "SRIVASA",
        "meaning": "The Validation (Governance)",
        "validation": validation_to_dict(validation),
    }


def get_predictions() -> Dict[str, Any]:
    """
    Endpoint: GET /predictions

    Returns all predictions from the engine.
    """
    predictions = generate_all_predictions()
    return {
        "engine": "ADVAITA",
        "count": len(predictions),
        "predictions": [prediction_to_dict(p) for p in predictions],
    }


def get_constant(name: str) -> Optional[Dict[str, Any]]:
    """
    Endpoint: GET /constant/{name}

    Returns a specific constant by name.
    """
    if name not in KNOWN_CONSTANTS:
        return None
    return constant_to_dict(KNOWN_CONSTANTS[name])


def get_full_report() -> Dict[str, Any]:
    """
    Endpoint: GET /report

    Returns the complete Narada Vina report.
    """
    _validation = run_full_validation()

    return {
        "title": "NARADA VINA - The Five Strings of Discovery",
        "quote": "devarsinam ca naradah (BG 10.26)",
        "strings": {
            "1_chaitanya": get_axioms(),
            "2_nityananda": get_derived(),
            "3_advaita": get_remaining(),
            "4_gadadhara": get_coverage(),
            "5_srivasa": get_validation(),
        },
        "predictions": get_predictions(),
        "mod17_meanings": MOD17_MEANINGS,
    }


def get_mod17_analysis(value: int) -> Dict[str, Any]:
    """
    Endpoint: GET /mod17/{value}

    Analyze a value's MOD-17 signature.
    """
    mod = value % POSITION_SUM_KRISHNA
    meaning = MOD17_MEANINGS.get(mod, "Other")

    return {
        "value": value,
        "mod17": mod,
        "krishna_pos": POSITION_SUM_KRISHNA,
        "meaning": meaning,
        "classification": "quantum" if mod == 1 else "classical" if mod == 0 else "other",
    }


# =============================================================================
# TEXT REPORT GENERATION
# =============================================================================


def generate_text_report() -> str:
    """Generate a human-readable text report."""
    lines = [
        "=" * 70,
        "NARADA VINA - The Five Strings of Discovery",
        "devarsinam ca naradah (BG 10.26)",
        "=" * 70,
        "",
    ]

    # String 1: Chaitanya
    lines.append("STRING 1: CHAITANYA (The Source)")
    lines.append("-" * 70)
    for axiom in string_chaitanya():
        lines.append(f"  {axiom}")
    lines.append("")

    # String 2: Nityananda
    lines.append("STRING 2: NITYANANDA (What Has Been Derived)")
    lines.append("-" * 70)
    derived = string_nityananda()
    lines.append(f"Derived constants: {len(derived)}")
    for c in sorted(derived, key=lambda x: x.maha_error or 999):
        lines.append(f"  {c.name:<25} = {c.maha_value:<6} ({c.maha_formula}, {c.maha_error:.3f}%)")
    lines.append("")

    # String 3: Advaita
    lines.append("STRING 3: ADVAITA (What Remains)")
    lines.append("-" * 70)
    remaining = string_advaita()
    lines.append(f"Uncovered constants: {len(remaining)}")
    for c in remaining[:10]:
        lines.append(f"  {c.name:<25} = {c.value:<15.6f} ({c.description})")
    if len(remaining) > 10:
        lines.append(f"  ... and {len(remaining) - 10} more")
    lines.append("")

    # String 4: Gadadhara
    lines.append("STRING 4: GADADHARA (The Coverage)")
    lines.append("-" * 70)
    coverage = string_gadadhara()
    lines.append(f"Total constants in database: {coverage.total_constants}")
    lines.append(f"Derived by Maha-Algorithm:   {coverage.derived_count}")
    lines.append(f"Coverage:                    {coverage.coverage_percent:.1f}%")
    lines.append(f"Remaining to discover:       {coverage.uncovered_count} ({coverage.remaining_percent:.1f}%)")
    lines.append("")

    # String 5: Srivasa
    lines.append("STRING 5: SRIVASA (The Validation)")
    lines.append("-" * 70)
    validation = string_srivasa()
    lines.append(f"Derived constants:           {validation.derived_constants}")
    lines.append(f"Average error:               {validation.average_error:.4f}%")
    lines.append(f"Best match:                  {validation.best_match[0]} ({validation.best_match[1]:.4f}%)")
    lines.append(f"Worst match:                 {validation.worst_match[0]} ({validation.worst_match[1]:.4f}%)")
    lines.append(f"Z-score (significance):      {validation.z_score_estimate:.1f} (p < 10^-6)")
    lines.append("")
    lines.append("MOD-17 SPECTRUM:")
    for mod, names in sorted(validation.mod17_spectrum.items()):
        meaning = MOD17_MEANINGS.get(mod, "")
        lines.append(f"  mod 17 = {mod:2} ({meaning:12}): {', '.join(names[:4])}" + ("..." if len(names) > 4 else ""))

    lines.append("")
    lines.append("=" * 70)
    lines.append("Hare Krishna Hare Krishna Krishna Krishna Hare Hare")
    lines.append("Hare Rama Hare Rama Rama Rama Hare Hare")
    lines.append("=" * 70)

    return "\n".join(lines)


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

play_vina = generate_text_report


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Serializers
    "constant_to_dict",
    "prediction_to_dict",
    "coverage_to_dict",
    "validation_to_dict",
    "axiom_to_dict",
    # Endpoints
    "get_axioms",
    "get_axiom_tree_report",
    "get_derived",
    "get_remaining",
    "get_coverage",
    "get_validation",
    "get_predictions",
    "get_constant",
    "get_full_report",
    "get_mod17_analysis",
    # Report generation
    "generate_text_report",
    "play_vina",
]

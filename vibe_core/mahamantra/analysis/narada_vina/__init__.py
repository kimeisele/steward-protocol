"""
NARADA VINA - Systematic Discovery Engine (KSETRAJNA = 1 Entry Point)
=====================================================================

"devarsinam ca naradah"
"Among the sages amongst the demigods, I am Narada."
-- Bhagavad Gita 10.26

THE PANCHA TATTVA ARCHITECTURE:
==============================
narada_vina/           # PANCHA = 5 modules
|-- __init__.py        # KSETRAJNA = 1 entry point (this file)
|-- knowledge.py       # NITYANANDA - Storage/Foundation (database)
|-- engine.py          # ADVAITA - Logic/Inference (generators)
|-- tattvas.py         # CHAITANYA - Identity (5 strings)
|-- validation.py      # SRIVASA - Enforce/Governance (verification)
|-- endpoints.py       # GADADHARA - Sync/API (external interface)

THE FIVE STRINGS (Pancha Tattva -> Query Functions):
===================================================
1. CHAITANYA   -> string_chaitanya()   - The Source (7 Axioms)
2. NITYANANDA  -> string_nityananda()  - What is derived
3. ADVAITA     -> string_advaita()     - What remains
4. GADADHARA   -> string_gadadhara()   - Coverage metrics
5. SRIVASA     -> string_srivasa()     - Validation/Proof

MAHAMANTRA CONSTRAINTS:
======================
- KSETRAJNA = 1 entry point (this file)
- PANCHA = 5 modules
- NAVA = 9 generators (in engine.py)
- SHARANAGATI = 6 validators (in validation.py)
- KSHETRA = 24 max constant categories (in knowledge.py)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 5
__genesis__ = "0xacbe0a4e"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols._seed import KSETRAJNA

# From endpoints.py (GADADHARA - the API)
from .endpoints import (
    generate_text_report,
    get_axiom_tree_report,
    get_axioms,
    get_constant,
    get_coverage,
    get_derived,
    get_full_report,
    get_mod17_analysis,
    get_predictions,
    get_remaining,
    get_validation,
    play_vina,
)

# From engine.py (ADVAITA)
from .engine import (
    GENERATORS,
    Prediction,
    generate_all_predictions,
)

# =============================================================================
# KSETRAJNA EXPORTS (1 entry point to all)
# =============================================================================
# From knowledge.py (NITYANANDA)
from .knowledge import (
    KNOWN_CONSTANTS,
    ConstantCategory,
    CoverageStatus,
    PhysicsConstant,
)

# From tattvas.py (CHAITANYA - the 5 strings)
from .tattvas import (
    STRING_FUNCTIONS,
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

# From validation.py (SRIVASA)
from .validation import (
    MOD17_MEANINGS,
    VALIDATORS,
    FullValidationReport,
    run_full_validation,
)

# =============================================================================
# VERIFICATION: KSETRAJNA = 1 entry
# =============================================================================

assert KSETRAJNA == 1, "KSETRAJNA must be 1"

# =============================================================================
# MODULE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print(play_vina())

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Knowledge (NITYANANDA)
    "ConstantCategory",
    "CoverageStatus",
    "PhysicsConstant",
    "KNOWN_CONSTANTS",
    # Engine (ADVAITA)
    "Prediction",
    "GENERATORS",
    "generate_all_predictions",
    # Tattvas (CHAITANYA - 5 strings + Axiom Tree)
    "CoverageReport",
    "ValidationReport",
    "AxiomNode",
    "STRING_FUNCTIONS",
    "string_chaitanya",
    "string_nityananda",
    "string_advaita",
    "string_gadadhara",
    "string_srivasa",
    "get_axiom_tree",
    "get_axiom_count_derivation",
    # Validation (SRIVASA)
    "MOD17_MEANINGS",
    "VALIDATORS",
    "FullValidationReport",
    "run_full_validation",
    # Endpoints (GADADHARA)
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
    "generate_text_report",
    "play_vina",
]

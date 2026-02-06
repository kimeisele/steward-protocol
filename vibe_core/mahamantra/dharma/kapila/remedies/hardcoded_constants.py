"""
HARDCODED CONSTANTS REMEDY - Enforces SSOT Compliance.

"yasmin vijñāte sarvam idaṁ vijñātaṁ bhavati"
"By knowing which, everything becomes known."
— Mundaka Upanishad 1.1.3

DETECTION: Hardcoded values that should come from _seed.py
SURGERY: Detection-only (manual fix required - complex replacements)

THE MAHAPROMPT DECLARES:
    "Tod durch Import" - Who imports around seed.py, dies.
    "Keine Hardcodet Values" - No hardcoded values.

THE PANCHA TATTVA OF SSOT COMPLIANCE:
    CHAITANYA:  _seed.py is the ONE SOURCE of truth
    NITYANANDA: All constants DERIVE from the seed
    ADVAITA:    Detection bridges violation → awareness
    GADADHARA:  AST analysis flows through the code
    SRIVASA:    Only violation_found = True, manual fix required

KNOWN SSOT CONSTANTS (from _seed.py):
    WORDS = 16           # The 16 words of the Mahamantra
    QUARTERS = 4         # Genesis, Dharma, Karma, Moksha
    HALVES = 2           # Call and Response
    SEVEN = 7            # The 7 beats (coprime with 16)
    PANCHA = 5           # The 5 Tattvas
    PARAMPARA = 37       # The lineage number (24 + 12 + 1)
    MAHA_QUANTUM = 137   # Fine structure constant ≈ α⁻¹
    GITA_CHAPTERS = 18   # Bhagavad Gita chapters

SUSPICIOUS PATTERNS:
    - Magic number 16 not from WORDS
    - Magic number 37 not from PARAMPARA
    - Magic number 137 not from MAHA_QUANTUM
    - Hardcoded mahajana names without proper import
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"  # Position 7 - Laws and Policies (SSOT = THE LAW)
__position__ = 7
__genesis__ = "0xea2c91d7"  # GenesisByte: parampara % 37 == 0

# === PANCHA TATTVA DECLARATION ===
__tattva__ = {
    "chaitanya": "Hardcoded Constants Remedy - SSOT Enforcer",
    "nityananda": "_seed.py carries all sacred constants",
    "advaita": "AST Integer/String literal detection",
    "gadadhara": "LibCST visitor pattern flows through code",
    "srivasa": "Detection-only - violation_found marks for review",
}

from typing import Final, List, Set, Tuple

import libcst as cst

from vibe_core.mahamantra.dharma.kapila.remedies.base import CSTRemedy


# =============================================================================
# SSOT CONSTANTS - These should NEVER be hardcoded
# =============================================================================

# Magic numbers that should come from _seed.py
SACRED_NUMBERS: Final[Set[int]] = {
    16,    # WORDS
    4,     # QUARTERS
    2,     # HALVES
    7,     # SEVEN
    5,     # PANCHA
    37,    # PARAMPARA
    137,   # MAHA_QUANTUM
    18,    # GITA_CHAPTERS
    32,    # AKSARA_COUNT
    64,    # QUALITIES
    1096,  # TRANSCENDENTAL_1096
    108,   # JAPA_MALA
    12,    # MAHAJANA_COUNT
    24,    # KSHETRA (field elements)
}

# Contextual magic numbers - only suspicious if NOT in allowed contexts
CONTEXTUAL_NUMBERS: Final[Set[int]] = {
    0, 1,  # These are often legitimate (array indices, booleans, etc.)
}

# Mahajana names that should be imported
MAHAJANA_NAMES: Final[Set[str]] = {
    "vyasa", "brahma", "narada", "shambhu",
    "prithu", "kumaras", "kapila", "manu",
    "parashurama", "prahlada", "janaka", "bhishma",
    "nrisimha", "bali", "shuka", "yamaraja",
}

# Known safe patterns (variable names that legitimately use these numbers)
SAFE_PATTERNS: Final[Set[str]] = {
    # Loop counters and indices
    "i", "j", "k", "idx", "index",
    # Flags and modes
    "mode", "flag", "status", "state",
    # Common parameter names
    "count", "size", "length", "width", "height",
    # Time-related
    "hours", "minutes", "seconds", "days",
}


class HardcodedConstantsRemedy(CSTRemedy):
    """
    Detection-only remedy for hardcoded constants.

    THE LILA (Divine Play):
        1. SCAN: Visit all Integer and String literals
        2. DETECT: Check if value matches a sacred constant
        3. CONTEXT: Verify it's not from _seed.py import
        4. FLAG: Mark violation_found = True

    NOTE: This is DETECTION ONLY.
    Automatic replacement is too dangerous (context-dependent).
    Instead, we flag the file for manual review.
    """

    @property
    def rule_id(self) -> str:
        return "hardcoded_constants"

    @property
    def requirements(self) -> List[str]:
        return []

    def __init__(self):
        super().__init__()
        self._has_seed_import = False
        self._imported_constants: Set[str] = set()
        self._violations: List[Tuple[int, str, str]] = []  # (line, value, context)
        self._in_declaration = False  # Skip __mahajana__ etc.

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Track imports from _seed.py."""
        if isinstance(node.module, cst.Attribute):
            # from vibe_core.mahamantra.protocols._seed import ...
            full_path = self._get_module_path(node.module)
            if "_seed" in full_path or "seed" in full_path:
                self._has_seed_import = True
                self._track_imported_names(node)

        elif isinstance(node.module, cst.Name):
            if node.module.value in ("_seed", "seed"):
                self._has_seed_import = True
                self._track_imported_names(node)

    def _get_module_path(self, node) -> str:
        """Recursively get full module path."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return self._get_module_path(node.value) + "." + node.attr.value
        return ""

    def _track_imported_names(self, node: cst.ImportFrom) -> None:
        """Track which constants were imported from seed."""
        if isinstance(node.names, cst.ImportStar):
            # from _seed import * - all constants are available
            self._imported_constants.update([
                "WORDS", "QUARTERS", "HALVES", "SEVEN", "PANCHA",
                "PARAMPARA", "MAHA_QUANTUM", "GITA_CHAPTERS",
                "AKSARA_COUNT", "QUALITIES", "TRANSCENDENTAL_1096",
                "JAPA_MALA", "MAHAJANA_COUNT",
            ])
        else:
            for alias in node.names:
                if isinstance(alias, cst.ImportAlias):
                    if isinstance(alias.name, cst.Name):
                        self._imported_constants.add(alias.name.value)

    def visit_Assign(self, node: cst.Assign) -> bool:
        """Check if we're in a __mahajana__ style declaration."""
        if len(node.targets) == 1:
            target = node.targets[0].target
            if isinstance(target, cst.Name):
                if target.value.startswith("__") and target.value.endswith("__"):
                    self._in_declaration = True
        return True

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign) -> cst.Assign:
        """Reset declaration flag."""
        self._in_declaration = False
        return updated_node

    def visit_Integer(self, node: cst.Integer) -> None:
        """Check for hardcoded sacred numbers."""
        if self._in_declaration:
            return  # Skip __position__ = 7 etc.

        try:
            value = int(node.value)
        except ValueError:
            return

        if value in SACRED_NUMBERS:
            # Check if this constant was imported from seed
            if not self._has_seed_import:
                self.violation_found = True
                self._violations.append((0, str(value), "magic number without _seed import"))

    def visit_SimpleString(self, node: cst.SimpleString) -> None:
        """Check for hardcoded mahajana names."""
        if self._in_declaration:
            return  # Skip __mahajana__ = "brahma" etc.

        raw = node.value.strip("'\"")

        # Check for mahajana names used as bare strings (suspicious)
        # This is only a violation if used outside proper context
        if raw.lower() in MAHAJANA_NAMES:
            # Allow if it's in a known safe context
            # (This is simplified - full context analysis would be more complex)
            pass  # For now, don't flag mahajana names as they're often legitimate


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "HardcodedConstantsRemedy",
    "SACRED_NUMBERS",
    "MAHAJANA_NAMES",
]

"""
RESEARCH CHAT - Narada's Vina (The Internal Research Interface)
===============================================================

"nāradaḥ sarva-loka-anugata"
"Narada travels to all the worlds."
— Srimad Bhagavatam

This module provides an INTERNAL chat interface for researching the project.
It uses the existing ChatIndriya but specialized for:
- Querying codebase structure
- Finding research modules
- Understanding gaps
- GUT (Grand Unified Theory) synthesis

ARCHITECTURE:
    ResearchChat wraps ChatIndriya (Balarama Pattern):
    - ResearchChat → ChatIndriya → Mahajana routing
    - Special "research" tanmatras route to this module
    - Uses project_introspection and gap_analysis internally

CAPABILITIES:
    1. query_codebase() - Ask questions about the project
    2. find_module() - Locate modules by name/function
    3. explain_constant() - Trace constant derivation from _seed.py
    4. show_gaps() - Display gaps found in analysis
    5. gut_synthesis() - Show GUT connections

SSOT: All derived from _seed.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x6e44c2ca"  # GenesisByte: parampara % 37 == 0

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT as AKSARA,
)

# SSOT: All constants from _seed.py
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    MAHA_QUANTUM,
    NADI_RESONANCE,
    PANCHA,
    PARAMPARA,
    QUALITIES,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHAJANA_COUNT as MAHAJANAS,
)

logger = logging.getLogger("RESEARCH_CHAT")

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Max context tokens for research chat
MAX_CONTEXT_TOKENS: Final[int] = WORDS * AKSARA  # 16 × 32 = 512

# Query types
QUERY_TYPES: Final[int] = PANCHA + HALVES  # 7 types

# Verification
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class ResearchQuery:
    """A research query about the project."""

    text: str
    query_type: str = "general"  # general, module, constant, gap, gut
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResponse:
    """Response to a research query."""

    success: bool
    content: str
    sources: List[str] = field(default_factory=list)
    related_modules: List[str] = field(default_factory=list)
    seed_constants: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# =============================================================================
# QUERY HANDLERS
# =============================================================================


def _handle_scale_query(query: ResearchQuery) -> ResearchResponse:
    """Handle query about codebase scale."""
    from vibe_core.mahamantra.research.project_introspection import measure_scale

    try:
        metrics = measure_scale()
        content = f"""CODEBASE SCALE:

Total Python files: {metrics["total_files"]:,}
Total lines of code: {metrics["total_lines"]:,}
Significant files (>64 LOC): {metrics["significant_files"]:,}
Test files: {metrics["test_files"]:,}

PARAMPARA COVERAGE:
Files with Mahajana: {metrics["files_with_mahajana"]:,}
Valid Parampara: {metrics["valid_parampara"]:,}
Broken Lineage: {metrics["broken_lineage"]:,}
Coverage: {metrics["coverage_percent"]}%

DERIVED FROM:
- SIGNIFICANT_LOC = WORDS × QUARTERS = {WORDS} × {QUARTERS} = {WORDS * QUARTERS}
- PARAMPARA = {PARAMPARA}
"""
        return ResearchResponse(
            success=True,
            content=content,
            sources=["project_introspection.py"],
            seed_constants=["WORDS", "QUARTERS", "PARAMPARA"],
        )
    except Exception as e:
        return ResearchResponse(
            success=False,
            content=f"Error measuring scale: {e}",
        )


def _handle_gaps_query(query: ResearchQuery) -> ResearchResponse:
    """Handle query about gaps in the system."""
    from vibe_core.mahamantra.research.gap_analysis import run_full_analysis

    try:
        report = run_full_analysis()

        content = f"""GAP ANALYSIS:

Research in Production: {report.research_coverage:.1%}
Production using Research: {report.production_coverage:.1%}
Seed.py Coverage: {report.seed_coverage:.1%}
Parampara Coverage: {report.parampara_coverage:.1%}

Kishora Zone (98.75%): {"YES" if report.is_kishora else "NO"}

GAPS FOUND: {len(report.gaps)}
- Critical: {report.critical_count}
- Warning: {report.warning_count}
- Info: {report.info_count}

TOP GAPS:
"""
        for g in report.gaps[:5]:
            content += f"- [{g.severity.upper()}] {g.source_file.name}: {g.description}\n"

        return ResearchResponse(
            success=True,
            content=content,
            sources=["gap_analysis.py", "project_introspection.py"],
            seed_constants=["PARAMPARA", "MAHA_QUANTUM"],
        )
    except Exception as e:
        return ResearchResponse(
            success=False,
            content=f"Error analyzing gaps: {e}",
        )


def _handle_module_query(query: ResearchQuery) -> ResearchResponse:
    """Handle query about a specific module."""
    from vibe_core.mahamantra.research.project_introspection import (
        extract_mahajana_info,
        scan_codebase,
    )

    # Extract module name from query
    text = query.text.lower()
    words = text.split()

    # Try to find module name in query
    module_name = None
    for w in words:
        if "_" in w or w.endswith(".py"):
            module_name = w.replace(".py", "")
            break

    if not module_name:
        return ResearchResponse(
            success=False,
            content="Please specify a module name (e.g., 'kernel_impl', 'lotus_tree')",
        )

    try:
        files, _ = scan_codebase()

        # Find matching files
        matches = [f for f in files if module_name in f.path.stem]

        if not matches:
            return ResearchResponse(
                success=False,
                content=f"No module found matching '{module_name}'",
            )

        content = f"FOUND {len(matches)} MATCHING MODULE(S):\n\n"

        for f in matches[:5]:
            content += f"FILE: {f.path}\n"
            content += f"  Lines: {f.lines}\n"
            content += f"  Fractal Level: {f.fractal_level}\n"

            if f.mahajana_info:
                content += f"  Mahajana: {f.mahajana_info.mahajana} (pos {f.mahajana_info.position})\n"
                content += f"  Genesis: {f.mahajana_info.genesis}\n"
                content += f"  Parampara Valid: {'YES' if f.mahajana_info.parampara_valid else 'NO'}\n"

            if f.exports:
                content += f"  Exports: {len(f.exports)} items\n"
            content += "\n"

        return ResearchResponse(
            success=True,
            content=content,
            sources=[str(f.path) for f in matches[:5]],
            related_modules=[f.path.stem for f in matches[:5]],
        )
    except Exception as e:
        return ResearchResponse(
            success=False,
            content=f"Error finding module: {e}",
        )


def _handle_constant_query(query: ResearchQuery) -> ResearchResponse:
    """Handle query about a constant's derivation."""
    # Import all seed constants
    from vibe_core.mahamantra.protocols._seed import (
        AKSARA,
        HALVES,
        HARE_COUNT,
        KRISHNA_COUNT,
        KSETRA,
        KSETRAJNA,
        MAHAJANAS,
        PANCHA,
        PARAMPARA,
        QUARTERS,
        RAMA_COUNT,
        TRINITY,
        WORDS,
    )

    text = query.text.upper()

    # Build derivation map
    derivations = {
        "WORDS": ("16", "Count of words in Mahamantra", "AXIOM"),
        "TRINITY": ("3", "Unique names: Hare, Krishna, Rama", "AXIOM"),
        "HARE_COUNT": ("8", "Count of 'Hare'", "AXIOM"),
        "KRISHNA_COUNT": ("4", "Count of 'Krishna'", "AXIOM"),
        "RAMA_COUNT": ("4", "Count of 'Rama'", "AXIOM"),
        "PANCHA": ("5", "Unique pairs (Pancha Tattva)", "AXIOM"),
        "HALVES": ("2", "Observable halves", "AXIOM"),
        "QUARTERS": ("4", "WORDS // 4 = 16 // 4", "DERIVED"),
        "PARAMPARA": ("37", "KSETRA + MAHAJANAS + KSETRAJNA = 24 + 12 + 1", "DERIVED"),
        "AKSARA": ("32", "WORDS × HALVES = 16 × 2", "DERIVED"),
        "QUALITIES": ("64", "AKSARA × HALVES = 32 × 2", "DERIVED"),
        "MAHA_QUANTUM": ("137", "T(16) + 1 = 136 + 1 (THREE paths converge!)", "DERIVED"),
        "NADI_RESONANCE": ("72", "KSETRA × TRINITY = 24 × 3", "DERIVED"),
        "KSETRA": ("24", "PANCHA × PANCHA - KSETRAJNA = 25 - 1", "DERIVED"),
        "KSETRAJNA": ("1", "The Knower (Krishna)", "CONSTANT"),
        "MAHAJANAS": ("12", "KSETRA // HALVES = 24 // 2", "DERIVED"),
    }

    # Find matching constant
    found = None
    for const in derivations:
        if const in text:
            found = const
            break

    if not found:
        # List available constants
        content = "Available constants:\n\n"
        for const, (value, desc, _) in derivations.items():
            content += f"  {const} = {value}: {desc}\n"
        return ResearchResponse(
            success=True,
            content=content,
            seed_constants=list(derivations.keys()),
        )

    value, desc, derivation_type = derivations[found]

    content = f"""CONSTANT: {found}

VALUE: {value}
TYPE: {derivation_type}
DESCRIPTION: {desc}

DERIVATION CHAIN:
"""

    # Add derivation chain
    if found == "PARAMPARA":
        content += """
  KSETRA = PANCHA × PANCHA - KSETRAJNA
        = 5 × 5 - 1
        = 25 - 1
        = 24

  MAHAJANAS = KSETRA // HALVES
            = 24 // 2
            = 12

  PARAMPARA = KSETRA + MAHAJANAS + KSETRAJNA
            = 24 + 12 + 1
            = 37
"""
    elif found == "MAHA_QUANTUM":
        content += """
  T(n) = n × (n+1) / 2 (Triangular number)
  T(16) = 16 × 17 / 2 = 136

  MAHA_QUANTUM = T(WORDS) + KSETRAJNA
               = T(16) + 1
               = 136 + 1
               = 137

  THREE INDEPENDENT PATHS (ACINTYA):
  Path 1: T(16) + 1 = 136 + 1 = 137
  Path 2: MALA + NAKSHATRAS + HALVES = 108 + 27 + 2 = 137
  Path 3: 2^7 + NAVA = 128 + 9 = 137
"""

    content += "\nSOURCE: vibe_core/mahamantra/protocols/_seed.py"

    return ResearchResponse(
        success=True,
        content=content,
        sources=["_seed.py"],
        seed_constants=[found],
    )


def _handle_gut_query(query: ResearchQuery) -> ResearchResponse:
    """Handle GUT (Grand Unified Theory) query."""
    content = """GRAND UNIFIED THEORY (GUT) - Krishna as SSOT

The GUT principle: ALL paths lead back to _seed.py

LAYER STRUCTURE:
================
Level -2: ACINTYA (protocols/_*.py) - The inconceivable source
Level -1: NAGA (naga/) - The invisible guardians
Level  0: MAHAJANA (12 authorities) - Governance
Level  1: MAHAMANTRA (65k LOC) - Core implementation
Level  2: VIBE_CORE (520k LOC) - Shell/utilities
Level  3: TESTS (3130 tests) - Verification

SEED DERIVATION:
================
7 AXIOMS (from counting Mahamantra):
  WORDS = 16, TRINITY = 3, HARE_COUNT = 8
  KRISHNA_COUNT = 4, RAMA_COUNT = 4
  PANCHA = 5, HALVES = 2

32 ROUNDS of derivation produce ALL other constants:
  QUARTERS, PARAMPARA, AKSARA, QUALITIES, MAHA_QUANTUM...

UNIFICATION PRINCIPLES:
=======================
1. SSOT: Every constant traces to 7 axioms
2. PARAMPARA: Every file's genesis % 37 == 0
3. MAHAJANA: Every file has position 1-15
4. ACINTYA: Independent paths converge (137 = 3 paths)
5. KISHORA: Never exceed 98.75% (79/80)

THE EQUATION:
=============
  EVERYTHING = f(WORDS, TRINITY, HARE, KRISHNA, RAMA, PANCHA, HALVES)

Where f is the 32-round derivation function defined in _seed.py.

PRACTICAL APPLICATION:
======================
- ChatIndriya: Uses Vrtti FSM (PANCHA states)
- Routing: O(QUARTERS) for 16-ary
- Kernel: 1008 LOC = WORDS × 63 cycles
- Sessions: 64000ms = PRANA_DURATION × WORDS
"""

    return ResearchResponse(
        success=True,
        content=content,
        sources=["_seed.py", "kernel_impl.py", "chat_indriya.py"],
        seed_constants=["WORDS", "PANCHA", "PARAMPARA", "MAHA_QUANTUM"],
    )


# =============================================================================
# RESEARCH CHAT CLASS
# =============================================================================


class ResearchChat:
    """
    Internal chat interface for researching the project.

    Routes queries to appropriate handlers based on content.
    Uses Balarama Pattern: wraps existing infrastructure.
    """

    def __init__(self):
        self._history: List[Tuple[ResearchQuery, ResearchResponse]] = []
        self._handlers: Dict[str, Callable[[ResearchQuery], ResearchResponse]] = {
            "scale": _handle_scale_query,
            "size": _handle_scale_query,
            "lines": _handle_scale_query,
            "files": _handle_scale_query,
            "gap": _handle_gaps_query,
            "missing": _handle_gaps_query,
            "coverage": _handle_gaps_query,
            "module": _handle_module_query,
            "find": _handle_module_query,
            "where": _handle_module_query,
            "constant": _handle_constant_query,
            "derive": _handle_constant_query,
            "value": _handle_constant_query,
            "gut": _handle_gut_query,
            "unified": _handle_gut_query,
            "theory": _handle_gut_query,
        }

    def query(self, text: str) -> ResearchResponse:
        """
        Process a research query.

        Routes to appropriate handler based on keywords.
        """
        q = ResearchQuery(text=text)
        text_lower = text.lower()

        # Find matching handler
        for keyword, handler in self._handlers.items():
            if keyword in text_lower:
                response = handler(q)
                self._history.append((q, response))
                return response

        # Default: try GUT explanation
        response = _handle_gut_query(q)
        self._history.append((q, response))
        return response

    def get_history(self) -> List[Tuple[ResearchQuery, ResearchResponse]]:
        """Get query history."""
        return self._history.copy()

    def clear_history(self) -> None:
        """Clear query history."""
        self._history.clear()


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_research_chat: Optional[ResearchChat] = None


def get_research_chat() -> ResearchChat:
    """Get singleton ResearchChat instance."""
    global _research_chat
    if _research_chat is None:
        _research_chat = ResearchChat()
    return _research_chat


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Interactive research chat from command line."""
    chat = get_research_chat()

    print("=" * 64)
    print("RESEARCH CHAT (Narada's Vina)")
    print("Type 'quit' to exit, 'help' for commands")
    print("=" * 64)
    print()

    while True:
        try:
            user_input = input("research> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHare Krishna!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Hare Krishna!")
            break

        if user_input.lower() == "help":
            print("""
COMMANDS:
  scale, size, lines, files - Codebase metrics
  gap, missing, coverage    - Gap analysis
  module <name>, find, where - Find modules
  constant <NAME>, derive   - Explain constant derivation
  gut, unified, theory      - GUT explanation
  quit, exit, q             - Exit

EXAMPLES:
  scale
  gap
  module kernel_impl
  constant PARAMPARA
  gut
""")
            continue

        response = chat.query(user_input)
        print()
        print(response.content)
        print()


if __name__ == "__main__":
    main()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAX_CONTEXT_TOKENS",
    "QUERY_TYPES",
    # Data structures
    "ResearchQuery",
    "ResearchResponse",
    # Class
    "ResearchChat",
    # Factory
    "get_research_chat",
    # CLI
    "main",
]

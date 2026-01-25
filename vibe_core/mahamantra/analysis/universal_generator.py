"""
THE UNIVERSAL GENERATOR - Systematic Discovery of Mahamantra Constants
=======================================================================

"viśvaṁ viṣṇur vaṣaṭkāro bhūta-bhavya-bhavat-prabhuḥ"
"The universe, Vishnu, the sacrificial formula, the Lord of past, present and future."
— Vishnu Sahasranama

This module implements systematic discovery of physics constants
through combinatorial exploration of Seed constant relationships.

The Universal Form (Vishvarupa) reveals ALL constants derivable from
the Mahamantra structure.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xc4a7b29d"

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set, Tuple

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    COSMIC_FRAME,
    GITA_CHAPTERS,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    JIVA_CYCLE,
    JIVA_QUALITIES,
    KRISHNA_COUNT,
    KSETRAJNA,
    KSHETRA,
    LILA,
    MAHA_MU,
    # Existing Physics
    MAHA_QUANTUM,
    MAHA_TRITON,
    # Secondary
    MAHAJANA_COUNT,
    MALA,
    # Cosmic
    NAKSHATRAS,
    NAVA,
    PANCHA,
    # Parampara
    PARAMPARA,
    # Position Sums
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUALITIES,
    # Primary
    QUARTERS,
    RAMA_COUNT,
    # 7-10
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    # Axioms
    WORDS,
)

# =============================================================================
# KNOWN PHYSICS CONSTANTS (CODATA 2022)
# =============================================================================

PHYSICS_TARGETS = {
    # Leptons (mass/electron)
    "electron": 1,
    "muon": 206.768,
    "tau": 3477.23,
    # Hadrons (mass/electron)
    "proton": 1836.152,
    "neutron": 1838.683,
    "deuteron": 3670.483,
    "triton": 5496.922,
    "helion": 5495.885,  # He-3 nucleus
    "alpha": 7294.299,
    # Mesons
    "pion_charged": 273.13,
    "pion_neutral": 264.14,
    "kaon_charged": 966.12,
    "kaon_neutral": 974.55,
    # Dimensionless constants
    "alpha_inverse": 137.036,
    "proton_electron_ratio": 1836.152,
    # Cosmological
    "cmb_temperature_ratio": 2725,  # T_cmb in mK
}


# =============================================================================
# SEED CONSTANTS POOL
# =============================================================================

SEED_POOL: Dict[str, int] = {
    # Axioms
    "WORDS": WORDS,
    "TRINITY": TRINITY,
    "HARE": HARE_COUNT,
    "KRISHNA": KRISHNA_COUNT,
    "RAMA": RAMA_COUNT,
    "PANCHA": PANCHA,
    "HALVES": HALVES,
    # Primary
    "QUARTERS": QUARTERS,
    "KSETRAJNA": KSETRAJNA,
    "HALF_SIZE": HALF_SIZE,
    "LILA": LILA,
    "KSHETRA": KSHETRA,
    "NAVA": NAVA,
    "SHARANAGATI": SHARANAGATI,
    "AKSARA": AKSARA_COUNT,
    # Secondary
    "MAHAJANA": MAHAJANA_COUNT,
    "MALA": MALA,
    "JIVA_CYCLE": JIVA_CYCLE,
    "GITA": GITA_CHAPTERS,
    "QUALITIES": QUALITIES,
    "JIVA_Q": JIVA_QUALITIES,
    # Cosmic
    "NAKSHATRAS": NAKSHATRAS,
    # Position Sums
    "HARE_POS": POSITION_SUM_HARE,
    "KRISHNA_POS": POSITION_SUM_KRISHNA,
    "RAMA_POS": POSITION_SUM_RAMA,
    "TOTAL_POS": POSITION_SUM_TOTAL,
    # 7-10
    "SEVEN": SEVEN,
    "TEN": TEN,
    # Parampara
    "PARAMPARA": PARAMPARA,
    # Derived physics (for chaining)
    "MAHA_Q": MAHA_QUANTUM,
    "MAHA_MU": MAHA_MU,
}


# =============================================================================
# KEY MODULI FOR ANALYSIS
# =============================================================================

KEY_MODULI: Dict[str, int] = {
    "KRISHNA_POS": POSITION_SUM_KRISHNA,  # 17
    "PARAMPARA": PARAMPARA,  # 37
    "NAKSHATRAS": NAKSHATRAS,  # 27
    "MALA": MALA,  # 108
}


# =============================================================================
# FORMULA TYPES
# =============================================================================


class OpType(Enum):
    """Operation types for formula generation."""

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    POW = auto()
    TRIANGULAR = auto()


@dataclass
class Formula:
    """A formula combining Seed constants."""

    expression: str
    value: int
    depth: int
    components: List[str]

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        return self.value == other.value


@dataclass
class PhysicsMatch:
    """A match between a formula and a physics constant."""

    formula: Formula
    target_name: str
    target_value: float
    error_percent: float
    mod_signature: Dict[str, int]


# =============================================================================
# UNIVERSAL GENERATOR
# =============================================================================


def triangular(n: int) -> int:
    """Compute triangular number T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


def generate_formulas(max_depth: int = 2) -> List[Formula]:
    """
    Generate all formulas up to given depth.

    Depth 0: Single constants
    Depth 1: Binary operations (A op B)
    Depth 2: Ternary operations (A op B op C)
    """
    formulas: List[Formula] = []
    seen_values: Set[int] = set()

    # Depth 0: Single constants
    for name, value in SEED_POOL.items():
        if value not in seen_values and value > 0:
            formulas.append(Formula(name, value, 0, [name]))
            seen_values.add(value)

    # Depth 0: Triangular numbers of small constants
    for name, value in SEED_POOL.items():
        if value <= 20:
            t_val = triangular(value)
            expr = f"T({name})"
            if t_val not in seen_values:
                formulas.append(Formula(expr, t_val, 0, [name]))
                seen_values.add(t_val)

    if max_depth < 1:
        return formulas

    # Depth 1: Binary operations
    names = list(SEED_POOL.keys())
    for i, n1 in enumerate(names):
        v1 = SEED_POOL[n1]
        for n2 in names[i:]:  # Avoid duplicates for commutative ops
            v2 = SEED_POOL[n2]

            # Addition
            val = v1 + v2
            if val not in seen_values:
                formulas.append(Formula(f"{n1} + {n2}", val, 1, [n1, n2]))
                seen_values.add(val)

            # Multiplication
            val = v1 * v2
            if val not in seen_values and val < 100000:
                formulas.append(Formula(f"{n1} × {n2}", val, 1, [n1, n2]))
                seen_values.add(val)

            # Subtraction (both directions)
            if v1 > v2:
                val = v1 - v2
                if val not in seen_values and val > 0:
                    formulas.append(Formula(f"{n1} - {n2}", val, 1, [n1, n2]))
                    seen_values.add(val)
            elif v2 > v1:
                val = v2 - v1
                if val not in seen_values and val > 0:
                    formulas.append(Formula(f"{n2} - {n1}", val, 1, [n1, n2]))
                    seen_values.add(val)

            # Division (if clean)
            if v2 > 0 and v1 % v2 == 0:
                val = v1 // v2
                if val not in seen_values and val > 0:
                    formulas.append(Formula(f"{n1} / {n2}", val, 1, [n1, n2]))
                    seen_values.add(val)
            if v1 > 0 and v2 % v1 == 0:
                val = v2 // v1
                if val not in seen_values and val > 0:
                    formulas.append(Formula(f"{n2} / {n1}", val, 1, [n1, n2]))
                    seen_values.add(val)

            # Power (small exponents only)
            if v2 <= 4 and v1 > 1:
                val = v1**v2
                if val not in seen_values and val < 100000:
                    formulas.append(Formula(f"{n1}^{n2}", val, 1, [n1, n2]))
                    seen_values.add(val)

    if max_depth < 2:
        return formulas

    # Depth 2: Add/subtract to existing formulas
    depth1_formulas = [f for f in formulas if f.depth == 1]
    for f in depth1_formulas:
        for name, value in SEED_POOL.items():
            if name in f.components:
                continue

            # Add
            val = f.value + value
            if val not in seen_values and val < 100000:
                expr = f"({f.expression}) + {name}"
                formulas.append(Formula(expr, val, 2, f.components + [name]))
                seen_values.add(val)

            # Subtract
            if f.value > value:
                val = f.value - value
                if val not in seen_values and val > 0:
                    expr = f"({f.expression}) - {name}"
                    formulas.append(Formula(expr, val, 2, f.components + [name]))
                    seen_values.add(val)

            # Multiply
            val = f.value * value
            if val not in seen_values and val < 100000:
                expr = f"({f.expression}) × {name}"
                formulas.append(Formula(expr, val, 2, f.components + [name]))
                seen_values.add(val)

    return formulas


def find_physics_matches(formulas: List[Formula], max_error: float = 0.5) -> List[PhysicsMatch]:
    """Find formulas that match known physics constants."""
    matches: List[PhysicsMatch] = []

    for target_name, target_value in PHYSICS_TARGETS.items():
        for formula in formulas:
            if target_value == 0:
                continue

            error = abs(formula.value - target_value) / target_value * 100

            if error <= max_error:
                # Compute mod signature
                mod_sig = {}
                for mod_name, mod_val in KEY_MODULI.items():
                    mod_sig[mod_name] = formula.value % mod_val

                matches.append(
                    PhysicsMatch(
                        formula=formula,
                        target_name=target_name,
                        target_value=target_value,
                        error_percent=error,
                        mod_signature=mod_sig,
                    )
                )

    # Sort by error
    matches.sort(key=lambda m: m.error_percent)
    return matches


def analyze_mod_patterns(formulas: List[Formula]) -> Dict[str, Dict[int, List[Formula]]]:
    """Analyze modulo patterns across all formulas."""
    patterns: Dict[str, Dict[int, List[Formula]]] = {}

    for mod_name, mod_val in KEY_MODULI.items():
        patterns[mod_name] = {}
        for formula in formulas:
            remainder = formula.value % mod_val
            if remainder not in patterns[mod_name]:
                patterns[mod_name][remainder] = []
            patterns[mod_name][remainder].append(formula)

    return patterns


def generate_report(max_depth: int = 2, max_error: float = 0.5) -> str:
    """Generate a complete analysis report."""
    lines = [
        "═" * 70,
        "UNIVERSAL GENERATOR REPORT",
        "The Vishvarupa of Mahamantra Constants",
        "═" * 70,
        "",
    ]

    # Generate formulas
    formulas = generate_formulas(max_depth)
    lines.append(f"Total formulas generated (depth ≤ {max_depth}): {len(formulas)}")
    lines.append("")

    # Find physics matches
    matches = find_physics_matches(formulas, max_error)
    lines.append(f"Physics matches found (error ≤ {max_error}%): {len(matches)}")
    lines.append("")

    lines.append("PHYSICS CONSTANT MATCHES:")
    lines.append("-" * 70)
    lines.append(f"{'Target':<18} {'Value':>8} {'Formula':<25} {'Error':>8}")
    lines.append("-" * 70)

    for match in matches:
        lines.append(
            f"{match.target_name:<18} {match.formula.value:>8} "
            f"{match.formula.expression:<25} {match.error_percent:>7.4f}%"
        )

    # Mod signature analysis
    lines.append("")
    lines.append("MOD SIGNATURES OF MATCHES:")
    lines.append("-" * 70)
    for match in matches:
        sig_str = ", ".join(f"{k}={v}" for k, v in match.mod_signature.items())
        lines.append(f"{match.target_name:<18}: {sig_str}")

    lines.append("")
    lines.append("═" * 70)

    return "\n".join(lines)


# =============================================================================
# MODULE EXECUTION
# =============================================================================

if __name__ == "__main__":
    print(generate_report(max_depth=2, max_error=0.5))

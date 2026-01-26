"""
GAP ANALYSIS - Antaryami (Inner Witness)
========================================

"antaryāmī sarva-bhūtānāṁ guhāyāṁ niviṣṭaḥ"
"The Supersoul dwelling in the cavity of the heart of all beings."

This module identifies GAPS in the system:
- Research not connected to production
- Production not using research
- Missing Parampara connections
- Orphan modules (no imports/exports)
- Test coverage gaps

ARCHITECTURE:
    Gap Analysis uses the GUT (Grand Unified Theory) principle:
    - EVERYTHING should connect back to _seed.py
    - EVERYTHING should have Parampara verification
    - EVERYTHING should be reachable from kernel_impl.py

CAPABILITIES:
    1. analyze_research_production_gap() - What research is NOT in production?
    2. analyze_production_research_gap() - What production is NOT using research?
    3. find_orphan_modules() - Files not imported by anything
    4. find_missing_tests() - Code without test coverage
    5. analyze_seed_coverage() - What uses _seed.py constants?

SSOT: All analysis derives from _seed.py constants.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 13
__genesis__ = "0x6e44c2a5"  # GenesisByte: parampara % 37 == 0

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Final, List, Optional, Set, Tuple

# SSOT: All constants from _seed.py
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    MAHA_QUANTUM,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHAJANA_COUNT as MAHAJANAS,
)

# Use project introspection
from vibe_core.mahamantra.research.project_introspection import (
    FileInfo,
    extract_imports,
    scan_codebase,
)

logger = logging.getLogger("GAP_ANALYSIS")

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Key research modules that SHOULD be in production
RESEARCH_CORE_MODULES: Final[List[str]] = [
    "lotus_tree",
    "ip_routing",
    "routing_holographic",
    "kishora_architecture",
    "acintya_mathematics",
    "siksastakam_engineering",
]

# Key production files that SHOULD use research
PRODUCTION_CORE_MODULES: Final[List[str]] = [
    "kernel_impl",
    "chat_indriya",
    "chat_service",
    "unified_cli",
    "naga_cli",
    "sankirtan",
]

# Seed constants that SHOULD be used everywhere
SEED_CONSTANTS: Final[List[str]] = [
    "WORDS",
    "QUARTERS",
    "PARAMPARA",
    "PANCHA",
    "HALVES",
    "MAHA_QUANTUM",
]

# Kishora threshold (98.75% = 79/80)
KISHORA_THRESHOLD: Final[float] = 79 / 80

# Verification
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class GapType:
    """Types of gaps found in analysis."""

    RESEARCH_NOT_IN_PRODUCTION = "research_not_in_production"
    PRODUCTION_NOT_USING_RESEARCH = "production_not_using_research"
    ORPHAN_MODULE = "orphan_module"
    NO_TEST = "no_test"
    NO_SEED_IMPORT = "no_seed_import"
    BROKEN_PARAMPARA = "broken_parampara"
    MISSING_MAHAJANA = "missing_mahajana"


@dataclass
class GapRecord:
    """Record of a specific gap found."""

    gap_type: str
    source_file: Path
    target_file: Optional[Path] = None
    description: str = ""
    severity: str = "info"  # info, warning, critical
    recommendation: str = ""

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.gap_type}: {self.source_file.name} - {self.description}"


@dataclass
class GapReport:
    """Complete gap analysis report."""

    timestamp: str = ""
    gaps: List[GapRecord] = field(default_factory=list)

    # Summary stats
    total_research_files: int = 0
    research_in_production: int = 0
    total_production_files: int = 0
    production_using_research: int = 0

    # Coverage ratios
    research_coverage: float = 0.0
    production_coverage: float = 0.0
    seed_coverage: float = 0.0
    parampara_coverage: float = 0.0

    @property
    def is_kishora(self) -> bool:
        """Are we in Kishora zone (>= 98.75%)?"""
        avg_coverage = (
            self.research_coverage + self.production_coverage + self.seed_coverage + self.parampara_coverage
        ) / 4
        return avg_coverage >= KISHORA_THRESHOLD

    @property
    def critical_count(self) -> int:
        return sum(1 for g in self.gaps if g.severity == "critical")

    @property
    def warning_count(self) -> int:
        return sum(1 for g in self.gaps if g.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for g in self.gaps if g.severity == "info")


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================


def find_files_importing(module_name: str, files: List[FileInfo]) -> List[FileInfo]:
    """Find all files that import a given module."""
    result = []
    for f in files:
        for imp in f.imports:
            if module_name in imp:
                result.append(f)
                break
    return result


def find_research_files(files: List[FileInfo]) -> List[FileInfo]:
    """Find all research module files."""
    return [f for f in files if "/research/" in str(f.path) and not f.has_tests]


def find_production_files(files: List[FileInfo]) -> List[FileInfo]:
    """Find all production (non-research, non-test) files."""
    return [f for f in files if "/research/" not in str(f.path) and not f.has_tests and f.is_significant]


def analyze_research_production_gap(files: List[FileInfo]) -> Tuple[List[GapRecord], Dict[str, int]]:
    """
    Find research modules NOT being used in production.

    Returns:
        Tuple of (list of gaps, dict of module -> import count)
    """
    gaps = []
    import_counts: Dict[str, int] = {}

    research_files = find_research_files(files)
    production_files = find_production_files(files)

    for rf in research_files:
        module_name = rf.path.stem  # e.g., "lotus_tree"

        # Count imports in production
        importers = find_files_importing(module_name, production_files)
        import_counts[module_name] = len(importers)

        if len(importers) == 0 and module_name in RESEARCH_CORE_MODULES:
            gaps.append(
                GapRecord(
                    gap_type=GapType.RESEARCH_NOT_IN_PRODUCTION,
                    source_file=rf.path,
                    description=f"Core research module '{module_name}' not imported by any production code",
                    severity="warning",
                    recommendation=f"Import from vibe_core.mahamantra.research.{module_name}",
                )
            )
        elif len(importers) == 0:
            gaps.append(
                GapRecord(
                    gap_type=GapType.RESEARCH_NOT_IN_PRODUCTION,
                    source_file=rf.path,
                    description=f"Research module '{module_name}' not imported anywhere",
                    severity="info",
                    recommendation="Consider integrating or documenting why standalone",
                )
            )

    return gaps, import_counts


def analyze_production_research_gap(files: List[FileInfo]) -> Tuple[List[GapRecord], Dict[str, bool]]:
    """
    Find production modules NOT using any research.

    Returns:
        Tuple of (list of gaps, dict of module -> uses_research)
    """
    gaps = []
    uses_research: Dict[str, bool] = {}

    production_files = find_production_files(files)

    for pf in production_files:
        module_name = pf.path.stem

        # Check if imports any research
        imports_research = any("research" in imp for imp in pf.imports)
        uses_research[module_name] = imports_research

        if not imports_research and module_name in PRODUCTION_CORE_MODULES:
            gaps.append(
                GapRecord(
                    gap_type=GapType.PRODUCTION_NOT_USING_RESEARCH,
                    source_file=pf.path,
                    description=f"Core production module '{module_name}' not using any research",
                    severity="warning",
                    recommendation="Import relevant constants from research modules",
                )
            )

    return gaps, uses_research


def analyze_seed_coverage(files: List[FileInfo]) -> Tuple[List[GapRecord], float]:
    """
    Find files that SHOULD import from _seed.py but don't.

    Returns:
        Tuple of (list of gaps, coverage ratio)
    """
    gaps = []
    should_import = 0
    does_import = 0

    for f in files:
        if not f.is_significant or f.has_tests:
            continue

        # Check if it's in mahamantra (should use seed)
        if "/mahamantra/" in str(f.path):
            should_import += 1

            imports_seed = any("_seed" in imp or "seed" in imp for imp in f.imports)
            if imports_seed:
                does_import += 1
            else:
                gaps.append(
                    GapRecord(
                        gap_type=GapType.NO_SEED_IMPORT,
                        source_file=f.path,
                        description="Mahamantra file not importing from _seed.py",
                        severity="info",
                        recommendation="Import constants from vibe_core.mahamantra.protocols._seed",
                    )
                )

    coverage = does_import / max(should_import, 1)
    return gaps, coverage


def find_orphan_modules(files: List[FileInfo]) -> List[GapRecord]:
    """
    Find modules not imported by anything else.

    These are potential dead code or standalone utilities.
    """
    gaps = []

    # Build set of all imported module names
    all_imports: Set[str] = set()
    for f in files:
        for imp in f.imports:
            # Extract module name from import path
            parts = imp.split(".")
            all_imports.update(parts)

    for f in files:
        if f.has_tests or not f.is_significant:
            continue

        module_name = f.path.stem

        # Check if this module is imported anywhere
        if module_name not in all_imports:
            # Exclude entry points and __init__ files
            if module_name not in ("__init__", "__main__", "main", "cli", "app"):
                gaps.append(
                    GapRecord(
                        gap_type=GapType.ORPHAN_MODULE,
                        source_file=f.path,
                        description=f"Module '{module_name}' not imported by any other file",
                        severity="info",
                        recommendation="Verify if this is intentional (entry point) or dead code",
                    )
                )

    return gaps


def find_missing_tests(files: List[FileInfo]) -> List[GapRecord]:
    """
    Find production modules without corresponding test files.
    """
    gaps = []

    # Get all test file stems
    test_stems = {f.path.stem.replace("test_", "") for f in files if f.has_tests}

    for f in files:
        if f.has_tests or not f.is_significant:
            continue

        module_name = f.path.stem

        if module_name not in test_stems:
            # Check if it's in a tested module's __init__
            if module_name not in ("__init__", "__main__"):
                gaps.append(
                    GapRecord(
                        gap_type=GapType.NO_TEST,
                        source_file=f.path,
                        description=f"No test file for '{module_name}'",
                        severity="info",
                        recommendation=f"Create tests/*/test_{module_name}.py",
                    )
                )

    return gaps


# =============================================================================
# MAIN ANALYSIS
# =============================================================================


def run_full_analysis(root: Path = None) -> GapReport:
    """
    Run complete gap analysis on the codebase.

    Returns:
        GapReport with all findings.
    """
    from datetime import datetime

    if root is None:
        root = Path.cwd()

    files, metrics = scan_codebase(root)

    report = GapReport(timestamp=datetime.now().isoformat())

    # Research analysis
    research_files = find_research_files(files)
    production_files = find_production_files(files)
    report.total_research_files = len(research_files)
    report.total_production_files = len(production_files)

    # 1. Research -> Production gaps
    research_gaps, import_counts = analyze_research_production_gap(files)
    report.gaps.extend(research_gaps)
    report.research_in_production = sum(1 for v in import_counts.values() if v > 0)
    report.research_coverage = report.research_in_production / max(report.total_research_files, 1)

    # 2. Production -> Research gaps
    production_gaps, uses_research = analyze_production_research_gap(files)
    report.gaps.extend(production_gaps)
    report.production_using_research = sum(1 for v in uses_research.values() if v)
    report.production_coverage = report.production_using_research / max(report.total_production_files, 1)

    # 3. Seed coverage
    seed_gaps, seed_cov = analyze_seed_coverage(files)
    report.gaps.extend(seed_gaps)
    report.seed_coverage = seed_cov

    # 4. Parampara coverage (from metrics)
    report.parampara_coverage = metrics.coverage_ratio

    # 5. Orphan modules
    report.gaps.extend(find_orphan_modules(files))

    # 6. Missing tests
    report.gaps.extend(find_missing_tests(files))

    return report


def generate_gap_report() -> str:
    """
    Generate human-readable gap report.
    """
    report = run_full_analysis()

    lines = [
        "=" * 64,
        "GAP ANALYSIS REPORT (Antaryami)",
        f"Generated: {report.timestamp}",
        "=" * 64,
        "",
        "COVERAGE SUMMARY:",
        f"  Research in Production: {report.research_coverage:.1%} ({report.research_in_production}/{report.total_research_files})",
        f"  Production using Research: {report.production_coverage:.1%}",
        f"  Seed.py Coverage: {report.seed_coverage:.1%}",
        f"  Parampara Coverage: {report.parampara_coverage:.1%}",
        f"  Kishora Zone (98.75%): {'YES' if report.is_kishora else 'NO'}",
        "",
        f"GAPS FOUND: {len(report.gaps)}",
        f"  Critical: {report.critical_count}",
        f"  Warning: {report.warning_count}",
        f"  Info: {report.info_count}",
        "",
    ]

    # Group gaps by type
    by_type: Dict[str, List[GapRecord]] = {}
    for g in report.gaps:
        if g.gap_type not in by_type:
            by_type[g.gap_type] = []
        by_type[g.gap_type].append(g)

    for gap_type, gaps in sorted(by_type.items()):
        lines.append(f"\n{gap_type.upper()} ({len(gaps)}):")
        for g in gaps[:10]:  # Limit to 10 per type
            lines.append(f"  - {g.source_file.name}: {g.description}")
        if len(gaps) > 10:
            lines.append(f"  ... and {len(gaps) - 10} more")

    lines.extend(
        [
            "",
            "=" * 64,
            "GUT PRINCIPLE: All paths lead to _seed.py",
            f"PARAMPARA = {PARAMPARA}, MAHA_QUANTUM = {MAHA_QUANTUM}",
            "=" * 64,
        ]
    )

    return "\n".join(lines)


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Run gap analysis from command line."""
    print(generate_gap_report())


if __name__ == "__main__":
    main()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "RESEARCH_CORE_MODULES",
    "PRODUCTION_CORE_MODULES",
    "SEED_CONSTANTS",
    "KISHORA_THRESHOLD",
    # Data structures
    "GapType",
    "GapRecord",
    "GapReport",
    # Analysis functions
    "find_files_importing",
    "find_research_files",
    "find_production_files",
    "analyze_research_production_gap",
    "analyze_production_research_gap",
    "analyze_seed_coverage",
    "find_orphan_modules",
    "find_missing_tests",
    "run_full_analysis",
    "generate_gap_report",
    "main",
]

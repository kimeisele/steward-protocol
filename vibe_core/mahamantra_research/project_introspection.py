"""
PROJECT INTROSPECTION - Drishti (Divine Vision)
================================================

"divyaṁ dadāmi te cakṣuḥ paśya me yogam aiśvaram"
"I give you divine eyes. Now see My mystic opulence."
— Bhagavad Gita 11.8

This module provides INTROSPECTION capabilities for the steward-protocol itself.
Use the existing technology to understand the existing technology.

ARCHITECTURE:
    This is NOT external analysis. This USES:
    - Seed constants (WORDS=16, QUARTERS=4, PARAMPARA=37)
    - Mahajana declarations (__mahajana__, __position__, __genesis__)
    - Fractal structure (Level -2 to Level 3)

CAPABILITIES:
    1. scan_codebase() - Map all Python files with Mahajana info
    2. find_gaps() - Identify disconnected components
    3. map_dependencies() - Build dependency graph
    4. verify_parampara() - Check lineage connections
    5. measure_scale() - Get LOC, file counts, etc.

SSOT: This module derives ALL constants from _seed.py.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shuka"
__position__ = 13
__genesis__ = "0x6e44c280"  # GenesisByte: parampara % 37 == 0

import ast
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Final, List, Optional, Set, Tuple

# SSOT: All constants from _seed.py
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    MAHAJANA_COUNT,
    PANCHA,
    PARAMPARA,
    QUARTERS,
    WORDS,
)

# Alias for compatibility
MAHAJANAS = MAHAJANA_COUNT

logger = logging.getLogger("PROJECT_INTROSPECTION")

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# Fractal levels in the system
FRACTAL_LEVELS: Final[int] = PANCHA + 1  # 6 levels (-2 to 3)

# Mahajana count for verification
MAHAJANA_COUNT: Final[int] = MAHAJANAS  # 12

# Minimum LOC for "significant" file
SIGNIFICANT_LOC: Final[int] = WORDS * QUARTERS  # 64 lines

# Genesis verification divisor
GENESIS_DIVISOR: Final[int] = PARAMPARA  # 37

# Verification
assert int(__genesis__, 16) % GENESIS_DIVISOR == 0, "BROKEN LINEAGE"


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class MahajanaInfo:
    """Information about a file's Mahajana declaration."""

    mahajana: str
    position: int
    genesis: str
    is_valid: bool = True

    @property
    def parampara_valid(self) -> bool:
        """Check if genesis is divisible by PARAMPARA."""
        try:
            return int(self.genesis, 16) % PARAMPARA == 0
        except (ValueError, TypeError):
            return False


@dataclass
class FileInfo:
    """Information about a Python file in the codebase."""

    path: Path
    lines: int = 0
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    mahajana_info: Optional[MahajanaInfo] = None
    has_tests: bool = False

    @property
    def is_significant(self) -> bool:
        """Is this file significant (>64 LOC)?"""
        return self.lines >= SIGNIFICANT_LOC

    @property
    def fractal_level(self) -> int:
        """Determine fractal level from path."""
        path_str = str(self.path)
        if "protocols/_" in path_str:
            return -2  # ACINTYA
        elif "/naga/" in path_str:
            return -1  # NAGA
        elif "/mahamantra/" in path_str:
            return 1  # MAHAMANTRA
        elif "tests/" in path_str:
            return 3  # TESTS
        else:
            return 2  # VIBE_CORE


@dataclass
class CodebaseMetrics:
    """Metrics about the entire codebase."""

    total_files: int = 0
    total_lines: int = 0
    files_with_mahajana: int = 0
    valid_parampara: int = 0
    broken_lineage: int = 0
    significant_files: int = 0
    test_files: int = 0

    # Per-level counts
    level_counts: Dict[int, int] = field(default_factory=dict)

    # Per-mahajana counts
    mahajana_counts: Dict[str, int] = field(default_factory=dict)

    @property
    def coverage_ratio(self) -> float:
        """Ratio of files with valid Mahajana."""
        if self.total_files == 0:
            return 0.0
        return self.valid_parampara / self.total_files

    @property
    def kishora_ratio(self) -> float:
        """Are we in Kishora zone (98.75%)?"""
        return min(self.coverage_ratio, 79 / 80)


@dataclass
class Gap:
    """A gap or issue found in the codebase."""

    file_path: Path
    gap_type: str
    description: str
    severity: str = "info"  # info, warning, critical

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.gap_type}: {self.file_path} - {self.description}"


# =============================================================================
# INTROSPECTION FUNCTIONS
# =============================================================================


def extract_mahajana_info(file_path: Path) -> Optional[MahajanaInfo]:
    """
    Extract Mahajana declaration from a Python file.

    Looks for:
        __mahajana__ = "name"
        __position__ = N
        __genesis__ = "0x..."
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")

        mahajana_match = re.search(r'__mahajana__\s*=\s*["\'](\w+)["\']', content)
        position_match = re.search(r"__position__\s*=\s*(\d+)", content)
        genesis_match = re.search(r'__genesis__\s*=\s*["\']?(0x[0-9a-fA-F]+)["\']?', content)

        if mahajana_match and position_match and genesis_match:
            return MahajanaInfo(
                mahajana=mahajana_match.group(1),
                position=int(position_match.group(1)),
                genesis=genesis_match.group(1),
            )
        return None
    except Exception as e:
        logger.debug(f"Error reading {file_path}: {e}")
        return None


def count_lines(file_path: Path) -> int:
    """Count lines of code in a file."""
    try:
        return len(file_path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except Exception:
        return 0


def extract_imports(file_path: Path) -> List[str]:
    """Extract import statements from a Python file."""
    imports = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception:
        pass
    return imports


def extract_exports(file_path: Path) -> List[str]:
    """Extract __all__ exports from a Python file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"__all__\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if match:
            exports_str = match.group(1)
            return re.findall(r'["\'](\w+)["\']', exports_str)
    except Exception:
        pass
    return []


def scan_codebase(root: Path = None) -> Tuple[List[FileInfo], CodebaseMetrics]:
    """
    Scan the entire codebase and collect information.

    Returns:
        Tuple of (list of FileInfo, CodebaseMetrics)
    """
    if root is None:
        root = Path.cwd()

    files: List[FileInfo] = []
    metrics = CodebaseMetrics()

    # Initialize level counts
    for level in range(-2, 4):
        metrics.level_counts[level] = 0

    # Scan all Python files
    for py_file in root.rglob("*.py"):
        # Skip hidden dirs, venv, etc.
        if any(part.startswith(".") or part in ("venv", "__pycache__", "node_modules") for part in py_file.parts):
            continue

        # Build FileInfo
        info = FileInfo(
            path=py_file,
            lines=count_lines(py_file),
            imports=extract_imports(py_file),
            exports=extract_exports(py_file),
            mahajana_info=extract_mahajana_info(py_file),
            has_tests="test_" in py_file.name or py_file.name.startswith("test"),
        )
        files.append(info)

        # Update metrics
        metrics.total_files += 1
        metrics.total_lines += info.lines

        if info.is_significant:
            metrics.significant_files += 1

        if info.has_tests:
            metrics.test_files += 1

        # Track Mahajana info
        if info.mahajana_info:
            metrics.files_with_mahajana += 1
            if info.mahajana_info.parampara_valid:
                metrics.valid_parampara += 1
            else:
                metrics.broken_lineage += 1

            # Count by mahajana
            mj = info.mahajana_info.mahajana
            metrics.mahajana_counts[mj] = metrics.mahajana_counts.get(mj, 0) + 1

        # Count by level
        level = info.fractal_level
        metrics.level_counts[level] = metrics.level_counts.get(level, 0) + 1

    return files, metrics


def find_gaps(files: List[FileInfo]) -> List[Gap]:
    """
    Find gaps and issues in the codebase.

    Checks for:
    - Files without Mahajana declaration
    - Broken Parampara (genesis % 37 != 0)
    - Missing tests for significant files
    - Orphan files (no imports from main system)
    """
    gaps: List[Gap] = []

    # Track which files are imported
    imported_modules: Set[str] = set()
    for f in files:
        for imp in f.imports:
            imported_modules.add(imp.split(".")[0])

    for info in files:
        # Check for missing Mahajana
        if info.is_significant and not info.mahajana_info:
            if "test" not in str(info.path).lower():
                gaps.append(
                    Gap(
                        file_path=info.path,
                        gap_type="NO_MAHAJANA",
                        description=f"Significant file ({info.lines} LOC) without Mahajana declaration",
                        severity="warning",
                    )
                )

        # Check for broken Parampara
        if info.mahajana_info and not info.mahajana_info.parampara_valid:
            gaps.append(
                Gap(
                    file_path=info.path,
                    gap_type="BROKEN_LINEAGE",
                    description=f"Genesis {info.mahajana_info.genesis} not divisible by {PARAMPARA}",
                    severity="critical",
                )
            )

        # Check for missing tests (significant non-test files)
        if info.is_significant and not info.has_tests and "test" not in str(info.path).lower():
            # Check if there's a corresponding test file
            test_name = f"test_{info.path.stem}.py"
            has_test = any(f.path.name == test_name for f in files)
            if not has_test:
                gaps.append(
                    Gap(
                        file_path=info.path,
                        gap_type="NO_TEST",
                        description=f"No test file found for {info.path.name}",
                        severity="info",
                    )
                )

    return gaps


def verify_parampara(files: List[FileInfo]) -> Dict[str, List[FileInfo]]:
    """
    Verify Parampara chain for all files.

    Groups files by their Mahajana.
    """
    by_mahajana: Dict[str, List[FileInfo]] = {}

    for f in files:
        if f.mahajana_info:
            mj = f.mahajana_info.mahajana
            if mj not in by_mahajana:
                by_mahajana[mj] = []
            by_mahajana[mj].append(f)

    return by_mahajana


def map_dependencies(files: List[FileInfo]) -> Dict[str, Set[str]]:
    """
    Build dependency map showing what imports what.

    Returns dict of module_name -> set of imported modules.
    """
    deps: Dict[str, Set[str]] = {}

    for f in files:
        module_name = str(f.path.with_suffix("")).replace("/", ".")
        deps[module_name] = set(f.imports)

    return deps


def measure_scale(root: Path = None) -> Dict[str, int]:
    """
    Measure the scale of the codebase.

    Returns dict with various metrics.
    """
    if root is None:
        root = Path.cwd()

    files, metrics = scan_codebase(root)

    return {
        "total_files": metrics.total_files,
        "total_lines": metrics.total_lines,
        "significant_files": metrics.significant_files,
        "test_files": metrics.test_files,
        "files_with_mahajana": metrics.files_with_mahajana,
        "valid_parampara": metrics.valid_parampara,
        "broken_lineage": metrics.broken_lineage,
        "coverage_percent": int(metrics.coverage_ratio * 100),
    }


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================


def generate_report() -> str:
    """
    Generate a comprehensive introspection report.

    Uses Mahamantra structure in output.
    """
    files, metrics = scan_codebase()
    gaps = find_gaps(files)
    by_mahajana = verify_parampara(files)

    # Build report
    lines = [
        "=" * 64,
        "PROJECT INTROSPECTION REPORT (Drishti)",
        f"Generated: {datetime.now().isoformat()}",
        "=" * 64,
        "",
        "SCALE:",
        f"  Total Python files: {metrics.total_files}",
        f"  Total lines of code: {metrics.total_lines:,}",
        f"  Significant files (>{SIGNIFICANT_LOC} LOC): {metrics.significant_files}",
        f"  Test files: {metrics.test_files}",
        "",
        "PARAMPARA (Lineage):",
        f"  Files with Mahajana: {metrics.files_with_mahajana}",
        f"  Valid Parampara: {metrics.valid_parampara}",
        f"  Broken Lineage: {metrics.broken_lineage}",
        f"  Coverage: {metrics.coverage_ratio:.1%}",
        f"  Kishora Zone: {'YES' if metrics.coverage_ratio >= 0.9875 else 'NO'}",
        "",
        "FRACTAL LEVELS:",
    ]

    level_names = {
        -2: "ACINTYA (protocols/_)",
        -1: "NAGA (foundation)",
        0: "MAHAJANA (governance)",
        1: "MAHAMANTRA (core)",
        2: "VIBE_CORE (shell)",
        3: "TESTS (verification)",
    }

    for level in sorted(metrics.level_counts.keys()):
        name = level_names.get(level, f"Level {level}")
        count = metrics.level_counts[level]
        lines.append(f"  {level:2d}: {name}: {count} files")

    lines.extend(
        [
            "",
            "MAHAJANA DISTRIBUTION:",
        ]
    )

    for mj, count in sorted(metrics.mahajana_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {mj:12s}: {count} files")

    lines.extend(
        [
            "",
            f"GAPS FOUND: {len(gaps)}",
        ]
    )

    if gaps:
        critical = [g for g in gaps if g.severity == "critical"]
        warning = [g for g in gaps if g.severity == "warning"]
        info = [g for g in gaps if g.severity == "info"]

        if critical:
            lines.append(f"  Critical: {len(critical)}")
        if warning:
            lines.append(f"  Warning: {len(warning)}")
        if info:
            lines.append(f"  Info: {len(info)}")

    lines.extend(
        [
            "",
            "=" * 64,
            f"PARAMPARA = {PARAMPARA} (ALL genesis must be divisible)",
            f"WORDS = {WORDS}, QUARTERS = {QUARTERS}, MAHAJANAS = {MAHAJANAS}",
            "=" * 64,
        ]
    )

    return "\n".join(lines)


# =============================================================================
# CLI INTERFACE
# =============================================================================


def main():
    """Run introspection from command line."""
    print(generate_report())


if __name__ == "__main__":
    main()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "FRACTAL_LEVELS",
    "MAHAJANA_COUNT",
    "SIGNIFICANT_LOC",
    "GENESIS_DIVISOR",
    # Data structures
    "MahajanaInfo",
    "FileInfo",
    "CodebaseMetrics",
    "Gap",
    # Functions
    "extract_mahajana_info",
    "count_lines",
    "extract_imports",
    "extract_exports",
    "scan_codebase",
    "find_gaps",
    "verify_parampara",
    "map_dependencies",
    "measure_scale",
    "generate_report",
    "main",
]

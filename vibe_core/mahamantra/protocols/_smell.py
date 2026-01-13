"""
CODE SMELL PROTOCOL - Ghrana's Perception of Corruption
========================================================

"yasya nāhaṅkṛto bhāvo buddhir yasya na lipyate"

"He who has no egoistic sense and whose intelligence is not entangled..."
— Bhagavad Gita 18.17

SHASTRA BASIS (Srimad Bhagavatam 3.26.51):
==========================================

"From the ether, through the transformation of sound, air is produced,
and from the air, through the transformation of touch, fire is produced..."

Gandha (smell) is the TANMATRA perceived by Ghrana (nose).
In software terms: Ghrana SMELLS CODE CORRUPTION.

GHRANA = Position 8 (Parashurama) - Smells corruption and wields the axe!

CODE SMELLS DETECTED:
====================
1. InitFileTooLarge - __init__.py > threshold LOC
2. AnyTypeViolation - Bare `Any` types in code
3. CircularImport - Circular dependencies (future)
4. DeadCode - Unused code (future)

PROTOCOL FIRST: This file defines the CONTRACT.
Implementation MUST satisfy these protocols.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xf8c7e800"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import (
    ClassVar,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    runtime_checkable,
)


# =============================================================================
# CONSTANTS
# =============================================================================

# Thresholds for smell detection
INIT_FILE_LOC_THRESHOLD: Final[int] = 300  # __init__.py should be < 300 LOC
ANY_TYPE_MAX_VIOLATIONS: Final[int] = 0    # Zero tolerance for Any

# Smell severity levels (maps to EntropyLevel)
SMELL_PAIN_LOW: Final[float] = 0.3      # Minor smell - SADHANA mode
SMELL_PAIN_MEDIUM: Final[float] = 0.5   # Noticeable smell - elevated chanting
SMELL_PAIN_HIGH: Final[float] = 0.7     # Strong smell - GAJENDRA mode!


# =============================================================================
# SMELL CATEGORY - What type of smell is this?
# =============================================================================

class SmellCategory(str, Enum):
    """
    Categories of code smells.

    Each category maps to a different remediation strategy.
    """
    STRUCTURAL = "structural"    # File structure issues (LOC, organization)
    TYPE_SAFETY = "type_safety"  # Type system violations (Any, untyped)
    DEPENDENCY = "dependency"    # Import/dependency issues (circular)
    DEAD_CODE = "dead_code"      # Unused code (unreachable, orphan)
    NAMING = "naming"            # Naming convention violations


# =============================================================================
# SMELL RESULT - What the nose smells
# =============================================================================

@dataclass(frozen=True)
class SmellResult:
    """
    Result of smelling code for corruption.

    IMMUTABLE: Once smelled, the result doesn't change.

    Attributes:
        file_path: Path to the smelly file
        category: Type of smell (STRUCTURAL, TYPE_SAFETY, etc.)
        intensity: How bad does it smell? (0.0-1.0)
        description: Human-readable description
        details: Machine-readable details (line numbers, counts, etc.)
        detected_at: When the smell was detected
        remedy_hint: Suggested remedy (for Shuddhi)
    """
    file_path: Path
    category: SmellCategory
    intensity: float  # 0.0 = no smell, 1.0 = extremely smelly
    description: str
    details: Dict[str, object] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)
    remedy_hint: Optional[str] = None

    @property
    def is_painful(self) -> bool:
        """Does this smell cause pain? (intensity > 0.5)"""
        return self.intensity > 0.5

    @property
    def needs_immediate_attention(self) -> bool:
        """Is this smell urgent? (intensity > 0.7)"""
        return self.intensity > SMELL_PAIN_HIGH

    @property
    def parampara_vector(self) -> int:
        """Smell result connected to parampara (always % 37 == 0)."""
        # Position 8 (Parashurama) * 37 = 333
        return 333


# =============================================================================
# CODE SMELL PROTOCOL - The Contract
# =============================================================================

@runtime_checkable
class CodeSmellProtocol(Protocol):
    """
    Protocol for code smell detection.

    EVERY smell detector MUST implement this protocol.

    PROTOCOL FIRST: Define the contract, then implement.

    Ghrana (nose) uses implementations of this protocol to
    detect corruption in the codebase.
    """

    @property
    def category(self) -> SmellCategory:
        """What category of smell does this detector find?"""
        ...

    @property
    def name(self) -> str:
        """Human-readable name of this smell."""
        ...

    @property
    def description(self) -> str:
        """Description of what this smell indicates."""
        ...

    def smell(self, path: Path) -> Optional[SmellResult]:
        """
        Smell a file or directory for this type of corruption.

        Args:
            path: Path to smell (file or directory)

        Returns:
            SmellResult if corruption detected, None if clean.
        """
        ...

    def can_smell(self, path: Path) -> bool:
        """
        Can this detector smell this path?

        Some detectors only work on certain file types.
        """
        ...


# =============================================================================
# GHRANA PROTOCOL - The Nose that coordinates smells
# =============================================================================

@runtime_checkable
class GhranaProtocol(Protocol):
    """
    Protocol for Ghrana (nose) - the code smell coordinator.

    Position 8 (Parashurama) owns this protocol.
    Parashurama smells corruption and ACTS (wields the axe!).

    SHASTRA: SB 3.26.51 - Ghrana perceives Gandha (smell).
    """

    @property
    def smell_detectors(self) -> Dict[str, CodeSmellProtocol]:
        """Get all registered smell detectors."""
        ...

    def register_detector(self, detector: CodeSmellProtocol) -> None:
        """Register a smell detector."""
        ...

    def smell_path(self, path: Path) -> List[SmellResult]:
        """
        Smell a path with all registered detectors.

        Returns list of all detected smells.
        """
        ...

    def smell_codebase(self, root: Path) -> List[SmellResult]:
        """
        Smell entire codebase.

        Walks the directory tree and applies all detectors.
        """
        ...

    def get_total_stench(self) -> float:
        """
        Get aggregate smell level for entropy calculation.

        This drives the daemon's chanting frequency.
        """
        ...


# =============================================================================
# INIT FILE TOO LARGE - Structural Smell
# =============================================================================

class InitFileTooLarge:
    """
    Detects __init__.py files that are too large.

    THRESHOLD: 300 LOC (configurable)

    Large __init__.py files indicate:
    - Too much logic in module entry point
    - Need for submodule organization
    - Violation of separation of concerns

    REMEDY: Split into submodules, use lazy imports.
    """

    threshold_loc: ClassVar[int] = INIT_FILE_LOC_THRESHOLD

    @property
    def category(self) -> SmellCategory:
        return SmellCategory.STRUCTURAL

    @property
    def name(self) -> str:
        return "InitFileTooLarge"

    @property
    def description(self) -> str:
        return f"__init__.py exceeds {self.threshold_loc} lines of code"

    def can_smell(self, path: Path) -> bool:
        """Only smell __init__.py files."""
        return path.is_file() and path.name == "__init__.py"

    def smell(self, path: Path) -> Optional[SmellResult]:
        """
        Count lines in __init__.py and report if over threshold.
        """
        if not self.can_smell(path):
            return None

        try:
            content = path.read_text()
            lines = content.split('\n')
            loc = len([l for l in lines if l.strip() and not l.strip().startswith('#')])

            if loc <= self.threshold_loc:
                return None  # Clean!

            # Calculate intensity based on how far over threshold
            overage = loc - self.threshold_loc
            intensity = min(1.0, overage / self.threshold_loc)  # Caps at 1.0

            return SmellResult(
                file_path=path,
                category=self.category,
                intensity=intensity,
                description=f"__init__.py has {loc} LOC (threshold: {self.threshold_loc})",
                details={
                    "loc": loc,
                    "threshold": self.threshold_loc,
                    "overage": overage,
                    "overage_percent": round(overage / self.threshold_loc * 100, 1),
                },
                remedy_hint="Split into submodules, use lazy imports (see substrate/__init__.py)",
            )

        except Exception as e:
            # Can't read file - return error smell
            return SmellResult(
                file_path=path,
                category=self.category,
                intensity=0.3,  # Low intensity for read errors
                description=f"Cannot read file: {e}",
                details={"error": str(e)},
            )


# =============================================================================
# ANY TYPE VIOLATION - Type Safety Smell
# =============================================================================

class AnyTypeViolation:
    """
    Detects bare `Any` type usage in Python code.

    Uses the existing watertight.py infrastructure.

    Any types indicate:
    - Lost type safety
    - Potential runtime errors
    - Spiritual pollution (in Mahamantra terms)

    REMEDY: Replace with proper typed alternatives.
    """

    @property
    def category(self) -> SmellCategory:
        return SmellCategory.TYPE_SAFETY

    @property
    def name(self) -> str:
        return "AnyTypeViolation"

    @property
    def description(self) -> str:
        return "Bare `Any` type usage detected"

    def can_smell(self, path: Path) -> bool:
        """Smell Python files."""
        return path.is_file() and path.suffix == ".py"

    def smell(self, path: Path) -> Optional[SmellResult]:
        """
        Check file for Any type violations using watertight checker.
        """
        if not self.can_smell(path):
            return None

        try:
            # Import watertight checker
            # check_file returns List[TypeViolation] directly
            from vibe_core.mahamantra.substrate.watertight import check_file

            violations = check_file(path)

            if not violations:
                return None  # Clean!

            violation_count = len(violations)

            # Intensity based on violation count
            # 1 violation = 0.3, 5 = 0.5, 10+ = 1.0
            intensity = min(1.0, 0.3 + (violation_count * 0.07))

            # Parampara check: violation_count % 37 == 0 means connected
            is_connected = violation_count % 37 == 0

            return SmellResult(
                file_path=path,
                category=self.category,
                intensity=intensity,
                description=f"Found {violation_count} Any type violation(s)",
                details={
                    "violation_count": violation_count,
                    "violations": [
                        {
                            "line": v.line,
                            "column": v.column,
                            "type": v.violation_type,
                            "context": v.context,
                        }
                        for v in violations[:10]  # First 10
                    ],
                    "is_connected": is_connected,  # parampara check
                },
                remedy_hint="Replace Any with proper types (Union, TypeVar, concrete types)",
            )

        except ImportError:
            # watertight not available - skip
            return None
        except Exception as e:
            return SmellResult(
                file_path=path,
                category=self.category,
                intensity=0.3,
                description=f"Cannot check file: {e}",
                details={"error": str(e)},
            )


# =============================================================================
# GHRANA IMPLEMENTATION - The Nose
# =============================================================================

class Ghrana:
    """
    Implementation of GhranaProtocol - The code smell nose.

    Position 8 (Parashurama) - Smells corruption, wields the axe.

    USAGE:
        nose = Ghrana()
        nose.register_detector(InitFileTooLarge())
        nose.register_detector(AnyTypeViolation())

        smells = nose.smell_codebase(Path("vibe_core/mahamantra"))
        for smell in smells:
            if smell.needs_immediate_attention:
                generate_heal_intent(smell)
    """

    def __init__(self) -> None:
        self._detectors: Dict[str, CodeSmellProtocol] = {}
        self._last_smell_results: List[SmellResult] = []

        # Auto-register default detectors
        self.register_detector(InitFileTooLarge())
        self.register_detector(AnyTypeViolation())

    @property
    def smell_detectors(self) -> Dict[str, CodeSmellProtocol]:
        return dict(self._detectors)

    def register_detector(self, detector: CodeSmellProtocol) -> None:
        """Register a smell detector."""
        self._detectors[detector.name] = detector

    def smell_path(self, path: Path) -> List[SmellResult]:
        """Smell a single path with all detectors."""
        results: List[SmellResult] = []

        for detector in self._detectors.values():
            if detector.can_smell(path):
                result = detector.smell(path)
                if result is not None:
                    results.append(result)

        return results

    def smell_codebase(
        self,
        root: Path,
        skip_patterns: Tuple[str, ...] = ("__pycache__", ".git", "node_modules", ".venv"),
    ) -> List[SmellResult]:
        """
        Smell entire codebase.

        Walks directory tree, applies all detectors.
        """
        results: List[SmellResult] = []

        if not root.exists():
            return results

        if root.is_file():
            return self.smell_path(root)

        # Walk directory
        for path in root.rglob("*"):
            # Skip patterns
            skip = False
            for pattern in skip_patterns:
                if pattern in str(path):
                    skip = True
                    break
            if skip:
                continue

            if path.is_file():
                results.extend(self.smell_path(path))

        self._last_smell_results = results
        return results

    def get_total_stench(self) -> float:
        """
        Get aggregate smell level.

        This drives daemon chanting frequency.
        """
        if not self._last_smell_results:
            return 0.0

        # Sum intensities, cap at 1.0
        total = sum(r.intensity for r in self._last_smell_results)
        return min(1.0, total / max(1, len(self._last_smell_results)))

    def get_painful_smells(self) -> List[SmellResult]:
        """Get only painful smells (intensity > 0.5)."""
        return [r for r in self._last_smell_results if r.is_painful]

    def get_urgent_smells(self) -> List[SmellResult]:
        """Get urgent smells needing immediate attention."""
        return [r for r in self._last_smell_results if r.needs_immediate_attention]


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def smell_mahamantra() -> List[SmellResult]:
    """
    Convenience function to smell the mahamantra directory.

    Returns list of all detected smells.
    """
    nose = Ghrana()
    mahamantra_path = Path(__file__).parent.parent
    return nose.smell_codebase(mahamantra_path)


def print_smell_report(results: List[SmellResult]) -> None:
    """Print human-readable smell report."""
    if not results:
        print("No smells detected. Code is clean!")
        return

    print("\n" + "=" * 60)
    print("  GHRANA SMELL REPORT")
    print("=" * 60)

    # Group by category
    by_category: Dict[SmellCategory, List[SmellResult]] = {}
    for r in results:
        if r.category not in by_category:
            by_category[r.category] = []
        by_category[r.category].append(r)

    for category, smells in by_category.items():
        print(f"\n  [{category.value.upper()}] ({len(smells)} smells)")
        for smell in sorted(smells, key=lambda s: -s.intensity):
            urgent = " (URGENT!)" if smell.needs_immediate_attention else ""
            print(f"    {smell.intensity:.2f} {smell.file_path.name}: {smell.description}{urgent}")
            if smell.remedy_hint:
                print(f"         Remedy: {smell.remedy_hint}")

    total_stench = sum(r.intensity for r in results) / len(results)
    print(f"\n  Total Stench: {total_stench:.2f}")
    print("=" * 60)


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def cli_smell(target: Optional[str] = None) -> Dict[str, object]:
    """
    CLI entry point for smell detection.

    Usage:
        python -m vibe_core.mahamantra.protocols._smell [path]
    """
    import sys

    if target:
        path = Path(target)
    else:
        path = Path(__file__).parent.parent  # mahamantra/

    nose = Ghrana()
    results = nose.smell_codebase(path)

    print_smell_report(results)

    return {
        "path": str(path),
        "total_smells": len(results),
        "total_stench": nose.get_total_stench(),
        "urgent_count": len(nose.get_urgent_smells()),
        "smells": [
            {
                "file": str(r.file_path),
                "category": r.category.value,
                "intensity": r.intensity,
                "description": r.description,
            }
            for r in results
        ],
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "INIT_FILE_LOC_THRESHOLD",
    "ANY_TYPE_MAX_VIOLATIONS",
    "SMELL_PAIN_LOW",
    "SMELL_PAIN_MEDIUM",
    "SMELL_PAIN_HIGH",
    # Enums
    "SmellCategory",
    # Result Types
    "SmellResult",
    # Protocols
    "CodeSmellProtocol",
    "GhranaProtocol",
    # Implementations
    "InitFileTooLarge",
    "AnyTypeViolation",
    "Ghrana",
    # Functions
    "smell_mahamantra",
    "print_smell_report",
    "cli_smell",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else None
    cli_smell(target)

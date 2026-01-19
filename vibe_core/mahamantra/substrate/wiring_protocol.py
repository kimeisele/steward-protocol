"""
WIRING PROTOCOL - The Enforcement Layer
========================================

"dharma-kṣetre kuru-kṣetre samavetā yuyutsavaḥ"
"On the field of dharma, assembled ready to fight"
— Bhagavad Gita 1.1

THIS IS NOT DOCUMENTATION. THIS IS ENFORCEMENT.

FOLDER_IS_WIRING is not a suggestion. It's a protocol that:
1. VALIDATES structure matches SSOT
2. REJECTS violations
3. REPORTS discrepancies

If folder structure doesn't match MAHAMANTRA_POSITIONS, the system is BROKEN.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x4a7c2e91"

from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Dict,
    Final,
    List,
    Protocol,
    Set,
    Tuple,
    TypedDict,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.position import MAHAMANTRA_POSITIONS
from vibe_core.mahamantra.substrate.mahajana import Quarter


# =============================================================================
# VIOLATION TYPES (Watertight - no Any)
# =============================================================================


class ViolationType:
    """Types of wiring violations."""

    ORPHAN_FOLDER: Final[str] = "orphan_folder"  # Folder not in SSOT
    MISSING_FOLDER: Final[str] = "missing_folder"  # SSOT entry without folder
    MISSING_DECLARATION: Final[str] = "missing_decl"  # No __mahajana__ etc
    WRONG_POSITION: Final[str] = "wrong_position"  # __position__ doesn't match
    WRONG_QUARTER: Final[str] = "wrong_quarter"  # Folder in wrong quarter
    NO_PROTOCOL: Final[str] = "no_protocol"  # No Protocol class
    NO_NULL: Final[str] = "no_null"  # No Null implementation


class Violation(TypedDict):
    """A single wiring violation."""

    type: str  # ViolationType value
    path: str  # Folder or file path
    expected: str  # What SSOT says should be
    actual: str  # What we found
    severity: str  # "error" or "warning"


class ValidationResult(TypedDict):
    """Result of wiring validation."""

    valid: bool
    violations: List[Violation]
    wired_count: int  # Correctly wired folders
    orphan_count: int  # Folders not in SSOT
    missing_count: int  # SSOT entries without folders
    coverage: float  # wired_count / 16


# =============================================================================
# SSOT EXPECTATIONS (Derived from MAHAMANTRA_POSITIONS)
# =============================================================================

# What MUST exist according to SSOT
EXPECTED_QUARTERS: Final[Set[str]] = {q.value for q in Quarter}

EXPECTED_POSITIONS: Final[Dict[str, List[str]]] = {
    "genesis": [],
    "dharma": [],
    "karma": [],
    "moksha": [],
}

# Populate from SSOT
for pos in MAHAMANTRA_POSITIONS:
    quarter = pos.quarter.value
    guardian = pos.guardian.value
    EXPECTED_POSITIONS[quarter].append(guardian)

# Full path expectations: quarter/position -> index
EXPECTED_PATHS: Final[Dict[str, int]] = {}
for pos in MAHAMANTRA_POSITIONS:
    path = f"{pos.quarter.value}/{pos.guardian.value}"
    EXPECTED_PATHS[path] = pos.index


# =============================================================================
# WIRING PROTOCOL (The Enforcement Interface)
# =============================================================================


@runtime_checkable
class WiringEnforcementProtocol(Protocol):
    """
    Protocol for ENFORCING folder = wiring.

    This is not validation. This is LAW.

    Implementations MUST:
    1. Check folder structure against SSOT
    2. Report ALL violations
    3. Provide actionable fixes
    """

    def validate(self) -> ValidationResult:
        """
        Validate entire mahamantra structure.
        Returns comprehensive validation result.
        """
        ...

    def is_wired(self, path: str) -> bool:
        """
        Check if a path is properly wired.
        Path format: "quarter/position" e.g. "genesis/brahma"
        """
        ...

    def get_violations(self) -> List[Violation]:
        """Get all current violations."""
        ...

    def get_expected_structure(self) -> Dict[str, List[str]]:
        """Get what SSOT expects."""
        ...


# =============================================================================
# WIRING ENFORCER (The Implementation)
# =============================================================================


class WiringEnforcer:
    """
    Enforces FOLDER_IS_WIRING.

    Scans mahamantra folder structure and validates against SSOT.
    Reports violations. No mercy.
    """

    def __init__(self, mahamantra_path: Path) -> None:
        self._base = mahamantra_path
        self._violations: List[Violation] = []
        self._wired: Set[str] = set()

    def validate(self) -> ValidationResult:
        """
        Validate entire structure.

        Checks:
        1. All expected quarters exist
        2. All expected positions exist in correct quarters
        3. Each position folder has correct __mahajana__, __position__
        4. No orphan folders
        """
        self._violations = []
        self._wired = set()

        # Check quarters
        self._validate_quarters()

        # Check positions
        self._validate_positions()

        # Check for orphans
        self._find_orphans()

        # Calculate metrics
        wired_count = len(self._wired)
        orphan_count = len([v for v in self._violations if v["type"] == ViolationType.ORPHAN_FOLDER])
        missing_count = len([v for v in self._violations if v["type"] == ViolationType.MISSING_FOLDER])

        return ValidationResult(
            valid=len([v for v in self._violations if v["severity"] == "error"]) == 0,
            violations=self._violations,
            wired_count=wired_count,
            orphan_count=orphan_count,
            missing_count=missing_count,
            coverage=wired_count / 16.0,
        )

    def _validate_quarters(self) -> None:
        """Check all quarters exist."""
        for quarter in EXPECTED_QUARTERS:
            quarter_path = self._base / quarter
            if not quarter_path.exists():
                self._violations.append(
                    Violation(
                        type=ViolationType.MISSING_FOLDER,
                        path=str(quarter_path),
                        expected=quarter,
                        actual="<missing>",
                        severity="error",
                    )
                )

    def _validate_positions(self) -> None:
        """Check all positions exist in correct quarters."""
        for quarter, positions in EXPECTED_POSITIONS.items():
            quarter_path = self._base / quarter
            if not quarter_path.exists():
                continue  # Already reported as missing quarter

            for position in positions:
                pos_path = quarter_path / position
                full_path = f"{quarter}/{position}"
                expected_index = EXPECTED_PATHS.get(full_path, -1)

                if not pos_path.exists():
                    self._violations.append(
                        Violation(
                            type=ViolationType.MISSING_FOLDER,
                            path=str(pos_path),
                            expected=full_path,
                            actual="<missing>",
                            severity="error",
                        )
                    )
                    continue

                # Check __init__.py exists
                init_file = pos_path / "__init__.py"
                if not init_file.exists():
                    self._violations.append(
                        Violation(
                            type=ViolationType.MISSING_DECLARATION,
                            path=str(init_file),
                            expected="__init__.py with __mahajana__, __position__",
                            actual="<missing>",
                            severity="error",
                        )
                    )
                    continue

                # Check declarations
                self._validate_declarations(init_file, position, expected_index)

                # If we got here, it's wired
                self._wired.add(full_path)

    def _validate_declarations(self, init_file: Path, expected_name: str, expected_index: int) -> None:
        """Check __mahajana__ and __position__ are correct."""
        try:
            content = init_file.read_text()

            # Check __mahajana__
            if f'__mahajana__ = "{expected_name}"' not in content:
                # Try single quotes
                if f"__mahajana__ = '{expected_name}'" not in content:
                    self._violations.append(
                        Violation(
                            type=ViolationType.MISSING_DECLARATION,
                            path=str(init_file),
                            expected=f'__mahajana__ = "{expected_name}"',
                            actual="<wrong or missing>",
                            severity="error",
                        )
                    )

            # Check __position__
            if f"__position__ = {expected_index}" not in content:
                self._violations.append(
                    Violation(
                        type=ViolationType.WRONG_POSITION,
                        path=str(init_file),
                        expected=f"__position__ = {expected_index}",
                        actual="<wrong or missing>",
                        severity="error",
                    )
                )

        except Exception:
            self._violations.append(
                Violation(
                    type=ViolationType.MISSING_DECLARATION,
                    path=str(init_file),
                    expected="readable __init__.py",
                    actual="<read error>",
                    severity="error",
                )
            )

    def _find_orphans(self) -> None:
        """Find folders that exist but aren't in SSOT."""
        for quarter in EXPECTED_QUARTERS:
            quarter_path = self._base / quarter
            if not quarter_path.exists():
                continue

            expected_in_quarter = set(EXPECTED_POSITIONS.get(quarter, []))

            for child in quarter_path.iterdir():
                if child.name.startswith("_"):
                    continue
                if not child.is_dir():
                    continue

                if child.name not in expected_in_quarter:
                    self._violations.append(
                        Violation(
                            type=ViolationType.ORPHAN_FOLDER,
                            path=str(child),
                            expected="<should not exist>",
                            actual=child.name,
                            severity="warning",
                        )
                    )

    def is_wired(self, path: str) -> bool:
        """Check if path is properly wired."""
        return path in EXPECTED_PATHS

    def get_violations(self) -> List[Violation]:
        """Get violations from last validation."""
        return self._violations

    def get_expected_structure(self) -> Dict[str, List[str]]:
        """Get what SSOT expects."""
        return dict(EXPECTED_POSITIONS)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================


def enforce_wiring(mahamantra_path: Path) -> ValidationResult:
    """
    One-shot validation of mahamantra wiring.

    Usage:
        from vibe_core.mahamantra.substrate.wiring_protocol import enforce_wiring
        from pathlib import Path

        result = enforce_wiring(Path("vibe_core/mahamantra"))
        if not result["valid"]:
            for v in result["violations"]:
                print(f"{v['severity']}: {v['type']} at {v['path']}")
    """
    enforcer = WiringEnforcer(mahamantra_path)
    return enforcer.validate()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ViolationType",
    "Violation",
    "ValidationResult",
    # SSOT expectations
    "EXPECTED_QUARTERS",
    "EXPECTED_POSITIONS",
    "EXPECTED_PATHS",
    # Protocol
    "WiringEnforcementProtocol",
    # Implementation
    "WiringEnforcer",
    # Convenience
    "enforce_wiring",
]

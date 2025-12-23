"""
OPUS-159: Genesis Types

Core types for the vibe_core Genesis service.

ModuleType enum and result dataclasses for the Stadtamt.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional


class ModuleType(Enum):
    """Types of modules the Genesis service can handle."""

    # Core vibe_core types
    PLUGIN = auto()  # vibe_core/plugins/*
    CARTRIDGE = auto()  # vibe_core/cartridges/*
    SECTION = auto()  # vibe_core/phoenix/sections/*

    # MANAS-specific types
    ANALYZER = auto()  # */analyzers/*
    SENSE = auto()  # */cortex/*_sense.py
    ACTION = auto()  # */cortex/*_action.py

    # Other types
    CIRCUIT = auto()  # */circuits/*.yaml
    KNOWLEDGE = auto()  # knowledge/*
    TOOL = auto()  # */tools/*
    TEST = auto()  # tests/*

    # Fallback
    UNKNOWN = auto()

    @classmethod
    def from_string(cls, value: str) -> "ModuleType":
        """Convert string to ModuleType."""
        try:
            return cls[value.upper()]
        except KeyError:
            return cls.UNKNOWN


@dataclass
class ComplianceCheck:
    """Result of a single compliance check."""

    name: str
    passed: bool
    message: str = ""
    severity: str = "warning"  # info, warning, error


@dataclass
class ComplianceReport:
    """Full GAD-000 compliance report for a module."""

    path: Path
    module_type: ModuleType
    checks: List[ComplianceCheck] = field(default_factory=list)
    score: float = 0.0  # 0.0-1.0

    @property
    def passed(self) -> bool:
        """True if all required checks passed."""
        return all(c.passed for c in self.checks if c.severity == "error")

    @property
    def missing_files(self) -> List[str]:
        """List of missing required files."""
        missing = []
        for c in self.checks:
            if not c.passed and c.name.startswith("file:"):
                # Extract filename from "file:__init__.py"
                filename = c.name.replace("file:", "")
                missing.append(filename)
        return missing

    def add_check(self, name: str, passed: bool, message: str = "", severity: str = "warning"):
        """Add a compliance check result."""
        self.checks.append(ComplianceCheck(name, passed, message, severity))
        self._recalculate_score()

    def _recalculate_score(self):
        """Recalculate compliance score."""
        if not self.checks:
            self.score = 0.0
            return
        passed = sum(1 for c in self.checks if c.passed)
        self.score = passed / len(self.checks)


@dataclass
class BuildResult:
    """Result of building infrastructure."""

    path: Path
    module_type: ModuleType
    created_files: Dict[str, Path] = field(default_factory=dict)
    skipped_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True if no errors occurred."""
        return len(self.errors) == 0

    @property
    def files_created_count(self) -> int:
        """Number of files created."""
        return len(self.created_files)

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        if self.success:
            return f"Created {self.files_created_count} files for {self.module_type.name}"
        return f"Failed: {self.errors[0]}"


@dataclass
class GenesisResult:
    """Combined result of genesis operation."""

    path: Path
    module_type: ModuleType
    compliance_before: Optional[ComplianceReport] = None
    compliance_after: Optional[ComplianceReport] = None
    build_result: Optional[BuildResult] = None

    @property
    def success(self) -> bool:
        """True if operation succeeded."""
        if self.build_result:
            return self.build_result.success
        return True

    @property
    def improved(self) -> bool:
        """True if compliance improved."""
        if self.compliance_before and self.compliance_after:
            return self.compliance_after.score > self.compliance_before.score
        return False

    @property
    def files_created(self) -> List[str]:
        """List of files created."""
        if self.build_result:
            return list(self.build_result.created_files.keys())
        return []

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        if self.build_result and self.build_result.files_created_count > 0:
            return (
                f"Created {self.build_result.files_created_count} files, compliance: {self.compliance_after.score:.0%}"
            )
        if self.compliance_after and self.compliance_after.passed:
            return f"Already compliant ({self.compliance_after.score:.0%})"
        return "No changes needed"

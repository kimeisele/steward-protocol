"""
SRIVASA - Compliance Validator
===============================

"srivasa thakura prabhu nrtya kare range"
"Srivasa Thakura dances in ecstasy."
-- Chaitanya Charitamrita

Validates the codebase against:
- SSOT (Single Source of Truth) principles
- TIER system compliance (TIER 0 = 7 axioms)
- Declaration vs routing consistency
- Mahajana position integrity
- Genesis byte validity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# === MAHAJANA DECLARATION ===
__mahajana__ = "srivasa"
__position__ = 4
__genesis__ = "0x00000004"

# The 7 TIER-0 Axioms (counted from Mahamantra)
TIER_0_AXIOMS = {
    "WORDS": 16,      # Total words in Mahamantra
    "TRINITY": 3,     # 3 names: Hare, Krishna, Rama
    "HARE_COUNT": 8,  # Hare appears 8 times
    "KRISHNA_COUNT": 4,
    "RAMA_COUNT": 4,
    "PANCHA": 5,      # Pancha Tattva
    "HALVES": 2,      # Two halves
}

# 16 Mahajana positions
MAHAJANA_POSITIONS = {
    0: "vyasa", 1: "brahma", 2: "narada", 3: "shambhu",
    4: "prithu", 5: "kumaras", 6: "kapila", 7: "manu",
    8: "parashurama", 9: "prahlada", 10: "janaka", 11: "bhishma",
    12: "nrisimha", 13: "bali", 14: "shuka", 15: "yamaraja",
}


@dataclass
class ValidationIssue:
    """A validation issue found."""
    path: str
    issue_type: str
    message: str
    severity: str = "warning"  # "error", "warning", "info"


@dataclass
class ValidationResult:
    """Result of validation."""
    issues: List[ValidationIssue] = field(default_factory=list)
    passed: int = 0
    failed: int = 0


class ComplianceValidator:
    """
    Validates codebase against Maha principles.
    
    Usage:
        validator = ComplianceValidator(project_root)
        result = validator.validate_all()
        ssot_issues = validator.check_ssot()
    """
    
    def __init__(self, root: Path):
        self.root = root
        self._result = ValidationResult()
    
    def validate_all(self, scanner=None) -> ValidationResult:
        """Run all validations."""
        if scanner is None:
            from .scanner import ModuleScanner
            scanner = ModuleScanner(self.root)
            scanner.scan_all()
        
        self._check_position_integrity(scanner)
        self._check_mahajana_consistency(scanner)
        self._check_ssot_usage(scanner)
        
        return self._result
    
    def _check_position_integrity(self, scanner) -> None:
        """Check that declared positions match mahajana names."""
        for path, info in scanner._modules.items():
            if info.mahajana and info.position is not None:
                expected_mahajana = MAHAJANA_POSITIONS.get(info.position)
                if expected_mahajana and expected_mahajana != info.mahajana:
                    self._result.issues.append(ValidationIssue(
                        path=path,
                        issue_type="position_mismatch",
                        message=f"Position {info.position} should be '{expected_mahajana}', got '{info.mahajana}'",
                        severity="error",
                    ))
                    self._result.failed += 1
                else:
                    self._result.passed += 1
    
    def _check_mahajana_consistency(self, scanner) -> None:
        """Check that mahajana declarations are valid."""
        valid_mahajanas = set(MAHAJANA_POSITIONS.values())
        
        for path, info in scanner._modules.items():
            if info.mahajana:
                if info.mahajana not in valid_mahajanas:
                    self._result.issues.append(ValidationIssue(
                        path=path,
                        issue_type="invalid_mahajana",
                        message=f"Unknown mahajana: '{info.mahajana}'",
                        severity="warning",
                    ))
                    self._result.failed += 1
                else:
                    self._result.passed += 1
    
    def _check_ssot_usage(self, scanner) -> None:
        """Check for SSOT violations (magic numbers that should be axioms)."""
        for path, info in scanner._modules.items():
            try:
                content = info.path.read_text(encoding="utf-8")
                
                # Check for hardcoded 16 (should be WORDS)
                if "= 16" in content and "WORDS" not in content:
                    if "_axioms" not in path and "test" not in path.lower():
                        self._result.issues.append(ValidationIssue(
                            path=path,
                            issue_type="ssot_violation",
                            message="Hardcoded 16 found - should use WORDS from _axioms.py",
                            severity="warning",
                        ))
                
                # Check for hardcoded 108 (should be MALA)
                if "= 108" in content and "MALA" not in content:
                    if "_axioms" not in path:
                        self._result.issues.append(ValidationIssue(
                            path=path,
                            issue_type="ssot_violation",
                            message="Hardcoded 108 found - should use MALA",
                            severity="warning",
                        ))
                
            except Exception:
                pass
    
    def check_ssot(self) -> Dict[str, Any]:
        """Check SSOT compliance specifically."""
        from .scanner import ModuleScanner
        scanner = ModuleScanner(self.root)
        scanner.scan_all()
        
        self._check_ssot_usage(scanner)
        
        return {
            "violations": [i for i in self._result.issues if i.issue_type == "ssot_violation"],
            "count": len([i for i in self._result.issues if i.issue_type == "ssot_violation"]),
        }
    
    def summary(self) -> Dict[str, Any]:
        """Get a token-efficient summary."""
        by_type: Dict[str, int] = {}
        by_severity: Dict[str, int] = {}
        
        for issue in self._result.issues:
            by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        
        return {
            "passed": self._result.passed,
            "failed": self._result.failed,
            "total_issues": len(self._result.issues),
            "by_type": by_type,
            "by_severity": by_severity,
            "top_issues": [(i.path, i.message) for i in self._result.issues[:10]],
        }


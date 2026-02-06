#!/usr/bin/env python3
"""
P0 AUDIT VERIFICATION - COMPLETE SYSTEM DIAGNOSIS
==================================================

This script verifies ALL critical P0 problems in the codebase.
Run this BEFORE and AFTER fixes to verify progress.

Usage:
    python P0_AUDIT_VERIFICATION.py
    python P0_AUDIT_VERIFICATION.py --verbose
"""

import ast
import hashlib
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Colors for output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

PROJECT_ROOT = Path(__file__).parent
VIBE_CORE = PROJECT_ROOT / "vibe_core"


class P0Problem:
    """Represents a P0 problem with verification."""
    
    def __init__(self, id: str, title: str, severity: str):
        self.id = id
        self.title = title
        self.severity = severity
        self.findings: List[Dict] = []
        self.verified = False
    
    def add_finding(self, file: str, line: int, code: str, reason: str):
        self.findings.append({
            "file": file,
            "line": line,
            "code": code,
            "reason": reason
        })
        self.verified = True
    
    def report(self) -> str:
        status = f"{RED}✗ VERIFIED{RESET}" if self.verified else f"{GREEN}✓ CLEAN{RESET}"
        output = [f"\n{'='*80}"]
        output.append(f"{self.severity} | {self.id}: {self.title}")
        output.append(f"Status: {status}")
        output.append(f"Findings: {len(self.findings)}")
        
        if self.findings:
            output.append(f"\n{YELLOW}Evidence:{RESET}")
            for i, finding in enumerate(self.findings[:10], 1):  # Show first 10
                output.append(f"  {i}. {finding['file']}:{finding['line']}")
                output.append(f"     {finding['reason']}")
                output.append(f"     Code: {finding['code'][:80]}")
        
        return "\n".join(output)


class P0Auditor:
    """Complete P0 audit system."""
    
    def __init__(self):
        self.problems: List[P0Problem] = []
        self.stats = {
            "files_scanned": 0,
            "lines_scanned": 0,
            "p0_critical": 0,
            "p0_security": 0,
            "p0_architecture": 0,
        }
    
    def scan_all(self):
        """Run all P0 checks."""
        print(f"{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}P0 AUDIT VERIFICATION - COMPLETE SYSTEM DIAGNOSIS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}\n")
        
        # P0-1: Non-deterministic hash()
        self.check_nondeterministic_hash()
        
        # P0-2: Audit bypasses
        self.check_audit_bypasses()
        
        # P0-3: Assert-based security
        self.check_assert_security()
        
        # P0-4: Circular imports
        self.check_circular_imports()
        
        # P0-5: Duplicate state systems
        self.check_duplicate_state()
        
        # P0-6: Research code in production
        self.check_research_in_production()
        
        # P0-7: Service instantiation bypasses
        self.check_service_bypasses()
        
        # P0-8: Incomplete Balarama pattern
        self.check_incomplete_balarama()
        
        # Generate report
        self.generate_report()
    
    def check_nondeterministic_hash(self):
        """P0-1: Find uses of hash() that break determinism."""
        problem = P0Problem(
            "P0-1",
            "Non-Deterministic hash() Usage",
            "🔥 P0-CRITICAL"
        )
        
        # Scan for hash() calls
        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                lines = content.split("\n")
                
                for i, line in enumerate(lines, 1):
                    if "hash(" in line and "hashlib" not in line:
                        # Check if it's actually Python's hash()
                        if "#" not in line.split("hash(")[0]:  # Not in comment
                            problem.add_finding(
                                str(py_file.relative_to(PROJECT_ROOT)),
                                i,
                                line.strip(),
                                "Uses Python hash() which is non-deterministic across runs"
                            )
            except Exception:
                pass
        
        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_critical"] += 1

    def check_audit_bypasses(self):
        """P0-2: Find audit/security bypasses."""
        problem = P0Problem(
            "P0-2",
            "Audit Trail Bypasses (Fail-Open)",
            "🔥 P0-SECURITY"
        )

        patterns = [
            ("except Exception", "pass", "Silent exception swallowing"),
            ("except Exception", "print", "Exception logged but execution continues"),
            ("try:", "except:", "Bare except clause"),
        ]

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    # Check for audit bypass patterns
                    if "Sankirtan Chamber bypassed" in line:
                        problem.add_finding(
                            str(py_file.relative_to(PROJECT_ROOT)),
                            i,
                            line.strip(),
                            "Explicit audit bypass - security critical operations can skip logging"
                        )

                    # Check for silent exception handling in critical paths
                    if "except Exception" in line and i < len(lines) - 1:
                        next_line = lines[i].strip()
                        if next_line.startswith("pass") or "continue" in next_line:
                            problem.add_finding(
                                str(py_file.relative_to(PROJECT_ROOT)),
                                i,
                                line.strip(),
                                "Silent exception handling - errors are hidden"
                            )
            except Exception:
                pass

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_security"] += 1

    def check_assert_security(self):
        """P0-3: Find assert statements used for security/integrity checks."""
        problem = P0Problem(
            "P0-3",
            "Assert-Based Security (Removed in -O mode)",
            "🔥 P0-INTEGRITY"
        )

        critical_files = [
            "orchestrator.py",
            "maha_kernel.py",
            "maha_state.py",
            "verification.py",
        ]

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue

            # Focus on critical files
            if not any(cf in str(py_file) for cf in critical_files):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    if line.strip().startswith("assert "):
                        # Check if it's a security/integrity check
                        if any(keyword in line.lower() for keyword in [
                            "xor", "verify", "integrity", "valid", "check",
                            "quantum", "parampara", "lineage"
                        ]):
                            problem.add_finding(
                                str(py_file.relative_to(PROJECT_ROOT)),
                                i,
                                line.strip(),
                                "Critical integrity check using assert - will be removed in python -O"
                            )
            except Exception:
                pass

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_critical"] += 1

    def check_circular_imports(self):
        """P0-4: Find circular import patterns."""
        problem = P0Problem(
            "P0-4",
            "Circular Import Dependencies",
            "🔥 P0-ARCHITECTURE"
        )

        # Look for lazy import patterns (evidence of circular imports)
        patterns = [
            "LAZY",
            "circular import",
            "avoid circular",
            "break circular",
            "lazy load",
        ]

        for py_file in VIBE_CORE.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern in patterns:
                        if pattern.lower() in line.lower() and "import" in line.lower():
                            problem.add_finding(
                                str(py_file.relative_to(PROJECT_ROOT)),
                                i,
                                line.strip(),
                                f"Lazy import pattern detected - indicates circular dependency"
                            )
                            break
            except Exception:
                pass

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_architecture"] += 1

    def check_duplicate_state(self):
        """P0-5: Find duplicate state management systems."""
        problem = P0Problem(
            "P0-5",
            "Duplicate State Management Systems",
            "🔥 P0-ARCHITECTURE"
        )

        state_systems = {
            "MahaState": 0,
            "StateService": 0,
            "Prakriti": 0,
            "SynapseStore": 0,
            "EphemeralStorage": 0,
            "Ouroboros": 0,
            "ServiceRegistry": 0,
        }

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                for system in state_systems:
                    if system in content:
                        state_systems[system] += 1
            except Exception:
                pass

        # Report systems with high usage
        for system, count in state_systems.items():
            if count > 5:  # Arbitrary threshold
                problem.add_finding(
                    "multiple files",
                    0,
                    f"{system} used in {count} files",
                    f"Parallel state system - no single source of truth"
                )

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_architecture"] += 1

    def check_research_in_production(self):
        """P0-6: Find research code imported into production."""
        problem = P0Problem(
            "P0-6",
            "Research Code in Production Paths",
            "⚠️  P0-STABILITY"
        )

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file) or "research" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    if "from" in line and "research" in line and "import" in line:
                        if not line.strip().startswith("#"):
                            problem.add_finding(
                                str(py_file.relative_to(PROJECT_ROOT)),
                                i,
                                line.strip(),
                                "Production code imports from research/ - unstable dependency"
                            )
            except Exception:
                pass

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_architecture"] += 1

    def check_service_bypasses(self):
        """P0-7: Find direct service instantiation bypasses."""
        problem = P0Problem(
            "P0-7",
            "Service Instantiation Bypasses",
            "⚠️  P0-ARCHITECTURE"
        )

        service_patterns = [
            "Service()",
            "JanakaService()",
            "SamskaraService()",
            "KapilaService()",
            "BhishmaService()",
            "BrahmaService()",
        ]

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                lines = content.split("\n")

                for i, line in enumerate(lines, 1):
                    for pattern in service_patterns:
                        if pattern in line and "=" in line:
                            # Check if it's direct instantiation
                            if not line.strip().startswith("#"):
                                problem.add_finding(
                                    str(py_file.relative_to(PROJECT_ROOT)),
                                    i,
                                    line.strip(),
                                    f"Direct service instantiation - bypasses mahamantra routing"
                                )
                                break
            except Exception:
                pass

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_architecture"] += 1

    def check_incomplete_balarama(self):
        """P0-8: Find incomplete Balarama pattern enforcement."""
        problem = P0Problem(
            "P0-8",
            "Incomplete Balarama Pattern Enforcement",
            "⚠️  P0-ARCHITECTURE"
        )

        # Count MahamantraProxy usage vs direct service usage
        proxy_count = 0
        direct_count = 0

        for py_file in VIBE_CORE.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()

                if "MahamantraProxy(" in content:
                    proxy_count += content.count("MahamantraProxy(")

                # Count direct service instantiations
                for service in ["Service()", "JanakaService()", "BrahmaService()"]:
                    if service in content:
                        direct_count += content.count(service)
            except Exception:
                pass

        if direct_count > 0:
            problem.add_finding(
                "multiple files",
                0,
                f"MahamantraProxy: {proxy_count} uses, Direct instantiation: {direct_count} uses",
                "Balarama pattern not enforced globally - inconsistent service governance"
            )

        self.problems.append(problem)
        if problem.verified:
            self.stats["p0_architecture"] += 1

    def generate_report(self):
        """Generate final report."""
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}AUDIT RESULTS{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")

        # Print all problems
        for problem in self.problems:
            print(problem.report())

        # Summary
        print(f"\n{BLUE}{'='*80}{RESET}")
        print(f"{BLUE}SUMMARY{RESET}")
        print(f"{BLUE}{'='*80}{RESET}")

        total_problems = sum(1 for p in self.problems if p.verified)
        total_findings = sum(len(p.findings) for p in self.problems)

        print(f"\nTotal P0 Problems: {RED}{total_problems}{RESET}")
        print(f"Total Findings: {RED}{total_findings}{RESET}")
        print(f"\nBreakdown:")
        print(f"  🔥 P0-CRITICAL: {self.stats['p0_critical']}")
        print(f"  🔥 P0-SECURITY: {self.stats['p0_security']}")
        print(f"  ⚠️  P0-ARCHITECTURE: {self.stats['p0_architecture']}")

        # Save to JSON
        report_data = {
            "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip(),
            "total_problems": total_problems,
            "total_findings": total_findings,
            "stats": self.stats,
            "problems": [
                {
                    "id": p.id,
                    "title": p.title,
                    "severity": p.severity,
                    "verified": p.verified,
                    "findings_count": len(p.findings),
                    "findings": p.findings[:5]  # First 5 only
                }
                for p in self.problems
            ]
        }

        report_file = PROJECT_ROOT / "P0_AUDIT_REPORT.json"
        report_file.write_text(json.dumps(report_data, indent=2))
        print(f"\n{GREEN}✓ Report saved to: {report_file}{RESET}")


if __name__ == "__main__":
    auditor = P0Auditor()
    auditor.scan_all()


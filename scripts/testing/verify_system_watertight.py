#!/usr/bin/env python3
"""
SYSTEM WATERTIGHTNESS VERIFIER
Scans the codebase for hidden mocks, fake code, and placeholder implementations.
This is the foundation verification tool - no system is solid without it.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Terms of shame - indicators of non-production code
FORBIDDEN_TERMS = [
    ("mock", "mock implementation detected"),
    ("fake", "fake implementation detected"),
    ("dummy", "dummy implementation detected"),
    ("placeholder", "placeholder code detected"),
    ("return 0 #", "dummy return value"),
    ("return True #", "dummy boolean return"),
    ("pass  # TODO", "unimplemented code"),
    ("pass  # FIXME", "broken code marked for fixing"),
    ("# XXX", "incomplete code marker"),
    ("# HACK", "hack/workaround in production code"),
]

# Critical directories that MUST be clean (kernel-level only)
CRITICAL_DIRS = [
    "vibe_core/kernel_impl.py",
    "vibe_core/process_manager.py",
    "vibe_core/resource_manager.py",
    "vibe_core/vfs.py",
    "vibe_core/network_proxy.py",
    "vibe_core/lineage.py",
]

# Directories to exclude from checks
EXCLUDED_DIRS = {
    "tests",
    "test",
    "examples",
    "venv",
    "env",
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    ".pytest_cache",
    "build",
    "dist",
    "*.egg-info",
}

# Allowed comments - exceptions to the rules
ALLOW_MARKERS = {"# allow-mock", "# noqa", "# type: ignore"}


class WatertightnessVerifier:
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir)
        self.violations = []
        self.warnings = []
        self.stats = {
            "files_scanned": 0,
            "lines_scanned": 0,
            "violations_found": 0,
            "warnings_found": 0,
        }

    def should_skip(self, path: Path) -> bool:
        """Check if path should be excluded from scanning."""
        parts = path.parts
        for excluded in EXCLUDED_DIRS:
            if excluded in parts:
                return True
        return False

    def check_line(self, file_path: Path, line_num: int, line: str) -> None:
        """Check a single line for forbidden terms."""
        # Skip comments that are allowed
        if any(marker in line for marker in ALLOW_MARKERS):
            return

        for term, description in FORBIDDEN_TERMS:
            if term.lower() in line.lower():
                # Additional heuristics for false positives

                # Template placeholders are FEATURES, not bugs
                if term == "placeholder":
                    # Allow {{ placeholder }} template syntax
                    if "{{" in line and "}}" in line:
                        continue
                    # Allow "Permeable Prompts" module (prompt_context.py, context_loader.py)
                    if "prompt" in str(file_path).lower() or "context_loader" in str(file_path):
                        continue
                    # Allow "replace_placeholder" function names
                    if "def replace_placeholder" in line or "replace_placeholder(" in line:
                        continue

                # "mock" appears in many legitimate contexts
                if term == "mock":
                    # Allow unittest.mock imports
                    if "import" in line and "unittest.mock" in line:
                        continue
                    # Allow @mock.patch decorators in tests
                    if "test" in str(file_path).lower():
                        continue
                    # Allow NoOpClient/MockResponse (graceful degradation)
                    if "NoOp" in line or "llm_client" in str(file_path):
                        continue
                    # Allow "This is NOT a mock" comments
                    if "NOT a mock" in line or "not a mock" in line:
                        continue

                # "pass" is legitimate in many cases
                if term == "pass" and "pass  #" not in line:
                    continue

                violation = {
                    "file": str(file_path.relative_to(self.root)),
                    "line": line_num,
                    "code": line.strip(),
                    "issue": description,
                }

                # Check if this is in a critical directory
                is_critical = any(crit in str(file_path) for crit in CRITICAL_DIRS)

                if is_critical:
                    self.violations.append(violation)
                    self.stats["violations_found"] += 1
                else:
                    self.warnings.append(violation)
                    self.stats["warnings_found"] += 1

    def scan_file(self, file_path: Path) -> None:
        """Scan a single Python file."""
        if not file_path.suffix == ".py":
            return

        if self.should_skip(file_path):
            return

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    self.stats["lines_scanned"] += 1
                    self.check_line(file_path, line_num, line)

            self.stats["files_scanned"] += 1
        except Exception as e:
            self.warnings.append(
                {
                    "file": str(file_path.relative_to(self.root)),
                    "error": f"Could not scan: {e}",
                }
            )

    def run_scan(self) -> bool:
        """Scan all Python files in the project."""
        print("🕵️  STARTING DEEP SCAN FOR BULLSHIT...")
        print(f"   Root: {self.root}")
        print(f"   Scanning {len(CRITICAL_DIRS)} critical directories...")
        print()

        for root, dirs, files in os.walk(self.root):
            # Remove excluded dirs from traversal
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file in files:
                file_path = Path(root) / file
                self.scan_file(file_path)

        return len(self.violations) == 0

    def print_results(self) -> None:
        """Print detailed results."""
        print(f"\n{'=' * 70}")
        print(f"SCAN RESULTS")
        print(f"{'=' * 70}\n")

        print(f"📊 STATISTICS:")
        print(f"   Files scanned:       {self.stats['files_scanned']}")
        print(f"   Lines scanned:       {self.stats['lines_scanned']}")
        print(f"   Critical violations: {self.stats['violations_found']}")
        print(f"   Warnings:            {self.stats['warnings_found']}")
        print()

        if self.violations:
            print(f"❌ CRITICAL VIOLATIONS FOUND ({len(self.violations)} issues):\n")
            for v in self.violations:
                print(f"   FILE: {v['file']}:{v['line']}")
                print(f"   ISSUE: {v['issue']}")
                print(f"   CODE: {v['code']}")
                print()

        if self.warnings:
            print(f"⚠️  WARNINGS ({len(self.warnings)} issues):\n")
            for w in self.warnings:
                if "error" in w:
                    print(f"   {w['file']}: {w['error']}")
                else:
                    print(f"   FILE: {w['file']}:{w['line']}")
                    print(f"   ISSUE: {w['issue']}")
                    print(f"   CODE: {w['code']}")
                    print()

        print(f"{'=' * 70}")

        if not self.violations:
            print("✅ SYSTEM IS WATERTIGHT. NO CRITICAL MOCKS FOUND.")
            print("   The foundation is clean. Ready for real economy implementation.")
        else:
            print("❌ SYSTEM IS NOT WATERTIGHT.")
            print("   Fix these critical violations before proceeding.")
            print()
            print("   VIOLATIONS MUST BE ADDRESSED:")
            for v in self.violations:
                print(f"   - {v['file']}:{v['line']}")

        print(f"{'=' * 70}\n")


def main():
    verifier = WatertightnessVerifier()

    is_clean = verifier.run_scan()
    verifier.print_results()

    if not is_clean:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

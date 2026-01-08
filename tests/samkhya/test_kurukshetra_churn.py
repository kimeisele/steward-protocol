"""
TEST_KURUKSHETRA_CHURN.py - Migration Validator

"Auf dem Schlachtfeld von Kurukshetra stehen zwei Armeen."
- MAYAVAD: Direct imports of RealVibeKernel (legacy)
- VAISHNAVA: ServiceRegistry/KernelProtocol access (unified)

This test validates that the churn from legacy to unified protocols is progressing.
"""

import ast
from pathlib import Path
from typing import List, Set, Tuple

import pytest


class MayavadScanner(ast.NodeVisitor):
    """AST visitor to find MAYAVAD import patterns.

    Skips imports inside TYPE_CHECKING blocks (those are acceptable for type hints).
    """

    def __init__(self):
        self.mayavad_imports: List[Tuple[int, str]] = []  # (line, import_statement)
        self.vaishnava_imports: List[Tuple[int, str]] = []
        self._in_type_checking = False

    def visit_If(self, node: ast.If) -> None:
        """Track if we're inside a TYPE_CHECKING block."""
        # Check if this is "if TYPE_CHECKING:"
        is_type_checking = isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
        if is_type_checking:
            self._in_type_checking = True
            for child in node.body:
                self.visit(child)
            self._in_type_checking = False
            for child in node.orelse:
                self.visit(child)
        else:
            self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            # MAYAVAD: Direct RealVibeKernel import (skip if in TYPE_CHECKING)
            if "kernel_impl" in node.module and any(alias.name == "RealVibeKernel" for alias in node.names):
                if not self._in_type_checking:
                    self.mayavad_imports.append((node.lineno, f"from {node.module} import ..."))

            # VAISHNAVA: KernelProtocol import
            if "kernel_protocol" in node.module or "protocols" in node.module:
                for alias in node.names:
                    if "Protocol" in alias.name or alias.name == "ServiceRegistry":
                        self.vaishnava_imports.append((node.lineno, f"from {node.module} import {alias.name}"))

        self.generic_visit(node)


def scan_directory_for_mayavad(
    directory: Path,
    exclude_dirs: Set[str] = None,
    exclude_files: Set[str] = None,
) -> dict:
    """Scan a directory for MAYAVAD patterns.

    Args:
        directory: Path to scan
        exclude_dirs: Directory names to skip
        exclude_files: File basenames to skip (for factory patterns)
    """
    if exclude_dirs is None:
        exclude_dirs = {"__pycache__", ".git", ".pytest_cache", "node_modules"}
    if exclude_files is None:
        exclude_files = set()

    results = {
        "mayavad_files": [],
        "vaishnava_files": [],
        "total_mayavad": 0,
        "total_vaishnava": 0,
    }

    for py_file in directory.rglob("*.py"):
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue
        if py_file.name in exclude_files:
            continue

        try:
            source = py_file.read_text()
            tree = ast.parse(source)
        except (SyntaxError, UnicodeDecodeError):
            continue

        scanner = MayavadScanner()
        scanner.visit(tree)

        if scanner.mayavad_imports:
            results["mayavad_files"].append(
                {
                    "path": str(py_file.relative_to(directory)),
                    "count": len(scanner.mayavad_imports),
                    "lines": [line for line, _ in scanner.mayavad_imports],
                }
            )
            results["total_mayavad"] += len(scanner.mayavad_imports)

        if scanner.vaishnava_imports:
            results["vaishnava_files"].append(
                {
                    "path": str(py_file.relative_to(directory)),
                    "count": len(scanner.vaishnava_imports),
                }
            )
            results["total_vaishnava"] += len(scanner.vaishnava_imports)

    return results


class TestKurukshetraChurn:
    """
    KURUKSHETRA CHURN - The Battlefield of Protocol Migration.

    These tests track progress of the churn from MAYAVAD to VAISHNAVA patterns.
    """

    @pytest.fixture
    def vibe_core_path(self) -> Path:
        """Get path to vibe_core."""
        # Navigate from tests/samkhya to vibe_core
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent.parent
        return repo_root / "vibe_core"

    @pytest.fixture
    def scripts_path(self) -> Path:
        """Get path to scripts directory."""
        test_dir = Path(__file__).parent
        repo_root = test_dir.parent.parent
        return repo_root / "scripts"

    # =========================================================================
    # POST 1: VIBE_CORE - The Core Should Be Clean
    # =========================================================================

    def test_plugins_no_direct_kernel_imports(self, vibe_core_path: Path):
        """No plugin should import RealVibeKernel directly.

        WHITELIST (test infrastructure):
        - test_orchestration/: Test fixtures that genuinely need real kernels
        """
        plugins_dir = vibe_core_path / "plugins"
        if not plugins_dir.exists():
            pytest.skip("plugins directory not found")

        # Whitelist test infrastructure
        test_infra_dirs = {"test_orchestration"}
        results = scan_directory_for_mayavad(plugins_dir, exclude_dirs=test_infra_dirs)

        if results["total_mayavad"] > 0:
            mayavad_report = "\n".join(
                f"  - {f['path']}: {f['count']} imports (lines: {f['lines']})"
                for f in results["mayavad_files"][:10]  # Show top 10
            )
            pytest.fail(
                f"MAYAVAD in plugins: {results['total_mayavad']} direct RealVibeKernel imports\n"
                f"Should use KernelProtocol instead.\n{mayavad_report}"
            )

    def test_protocols_no_direct_kernel_imports(self, vibe_core_path: Path):
        """Protocols should never import RealVibeKernel.

        WHITELIST (intentional factory/test patterns):
        - om.py: The singularity factory that creates kernels
        - testable*.py: Test infrastructure files
        """
        protocols_dir = vibe_core_path / "protocols"
        if not protocols_dir.exists():
            pytest.skip("protocols directory not found")

        # Whitelist factory patterns
        factory_whitelist = {"om.py", "testable.py", "testable_registry.py"}
        results = scan_directory_for_mayavad(protocols_dir, exclude_files=factory_whitelist)

        if results["total_mayavad"] > 0:
            mayavad_report = "\n".join(f"  - {f['path']}: {f['count']} imports" for f in results["mayavad_files"])
            pytest.fail(
                f"CRITICAL: {results['total_mayavad']} MAYAVAD imports in protocols!\n"
                f"Protocols must NEVER import concrete implementations.\n{mayavad_report}"
            )

    # =========================================================================
    # POST 2: SCRIPTS - Legacy is Tolerated (For Now)
    # =========================================================================

    def test_scripts_mayavad_census(self, scripts_path: Path):
        """Census of MAYAVAD patterns in scripts (informational, not blocking)."""
        if not scripts_path.exists():
            pytest.skip("scripts directory not found")

        results = scan_directory_for_mayavad(scripts_path)

        print("\n" + "=" * 60)
        print("KURUKSHETRA CENSUS - Scripts Directory")
        print("=" * 60)
        print(f"MAYAVAD (legacy):    {results['total_mayavad']} imports")
        print(f"VAISHNAVA (unified): {results['total_vaishnava']} imports")
        if results["total_mayavad"] > 0:
            ratio = results["total_vaishnava"] / (results["total_mayavad"] + results["total_vaishnava"]) * 100
            print(f"Migration Progress:  {ratio:.1f}%")
        print("=" * 60)

        # This test always passes - it's for census
        assert True

    # =========================================================================
    # POST 3: TESTS - Mixed Allowed (Testing the Implementation)
    # =========================================================================

    def test_test_files_mayavad_allowed(self):
        """Test files MAY import RealVibeKernel for testing purposes."""
        # This is intentionally a pass - tests can use concrete types
        assert True, "Test files are allowed to use RealVibeKernel for integration testing"

    # =========================================================================
    # PROGRESS TRACKING
    # =========================================================================

    def test_churn_progress_report(self, vibe_core_path: Path):
        """Generate overall churn progress report."""
        if not vibe_core_path.exists():
            pytest.skip("vibe_core not found")

        results = scan_directory_for_mayavad(vibe_core_path)

        print("\n" + "=" * 60)
        print("SAMUDRA MANTHAN - CHURN PROGRESS REPORT")
        print("=" * 60)
        print(f"Total MAYAVAD imports:    {results['total_mayavad']}")
        print(f"Total VAISHNAVA imports:  {results['total_vaishnava']}")

        if results["mayavad_files"]:
            print("\nTop MAYAVAD Files:")
            sorted_files = sorted(results["mayavad_files"], key=lambda x: x["count"], reverse=True)
            for f in sorted_files[:5]:
                print(f"  - {f['path']}: {f['count']} imports")

        print("=" * 60)

        # This test always passes - it's for reporting
        assert True

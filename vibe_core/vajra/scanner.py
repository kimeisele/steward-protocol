"""
⚡ VAJRA Scanner - Static Analysis for Orphaned Components
==========================================================

Scans the codebase for components that implement inject_kernel()
but might not be receiving kernel injection.

Used in:
- CI pipelines (pre-commit, GitHub Actions)
- Development audits
- Documentation generation
"""

import ast
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

logger = logging.getLogger("VAJRA.Scanner")


@dataclass
class WirableComponent:
    """A component that implements WiringProtocol."""

    name: str
    file_path: str
    line_number: int
    has_inject_kernel: bool = False
    has_vibe_kernel_attr: bool = False
    has_get_ledger: bool = False
    wiring_status: str = "UNKNOWN"  # WIRED, ORPHAN, PARTIAL


@dataclass
class ScanResult:
    """Results of a VAJRA scan."""

    total_components: int = 0
    wired_components: int = 0
    orphaned_components: int = 0
    partial_components: int = 0
    components: List[WirableComponent] = field(default_factory=list)
    orphans: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def health_score(self) -> float:
        if self.total_components == 0:
            return 100.0
        return (self.wired_components / self.total_components) * 100

    def to_dict(self) -> dict:
        return {
            "total_components": self.total_components,
            "wired_components": self.wired_components,
            "orphaned_components": self.orphaned_components,
            "partial_components": self.partial_components,
            "health_score": round(self.health_score, 1),
            "orphans": self.orphans,
        }


class VAJRAScanner:
    """
    Static analyzer for VAJRA wiring compliance.

    Scans Python files for classes that:
    1. Have _vibe_kernel attribute
    2. Have inject_kernel() method
    3. Have _get_ledger() helper (optional but recommended)

    Then checks if these components are being wired somewhere.
    """

    # Directories to scan
    DEFAULT_SCAN_DIRS = [
        "vibe_core",
        "steward",
    ]

    # Known wiring locations (files that call inject_kernel)
    WIRING_LOCATIONS = [
        "kernel_impl.py",
        "intent_router.py",
        "cognitive_kernel.py",
        "kernel_tick.py",
        "cartridge_main.py",
    ]

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self._wirable_classes: Dict[str, WirableComponent] = {}
        self._wiring_calls: Set[str] = set()

    def scan(self, scan_dirs: Optional[List[str]] = None) -> ScanResult:
        """
        Scan for wirable components and their wiring status.

        Args:
            scan_dirs: Directories to scan (default: DEFAULT_SCAN_DIRS)

        Returns:
            ScanResult with component inventory and orphan list
        """
        scan_dirs = scan_dirs or self.DEFAULT_SCAN_DIRS
        result = ScanResult()

        # Phase 1: Find all wirable components
        for dir_name in scan_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    self._scan_file_for_wirables(py_file)
                except Exception as e:
                    result.errors.append(f"{py_file}: {e}")

        # Phase 2: Find all wiring calls (inject_kernel invocations)
        for dir_name in scan_dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue

            for py_file in dir_path.rglob("*.py"):
                try:
                    self._scan_file_for_wiring_calls(py_file)
                except Exception as e:
                    # OPUS-312: Log wiring scan failures
                    import logging

                    logging.getLogger("VAJRA").warning(f"Wiring scan failed for {py_file}: {e}")

        # Phase 3: Determine wiring status
        for name, component in self._wirable_classes.items():
            # Check if this component's inject_kernel is called somewhere
            is_wired = self._check_if_wired(name)

            if is_wired:
                component.wiring_status = "WIRED"
                result.wired_components += 1
            elif component.has_inject_kernel and component.has_vibe_kernel_attr:
                if component.has_get_ledger:
                    component.wiring_status = "ORPHAN"
                    result.orphaned_components += 1
                    result.orphans.append(f"{component.file_path}:{component.name}")
                else:
                    component.wiring_status = "PARTIAL"
                    result.partial_components += 1
            else:
                component.wiring_status = "PARTIAL"
                result.partial_components += 1

            result.components.append(component)

        result.total_components = len(self._wirable_classes)

        logger.info(
            f"⚡ VAJRA Scan: {result.wired_components}/{result.total_components} wired "
            f"({result.health_score:.1f}%), {result.orphaned_components} orphans"
        )

        if result.orphans:
            logger.warning(f"⚡ ORPHANED COMPONENTS: {', '.join(result.orphans)}")

        return result

    def _scan_file_for_wirables(self, file_path: Path) -> None:
        """Scan a file for classes implementing WiringProtocol."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return

        rel_path = str(file_path.relative_to(self.project_root))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                component = WirableComponent(
                    name=node.name,
                    file_path=rel_path,
                    line_number=node.lineno,
                )

                # Check class body for wiring artifacts
                for item in node.body:
                    # Check for _vibe_kernel = None
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "_vibe_kernel":
                                component.has_vibe_kernel_attr = True

                    # Check for inject_kernel method
                    if isinstance(item, ast.FunctionDef):
                        if item.name == "inject_kernel":
                            component.has_inject_kernel = True
                        if item.name == "_get_ledger":
                            component.has_get_ledger = True

                    # Check for annotated assignment: _vibe_kernel: Optional[...]
                    if isinstance(item, ast.AnnAssign):
                        if isinstance(item.target, ast.Name) and item.target.id == "_vibe_kernel":
                            component.has_vibe_kernel_attr = True

                # Only track if it looks wirable
                if component.has_inject_kernel or component.has_vibe_kernel_attr:
                    self._wirable_classes[node.name] = component

    def _scan_file_for_wiring_calls(self, file_path: Path) -> None:
        """Scan a file for inject_kernel() calls."""
        try:
            content = file_path.read_text()
        except Exception:
            return

        # Pattern: something.inject_kernel(
        pattern = r"(\w+)\.inject_kernel\s*\("
        for match in re.finditer(pattern, content):
            # Track the variable name being wired
            self._wiring_calls.add(match.group(1))

        # Also track class names from: ComponentClass().inject_kernel or self._component.inject_kernel
        pattern2 = r"self\.(_?\w+)\.inject_kernel\s*\("
        for match in re.finditer(pattern2, content):
            attr_name = match.group(1)
            self._wiring_calls.add(attr_name)

    def _check_if_wired(self, class_name: str) -> bool:
        """Check if a class is likely being wired somewhere."""
        # Direct wiring calls
        if class_name.lower() in [c.lower() for c in self._wiring_calls]:
            return True

        # Common patterns: _validator, _manas, _router, etc.
        common_patterns = [
            f"_{class_name.lower()}",
            class_name.lower(),
            f"self.{class_name.lower()}",
        ]

        for pattern in common_patterns:
            if any(pattern in call.lower() for call in self._wiring_calls):
                return True

        return False


def scan_for_orphans(
    project_root: Optional[Path] = None,
    scan_dirs: Optional[List[str]] = None,
    fail_on_orphans: bool = False,
) -> ScanResult:
    """
    Convenience function to scan for orphaned components.

    Args:
        project_root: Root of the project
        scan_dirs: Directories to scan
        fail_on_orphans: If True, raise exception when orphans found

    Returns:
        ScanResult

    Raises:
        RuntimeError: If fail_on_orphans=True and orphans exist
    """
    scanner = VAJRAScanner(project_root)
    result = scanner.scan(scan_dirs)

    if fail_on_orphans and result.orphans:
        raise RuntimeError(f"⚡ VAJRA: Found {len(result.orphans)} orphaned components: {', '.join(result.orphans)}")

    return result


# CLI entry point
def main():
    """Run VAJRA scanner from command line."""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="⚡ VAJRA Scanner - Find orphaned components")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--strict", action="store_true", help="Exit with error if orphans found")
    parser.add_argument("--dirs", nargs="+", help="Directories to scan")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )

    try:
        result = scan_for_orphans(
            scan_dirs=args.dirs,
            fail_on_orphans=args.strict,
        )

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print("\n⚡ VAJRA SCAN RESULTS")
            print("=" * 40)
            print(f"Total Components: {result.total_components}")
            print(f"Wired: {result.wired_components} ✅")
            print(f"Orphaned: {result.orphaned_components} ❌")
            print(f"Partial: {result.partial_components} ⚠️")
            print(f"Health Score: {result.health_score:.1f}%")

            if result.orphans:
                print("\n❌ ORPHANED COMPONENTS:")
                for orphan in result.orphans:
                    print(f"   - {orphan}")

        exit(1 if result.orphans and args.strict else 0)

    except RuntimeError as e:
        print(str(e))
        exit(1)


if __name__ == "__main__":
    main()

"""
OPUS-159: Compliance Bureau

GAD-000 Turing Test: Can an AI operate this module?

The 7-Point DNA:
1. Discoverability - manifest.json exists and valid
2. Observability - status/state queryable
3. Parseability - errors are structured
4. Composability - follows interface contracts
5. Idempotency - safe to retry
6. Documentation - AI-readable
7. Identity - signatures (future: GAD-1000)
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from .types import ComplianceCheck, ComplianceReport, ModuleType

logger = logging.getLogger("GENESIS.COMPLIANCE")


class ComplianceBureau:
    """
    GAD-000 Compliance Bureau.

    Audits modules for AI-operability.
    Returns detailed reports on what's missing.
    """

    # Required files per module type
    REQUIRED_FILES: Dict[ModuleType, List[str]] = {
        ModuleType.PLUGIN: ["__init__.py", "manifest.json", "plugin_main.py"],
        ModuleType.CARTRIDGE: ["__init__.py", "cartridge_main.py", "cartridge.yaml", "steward.json"],
        ModuleType.SECTION: ["manifest.json"],
        ModuleType.ANALYZER: [],  # Just needs to inherit BaseAnalyzer
        ModuleType.SENSE: [],  # Just needs to inherit BaseSense
        ModuleType.ACTION: [],  # Just needs to inherit BaseAction
        ModuleType.KNOWLEDGE: ["manifest.json"],
        ModuleType.CIRCUIT: [],  # YAML file with circuit: section
        ModuleType.TOOL: ["__init__.py"],
    }

    # Optional but recommended files
    RECOMMENDED_FILES: Dict[ModuleType, List[str]] = {
        ModuleType.PLUGIN: ["README.md"],
        ModuleType.CARTRIDGE: ["STEWARD.md", "tools/__init__.py"],
        ModuleType.SECTION: ["schema.json", "defaults.yaml"],
    }

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize the Compliance Bureau."""
        self._workspace = workspace or Path.cwd()

    def audit(self, path: Path, module_type: Optional[ModuleType] = None) -> ComplianceReport:
        """
        Run full GAD-000 compliance audit.

        Args:
            path: Path to the module
            module_type: Type of module (auto-detected if not provided)

        Returns:
            ComplianceReport with all checks
        """
        if not path.exists():
            report = ComplianceReport(path=path, module_type=module_type or ModuleType.UNKNOWN)
            report.add_check("exists", False, "Path does not exist", "error")
            return report

        # Auto-detect type if not provided
        if module_type is None:
            module_type = self._detect_type(path)

        report = ComplianceReport(path=path, module_type=module_type)

        # Check 1: Required files (Discoverability)
        self._check_required_files(path, module_type, report)

        # Check 2: Manifest validity (Discoverability)
        self._check_manifest(path, module_type, report)

        # Check 3: Entry point exists (Composability)
        self._check_entry_point(path, module_type, report)

        # Check 4: Recommended files (Documentation)
        self._check_recommended_files(path, module_type, report)

        # Check 5: Architectural Standards (Dharma)
        self._check_standards(path, module_type, report)

        # Check 6: No obvious issues (Parseability)
        self._check_code_quality(path, module_type, report)

        return report

    def _check_standards(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Check for violations of architectural standards (Todsünden)."""
        if module_type not in [
            ModuleType.PLUGIN,
            ModuleType.CARTRIDGE,
            ModuleType.TOOL,
            ModuleType.ACTION,
            ModuleType.SENSE,
        ]:
            return

        # Find all Python files in the module
        for py_file in path.glob("**/*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text()

                # TODSÜNDE #2: Ghost State (Raw Writes)
                # Simple check for open(..., 'w') or 'a'
                if "open(" in content and (
                    '"w"' in content or "'w'" in content or '"a"' in content or "'a'" in content
                ):
                    report.add_check(
                        f"standards:unsafe_io:{py_file.name}",
                        False,
                        f"Raw write detected in {py_file.name}. Use self.system.write_file instead.",
                        "error",
                    )

                # TODSÜNDE #1: Silent Failures
                if "except Exception: pass" in content or "except: pass" in content:
                    report.add_check(
                        f"standards:silent_failure:{py_file.name}",
                        False,
                        f"Silent failure (except: pass) detected in {py_file.name}.",
                        "warning",
                    )
            except Exception as e:
                logger.debug(f"Could not scan standards for {py_file}: {e}")

    def quick_check(self, path: Path, module_type: Optional[ModuleType] = None) -> bool:
        """
        Fast check: Does minimum infrastructure exist?

        Returns True if all required files exist.
        """
        if not path.exists():
            return False

        if module_type is None:
            module_type = self._detect_type(path)

        required = self.REQUIRED_FILES.get(module_type, [])
        for filename in required:
            if not (path / filename).exists():
                return False
        return True

    def get_missing(self, path: Path, module_type: ModuleType) -> List[str]:
        """
        What infrastructure is missing?

        Returns list of missing required files.
        """
        missing = []
        required = self.REQUIRED_FILES.get(module_type, [])

        for filename in required:
            if not (path / filename).exists():
                missing.append(filename)

        return missing

    def _detect_type(self, path: Path) -> ModuleType:
        """Auto-detect module type from path."""
        path_str = str(path)

        if "plugins" in path_str:
            return ModuleType.PLUGIN
        if "cartridges" in path_str:
            return ModuleType.CARTRIDGE
        if "phoenix/sections" in path_str:
            return ModuleType.SECTION
        if "analyzers" in path_str:
            return ModuleType.ANALYZER
        if "_sense.py" in path_str:
            return ModuleType.SENSE
        if "_action.py" in path_str:
            return ModuleType.ACTION
        if "knowledge" in path_str:
            return ModuleType.KNOWLEDGE
        if "circuits" in path_str:
            return ModuleType.CIRCUIT
        if "tools" in path_str:
            return ModuleType.TOOL

        return ModuleType.UNKNOWN

    def _check_required_files(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Check for required files."""
        required = self.REQUIRED_FILES.get(module_type, [])

        for filename in required:
            exists = (path / filename).exists()
            report.add_check(
                f"file:{filename}",
                exists,
                f"{'Found' if exists else 'Missing'}: {filename}",
                "error" if not exists else "info",
            )

    def _check_manifest(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Check manifest.json validity."""
        manifest_path = path / "manifest.json"

        if not manifest_path.exists():
            return  # Already checked in required files

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            # Check required fields
            required_fields = ["type", "id", "name", "version"]
            for field in required_fields:
                if field in manifest:
                    report.add_check(
                        f"manifest:{field}",
                        True,
                        f"Manifest has {field}",
                        "info",
                    )
                else:
                    report.add_check(
                        f"manifest:{field}",
                        False,
                        f"Manifest missing {field}",
                        "warning",
                    )

        except json.JSONDecodeError as e:
            report.add_check(
                "manifest:valid",
                False,
                f"Invalid JSON: {e}",
                "error",
            )

    def _check_entry_point(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Check entry point exists and is importable."""
        entry_points = {
            ModuleType.PLUGIN: "plugin_main.py",
            ModuleType.CARTRIDGE: "cartridge_main.py",
        }

        entry_file = entry_points.get(module_type)
        if not entry_file:
            return

        entry_path = path / entry_file
        if entry_path.exists():
            # Check for class definition
            content = entry_path.read_text()
            has_class = "class " in content
            report.add_check(
                "entry_point:class",
                has_class,
                f"Entry point {'has' if has_class else 'missing'} class definition",
                "warning" if not has_class else "info",
            )

    def _check_recommended_files(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Check for recommended files."""
        recommended = self.RECOMMENDED_FILES.get(module_type, [])

        for filename in recommended:
            exists = (path / filename).exists()
            report.add_check(
                f"recommended:{filename}",
                exists,
                f"{'Found' if exists else 'Missing'} (recommended): {filename}",
                "info",
            )

    def _check_code_quality(self, path: Path, module_type: ModuleType, report: ComplianceReport) -> None:
        """Basic code quality checks."""
        # Check for __init__.py in Python modules
        if module_type in [ModuleType.PLUGIN, ModuleType.CARTRIDGE, ModuleType.TOOL]:
            init_path = path / "__init__.py"
            if init_path.exists():
                content = init_path.read_text()
                has_all = "__all__" in content
                report.add_check(
                    "quality:__all__",
                    has_all,
                    f"__init__.py {'has' if has_all else 'missing'} __all__ export",
                    "info",
                )

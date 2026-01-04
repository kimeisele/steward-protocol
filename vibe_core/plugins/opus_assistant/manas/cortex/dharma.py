"""
OPUS-048: DHARMA (Das kosmische Gesetz) - Architectural Drift Detection.

Sanskrit: Dharma = The cosmic law, duty, order that prevents chaos.

This module transforms MANAS from observer to judge:
1. Reads the "Constitution" (architecture docs)
2. Scans the "Reality" (filesystem)
3. Detects "Outlaws" (undocumented code)
4. Proposes "Constitutional Amendments" (legalization)

Architecture:
    ArchitectureSpec → What SHOULD exist (docs)
         ↓
    FilesystemScanner → What DOES exist (reality)
         ↓
    DharmaAuditor.audit() → Compare spec vs reality
         ↓
    DriftReport → List of violations
         ↓
    ProposalGenerator → CAPs (Constitutional Amendment Proposals)

"Code that runs but is not documented is an outlaw."
"Outlaws can be legalized through proper governance."
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("MANAS.Cortex.Dharma")


# =============================================================================
# DATA MODELS
# =============================================================================


@dataclass
class ArchitecturalViolation:
    """A single architectural violation (drift)."""

    violation_type: str  # "undocumented_module", "missing_module", "pattern_violation"
    path: str  # File/directory path
    description: str
    severity: str  # "low", "medium", "high", "critical"
    suggested_action: str  # What to do about it
    can_auto_fix: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.violation_type,
            "path": self.path,
            "description": self.description,
            "severity": self.severity,
            "suggested_action": self.suggested_action,
            "can_auto_fix": self.can_auto_fix,
        }


@dataclass
class DriftReport:
    """Complete drift analysis report."""

    generated_at: str
    total_violations: int
    violations: List[ArchitecturalViolation]
    documented_modules: int
    actual_modules: int
    compliance_score: float  # 0-100%

    # Breakdown by severity
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "total_violations": self.total_violations,
            "documented_modules": self.documented_modules,
            "actual_modules": self.actual_modules,
            "compliance_score": self.compliance_score,
            "severity_breakdown": {
                "critical": self.critical,
                "high": self.high,
                "medium": self.medium,
                "low": self.low,
            },
            "violations": [v.to_dict() for v in self.violations],
        }

    def summary(self) -> str:
        """Human-readable summary."""
        if self.total_violations == 0:
            return "✅ Keine Architektur-Verstöße gefunden. Das System ist gesetzestreu."

        return (
            f"⚠️ **{self.total_violations} Architektur-Verstöße gefunden**\n"
            f"- Kritisch: {self.critical}\n"
            f"- Hoch: {self.high}\n"
            f"- Mittel: {self.medium}\n"
            f"- Niedrig: {self.low}\n\n"
            f"Compliance Score: {self.compliance_score:.1f}%"
        )


@dataclass
class ConstitutionalAmendmentProposal:
    """A proposal to legalize an outlaw module."""

    proposal_id: str
    title: str
    description: str
    affected_paths: List[str]
    proposed_changes: List[str]  # Documentation changes
    created_at: str
    status: str = "pending"  # pending, approved, rejected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "affected_paths": self.affected_paths,
            "proposed_changes": self.proposed_changes,
            "created_at": self.created_at,
            "status": self.status,
        }


# =============================================================================
# ARCHITECTURE SPEC - What SHOULD exist
# =============================================================================


class ArchitectureSpec:
    """
    Reads and parses architecture documentation to understand
    what modules are "legal" in the system.
    """

    # Known legal top-level directories
    LEGAL_TOP_LEVEL = {
        "vibe_core",
        "tests",
        "scripts",
        "docs",
        "config",
        "data",
        "gateway",
        "knowledge",
        ".opus_state",
        ".vibe",
        ".git",
        ".github",
        ".venv",
        "__pycache__",
    }

    # Known legal plugin names (can be extended from docs)
    LEGAL_PLUGINS = {
        "agent_city",
        "doctor",
        "envoy",
        "interface",
        "lifecycle",
        "nexus_holon",
        "opus_assistant",
        "plugin_template",
        "runtime_extensions",
        "sarga_cycle",
        "steward_protocol",
        "test_mode",
        "test_orchestration",
        "tools",
        "vedic_governance",
    }

    # Known legal cartridge categories
    LEGAL_CARTRIDGE_CATEGORIES = {"system", "agent_city"}

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._documented_modules: Set[str] = set()
        self._scan_documentation()

    def _scan_documentation(self) -> None:
        """Scan architecture docs to find documented modules."""
        docs_dir = self._workspace / "docs" / "architecture"
        if not docs_dir.exists():
            return

        # Scan all .md files for module references
        for md_file in docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                # Extract module references like vibe_core/xxx or plugins/xxx
                modules = re.findall(r"vibe_core/(\w+)", content)
                self._documented_modules.update(modules)

                # Extract plugin references
                plugins = re.findall(r"plugins/(\w+)", content)
                self._documented_modules.update(plugins)
            except Exception:
                pass

        logger.debug(f"Found {len(self._documented_modules)} documented modules")

    def is_legal_plugin(self, name: str) -> bool:
        """Check if a plugin name is legal."""
        return name in self.LEGAL_PLUGINS or name in self._documented_modules

    def is_legal_top_level(self, name: str) -> bool:
        """Check if a top-level directory is legal."""
        return name in self.LEGAL_TOP_LEVEL or name.startswith(".")

    def get_documented_modules(self) -> Set[str]:
        """Get all documented module names."""
        return self._documented_modules.copy()


# =============================================================================
# FILESYSTEM SCANNER - What DOES exist
# =============================================================================


class FilesystemScanner:
    """Scans the actual filesystem to find what exists."""

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()

    def scan_plugins(self) -> List[str]:
        """Get list of actual plugin directories."""
        plugins_dir = self._workspace / "vibe_core" / "plugins"
        if not plugins_dir.exists():
            return []

        return [d.name for d in plugins_dir.iterdir() if d.is_dir() and not d.name.startswith("_")]

    def scan_top_level(self) -> List[str]:
        """Get list of top-level directories."""
        return [d.name for d in self._workspace.iterdir() if d.is_dir() and not d.name.startswith(".")]

    def scan_cartridges(self) -> Dict[str, List[str]]:
        """Get cartridges by category."""
        result = {}
        cartridges_dir = self._workspace / "vibe_core" / "cartridges"

        if not cartridges_dir.exists():
            return result

        for category in cartridges_dir.iterdir():
            if not category.is_dir() or category.name.startswith("_"):
                continue

            agents = [d.name for d in category.iterdir() if d.is_dir() and not d.name.startswith("_")]
            result[category.name] = agents

        return result

    def find_orphan_python_files(self) -> List[str]:
        """Find Python files that aren't part of any package."""
        orphans = []

        # Check root-level .py files
        for py_file in self._workspace.glob("*.py"):
            if py_file.name not in {
                "setup.py",
                "conftest.py",
                "boot.py",
                "run_server.py",
            }:
                orphans.append(str(py_file.relative_to(self._workspace)))

        return orphans


# =============================================================================
# DHARMA AUDITOR - The Constitutional Court
# =============================================================================


class DharmaAuditor:
    """
    The Constitutional Court of Code.

    Compares the law (architecture spec) with reality (filesystem)
    and reports violations.
    """

    def __init__(self, workspace: Optional[Path] = None):
        self._workspace = workspace or Path.cwd()
        self._spec = ArchitectureSpec(workspace=workspace)
        self._scanner = FilesystemScanner(workspace=workspace)

    def audit(self) -> DriftReport:
        """
        Perform full architectural audit.

        Returns:
            DriftReport with all violations found
        """
        logger.info("⚖️ DHARMA: Beginning architectural audit...")

        violations = []

        # Check plugins
        violations.extend(self._audit_plugins())

        # Check top-level directories
        violations.extend(self._audit_top_level())

        # Check for orphan files
        violations.extend(self._audit_orphans())

        # Check cartridge structure
        violations.extend(self._audit_cartridges())

        # Calculate compliance score
        actual_plugins = len(self._scanner.scan_plugins())
        legal_plugins = len([v for v in violations if v.violation_type != "undocumented_module"])
        documented = len(self._spec.get_documented_modules())

        if actual_plugins > 0:
            compliance = max(
                0, (actual_plugins - len([v for v in violations if "plugin" in v.path])) / actual_plugins * 100
            )
        else:
            compliance = 100.0

        # Count by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for v in violations:
            if v.severity in severity_counts:
                severity_counts[v.severity] += 1

        report = DriftReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_violations=len(violations),
            violations=violations,
            documented_modules=documented,
            actual_modules=actual_plugins,
            compliance_score=compliance,
            critical=severity_counts["critical"],
            high=severity_counts["high"],
            medium=severity_counts["medium"],
            low=severity_counts["low"],
        )

        logger.info(f"⚖️ DHARMA: Audit complete - {len(violations)} violations found")
        return report

    def _audit_plugins(self) -> List[ArchitecturalViolation]:
        """Audit plugin directory for undocumented modules."""
        violations = []
        actual_plugins = self._scanner.scan_plugins()

        for plugin in actual_plugins:
            if not self._spec.is_legal_plugin(plugin):
                violations.append(
                    ArchitecturalViolation(
                        violation_type="undocumented_module",
                        path=f"vibe_core/plugins/{plugin}",
                        description=f"Plugin '{plugin}' existiert, ist aber nicht in der Architektur dokumentiert.",
                        severity="medium",
                        suggested_action=f"Dokumentiere '{plugin}' in docs/architecture/ oder entferne es.",
                        can_auto_fix=True,
                    )
                )

        return violations

    def _audit_top_level(self) -> List[ArchitecturalViolation]:
        """Audit top-level directories."""
        violations = []
        actual_dirs = self._scanner.scan_top_level()

        for dirname in actual_dirs:
            if not self._spec.is_legal_top_level(dirname):
                violations.append(
                    ArchitecturalViolation(
                        violation_type="undocumented_directory",
                        path=dirname,
                        description=f"Verzeichnis '{dirname}' ist nicht in der Architektur vorgesehen.",
                        severity="low",
                        suggested_action=f"Prüfe ob '{dirname}' notwendig ist oder entferne es.",
                        can_auto_fix=False,
                    )
                )

        return violations

    def _audit_orphans(self) -> List[ArchitecturalViolation]:
        """Check for orphan Python files."""
        violations = []
        orphans = self._scanner.find_orphan_python_files()

        for orphan in orphans:
            violations.append(
                ArchitecturalViolation(
                    violation_type="orphan_file",
                    path=orphan,
                    description=f"Python-Datei '{orphan}' gehört zu keinem Paket.",
                    severity="low",
                    suggested_action="Verschiebe die Datei in ein geeignetes Modul oder entferne sie.",
                    can_auto_fix=False,
                )
            )

        return violations

    def _audit_cartridges(self) -> List[ArchitecturalViolation]:
        """Audit cartridge structure."""
        violations = []
        cartridges = self._scanner.scan_cartridges()

        for category, agents in cartridges.items():
            if category not in self._spec.LEGAL_CARTRIDGE_CATEGORIES:
                violations.append(
                    ArchitecturalViolation(
                        violation_type="undocumented_category",
                        path=f"vibe_core/cartridges/{category}",
                        description=f"Cartridge-Kategorie '{category}' ist nicht dokumentiert.",
                        severity="medium",
                        suggested_action=f"Dokumentiere die Kategorie '{category}' oder verschiebe Agents.",
                        can_auto_fix=True,
                    )
                )

            # Check each agent has a manifest
            for agent in agents:
                manifest_path = self._workspace / "vibe_core" / "cartridges" / category / agent / "steward.json"
                if not manifest_path.exists():
                    violations.append(
                        ArchitecturalViolation(
                            violation_type="missing_manifest",
                            path=f"vibe_core/cartridges/{category}/{agent}",
                            description=f"Agent '{agent}' hat kein steward.json Manifest.",
                            severity="high",
                            suggested_action="Erstelle ein steward.json Manifest für diesen Agent.",
                            can_auto_fix=True,
                        )
                    )

        return violations

    def check_architectural_drift(self) -> str:
        """
        Quick drift check for KRIYA integration.

        Returns:
            Human-readable summary of drift status
        """
        report = self.audit()
        return report.summary()

    def generate_proposal(self, violations: List[ArchitecturalViolation]) -> Optional[ConstitutionalAmendmentProposal]:
        """
        Generate a Constitutional Amendment Proposal to legalize violations.

        Args:
            violations: List of violations to legalize

        Returns:
            CAP if violations can be auto-fixed
        """
        if not violations:
            return None

        fixable = [v for v in violations if v.can_auto_fix]
        if not fixable:
            return None

        proposal_id = f"CAP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        affected_paths = [v.path for v in fixable]

        proposed_changes = []
        for v in fixable:
            if v.violation_type == "undocumented_module":
                # Suggest adding to architecture docs
                module_name = v.path.split("/")[-1]
                proposed_changes.append(f"Füge '{module_name}' zu docs/architecture/ARCHITECTURE.md hinzu")
            elif v.violation_type == "missing_manifest":
                proposed_changes.append(f"Generiere steward.json für {v.path}")

        return ConstitutionalAmendmentProposal(
            proposal_id=proposal_id,
            title=f"Legalisierung von {len(fixable)} undokumentierten Modulen",
            description="Dieser Antrag fügt fehlende Dokumentation hinzu und legalisiert existierenden Code.",
            affected_paths=affected_paths,
            proposed_changes=proposed_changes,
            created_at=datetime.now(timezone.utc).isoformat(),
        )


# =============================================================================
# KRIYA INTEGRATION - Chat to Audit Bridge
# =============================================================================


def check_drift_for_chat() -> str:
    """
    Quick function for KRIYA integration.

    Usage in JnanaHandler:
        if "architektur" in message or "drift" in message:
            return check_drift_for_chat()
    """
    auditor = DharmaAuditor()
    report = auditor.audit()

    if report.total_violations == 0:
        return (
            "✅ **Architektur-Audit bestanden**\n\n"
            f"Das System ist gesetzestreu.\n"
            f"- Dokumentierte Module: {report.documented_modules}\n"
            f"- Tatsächliche Module: {report.actual_modules}\n"
            f"- Compliance Score: {report.compliance_score:.1f}%"
        )

    # Build violation summary
    violation_list = []
    for v in report.violations[:5]:  # Show first 5
        emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(v.severity, "⚪")
        violation_list.append(f"{emoji} `{v.path}`: {v.description[:50]}...")

    response = f"⚠️ **Architektur-Drift erkannt!**\n\n**{report.total_violations} Verstöße gefunden:**\n" + "\n".join(
        violation_list
    )

    if report.total_violations > 5:
        response += f"\n... und {report.total_violations - 5} weitere"

    response += f"\n\n**Compliance Score:** {report.compliance_score:.1f}%"

    # Check if we can propose fixes
    fixable = [v for v in report.violations if v.can_auto_fix]
    if fixable:
        response += f"\n\n💡 {len(fixable)} Verstöße können automatisch legalisiert werden.\nSag 'Legalisiere die Architektur-Verstöße' um einen Antrag zu erstellen."

    return response

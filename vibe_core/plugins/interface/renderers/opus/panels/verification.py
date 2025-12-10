"""
OPUS-000: SYSTEM VERIFICATION PANEL
====================================

The Master Verificator - Cross-references OPUS architecture docs with code reality.
Produces a trust score based on what EXISTS vs what's DOCUMENTED vs what's WIRED.

This is OPUS-000: The single source of truth for system integrity.

Philosophy:
    "Documentation without verification is fiction."
"""

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from . import BasePanel

if TYPE_CHECKING:
    pass


class VerificationPanel(BasePanel):
    """
    OPUS-000: System Verification Panel.

    Cross-references:
    - OPUS docs (docs/architecture/OPUS/*.md)
    - Code files (what exists)
    - Imports/wiring (what's actually used)
    - Tests (what's covered)

    Produces a trust score: 0-100%
    """

    @property
    def panel_id(self) -> str:
        return "verification"

    @property
    def title(self) -> str:
        return "System Verification (OPUS-000)"

    @property
    def priority(self) -> int:
        return 1  # First panel - most critical

    def render(self) -> str:
        """Render verification report."""
        # Check cache first
        cached = self.get_cached("verification_report")
        if cached is not None:
            return cached

        report = self._run_verification()
        content = self._format_report(report)

        self.set_cached("verification_report", content)
        return content

    def _run_verification(self) -> Dict[str, Any]:
        """Run full system verification."""
        report = {
            "opus_docs": self._verify_opus_docs(),
            "critical_components": self._verify_critical_components(),
            "wiring": self._verify_wiring(),
            "containers": self._verify_containers(),
            "trust_score": 0,
        }

        # Calculate trust score
        report["trust_score"] = self._calculate_trust_score(report)

        return report

    def _verify_opus_docs(self) -> List[Dict[str, Any]]:
        """Verify each OPUS doc exists and has corresponding implementation."""
        opus_path = self._root / "docs/architecture/OPUS"
        results = []

        # Expected OPUS docs with their code references
        opus_mapping = {
            "001-KERNEL-EXTRACTION.md": {
                "code": "vibe_core/kernel_impl.py",
                "critical": True,
            },
            "002-PHOENIX-CONFIG.md": {
                "code": "vibe_core/phoenix/config.py",
                "critical": True,
            },
            "009-UNIFIED-STATE-PRAKRITI.md": {
                "code": "vibe_core/state/prakriti.py",
                "critical": True,
            },
            "010-VERIFICATION-PROTOCOL.md": {
                "code": "vibe_core/plugins/steward_protocol/plugin_main.py",
                "critical": True,
            },
            "011-LAYERED-ROUTER.md": {
                "code": "vibe_core/runtime/layered_router.py",
                "critical": False,
            },
            "015-CONTAINER-FORMAT.md": {
                "code": "vibe_core/loaders/container_loader.py",
                "critical": True,
            },
        }

        for doc_name, meta in opus_mapping.items():
            doc_path = opus_path / doc_name
            code_path = self._root / meta["code"]

            result = {
                "doc": doc_name,
                "doc_exists": doc_path.exists(),
                "code_file": meta["code"],
                "code_exists": code_path.exists(),
                "critical": meta["critical"],
                "status": "unknown",
            }

            if result["doc_exists"] and result["code_exists"]:
                result["status"] = "verified"
            elif result["doc_exists"] and not result["code_exists"]:
                result["status"] = "doc_only"  # Planned but not implemented
            elif not result["doc_exists"] and result["code_exists"]:
                result["status"] = "undocumented"  # Code without spec
            else:
                result["status"] = "missing"

            results.append(result)

        return results

    def _verify_critical_components(self) -> List[Dict[str, Any]]:
        """Verify critical components exist, are wired, and have tests."""
        components = [
            {
                "name": "Kernel",
                "code": "vibe_core/kernel_impl.py",
                "wired_in": None,  # Entrypoint
                "test_pattern": "tests/**/test_kernel*.py",
            },
            {
                "name": "Ledger (Hash Chain)",
                "code": "vibe_core/ledger.py",
                "wired_in": "vibe_core/kernel_impl.py",
                "wired_pattern": r"from \.ledger import",
                "test_pattern": "tests/**/test_ledger*.py",
            },
            {
                "name": "Prakriti State",
                "code": "vibe_core/state/prakriti.py",
                "wired_in": "vibe_core/kernel_impl.py",
                "wired_pattern": r"from vibe_core\.state import Prakriti",
                "test_pattern": "tests/**/test_prakriti*.py",
            },
            {
                "name": "InvariantChecker",
                "code": "vibe_core/governance/invariants.py",
                "wired_in": "vibe_core/kernel_impl.py",
                "wired_pattern": r"from.*invariants import|InvariantChecker",
                "test_pattern": "tests/**/test_invariant*.py",
            },
            {
                "name": "ContainerMounter",
                "code": "vibe_core/loaders/container_loader.py",
                "wired_in": "vibe_core/steward/agent_loader.py",
                "wired_pattern": r"ContainerMounter",
                "test_pattern": "tests/**/test_container*.py",
            },
            {
                "name": "StewardProtocol Plugin",
                "code": "vibe_core/plugins/steward_protocol/plugin_main.py",
                "wired_in": None,  # Auto-discovered plugin
                "test_pattern": "tests/**/test_steward*.py",
            },
            {
                "name": "VedicGovernance Plugin",
                "code": "vibe_core/plugins/vedic_governance/plugin_main.py",
                "wired_in": None,  # Auto-discovered plugin
                "test_pattern": "tests/**/test_vedic*.py",
            },
        ]

        results = []
        for comp in components:
            code_path = self._root / comp["code"]
            result = {
                "name": comp["name"],
                "code": comp["code"],
                "exists": code_path.exists(),
                "wired": None,
                "tested": False,
            }

            # Check wiring
            if comp.get("wired_in") and comp.get("wired_pattern"):
                wired_path = self._root / comp["wired_in"]
                if wired_path.exists():
                    content = wired_path.read_text()
                    result["wired"] = bool(re.search(comp["wired_pattern"], content))
                else:
                    result["wired"] = False
            elif comp.get("wired_in") is None:
                result["wired"] = True  # Auto-discovered or entrypoint

            # Check tests
            test_files = list(self._root.glob(comp["test_pattern"]))
            result["tested"] = len(test_files) > 0
            result["test_count"] = len(test_files)

            results.append(result)

        return results

    def _verify_wiring(self) -> Dict[str, Any]:
        """Verify critical wiring points."""
        kernel_path = self._root / "vibe_core/kernel_impl.py"
        if not kernel_path.exists():
            return {"error": "kernel_impl.py not found"}

        kernel_content = kernel_path.read_text()

        wiring_checks = {
            "prakriti_injected": r"self\.prakriti\s*=\s*Prakriti",
            "ledger_initialized": r"self\._ledger\s*=\s*(SQLiteLedger|InMemoryLedger)",
            "plugins_booted": r"plugin\.on_boot\(self\)",
            "governance_hooks": r"on_task_pre_assign|on_agent_pre_register",
            "capability_registry": r"self\._capability_registry\s*=",
            "invariant_checker": r"InvariantChecker|invariant.*check",  # This will likely fail
        }

        results = {}
        for name, pattern in wiring_checks.items():
            results[name] = bool(re.search(pattern, kernel_content))

        return results

    def _verify_containers(self) -> Dict[str, Any]:
        """Verify container format implementation status."""
        container_loader = self._root / "vibe_core/loaders/container_loader.py"

        result = {
            "loader_exists": container_loader.exists(),
            "crypto_implemented": False,
            "hollows_supported": False,
            "signature_verified": False,
        }

        if container_loader.exists():
            content = container_loader.read_text()

            # Check for TODO indicating incomplete implementation
            result["crypto_implemented"] = "TODO" not in content or "Implement real crypto" not in content
            result["hollows_supported"] = "hollows" in content.lower()
            result["signature_verified"] = "verify_signature" in content and "TODO" not in content

        return result

    def _calculate_trust_score(self, report: Dict[str, Any]) -> int:
        """Calculate overall trust score 0-100."""
        score = 0
        max_score = 0

        # OPUS docs verification (20 points)
        for doc in report["opus_docs"]:
            max_score += 20 if doc["critical"] else 10
            if doc["status"] == "verified":
                score += 20 if doc["critical"] else 10
            elif doc["status"] == "doc_only":
                score += 5  # Planned but not implemented

        # Critical components (40 points)
        for comp in report["critical_components"]:
            max_score += 10
            if comp["exists"]:
                score += 4
            if comp["wired"]:
                score += 3
            if comp["tested"]:
                score += 3

        # Wiring checks (20 points)
        wiring = report["wiring"]
        if isinstance(wiring, dict) and "error" not in wiring:
            for key, wired in wiring.items():
                max_score += 4
                if wired:
                    score += 4

        # Container format (20 points)
        containers = report["containers"]
        max_score += 20
        if containers["loader_exists"]:
            score += 5
        if containers["crypto_implemented"]:
            score += 5
        if containers["hollows_supported"]:
            score += 5
        if containers["signature_verified"]:
            score += 5

        return int((score / max_score) * 100) if max_score > 0 else 0

    def _format_report(self, report: Dict[str, Any]) -> str:
        """Format verification report as markdown."""
        lines = [f"## {self.title}", ""]

        # Trust Score Banner
        score = report["trust_score"]
        if score >= 80:
            badge = "🟢"
        elif score >= 60:
            badge = "🟡"
        else:
            badge = "🔴"

        lines.append(f"**Trust Score: {badge} {score}%**")
        lines.append("")

        # OPUS Docs Status
        lines.append("### OPUS Docs ↔ Code")
        lines.append("")
        lines.append("| Doc | Code | Status |")
        lines.append("|-----|------|--------|")

        for doc in report["opus_docs"]:
            status_icon = {
                "verified": "✅",
                "doc_only": "📝",
                "undocumented": "⚠️",
                "missing": "❌",
            }.get(doc["status"], "?")

            critical = "🔴" if doc["critical"] else ""
            lines.append(f"| {critical}{doc['doc'][:20]} | {doc['code_file'].split('/')[-1]} | {status_icon} {doc['status']} |")

        lines.append("")

        # Critical Components
        lines.append("### Critical Components")
        lines.append("")
        lines.append("| Component | Exists | Wired | Tested |")
        lines.append("|-----------|--------|-------|--------|")

        for comp in report["critical_components"]:
            exists = "✅" if comp["exists"] else "❌"
            wired = "✅" if comp["wired"] else ("❌" if comp["wired"] is False else "➖")
            tested = f"✅ ({comp.get('test_count', 0)})" if comp["tested"] else "❌"
            lines.append(f"| {comp['name']} | {exists} | {wired} | {tested} |")

        lines.append("")

        # Wiring Status
        wiring = report["wiring"]
        if isinstance(wiring, dict) and "error" not in wiring:
            lines.append("### Kernel Wiring")
            lines.append("")
            for key, is_wired in wiring.items():
                icon = "✅" if is_wired else "❌"
                lines.append(f"- {icon} `{key}`")
            lines.append("")

        # Container Format
        containers = report["containers"]
        lines.append("### Container Format (OPUS-015)")
        lines.append("")
        lines.append(f"- {'✅' if containers['loader_exists'] else '❌'} Loader exists")
        lines.append(f"- {'✅' if containers['crypto_implemented'] else '❌'} Crypto verification")
        lines.append(f"- {'✅' if containers['hollows_supported'] else '❌'} Hollows support")
        lines.append(f"- {'✅' if containers['signature_verified'] else '❌'} Signature verification")

        return "\n".join(lines)

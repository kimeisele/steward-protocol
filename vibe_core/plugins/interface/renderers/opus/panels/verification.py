"""
OPUS-000: SYSTEM VERIFICATION PANEL
====================================

UI layer for OPUS verification. Logic lives in opus_assistant plugin.

OPUS-029: "The Split" - Logic extracted to opus_assistant/core/verification_logic.py
This panel is now a thin UI wrapper that:
1. Loads config
2. Calls VerificationEngine
3. Formats output as markdown

Philosophy:
    "Documents that cannot verify themselves are fiction."
"""

from typing import TYPE_CHECKING, Any, Dict

import yaml

# OPUS-029: Import logic from opus_assistant plugin
from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

from . import BasePanel

if TYPE_CHECKING:
    pass


class VerificationPanel(BasePanel):
    """
    OPUS-000: System Verification Panel.

    Reads @HARNESS sections from each OPUS doc and verifies against code reality.
    Configuration from config/opus.yaml.

    OPUS-029: Logic delegated to VerificationEngine.
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

    def _load_config(self) -> Dict[str, Any]:
        """Load verification config from opus.yaml."""
        config_path = self._root / "config" / "opus.yaml"
        try:
            if config_path.exists():
                data = yaml.safe_load(config_path.read_text())
                return data.get("verification", {})
        except Exception:
            pass
        return {}

    def render(self) -> str:
        """Render verification report."""
        cached = self.get_cached("verification_report")
        if cached is not None:
            return cached

        config = self._load_config()
        if not config.get("enabled", True):
            return f"## {self.title}\n\n_Verification disabled in config/opus.yaml_"

        # OPUS-029: Delegate to VerificationEngine
        engine = VerificationEngine(workspace_root=self._root, config=config)
        report = engine.run_verification()

        content = self._format_report(report, config)

        self.set_cached("verification_report", content)
        return content

    def _format_report(self, report: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format verification report as markdown (UI only)."""
        lines = [f"## {self.title}", ""]

        if "error" in report:
            lines.append(f"**Error:** {report['error']}")
            return "\n".join(lines)

        # Summary
        total = report.get("total_score", 0)
        thresholds = config.get("thresholds", {})
        pass_threshold = thresholds.get("pass", 80)
        warn_threshold = thresholds.get("warn", 60)

        if total >= pass_threshold:
            badge = "🟢"
        elif total >= warn_threshold:
            badge = "🟡"
        else:
            badge = "🔴"

        with_harness = report.get("docs_with_harness", 0)
        without_harness = report.get("docs_without_harness", 0)

        lines.append(
            f"**Trust Score: {badge} {total}%** ({with_harness} docs verified, {without_harness} without @HARNESS)"
        )
        lines.append("")

        # Per-doc status
        lines.append("### OPUS Docs")
        lines.append("")
        lines.append("| Doc | Score | Files | Tests | Wiring | Absent | Config | Semantic |")
        lines.append("|-----|-------|-------|-------|--------|--------|--------|----------|")

        for doc in report.get("docs", []):
            name = doc["name"][:25]
            if doc.get("has_harness"):
                score = doc.get("score", 0)
                checks = doc.get("checks", {})

                files_ok = "✅" if checks.get("files", {}).get("passed") else "❌"
                tests_ok = "✅" if checks.get("tests", {}).get("passed") else "❌"
                wiring_ok = "✅" if checks.get("wiring", {}).get("passed") else "❌"
                absent_ok = "✅" if checks.get("absent", {}).get("passed", True) else "🚨"
                config_ok = "✅" if checks.get("config", {}).get("passed") else "❌"

                # OPUS-026: Semantic check status
                semantic_check = checks.get("semantic", {})
                if semantic_check.get("details") in ("No semantic checks specified", "Skipped (quick mode)"):
                    semantic_ok = "⚪"  # No semantic checks defined or skipped
                elif semantic_check.get("passed"):
                    semantic_ok = "✅"
                elif semantic_check.get("checks_skipped"):
                    semantic_ok = "⏭️"  # Skipped (timeout etc)
                else:
                    semantic_ok = "❌"

                lines.append(
                    f"| {name} | {score}% | {files_ok} | {tests_ok} | {wiring_ok} | {absent_ok} | {config_ok} | {semantic_ok} |"
                )
            else:
                lines.append(f"| {name} | - | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ |")

        lines.append("")

        # Show failures and violations
        failures = []
        violations = []
        semantic_failures = []
        for doc in report.get("docs", []):
            if not doc.get("has_harness"):
                continue
            for check_name, check_result in doc.get("checks", {}).items():
                if not check_result.get("passed", True):
                    # Missing items (files, tests, wiring)
                    for item in check_result.get("missing", []):
                        failures.append(f"**{doc['name']}** [{check_name}]: {item}")
                    # Violations (absent patterns found)
                    for item in check_result.get("violations", []):
                        violations.append(f"**{doc['name']}** 🚨 {item}")
                    # OPUS-026: Semantic failures
                    for item in check_result.get("checks_failed", []):
                        semantic_failures.append(f"**{doc['name']}** [semantic]: {item}")

        if violations:
            lines.append("### 🚨 Violations (forbidden patterns found)")
            lines.append("")
            for v in violations[:10]:
                lines.append(f"- {v}")
            if len(violations) > 10:
                lines.append(f"- _...and {len(violations) - 10} more_")
            lines.append("")

        if failures:
            lines.append("### ❌ Failures")
            lines.append("")
            for f in failures[:10]:
                lines.append(f"- {f}")
            if len(failures) > 10:
                lines.append(f"- _...and {len(failures) - 10} more_")
            lines.append("")

        # OPUS-026: Show semantic failures separately
        if semantic_failures:
            lines.append("### 🧪 Semantic Failures (code execution failed)")
            lines.append("")
            for sf in semantic_failures[:10]:
                lines.append(f"- {sf}")
            if len(semantic_failures) > 10:
                lines.append(f"- _...and {len(semantic_failures) - 10} more_")

        return "\n".join(lines)

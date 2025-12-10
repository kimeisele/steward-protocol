"""
OPUS-000: SYSTEM VERIFICATION PANEL
====================================

Cross-references OPUS architecture docs with code reality using @HARNESS sections.

Architecture:
- Each OPUS doc defines its own @HARNESS section (YAML in HTML comment)
- This panel reads ALL OPUS docs, extracts harnesses, verifies against code
- Configuration lives in config/opus.yaml (verification section)
- NO HARDCODED MAPPINGS - self-describing documents

@HARNESS Format (in OPUS docs):
    <!-- @HARNESS
    files:
      - path: vibe_core/some_file.py
        required: true
    tests:
      - tests/unit/test_something.py
    wiring:
      - pattern: "SomeClass"
        in: vibe_core/kernel_impl.py
    config:
      - section: phoenix.some_section
    -->

Philosophy:
    "Documents that cannot verify themselves are fiction."
"""

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

from . import BasePanel

if TYPE_CHECKING:
    pass


class VerificationPanel(BasePanel):
    """
    OPUS-000: System Verification Panel.

    Reads @HARNESS sections from each OPUS doc and verifies against code reality.
    Configuration from config/opus.yaml.
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

        report = self._run_verification(config)
        content = self._format_report(report, config)

        self.set_cached("verification_report", content)
        return content

    def _run_verification(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run verification for all OPUS docs with @HARNESS sections."""
        docs_path = self._root / config.get("docs_path", "docs/architecture/OPUS")
        harness_marker = config.get("harness_marker", "@HARNESS")

        results = {
            "docs": [],
            "total_score": 0,
            "docs_with_harness": 0,
            "docs_without_harness": 0,
        }

        if not docs_path.exists():
            results["error"] = f"OPUS docs path not found: {docs_path}"
            return results

        # Process each OPUS markdown file
        for md_file in sorted(docs_path.glob("*.md")):
            if md_file.name.startswith("_"):
                continue

            doc_result = self._verify_doc(md_file, harness_marker, config)
            results["docs"].append(doc_result)

            if doc_result.get("has_harness"):
                results["docs_with_harness"] += 1
                results["total_score"] += doc_result.get("score", 0)
            else:
                results["docs_without_harness"] += 1

        # Calculate average score
        if results["docs_with_harness"] > 0:
            results["total_score"] = results["total_score"] // results["docs_with_harness"]

        return results

    def _verify_doc(self, md_file: Path, harness_marker: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a single OPUS doc against its @HARNESS section."""
        result = {
            "name": md_file.name,
            "has_harness": False,
            "score": 0,
            "checks": {},
        }

        try:
            content = md_file.read_text()
        except Exception as e:
            result["error"] = str(e)
            return result

        # Extract @HARNESS section
        harness = self._extract_harness(content, harness_marker)
        if not harness:
            return result

        result["has_harness"] = True
        weights = config.get("weights", {})

        # Verify files exist
        files_check = self._verify_files(harness.get("files", []))
        result["checks"]["files"] = files_check
        if files_check["passed"]:
            result["score"] += weights.get("files_exist", 30)

        # Verify tests exist
        tests_check = self._verify_tests(harness.get("tests", []))
        result["checks"]["tests"] = tests_check
        if tests_check["passed"]:
            result["score"] += weights.get("tests_exist", 25)

        # Verify wiring patterns
        wiring_check = self._verify_wiring(harness.get("wiring", []))
        result["checks"]["wiring"] = wiring_check
        if wiring_check["passed"]:
            result["score"] += weights.get("wiring_verified", 25)

        # Verify absent patterns (things that MUST NOT exist)
        absent_check = self._verify_absent(harness.get("absent", []))
        result["checks"]["absent"] = absent_check
        if not absent_check["passed"]:
            # Penalty for having forbidden patterns
            result["score"] = max(0, result["score"] - 20)

        # Verify config sections
        config_check = self._verify_config(harness.get("config", []))
        result["checks"]["config"] = config_check
        if config_check["passed"]:
            result["score"] += weights.get("config_exists", 10)

        # Verify doc completeness
        required_sections = config.get("required_sections", [])
        doc_check = self._verify_doc_sections(content, required_sections)
        result["checks"]["doc"] = doc_check
        if doc_check["passed"]:
            result["score"] += weights.get("doc_complete", 10)

        return result

    def _extract_harness(self, content: str, marker: str) -> Optional[Dict[str, Any]]:
        """Extract @HARNESS YAML from markdown content."""
        # Pattern: <!-- @HARNESS ... -->
        pattern = rf"<!--\s*{re.escape(marker)}\s*\n(.*?)\n\s*-->"
        match = re.search(pattern, content, re.DOTALL)

        if not match:
            return None

        try:
            harness_yaml = match.group(1)
            return yaml.safe_load(harness_yaml)
        except Exception:
            return None

    def _verify_files(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that required files exist."""
        if not files:
            return {"passed": True, "details": "No files specified"}

        missing = []
        found = []

        for file_spec in files:
            if isinstance(file_spec, str):
                path = file_spec
                required = True
            else:
                path = file_spec.get("path", "")
                required = file_spec.get("required", True)

            full_path = self._root / path
            if full_path.exists():
                found.append(path)
            elif required:
                missing.append(path)

        return {
            "passed": len(missing) == 0,
            "found": found,
            "missing": missing,
        }

    def _verify_tests(self, tests: List[Any]) -> Dict[str, Any]:
        """Verify that test files exist."""
        if not tests:
            return {"passed": True, "details": "No tests specified"}

        missing = []
        found = []

        for test_item in tests:
            # Handle both string patterns and dicts (if accidentally used like files)
            test_pattern = test_item
            if isinstance(test_item, dict):
                test_pattern = test_item.get("path", "")

            if not isinstance(test_pattern, str) or not test_pattern:
                missing.append(f"Invalid test pattern: {test_item}")
                continue

            try:
                # Support glob patterns
                matches = list(self._root.glob(test_pattern))
                if matches:
                    found.extend([str(m.relative_to(self._root)) for m in matches])
                else:
                    missing.append(test_pattern)
            except Exception as e:
                missing.append(f"Error checking {test_pattern}: {e}")

        return {
            "passed": len(missing) == 0,
            "found": found,
            "missing": missing,
        }

    def _verify_wiring(self, wirings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that wiring patterns are present in target files."""
        if not wirings:
            return {"passed": True, "details": "No wiring specified"}

        missing = []
        found = []

        for wiring in wirings:
            pattern = wiring.get("pattern", "")
            target_file = wiring.get("in", "")

            if not pattern or not target_file:
                continue

            target_path = self._root / target_file
            if not target_path.exists():
                missing.append(f"{pattern} in {target_file} (file not found)")
                continue

            try:
                content = target_path.read_text()
                if re.search(pattern, content):
                    found.append(f"{pattern} in {target_file}")
                else:
                    missing.append(f"{pattern} in {target_file}")
            except Exception:
                missing.append(f"{pattern} in {target_file} (read error)")

        return {
            "passed": len(missing) == 0,
            "found": found,
            "missing": missing,
        }

    def _verify_absent(self, absents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that forbidden patterns are NOT present (catches lies/stubs)."""
        if not absents:
            return {"passed": True, "details": "No absent patterns specified"}

        violations = []
        clean = []

        for absent in absents:
            pattern = absent.get("pattern", "")
            target_file = absent.get("in", "")

            if not pattern or not target_file:
                continue

            target_path = self._root / target_file
            if not target_path.exists():
                clean.append(f"{pattern} in {target_file} (file not found)")
                continue

            try:
                content = target_path.read_text()
                matches = list(re.finditer(pattern, content))
                if matches:
                    for match in matches:
                        line_num = content[: match.start()].count("\n") + 1
                        violations.append(f"{target_file}:{line_num} matches '{pattern}'")
                else:
                    clean.append(f"{pattern} in {target_file}")
            except Exception:
                clean.append(f"{pattern} in {target_file} (read error)")

        return {
            "passed": len(violations) == 0,
            "clean": clean,
            "violations": violations,
        }

    def _verify_config(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify that Phoenix config sections exist."""
        if not configs:
            return {"passed": True, "details": "No config specified"}

        missing = []
        found = []

        for config_spec in configs:
            if isinstance(config_spec, str):
                section = config_spec
            else:
                section = config_spec.get("section", "")

            if not section:
                continue

            # Parse section path (e.g., "phoenix.containers" -> config/phoenix.yaml, key "containers")
            parts = section.split(".")
            if len(parts) < 2:
                continue

            config_file = self._root / "config" / f"{parts[0]}.yaml"
            if not config_file.exists():
                missing.append(section)
                continue

            try:
                data = yaml.safe_load(config_file.read_text())
                # Navigate to nested key
                current = data
                key_exists = True
                for part in parts[1:]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        key_exists = False
                        break

                if key_exists:
                    found.append(section)
                else:
                    missing.append(section)
            except Exception:
                missing.append(section)

        return {
            "passed": len(missing) == 0,
            "found": found,
            "missing": missing,
        }

    def _verify_doc_sections(self, content: str, required_sections: List[str]) -> Dict[str, Any]:
        """Verify that required markdown sections exist in doc."""
        if not required_sections:
            return {"passed": True, "details": "No sections required"}

        missing = []
        found = []

        for section in required_sections:
            if section in content:
                found.append(section)
            else:
                missing.append(section)

        return {
            "passed": len(missing) == 0,
            "found": found,
            "missing": missing,
        }

    def _format_report(self, report: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Format verification report as markdown."""
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
        lines.append("| Doc | Score | Files | Tests | Wiring | Absent | Config |")
        lines.append("|-----|-------|-------|-------|--------|--------|--------|")

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

                lines.append(
                    f"| {name} | {score}% | {files_ok} | {tests_ok} | {wiring_ok} | {absent_ok} | {config_ok} |"
                )
            else:
                lines.append(f"| {name} | - | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ |")

        lines.append("")

        # Show failures and violations
        failures = []
        violations = []
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

        return "\n".join(lines)

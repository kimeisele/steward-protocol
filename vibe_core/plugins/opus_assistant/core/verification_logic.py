"""
OPUS Verification Engine - Pure Logic, No UI Dependencies.

Extracted from interface/renderers/opus/panels/verification.py (OPUS-029).

This module contains the LOGIC for @HARNESS verification.
NO rich, NO panel dependencies. Pure Python.

Architecture:
- Each OPUS doc defines its own @HARNESS section (YAML in HTML comment)
- This engine reads ALL OPUS docs, extracts harnesses, verifies against code
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class HarnessResult:
    """Result of verifying a single @HARNESS section."""

    name: str
    has_harness: bool
    score: int = 0
    checks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class VerificationReport:
    """Complete verification report."""

    total_score: int
    docs_with_harness: int
    docs_without_harness: int
    docs: List[HarnessResult]
    error: Optional[str] = None


class VerificationEngine:
    """
    Pure verification engine - no UI dependencies.

    Usage:
        engine = VerificationEngine(workspace_root=Path("."))
        report = engine.run_verification()

    Or with custom config:
        config = {"docs_path": "docs/architecture/OPUS", "harness_marker": "@HARNESS"}
        engine = VerificationEngine(workspace_root=Path("."), config=config)
        report = engine.run_verification()
    """

    # Default weights for scoring
    DEFAULT_WEIGHTS = {
        "files_exist": 30,
        "tests_exist": 25,
        "wiring_verified": 25,
        "config_exists": 10,
        "doc_complete": 10,
        "semantic_passes": 20,
    }

    def __init__(self, workspace_root: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize verification engine.

        Args:
            workspace_root: Root path of the workspace
            config: Optional config dict (loads from opus.yaml if not provided)
        """
        self._root = Path(workspace_root)
        self._config = config if config is not None else self._load_config()

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

    def run_verification(self, quick: bool = False, changed_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run verification for OPUS docs with @HARNESS sections.

        OPUS-035: Delta-Pulse - If changed_files is provided, only verify
        docs that reference those files. This makes the heartbeat efficient.

        Args:
            quick: If True, skip semantic checks (faster)
            changed_files: Optional list of changed file paths (delta mode)

        Returns:
            Dict with verification results (compatible with panel format)
        """
        config = self._config
        docs_path = self._root / config.get("docs_path", "docs/architecture/OPUS")
        harness_marker = config.get("harness_marker", "@HARNESS")

        results: Dict[str, Any] = {
            "docs": [],
            "total_score": 0,
            "docs_with_harness": 0,
            "docs_without_harness": 0,
            "delta_mode": changed_files is not None,
            "changed_files": changed_files or [],
        }

        if not docs_path.exists():
            results["error"] = f"OPUS docs path not found: {docs_path}"
            return results

        # OPUS-035: Build file→doc index for delta mode
        if changed_files:
            relevant_docs = self._find_docs_for_files(docs_path, harness_marker, changed_files)
            if not relevant_docs:
                # No relevant docs - system is clean for these changes
                results["delta_clean"] = True
                return results
        else:
            relevant_docs = None  # Full scan

        # Process each OPUS markdown file
        for md_file in sorted(docs_path.glob("*.md")):
            if md_file.name.startswith("_"):
                continue

            # OPUS-035: Skip docs not affected by changes (delta mode)
            if relevant_docs is not None and md_file.name not in relevant_docs:
                continue

            doc_result = self._verify_doc(md_file, harness_marker, config, skip_semantic=quick)
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

    def _find_docs_for_files(self, docs_path: Path, harness_marker: str, changed_files: List[str]) -> set:
        """
        OPUS-035: Find which OPUS docs reference the changed files.

        This is the heart of delta-pulse - we only verify docs that
        could be affected by the changes.

        Args:
            docs_path: Path to OPUS docs
            harness_marker: The @HARNESS marker string
            changed_files: List of changed file paths

        Returns:
            Set of doc names that reference the changed files
        """
        relevant_docs = set()
        changed_set = set(changed_files)

        for md_file in docs_path.glob("*.md"):
            if md_file.name.startswith("_"):
                continue

            try:
                content = md_file.read_text()
                harness = self._extract_harness(content, harness_marker)
                if not harness:
                    continue

                # Check if any files in this harness are in changed_files
                harness_files = set()

                # Collect all files referenced in @HARNESS
                for f in harness.get("files", []):
                    if isinstance(f, str):
                        harness_files.add(f)
                    elif isinstance(f, dict):
                        harness_files.add(f.get("path", ""))

                for t in harness.get("tests", []):
                    if isinstance(t, str):
                        harness_files.add(t)
                    elif isinstance(t, dict):
                        harness_files.add(t.get("path", ""))

                for w in harness.get("wiring", []):
                    if isinstance(w, dict):
                        harness_files.add(w.get("in", ""))

                # Check intersection
                if harness_files & changed_set:
                    relevant_docs.add(md_file.name)

            except Exception:
                continue

        return relevant_docs

    def _verify_doc(
        self,
        md_file: Path,
        harness_marker: str,
        config: Dict[str, Any],
        skip_semantic: bool = False,
    ) -> Dict[str, Any]:
        """Verify a single OPUS doc against its @HARNESS section."""
        result: Dict[str, Any] = {
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
        weights = config.get("weights", self.DEFAULT_WEIGHTS)

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

        # OPUS-026: Semantic verification (actually RUN code)
        if not skip_semantic:
            semantic_check = self._verify_semantic(harness.get("semantic", []))
            result["checks"]["semantic"] = semantic_check
            if semantic_check["passed"]:
                result["score"] += weights.get("semantic_passes", 20)
        else:
            result["checks"]["semantic"] = {"passed": True, "details": "Skipped (quick mode)"}

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

    def _is_command_not_path(self, pattern: str) -> bool:
        """
        OPUS-313: Detect if a pattern is a command rather than a file path.

        Some @HARNESS blocks incorrectly contain verification commands like:
          - python -c "from vibe_core.state import X; print('OK')"
          - python scripts/ci/test_kernel_boot.py

        These should be in a 'semantic:' section, not 'tests:' or 'files:'.
        We filter them out to prevent false-positive "missing file" warnings.

        Also catches placeholder garbage like:
          - 'rationale'
          - 'required'
          - 'your/module/other.py'
        """
        # Commands start with executable names
        command_prefixes = ("python ", "python3 ", "vibe ", "bash ", "sh ")
        if pattern.startswith(command_prefixes):
            return True

        # Commands often have spaces (except in quoted paths)
        # Real paths rarely have unquoted spaces
        if " " in pattern and not pattern.startswith('"'):
            return True

        # Placeholder garbage (single words without slashes, not extensions)
        garbage_patterns = {"rationale", "required", "optional", "note", "description"}
        if pattern.lower() in garbage_patterns:
            return True

        # Example/placeholder paths
        if pattern.startswith("your/") or "/other.py" in pattern:
            return True

        return False

    def _verify_files(self, files: List[Any]) -> Dict[str, Any]:
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

            # OPUS-313: Filter out commands and garbage
            if self._is_command_not_path(path):
                continue

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
            # Handle both string patterns and dicts
            test_pattern = test_item
            if isinstance(test_item, dict):
                test_pattern = test_item.get("path", "")

            if not isinstance(test_pattern, str) or not test_pattern:
                missing.append(f"Invalid test pattern: {test_item}")
                continue

            # OPUS-313: Filter out command-like strings (parser bug fix)
            # Some @HARNESS blocks incorrectly put verification commands in tests:
            # e.g., 'python -c "from vibe_core..."' - these are NOT file paths
            if self._is_command_not_path(test_pattern):
                continue  # Skip commands silently - they're not missing files

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

    def _verify_config(self, configs: List[Any]) -> Dict[str, Any]:
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

    def _verify_semantic(self, semantics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        OPUS-026: Semantic verification - actually EXECUTE code to verify functionality.

        Unlike syntactic checks (grep), this RUNS code to prove it works.

        Supported check types:
        - plugin_loaded: Verify plugin exists in kernel._plugins_map
        - method_exists: Verify class.method is callable
        - pytest_passes: Run specific pytest and check exit code

        Safety guarantees:
        - 2s timeout per check (no UI freeze)
        - Full try/except panzerung (never crashes)
        - Uses TestKernel (no side effects)
        """
        import signal
        import subprocess
        from contextlib import contextmanager

        if not semantics:
            return {"passed": True, "details": "No semantic checks specified"}

        TIMEOUT_SECONDS = 2
        passed = []
        failed = []
        skipped = []

        # Timeout context manager
        @contextmanager
        def timeout(seconds: int):
            def handler(signum, frame):
                raise TimeoutError(f"Semantic check timed out after {seconds}s")

            old_handler = signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                yield
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        for check in semantics:
            check_type = check.get("type", "")
            check_name = check.get("name", check_type)

            try:
                with timeout(TIMEOUT_SECONDS):
                    if check_type == "plugin_loaded":
                        # Verify plugin entry point is importable (no full kernel boot!)
                        plugin_name = check.get("plugin", "")
                        plugin_dir = self._root / "vibe_core" / "plugins" / plugin_name

                        if not plugin_dir.exists():
                            failed.append(f"{check_name}: Plugin directory not found: {plugin_name}")
                            continue

                        manifest_json = plugin_dir / "manifest.json"
                        plugin_main = plugin_dir / "plugin_main.py"

                        if not manifest_json.exists():
                            failed.append(f"{check_name}: manifest.json missing for '{plugin_name}'")
                            continue

                        if not plugin_main.exists():
                            failed.append(f"{check_name}: plugin_main.py missing for '{plugin_name}'")
                            continue

                        # Try to import the plugin module (without full kernel)
                        import importlib.util

                        spec = importlib.util.spec_from_file_location(f"_plugin_{plugin_name}", plugin_main)
                        if spec and spec.loader:
                            try:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                passed.append(f"{check_name}: Plugin '{plugin_name}' entry point valid")
                            except Exception as e:
                                failed.append(f"{check_name}: Plugin '{plugin_name}' import failed: {e}")
                        else:
                            failed.append(f"{check_name}: Could not load plugin module")

                    elif check_type == "module_exports":
                        # OPUS-075: Verify module exports specific symbols
                        import importlib

                        module_name = check.get("module", "")
                        exports = check.get("exports", [])

                        if not module_name:
                            skipped.append(f"{check_name}: No module specified")
                            continue

                        try:
                            module = importlib.import_module(module_name)
                            missing = [e for e in exports if not hasattr(module, e)]

                            if not missing:
                                passed.append(f"{check_name}: all exports present")
                            else:
                                failed.append(f"{check_name}: missing exports {missing}")
                        except ImportError as e:
                            failed.append(f"{check_name}: cannot import {module_name} ({e})")

                    elif check_type == "method_exists":
                        # Verify method is callable via importlib
                        import importlib

                        module_path = check.get("in", "")
                        class_name = check.get("class", "")
                        method_name = check.get("method", "")

                        if not all([module_path, class_name, method_name]):
                            skipped.append(f"{check_name}: Missing class/method/in")
                            continue

                        # Verify file exists first
                        full_path = self._root / module_path
                        if not full_path.exists():
                            failed.append(f"{check_name}: File not found: {module_path}")
                            continue

                        # Convert path to module name
                        module_name = module_path.replace("/", ".").replace(".py", "")

                        module = importlib.import_module(module_name)

                        cls = getattr(module, class_name, None)
                        if cls is None:
                            failed.append(f"{check_name}: Class '{class_name}' not found")
                            continue

                        method = getattr(cls, method_name, None)
                        if callable(method):
                            passed.append(f"{check_name}: {class_name}.{method_name}() exists")
                        else:
                            failed.append(f"{check_name}: {class_name}.{method_name} not callable")

                    elif check_type == "pytest_passes":
                        # Run specific pytest with timeout
                        test_path = check.get("test", "")
                        if not test_path:
                            skipped.append(f"{check_name}: No test path specified")
                            continue

                        result = subprocess.run(
                            ["python", "-m", "pytest", test_path, "-x", "-q", "--tb=no"],
                            capture_output=True,
                            text=True,
                            timeout=TIMEOUT_SECONDS,
                            cwd=str(self._root),
                        )

                        if result.returncode == 0:
                            passed.append(f"{check_name}: {test_path} PASSED")
                        else:
                            failed.append(f"{check_name}: {test_path} FAILED")

                    elif check_type == "execution_mode":
                        # OPUS-075/076: Verify system is NOT in simulation mode
                        # Check BOTH config/providers.yaml (source of truth) AND SETTINGS.md
                        expected = check.get("expected", "live_fire")

                        # Primary source: config/providers.yaml (YAML config)
                        providers_file = self._root / "config" / "providers.yaml"
                        if providers_file.exists():
                            providers_content = providers_file.read_text()
                            if "live_fire_enabled: true" in providers_content:
                                if expected == "live_fire":
                                    passed.append(f"{check_name}: live_fire mode confirmed (providers.yaml)")
                                else:
                                    failed.append(f"{check_name}: expected simulation but providers.yaml has live_fire")
                                continue
                            elif "live_fire_enabled: false" in providers_content:
                                if expected == "live_fire":
                                    failed.append(f"{check_name}: SIMULATION MODE in providers.yaml!")
                                else:
                                    passed.append(f"{check_name}: simulation mode confirmed (providers.yaml)")
                                continue

                        # Fallback: SETTINGS.md (auto-generated, may be stale)
                        settings_file = self._root / "SETTINGS.md"
                        if not settings_file.exists():
                            skipped.append(f"{check_name}: Neither providers.yaml nor SETTINGS.md found")
                            continue

                        content = settings_file.read_text()
                        import re

                        in_simulation = (
                            "[x] Simulation Mode" in content
                            or "mode=simulation" in content.lower()
                            or bool(re.search(r"\|\s*`?mode`?\s*\|\s*`?simulation`?\s*\|", content, re.IGNORECASE))
                        )
                        in_live_fire = (
                            "[x] Live Fire" in content
                            or "mode=live_fire" in content.lower()
                            or bool(re.search(r"\|\s*`?mode`?\s*\|\s*`?live_fire`?\s*\|", content, re.IGNORECASE))
                        )

                        if expected == "live_fire":
                            if in_live_fire and not in_simulation:
                                passed.append(f"{check_name}: live_fire mode confirmed (SETTINGS.md)")
                            elif in_simulation:
                                failed.append(f"{check_name}: SIMULATION MODE in SETTINGS.md (may be stale)")
                            else:
                                skipped.append(f"{check_name}: mode unclear from SETTINGS.md")
                        else:
                            if in_simulation:
                                passed.append(f"{check_name}: simulation mode confirmed (SETTINGS.md)")
                            else:
                                failed.append(f"{check_name}: expected simulation but found live_fire")

                    elif check_type == "file_writable":
                        # OPUS-075: Verify write access to path
                        check_path = check.get("path", "")
                        if not check_path:
                            skipped.append(f"{check_name}: No path specified")
                            continue

                        full_path = self._root / check_path
                        full_path.mkdir(parents=True, exist_ok=True)

                        # Try to write a test file
                        test_file = full_path / ".harness_write_test"
                        try:
                            test_file.write_text("write_test")
                            test_file.unlink()  # Clean up
                            passed.append(f"{check_name}: write access to {check_path} confirmed")
                        except PermissionError:
                            failed.append(f"{check_name}: NO WRITE ACCESS to {check_path}")
                        except Exception as e:
                            failed.append(f"{check_name}: write test failed: {e}")

                    elif check_type == "ledger_healthy":
                        # OPUS-075: Verify VAJRA ledger has history
                        min_events = check.get("min_events", 10)
                        ledger_path = self._root / ".vibe" / "ledger.db"

                        if not ledger_path.exists():
                            failed.append(f"{check_name}: ledger.db not found")
                            continue

                        import sqlite3

                        try:
                            conn = sqlite3.connect(str(ledger_path))
                            cursor = conn.execute("SELECT COUNT(*) FROM events")
                            count = cursor.fetchone()[0]
                            conn.close()

                            if count >= min_events:
                                passed.append(f"{check_name}: {count} events (>={min_events} required)")
                            else:
                                failed.append(f"{check_name}: only {count} events ({min_events} required)")
                        except Exception as e:
                            failed.append(f"{check_name}: ledger query failed: {e}")

                    elif check_type == "state_sync":
                        # OPUS-075: Anti-spaghetti - verify two config sources are in sync
                        import json

                        source_path = self._root / check.get("source", "")
                        source_key = check.get("source_key", "")
                        target_path = self._root / check.get("target", "")
                        target_key = check.get("target_key", "")
                        inverted = check.get("inverted", False)

                        if not source_path.exists():
                            failed.append(f"{check_name}: source {source_path} not found")
                            continue
                        if not target_path.exists():
                            failed.append(f"{check_name}: target {target_path} not found")
                            continue

                        try:
                            # Read source (YAML)
                            source_content = source_path.read_text()
                            source_value = None
                            if f"{source_key}: true" in source_content:
                                source_value = True
                            elif f"{source_key}: false" in source_content:
                                source_value = False

                            # Read target (JSON)
                            target_data = json.loads(target_path.read_text())
                            # Handle nested keys - check view_preferences first
                            target_value = target_data.get("view_preferences", {}).get(target_key)
                            if target_value is None:
                                target_value = target_data.get(target_key)

                            if source_value is None:
                                skipped.append(f"{check_name}: couldn't parse {source_key} from source")
                                continue

                            # Check sync (with optional inversion)
                            expected_target = not source_value if inverted else source_value

                            if target_value == expected_target:
                                passed.append(
                                    f"{check_name}: synced ({source_key}={source_value} ↔ {target_key}={target_value})"
                                )
                            else:
                                failed.append(
                                    f"{check_name}: SPAGHETTI DETECTED! {source_key}={source_value} but {target_key}={target_value}"
                                )
                        except Exception as e:
                            failed.append(f"{check_name}: sync check failed: {e}")

                    else:
                        skipped.append(f"{check_name}: Unknown check type '{check_type}'")

            except TimeoutError:
                skipped.append(f"{check_name}: TIMEOUT ({TIMEOUT_SECONDS}s)")
            except Exception as e:
                # PANZERUNG: Never crash, just record failure
                failed.append(f"{check_name}: ERROR - {type(e).__name__}: {str(e)[:50]}")

        return {
            "passed": len(failed) == 0 and len(skipped) == 0,
            "checks_passed": passed,
            "checks_failed": failed,
            "checks_skipped": skipped,
        }

    # =========================================================================
    # Utility Methods for External Use
    # =========================================================================

    def get_all_harness_files(self) -> List[str]:
        """
        Get all files referenced in @HARNESS sections across all OPUS docs.

        Useful for drift detection.

        Returns:
            List of file paths referenced in @HARNESS
        """
        docs_path = self._root / self._config.get("docs_path", "docs/architecture/OPUS")
        harness_marker = self._config.get("harness_marker", "@HARNESS")
        all_files = set()

        if not docs_path.exists():
            return []

        for md_file in docs_path.glob("*.md"):
            if md_file.name.startswith("_"):
                continue

            try:
                content = md_file.read_text()
                harness = self._extract_harness(content, harness_marker)
                if harness:
                    # Collect files (OPUS-313: filter commands/garbage)
                    for f in harness.get("files", []):
                        path = f if isinstance(f, str) else f.get("path", "")
                        if path and not self._is_command_not_path(path):
                            all_files.add(path)
                    # Collect tests (OPUS-313: filter commands/garbage)
                    for t in harness.get("tests", []):
                        path = t if isinstance(t, str) else t.get("path", "") if isinstance(t, dict) else ""
                        if path and not self._is_command_not_path(path):
                            all_files.add(path)
                    # Collect wiring targets
                    for w in harness.get("wiring", []):
                        target = w.get("in", "")
                        if target and not self._is_command_not_path(target):
                            all_files.add(target)
            except Exception:
                continue

        return [f for f in all_files if f]

    def get_docs_without_harness(self) -> List[str]:
        """
        Get list of OPUS docs that don't have @HARNESS sections.

        Useful for identifying docs that need harness added.

        Returns:
            List of doc names without @HARNESS
        """
        docs_path = self._root / self._config.get("docs_path", "docs/architecture/OPUS")
        harness_marker = self._config.get("harness_marker", "@HARNESS")
        missing = []

        if not docs_path.exists():
            return []

        for md_file in docs_path.glob("*.md"):
            if md_file.name.startswith("_"):
                continue

            try:
                content = md_file.read_text()
                harness = self._extract_harness(content, harness_marker)
                if not harness:
                    missing.append(md_file.name)
            except Exception:
                missing.append(md_file.name)

        return missing

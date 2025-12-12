"""
OPUS.md Writer - Standalone renderer for opus_assistant plugin.

OPUS-029 Migration: Replaces interface/renderers/opus/ with standalone writer.

Responsibilities:
1. Generate OPUS.md content (header, sections, footer)
2. Preserve @AI/@HUMAN sections (never overwrite)
3. Load config from config/opus.yaml
4. Collect data for all panels (verification, code_health, etc.)

Philosophy:
    "The plugin writes its own documentation. No external dependencies."
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class OpusMdWriter:
    """
    Writes OPUS.md directly from opus_assistant plugin.

    Usage:
        writer = OpusMdWriter(workspace_root=Path("."))
        writer.write()  # Generates OPUS.md
    """

    # Section markers for preservation
    LIVE_START = "<!-- @LIVE:"
    LIVE_END = "<!-- /@LIVE -->"
    AI_START = "<!-- @AI:"
    AI_END = "<!-- /@AI -->"
    HUMAN_START = "<!-- @HUMAN:"
    HUMAN_END = "<!-- /@HUMAN -->"

    def __init__(self, workspace_root: Path, kernel: Optional[Any] = None):
        """
        Initialize writer.

        Args:
            workspace_root: Project root directory
            kernel: Optional kernel instance for runtime data
        """
        self._root = Path(workspace_root)
        self._kernel = kernel
        self._opus_path = self._root / "OPUS.md"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config/opus.yaml."""
        config_path = self._root / "config" / "opus.yaml"
        try:
            if config_path.exists():
                return yaml.safe_load(config_path.read_text())
        except Exception:
            pass
        return {}

    def write(self, quick: bool = False) -> Path:
        """
        Generate and write OPUS.md.

        Args:
            quick: Skip expensive operations (semantic verification)

        Returns:
            Path to written OPUS.md
        """
        # Preserve existing sections
        preserved = self._extract_preserved_sections()

        # Generate content
        content = self._generate_content(quick=quick, preserved=preserved)

        # Write file
        self._opus_path.write_text(content)

        return self._opus_path

    def _generate_content(self, quick: bool = False, preserved: Optional[Dict[str, str]] = None) -> str:
        """Generate full OPUS.md content."""
        lines = []

        # Header with philosophy
        lines.append(self._render_header())

        # LIVE sections (generated dynamically)
        lines.append(self._render_state_of_mind())  # NEW: The "soul" of the system
        lines.append(self._render_system_journal())  # NEW: What the system observed
        lines.append(self._render_circuit_status())  # NEW: Cognitive circuits
        lines.append(self._render_verification(quick=quick))
        lines.append(self._render_architecture_plans())
        lines.append(self._render_prakriti_state())
        lines.append(self._render_code_health())
        lines.append(self._render_test_health())

        # Preserved sections
        lines.append(self._render_work_sections(preserved or {}))

        # Footer
        lines.append(self._render_footer())

        return "\n".join(lines)

    def _render_header(self) -> str:
        """Render minimal dynamic header - no stale content."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        kernel_status = "STOPPED"
        agent_count = 0
        if self._kernel:
            try:
                kernel_status = self._kernel.status.value
                agent_count = len(getattr(self._kernel, "_agents", {}))
            except Exception:
                pass

        # Dynamic status badge
        status_badge = "🟢 LIVE" if kernel_status == "RUNNING" else "⚪ OFFLINE"

        return f"""# OPUS - System State

**{status_badge}** | Updated: {timestamp} UTC | Kernel: {kernel_status} ({agent_count} agents)

---
"""

    def _render_state_of_mind(self) -> str:
        """
        Render the 🧠 State of Mind section.

        This is the "soul" of the system - what the agent is thinking.
        Synthesized from all three Prakriti layers.
        """
        lines = [f"{self.LIVE_START}state_of_mind -->"]
        lines.append("## 🧠 State of Mind")
        lines.append("")
        lines.append("*What the system knows right now (synthesized from Prakriti)*")
        lines.append("")

        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)

            # Layer 1: Sthula (Physical)
            lines.append("### Layer 1 - Sthula (Physical Reality)")
            lines.append("")
            try:
                git_status = prakriti.git.status()
                branch = git_status.get("branch", "unknown")
                sha = git_status.get("sha", "unknown")[:8]
                dirty = git_status.get("dirty", False)

                status_icon = "⚠️ Uncommitted" if dirty else "✅ Clean"
                lines.append(f"- **Branch:** `{branch}` @ `{sha}`")
                lines.append(f"- **Working Tree:** {status_icon}")

                # Show uncommitted files if dirty
                if dirty:
                    try:
                        dirty_files = prakriti.git.dirty_files() if hasattr(prakriti.git, "dirty_files") else []
                        if dirty_files:
                            lines.append(f"- **Uncommitted:** {', '.join(dirty_files[:5])}")
                            if len(dirty_files) > 5:
                                lines.append(f"  _...and {len(dirty_files) - 5} more_")
                    except Exception:
                        pass
            except Exception as e:
                lines.append(f"- ❌ Git unavailable: {e}")
            lines.append("")

            # Layer 2: Prana (Runtime)
            lines.append("### Layer 2 - Prana (Runtime Energy)")
            lines.append("")
            try:
                if self._kernel:
                    kernel_status = self._kernel.status.value
                    agent_count = len(getattr(self._kernel, "_agents", {}))
                    status_icon = "🟢 Running" if kernel_status == "RUNNING" else "⚪ Stopped"
                    lines.append(f"- **Kernel:** {status_icon}")
                    lines.append(f"- **Agents:** {agent_count} active")
                else:
                    lines.append("- **Kernel:** ⚪ Offline")
                    lines.append("- **Agents:** 0 active")

                # Session info
                session = getattr(prakriti, "session", None)
                if session:
                    lines.append(f"- **Session:** `{session.session_id[:12]}...`")
                else:
                    lines.append("- **Session:** Standalone")
            except Exception as e:
                lines.append(f"- ❌ Runtime unavailable: {e}")
            lines.append("")

            # Layer 3: Purusha (Identity)
            lines.append("### Layer 3 - Purusha (Cognitive Identity)")
            lines.append("")
            try:
                # Ephemeral thoughts
                thoughts = prakriti.ephemeral.get_thoughts() if hasattr(prakriti.ephemeral, "get_thoughts") else []
                thought_count = len(thoughts) if thoughts else 0
                lines.append(f"- **Ephemeral Thoughts:** {thought_count}")

                # Active persona
                try:
                    personas = prakriti.personas
                    active = personas.status().get("active_persona") if hasattr(personas, "status") else None
                    if active:
                        lines.append(f"- **Active Persona:** `{active}`")
                    else:
                        lines.append("- **Active Persona:** None")
                except Exception:
                    lines.append("- **Active Persona:** None")
            except Exception as e:
                lines.append(f"- ❌ Identity unavailable: {e}")
            lines.append("")

            # Focus Areas (what needs attention)
            lines.append("### 🎯 Focus Areas")
            lines.append("")
            focus_areas = []

            # Derive focus from state
            try:
                git_status = prakriti.git.status()
                if git_status.get("dirty"):
                    focus_areas.append("Commit pending changes")
            except Exception:
                pass

            # Check drift
            try:
                from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

                detector = DriftDetector(workspace_root=self._root)
                quick = detector.quick_check()
                if not quick.get("healthy", True):
                    focus_areas.append("Documentation drift detected")
            except Exception:
                pass

            if focus_areas:
                for area in focus_areas:
                    lines.append(f"- {area}")
            else:
                lines.append("- _System is healthy, no immediate focus needed_")

        except Exception as e:
            lines.append(f"_State of Mind synthesis failed: {e}_")

        lines.append("")
        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_system_journal(self) -> str:
        """
        Render the 📓 System Journal section.

        The observation log - what the system has noticed.
        Read from existing OPUS.md journal or ObservationLogger.
        """
        lines = [f"{self.LIVE_START}system_journal -->"]
        lines.append("## 📓 System Journal")
        lines.append("")
        lines.append("*Recent observations and insights from the system*")
        lines.append("")

        # Try to get observations from the ObservationLogger
        observations = []

        try:

            # If there's an existing OPUS.md, parse journal from it
            if self._opus_path.exists():
                content = self._opus_path.read_text()
                # Parse existing journal entries
                import re

                journal_pattern = re.compile(
                    r"- `(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})` ([^\s]+) \*\*\[([^\]]+)\]\*\* (.+)", re.MULTILINE
                )
                matches = journal_pattern.findall(content)
                for ts, icon, source, message in matches[:20]:
                    observations.append(
                        {"timestamp": ts, "severity": icon, "source": source, "message": message.strip()}
                    )
        except Exception:
            pass

        if observations:
            lines.append("| Time | Severity | Source | Message |")
            lines.append("|------|----------|--------|---------|")
            for obs in observations[:15]:  # Limit to 15 entries
                ts = obs["timestamp"][-8:]  # Just time portion
                lines.append(f"| `{ts}` | {obs['severity']} | {obs['source']} | {obs['message'][:50]} |")
            if len(observations) > 15:
                lines.append(f"| ... | ... | ... | _+{len(observations) - 15} more entries_ |")
        else:
            lines.append("_No observations recorded yet._")
            lines.append("")
            lines.append("The system will log observations here as it runs:")
            lines.append("- ℹ️ INFO: Normal operational events")
            lines.append("- ⚠️ WARN: Things to watch")
            lines.append("- 🚨 ALERT: Needs attention")
            lines.append("- 💡 INSIGHT: AI-generated insights")

        lines.append("")
        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_circuit_status(self) -> str:
        """
        Render the ⚡ Circuit Status section.

        Shows available cognitive circuits and their status.
        """
        lines = [f"{self.LIVE_START}circuit_status -->"]
        lines.append("## ⚡ Cognitive Circuits")
        lines.append("")
        lines.append("*Autonomous behavior patterns available to the system*")
        lines.append("")

        circuits = []
        circuits_dir = self._root / "vibe_core/plugins/opus_assistant/circuits"

        try:
            if circuits_dir.exists():
                for circuit_file in sorted(circuits_dir.glob("*.yaml")):
                    try:
                        content = circuit_file.read_text()
                        data = yaml.safe_load(content)
                        circuit = data.get("circuit", {})

                        circuit_id = circuit.get("id", circuit_file.stem)
                        name = circuit.get("name", circuit_id)
                        description = circuit.get("description", "")[:60]
                        triggers = circuit.get("triggers", [])

                        # Extract trigger types
                        trigger_events = []
                        for t in triggers:
                            event = t.get("event", "")
                            if event:
                                trigger_events.append(event)

                        circuits.append(
                            {
                                "id": circuit_id,
                                "name": name,
                                "description": description,
                                "triggers": trigger_events,
                                "states": len(circuit.get("states", {})),
                            }
                        )
                    except Exception:
                        circuits.append(
                            {
                                "id": circuit_file.stem,
                                "name": circuit_file.stem,
                                "description": "⚠️ Parse error",
                                "triggers": [],
                                "states": 0,
                            }
                        )

        except Exception as e:
            lines.append(f"_Circuit discovery failed: {e}_")
            lines.append(self.LIVE_END)
            return "\n".join(lines)

        if circuits:
            lines.append("| Circuit | Triggers | States | Description |")
            lines.append("|---------|----------|--------|-------------|")
            for c in circuits:
                triggers_str = ", ".join(c["triggers"][:3])
                if len(c["triggers"]) > 3:
                    triggers_str += "..."
                lines.append(f"| **{c['id']}** | `{triggers_str}` | {c['states']} | {c['description']} |")
            lines.append("")
            lines.append(f"**{len(circuits)} circuits** ready for autonomous execution")
        else:
            lines.append("_No circuits defined yet._")
            lines.append("")
            lines.append("Circuits enable autonomous agent behavior:")
            lines.append("- `OPUS_AUTO_VERIFY`: Triggered by GIT_COMMIT")
            lines.append("- `OPUS_AUTO_REFRESH`: Keeps OPUS.md fresh")
            lines.append("- `OPUS_AUTO_HEAL`: Self-healing on drift")

        lines.append("")
        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_verification(self, quick: bool = False) -> str:
        """Render verification panel."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import (
            VerificationEngine,
        )

        engine = VerificationEngine(workspace_root=self._root, config=self._config.get("verification", {}))
        report = engine.run_verification(quick=quick)

        lines = [f"{self.LIVE_START}verification -->"]
        lines.append("## System Verification (OPUS-000)")
        lines.append("")

        if "error" in report:
            lines.append(f"**Error:** {report['error']}")
            lines.append(self.LIVE_END)
            return "\n".join(lines)

        # Summary
        total = report.get("total_score", 0)
        thresholds = self._config.get("verification", {}).get("thresholds", {})
        pass_threshold = thresholds.get("pass", 80)
        warn_threshold = thresholds.get("warn", 60)

        badge = "🟢" if total >= pass_threshold else "🟡" if total >= warn_threshold else "🔴"

        with_harness = report.get("docs_with_harness", 0)
        without_harness = report.get("docs_without_harness", 0)

        lines.append(
            f"**Trust Score: {badge} {total}%** ({with_harness} docs verified, {without_harness} without @HARNESS)"
        )
        lines.append("")

        # Doc table
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

                semantic_check = checks.get("semantic", {})
                if semantic_check.get("details") in ("No semantic checks specified", "Skipped (quick mode)"):
                    semantic_ok = "⚪"
                elif semantic_check.get("passed"):
                    semantic_ok = "✅"
                else:
                    semantic_ok = "❌"

                lines.append(
                    f"| {name} | {score}% | {files_ok} | {tests_ok} | {wiring_ok} | {absent_ok} | {config_ok} | {semantic_ok} |"
                )
            else:
                lines.append(f"| {name} | - | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ |")

        lines.append("")

        # Failures
        failures = []
        semantic_failures = []
        for doc in report.get("docs", []):
            if not doc.get("has_harness"):
                continue
            for check_name, check_result in doc.get("checks", {}).items():
                if not check_result.get("passed", True):
                    for item in check_result.get("missing", []):
                        failures.append(f"**{doc['name']}** [{check_name}]: {item}")
                    for item in check_result.get("checks_failed", []):
                        semantic_failures.append(f"**{doc['name']}** [semantic]: {item}")

        if failures:
            lines.append("### ❌ Failures")
            lines.append("")
            for f in failures[:10]:
                lines.append(f"- {f}")
            if len(failures) > 10:
                lines.append(f"- _...and {len(failures) - 10} more_")
            lines.append("")

        if semantic_failures:
            lines.append("### 🧪 Semantic Failures (code execution failed)")
            lines.append("")
            for sf in semantic_failures[:10]:
                lines.append(f"- {sf}")
            if len(semantic_failures) > 10:
                lines.append(f"- _...and {len(semantic_failures) - 10} more_")

        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_architecture_plans(self) -> str:
        """Render architecture plans list."""
        lines = [f"{self.LIVE_START}architecture_plans -->"]
        lines.append("## Architecture Plans")
        lines.append("")

        opus_dir = self._root / "docs/architecture/OPUS"
        if not opus_dir.exists():
            lines.append("_No OPUS docs found_")
            lines.append(self.LIVE_END)
            return "\n".join(lines)

        docs = []
        for f in sorted(opus_dir.glob("*.md")):
            if f.name.lower() not in ("readme.md", "index.md", "008-index.md"):
                docs.append((f.stem, f))

        lines.append(f"**{len(docs)} documents** in `docs/architecture/OPUS/`")
        lines.append("")

        for name, path in docs:
            rel_path = f"docs/architecture/OPUS/{path.name}"
            lines.append(f"- [{name}]({rel_path})")

        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_prakriti_state(self) -> str:
        """Render Prakriti state panel."""
        lines = [f"{self.LIVE_START}prakriti_state -->"]
        lines.append("## Prakriti State (OPUS-027)")
        lines.append("")

        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)
        except Exception:
            lines.append("_Prakriti not available_")
            lines.append(self.LIVE_END)
            return "\n".join(lines)

        # Session status
        session = getattr(prakriti, "session", None)
        if session:
            lines.append("### 📍 Active Session")
            lines.append("")
            lines.append("| Property | Value |")
            lines.append("| --- | --- |")
            lines.append(f"| Session ID | `{session.session_id}` |")
            lines.append(f"| Boot Commit | `{session.boot_commit[:7]}` |")
            lines.append("")
        else:
            lines.append("### 📍 Session")
            lines.append("")
            lines.append("_No active session (kernel may be stopped)_")
            lines.append("")

        # Layer status
        lines.append("### 🔮 Three Layers")
        lines.append("")
        lines.append("| Layer | Name | Status | Details |")
        lines.append("| --- | --- | --- | --- |")

        # STHULA
        try:
            git_status = prakriti.git.status()
            is_dirty = git_status.get("is_dirty", False)
            branch = git_status.get("branch", "unknown")
            sthula = ("🟡", f"Dirty on `{branch}`") if is_dirty else ("✅", f"Clean on `{branch}`")
        except Exception:
            sthula = ("❌", "Error")
        lines.append(f"| 1 | STHULA (Physical) | {sthula[0]} | {sthula[1]} |")

        # PRANA
        if self._kernel:
            try:
                status_val = self._kernel.status.value
                agents = len(getattr(self._kernel, "_agents", {}))
                prana = ("✅", f"Running ({agents} agents)") if status_val == "RUNNING" else ("⏹️", "Stopped")
            except Exception:
                prana = ("⏹️", "Stopped")
        else:
            prana = ("⏹️", "Stopped")
        lines.append(f"| 2 | PRANA (Runtime) | {prana[0]} | {prana[1]} |")

        # PURUSHA
        try:
            personas_status = prakriti.personas.status()
            active = personas_status.get("active_persona")
            if active:
                purusha = ("✅", f"Active: `{active}`")
            else:
                purusha = ("⚪", "No personas defined")
        except Exception:
            purusha = ("⚪", "No personas defined")
        lines.append(f"| 3 | PURUSHA (Identity) | {purusha[0]} | {purusha[1]} |")

        lines.append("")

        # Cryptographic Zipper
        lines.append("### 🔗 Cryptographic Zipper")
        lines.append("")
        lines.append("| Component | Hash | Synced |")
        lines.append("| --- | --- | --- |")

        try:
            git_sha = prakriti.git.head_sha()[:12]
            ledger_hash = (
                prakriti.ledger.get_current_head_hash()[:12] if prakriti.ledger.get_current_head_hash() else "empty"
            )
            last_sync = prakriti.ledger.get_last_sync_commit()
            synced = "✅" if last_sync and git_sha and last_sync.startswith(git_sha[:7]) else "⚪"
        except Exception:
            git_sha = "unknown"
            ledger_hash = "unknown"
            synced = "❓"

        lines.append(f"| Git HEAD | `{git_sha}` | {synced} |")
        lines.append(f"| Ledger HEAD | `{ledger_hash}` | {synced} |")
        lines.append("")

        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_code_health(self) -> str:
        """Render code health panel (TODOs/HACKs/FIXMEs)."""
        lines = [f"{self.LIVE_START}code_health -->"]
        lines.append("## Code Health (TODO/HACK/FIXME)")
        lines.append("")

        # Scan patterns
        todos = self._scan_pattern(r"#\s*TODO", "vibe_core/**/*.py")
        hacks = self._scan_pattern(r"#\s*HACK", "vibe_core/**/*.py")
        fixmes = self._scan_pattern(r"#\s*FIXME", "vibe_core/**/*.py")

        total = len(todos) + len(hacks) + len(fixmes)
        if total == 0:
            lines.append("_No technical debt markers found_")
            lines.append(self.LIVE_END)
            return "\n".join(lines)

        lines.append(f"**Total: {total}** (TODO: {len(todos)}, HACK: {len(hacks)}, FIXME: {len(fixmes)})")
        lines.append("")

        # TODOs (collapsible)
        if todos:
            lines.append("<details>")
            lines.append(f"<summary>TODOs ({len(todos)})</summary>")
            lines.append("")
            for item in todos[:20]:
                lines.append(f"- `{item['file']}:{item['line']}` - {item['text'][:60]}")
            if len(todos) > 20:
                lines.append(f"- _...and {len(todos) - 20} more_")
            lines.append("")
            lines.append("</details>")

        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _scan_pattern(self, pattern: str, glob_pattern: str) -> List[Dict[str, Any]]:
        """Scan files for a pattern."""
        results = []
        try:
            import re as regex

            for file_path in self._root.glob(glob_pattern):
                if "archive" in str(file_path) or "__pycache__" in str(file_path):
                    continue
                try:
                    content = file_path.read_text()
                    for i, line in enumerate(content.split("\n"), 1):
                        if regex.search(pattern, line):
                            rel_path = str(file_path.relative_to(self._root))
                            results.append({"file": rel_path, "line": i, "text": line.strip()})
                except Exception:
                    pass
        except Exception:
            pass
        return results[:50]  # Limit

    def _render_test_health(self) -> str:
        """Render test health panel."""
        lines = [f"{self.LIVE_START}test_health -->"]
        lines.append("## Test Suite Health")
        lines.append("")

        tests_dir = self._root / "tests"

        # Count tests
        active_tests = [t for t in tests_dir.glob("**/test_*.py") if "archive" not in str(t)]
        archived_tests = list((tests_dir / "archive").glob("**/test_*.py")) if (tests_dir / "archive").exists() else []

        unit_tests = [t for t in active_tests if "/unit/" in str(t)]
        integration_tests = [t for t in active_tests if "/integration/" in str(t)]
        hardening_tests = [t for t in active_tests if "/hardening/" in str(t)]
        root_tests = [t for t in active_tests if str(t.parent) == str(tests_dir)]

        # Fixture usage
        using_fixtures = 0
        using_raw = 0
        for test_file in active_tests[:30]:
            try:
                content = test_file.read_text()
                if "fixtures import" in content or "test_kernel" in content:
                    using_fixtures += 1
                elif "RealVibeKernel" in content:
                    using_raw += 1
            except Exception:
                pass

        lines.append("| Metric | Count | Status |")
        lines.append("| --- | --- | --- |")
        lines.append(f"| Active Tests | {len(active_tests)} | - |")
        if archived_tests:
            lines.append(f"| Archived (broken) | {len(archived_tests)} | - |")
        lines.append(f"| Organized | {len(active_tests) - len(root_tests)}/{len(active_tests)} | - |")
        lines.append(f"| Unit Tests | {len(unit_tests)} | - |")
        lines.append(f"| Integration Tests | {len(integration_tests)} | - |")
        lines.append(f"| Hardening Tests | {len(hardening_tests)} | - |")

        total_scanned = using_fixtures + using_raw
        if total_scanned > 0:
            pct = (using_fixtures / total_scanned) * 100
            lines.append(f"| Using Fixtures | {using_fixtures}/{total_scanned} ({pct:.0f}%) | OK |")

        lines.append("")
        if archived_tests:
            lines.append(f"**Debt:** {len(archived_tests)} tests in `tests/archive/` need revival")

        lines.append(self.LIVE_END)
        return "\n".join(lines)

    def _render_work_sections(self, preserved: Dict[str, str]) -> str:
        """Render preserved AI/HUMAN work sections."""
        current_work = preserved.get("current_work", "_Define current task_")
        blockers = preserved.get("blockers", "_None_")
        notes = preserved.get("notes", "_Add notes here_")

        return f"""---

{self.AI_START}current_work -->
## Current Work

<!-- AI: Update this with what you're working on -->
{current_work}
{self.AI_END}

{self.AI_START}blockers -->
## Blockers

<!-- AI: List any blockers -->
{blockers}
{self.AI_END}

{self.HUMAN_START}notes -->
## Notes

<!-- Human can write here -->
{notes}
{self.HUMAN_END}
"""

    def _render_footer(self) -> str:
        """Render footer."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"\n---\n*Generated by OPUS Assistant Plugin | {timestamp} UTC*"

    def _extract_preserved_sections(self) -> Dict[str, str]:
        """Extract @AI and @HUMAN sections from existing OPUS.md."""
        preserved = {}

        if not self._opus_path.exists():
            return preserved

        try:
            content = self._opus_path.read_text()
        except Exception:
            return preserved

        # Extract AI sections
        for section_name in ["current_work", "blockers"]:
            pattern = rf"<!-- @AI:{section_name} -->\s*\n## [^\n]+\n\n<!-- [^>]* -->\n(.*?)<!-- /@AI -->"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                preserved[section_name] = match.group(1).strip()

        # Extract HUMAN sections
        pattern = r"<!-- @HUMAN:notes -->\s*\n## [^\n]+\n\n<!-- [^>]* -->\n(.*?)<!-- /@HUMAN -->"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            preserved["notes"] = match.group(1).strip()

        return preserved


def write_opus_md(workspace_root: Path, kernel: Optional[Any] = None, quick: bool = False) -> Path:
    """
    Convenience function to write OPUS.md.

    Args:
        workspace_root: Project root
        kernel: Optional kernel for runtime data
        quick: Skip expensive verification

    Returns:
        Path to OPUS.md
    """
    writer = OpusMdWriter(workspace_root, kernel)
    return writer.write(quick=quick)

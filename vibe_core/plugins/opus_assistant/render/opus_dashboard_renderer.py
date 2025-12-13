"""
OPUS Dashboard Renderer - Template-Based UI Generation.

OPUS-029 Phase 10: From String Spaghetti to Clean Templates

This replaces 400+ lines of f-string concatenation with a single
Jinja2 template that:
1. Separates presentation from logic
2. Is READABLE by OPUS for self-modification
3. Supports emotional UI (header changes based on trust)
4. Has CLI action links for circuits

Architecture:
    ┌─────────────────────────────────────────┐
    │        OpusDashboardRenderer            │
    │        (Data Aggregator)                │
    └──────────────────┬──────────────────────┘
                       │ gathers data from
                       ▼
    ┌─────────────────────────────────────────┐
    │  Prakriti │ Verification │ Circuits     │
    │  Git/Ledger │ Trust Score │ Definitions │
    └──────────────────┬──────────────────────┘
                       │ passes to
                       ▼
    ┌─────────────────────────────────────────┐
    │      opus_dashboard.md.j2               │
    │      (Jinja2 Template)                  │
    │      - Emotional Header                 │
    │      - CLI Action Links                 │
    │      - Self-Documenting                 │
    └──────────────────┬──────────────────────┘
                       │ renders to
                       ▼
    ┌─────────────────────────────────────────┐
    │             OPUS.md                     │
    └─────────────────────────────────────────┘
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("OPUS_DASHBOARD")


class OpusDashboardRenderer:
    """
    Template-based OPUS.md renderer.

    Uses Jinja2 templates instead of string concatenation.
    This is the 10/10 approach Gemini demanded.
    """

    def __init__(self, workspace_root: Path, kernel: Optional[Any] = None):
        """
        Initialize renderer.

        Args:
            workspace_root: Project root directory
            kernel: Optional kernel instance for runtime data
        """
        self._root = workspace_root
        self._kernel = kernel
        self._opus_path = self._root / "OPUS.md"
        self._template_path = self._root / "vibe_core/plugins/opus_assistant/templates/opus_dashboard.md.j2"
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

    def render(self, quick: bool = False) -> str:
        """
        Render OPUS.md using template.

        Args:
            quick: Skip expensive operations

        Returns:
            Rendered markdown content
        """
        try:
            from jinja2 import Environment, FileSystemLoader, select_autoescape

            # Setup Jinja2 environment
            template_dir = self._template_path.parent
            env = Environment(
                loader=FileSystemLoader(str(template_dir)),
                autoescape=select_autoescape(["html", "xml"]),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            template = env.get_template("opus_dashboard.md.j2")

            # Gather all data
            context = self._gather_context(quick=quick)

            # Render template
            return template.render(**context)

        except ImportError:
            logger.warning("Jinja2 not available, falling back to legacy renderer")
            return self._fallback_render(quick=quick)
        except Exception as e:
            logger.error(f"Template render failed: {e}")
            return self._fallback_render(quick=quick)

    def write(self, quick: bool = False) -> Path:
        """
        Render and write OPUS.md.

        Args:
            quick: Skip expensive operations

        Returns:
            Path to written file
        """
        # Preserve existing sections
        preserved = self._extract_preserved_sections()

        # Render content
        content = self.render(quick=quick)

        # Re-inject preserved sections (template has placeholders)
        content = self._inject_preserved_sections(content, preserved)

        # Write file
        self._opus_path.write_text(content)

        return self._opus_path

    def _gather_context(self, quick: bool = False) -> Dict[str, Any]:
        """Gather all data for template context."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # Verification (for trust score)
        verification = self._gather_verification(quick=quick)
        trust_score = verification.get("total_score", 0)

        # Health status
        health_status = self._compute_health_status(trust_score)

        # 🔌 WIRING: Gather karma from OPUS StateManager
        karma = self._gather_karma()

        return {
            "timestamp": timestamp,
            "trust_score": trust_score,
            "health_status": health_status,
            "kernel": self._gather_kernel_state(),
            "git": self._gather_git_state(),
            "session": self._gather_session(),
            "karma": karma,  # 🔌 WIRING: Karma score, history, trend
            "layers": self._gather_prakriti_layers(),
            "focus_areas": self._gather_focus_areas(),
            "journal": self._gather_journal(),
            "circuits": self._gather_circuits(),
            "verification": verification,
            "architecture_plans": self._gather_architecture_plans(),
            "zipper": self._gather_zipper(),
            "code_health": self._gather_code_health(),
            "test_health": self._gather_test_health(),
            "module_index": self._gather_module_index(),  # NEW: Codebase navigation
            "hot_paths": self._gather_hot_paths(),  # NEW: Most changed files
            "preserved": {},  # Will be injected separately
        }

    def _compute_health_status(self, trust_score: int) -> str:
        """Compute health status from trust score."""
        if trust_score >= 80:
            return "HEALTHY"
        elif trust_score >= 60:
            return "DEGRADED"
        elif trust_score >= 40:
            return "WARNING"
        else:
            return "CRITICAL"

    def _gather_kernel_state(self) -> Dict[str, Any]:
        """Gather kernel state."""
        if self._kernel:
            try:
                return {
                    "status": self._kernel.status.value,
                    "agent_count": len(getattr(self._kernel, "_agents", {})),
                }
            except Exception:
                pass
        return {"status": "STOPPED", "agent_count": 0}

    def _gather_git_state(self) -> Dict[str, Any]:
        """Gather git state from Prakriti."""
        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)
            status = prakriti.git.status()

            uncommitted = []
            if status.get("dirty", False):
                try:
                    uncommitted = prakriti.git.dirty_files() if hasattr(prakriti.git, "dirty_files") else []
                except Exception:
                    pass

            return {
                "branch": status.get("branch", "unknown"),
                "sha": status.get("sha", "unknown"),
                "dirty": status.get("dirty", False),
                "uncommitted_files": uncommitted[:10],
            }
        except Exception as e:
            logger.debug(f"Git state unavailable: {e}")
            return {"branch": "unknown", "sha": "unknown", "dirty": False, "uncommitted_files": []}

    def _gather_session(self) -> Optional[Dict[str, Any]]:
        """
        Gather session info from OPUS StateManager and Prakriti.

        🔌 WIRING: Combines Prakriti session with OPUS StateManager session.
        """
        session_data = {}

        # Try OPUS StateManager first (has richer data)
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()
            opus_session = state_mgr.load_session()
            if opus_session:
                session_data = {
                    "id": opus_session.session_id,
                    "boot_commit": getattr(opus_session, "boot_commit", None),
                    "boot_mode": opus_session.boot_mode,
                    "started_at": opus_session.started_at,
                    "tick_count": getattr(opus_session, "tick_count", None),
                    # 🎛️ CONTROL PLANE: View preferences for metamorphic UI
                    "view_preferences": opus_session.view_preferences,
                }
        except Exception as e:
            logger.debug(f"OPUS session unavailable: {e}")

        # Fallback/supplement with Prakriti session
        if not session_data:
            try:
                from vibe_core.state.prakriti import Prakriti

                prakriti = Prakriti(self._root)
                session = getattr(prakriti, "session", None)
                if session:
                    session_data = {
                        "id": session.session_id,
                        "boot_commit": getattr(session, "boot_commit", "unknown"),
                    }
            except Exception:
                pass

        return session_data if session_data else None

    def _gather_prakriti_layers(self) -> Dict[str, Any]:
        """Gather Prakriti layer details."""
        purusha = {"thought_count": 0, "persona": None}

        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)

            # Ephemeral thoughts
            if hasattr(prakriti.ephemeral, "get_thoughts"):
                thoughts = prakriti.ephemeral.get_thoughts()
                purusha["thought_count"] = len(thoughts) if thoughts else 0

            # Active persona
            if hasattr(prakriti, "personas"):
                status = prakriti.personas.status() if hasattr(prakriti.personas, "status") else {}
                purusha["persona"] = status.get("active_persona")
        except Exception:
            pass

        return {"purusha": purusha}

    def _gather_focus_areas(self) -> List[str]:
        """Determine focus areas from system state."""
        focus = []

        # Git dirty?
        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)
            if prakriti.git.status().get("dirty"):
                focus.append("Commit pending changes")
        except Exception:
            pass

        # Drift?
        try:
            from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

            detector = DriftDetector(workspace_root=self._root)
            quick = detector.quick_check()
            if not quick.get("healthy", True):
                focus.append("Documentation drift detected")
        except Exception:
            pass

        return focus

    def _gather_journal(self) -> List[Dict[str, Any]]:
        """
        Gather journal entries from OPUS StateManager.

        🔌 WIRING: This now reads from .opus_state/observations.jsonl
        instead of parsing the existing OPUS.md file.
        """
        observations = []

        # Severity to emoji mapping
        severity_icons = {
            "ALERT": "🚨",
            "WARN": "⚠️",
            "INFO": "ℹ️",
            "INSIGHT": "💡",
        }

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()
            entries = state_mgr.get_observations(limit=20)

            for entry in entries:
                observations.append(
                    {
                        "timestamp": entry.timestamp,
                        "severity_icon": severity_icons.get(entry.severity, "📝"),
                        "source": entry.source,
                        "message": entry.message,
                    }
                )
        except Exception as e:
            logger.debug(f"Failed to gather journal from StateManager: {e}")
            # Fallback: try parsing existing OPUS.md (legacy support)
            try:
                if self._opus_path.exists():
                    content = self._opus_path.read_text()
                    pattern = re.compile(
                        r"- `(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})` ([^\s]+) \*\*\[([^\]]+)\]\*\* (.+)",
                        re.MULTILINE,
                    )
                    matches = pattern.findall(content)
                    for ts, icon, source, message in matches[:20]:
                        observations.append(
                            {
                                "timestamp": ts,
                                "severity_icon": icon,
                                "source": source,
                                "message": message.strip(),
                            }
                        )
            except Exception:
                pass

        return observations

    def _gather_karma(self) -> Dict[str, Any]:
        """
        Gather karma data from OPUS StateManager.

        🔌 WIRING: Reads from .opus_state/karma_history.jsonl
        Returns current karma score, history, and boot mode.
        """
        karma_data = {
            "current_score": 100,
            "boot_mode": "full_power",
            "history": [],
            "trend": "stable",
        }

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()

            # Get last karma entry (current score)
            last_karma = state_mgr.get_last_karma()
            if last_karma:
                karma_data["current_score"] = last_karma.score
                karma_data["boot_mode"] = last_karma.boot_mode

            # Get karma history for trend calculation
            history = state_mgr.get_karma_history(limit=10)
            if history:
                karma_data["history"] = [
                    {
                        "timestamp": entry.timestamp,
                        "score": entry.score,
                        "boot_mode": entry.boot_mode,
                        "error_count": entry.error_count,
                        "crash_count": entry.crash_count,
                    }
                    for entry in history
                ]

                # Calculate trend (improving, declining, stable)
                if len(history) >= 2:
                    recent = history[0].score
                    older = history[-1].score
                    if recent > older + 5:
                        karma_data["trend"] = "improving"
                    elif recent < older - 5:
                        karma_data["trend"] = "declining"
                    else:
                        karma_data["trend"] = "stable"

        except Exception as e:
            logger.debug(f"Failed to gather karma from StateManager: {e}")

        return karma_data

    def _gather_circuits(self) -> List[Dict[str, Any]]:
        """Gather circuit definitions."""
        circuits = []
        circuits_dir = self._root / "vibe_core/plugins/opus_assistant/circuits"

        try:
            if circuits_dir.exists():
                for circuit_file in sorted(circuits_dir.glob("*.yaml")):
                    try:
                        data = yaml.safe_load(circuit_file.read_text())
                        circuit = data.get("circuit", {})

                        triggers = [t.get("event", "") for t in circuit.get("triggers", []) if t.get("event")]

                        circuits.append(
                            {
                                "id": circuit.get("id", circuit_file.stem),
                                "name": circuit.get("name", circuit_file.stem),
                                "description": circuit.get("description", "")[:60],
                                "triggers": triggers,
                                "states": len(circuit.get("states", {})),
                            }
                        )
                    except Exception:
                        circuits.append(
                            {
                                "id": circuit_file.stem,
                                "name": circuit_file.stem,
                                "description": "Parse error",
                                "triggers": [],
                                "states": 0,
                            }
                        )
        except Exception:
            pass

        return circuits

    def _gather_verification(self, quick: bool = False) -> Dict[str, Any]:
        """Run verification and gather results."""
        try:
            from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

            engine = VerificationEngine(
                workspace_root=self._root,
                config=self._config.get("verification", {}),
            )
            report = engine.run_verification(quick=quick)

            # Process for template
            docs = []
            failures = []

            for doc in report.get("docs", []):
                doc_entry = {
                    "name": doc["name"][:25],
                    "has_harness": doc.get("has_harness", False),
                    "score": doc.get("score", 0),
                    "checks": {},
                }

                if doc.get("has_harness"):
                    checks = doc.get("checks", {})
                    doc_entry["checks"] = {
                        "files": checks.get("files", {}).get("passed", False),
                        "tests": checks.get("tests", {}).get("passed", False),
                        "wiring": checks.get("wiring", {}).get("passed", False),
                        "absent": checks.get("absent", {}).get("passed", True),
                        "config": checks.get("config", {}).get("passed", False),
                        "semantic": "skipped"
                        if checks.get("semantic", {}).get("details")
                        in ("No semantic checks specified", "Skipped (quick mode)")
                        else checks.get("semantic", {}).get("passed", False),
                    }

                    # Collect failures
                    for check_name, check_result in checks.items():
                        if not check_result.get("passed", True):
                            for item in check_result.get("missing", []):
                                failures.append(f"**{doc['name']}** [{check_name}]: {item}")

                docs.append(doc_entry)

            return {
                "total_score": report.get("total_score", 0),
                "docs_verified": report.get("docs_with_harness", 0),
                "docs_without_harness": report.get("docs_without_harness", 0),
                "docs": docs,
                "failures": failures,
            }
        except Exception as e:
            logger.debug(f"Verification failed: {e}")
            return {"total_score": 0, "docs_verified": 0, "docs_without_harness": 0, "docs": [], "failures": []}

    def _gather_architecture_plans(self) -> List[Dict[str, str]]:
        """Gather architecture plan documents."""
        plans = []
        opus_dir = self._root / "docs/architecture/OPUS"

        try:
            if opus_dir.exists():
                for f in sorted(opus_dir.glob("*.md")):
                    if f.name.lower() not in ("readme.md", "index.md", "008-index.md"):
                        plans.append(
                            {
                                "name": f.stem,
                                "path": f"docs/architecture/OPUS/{f.name}",
                            }
                        )
        except Exception:
            pass

        return plans

    def _gather_zipper(self) -> Dict[str, Any]:
        """Gather cryptographic zipper state."""
        try:
            from vibe_core.state.prakriti import Prakriti

            prakriti = Prakriti(self._root)
            git_sha = prakriti.git.head_sha()
            ledger_hash = prakriti.ledger.get_current_head_hash() or "empty"
            last_sync = prakriti.ledger.get_last_sync_commit()

            synced = last_sync and git_sha and last_sync.startswith(git_sha[:7])

            return {
                "git_sha": git_sha,
                "ledger_hash": ledger_hash,
                "synced": synced,
            }
        except Exception:
            return {"git_sha": "unknown", "ledger_hash": "unknown", "synced": False}

    def _gather_code_health(self) -> Dict[str, List[Dict[str, Any]]]:
        """Gather code health markers (TODO/HACK/FIXME)."""

        def scan_pattern(pattern: str) -> List[Dict[str, Any]]:
            results = []
            try:
                for file_path in self._root.glob("vibe_core/**/*.py"):
                    if "archive" in str(file_path) or "__pycache__" in str(file_path):
                        continue
                    try:
                        content = file_path.read_text()
                        for i, line in enumerate(content.split("\n"), 1):
                            if re.search(pattern, line):
                                results.append(
                                    {
                                        "file": str(file_path.relative_to(self._root)),
                                        "line": i,
                                        "text": line.strip(),
                                    }
                                )
                    except Exception:
                        pass
            except Exception:
                pass
            return results[:50]

        return {
            "todos": scan_pattern(r"#\s*TODO"),
            "hacks": scan_pattern(r"#\s*HACK"),
            "fixmes": scan_pattern(r"#\s*FIXME"),
        }

    def _gather_test_health(self) -> Dict[str, Any]:
        """Gather test suite health metrics."""
        tests_dir = self._root / "tests"

        try:
            active_tests = [t for t in tests_dir.glob("**/test_*.py") if "archive" not in str(t)]
            archived_tests = (
                list((tests_dir / "archive").glob("**/test_*.py")) if (tests_dir / "archive").exists() else []
            )

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

            total_scanned = using_fixtures + using_raw

            return {
                "active": len(active_tests),
                "archived": len(archived_tests),
                "organized": len(active_tests) - len(root_tests),
                "unit": len(unit_tests),
                "integration": len(integration_tests),
                "hardening": len(hardening_tests),
                "using_fixtures": using_fixtures,
                "total_scanned": total_scanned,
                "fixture_pct": f"{(using_fixtures / total_scanned) * 100:.0f}" if total_scanned > 0 else None,
            }
        except Exception:
            return {"active": 0, "archived": 0, "organized": 0, "unit": 0, "integration": 0, "hardening": 0}

    def _gather_module_index(self) -> List[Dict[str, Any]]:
        """
        Gather module index for codebase navigation.

        Scans vibe_core/ for top-level modules and extracts:
        - Module name
        - One-line description (from docstring)
        - File count
        - Has tests?

        This is the "what's in this codebase?" answer.
        """
        modules = []
        vibe_core = self._root / "vibe_core"

        if not vibe_core.exists():
            return modules

        # Scan top-level directories
        for item in sorted(vibe_core.iterdir()):
            if item.name.startswith(("_", ".")):
                continue

            if item.is_dir():
                # Get description from __init__.py docstring
                init_file = item / "__init__.py"
                description = ""
                if init_file.exists():
                    try:
                        content = init_file.read_text()
                        # Extract first docstring
                        if '"""' in content:
                            start = content.find('"""') + 3
                            end = content.find('"""', start)
                            if end > start:
                                doc = content[start:end].strip()
                                # First line only
                                description = doc.split("\n")[0][:60]
                    except Exception:
                        pass

                # Count Python files
                py_files = list(item.glob("**/*.py"))
                file_count = len([f for f in py_files if "__pycache__" not in str(f)])

                # Has tests?
                has_tests = (item / "tests").exists() or any("test_" in f.name for f in py_files)

                modules.append(
                    {
                        "name": item.name,
                        "description": description or f"({file_count} files)",
                        "files": file_count,
                        "has_tests": has_tests,
                        "path": f"vibe_core/{item.name}/",
                    }
                )

        return modules[:20]  # Limit to top 20 modules

    def _gather_hot_paths(self) -> List[Dict[str, Any]]:
        """
        Gather hot paths - most frequently changed files.

        Uses git log to find files with most commits.
        These are the entry points for understanding the codebase.
        """
        hot_paths = []

        try:
            import subprocess

            # Get files with most commits (last 100 commits)
            result = subprocess.run(
                ["git", "log", "--pretty=format:", "--name-only", "-100"],
                cwd=self._root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                # Count file occurrences
                file_counts: Dict[str, int] = {}
                for line in result.stdout.split("\n"):
                    line = line.strip()
                    if line and line.endswith(".py") and "vibe_core" in line:
                        file_counts[line] = file_counts.get(line, 0) + 1

                # Sort by count, get top 10
                sorted_files = sorted(file_counts.items(), key=lambda x: -x[1])[:10]

                for file_path, count in sorted_files:
                    # Get last commit message for this file
                    msg_result = subprocess.run(
                        ["git", "log", "-1", "--pretty=format:%s", "--", file_path],
                        cwd=self._root,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    last_msg = msg_result.stdout.strip()[:40] if msg_result.returncode == 0 else ""

                    hot_paths.append(
                        {
                            "path": file_path,
                            "commits": count,
                            "last_change": last_msg,
                        }
                    )

        except Exception:
            pass

        return hot_paths

    def _extract_preserved_sections(self) -> Dict[str, str]:
        """Extract @AI and @HUMAN sections from existing OPUS.md."""
        preserved = {}

        if not self._opus_path.exists():
            return preserved

        try:
            content = self._opus_path.read_text()

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

        except Exception:
            pass

        return preserved

    def _inject_preserved_sections(self, content: str, preserved: Dict[str, str]) -> str:
        """Inject preserved sections back into rendered content."""
        for key, value in preserved.items():
            placeholder = (
                "_Define current task_"
                if key == "current_work"
                else ("_None_" if key == "blockers" else "_Add notes here_")
            )
            if value and value != placeholder:
                content = content.replace(placeholder, value)

        return content

    def _fallback_render(self, quick: bool = False) -> str:
        """Fallback to legacy renderer if Jinja2 unavailable."""
        from vibe_core.plugins.opus_assistant.render.opus_md_writer import OpusMdWriter

        writer = OpusMdWriter(self._root, self._kernel)
        return writer._generate_content(quick=quick)

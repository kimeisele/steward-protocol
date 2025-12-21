"""
OPUS Dashboard Renderer - Template-Based UI Generation.

OPUS-029 Phase 10: From String Spaghetti to Clean Templates
OPUS-031 Layer 1.5: Bidirectional Control Surface

This replaces 400+ lines of f-string concatenation with a single
Jinja2 template that:
1. Separates presentation from logic
2. Is READABLE by OPUS for self-modification
3. Supports emotional UI (header changes based on trust)
4. Has CLI action links for circuits

LAYER 1.5 BIDIRECTIONAL LOOP (OPUS-031):
    ┌─────────────────────────────────────────┐
    │         1. READ EXISTING OPUS.md        │
    │         (Before rendering!)             │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────┐
    │      2. PARSE CONTROL PLANE             │
    │      ControlCablesParser extracts       │
    │      human edits from checkboxes        │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
    ┌─────────────────────────────────────────┐
    │      3. APPLY TO STATE                  │
    │      StateManager.set_preference()      │
    │      persists to .opus_state/           │
    └──────────────────┬──────────────────────┘
                       │
                       ▼
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
    │    (With human edits reflected)         │
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
        self._manas_config = self._load_manas_config()  # OPUS-092: Load MANAS config for Senses

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from config/opus.yaml."""
        config_path = self._root / "config" / "opus.yaml"
        try:
            if config_path.exists():
                return yaml.safe_load(config_path.read_text())
        except Exception:
            pass
        return {}

    def _load_manas_config(self) -> Dict[str, Any]:
        """
        Load MANAS configuration from config/manas.yaml.

        OPUS-092: Senses need config to function properly.
        This ensures Prakriti/Dharma get their config when instantiated for reporting.
        """
        config_path = self._root / "config" / "manas.yaml"
        try:
            if config_path.exists():
                full_config = yaml.safe_load(config_path.read_text()) or {}
                logger.debug(f"📝 Loaded MANAS config with {len(full_config)} sections")
                return full_config
        except Exception as e:
            logger.debug(f"⚠️  Failed to load MANAS config: {e}")
        return {}

    def render(self, quick: bool = False) -> str:
        """
        Render OPUS.md using template.

        LAYER 1.5 BIDIRECTIONAL LOOP (OPUS-031):
        1. Read existing OPUS.md (if exists)
        2. Parse Control Plane for human edits
        3. Apply to StateManager (persists changes)
        4. Gather context (now reflects human edits)
        5. Render template

        Args:
            quick: Skip expensive operations

        Returns:
            Rendered markdown content
        """
        # ========================================
        # LAYER 1.5: BIDIRECTIONAL CONTROL CABLES
        # Read BEFORE Write - Extract human edits
        # ========================================
        self._apply_control_cables()

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

            # Gather all data (now includes human edits from step 1)
            context = self._gather_context(quick=quick)

            # Render template
            return template.render(**context)

        except ImportError:
            logger.warning("Jinja2 not available, falling back to legacy renderer")
            return self._fallback_render(quick=quick)
        except Exception as e:
            logger.error(f"Template render failed: {e}")
            return self._fallback_render(quick=quick)

    def _apply_control_cables(self) -> None:
        """
        LAYER 1.5: Parse existing OPUS.md and apply human edits to state.
        LAYER 1.5+: OPUS-032 Volition - Execute approved intents.

        This is the "read before write" step that makes OPUS.md bidirectional.
        Human edits to checkboxes in the Control Plane section are persisted
        to StateManager before the next render cycle.

        OPUS-032 Addition: Intent approvals/rejections are also processed here,
        triggering MANAS to execute or reject intents.

        Design Decisions (OPUS-031/032):
        - DD4: Bidirectional Control Surface - OPUS.md is INPUT, not just OUTPUT
        - DD5: Configuration, Not Commands - Settings persist until changed
        - DD7: Volition - Intent approval triggers execution
        """
        if not self._opus_path.exists():
            logger.debug("No existing OPUS.md - skipping control cables")
            return

        try:
            from vibe_core.plugins.opus_assistant.core.control_cables import (
                ControlCablesParser,
            )
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                get_state_manager,
            )

            # Read existing OPUS.md
            opus_content = self._opus_path.read_text()

            # Parse Control Plane section
            parser = ControlCablesParser()
            settings = parser.parse_control_plane(opus_content)

            # Get state manager
            state_manager = get_state_manager()

            # Check what changed
            changes = parser.get_changed_settings(state_manager, settings)

            if changes:
                logger.info(
                    f"🔌 Control Cables: Detected {len(changes)} human edits: {', '.join(c['key'] for c in changes)}"
                )

            # Apply to state (persists to .opus_state/session.json)
            parser.apply_to_state(state_manager, settings)

            # ================================================================
            # OPUS-032: VOLITION - Process Intent Approvals/Rejections
            # ================================================================
            try:
                volition_results = parser.apply_intent_decisions(opus_content)

                if volition_results["executed"]:
                    logger.info(
                        f"🧠 VOLITION: Executed {len(volition_results['executed'])} intent(s): "
                        f"{', '.join(volition_results['executed'])}"
                    )

                if volition_results["rejected"]:
                    logger.info(
                        f"🧠 VOLITION: Rejected {len(volition_results['rejected'])} intent(s): "
                        f"{', '.join(volition_results['rejected'])}"
                    )

                if volition_results["errors"]:
                    for error in volition_results["errors"]:
                        logger.warning(f"🧠 VOLITION error: {error}")

            except Exception as e:
                logger.debug(f"Volition processing failed: {e}")

        except ImportError as e:
            logger.debug(f"Control cables not available: {e}")
        except Exception as e:
            logger.warning(f"Failed to apply control cables: {e}")

    # NOTE: write() method REMOVED - opus_assistant is BACKEND only
    # All file writes go through InterfacePlugin -> kernel.io
    # See: vibe_core/plugins/interface/renderers/opus/renderer.py

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

        # 💰 LAYER 1.5: Gather treasury for budget display
        treasury = self._gather_treasury()

        return {
            "timestamp": timestamp,
            "trust_score": trust_score,
            "health_status": health_status,
            "kernel": self._gather_kernel_state(),
            "git": self._gather_git_state(),
            "session": self._gather_session(),
            "master_config": self._gather_master_config(),  # OPUS-076: System-wide config (NOT session)
            "karma": karma,  # 🔌 WIRING: Karma score, history, trend
            "treasury": treasury,  # 💰 LAYER 1.5: Budget tracking
            "syscalls": self._gather_syscalls(),  # ⚡ LAYER 2: Experience Replay
            "pending_intent": self._gather_pending_intent(),  # 🎯 LAYER 1.5: Intent Buffer
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
            "dependency_graph": self._gather_dependency_graph(),  # 🎯 SENIOR AI COCKPIT
            "tri_guna": self._gather_tri_guna(),  # 🔮 OPUS-009: State Health
            "dharma": self._gather_dharma(),  # 🙏 OPUS-009: Vedic Conscience
            "sutra": self._gather_sutra(),  # 📜 OPUS-054: Doc/Code Gap Detection
            "sankalpa": self._gather_sankalpa(),  # 🎯 OPUS-055: Strategic Will
            "manas_status": self._gather_manas_status(),  # 🧠 OPUS-133: Neural Learning
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

    def _gather_master_config(self) -> Dict[str, Any]:
        """
        OPUS-076: Read system-wide config from config/providers.yaml.

        FRACTAL ARCHITECTURE:
        - Master config (providers.yaml) → System-wide truth (live_fire, etc.)
        - Opus state (session.json) → Plugin-specific state (view prefs, karma)

        These are SEPARATE. Do not duplicate master config in session.json!
        """
        master_config = {
            "live_fire_enabled": False,  # Safe default
        }

        providers_path = self._root / "config" / "providers.yaml"
        if providers_path.exists():
            try:
                content = providers_path.read_text()
                # Simple parsing - we just need live_fire_enabled
                if "live_fire_enabled: true" in content:
                    master_config["live_fire_enabled"] = True
                elif "live_fire_enabled: false" in content:
                    master_config["live_fire_enabled"] = False
            except Exception as e:
                logger.debug(f"Failed to read master config: {e}")

        return master_config

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

    def _gather_treasury(self) -> Optional[Dict[str, Any]]:
        """
        Gather treasury data for budget display.

        💰 LAYER 1.5: Reads from .opus_state/treasury.json
        Returns daily spend data for the Control Plane panel.
        """
        try:
            from vibe_core.plugins.opus_assistant.core.treasury import get_treasury

            treasury = get_treasury()
            daily = treasury.get_daily_spend()

            return {
                "date": daily.date,
                "tokens_input": daily.tokens_input,
                "tokens_output": daily.tokens_output,
                "estimated_cost": daily.estimated_cost,
                "api_calls": daily.api_calls,
                "budget_warnings": daily.budget_warnings,
            }

        except ImportError:
            logger.debug("Treasury not available (not yet implemented)")
            return None
        except Exception as e:
            logger.debug(f"Failed to gather treasury: {e}")
            return None

    def _gather_syscalls(self) -> Optional[Dict[str, Any]]:
        """
        Gather syscall data for the Syscall Console panel.

        ⚡ LAYER 2: Experience Replay Buffer visualization.
        Shows recent syscalls and statistics for few-shot learning.
        """
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()

            # Get recent syscalls for display
            all_syscalls = state_mgr.get_successful_syscalls(limit=20)

            # Convert to dict format for template
            history = [
                {
                    "timestamp": sc.timestamp,
                    "intent": sc.intent,
                    "syscall_type": sc.syscall_type,
                    "result": sc.result,
                    "execution_time_ms": sc.execution_time_ms,
                }
                for sc in all_syscalls
            ]

            # Get stats
            stats = state_mgr.get_syscall_stats()

            return {
                "history": history,
                "stats": stats,
            }

        except Exception as e:
            logger.debug(f"Failed to gather syscalls: {e}")
            return None

    def _gather_pending_intent(self) -> Optional[Dict[str, Any]]:
        """
        Gather pending intents for the Intent Buffer panel.

        🎯 LAYER 1.5: The "Frontallappen" - shows what system plans to do next.
        🧠 OPUS-032: Now reads from MANAS cognitive kernel for proactive intents.
        Human can approve via checkbox in OPUS.md.
        """
        # First try MANAS (OPUS-032)
        try:
            # Try to get MANAS from the kernel tick handler
            if self._kernel:
                opus_plugin = self._kernel.get_plugin("opus_assistant")
                if opus_plugin and hasattr(opus_plugin, "_tick_handler"):
                    manas = opus_plugin._tick_handler.get_manas()
                    if manas:
                        buffer = manas.get_intent_buffer_for_opus()
                        if buffer.get("pending"):
                            return {
                                "source": "manas",
                                "intents": buffer.get("pending", []),
                                "total_pending": buffer.get("total_pending", 0),
                                "idle_minutes": buffer.get("idle_minutes", 0),
                                "last_thought": buffer.get("last_thought"),
                                "recent_executed": buffer.get("recent_executed", []),
                            }
        except Exception as e:
            logger.debug(f"Failed to get MANAS intents: {e}")

        # Fallback to existing MANAS singleton (GAD-000: Don't create expensive instances for display)
        try:
            from vibe_core.plugins.opus_assistant.manas import CognitiveKernel

            # GAD-000: Only access existing instance, don't create new one for dashboard
            if CognitiveKernel.has_instance(workspace=self._root):
                manas = CognitiveKernel.get_instance(workspace=self._root)
                buffer = manas.get_intent_buffer_for_opus()
                if buffer.get("pending"):
                    return {
                        "source": "manas",
                        "intents": buffer.get("pending", []),
                        "total_pending": buffer.get("total_pending", 0),
                        "idle_minutes": buffer.get("idle_minutes", 0),
                        "last_thought": buffer.get("last_thought"),
                        "recent_executed": buffer.get("recent_executed", []),
                    }
        except Exception as e:
            logger.debug(f"Failed to get existing MANAS intents: {e}")

        # Fallback to legacy StateManager intents
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()
            legacy_intent = state_mgr.get_pending_intent()
            if legacy_intent:
                return {"source": "legacy", "legacy_intent": legacy_intent}
        except Exception as e:
            logger.debug(f"Failed to gather legacy pending intent: {e}")

        return None

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

    def _gather_tri_guna(self) -> Optional[Dict[str, int]]:
        """Gather Tri-Guna state health from PrakritiSense (OPUS-009)."""
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.prakriti_sense import PrakritiSense

            # OPUS-092: Pass config to Sense for proper initialization
            prakriti_config = self._manas_config.get("prakriti_sense", {})
            sense = PrakritiSense(workspace=self._root, config=prakriti_config)
            guna = sense.perceive_state()
            return {
                "sattva": guna.sattva_count,
                "rajas": guna.rajas_count,
                "tamas": guna.tamas_count,
                "total": guna.total_paths,
            }
        except Exception:
            return None

    def _gather_dharma(self) -> Optional[Dict[str, Any]]:
        """Gather Dharma state from DharmaSense (OPUS-009 Extension)."""
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.dharma_sense import DharmaSense

            # OPUS-092: Pass config to Sense for proper initialization
            dharma_config = self._manas_config.get("dharma_sense", {})
            sense = DharmaSense(workspace=self._root, agent_id="manas", config=dharma_config)
            summary = sense.get_dharma_summary()
            return summary.to_dict()
        except Exception:
            return None

    def _gather_sutra(self) -> Optional[Dict[str, Any]]:
        """
        Gather Sutra state from SutraSense (OPUS-054).

        📜 SUTRA SENSE: The Third Eye of MANAS
        Doc/Code gap detection for documentation curation.

        Bhagavad Gita 9.22:
        "yoga-kṣemaṁ vahāmy aham" - I bring what is lacking
        """
        try:
            from datetime import datetime

            from vibe_core.plugins.opus_assistant.manas.cortex.sutra_sense import SutraSense

            # OPUS-092: Pass config to Sense for proper initialization
            sutra_config = self._manas_config.get("sutra_sense", {})
            sense = SutraSense(workspace=self._root, config=sutra_config)
            summary = sense.perceive_gaps(refresh=True)  # Fresh scan for OPUS.md
            gaps = sense.get_gaps()

            # Build top gaps for display
            top_gaps = []
            for gap in gaps[:5]:
                top_gaps.append(
                    {
                        "type": gap.gap_type,
                        "doc": gap.doc_path.name if gap.doc_path else None,
                        "code": gap.code_path.name if gap.code_path else None,
                        "severity": gap.severity,
                        "message": gap.description[:60] if gap.description else "",
                    }
                )

            high_severity_gaps = [g for g in gaps if g.severity in ("high", "critical")]

            # Phase 2: Hidden Code Discovery
            hidden_code = sense.discover_hidden_code()
            hidden_high = [h for h in hidden_code if h.importance == "high"]

            # Phase 2: Roadmap
            roadmap = sense.generate_roadmap()
            roadmap_preview = [
                {
                    "priority": item.priority,
                    "action": item.action,
                    "target": item.target.split("/")[-1][:25] if "/" in item.target else item.target[:25],
                    "effort": item.estimated_effort,
                }
                for item in roadmap[:5]
            ]

            # Phase 2: Intent Clusters
            clusters = sense.get_clusters(min_intents=3)

            return {
                # Phase 1: Gap Detection
                "total_docs": summary.total_docs,
                "docs_with_harness": summary.docs_with_harness,
                "docs_without_harness": summary.docs_without_harness,
                "gaps_count": summary.gaps_found,
                "health_ratio": summary.health_ratio,
                "health_pct": int(summary.health_ratio * 100),
                "critical_gaps": len(high_severity_gaps),
                "top_gaps": top_gaps,
                # Phase 2: Proactive Mode
                "hidden_code_count": len(hidden_code),
                "hidden_code_high": len(hidden_high),
                "roadmap_count": len(roadmap),
                "roadmap_preview": roadmap_preview,
                "cluster_count": len(clusters),
                "clusters": [{"topic": c.topic, "intents": c.intent_count} for c in clusters[:3]],
                # Freshness indicator
                "last_scan": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "phase": 2,
            }
        except Exception as e:
            logger.debug(f"Failed to gather sutra: {e}")
            return None

    def _gather_sankalpa(self) -> Optional[Dict[str, Any]]:
        """
        Gather SANKALPA status (OPUS-055: Strategic Will).

        🎯 SANKALPA: The Will of MANAS
        Mission tracking, goal formation, and strategic planning.

        Bhagavad Gita 6.24:
        "sankalpa-prabhavān kāmāṁs tyaktvā sarvān aśeṣataḥ"
        Abandoning all desires born of sankalpa (determination)...

        Maps to config/interface.yaml sections:
        - current_goal → Active mission goal
        - phase_status → Mission execution phase
        - extraction_log → Learning/observations (future)
        - next_actions → Planned actions from planner
        """
        try:
            from vibe_core.plugins.opus_assistant.manas.cortex.sankalpa import (
                MissionStatus,
                SankalpaOrchestrator,
            )

            # Get SANKALPA orchestrator
            sankalpa_config = self._manas_config.get("sankalpa", {})
            orchestrator = SankalpaOrchestrator(workspace=self._root, config=sankalpa_config)
            status = orchestrator.get_status()

            # Extract current goal from active mission
            current_goal = "No active mission"
            phase_status = "IDLE"
            active_missions = []

            missions = status.get("missions", [])
            for m in missions:
                if m.get("status") == "active":
                    active_missions.append(m)
                    if current_goal == "No active mission":
                        current_goal = m.get("name", "Unnamed mission")
                        phase_status = "ACTIVE"

            # Get next actions from planner
            next_actions = []
            try:
                intents = orchestrator.think(context={}, idle_minutes=0, pending_intents=0)
                for intent in intents[:3]:
                    next_actions.append(
                        {
                            "action": intent.action if hasattr(intent, "action") else str(intent),
                            "priority": intent.priority if hasattr(intent, "priority") else "medium",
                        }
                    )
            except Exception:
                pass

            return {
                "current_goal": current_goal,
                "phase_status": phase_status,
                "total_missions": status.get("total_missions", 0),
                "active_missions": status.get("active_missions", 0),
                "total_strategies": status.get("total_strategies", 0),
                "enabled_strategies": status.get("enabled_strategies", 0),
                "missions": missions[:5],  # Top 5 missions for display
                "next_actions": next_actions,
            }

        except Exception as e:
            logger.debug(f"Failed to gather sankalpa: {e}")
            return {
                "current_goal": "SANKALPA unavailable",
                "phase_status": "ERROR",
                "total_missions": 0,
                "active_missions": 0,
                "total_strategies": 0,
                "enabled_strategies": 0,
                "missions": [],
                "next_actions": [],
            }

    def _gather_manas_status(self) -> Optional[Dict[str, Any]]:
        """
        Gather MANAS cognitive status for brain transparency (OPUS-133).

        🧠 MANAS NEURAL STATUS: Shows what MANAS is thinking and learning.

        Includes:
        - Online/offline status
        - Intent buffer (pending, executed, rejected)
        - Harness health (documentation coverage)
        - Neural Learning status (OPUS-133):
            - Synaptic weights and learning rates
            - Viveka decisions (dharmic evaluations)
            - Prabhupada Patch metrics (Vairagya, Nishkama, Prasadam)

        This enables full transparency into the AI's cognitive state.
        """
        try:
            import json
            from datetime import datetime

            manas_status: Dict[str, Any] = {
                "online": False,
                "intent_buffer": {
                    "pending": [],
                    "executed": [],
                    "rejected": [],
                    "total_pending": 0,
                    "last_updated": None,
                },
                "harness_health": None,
                "last_thought": None,
                "neural_learning": None,  # OPUS-133: Neural learning stats
            }

            # Check if kernel is running MANAS
            if self._kernel:
                try:
                    opus_plugin = self._kernel.get_plugin("opus_assistant")
                    if opus_plugin and hasattr(opus_plugin, "_tick_handler"):
                        manas = opus_plugin._tick_handler.get_manas()
                        if manas:
                            manas_status["online"] = True
                            buffer = manas.get_intent_buffer_for_opus()
                            manas_status["intent_buffer"] = {
                                "pending": buffer.get("pending", []),
                                "executed": buffer.get("recent_executed", []),
                                "rejected": [],
                                "total_pending": buffer.get("total_pending", 0),
                                "last_updated": datetime.utcnow().isoformat(),
                            }
                            manas_status["last_thought"] = buffer.get("last_thought")
                except Exception as e:
                    logger.debug(f"Failed to get live MANAS status: {e}")

            # OPUS-168: Check for existing MANAS instance (GAD-000: Don't create expensive instances for status)
            # Pattern: Check has_instance() first (cheap), only then get_instance() (reuses existing)
            if not manas_status["online"]:
                try:
                    from vibe_core.plugins.opus_assistant.manas import CognitiveKernel

                    # GAD-000: Only access existing instance, don't create new one for dashboard
                    if CognitiveKernel.has_instance(workspace=self._root):
                        manas = CognitiveKernel.get_instance(workspace=self._root)
                        manas_status["online"] = True
                        buffer = manas.get_intent_buffer_for_opus()
                        manas_status["intent_buffer"] = {
                            "pending": buffer.get("pending", []),
                            "executed": buffer.get("recent_executed", []),
                            "rejected": [],
                            "total_pending": buffer.get("total_pending", 0),
                            "last_updated": datetime.utcnow().isoformat(),
                        }
                        manas_status["last_thought"] = buffer.get("last_thought")
                    # If no instance exists, MANAS is truly offline - rely on persisted state below
                except Exception as e:
                    logger.debug(f"Failed to get existing MANAS status: {e}")

            # Read persisted state from .opus_state/manas_intents.json
            intents_path = self._root / ".opus_state" / "manas_intents.json"
            if intents_path.exists():
                try:
                    data = json.loads(intents_path.read_text())
                    if not manas_status["online"]:
                        # Use persisted data if kernel not running
                        manas_status["intent_buffer"]["pending"] = data.get("pending", [])
                        manas_status["intent_buffer"]["total_pending"] = len(data.get("pending", []))
                    manas_status["intent_buffer"]["executed"] = data.get("executed", [])[-10:]
                    manas_status["intent_buffer"]["rejected"] = data.get("rejected", [])[-5:]
                    manas_status["intent_buffer"]["last_updated"] = data.get("last_updated")
                except Exception:
                    pass

            # =================================================================
            # OPUS-133: NEURAL LEARNING STATUS
            # =================================================================
            neural_learning = self._gather_neural_learning()
            if neural_learning:
                manas_status["neural_learning"] = neural_learning

            # Harness health (documentation coverage)
            try:
                from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

                engine = VerificationEngine(workspace_root=self._root)
                report = engine.run_verification(quick=True)
                manas_status["harness_health"] = {
                    "total_files": report.get("docs_with_harness", 0) + report.get("docs_without_harness", 0),
                    "with_harness": report.get("docs_with_harness", 0),
                    "coverage_percent": report.get("total_score", 0),
                    "broken_harness": len([d for d in report.get("docs", []) if d.get("score", 100) < 50]),
                    "broken_files": [],
                    "sanskrit_missing": [],
                }
            except Exception:
                pass

            return manas_status

        except Exception as e:
            logger.debug(f"Failed to gather MANAS status: {e}")
            return None

    def _gather_neural_learning(self) -> Optional[Dict[str, Any]]:
        """
        OPUS-133: Gather neural learning status from VivekaAction.

        Returns synaptic weights, learning rates, Prabhupada Patch metrics,
        and OPERATIONAL TIMESTAMPS for sysadmin reliability.
        """
        try:
            import json
            import os
            from datetime import datetime

            neural: Dict[str, Any] = {
                "synapses": {
                    "total_triggers": 0,
                    "total_connections": 0,
                    "avg_weight": 0.5,
                    "high_confidence": 0,  # Weight > 0.8
                    "low_confidence": 0,  # Weight < 0.3
                },
                "learning_rates": {
                    "success": 0.05,
                    "failure": -0.10,
                },
                "prabhupada_patch": {
                    "vairagya_threshold": 0.95,
                    "vairagya_decay": 0.99,
                    "nishkama_duties": [],
                    "prasadam_threshold": 0.8,
                },
                "recent_decisions": [],
                # ====================================================
                # OPERATIONAL TIMESTAMPS (Sysadmin transparency)
                # ====================================================
                "ops": {
                    "last_synapse_update": None,
                    "last_vairagya_prune": None,
                    "last_vairagya_count": 0,
                    "last_reinforcement": None,
                    "last_decision": None,
                    "synapses_file_mtime": None,
                    "decisions_file_mtime": None,
                },
                "last_reinforcement": None,  # Legacy compat
            }

            # Read synapses from .opus_state/synapses.json
            synapses_path = self._root / ".opus_state" / "synapses.json"
            if synapses_path.exists():
                try:
                    # Get file modification time for ops transparency
                    mtime = os.path.getmtime(synapses_path)
                    neural["ops"]["synapses_file_mtime"] = datetime.fromtimestamp(mtime).isoformat()

                    data = json.loads(synapses_path.read_text())
                    triggers = data.get("triggers", [])
                    neural["synapses"]["total_triggers"] = len(triggers)

                    # Read operational metadata
                    meta = data.get("meta", {})
                    neural["ops"]["last_synapse_update"] = meta.get("last_synapse_update")
                    neural["ops"]["last_vairagya_prune"] = meta.get("last_vairagya_prune")
                    neural["ops"]["last_vairagya_count"] = meta.get("last_vairagya_count", 0)

                    all_weights = []
                    total_connections = 0
                    latest_learned_at = None

                    for trigger in triggers:
                        connections = trigger.get("connections", [])
                        total_connections += len(connections)
                        for conn in connections:
                            weight = conn.get("weight", 0.5)
                            all_weights.append(weight)
                            # Track latest learned_at timestamp
                            learned_at = conn.get("learned_at")
                            if learned_at and (not latest_learned_at or learned_at > latest_learned_at):
                                latest_learned_at = learned_at

                    neural["synapses"]["total_connections"] = total_connections
                    neural["synapses"]["latest_learned_at"] = latest_learned_at

                    if all_weights:
                        neural["synapses"]["avg_weight"] = sum(all_weights) / len(all_weights)
                        neural["synapses"]["high_confidence"] = len([w for w in all_weights if w > 0.8])
                        neural["synapses"]["low_confidence"] = len([w for w in all_weights if w < 0.3])
                except Exception as e:
                    logger.debug(f"Failed to read synapses: {e}")

            # Read last reinforcement tracking
            reinforce_path = self._root / ".opus_state" / "last_reinforcement.json"
            if reinforce_path.exists():
                try:
                    data = json.loads(reinforce_path.read_text())
                    neural["ops"]["last_reinforcement"] = data
                    neural["last_reinforcement"] = data  # Legacy compat
                except Exception:
                    pass

            # Read recent Viveka decisions from .opus_state/viveka_decisions.json
            decisions_path = self._root / ".opus_state" / "viveka_decisions.json"
            if decisions_path.exists():
                try:
                    # Get file modification time
                    mtime = os.path.getmtime(decisions_path)
                    neural["ops"]["decisions_file_mtime"] = datetime.fromtimestamp(mtime).isoformat()

                    data = json.loads(decisions_path.read_text())
                    # viveka_decisions.json is a LIST, not {"decisions": [...]}
                    decisions = data if isinstance(data, list) else data.get("decisions", [])
                    decisions = decisions[-10:]  # Last 10

                    if decisions:
                        neural["ops"]["last_decision"] = decisions[-1].get("timestamp")

                    neural["recent_decisions"] = [
                        {
                            "intent": d.get("intent_type", "?"),
                            "decision": d.get("decision", "?"),
                            "dharmic_score": d.get("dharmic_score", 0),
                            "timestamp": d.get("timestamp", ""),  # Full timestamp, template handles truncation
                        }
                        for d in decisions
                    ]
                except Exception as e:
                    logger.debug(f"Failed to read decisions: {e}")

            # Get Prabhupada Patch constants from viveka_action.py
            try:
                from vibe_core.plugins.opus_assistant.manas.cortex.viveka_action import (
                    DHARMIC_DUTIES,
                    PRASADAM_THRESHOLD,
                    VAIRAGYA_DECAY,
                    VAIRAGYA_THRESHOLD,
                )

                neural["prabhupada_patch"]["vairagya_threshold"] = VAIRAGYA_THRESHOLD
                neural["prabhupada_patch"]["vairagya_decay"] = VAIRAGYA_DECAY
                neural["prabhupada_patch"]["prasadam_threshold"] = PRASADAM_THRESHOLD
                neural["prabhupada_patch"]["nishkama_duties"] = list(DHARMIC_DUTIES)[:5]
            except ImportError:
                pass

            return neural

        except Exception as e:
            logger.debug(f"Failed to gather neural learning: {e}")
            return None

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

    def _gather_dependency_graph(self) -> Dict[str, Any]:
        """
        Gather module dependency graph for codebase navigation.

        🎯 SENIOR AI COCKPIT: This helps AI and humans understand
        which modules import which, revealing the architecture.

        Returns:
            {
                "nodes": [{"id": "plugins", "size": 108}, ...],
                "edges": [{"from": "plugins", "to": "state", "weight": 5}, ...],
                "critical_modules": ["state", "plugins"],  # Most imported
                "leaf_modules": ["scripts"],  # No dependents
            }
        """
        vibe_core = self._root / "vibe_core"
        if not vibe_core.exists():
            return {"nodes": [], "edges": [], "critical_modules": [], "leaf_modules": []}

        # Build import graph by scanning files
        import_counts: Dict[str, int] = {}  # module -> times imported
        edges: Dict[str, Dict[str, int]] = {}  # from -> {to -> count}

        for py_file in vibe_core.glob("**/*.py"):
            if "__pycache__" in str(py_file) or "archive" in str(py_file):
                continue

            # Get source module
            try:
                rel_path = py_file.relative_to(vibe_core)
                source_module = str(rel_path.parts[0]) if len(rel_path.parts) > 1 else None
            except ValueError:
                continue

            if not source_module:
                continue

            # Scan for imports
            try:
                content = py_file.read_text()
                for line in content.split("\n"):
                    if "from vibe_core." in line or "import vibe_core." in line:
                        # Extract target module
                        if "from vibe_core." in line:
                            target = line.split("from vibe_core.")[1].split(".")[0].split(" ")[0]
                        else:
                            target = line.split("import vibe_core.")[1].split(".")[0].split(" ")[0]

                        if target and target != source_module:
                            import_counts[target] = import_counts.get(target, 0) + 1

                            if source_module not in edges:
                                edges[source_module] = {}
                            edges[source_module][target] = edges[source_module].get(target, 0) + 1
            except Exception:
                pass

        # Build nodes with sizes (from module index)
        nodes = []
        for item in sorted(vibe_core.iterdir()):
            if item.name.startswith(("_", ".")) or not item.is_dir():
                continue
            py_files = list(item.glob("**/*.py"))
            file_count = len([f for f in py_files if "__pycache__" not in str(f)])
            nodes.append({"id": item.name, "size": file_count})

        # Convert edges to list format
        edge_list = []
        for source, targets in edges.items():
            for target, weight in targets.items():
                edge_list.append({"from": source, "to": target, "weight": weight})

        # Sort to find most critical and least connected
        sorted_by_imports = sorted(import_counts.items(), key=lambda x: -x[1])
        critical = [m for m, _ in sorted_by_imports[:5]]

        all_sources = set(edges.keys())
        leaf_modules = [n["id"] for n in nodes if n["id"] not in all_sources]

        return {
            "nodes": nodes,
            "edges": sorted(edge_list, key=lambda x: -x["weight"])[:20],  # Top 20 edges
            "critical_modules": critical,
            "leaf_modules": leaf_modules[:5],
        }

    def update_ai_section(self, section: str, content: str) -> bool:
        """
        OPUS-106: Update @AI sections in OPUS.md directly.

        Uses config-driven markers from config/interface.yaml ownership_types.ai

        Args:
            section: Section ID (e.g., "current_work", "blockers")
            content: New content for the section

        Returns:
            True if updated successfully
        """
        if not self._opus_path.exists():
            logger.warning("OPUS.md does not exist - cannot update AI section")
            return False

        try:
            # Load ownership markers from config (OPUS-106: Config-driven, not hardcoded)
            interface_config = self._load_interface_config()
            ai_ownership = interface_config.get("ownership_types", {}).get("ai", {})
            marker_start_tpl = ai_ownership.get("marker_start", "<!-- @AI:{id} -->")
            marker_end = ai_ownership.get("marker_end", "<!-- /@AI -->")

            # Build markers for this section
            marker_start = marker_start_tpl.replace("{id}", section)

            opus_content = self._opus_path.read_text()

            # Find section by markers
            start_idx = opus_content.find(marker_start)
            if start_idx == -1:
                logger.warning(f"Could not find @AI:{section} section in OPUS.md")
                return False

            end_idx = opus_content.find(marker_end, start_idx)
            if end_idx == -1:
                logger.warning(f"Could not find end marker for @AI:{section}")
                return False

            # Find the content area (after header line and comment)
            section_start = start_idx + len(marker_start)
            section_text = opus_content[section_start:end_idx]

            # Replace everything between start marker and end marker
            # Preserve the header line if present
            lines = section_text.split("\n")
            header_line = ""
            comment_line = ""
            for i, line in enumerate(lines):
                if line.startswith("## "):
                    header_line = line
                elif line.startswith("<!-- ") and not line.startswith("<!-- @"):
                    comment_line = line
                    break

            # Build new section content
            new_section = f"\n{header_line}\n\n{comment_line}\n{content}\n"

            # Replace
            updated_opus = opus_content[:section_start] + new_section + opus_content[end_idx:]

            # Write back
            self._opus_path.write_text(updated_opus)
            logger.info(f"✍️ OPUS.md @AI:{section} updated")
            return True

        except Exception as e:
            logger.error(f"Failed to update @AI:{section}: {e}")
            return False

    def _load_interface_config(self) -> Dict[str, Any]:
        """Load interface config from config/interface.yaml."""
        config_path = self._root / "config" / "interface.yaml"
        try:
            if config_path.exists():
                return yaml.safe_load(config_path.read_text()) or {}
        except Exception:
            pass
        return {}

    def get_ai_section(self, section: str) -> Optional[str]:
        """
        OPUS-106: Read current value of an @AI section.

        Uses config-driven markers from config/interface.yaml

        Args:
            section: Section ID (e.g., "current_work", "blockers")

        Returns:
            Current content or None (filters out placeholder values)
        """
        if not self._opus_path.exists():
            return None

        try:
            # Load ownership markers from config
            interface_config = self._load_interface_config()
            ai_ownership = interface_config.get("ownership_types", {}).get("ai", {})
            marker_start_tpl = ai_ownership.get("marker_start", "<!-- @AI:{id} -->")
            marker_end = ai_ownership.get("marker_end", "<!-- /@AI -->")

            marker_start = marker_start_tpl.replace("{id}", section)

            opus_content = self._opus_path.read_text()

            start_idx = opus_content.find(marker_start)
            if start_idx == -1:
                return None

            end_idx = opus_content.find(marker_end, start_idx)
            if end_idx == -1:
                return None

            section_text = opus_content[start_idx + len(marker_start) : end_idx]

            # Extract actual content (skip header and comment lines)
            lines = section_text.strip().split("\n")
            content_lines = []
            skip_header = True
            for line in lines:
                if skip_header:
                    if line.startswith("## ") or line.startswith("<!-- ") or not line.strip():
                        continue
                    skip_header = False
                content_lines.append(line)

            content = "\n".join(content_lines).strip()

            # Filter out placeholders (italic markdown)
            if content.startswith("_") and content.endswith("_"):
                return None

            return content if content else None

        except Exception:
            return None

    def _extract_preserved_sections(self) -> Dict[str, str]:
        """Extract @AI and @HUMAN sections from existing OPUS.md."""
        preserved = {}

        if not self._opus_path.exists():
            return preserved

        try:
            content = self._opus_path.read_text()

            # Extract AI sections (tactical + strategic SANKALPA)
            ai_sections = [
                "current_work",
                "blockers",  # Tactical (CognitiveWeaver)
                "current_goal",
                "phase_status",
                "extraction_log",  # Strategic (SANKALPA)
            ]
            for section_name in ai_sections:
                # Try both ## and ### headers
                pattern = rf"<!-- @AI:{section_name} -->\s*\n###? [^\n]+\n\n<!-- [^>]* -->\n(.*?)<!-- /@AI -->"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    preserved[section_name] = match.group(1).strip()

            # Extract HUMAN sections
            human_sections = ["notes", "next_actions"]
            for section_name in human_sections:
                pattern = rf"<!-- @HUMAN:{section_name} -->\s*\n## [^\n]+\n\n<!-- [^>]* -->\n(.*?)<!-- /@HUMAN -->"
                match = re.search(pattern, content, re.DOTALL)
                if match:
                    preserved[section_name] = match.group(1).strip()

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
        """Fallback content if Jinja2 unavailable - NO LEGACY!"""
        from datetime import datetime

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# OPUS - System State

> ⚠️ **ERROR** - Jinja2 template rendering failed

Install Jinja2: `pip install jinja2`

---

<!-- @AI:current_work -->
## Current Work

<!-- AI: Update this with what you're working on -->
_Jinja2 required for full rendering_
<!-- /@AI -->

---
*Fallback render | {timestamp} UTC*
"""

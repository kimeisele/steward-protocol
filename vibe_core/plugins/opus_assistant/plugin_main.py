"""
OPUS Assistant Plugin - Active manager for OPUS.md ecosystem.

OPUS-029 Phase 2: Dynamic Runtime Context Injection

Architecture (GAD-000 Compliant):
    ┌─────────────────────────────────┐
    │      Interface Plugin           │  ← RENDERS (rich, markdown)
    │      (Frontend)                 │
    └──────────────┬──────────────────┘
                   │ calls
                   ▼
    ┌─────────────────────────────────┐
    │      opus_assistant Plugin      │  ← DATA ONLY (dicts, no rendering)
    │      (Backend)                  │
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ ConfigLoader            │    │  ← Fraktale Config
    │  │ defaults.yaml + opus.yaml│   │
    │  └─────────────────────────┘    │
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ OpusContextService      │    │  ← PHASE 2: Dynamic Bootstrapping
    │  │ Synthesize + Inject     │    │     "State of Mind" for all agents
    │  └─────────────────────────┘    │
    │                                 │
    │  ┌─────────────────────────┐    │
    │  │ KernelTickHandler       │    │  ← Heartbeat via EventBus
    │  │ Stays ALIVE             │    │     Triggers context synthesis
    │  └─────────────────────────┘    │
    └─────────────────────────────────┘

Config Hierarchy:
1. defaults.yaml (shipped with plugin)
2. config/opus.yaml (system overrides)
3. Runtime overrides

Phase 2 - Dynamic Context:
- On KERNEL_TICK: Synthesize system state from all Prakriti layers
- Inject into EphemeralState as "State of Mind"
- Every spawning agent knows the current reality
- This is ACTIVE, not passive!

OPUS-015: Container-ready (.vibe packable)
"""

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.protocols import OpusAssistantProtocol

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader
    from vibe_core.plugins.opus_assistant.core.context_service import OpusContextService
    from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector
    from vibe_core.plugins.opus_assistant.core.observation_logger import ObservationLogger
    from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator
    from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine
    from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler
    from vibe_core.plugins.opus_assistant.events.syscall_listener import SyscallListener

logger = logging.getLogger("OPUS_ASSISTANT")


class OpusAssistantPlugin(KernelPlugin, OpusAssistantProtocol):
    """
    OPUS Assistant - Active manager for OPUS.md ecosystem.

    IMPORTANT: This plugin provides DATA ONLY.
    The interface plugin is the MASTER for rendering.
    We NEVER render markdown, rich panels, or any UI.

    Phase 2 Capabilities:
    - opus.verify: Run @HARNESS verification
    - opus.drift_detect: Compare code vs docs
    - opus.generate: Generate OPUS.md data
    - opus.preserve: Get preserved sections from existing OPUS.md
    - opus.tick: Respond to kernel tick events
    - opus.context: Dynamic runtime context synthesis
    - opus.prompt: Get system prompt fragment for agents
    """

    @property
    def plugin_id(self) -> str:
        return "opus_assistant"

    @property
    def priority(self) -> int:
        return 50  # After interface (10), before most others

    @property
    def pulse_phase(self):
        """OPUS-087 PRANA: Run in SENSORS phase to collect data first."""
        from vibe_core.plugin_protocol import PulsePhase

        return PulsePhase.SENSORS

    def __init__(self):
        """Initialize plugin state."""
        self._kernel: Optional["RealVibeKernel"] = None
        self._workspace: Optional[Path] = None
        self._config: Dict[str, Any] = {}
        self._config_loader: Optional["ConfigLoader"] = None
        self._tick_handler: Optional["KernelTickHandler"] = None
        self._syscall_listener: Optional["SyscallListener"] = None

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Initialize OPUS Assistant on kernel boot.

        1. Get workspace path
        2. Load fraktale config (defaults + opus.yaml)
        3. Subscribe to kernel tick (EventBus)
        4. Quick health check
        5. 🔌 WIRING: Save session state (Fractal Holon - "untötbar")
        6. 🔌 WIRING: Trigger genesis check for karma-aware boot
        7. OPUS-112: Register MANAS for system tool access
        """
        self._kernel = kernel

        # Register in DI container
        ServiceRegistry.register(OpusAssistantProtocol, self)

        # Get workspace path
        self._workspace = getattr(kernel, "workspace_path", None) or Path.cwd()

        # OPUS-112: Register MANAS as system-level agent for tool access
        self._register_manas_capabilities(kernel)

        # OPUS-306: MANAS boot deferred to first use for faster startup
        # The CognitiveKernel singleton is created but NOT booted here.
        # It will boot lazily on first tick() or perceive() call.
        # This saves ~17 seconds of boot time.
        self._manas_kernel_ref = kernel  # Store for lazy init

        # Load fraktale config
        self._load_fraktale_config()

        # Subscribe to kernel tick
        self._setup_kernel_tick()

        # OPUS-031 Layer 2: Subscribe to SYSCALL_EXECUTED events for Experience Replay
        self._setup_syscall_listener()

        # Quick health check on boot
        if self._config.get("drift", {}).get("check_on_boot", False):
            drift = self.quick_drift_check()
            if not drift.get("healthy", True):
                logger.warning(f"⚠️ OPUS drift: {len(drift.get('missing_files', []))} missing files")

        # OPUS-029 Phase 6: Register as PromptContext provider
        # This is the SCALABLE pattern - plugins register their own resolvers
        # WITHOUT modifying core files!
        self._register_context_provider()

        # 🔌 WIRING: Save initial session state (Fractal Holon - "untötbar")
        self._init_session_state()

        # 🔌 WIRING: Trigger genesis check for karma-aware boot
        # OPUS-307 Phase I.3: Removed duplicate _setup_kernel_tick() and _setup_syscall_listener()
        # They are already called at lines 145 and 148. Double subscription causes double events!
        if not self._is_test_mode():
            # Synthesize initial state
            self.synthesize_context()

        logger.info(f"🎯 OPUS Assistant online (Workspace: {self._workspace})")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Cleanup on kernel shutdown."""
        # 🔌 WIRING: Save final session state before shutdown
        self._save_session_state()

        # Unsubscribe from events
        if self._tick_handler:
            self._tick_handler.unsubscribe()
        if self._syscall_listener:
            self._syscall_listener.unsubscribe()

        logger.info("🎯 OPUS Assistant shutdown (session state saved)")

    # =========================================================================
    # OPUS-112: MANAS CAPABILITY REGISTRATION (VEDA-4)
    # =========================================================================

    def _register_manas_capabilities(self, kernel: "RealVibeKernel") -> None:
        """
        OPUS-112: Register MANAS as agent with capabilities from manifest.

        VEDA-4 Compliant: Reads capabilities from manifest.json, not hardcoded.
        This enables MANAS to dispatch to kernel.tool_registry for SYSTEM ACT.

        Note: Kernel auto-registers PLUGIN capabilities. This method registers
        MANAS specifically because it has its own agent_id distinct from the plugin.
        """
        import json

        # Read capabilities from manifest (VEDA-4: config-driven, not hardcoded)
        manifest_path = Path(__file__).parent / "manifest.json"
        if not manifest_path.exists():
            logger.warning("⚠️ OPUS-112: manifest.json not found, MANAS capabilities not registered")
            return

        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            manas_caps_config = manifest.get("manas_capabilities", {})

            # Flatten capability lists from the config
            all_caps = []
            for key, value in manas_caps_config.items():
                if key.startswith("_"):  # Skip comments
                    continue
                if isinstance(value, list):
                    all_caps.extend(value)

            if all_caps and hasattr(kernel, "_capability_registry"):
                kernel._capability_registry.register_agent("manas", all_caps)
                logger.info(f"⚡ OPUS-112: MANAS registered with {len(all_caps)} capabilities")
            else:
                logger.debug("⚡ OPUS-112: No MANAS capabilities to register or no registry")

        except Exception as e:
            logger.warning(f"⚠️ OPUS-112: Failed to register MANAS capabilities: {e}")

    # =========================================================================
    # OPUS-087 PRANA: PULSE LIFECYCLE (Macro-Cycle / Heartbeat)
    # =========================================================================

    async def on_pulse(self, kernel, transaction):
        """
        OPUS-087 PRANA: Refresh OPUS.md during heartbeat pulse.
        OPUS-212: Trigger MANAS cognitive cycle during pulse.
        OPUS-308: Now uses ManifestationService for rendering.

        This runs every 15 minutes via GitHub Actions (headless mode).
        Collects system state and registers mutation for OPUS.md update.
        """
        from vibe_core.plugin_protocol import HookResult
        from vibe_core.prana_orchestrator import StateMutation

        try:
            # 1. Trigger COGNITION (MANAS)
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols import CognitiveKernelProtocol

                manas = ServiceRegistry.get(CognitiveKernelProtocol)
                if manas:
                    logger.info("   + MANAS: Triggering cognitive tick...")
                    manas.tick()
            except Exception as e:
                logger.warning(f"   ⚠️ MANAS tick failed during pulse: {e}")

            # 2. OPUS-308: Use ManifestationService for rendering
            # Get data via get_manifestation_data(), render via service template
            workspace = self._workspace or Path.cwd()
            template_path = "vibe_core/plugins/opus_assistant/templates/opus_dashboard.md.j2"

            # Gather data (this calls OpusDashboardRenderer._gather_context internally)
            data = self.get_manifestation_data()

            # Apply control cables (bidirectional: read user edits before render)
            try:
                from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
                    OpusDashboardRenderer,
                )

                renderer = OpusDashboardRenderer(workspace_root=workspace, kernel=kernel)
                await renderer._apply_control_cables()
            except Exception as e:
                logger.debug(f"Control cables skipped: {e}")

            # Render via ManifestationService template support
            content = None
            if hasattr(kernel, "manifestation"):
                content = kernel.manifestation.render_with_template(template_path, data)

            # Fallback: direct Jinja2 render if service unavailable
            if content is None:
                try:
                    from jinja2 import Environment, FileSystemLoader, select_autoescape

                    template_dir = workspace / "vibe_core/plugins/opus_assistant/templates"
                    env = Environment(
                        loader=FileSystemLoader(str(template_dir)),
                        autoescape=select_autoescape(["html", "xml"]),
                        trim_blocks=True,
                        lstrip_blocks=True,
                    )
                    template = env.get_template("opus_dashboard.md.j2")
                    content = template.render(**data)
                except Exception as e:
                    logger.error(f"Template render failed: {e}")
                    return HookResult.error(f"OPUS render failed: {e}")

            # 3. Register mutation
            transaction.register(
                StateMutation(
                    plugin_id=self.plugin_id,
                    action="update_doc",
                    target="OPUS.md",
                    payload={"content": content},
                    priority=1,  # High priority
                )
            )

            logger.info(f"🎯 OPUS pulse: registered update_doc mutation ({len(content)} chars)")

            return HookResult.ok(data={"refreshed": True, "content_length": len(content)})

        except Exception as e:
            logger.error(f"🎯 OPUS pulse failed: {e}")
            return HookResult.error(f"OPUS refresh failed: {e}")

    def _collect_pulse_state(self, kernel) -> Dict[str, Any]:
        """
        Collect state in headless mode for pulse cycle.

        IMPORTANT: kernel may be None in GitHub Actions.
        Must work without full kernel initialization.
        """
        state = {}
        workspace = self._workspace or Path.cwd()

        # Layer 1: Git state (always available, no kernel needed)
        try:
            import subprocess

            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=5, cwd=workspace
            )
            state["git_sha"] = result.stdout.strip() if result.returncode == 0 else "unknown"

            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, timeout=5, cwd=workspace
            )
            state["git_branch"] = result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception as e:
            state["git_sha"] = "error"
            state["git_branch"] = "error"
            state["git_error"] = str(e)

        # Layer 2: File-based state (always available)
        opus_path = workspace / "OPUS.md"
        state["opus_exists"] = opus_path.exists()

        # Layer 3: Kernel state (if available)
        if kernel:
            state["kernel_running"] = True
            try:
                agents = kernel.get_agents() if hasattr(kernel, "get_agents") else []
                state["agent_count"] = len(agents)
            except Exception:
                state["agent_count"] = 0
        else:
            state["kernel_running"] = False
            state["agent_count"] = 0

        # Layer 4: Timestamp
        from datetime import datetime

        state["pulse_time"] = datetime.utcnow().isoformat()

        return state

    def _render_opus_for_pulse(self, state: Dict[str, Any]) -> str:
        """
        Render OPUS.md content from collected pulse state.

        Uses minimal rendering for headless mode - just updates timestamp
        and basic state. Full rendering happens when kernel is available.
        """
        from datetime import datetime

        workspace = self._workspace or Path.cwd()
        opus_path = workspace / "OPUS.md"

        # If OPUS.md exists, try to preserve most of it
        if opus_path.exists():
            try:
                existing = opus_path.read_text()

                # Just update the pulse timestamp in header
                import re

                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

                # Update "Last Pulse" if it exists, otherwise add it
                if "Last Pulse:" in existing:
                    updated = re.sub(r"Last Pulse:.*", f"Last Pulse: {timestamp}", existing)
                else:
                    # Add after first heading
                    updated = re.sub(r"(# OPUS.*\n)", f"\\1\n> Last Pulse: {timestamp}\n", existing, count=1)

                return updated
            except Exception as e:
                logger.warning(f"Could not update existing OPUS.md: {e}")

        # Generate minimal OPUS.md for new files
        return f"""# OPUS - System Dashboard

> Last Pulse: {state.get("pulse_time", "unknown")}

## System State

- Git: `{state.get("git_branch", "unknown")}` @ `{state.get("git_sha", "unknown")}`
- Kernel: {"Running" if state.get("kernel_running") else "Offline"}
- Agents: {state.get("agent_count", 0)}

---

*Generated by OPUS-087 PRANA Pulse*
"""

    def _is_test_mode(self) -> bool:
        """Check if running in pytest - skip some operations in tests."""
        return bool(os.environ.get("PYTEST_CURRENT_TEST"))

    def _init_session_state(self) -> None:
        """
        🔌 WIRING: Initialize and save session state on boot.

        This makes the system "untötbar" - it remembers sessions.
        Loads previous session karma to inform boot mode.
        """
        import uuid
        from datetime import datetime

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import (
                SessionState,
                get_state_manager,
            )

            state_mgr = get_state_manager()

            # Load previous karma to inform boot mode
            last_karma = state_mgr.get_last_karma()

            # Determine boot mode from last karma
            boot_mode = "full_power"
            if last_karma:
                if last_karma.score < 40:
                    boot_mode = "safe_mode"
                elif last_karma.score < 70:
                    boot_mode = "cautious_mode"

            # Create new session
            session = SessionState(
                session_id=str(uuid.uuid4())[:8],
                started_at=datetime.utcnow().isoformat(),
                last_karma_score=last_karma.score if last_karma else 100,
                observation_count=0,
                boot_mode=boot_mode,
            )

            state_mgr.save_session(session)
            logger.info(f"📍 Session {session.session_id} started (boot_mode: {boot_mode})")

        except Exception as e:
            logger.warning(f"Could not init session state: {e}")

    def _save_session_state(self) -> None:
        """
        🔌 WIRING: Save session state on shutdown.

        Updates observation count and karma before exit.
        """
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager()

            # Load current session
            session = state_mgr.load_session()
            if not session:
                return

            # Update with latest karma
            last_karma = state_mgr.get_last_karma()
            if last_karma:
                session.last_karma_score = last_karma.score

            # Update observation count
            observations = state_mgr.get_observations()
            session.observation_count = len(observations)

            # Save updated session
            state_mgr.save_session(session)
            logger.debug(f"💾 Session {session.session_id} saved (karma: {session.last_karma_score})")

        except Exception as e:
            logger.warning(f"Could not save session state: {e}")

    def _trigger_genesis_check(self) -> None:
        """
        🔌 WIRING: Trigger genesis check circuit on boot.

        This makes the system karma-aware from the first moment.
        """
        try:
            if self._tick_handler:
                import asyncio

                # Get the genesis check method
                async def run_genesis():
                    result = await self._tick_handler._check_session_karma({"lookback_hours": 24})
                    if result.get("is_critical"):
                        logger.warning(f"⚠️ GENESIS: Critical karma detected ({result.get('score')}/100)")
                    elif result.get("has_warnings"):
                        logger.info(f"🔶 GENESIS: Cautious boot ({result.get('score')}/100)")
                    else:
                        logger.info(f"🟢 GENESIS: Full power boot ({result.get('score')}/100)")

                # Try to run the genesis check
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(run_genesis())
                    else:
                        loop.run_until_complete(run_genesis())
                except RuntimeError:
                    asyncio.run(run_genesis())

        except Exception as e:
            logger.debug(f"Genesis check skipped: {e}")

    def _load_fraktale_config(self) -> None:
        """
        Load config using fraktale pattern.

        Merges: defaults.yaml (plugin) + opus.yaml (system)
        """
        from vibe_core.plugins.opus_assistant.core.config_loader import ConfigLoader

        self._config_loader = ConfigLoader(workspace_root=self._workspace or Path.cwd())
        self._config = self._config_loader.load()

        logger.debug(f"Loaded config: {list(self._config.keys())}")

    def _setup_kernel_tick(self) -> None:
        """
        Setup kernel tick handler.

        Subscribes to EventBus for constant context feed.
        """
        if not self._config.get("kernel_tick", {}).get("enabled", True):
            logger.debug("Kernel tick disabled in config")
            return

        try:
            from vibe_core.plugins.opus_assistant.events.kernel_tick import KernelTickHandler

            self._tick_handler = KernelTickHandler(self)
            if self._tick_handler.subscribe():
                logger.debug("Kernel tick handler active")
        except ImportError:
            logger.debug("EventBus not available - tick handler disabled")
        except Exception as e:
            logger.debug(f"Could not setup kernel tick: {e}")

    def _setup_syscall_listener(self) -> None:
        """
        OPUS-031 Layer 2: Setup syscall listener for Experience Replay.

        Subscribes to SYSCALL_EXECUTED events from EventBus.
        This is the "synapse" that connects core syscall execution to
        the plugin's long-term memory (Experience Replay Buffer).

        ARCHITECTURE (GAD-000 Compliant):
            Core emits SYSCALL_EXECUTED → Plugin subscribes → record_syscall()
        """
        try:
            from vibe_core.plugins.opus_assistant.events.syscall_listener import SyscallListener

            self._syscall_listener = SyscallListener()
            if self._syscall_listener.subscribe():
                logger.debug("🧠 Syscall listener active (Experience Replay enabled)")
        except ImportError:
            logger.debug("EventBus not available - syscall listener disabled")
        except Exception as e:
            logger.debug(f"Could not setup syscall listener: {e}")

    def _register_context_provider(self) -> None:
        """
        Register OPUS context with PromptContext (OPUS-029 Phase 6).

        This is the SCALABLE pattern for plugin context injection:
        1. Plugin implements a resolver function
        2. Plugin registers the resolver with PromptContext
        3. Core PromptComposer includes ALL resolved plugin contexts
        4. NO modification to core files required!

        The resolver returns formatted markdown that gets injected into
        CLI prompts, giving LLM operators the "State of Mind" context.
        """
        try:
            from vibe_core.runtime.prompt_context import get_prompt_context

            prompt_context = get_prompt_context()

            # Register our resolver - it returns formatted OPUS context
            prompt_context.register("opus_context", self._resolve_opus_context)

            logger.debug("Registered opus_context resolver with PromptContext")
        except ImportError:
            logger.debug("PromptContext not available - context provider disabled")
        except Exception as e:
            logger.debug(f"Could not register context provider: {e}")

    def _resolve_opus_context(self) -> str:
        """
        Resolver function for PromptContext.

        Synthesizes dynamic "State of Mind" from Prakriti layers.
        This is what shapes agent cognition at boot - NOT a static file.

        The prompt is a VARIABLE, not a constant. It evolves with the system.

        Returns:
            Synthesized state of mind from all Prakriti layers
        """
        return self._synthesize_state_of_mind()

    def _synthesize_state_of_mind(self) -> str:
        """
        Synthesize dynamic 'State of Mind' from Prakriti layers.

        OPUS-029: This is the core of cognitive bootstrapping.
        The agent's consciousness is shaped by LIVE system state.

        Layers:
            1. Sthula (Physical): Git state, files, ledger
            2. Prana (Runtime): Kernel, agents, session
            3. Purusha (Identity): Ephemeral thoughts, persona

        Plus: Available circuits, OPUS health, current focus.
        """
        import re

        import yaml

        workspace = self._workspace or Path.cwd()
        sections = []

        # === LAYER 1: STHULA (Physical Reality) ===
        try:
            from vibe_core.state.prakriti import Prakriti

            p = Prakriti(workspace)
            git_status = p.git.status()

            layer1 = f"""**Layer 1 - Sthula (Physical):**
- Branch: `{git_status.get("branch", "unknown")}`
- HEAD: `{git_status.get("sha", "unknown")}`
- Dirty: {"⚠️ Uncommitted changes" if git_status.get("dirty") else "✅ Clean"}"""
            sections.append(layer1)
        except Exception as e:
            sections.append(f"**Layer 1 - Sthula:** ❌ {e}")

        # === LAYER 2: PRANA (Runtime) ===
        try:
            kernel_status = p.kernel.status()
            agents = p.kernel.agents()
            layer2 = f"""**Layer 2 - Prana (Runtime):**
- Kernel: {"🟢 Running" if kernel_status.get("available") else "⚪ Offline"}
- Agents: {len(agents)} active
- Session: {p.session or "Standalone"}"""
            sections.append(layer2)
        except Exception as e:
            sections.append(f"**Layer 2 - Prana:** ❌ {e}")

        # === LAYER 3: PURUSHA (Identity/Cognition) ===
        try:
            thoughts = p.ephemeral.get_thoughts()
            thought_summary = f"{len(thoughts)} thoughts" if thoughts else "Fresh mind"
            layer3 = f"""**Layer 3 - Purusha (Identity):**
- Ephemeral: {thought_summary}"""
            sections.append(layer3)
        except Exception as e:
            sections.append(f"**Layer 3 - Purusha:** ❌ {e}")

        # === CIRCUITS (Cognitive Patterns Available) ===
        try:
            circuits_dir = workspace / "vibe_core/plugins/opus_assistant/circuits"
            circuits = []
            if circuits_dir.exists():
                for cf in circuits_dir.glob("*.yaml"):
                    with open(cf) as f:
                        data = yaml.safe_load(f)
                    c = data.get("circuit", {})
                    circuits.append(c.get("id", cf.stem))

            circuit_section = f"""**Cognitive Circuits:**
- Available: {", ".join(circuits) if circuits else "None"}"""
            sections.append(circuit_section)
        except Exception as e:
            sections.append(f"**Circuits:** ❌ {e}")

        # === OPUS HEALTH (System Trust) ===
        try:
            opus_path = workspace / "OPUS.md"
            if opus_path.exists():
                with open(opus_path) as f:
                    content = f.read(2000)

                # Extract trust score
                trust_match = re.search(r"Trust Score: [🟢🟡🔴⚪]\s*(\d+)%", content)
                trust = trust_match.group(1) if trust_match else "?"

                # Extract status
                status_match = re.search(r"\*\*([⚪🟢🔴🟡])\s*(\w+)\*\*", content)
                status = status_match.group(2) if status_match else "Unknown"

                opus_section = f"""**OPUS Health:**
- Status: {status}
- Trust Score: {trust}%"""
                sections.append(opus_section)
        except Exception as e:
            sections.append(f"**OPUS Health:** ❌ {e}")

        # === SYNTHESIZE ===
        header = "🧠 **STATE OF MIND** (Synthesized from Prakriti)"
        return header + "\n\n" + "\n\n".join(sections)

    # =========================================================================
    # Public API - DATA ONLY, NO RENDERING!
    # =========================================================================

    def verify(self, quick: bool = False) -> Dict[str, Any]:
        """
        Run OPUS verification.

        Returns DATA (dict), not rendered output.

        Args:
            quick: If True, skip semantic checks (faster)

        Returns:
            Verification report dict
        """
        from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        config = self._config.get("verification", {})
        engine = VerificationEngine(workspace_root=workspace, config=config)
        return engine.run_verification(quick=quick)

    def detect_drift(self, since_commit: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect drift between code and documentation.

        Returns DATA (dict), not rendered output.

        Args:
            since_commit: Git ref to compare against (default from config)

        Returns:
            Drift report dict
        """
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        detector = DriftDetector(workspace_root=workspace)

        # Use config default if not specified
        if since_commit is None:
            since_commit = self._config.get("drift", {}).get("default_since", "HEAD~10")

        report = detector.detect(since_commit=since_commit)
        return report.to_dict()

    def quick_drift_check(self) -> Dict[str, Any]:
        """
        Quick drift check (boot-time, fast).

        Returns DATA (dict), not rendered output.

        Returns:
            Quick check results dict
        """
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        detector = DriftDetector(workspace_root=workspace)
        return detector.quick_check()

    def generate_opus_data(self, include_verification: bool = True) -> Dict[str, Any]:
        """
        Generate OPUS.md data.

        Returns DATA (dict) that the interface plugin can render.
        We do NOT write OPUS.md - that's the renderer's job!

        Args:
            include_verification: Whether to include verification results

        Returns:
            OpusData as dict
        """
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        generator = OpusGenerator(workspace_root=workspace)
        data = generator.generate(include_verification=include_verification)

        # Convert dataclass to dict for transport
        return {
            "generated_at": data.generated_at,
            "workspace": data.workspace,
            "version": data.version,
            "verification": data.verification,
            "drift": data.drift,
            "plugins": data.plugins,
            "preserved_sections": data.preserved_sections,
            "warnings": data.warnings,
        }

    def get_preserved_sections(self) -> Dict[str, str]:
        """
        Get preserved sections from existing OPUS.md.

        Human and AI sections are NEVER overwritten.

        Returns:
            Dict mapping section name to content
        """
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        generator = OpusGenerator(workspace_root=workspace)
        return generator.get_preserved_sections()

    def has_existing_opus(self) -> bool:
        """Check if OPUS.md already exists in workspace root."""
        workspace = self._workspace or Path.cwd()
        return (workspace / "OPUS.md").exists()

    # NOTE: write_opus_md() REMOVED - opus_assistant is BACKEND only
    # All file writes go through InterfacePlugin -> kernel.io
    # Use: kernel.get_plugin("interface").render_view("opus")
    # See: vibe_core/plugins/interface/renderers/opus/renderer.py

    def get_config(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get plugin config value.

        Args:
            key: Dot-notation key (e.g., "verification.enabled")
                 If None, returns entire config
            default: Default value if key not found

        Returns:
            Config value or default
        """
        if key is None:
            return self._config

        if self._config_loader:
            return self._config_loader.get(key, default)

        return default

    # =========================================================================
    # CLI Command Handlers (Delegated to Layer 2 / commands.py)
    # =========================================================================

    def cmd_approve(self, **kwargs) -> Dict[str, Any]:
        """Delegate approve command to commands.py."""
        from .cli.commands import cmd_approve

        return cmd_approve(self, **kwargs)

    def cmd_reject(self, **kwargs) -> Dict[str, Any]:
        """Delegate reject command to commands.py."""
        from .cli.commands import cmd_reject

        return cmd_reject(self, **kwargs)

    def cmd_pending(self, **kwargs) -> Dict[str, Any]:
        """Delegate pending command to commands.py."""
        from .cli.commands import cmd_pending

        return cmd_pending(self, **kwargs)

    def cmd_karma(self, **kwargs) -> Dict[str, Any]:
        """Delegate karma command to commands.py."""
        from .cli.commands import cmd_karma

        return cmd_karma(self, **kwargs)

    # =========================================================================
    # OPUS-077: THE WATCHMAN SENSOR
    # =========================================================================

    def on_tool_executed(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        params: Dict[str, Any],
        result: Any,
        success: bool,
    ) -> None:
        """
        Global Immune System Hook.

        Monitors tool execution for damage.
        If Envoy writes broken code, Pratyaya (The Reflex) reverts it.
        """
        if tool_name == "write_file" and success:
            path = params.get("path")
            if path and path.endswith(".py"):
                # Call Pratyaya Reflex
                # FIX: Use absolute import to avoid "relative import with no known parent package"
                from vibe_core.plugins.opus_assistant.manas.analyzers.pratyaya_analyzer import PratyayaAnalyzer

                # Instantiate ad-hoc for speed (stateless reflex)
                pratyaya = PratyayaAnalyzer()

                # Check syntax immediately
                if not pratyaya.verify_syntax(path):
                    import logging

                    logger = logging.getLogger("OPUS.Reflex")
                    logger.error(f"🧬 IMMUNE RESPONSE: Syntax Error detected in {path}")

                    # TRIGGER REFLEX: AUTO-ROLLBACK
                    restored = pratyaya.reflex_rollback(path)

                    if restored:
                        logger.info(f"🧬 IMMUNE RESPONSE: Damage reverted for {path}")
                    else:
                        logger.critical(f"🧬 IMMUNE RESPONSE FAILED: Could not revert {path}")

    def reload_config(self) -> Dict[str, Any]:
        """
        Force reload config from files.

        Returns:
            New merged config
        """
        if self._config_loader:
            self._config = self._config_loader.reload()
        return self._config

    # =========================================================================
    # Engine Accessors (for interface plugin)
    # =========================================================================

    def get_verification_engine(self) -> "VerificationEngine":
        """Get a VerificationEngine instance."""
        from vibe_core.plugins.opus_assistant.core.verification_logic import VerificationEngine

        workspace = self._workspace or Path.cwd()
        config = self._config.get("verification", {})
        return VerificationEngine(workspace_root=workspace, config=config)

    def get_drift_detector(self) -> "DriftDetector":
        """Get a DriftDetector instance."""
        from vibe_core.plugins.opus_assistant.core.drift_detector import DriftDetector

        workspace = self._workspace or Path.cwd()
        return DriftDetector(workspace_root=workspace)

    def get_opus_generator(self) -> "OpusGenerator":
        """Get an OpusGenerator instance."""
        from vibe_core.plugins.opus_assistant.core.opus_generator import OpusGenerator

        workspace = self._workspace or Path.cwd()
        return OpusGenerator(workspace_root=workspace)

    def get_context_service(self) -> Optional["OpusContextService"]:
        """
        Get the OpusContextService instance.

        Returns:
            OpusContextService or None if tick handler not active
        """
        if self._tick_handler:
            return self._tick_handler.get_context_service()
        return None

    # =========================================================================
    # Phase 2: Context Service API
    # =========================================================================

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """
        Get current synthesized context.

        This is the "State of Mind" - what every agent should know.

        Returns:
            Current context dict or None
        """
        if self._tick_handler:
            return self._tick_handler.get_current_context()
        return None

    def get_system_prompt_fragment(self) -> str:
        """
        Get current system prompt fragment.

        This should be prepended to agent system prompts so they
        know the current "State of Mind" of the system.

        Returns:
            System prompt fragment string (markdown)
        """
        if self._tick_handler:
            return self._tick_handler.get_system_prompt_fragment()
        return ""

    def synthesize_context(self) -> Optional[Dict[str, Any]]:
        """
        Force immediate context synthesis.

        Useful for getting fresh context outside of tick cycle.

        Returns:
            Freshly synthesized context dict or None
        """
        context_service = self.get_context_service()
        if context_service:
            context = context_service.synthesize()
            context_service.inject(context)
            return context.to_dict()
        return None

    # =========================================================================
    # GAD-000: Discoverability & Observability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """
        GAD-000 Test 1: Machine-readable capability discovery.

        Returns structured data about what this plugin can do.
        """
        context_service = self.get_context_service()

        return {
            "version": self._config.get("plugin", {}).get("version", "1.2.0"),
            "phase": self._config.get("plugin", {}).get("phase", 2),
            "operations": [
                "verify",
                "detect_drift",
                "quick_drift_check",
                "generate_opus_data",
                "get_preserved_sections",
                "has_existing_opus",
                "get_config",
                "reload_config",
                # Phase 2: Context
                "get_current_context",
                "get_system_prompt_fragment",
                "synthesize_context",
            ],
            "capabilities": [
                "opus.verify",
                "opus.drift_detect",
                "opus.generate",
                "opus.preserve",
                "opus.config",
                "opus.tick",
                # Phase 2: Dynamic Context
                "opus.context",
                "opus.prompt",
            ],
            "architecture": {
                "role": "backend",
                "renders": False,
                "provides": "data_only",
                "config_pattern": "fraktale",
                "kernel_tick": self._tick_handler is not None,
                "context_service": context_service is not None,
            },
            "workspace": str(self._workspace) if self._workspace else None,
        }

    def get_system_status(self) -> Dict[str, Any]:
        """
        GAD-000 Test 2: Observability.

        Returns current plugin status including Phase 2 context info.
        """
        status = {
            "plugin_id": "opus_assistant",
            "status": "active" if self._kernel else "inactive",
            "version": self._config.get("plugin", {}).get("version", "1.2.0"),
            "phase": self._config.get("plugin", {}).get("phase", 2),
            "workspace": str(self._workspace) if self._workspace else None,
            "has_opus_md": self.has_existing_opus() if self._workspace else False,
            "config_loaded": self._config_loader is not None,
            "kernel_tick_active": self._tick_handler is not None,
        }

        # Add quick health check if active
        if self._kernel:
            quick = self.quick_drift_check()
            status["drift_health"] = quick.get("healthy", False)
            status["tracked_files"] = quick.get("total_tracked", 0)

        # Add tick handler state if available
        if self._tick_handler:
            status["tick_state"] = self._tick_handler.get_state()

        # Phase 2: Add context service status
        context_service = self.get_context_service()
        if context_service:
            status["context_service_active"] = True
            status["context_synthesis_count"] = context_service.get_synthesis_count()
            current_context = self.get_current_context()
            if current_context:
                status["current_system_health"] = current_context.get("health", {}).get("status")
                status["context_hash"] = current_context.get("context_hash", "")[:16]
        else:
            status["context_service_active"] = False

        return status

    # =========================================================================
    # Phase 3: CLI Command Handlers
    # =========================================================================

    def cmd_opus_status(self, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:status

        Shows the current "State of Mind" - live context from the system.

        Args:
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted status dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_status_output

        # Get current context, or synthesize fresh if not available
        context = self.get_current_context()
        if context is None:
            context = self.synthesize_context()
        return format_status_output(context, json_mode=json)

    def cmd_opus_log(self, limit: int = 20, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:log

        Shows journal entries from OPUS.md (parsed observations).

        Args:
            limit: Max entries to show
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted log dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_log_output, parse_journal_from_opus

        workspace = self._workspace or Path.cwd()
        opus_path = workspace / "OPUS.md"

        observations = parse_journal_from_opus(opus_path)
        return format_log_output(observations, limit=limit, json_mode=json)

    def cmd_opus_verify(self, quick: bool = False, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:verify

        Manual trigger for verification loop.

        Args:
            quick: If True, skip semantic checks (faster)
            json: If True, return raw JSON-compatible data

        Returns:
            Formatted verification dict
        """
        from vibe_core.plugins.opus_assistant.cli.commands import format_verify_output

        verification = self.verify(quick=quick)
        return format_verify_output(verification, json_mode=json)

    def cmd_opus_refresh(self, quick: bool = True, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:refresh

        Manually regenerate OPUS.md via ManifestationService.

        OPUS-308: Now uses ManifestationService.force_manifest() instead
        of the old InterfacePlugin.render_view() flow.

        Args:
            quick: If True, skip semantic checks (faster, default)
            json: If True, return raw JSON-compatible data

        Returns:
            Result dict with path and status
        """
        import time

        start = time.time()

        # OPUS-308: Use ManifestationService for rendering
        result_path = None
        content = None

        if self._kernel and hasattr(self._kernel, "manifestation"):
            content = self._kernel.manifestation.force_manifest("opus_assistant")
            if content:
                result_path = self._workspace / "OPUS.md" if self._workspace else Path("OPUS.md")

        elapsed = time.time() - start

        if result_path is None or content is None:
            return {
                "status": "error",
                "error": "ManifestationService not available or rendering failed",
                "elapsed_ms": int(elapsed * 1000),
            }

        result = {
            "status": "success",
            "path": str(result_path),
            "elapsed_ms": int(elapsed * 1000),
            "quick_mode": quick,
        }

        if json:
            return result

        result["output"] = f"OPUS.md refreshed in {int(elapsed * 1000)}ms"
        return result

    def get_observation_logger(self) -> Optional["ObservationLogger"]:
        """
        Get the ObservationLogger instance for direct logging.

        Returns:
            ObservationLogger or None if tick handler not active
        """
        if self._tick_handler:
            return self._tick_handler.get_observation_logger()
        return None

    def cmd_opus_explore(self, query: str, limit: int = 10, deep: bool = False, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward opus:explore

        Token-efficient codebase exploration - better than RAG.

        Normal mode: Finds relevant files using name matching, content search, and hot path analysis.
        Deep mode (--deep): Reads file contents, analyzes imports, prepares LLM synthesis task.

        Args:
            query: What to explore (e.g., "authentication", "kernel", "plugins")
            limit: Max files to return (default 10, or 5 for deep mode)
            deep: If True, read files and prepare cognitive synthesis task
            json: If True, return raw JSON-compatible data

        Returns:
            Exploration results dict (includes synthesis_prompt in deep mode)
        """
        from vibe_core.plugins.opus_assistant.cli.commands import deep_explore, explore_codebase

        workspace = self._workspace or Path.cwd()

        if deep:
            # Deep mode: read files, analyze, prepare synthesis
            # Use smaller limit for deep mode (more content per file)
            deep_limit = min(limit, 5)
            return deep_explore(query, workspace, limit=deep_limit)
        else:
            # Normal mode: deterministic search
            return explore_codebase(query, workspace, limit=limit, json_mode=json)

    # =========================================================================
    # OPUS-308: MANIFESTATION PROTOCOL (Markdown as UI)
    # =========================================================================

    def get_manifestation_data(self) -> Dict[str, Any]:
        """
        OPUS-308: Return data for ManifestationService to render OPUS.md.

        This is the Manifestable protocol implementation. The renderer's
        _gather_context() does all the heavy lifting - we just delegate.

        The ManifestationService uses the Jinja2 template to render the
        actual markdown content.

        Returns:
            Context dict for opus_dashboard.md.j2 template
        """
        from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
            OpusDashboardRenderer,
        )

        workspace = self._workspace or Path.cwd()
        renderer = OpusDashboardRenderer(workspace_root=workspace, kernel=self._kernel)

        # Use the renderer's gather_context method (synchronous data collection)
        return renderer._gather_context(quick=False)

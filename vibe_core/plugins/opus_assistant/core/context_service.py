"""
OPUS Context Service - Dynamic Runtime Context Synthesis.

OPUS-029 Phase 2: The "Bootstrapping" - Active context injection.

This is NOT passive drift detection. This is ACTIVE context synthesis.
Every KERNEL_TICK, we aggregate the system state and inject it into
the runtime so every spawning agent knows the current reality.

The "State of Mind" for the entire system.

Architecture:
    ┌─────────────────────────────────────────────┐
    │              OpusContextService             │
    │         (The Dynamic Bootstrapper)          │
    └─────────────────┬───────────────────────────┘
                      │ synthesizes from
                      ▼
    ┌─────────────────────────────────────────────┐
    │              PRAKRITI                        │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐       │
    │  │ STHULA  │ │ PRANA   │ │ PURUSHA │       │
    │  │ Git     │ │ Kernel  │ │ Persona │       │
    │  │ Ledger  │ │ Ephemer │ │ Manager │       │
    │  │ Files   │ │         │ │         │       │
    │  └─────────┘ └─────────┘ └─────────┘       │
    └─────────────────────────────────────────────┘
                      │ injects into
                      ▼
    ┌─────────────────────────────────────────────┐
    │           EventBus + EphemeralState         │
    │     (Every spawning agent gets context)     │
    └─────────────────────────────────────────────┘
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.state.prakriti import Prakriti

logger = logging.getLogger("OPUS_CONTEXT")


@dataclass
class SystemHealth:
    """System health metrics."""

    git_clean: bool = True
    ledger_valid: bool = True
    kernel_active: bool = False
    drift_healthy: bool = True

    @property
    def overall_health(self) -> float:
        """Calculate overall health as percentage."""
        checks = [self.git_clean, self.ledger_valid, self.kernel_active, self.drift_healthy]
        return sum(1 for c in checks if c) / len(checks)

    @property
    def status(self) -> str:
        """Human-readable status."""
        health = self.overall_health
        if health >= 0.9:
            return "HEALTHY"
        elif health >= 0.7:
            return "DEGRADED"
        elif health >= 0.5:
            return "WARNING"
        else:
            return "CRITICAL"


@dataclass
class OpusContext:
    """
    Synthesized runtime context - the "State of Mind".

    This is what gets injected into every spawning agent.
    """

    # Timestamp
    synthesized_at: str
    context_hash: str

    # Layer 1: Physical State
    git_branch: str
    git_sha: str
    git_dirty: bool
    uncommitted_files: List[str]
    ledger_head: str
    ledger_event_count: int

    # Layer 2: Runtime State
    kernel_status: str
    active_agents: int
    pending_tasks: int
    session_id: Optional[str]
    uptime_seconds: float

    # Layer 3: Identity
    loaded_personas: List[str]

    # Health
    health: SystemHealth

    # Focus (what the system should prioritize)
    focus_areas: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # OPUS-032: Verification results for MANAS analyzers
    verification_results: Dict[str, Any] = field(default_factory=dict)

    # OPUS-174: MANAS Cognitive State (Mind-Body Alignment)
    manas_awareness: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        return {
            "synthesized_at": self.synthesized_at,
            "context_hash": self.context_hash,
            "git": {
                "branch": self.git_branch,
                "sha": self.git_sha,
                "dirty": self.git_dirty,
                "uncommitted_files": self.uncommitted_files,
            },
            "ledger": {
                "head": self.ledger_head,
                "event_count": self.ledger_event_count,
            },
            "runtime": {
                "kernel_status": self.kernel_status,
                "active_agents": self.active_agents,
                "pending_tasks": self.pending_tasks,
                "session_id": self.session_id,
                "uptime_seconds": self.uptime_seconds,
            },
            "identity": {
                "loaded_personas": self.loaded_personas,
            },
            "health": {
                "git_clean": self.health.git_clean,
                "ledger_valid": self.health.ledger_valid,
                "kernel_active": self.health.kernel_active,
                "drift_healthy": self.health.drift_healthy,
                "overall": self.health.overall_health,
                "status": self.health.status,
            },
            "focus_areas": self.focus_areas,
            "warnings": self.warnings,
            # OPUS-032: Verification results for MANAS
            "verification_results": self.verification_results,
            # OPUS-174: MANAS Cognitive State
            "manas_awareness": self.manas_awareness,
        }

    def to_system_prompt_fragment(self) -> str:
        """
        Generate a dynamic system prompt fragment.

        This is the "carrot" - injected into every agent's context.

        OPUS-174: Now includes VAK-style prompting based on MANAS consciousness state.
        The LLM's behavior is modulated by the cognitive state of the system.
        """
        lines = [
            "## Current System State (OPUS Context)",
            "",
            f"**Status:** {self.health.status} ({self.health.overall_health:.0%})",
            f"**Branch:** `{self.git_branch}` @ `{self.git_sha[:8]}`",
        ]

        if self.git_dirty:
            lines.append(f"**Uncommitted:** {len(self.uncommitted_files)} files")

        lines.extend(
            [
                f"**Runtime:** {self.kernel_status}, {self.active_agents} agents, {self.pending_tasks} pending",
                f"**Session:** {self.session_id or 'N/A'}",
                "",
            ]
        )

        # OPUS-174: Mind-Body Alignment - MANAS Cognitive State
        if self.manas_awareness:
            manas_state = self.manas_awareness.get("state", "unknown")
            consciousness_level = self.manas_awareness.get("consciousness_level", 0.0)

            if manas_state != "unknown":
                lines.extend(
                    [
                        "## Cognitive State (MANAS)",
                        "",
                        f"**State:** {manas_state.upper()} (level: {consciousness_level:.2f})",
                        "",
                    ]
                )

                # VAK-style dynamic prompting based on consciousness state
                lines.append(self._get_vak_directive(manas_state, consciousness_level))
                lines.append("")

        if self.focus_areas:
            lines.append("**Focus Areas:**")
            for area in self.focus_areas:
                lines.append(f"- {area}")
            lines.append("")

        if self.warnings:
            lines.append("**Warnings:**")
            for warn in self.warnings:
                lines.append(f"- ⚠️ {warn}")
            lines.append("")

        lines.extend(
            [
                f"*Context hash: {self.context_hash[:16]}*",
                f"*Synthesized: {self.synthesized_at}*",
            ]
        )

        return "\n".join(lines)

    def _get_vak_directive(self, state: str, level: float) -> str:
        """
        OPUS-174: Get VAK-style cognitive directive based on MANAS state.

        This is the Mind-Body Alignment - the LLM's prompt behavior is
        modulated by the system's consciousness state.

        Args:
            state: MANAS state (turiya, sattva, rajas, tamas)
            level: Consciousness level (0.0 - 1.0)

        Returns:
            Directive string for the LLM
        """
        # VAK directives - how the LLM should behave in each state
        directives = {
            "turiya": (
                "**Cognitive Directive:** You are in a state of DEEP INSIGHT (Turiya). "
                "The system has high synaptic urgency and good health. "
                "Synthesize broad patterns. Consider architectural implications. "
                "Be visionary - this is the time for significant decisions."
            ),
            "sattva": (
                "**Cognitive Directive:** You are in a state of BALANCED CLARITY (Sattva). "
                "The system is stable and reflective. "
                "Organize thoughts. Reinforce good patterns. "
                "Be thorough but not rushed - quality over speed."
            ),
            "rajas": (
                "**Cognitive Directive:** You are in a state of HIGH ALERT (Rajas). "
                "The system is reactive and responsive. "
                "Be concise and focused. Address immediate issues first. "
                "Do not over-explain - act decisively."
            ),
            "tamas": (
                "**Cognitive Directive:** You are in a state of CONSERVATION (Tamas). "
                "The system is in low-energy mode. "
                "Focus only on essentials. Minimal processing. "
                "Wait for better conditions before major decisions."
            ),
        }

        return directives.get(state, "")


class OpusContextService:
    """
    Dynamic Runtime Context Synthesizer.

    The "brain" that keeps the system self-aware.
    Every KERNEL_TICK, this service:
    1. Aggregates state from all Prakriti layers
    2. Synthesizes into an OpusContext
    3. Generates a dynamic system prompt
    4. Injects into runtime for all agents

    This is the "constant prompt feed" - the carrot in front of the donkey.
    """

    # Storage key in EphemeralState
    CONTEXT_KEY = "opus_runtime_context"
    PROMPT_KEY = "opus_system_prompt_fragment"

    def __init__(self, workspace_root: Path, prakriti: Optional["Prakriti"] = None):
        """
        Initialize context service.

        Args:
            workspace_root: Workspace path
            prakriti: Optional Prakriti instance (lazy-loaded if not provided)
        """
        self._workspace = workspace_root
        self._prakriti = prakriti
        self._last_context: Optional[OpusContext] = None
        self._synthesis_count = 0

    @property
    def prakriti(self) -> "Prakriti":
        """Lazy-load Prakriti if not injected."""
        if self._prakriti is None:
            from vibe_core.state.prakriti import Prakriti

            self._prakriti = Prakriti.from_workspace(self._workspace)
        return self._prakriti

    def synthesize(self) -> OpusContext:
        """
        Synthesize current system context.

        Aggregates state from all Prakriti layers.

        Returns:
            OpusContext with full system state
        """
        self._synthesis_count += 1
        timestamp = datetime.now().isoformat()

        # Layer 1: Physical State (Git + Ledger)
        git_status = self._get_git_status()
        ledger_status = self._get_ledger_status()

        # Layer 2: Runtime State (Kernel + Ephemeral)
        kernel_status = self._get_kernel_status()

        # Layer 3: Identity (Personas)
        personas = self._get_personas()

        # Health assessment
        health = self._assess_health(git_status, ledger_status, kernel_status)

        # Focus areas (what needs attention)
        focus_areas, warnings = self._determine_focus(git_status, kernel_status, health)

        # OPUS-032: Load verification results for MANAS analyzers
        verification_results = self._get_verification_results()

        # OPUS-174: Load MANAS cognitive state for Mind-Body Alignment
        manas_awareness = self._get_manas_awareness()

        # Generate context hash
        context_data = f"{timestamp}:{git_status.get('sha', '')}:{ledger_status.get('head', '')}"
        context_hash = hashlib.sha256(context_data.encode()).hexdigest()

        context = OpusContext(
            synthesized_at=timestamp,
            context_hash=context_hash,
            # Git
            git_branch=git_status.get("branch", "unknown"),
            git_sha=git_status.get("sha", "unknown"),
            git_dirty=git_status.get("dirty", False),
            uncommitted_files=git_status.get("uncommitted_files", []),
            # Ledger
            ledger_head=ledger_status.get("head", "unknown"),
            ledger_event_count=ledger_status.get("event_count", 0),
            # Runtime
            kernel_status=kernel_status.get("status", "unknown"),
            active_agents=kernel_status.get("active_agents", 0),
            pending_tasks=kernel_status.get("pending_tasks", 0),
            session_id=kernel_status.get("session_id"),
            uptime_seconds=kernel_status.get("uptime_seconds", 0.0),
            # Identity
            loaded_personas=personas,
            # Health
            health=health,
            focus_areas=focus_areas,
            warnings=warnings,
            # OPUS-032: Verification results
            verification_results=verification_results,
            # OPUS-174: MANAS cognitive state
            manas_awareness=manas_awareness,
        )

        self._last_context = context
        logger.debug(f"Synthesized context #{self._synthesis_count}: {health.status}")

        return context

    def inject(self, context: Optional[OpusContext] = None) -> None:
        """
        Inject context into runtime.

        Stores in EphemeralState so all agents can access it.

        Args:
            context: OpusContext to inject (synthesizes if None)
        """
        if context is None:
            context = self.synthesize()

        try:
            # Store in EphemeralState
            self.prakriti.ephemeral.set(self.CONTEXT_KEY, context.to_dict())

            # Store system prompt fragment
            prompt_fragment = context.to_system_prompt_fragment()
            self.prakriti.ephemeral.set(self.PROMPT_KEY, prompt_fragment)

            logger.info(f"🎯 Context injected: {context.health.status} ({context.context_hash[:8]})")

        except Exception as e:
            logger.warning(f"Failed to inject context: {e}")

    async def broadcast(self, context: Optional[OpusContext] = None) -> None:
        """
        Broadcast context via EventBus.

        Emits CONTEXT_SYNTHESIS event for all listeners.

        Args:
            context: OpusContext to broadcast (synthesizes if None)
        """
        if context is None:
            context = self.synthesize()

        try:
            from vibe_core.event_bus import emit_event

            await emit_event(
                event_type="CONTEXT_SYNTHESIS",
                agent_id="opus_assistant",
                message=f"Runtime context synthesized: {context.health.status}",
                details=context.to_dict(),
            )

            logger.debug(f"Broadcast context: {context.context_hash[:8]}")

        except ImportError:
            logger.debug("EventBus not available - skipping broadcast")
        except Exception as e:
            logger.warning(f"Failed to broadcast context: {e}")

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """
        Get current context from EphemeralState.

        Returns:
            Current context dict or None
        """
        try:
            return self.prakriti.ephemeral.get(self.CONTEXT_KEY)
        except Exception:
            return None

    def get_system_prompt_fragment(self) -> str:
        """
        Get current system prompt fragment.

        This is what should be prepended to agent system prompts.

        Returns:
            System prompt fragment string
        """
        try:
            fragment = self.prakriti.ephemeral.get(self.PROMPT_KEY)
            if fragment:
                return fragment
        except Exception:
            pass

        # Synthesize fresh if not available
        context = self.synthesize()
        return context.to_system_prompt_fragment()

    # =========================================================================
    # Private: State Aggregation
    # =========================================================================

    def _get_git_status(self) -> Dict[str, Any]:
        """Get git state from Prakriti Layer 1."""
        try:
            git = self.prakriti.git
            status = git.status()

            # Get uncommitted files
            uncommitted = []
            if status.get("dirty", False):
                try:
                    dirty_files = git.dirty_files() if hasattr(git, "dirty_files") else []
                    uncommitted = dirty_files[:10]  # Limit to 10
                except Exception:
                    pass

            return {
                "branch": status.get("branch", "unknown"),
                "sha": status.get("sha", "unknown"),
                "dirty": status.get("dirty", False),
                "uncommitted_files": uncommitted,
            }
        except Exception as e:
            logger.debug(f"Git status unavailable: {e}")
            return {"branch": "unknown", "sha": "unknown", "dirty": False, "uncommitted_files": []}

    def _get_ledger_status(self) -> Dict[str, Any]:
        """Get ledger state from Prakriti Layer 1."""
        try:
            ledger = self.prakriti.ledger
            head = ledger.get_head()

            return {
                "head": head.hash if head else "unknown",
                "event_count": head.event_count if head else 0,
                "last_sync_sha": head.last_sync_sha if head else None,
            }
        except Exception as e:
            logger.debug(f"Ledger status unavailable: {e}")
            return {"head": "unknown", "event_count": 0}

    def _get_kernel_status(self) -> Dict[str, Any]:
        """Get kernel state from Prakriti Layer 2."""
        try:
            kernel = self.prakriti.kernel

            if not kernel.has_kernel():
                return {
                    "status": "offline",
                    "active_agents": 0,
                    "pending_tasks": 0,
                    "session_id": None,
                    "uptime_seconds": 0.0,
                }

            snapshot = kernel.snapshot()
            session = self.prakriti.session

            return {
                "status": snapshot.status if snapshot else "unknown",
                "active_agents": len(snapshot.agents) if snapshot else 0,
                "pending_tasks": snapshot.queue.pending if snapshot and snapshot.queue else 0,
                "session_id": session.session_id if session else None,
                "uptime_seconds": snapshot.uptime_seconds if snapshot else 0.0,
            }
        except Exception as e:
            logger.debug(f"Kernel status unavailable: {e}")
            return {
                "status": "unknown",
                "active_agents": 0,
                "pending_tasks": 0,
                "session_id": None,
                "uptime_seconds": 0.0,
            }

    def _get_personas(self) -> List[str]:
        """Get loaded personas from Prakriti Layer 3."""
        try:
            personas = self.prakriti.personas
            return personas.list_personas() if hasattr(personas, "list_personas") else []
        except Exception as e:
            logger.debug(f"Personas unavailable: {e}")
            return []

    def _get_manas_awareness(self) -> Dict[str, Any]:
        """
        OPUS-174: Get MANAS cognitive state for Mind-Body Alignment.

        Loads from .opus_state/manas_awareness.json which is updated
        by CognitiveKernel.tick() every ~60 seconds.

        This enables VAK-style dynamic prompting where the LLM's
        behavior is modulated by MANAS's consciousness state.

        Returns:
            Dict with consciousness_level, state, inputs, etc.
        """
        import json

        awareness_path = self._workspace / ".opus_state" / "manas_awareness.json"

        try:
            if awareness_path.exists():
                with open(awareness_path) as f:
                    awareness = json.load(f)

                logger.debug(
                    f"Loaded MANAS awareness: state={awareness.get('state', 'unknown')}, "
                    f"level={awareness.get('consciousness_level', 0):.2f}"
                )
                return awareness

        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in manas_awareness.json: {e}")
        except Exception as e:
            logger.debug(f"Could not load MANAS awareness: {e}")

        # Default: unknown state (MANAS not yet ticked)
        return {
            "consciousness_level": 0.0,
            "state": "unknown",
            "inputs": {},
            "tick": 0,
        }

    def _get_verification_results(self) -> Dict[str, Any]:
        """
        OPUS-032: Get verification results for MANAS analyzers.

        Loads from cached watchman_report.json or .opus_state/verification.json.
        Full verification is expensive, so we prefer cached results.

        Returns:
            Dict with 'failures' list and 'score' if available
        """
        import json

        # Try multiple possible sources for verification results
        possible_paths = [
            self._workspace / "watchman_report.json",
            self._workspace / ".opus_state" / "verification.json",
            self._workspace / ".opus_state" / "harness_results.json",
        ]

        for report_path in possible_paths:
            try:
                if report_path.exists():
                    with open(report_path) as f:
                        report = json.load(f)

                    # Transform to expected format if needed
                    result = {
                        "failures": report.get("failures", []),
                        "score": report.get("score", report.get("trust_score", 100)),
                        "checks": report.get("checks", {}),
                        "source": str(report_path.name),
                    }

                    logger.debug(f"Loaded verification from {report_path.name}: {len(result['failures'])} failures")
                    return result

            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON in {report_path}: {e}")
            except Exception as e:
                logger.debug(f"Could not load {report_path}: {e}")

        # No cached results available
        logger.debug("No verification results available (no cached report found)")
        return {"failures": [], "score": 100, "checks": {}, "source": None}

    def _assess_health(
        self,
        git_status: Dict[str, Any],
        ledger_status: Dict[str, Any],
        kernel_status: Dict[str, Any],
    ) -> SystemHealth:
        """Assess overall system health."""
        health = SystemHealth()

        # Git clean?
        health.git_clean = not git_status.get("dirty", False)

        # Ledger valid?
        try:
            verification = self.prakriti.ledger.verify_chain()
            health.ledger_valid = verification.get("valid", False)
        except Exception:
            health.ledger_valid = True  # Assume valid if can't verify

        # Kernel active?
        health.kernel_active = kernel_status.get("status") not in ["offline", "unknown"]

        # Drift healthy?
        try:
            from .drift_detector import DriftDetector

            detector = DriftDetector(workspace_root=self._workspace)
            quick = detector.quick_check()
            health.drift_healthy = quick.get("healthy", True)
        except Exception:
            health.drift_healthy = True  # Assume healthy if can't check

        return health

    def _determine_focus(
        self,
        git_status: Dict[str, Any],
        kernel_status: Dict[str, Any],
        health: SystemHealth,
    ) -> tuple[List[str], List[str]]:
        """Determine focus areas and warnings based on state."""
        focus_areas = []
        warnings = []

        # Check git state
        if git_status.get("dirty", False):
            uncommitted = git_status.get("uncommitted_files", [])
            if len(uncommitted) > 5:
                warnings.append(f"High uncommitted file count: {len(uncommitted)}")
            focus_areas.append("Commit pending changes")

        # Check kernel state
        if kernel_status.get("pending_tasks", 0) > 10:
            warnings.append(f"High task queue: {kernel_status['pending_tasks']} pending")
            focus_areas.append("Process task backlog")

        # Check health
        if not health.git_clean:
            focus_areas.append("Git cleanup needed")

        if not health.ledger_valid:
            warnings.append("Ledger chain integrity issue")
            focus_areas.insert(0, "CRITICAL: Verify ledger")

        if not health.drift_healthy:
            focus_areas.append("Documentation drift detected")

        if not health.kernel_active:
            focus_areas.append("Kernel offline - limited capabilities")

        return focus_areas, warnings

    # =========================================================================
    # State Management
    # =========================================================================

    def get_synthesis_count(self) -> int:
        """Get number of context syntheses."""
        return self._synthesis_count

    def get_last_context(self) -> Optional[OpusContext]:
        """Get last synthesized context."""
        return self._last_context

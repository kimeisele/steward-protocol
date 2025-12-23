"""
OPUS-167: Weaver Bridge - Cognitive Weaver and State Sync

Extracted from CognitiveKernel to reduce kernel size.
This bridge handles:

1. CognitiveWeaver (OPUS-106): State ↔ Knowledge Bridge
   - Unified access to state layer and knowledge layer
   - Session context injection from OPUS.md

2. StateSyncWeaver (OPUS-096): Runtime state commits
   - Discovers dirty runtime files via git status
   - Commits during kernel operation (invisible hand)

"Gedächtnis ohne Wissen ist blind. Wissen ohne Gedächtnis ist vergesslich."
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.state.cognitive_weaver import CognitiveWeaver

logger = logging.getLogger("MANAS.WeaverBridge")


class WeaverBridge:
    """
    OPUS-167: Bridge to CognitiveWeaver and StateSyncWeaver.

    This class extracts the weaver-related logic from the kernel.
    It provides a clean interface for:
    - State ↔ Knowledge bridging (CognitiveWeaver)
    - Runtime state sync (StateSyncWeaver)

    Usage:
        bridge = WeaverBridge(workspace=Path.cwd())

        # Get unified context
        context = bridge.get_cognitive_context(focus="governance")

        # Consult knowledge before action
        result = bridge.consult_knowledge("delete_file", {"path": "foo.py"})

        # Pulse state sync
        bridge.weaver_pulse()
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize WeaverBridge.

        Args:
            workspace: Workspace root path
        """
        self._workspace = workspace or Path.cwd()
        self._cognitive_weaver: Optional["CognitiveWeaver"] = None

        self._init_cognitive_weaver()

    def _init_cognitive_weaver(self) -> None:
        """
        Initialize Cognitive Weaver - the State ↔ Knowledge Bridge.

        OPUS-106: "Gedächtnis ohne Wissen ist blind. Wissen ohne Gedächtnis ist vergesslich."

        This provides unified access to:
        - State Layer (Prakriti, StateSyncHolon) - What MANAS REMEMBERS
        - Knowledge Layer (UnifiedKnowledgeGraph) - What MANAS KNOWS
        - Session Context (OPUS.md preserved sections) - What MANAS was DOING
        """
        try:
            from vibe_core.state.cognitive_weaver import CognitiveWeaver

            self._cognitive_weaver = CognitiveWeaver(workspace=self._workspace)

            # OPUS-106: Inject session context from OPUS.md (UI → Mind Bridge)
            self._inject_session_context_from_opus()

            # Boot diagnosis
            diagnosis = self._cognitive_weaver.diagnose()
            health = diagnosis.get("unified", {}).get("overall_health", 0)
            session_ctx = (
                "with session context" if self._cognitive_weaver.has_session_context() else "no session context"
            )
            logger.info(f"🧵 WEAVER BRIDGE: State ↔ Knowledge Bridge initialized - Health: {health:.0%}, {session_ctx}")
        except Exception as e:
            logger.warning(f"🧵 WEAVER BRIDGE: Could not initialize CognitiveWeaver: {e}")
            self._cognitive_weaver = None

    def _inject_session_context_from_opus(self) -> None:
        """
        OPUS-106: Extract preserved sections from OPUS.md and inject into CognitiveWeaver.

        This bridges the UI-Layer (OPUS.md) with the Mind-Layer (MANAS).
        The preserved sections contain what the previous AI/Human wrote,
        enabling continuity across sessions.
        """
        if not self._cognitive_weaver:
            return

        try:
            opus_path = self._workspace / "OPUS.md"
            if not opus_path.exists():
                return

            # Try to get preserved sections from opus_assistant
            try:
                from vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer import (
                    OpusDashboardRenderer,
                )

                renderer = OpusDashboardRenderer(self._workspace)
                preserved = renderer._extract_preserved_sections()

                if preserved:
                    self._cognitive_weaver.inject_session_context(preserved)
                    logger.debug("🧵 WEAVER BRIDGE: Session context loaded from OPUS.md")
            except ImportError:
                logger.debug("🧵 WEAVER BRIDGE: OpusDashboardRenderer not available")
            except Exception as e:
                logger.debug(f"🧵 WEAVER BRIDGE: Could not extract preserved sections: {e}")

        except Exception as e:
            logger.warning(f"🧵 WEAVER BRIDGE: Failed to inject session context: {e}")

    @property
    def is_available(self) -> bool:
        """Check if CognitiveWeaver is available."""
        return self._cognitive_weaver is not None

    @property
    def cognitive_weaver(self) -> Optional["CognitiveWeaver"]:
        """Get the underlying CognitiveWeaver instance."""
        return self._cognitive_weaver

    def inject_cognitive_weaver(self, weaver: "CognitiveWeaver") -> None:
        """
        Inject the Cognitive Weaver for unified state + knowledge access.

        OPUS-106: This enables MANAS to perceive BOTH state and knowledge
        as ONE unified consciousness.

        Args:
            weaver: CognitiveWeaver instance
        """
        self._cognitive_weaver = weaver
        logger.info("🧵 WEAVER BRIDGE: CognitiveWeaver injected")

    def get_cognitive_context(self, focus: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get unified cognitive context combining state + knowledge.

        OPUS-106: This is the "perception" method - what MANAS sees when
        it looks at the unified state of consciousness.

        Args:
            focus: Optional focus area (e.g., "governance", "state")

        Returns:
            Dict with unified context or None if weaver unavailable
        """
        if not self._cognitive_weaver:
            return None

        try:
            context = self._cognitive_weaver.weave(focus=focus)
            return {
                "health_score": context.health_score,
                "tamas_count": len(context.tamas_paths),
                "dirty_count": len(context.dirty_paths),
                "wisdom_notes": context.wisdom_notes,
                "recommended_actions": context.recommended_actions,
                "prompt_context": context.to_prompt_context(),
            }
        except Exception as e:
            logger.debug(f"🧵 WEAVER BRIDGE: Could not weave context: {e}")
            return None

    def consult_knowledge(self, action: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Consult knowledge before taking an action.

        OPUS-106: Before MANAS acts, it can ask the knowledge graph:
        - Is this action allowed?
        - What constraints apply?
        - What authority is required?

        Args:
            action: The action being considered
            context: Context about the action

        Returns:
            Consultation result or None if unavailable
        """
        if not self._cognitive_weaver:
            return None

        try:
            consultation = self._cognitive_weaver.consult(action, context)
            return {
                "allowed": consultation.allowed,
                "constraints_violated": consultation.constraints_violated,
                "authority_required": consultation.authority_required,
                "recommendation": consultation.recommendation,
            }
        except Exception as e:
            logger.debug(f"🧵 WEAVER BRIDGE: Could not consult knowledge: {e}")
            return None

    def get_cognitive_diagnosis(self) -> Optional[Dict[str, Any]]:
        """
        Get full system diagnosis from Cognitive Weaver.

        Returns combined state + knowledge health check.
        """
        if not self._cognitive_weaver:
            return None

        try:
            return self._cognitive_weaver.diagnose()
        except Exception as e:
            logger.debug(f"🧵 WEAVER BRIDGE: Could not diagnose: {e}")
            return None

    def weaver_pulse(self) -> None:
        """
        OPUS-096: Trigger StateSyncWeaver to commit runtime state.

        The Weaver discovers dirty runtime files via git status (independent of StateService).
        This ensures files written during MANAS cycle get committed to git.

        This is the "invisible hand" that keeps state synced to git during kernel operation.
        The Weaver is also called from heartbeat.py for scheduled commits.
        """
        try:
            from vibe_core.state.prakriti import Prakriti
            from vibe_core.state.weaver import StateSyncWeaver

            prakriti = Prakriti(workspace_path=self._workspace)
            weaver = StateSyncWeaver(prakriti)
            result = weaver.pulse()

            if result.success and result.sha:
                logger.debug(f"🧵 WEAVER BRIDGE: Committed runtime state ({result.sha[:8]})")
            elif result.success:
                logger.debug("🧵 WEAVER BRIDGE: No runtime changes to commit")
            else:
                logger.debug(f"🧵 WEAVER BRIDGE: {result.error or result.message}")

        except Exception as e:
            # Weaver failure should not break MANAS cycle
            logger.debug(f"🧵 WEAVER BRIDGE: Skipped ({e})")


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "WeaverBridge",
]

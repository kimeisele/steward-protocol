"""
OPUS Assistant Kernel Tick - Constant heartbeat for plugin lifecycle.

OPUS-029 Phase 2: Dynamic Runtime Context Injection.

The plugin doesn't just boot and die. It stays ALIVE via EventBus.
More importantly, it ACTIVELY SYNTHESIZES and INJECTS context.

Kernel Tick Pattern:
1. Plugin subscribes to EventBus events (KERNEL_TICK, GIT_COMMIT, etc.)
2. On each tick, OpusContextService synthesizes system state
3. Context is INJECTED into runtime (EphemeralState)
4. Every spawning agent knows the current reality

This is the "constant prompt feed" - the carrot in front of the donkey.
Every agent wakes up knowing the "State of Mind" of the system.
"""

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from ..core.context_service import OpusContextService
    from ..plugin_main import OpusAssistantPlugin

logger = logging.getLogger("OPUS_TICK")


class KernelTickHandler:
    """
    Handles kernel tick events for OPUS Assistant.

    Subscribes to EventBus and keeps plugin state fresh.

    Architecture (Phase 2 - Dynamic Context):
    - EventBus emits periodic KERNEL_TICK events
    - OpusContextService synthesizes system state from all Prakriti layers
    - Context is INJECTED into EphemeralState
    - Every spawning agent gets the current "State of Mind"
    - On GIT_COMMIT, we re-synthesize and broadcast
    - On FILE_CHANGED, we re-verify affected docs

    This is the "constant prompt feed" - active, not passive!
    """

    def __init__(self, plugin: "OpusAssistantPlugin"):
        """
        Initialize tick handler.

        Args:
            plugin: Reference to parent plugin
        """
        self._plugin = plugin
        self._subscriptions: List[Callable] = []
        self._tick_count = 0
        self._last_state: Dict[str, Any] = {}
        self._context_service: Optional["OpusContextService"] = None

        # Initialize context service
        self._init_context_service()

    def _init_context_service(self) -> None:
        """Initialize the OpusContextService for dynamic context synthesis."""
        try:
            from ..core.context_service import OpusContextService

            workspace = self._plugin._workspace
            if workspace:
                self._context_service = OpusContextService(workspace_root=workspace)
                logger.debug("OpusContextService initialized")
        except Exception as e:
            logger.debug(f"Could not initialize context service: {e}")

    def subscribe(self) -> bool:
        """
        Subscribe to EventBus events.

        Returns:
            True if subscription successful, False otherwise
        """
        try:
            from vibe_core.event_bus import EventType, get_event_bus

            bus = get_event_bus()

            # Subscribe to relevant events
            config = self._plugin._config.get("kernel_tick", {})
            events = config.get("subscribe_events", ["KERNEL_TICK", "GIT_COMMIT"])

            for event_name in events:
                try:
                    # Try to get EventType enum, fallback to string
                    event_type = getattr(EventType, event_name, event_name)
                    bus.subscribe(self._on_event, event_type)
                    logger.debug(f"Subscribed to {event_name}")
                except Exception as e:
                    logger.debug(f"Could not subscribe to {event_name}: {e}")

            logger.info("🔄 Kernel tick handler subscribed")
            return True

        except ImportError:
            logger.debug("EventBus not available - tick handler disabled")
            return False
        except Exception as e:
            logger.warning(f"Failed to subscribe to EventBus: {e}")
            return False

    def unsubscribe(self) -> None:
        """Unsubscribe from all events."""
        # EventBus handles cleanup on shutdown
        self._subscriptions.clear()
        logger.info("🔄 Kernel tick handler unsubscribed")

    async def _on_event(self, event: Any) -> None:
        """
        Handle incoming events.

        Args:
            event: Event from EventBus
        """
        self._tick_count += 1
        event_type = getattr(event, "event_type", str(event))

        try:
            if "KERNEL_TICK" in str(event_type):
                await self._on_tick(event)
            elif "GIT_COMMIT" in str(event_type):
                await self._on_commit(event)
            elif "FILE_CHANGED" in str(event_type):
                await self._on_file_changed(event)
        except Exception as e:
            logger.debug(f"Error handling {event_type}: {e}")

    async def _on_tick(self, event: Any) -> None:
        """
        Handle periodic tick.

        PHASE 2: Active context synthesis and injection.
        This is NOT passive - we actively refresh the system's "State of Mind".
        """
        config = self._plugin._config.get("kernel_tick", {})
        actions = config.get("on_tick", ["synthesize_context", "quick_drift_check"])

        for action in actions:
            if action == "synthesize_context":
                # ACTIVE: Synthesize and inject context
                await self._synthesize_and_inject_context()

            elif action == "quick_drift_check":
                result = self._plugin.quick_drift_check()
                if not result.get("healthy", True):
                    logger.warning(f"⚠️ Drift detected on tick {self._tick_count}")
                self._last_state["drift"] = result

    async def _synthesize_and_inject_context(self) -> None:
        """
        Synthesize system context and inject into runtime.

        This is the "Dynamic Bootstrapping" - every tick updates
        the "State of Mind" that all agents can access.
        """
        if not self._context_service:
            return

        try:
            # Synthesize from all Prakriti layers
            context = self._context_service.synthesize()

            # Inject into EphemeralState (sync)
            self._context_service.inject(context)

            # Broadcast via EventBus (async)
            await self._context_service.broadcast(context)

            # Store in handler state
            self._last_state["context"] = context.to_dict()
            self._last_state["context_hash"] = context.context_hash
            self._last_state["system_health"] = context.health.status

            # Log periodically (every 10 ticks)
            if self._tick_count % 10 == 0:
                logger.info(
                    f"🎯 Context #{self._context_service.get_synthesis_count()}: "
                    f"{context.health.status} | {context.git_branch}@{context.git_sha[:8]}"
                )

        except Exception as e:
            logger.debug(f"Context synthesis failed: {e}")

    async def _on_commit(self, event: Any) -> None:
        """
        Handle git commit event.

        PHASE 2: Re-synthesize context after code changes.
        Git state changed, so we need a fresh "State of Mind".
        """
        config = self._plugin._config.get("kernel_tick", {})
        actions = config.get("on_commit", ["synthesize_context", "detect_drift"])

        for action in actions:
            if action == "synthesize_context":
                # IMPORTANT: Re-synthesize after commit
                # The git SHA changed, agents need to know
                await self._synthesize_and_inject_context()

            elif action == "detect_drift":
                result = self._plugin.detect_drift()
                self._last_state["last_drift_check"] = result
                logger.info(f"📊 Drift check after commit: health={result.get('health', 0):.0%}")

            elif action == "update_verification":
                result = self._plugin.verify(quick=True)
                self._last_state["last_verification"] = result
                logger.info(f"🔍 Verification after commit: score={result.get('total_score', 0)}%")

    async def _on_file_changed(self, event: Any) -> None:
        """
        Handle file change event.

        Re-verifies affected OPUS docs.
        """
        # Get changed file path from event
        details = getattr(event, "details", {})
        changed_file = details.get("path", "")

        if not changed_file:
            return

        # Check if it's a tracked file
        if changed_file.startswith("vibe_core/") or changed_file.startswith("docs/architecture/OPUS/"):
            logger.debug(f"📝 Tracked file changed: {changed_file}")
            # Could trigger partial re-verification here

    def get_state(self) -> Dict[str, Any]:
        """
        Get current tick handler state.

        Returns:
            Dict with handler status and last results
        """
        state = {
            "tick_count": self._tick_count,
            "subscribed": len(self._subscriptions) > 0,
            "last_state": self._last_state,
        }

        # Add context service info
        if self._context_service:
            state["context_synthesis_count"] = self._context_service.get_synthesis_count()
            state["has_context_service"] = True
            if "system_health" in self._last_state:
                state["system_health"] = self._last_state["system_health"]
        else:
            state["has_context_service"] = False

        return state

    def get_context_service(self) -> Optional["OpusContextService"]:
        """Get the OpusContextService instance."""
        return self._context_service

    def get_current_context(self) -> Optional[Dict[str, Any]]:
        """
        Get current synthesized context.

        Returns:
            Current context dict or None
        """
        if self._context_service:
            return self._context_service.get_current_context()
        return self._last_state.get("context")

    def get_system_prompt_fragment(self) -> str:
        """
        Get current system prompt fragment.

        This is what should be prepended to agent system prompts
        so they know the current "State of Mind".

        Returns:
            System prompt fragment string
        """
        if self._context_service:
            return self._context_service.get_system_prompt_fragment()
        return ""


# Synchronous wrapper for non-async contexts
class SyncKernelTickHandler(KernelTickHandler):
    """
    Synchronous version of KernelTickHandler.

    For use when async is not available.
    """

    def _on_event_sync(self, event: Any) -> None:
        """Synchronous event handler."""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule for later
                loop.create_task(self._on_event(event))
            else:
                loop.run_until_complete(self._on_event(event))
        except RuntimeError:
            # No event loop, create one
            asyncio.run(self._on_event(event))

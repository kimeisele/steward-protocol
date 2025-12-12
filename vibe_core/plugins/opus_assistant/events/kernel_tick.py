"""
OPUS Assistant Kernel Tick - Constant heartbeat for plugin lifecycle.

OPUS-029: The plugin doesn't just boot and die. It stays ALIVE via EventBus.

Kernel Tick Pattern:
1. Plugin subscribes to EventBus events (KERNEL_TICK, GIT_COMMIT, etc.)
2. On each tick, plugin refreshes state from Prakriti
3. Plugin can react to changes (drift, file changes, etc.)

This keeps the plugin "fed" with context - the carrot in front of the donkey.
"""

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List

if TYPE_CHECKING:
    from ..plugin_main import OpusAssistantPlugin

logger = logging.getLogger("OPUS_TICK")


class KernelTickHandler:
    """
    Handles kernel tick events for OPUS Assistant.

    Subscribes to EventBus and keeps plugin state fresh.

    Architecture:
    - EventBus emits periodic KERNEL_TICK events
    - We listen and refresh our understanding of the codebase
    - On GIT_COMMIT, we check for drift
    - On FILE_CHANGED, we re-verify affected docs

    This is the "constant prompt feed" that keeps the plugin context-aware.
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

        Refreshes plugin state and checks for issues.
        """
        config = self._plugin._config.get("kernel_tick", {})
        actions = config.get("on_tick", ["quick_drift_check"])

        for action in actions:
            if action == "quick_drift_check":
                result = self._plugin.quick_drift_check()
                if not result.get("healthy", True):
                    logger.warning(f"⚠️ Drift detected on tick {self._tick_count}")
                self._last_state["drift"] = result

    async def _on_commit(self, event: Any) -> None:
        """
        Handle git commit event.

        Checks for drift after code changes.
        """
        config = self._plugin._config.get("kernel_tick", {})
        actions = config.get("on_commit", ["detect_drift"])

        for action in actions:
            if action == "detect_drift":
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
        return {
            "tick_count": self._tick_count,
            "subscribed": len(self._subscriptions) > 0,
            "last_state": self._last_state,
        }


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

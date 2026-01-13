"""
Syscall Listener - Experience Replay Buffer Synapse

OPUS-031 Layer 2: Transforms SYSCALL_EXECUTED events into long-term memory.

ARCHITECTURE (GAD-000 Compliant):
    ┌─────────────────────────────────────────────────────────────┐
    │                    CORE (Nervous System)                     │
    │  ┌─────────────────────────────────────────────────────────┐│
    │  │       SemanticSyscallExecutor.execute()                 ││
    │  │                     │                                   ││
    │  │                     ▼                                   ││
    │  │       _emit_syscall_event() → EventBus                  ││
    │  └─────────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────────┘
                              │ SYSCALL_EXECUTED event
                              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    PLUGIN (Memory System)                    │
    │  ┌─────────────────────────────────────────────────────────┐│
    │  │       SyscallListener._on_syscall_executed()            ││
    │  │                     │                                   ││
    │  │                     ▼                                   ││
    │  │       state_manager.record_syscall(SyscallEntry)        ││
    │  │                     │                                   ││
    │  │                     ▼                                   ││
    │  │       .opus_state/syscalls.jsonl (Experience Replay)    ││
    │  └─────────────────────────────────────────────────────────┘│
    └─────────────────────────────────────────────────────────────┘

The system learns from its own successes.
Successful syscalls become few-shot examples for future executions.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x71f7dd9f"  # GenesisByte: parampara % 37 == 0

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.core.state_manager import OpusStateManager

logger = logging.getLogger("SYSCALL_LISTENER")


class SyscallListener:
    """
    Hippocampus of the system - transforms events into long-term memory.

    Subscribes to SYSCALL_EXECUTED events from the EventBus and records
    them to the Experience Replay Buffer via OpusStateManager.
    """

    def __init__(self, state_manager: Optional["OpusStateManager"] = None):
        """
        Initialize the syscall listener.

        Args:
            state_manager: Optional OpusStateManager instance.
                           If None, will be lazy-loaded on first event.
        """
        self._state_manager = state_manager
        self._subscribed = False
        self._event_count = 0

    def subscribe(self) -> bool:
        """
        Subscribe to SYSCALL_EXECUTED events from the EventBus.

        Returns:
            True if subscription successful, False otherwise.
        """
        try:
            from vibe_core.event_bus import EventType, get_event_bus

            bus = get_event_bus()
            bus.subscribe(self._on_syscall_executed, EventType.SYSCALL_EXECUTED)

            self._subscribed = True
            logger.info("🧠 SyscallListener subscribed to SYSCALL_EXECUTED events")
            return True

        except ImportError:
            logger.debug("EventBus not available - SyscallListener disabled")
            return False
        except Exception as e:
            logger.warning(f"Failed to subscribe SyscallListener: {e}")
            return False

    def unsubscribe(self) -> None:
        """Unsubscribe from EventBus."""
        self._subscribed = False
        logger.info("🧠 SyscallListener unsubscribed")

    async def _on_syscall_executed(self, event: Any) -> None:
        """
        Handle SYSCALL_EXECUTED event - transform to long-term memory.

        This is the "synapse" that connects the nervous system (core)
        to the memory system (plugin).

        Args:
            event: Event object from EventBus with details about the syscall.
        """
        self._event_count += 1

        try:
            # Extract syscall details from event
            details = getattr(event, "details", {}) or {}
            syscall_type = details.get("syscall_type", "UNKNOWN")
            params = details.get("params", {})
            success = details.get("success", False)
            output = details.get("output")
            error = details.get("error")

            # Determine result string
            if success:
                result = "SUCCESS"
            elif error:
                result = "FAILURE"
            else:
                result = "UNKNOWN"

            # Extract intent from params (if available) or construct from syscall
            intent = params.get("mission") or params.get("message") or f"Execute {syscall_type}"

            # Get or create state manager
            state_manager = self._get_state_manager()
            if not state_manager:
                logger.debug("StateManager not available - skipping syscall recording")
                return

            # Create SyscallEntry
            from vibe_core.plugins.opus_assistant.core.state_manager import SyscallEntry

            entry = SyscallEntry(
                timestamp=datetime.utcnow().isoformat(),
                intent=intent,
                syscall_type=syscall_type,
                parameters=params,
                result=result,
                output=str(output)[:500] if output else None,  # Truncate for storage
                context_hash=None,  # Could add git commit hash here
            )

            # Record to Experience Replay Buffer
            state_manager.record_syscall(entry)

            logger.debug(f"🧠 Syscall recorded: {syscall_type} ({result})")

        except Exception as e:
            # Don't let recording failures break the event handler
            logger.debug(f"Failed to record syscall: {e}")

    def _get_state_manager(self) -> Optional["OpusStateManager"]:
        """Lazy-load the state manager."""
        if self._state_manager is not None:
            return self._state_manager

        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            self._state_manager = get_state_manager()
            return self._state_manager
        except Exception as e:
            logger.debug(f"Could not get StateManager: {e}")
            return None

    @property
    def is_subscribed(self) -> bool:
        """Check if listener is subscribed to EventBus."""
        return self._subscribed

    @property
    def event_count(self) -> int:
        """Get count of events processed."""
        return self._event_count


# Singleton instance for easy access
_syscall_listener_instance: Optional[SyscallListener] = None


def get_syscall_listener() -> SyscallListener:
    """Get or create the singleton SyscallListener instance."""
    global _syscall_listener_instance
    if _syscall_listener_instance is None:
        _syscall_listener_instance = SyscallListener()
    return _syscall_listener_instance


def subscribe_syscall_listener() -> bool:
    """Convenience function to subscribe the syscall listener."""
    listener = get_syscall_listener()
    return listener.subscribe()

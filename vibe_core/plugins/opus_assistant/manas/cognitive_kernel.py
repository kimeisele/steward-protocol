"""
MANAS Cognitive Kernel - The Mind of OPUS.

OPUS-032: The Awakening

"Cogito, ergo sum" - I think, therefore I am.
    - René Descartes

This is the central orchestrator of MANAS:
- Rate-limited thinking (not every tick!)
- Intent generation and management
- Human-in-the-loop approval flow
- Memory integration for learning
- Auto-execution for safe tasks

The Cognitive Kernel transforms OPUS from a reactive system
to a proactive autonomous agent.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .intent_generator import Intent, IntentGenerator, IntentPriority, IntentRisk
from .memory_store import MemoryStore

logger = logging.getLogger("MANAS.Kernel")


@dataclass
class ManasConfig:
    """Configuration for MANAS Cognitive Kernel."""

    # Thinking rate limit (minimum time between thought cycles)
    thinking_interval_minutes: int = 60  # Once per hour by default

    # Idle threshold (activate MANAS after this much idle time)
    idle_threshold_minutes: int = 30

    # Auto-execute safe intents without approval?
    auto_execute_safe: bool = False  # Conservative default

    # Max intents to keep in buffer
    max_intent_buffer_size: int = 10

    # Intent expiry (hours)
    intent_expiry_hours: int = 24


@dataclass
class IntentBufferEntry:
    """An entry in the intent buffer (for OPUS.md display)."""

    intent: Intent
    status: str = "pending"  # pending, approved, rejected, executed, expired
    added_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    executed_at: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None


class CognitiveKernel:
    """
    The Mind of OPUS - Proactive Autonomous Cognition.

    This kernel:
    1. Monitors system state via Prakriti
    2. Generates intents when opportunities arise
    3. Manages intent buffer (displayed in OPUS.md)
    4. Handles approval/rejection flow
    5. Executes approved intents
    6. Learns from outcomes via MemoryStore

    Rate Limiting:
    - MANAS doesn't think on every KERNEL_TICK
    - It activates on an hourly pulse or after idle threshold
    - This prevents token/CPU burn

    Human-in-the-Loop:
    - Most intents go to Intent Buffer for approval
    - Only SAFE risk intents can auto-execute
    - User can approve/reject from OPUS.md
    """

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[ManasConfig] = None,
    ):
        """
        Initialize MANAS Cognitive Kernel.

        Args:
            workspace: Workspace root
            config: Optional configuration
        """
        self._workspace = workspace or Path.cwd()
        self._config = config or ManasConfig()

        # Core components
        self._memory = MemoryStore(workspace=self._workspace)
        self._intent_generator = IntentGenerator(workspace=self._workspace, memory_store=self._memory)

        # Intent buffer (persisted to .opus_state/manas_intents.json)
        self._intent_buffer: List[IntentBufferEntry] = []
        self._load_intent_buffer()

        # Rate limiting state
        self._last_thought_time: Optional[datetime] = None
        self._last_activity_time: datetime = datetime.utcnow()

        # Callbacks for execution
        self._execution_callback: Optional[Callable[[Intent], Dict[str, Any]]] = None

        logger.info("MANAS Cognitive Kernel initialized")

    # =========================================================================
    # CORE API
    # =========================================================================

    def think(self, context: Optional[Dict[str, Any]] = None, force: bool = False) -> List[Intent]:
        """
        Execute a thought cycle - analyze state and generate intents.

        This is rate-limited unless force=True.

        Args:
            context: Optional context from Prakriti
            force: Force thinking even if rate limit hasn't passed

        Returns:
            List of newly generated intents
        """
        # Rate limit check
        if not force and not self._should_think():
            logger.debug("MANAS: Rate limited, skipping thought cycle")
            return []

        logger.info("MANAS: Beginning thought cycle...")
        self._last_thought_time = datetime.utcnow()

        # Clean up expired intents
        self._cleanup_expired_intents()

        # Generate new intents
        new_intents = self._intent_generator.generate_intents(context or {})

        # Add to buffer (if not already present)
        added = []
        for intent in new_intents:
            if not self._is_intent_duplicate(intent):
                entry = IntentBufferEntry(intent=intent)
                self._intent_buffer.append(entry)
                added.append(intent)

                # Auto-execute if safe and enabled
                if self._config.auto_execute_safe and intent.auto_executable and intent.risk == IntentRisk.SAFE:
                    logger.info(f"MANAS: Auto-executing safe intent: {intent.title}")
                    self._execute_intent(entry)

        # Trim buffer to max size
        while len(self._intent_buffer) > self._config.max_intent_buffer_size:
            # Remove oldest non-pending intents first
            removed = False
            for i, entry in enumerate(self._intent_buffer):
                if entry.status != "pending":
                    self._intent_buffer.pop(i)
                    removed = True
                    break
            if not removed:
                # Remove oldest pending
                self._intent_buffer.pop(0)

        # Persist
        self._save_intent_buffer()

        if added:
            logger.info(f"MANAS: Generated {len(added)} new intents")
        else:
            logger.debug("MANAS: No new intents generated")

        return added

    def approve_intent(self, intent_id: str) -> bool:
        """
        Approve an intent for execution.

        Args:
            intent_id: ID of the intent to approve

        Returns:
            True if approved and executed successfully
        """
        entry = self._find_intent_entry(intent_id)
        if not entry:
            logger.warning(f"Intent {intent_id} not found")
            return False

        if entry.status != "pending":
            logger.warning(f"Intent {intent_id} is not pending (status: {entry.status})")
            return False

        entry.status = "approved"
        return self._execute_intent(entry)

    def reject_intent(self, intent_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject an intent.

        Args:
            intent_id: ID of the intent to reject
            reason: Optional reason for rejection

        Returns:
            True if rejected successfully
        """
        entry = self._find_intent_entry(intent_id)
        if not entry:
            logger.warning(f"Intent {intent_id} not found")
            return False

        entry.status = "rejected"

        # Record in memory (so we don't suggest it again soon)
        self._memory.record_intent_outcome(
            intent_type=entry.intent.intent_type,
            description=entry.intent.title,
            outcome="rejected",
            feedback=reason,
        )

        self._save_intent_buffer()
        logger.info(f"Intent {intent_id} rejected: {reason or 'no reason given'}")
        return True

    def get_pending_intents(self) -> List[Intent]:
        """Get all pending intents (for OPUS.md display)."""
        return [entry.intent for entry in self._intent_buffer if entry.status == "pending"]

    def get_intent_buffer(self) -> List[IntentBufferEntry]:
        """Get the full intent buffer."""
        return list(self._intent_buffer)

    def set_execution_callback(self, callback: Callable[[Intent], Dict[str, Any]]) -> None:
        """
        Set the callback for intent execution.

        Args:
            callback: Function that takes an Intent and returns execution result
        """
        self._execution_callback = callback

    def record_activity(self) -> None:
        """Record that system activity occurred (resets idle timer)."""
        self._last_activity_time = datetime.utcnow()

    def get_idle_minutes(self) -> int:
        """Get minutes since last activity."""
        delta = datetime.utcnow() - self._last_activity_time
        return int(delta.total_seconds() / 60)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of MANAS memory for display."""
        memories = self._memory.get_all_memories()
        successful_patterns = self._memory.get_successful_patterns(limit=5)

        # Count by outcome
        outcomes = {"success": 0, "failed": 0, "rejected": 0, "pending": 0}
        for m in memories:
            if m.outcome in outcomes:
                outcomes[m.outcome] += 1

        return {
            "total_memories": len(memories),
            "outcomes": outcomes,
            "successful_patterns": successful_patterns,
            "retention_days": self._memory.MEMORY_RETENTION_DAYS,
        }

    # =========================================================================
    # INTERNAL METHODS
    # =========================================================================

    def _should_think(self) -> bool:
        """Check if MANAS should think (rate limit + idle check)."""
        now = datetime.utcnow()

        # Check idle threshold
        idle_minutes = self.get_idle_minutes()
        if idle_minutes >= self._config.idle_threshold_minutes:
            logger.debug(f"MANAS: Idle for {idle_minutes} min, should think")
            return True

        # Check time since last thought
        if self._last_thought_time is None:
            return True  # First thought

        minutes_since_thought = (now - self._last_thought_time).total_seconds() / 60
        if minutes_since_thought >= self._config.thinking_interval_minutes:
            return True

        return False

    def _is_intent_duplicate(self, intent: Intent) -> bool:
        """Check if similar intent already exists in buffer."""
        for entry in self._intent_buffer:
            if entry.status == "pending" and entry.intent.intent_type == intent.intent_type:
                return True
        return False

    def _find_intent_entry(self, intent_id: str) -> Optional[IntentBufferEntry]:
        """Find intent entry by ID."""
        for entry in self._intent_buffer:
            if entry.intent.id == intent_id:
                return entry
        return None

    def _execute_intent(self, entry: IntentBufferEntry) -> bool:
        """
        Execute an approved intent.

        Args:
            entry: The intent buffer entry to execute

        Returns:
            True if execution succeeded
        """
        intent = entry.intent
        logger.info(f"MANAS: Executing intent: {intent.title}")

        start_time = datetime.utcnow()
        success = False
        result = {}

        try:
            if self._execution_callback:
                result = self._execution_callback(intent)
                success = result.get("success", False)
            elif intent.circuit_to_execute:
                # Execute via circuit (would integrate with kernel_tick)
                logger.info(f"MANAS: Would execute circuit: {intent.circuit_to_execute}")
                # For now, mark as success (actual execution TBD)
                success = True
                result = {"status": "circuit_queued", "circuit": intent.circuit_to_execute}
            else:
                logger.warning(f"No execution method for intent: {intent.id}")
                result = {"error": "No execution method available"}

        except Exception as e:
            logger.error(f"Intent execution failed: {e}")
            result = {"error": str(e)}
            success = False

        # Update entry
        entry.status = "executed" if success else "failed"
        entry.executed_at = datetime.utcnow().isoformat()
        entry.execution_result = result

        # Record in memory
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        self._memory.record_intent_outcome(
            intent_type=intent.intent_type,
            description=intent.title,
            outcome="success" if success else "failed",
            context=intent.params,
            feedback=result.get("error"),
            execution_time_ms=execution_time,
        )

        self._save_intent_buffer()

        if success:
            logger.info(f"MANAS: Intent {intent.id} executed successfully")
        else:
            logger.warning(f"MANAS: Intent {intent.id} execution failed: {result.get('error')}")

        return success

    def _cleanup_expired_intents(self) -> None:
        """Remove expired intents from buffer."""
        now = datetime.utcnow()
        expiry_threshold = now - timedelta(hours=self._config.intent_expiry_hours)
        expiry_str = expiry_threshold.isoformat()

        original_count = len(self._intent_buffer)
        self._intent_buffer = [
            entry for entry in self._intent_buffer if entry.added_at >= expiry_str or entry.status == "pending"
        ]

        expired = original_count - len(self._intent_buffer)
        if expired > 0:
            logger.debug(f"MANAS: Cleaned up {expired} expired intents")

    # =========================================================================
    # PERSISTENCE
    # =========================================================================

    def _get_buffer_file(self) -> Path:
        """Get path to intent buffer file."""
        return self._workspace / ".opus_state" / "manas_intents.json"

    def _load_intent_buffer(self) -> None:
        """Load intent buffer from disk."""
        try:
            buffer_file = self._get_buffer_file()
            if buffer_file.exists():
                data = json.loads(buffer_file.read_text())

                self._intent_buffer = []
                for entry_data in data.get("intents", []):
                    intent_data = entry_data.get("intent", {})

                    # Reconstruct Intent
                    intent = Intent(
                        id=intent_data.get("id", "unknown"),
                        intent_type=intent_data.get("intent_type", "unknown"),
                        title=intent_data.get("title", "Unknown"),
                        description=intent_data.get("description", ""),
                        reasoning=intent_data.get("reasoning", ""),
                        priority=IntentPriority(intent_data.get("priority", "medium")),
                        risk=IntentRisk(intent_data.get("risk", "medium")),
                        created_at=intent_data.get("created_at", datetime.utcnow().isoformat()),
                        circuit_to_execute=intent_data.get("circuit_to_execute"),
                        params=intent_data.get("params", {}),
                        auto_executable=intent_data.get("auto_executable", False),
                        expires_at=intent_data.get("expires_at"),
                    )

                    entry = IntentBufferEntry(
                        intent=intent,
                        status=entry_data.get("status", "pending"),
                        added_at=entry_data.get("added_at", datetime.utcnow().isoformat()),
                        executed_at=entry_data.get("executed_at"),
                        execution_result=entry_data.get("execution_result"),
                    )
                    self._intent_buffer.append(entry)

                logger.debug(f"Loaded {len(self._intent_buffer)} intents from disk")

        except Exception as e:
            logger.warning(f"Could not load intent buffer: {e}")
            self._intent_buffer = []

    def _save_intent_buffer(self) -> None:
        """Save intent buffer to disk."""
        try:
            buffer_file = self._get_buffer_file()
            buffer_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "intents": [
                    {
                        "intent": entry.intent.to_dict(),
                        "status": entry.status,
                        "added_at": entry.added_at,
                        "executed_at": entry.executed_at,
                        "execution_result": entry.execution_result,
                    }
                    for entry in self._intent_buffer
                ],
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Atomic write
            temp_file = buffer_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.replace(buffer_file)

        except Exception as e:
            logger.warning(f"Could not save intent buffer: {e}")

    # =========================================================================
    # INTEGRATION POINTS
    # =========================================================================

    def get_intent_buffer_for_opus(self) -> Dict[str, Any]:
        """
        Get intent buffer formatted for OPUS.md display.

        Returns data ready to be rendered in the Intent Buffer section.
        """
        pending = [entry for entry in self._intent_buffer if entry.status == "pending"]
        executed = [entry for entry in self._intent_buffer if entry.status == "executed"][-5:]  # Last 5

        return {
            "pending": [
                {
                    "id": entry.intent.id,
                    "title": entry.intent.title,
                    "description": entry.intent.description,
                    "priority": entry.intent.priority.value,
                    "risk": entry.intent.risk.value,
                    "reasoning": entry.intent.reasoning,
                    "auto_executable": entry.intent.auto_executable,
                }
                for entry in pending
            ],
            "recent_executed": [
                {
                    "id": entry.intent.id,
                    "title": entry.intent.title,
                    "status": entry.status,
                    "executed_at": entry.executed_at,
                    "success": entry.execution_result.get("success", False) if entry.execution_result else False,
                }
                for entry in executed
            ],
            "total_pending": len(pending),
            "idle_minutes": self.get_idle_minutes(),
            "last_thought": self._last_thought_time.isoformat() if self._last_thought_time else None,
        }

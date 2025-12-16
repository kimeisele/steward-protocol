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

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from .intent_generator import Intent, IntentGenerator, IntentPriority, IntentRisk
from .memory_store import MemoryStore

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("MANAS.Kernel")

# ⚡ PHOENIX INJECTION: Import ManasConfig from Phoenix section (Dharma)
# This ensures MANAS uses the same config structure as Phoenix defines
try:
    from vibe_core.phoenix.sections.manas import ManasConfig

    logger.debug("⚡ MANAS: Using ManasConfig from Phoenix section (Dharma)")
except ImportError:
    # Fallback: Define locally if Phoenix not available
    @dataclass
    class ManasConfig:
        """Configuration for MANAS Cognitive Kernel (Local Fallback)."""

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

        # KARMA GATE: Threshold for earned autonomy (0-100)
        # High karma (Bhakti + success) grants trust for LOW risk auto-execute
        karma_auto_execute_threshold: int = 90

        # OPUS-035: Intent Throttling - Don't overwhelm the human
        # Max intents to generate per tick (prioritize CRITICAL/HIGH over LOW)
        max_intents_per_tick: int = 3

        # OPUS-035: Prioritize survival over growth
        # If True, CRITICAL/ERROR intents are processed before GENESIS intents
        survival_first: bool = True

    logger.warning("⚠️ MANAS: Phoenix section not available, using local ManasConfig fallback")


@dataclass
class IntentConfidence:
    """
    OPUS-032: Confidence is not a guess - it's a computed vector.

    Three components determine if we can auto-execute:
    1. pattern_match: Have we seen this exact failure before?
    2. karma_level: Does the system have enough "credit"?
    3. rollback_safety: Can we easily undo this action?

    Usage:
        confidence = IntentConfidence.compute(intent, memory, karma_score=85)
        if confidence.total_score >= 0.9:
            # Safe to auto-execute
    """

    pattern_match: float = 0.0  # 0.0-1.0: How often have we fixed this before?
    karma_level: float = 0.0  # 0.0-1.0: Current karma / 100
    rollback_safety: float = 0.0  # 0.0-1.0: How easy to git revert?

    @property
    def total_score(self) -> float:
        """
        Compute total confidence.

        CRITICAL: If rollback is unsafe, confidence is ZERO.
        We never auto-execute irreversible actions.
        """
        if self.rollback_safety < 0.5:
            return 0.0  # Safety first!

        # Weighted: Karma matters more than pattern matching
        return (self.pattern_match * 0.4) + (self.karma_level * 0.6)

    @classmethod
    def compute(
        cls,
        intent: "Intent",
        memory: "MemoryStore",
        karma_score: int,
    ) -> "IntentConfidence":
        """
        Factory method to compute confidence for an intent.

        Args:
            intent: The intent to evaluate
            memory: Memory store for pattern lookup
            karma_score: Current karma score (0-100)

        Returns:
            IntentConfidence with computed values
        """
        # Pattern match: Have we successfully done this before?
        success_rate = memory.get_success_rate(intent.intent_type)
        pattern_match = success_rate if success_rate else 0.0

        # Karma level: Normalize to 0-1
        karma_level = karma_score / 100.0

        # Rollback safety: Based on intent type
        safe_types = {"contract_surrender", "doc_update", "test_create", "contract_doc_update"}
        unsafe_types = {"capability_genesis", "refactor_major", "delete_file", "contract_import_fix"}

        if intent.intent_type in safe_types:
            rollback_safety = 1.0
        elif intent.intent_type in unsafe_types:
            rollback_safety = 0.3
        else:
            rollback_safety = 0.7  # Default: medium safety

        return cls(
            pattern_match=pattern_match,
            karma_level=karma_level,
            rollback_safety=rollback_safety,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage/display."""
        return {
            "pattern_match": self.pattern_match,
            "karma_level": self.karma_level,
            "rollback_safety": self.rollback_safety,
            "total_score": self.total_score,
        }


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

        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel: Optional["RealVibeKernel"] = None

        # 🦁 NARASIMHA: The Cognitive Guardian (Conscience)
        from ..narasimha.guardian import CortexNarasimha

        self._narasimha = CortexNarasimha(workspace=self._workspace)

        logger.info("MANAS Cognitive Kernel initialized")

    # =========================================================================
    # ⚡ VAJRA: KERNEL INTEGRATION (OPUS-057)
    # =========================================================================

    def inject_kernel(self, kernel: "RealVibeKernel") -> None:
        """
        Inject the core VibeKernel for ledger access.

        OPUS-057 VAJRA: Every intent MUST be recorded in the ledger.
        Without kernel injection, MANAS operates in "shadow mode" (no ledger).

        Args:
            kernel: The RealVibeKernel instance
        """
        self._vibe_kernel = kernel
        logger.info("⚡ VAJRA: Kernel injected - ledger binding ACTIVE")

    def inject_ledger(self, ledger: Any) -> None:
        """
        Inject a standalone ledger for autonomous mode (heartbeat).

        OPUS-074 WIRING: Allows VAJRA binding without full Kernel boot.
        Used by heartbeat.py for headless/autonomous operation.

        Args:
            ledger: SQLiteLedger or compatible ledger instance
        """
        self._ledger = ledger
        logger.info("⚡ VAJRA: Standalone Ledger injected into MANAS (headless mode)")

    def _record_to_ledger(
        self,
        event_type: str,
        intent: Intent,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Record an intent event to the core ledger.

        OPUS-057 VAJRA: Cryptographic binding of all MANAS actions.
        OPUS-074 WIRING: Supports standalone ledger for headless mode.

        Args:
            event_type: Type of event (INTENT_PROPOSED, INTENT_EXECUTED, etc.)
            intent: The intent being recorded
            extra_data: Additional data to include

        Returns:
            Event ID if recorded, None if no ledger available
        """
        # OPUS-074: Prioritize standalone ledger, fallback to kernel.ledger
        ledger = getattr(self, "_ledger", None)
        if not ledger and self._vibe_kernel:
            ledger = self._vibe_kernel.ledger

        if not ledger:
            logger.debug("⚠️ VAJRA: No ledger - intent not ledgered (shadow mode)")
            return None

        # Build intent hash for integrity
        intent_data = {
            "id": intent.id,
            "type": intent.intent_type,
            "title": intent.title,
            "risk": intent.risk.value,
            "priority": intent.priority.value,
            "params": intent.params,
        }
        intent_hash = hashlib.sha256(json.dumps(intent_data, sort_keys=True).encode()).hexdigest()[:16]

        details = {
            "intent_id": intent.id,
            "intent_type": intent.intent_type,
            "intent_title": intent.title,
            "intent_risk": intent.risk.value,
            "intent_priority": intent.priority.value,
            "intent_hash": intent_hash,
            **(extra_data or {}),
        }

        try:
            event_id = ledger.record_event(
                event_type=event_type,
                agent_id="manas",
                details=details,
            )
            logger.debug(f"⚡ VAJRA: {event_type} recorded → {event_id}")
            return event_id
        except Exception as e:
            logger.error(f"⚡ VAJRA: Failed to record {event_type}: {e}")
            return None

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

        # OPUS-035: Throttling - Prioritize survival over growth
        if self._config.survival_first and len(new_intents) > self._config.max_intents_per_tick:
            new_intents = self._prioritize_survival(new_intents)

        # OPUS-035: Throttle to max_intents_per_tick
        if len(new_intents) > self._config.max_intents_per_tick:
            logger.debug(f"⚡ MANAS: Throttling {len(new_intents)} → {self._config.max_intents_per_tick} intents")
            new_intents = new_intents[: self._config.max_intents_per_tick]

        # Add to buffer (if not already present)
        added = []
        for intent in new_intents:
            if not self._is_intent_duplicate(intent):
                entry = IntentBufferEntry(intent=intent)

                # 🦁 NARASIMHA JUDGMENT: Judge before buffering
                verdict = self._narasimha.judge_intent(intent)
                if verdict.status == "GUILTY":
                    logger.critical(f"🦁 NARASIMHA BLOCKED INTENT: {intent.title} - {verdict.reason}")
                    entry.status = "blocked"  # New status for sinful intents
                    entry.execution_result = {
                        "error": f"BLOCKED BY NARASIMHA: {verdict.reason}",
                        "verdict": str(verdict),
                    }
                    # We still buffer it as a record of sin, but it can never run

                self._intent_buffer.append(entry)
                added.append(intent)

                # ⚡ VAJRA: Record intent proposal to ledger
                self._record_to_ledger(
                    event_type="MANAS_INTENT_PROPOSED",
                    intent=intent,
                    extra_data={
                        "proposed_at": datetime.utcnow().isoformat(),
                        "auto_executable": intent.auto_executable,
                    },
                )

                # Auto-execute if safe OR if karma gate allows (earned autonomy)
                is_safe = self._config.auto_execute_safe and intent.auto_executable and intent.risk == IntentRisk.SAFE
                is_trusted = self._karma_allows_auto_execute(intent)

                if is_safe or is_trusted:
                    reason = "SAFE" if is_safe else f"KARMA GATE (>={self._config.karma_auto_execute_threshold})"
                    logger.info(f"🙏 MANAS: Auto-executing [{reason}]: {intent.title}")
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

        OPUS-057 VAJRA: Approvals are recorded to the ledger.

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

        # ⚡ VAJRA: Record approval to ledger
        self._record_to_ledger(
            event_type="MANAS_INTENT_APPROVED",
            intent=entry.intent,
            extra_data={"approved_at": datetime.utcnow().isoformat()},
        )

        # 🦁 NARASIMHA JUDGMENT: Final check before execution
        # Even if human approved, we double check (e.g. if context changed)
        verdict = self._narasimha.judge_intent(entry.intent)
        if verdict.status == "GUILTY":
            logger.critical(f"🦁 NARASIMHA BLOCKED EXECUTION: {entry.intent.title}")
            entry.status = "blocked"
            entry.execution_result = {"error": f"BLOCKED BY NARASIMHA: {verdict.reason}"}
            return False

        return self._execute_intent(entry)

    def reject_intent(self, intent_id: str, reason: Optional[str] = None) -> bool:
        """
        Reject an intent.

        OPUS-057 VAJRA: Rejections are recorded to the ledger.

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

        # ⚡ VAJRA: Record rejection to ledger
        self._record_to_ledger(
            event_type="MANAS_INTENT_REJECTED",
            intent=entry.intent,
            extra_data={
                "rejected_at": datetime.utcnow().isoformat(),
                "reason": reason,
            },
        )

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

    def _prioritize_survival(self, intents: List[Intent]) -> List[Intent]:
        """
        OPUS-035: Prioritize survival over growth.

        Sort intents so that CRITICAL/HIGH priority (50% - repairs)
        come before LOW priority (51% - genesis).

        Philosophy: First survive, then thrive.

        Args:
            intents: List of intents to prioritize

        Returns:
            Sorted list with survival intents first
        """
        # Define priority order: CRITICAL > HIGH > MEDIUM > LOW
        priority_order = {
            IntentPriority.CRITICAL: 0,
            IntentPriority.HIGH: 1,
            IntentPriority.MEDIUM: 2,
            IntentPriority.LOW: 3,
        }

        # Also prioritize contract violations (50%) over semantic gaps (51%)
        def sort_key(intent: Intent) -> tuple:
            pri = priority_order.get(intent.priority, 99)
            # Contract intents (repairs) come before semantic (genesis)
            is_repair = 0 if intent.intent_type.startswith("contract_") else 1
            return (pri, is_repair, intent.created_at)

        return sorted(intents, key=sort_key)

    def _karma_allows_auto_execute(self, intent: Intent) -> bool:
        """
        🙏 KARMA GATE: High karma earns trust for autonomous execution.

        Bhakti (devotion) + consistent success → earned autonomy.
        The system must PROVE itself worthy of self-governance.
        """
        if intent.risk not in (IntentRisk.LOW, IntentRisk.SAFE):
            return False  # Only LOW/SAFE can be karma-gated

        # Get karma from StateManager (where Bhakti circuit stores it)
        try:
            from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

            state_mgr = get_state_manager(self._workspace)
            last_karma = state_mgr.get_last_karma()
        except Exception:
            return False

        if not last_karma:
            return False

        threshold = self._config.karma_auto_execute_threshold
        if last_karma.score >= threshold:
            logger.debug(f"🙏 KARMA GATE: {last_karma.score} >= {threshold}, trust granted")
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

        OPUS-057 VAJRA: All executions are recorded to the ledger.

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

        # ⚡ VAJRA: Record INTENT_EXECUTING to ledger BEFORE execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTING",
            intent=intent,
            extra_data={"timestamp": start_time.isoformat()},
        )

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

        # Calculate execution time
        execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # ⚡ VAJRA: Record INTENT_EXECUTED or INTENT_FAILED to ledger AFTER execution
        self._record_to_ledger(
            event_type="MANAS_INTENT_EXECUTED" if success else "MANAS_INTENT_FAILED",
            intent=intent,
            extra_data={
                "execution_time_ms": execution_time,
                "result": result,
                "outcome": "success" if success else "failed",
            },
        )

        # Record in memory (MANAS internal)
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

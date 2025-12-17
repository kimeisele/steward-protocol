"""
MANAS Memory Store - Learning from the Past.

OPUS-032: The Cognitive Kernel

"Those who cannot remember the past are condemned to repeat it."
    - George Santayana

This module provides persistent memory for MANAS:
- Remember past intents and their outcomes
- Learn what works and what doesn't
- Avoid suggesting the same failed action repeatedly
- Build "muscle memory" for successful patterns

Storage: .opus_state/manas_memory.json (survives restarts)
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MANAS.Memory")


@dataclass
class MemoryEntry:
    """A single memory of a past intent and its outcome."""

    intent_type: str  # e.g., "cleanup_branches", "fix_imports"
    intent_description: str  # Human-readable description
    timestamp: str  # ISO format
    outcome: str  # "success", "failed", "rejected", "pending"
    context: Dict[str, Any] = field(default_factory=dict)  # What triggered it
    feedback: Optional[str] = None  # Why it failed/was rejected
    execution_time_ms: Optional[int] = None  # How long it took

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary."""
        return cls(**data)


class MemoryStore:
    """
    Persistent memory for MANAS cognitive kernel.

    Features:
    - Stores intent history with outcomes
    - Calculates success rates per intent type
    - Implements forgetting (old memories fade)
    - Prevents repeated failures (cooldown period)

    Storage location: .opus_state/manas_memory.json

    Configuration: Reads from config/opus.yaml under 'memory' section.
    Falls back to defaults if config not available.
    """

    # Default values (overridden by config/opus.yaml)
    DEFAULT_MEMORY_RETENTION_DAYS = 30
    DEFAULT_FAILURE_COOLDOWN_HOURS = 24
    DEFAULT_MAX_MEMORIES = 500
    DEFAULT_SUCCESS_RATE_THRESHOLD = 0.7
    DEFAULT_MIN_ATTEMPTS_FOR_TRUST = 2

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize memory store.

        Args:
            workspace: Workspace root (defaults to cwd)
        """
        self._workspace = workspace or Path.cwd()
        self._memory_file = self._workspace / ".opus_state" / "manas_memory.json"
        self._memories: List[MemoryEntry] = []

        # Load config from opus.yaml
        self._config = self._load_config()
        self._load()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load memory configuration from config/opus.yaml.

        Returns config dict with defaults for any missing keys.
        """
        config = {
            "max_memories": self.DEFAULT_MAX_MEMORIES,
            "retention_days": self.DEFAULT_MEMORY_RETENTION_DAYS,
            "failure_cooldown_hours": self.DEFAULT_FAILURE_COOLDOWN_HOURS,
            "success_rate_threshold": self.DEFAULT_SUCCESS_RATE_THRESHOLD,
            "min_attempts_for_trust": self.DEFAULT_MIN_ATTEMPTS_FOR_TRUST,
        }

        config_path = self._workspace / "config" / "opus.yaml"
        if config_path.exists():
            try:
                import yaml

                with open(config_path) as f:
                    data = yaml.safe_load(f)
                    memory_config = data.get("memory", {})
                    config.update(memory_config)
                    logger.debug(f"Loaded memory config from opus.yaml: {memory_config}")
            except Exception as e:
                logger.warning(f"Could not load memory config: {e}")

        return config

    # Properties for backward compatibility
    @property
    def MEMORY_RETENTION_DAYS(self) -> int:
        return self._config.get("retention_days", self.DEFAULT_MEMORY_RETENTION_DAYS)

    @property
    def FAILURE_COOLDOWN_HOURS(self) -> int:
        return self._config.get("failure_cooldown_hours", self.DEFAULT_FAILURE_COOLDOWN_HOURS)

    @property
    def MAX_MEMORIES(self) -> int:
        return self._config.get("max_memories", self.DEFAULT_MAX_MEMORIES)

    def _load(self) -> None:
        """Load memories from disk."""
        try:
            if self._memory_file.exists():
                data = json.loads(self._memory_file.read_text())
                self._memories = [MemoryEntry.from_dict(m) for m in data.get("memories", [])]
                logger.debug(f"Loaded {len(self._memories)} memories from disk")
        except Exception as e:
            logger.warning(f"Could not load memories: {e}")
            self._memories = []

    def _save(self) -> None:
        """Save memories to disk (atomic write)."""
        try:
            self._memory_file.parent.mkdir(parents=True, exist_ok=True)

            # Prune old memories before saving
            self._prune_old_memories()

            data = {"memories": [m.to_dict() for m in self._memories], "updated_at": datetime.utcnow().isoformat()}

            # Atomic write
            temp_file = self._memory_file.with_suffix(".tmp")
            temp_file.write_text(json.dumps(data, indent=2))
            temp_file.replace(self._memory_file)

            logger.debug(f"Saved {len(self._memories)} memories to disk")
        except Exception as e:
            logger.warning(f"Could not save memories: {e}")

    def _prune_old_memories(self) -> None:
        """Remove memories older than retention period."""
        cutoff = datetime.utcnow() - timedelta(days=self.MEMORY_RETENTION_DAYS)
        cutoff_str = cutoff.isoformat()

        original_count = len(self._memories)
        self._memories = [m for m in self._memories if m.timestamp >= cutoff_str]

        # Also enforce max limit (keep most recent)
        if len(self._memories) > self.MAX_MEMORIES:
            self._memories = sorted(self._memories, key=lambda m: m.timestamp, reverse=True)[: self.MAX_MEMORIES]

        pruned = original_count - len(self._memories)
        if pruned > 0:
            logger.info(f"Pruned {pruned} old memories")

    def remember(self, entry: MemoryEntry) -> None:
        """
        Store a new memory.

        Args:
            entry: The memory entry to store
        """
        self._memories.append(entry)
        self._save()
        logger.debug(f"Remembered: {entry.intent_type} ({entry.outcome})")

    def record_intent_outcome(
        self,
        intent_type: str,
        description: str,
        outcome: str,
        context: Optional[Dict[str, Any]] = None,
        feedback: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
    ) -> None:
        """
        Convenience method to record an intent outcome.

        Args:
            intent_type: Type of intent (e.g., "cleanup_branches")
            description: Human-readable description
            outcome: "success", "failed", "rejected", "pending"
            context: Additional context
            feedback: Why it failed/was rejected
            execution_time_ms: How long it took
        """
        entry = MemoryEntry(
            intent_type=intent_type,
            intent_description=description,
            timestamp=datetime.utcnow().isoformat(),
            outcome=outcome,
            context=context or {},
            feedback=feedback,
            execution_time_ms=execution_time_ms,
        )
        self.remember(entry)

    def get_success_rate(self, intent_type: str) -> float:
        """
        Get success rate for a specific intent type.

        Args:
            intent_type: Type of intent to check

        Returns:
            Success rate (0.0 - 1.0), or 0.5 if no history
        """
        relevant = [m for m in self._memories if m.intent_type == intent_type and m.outcome in ("success", "failed")]

        if not relevant:
            return 0.5  # No history = neutral

        successes = sum(1 for m in relevant if m.outcome == "success")
        return successes / len(relevant)

    def is_in_cooldown(self, intent_type: str) -> bool:
        """
        Check if intent type is in cooldown after failure.

        Args:
            intent_type: Type of intent to check

        Returns:
            True if we should wait before suggesting again
        """
        cooldown_cutoff = datetime.utcnow() - timedelta(hours=self.FAILURE_COOLDOWN_HOURS)
        cooldown_str = cooldown_cutoff.isoformat()

        recent_failures = [
            m
            for m in self._memories
            if m.intent_type == intent_type and m.outcome == "failed" and m.timestamp >= cooldown_str
        ]

        return len(recent_failures) > 0

    def was_recently_rejected(self, intent_type: str, hours: int = 24) -> bool:
        """
        Check if intent type was recently rejected by user.

        Args:
            intent_type: Type of intent to check
            hours: How far back to look

        Returns:
            True if user rejected this recently
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        cutoff_str = cutoff.isoformat()

        recent_rejections = [
            m
            for m in self._memories
            if m.intent_type == intent_type and m.outcome == "rejected" and m.timestamp >= cutoff_str
        ]

        return len(recent_rejections) > 0

    def get_last_attempt(self, intent_type: str) -> Optional[MemoryEntry]:
        """
        Get the most recent attempt of an intent type.

        Args:
            intent_type: Type of intent to check

        Returns:
            Most recent memory entry, or None
        """
        relevant = [m for m in self._memories if m.intent_type == intent_type]
        if not relevant:
            return None

        return max(relevant, key=lambda m: m.timestamp)

    def get_successful_patterns(self, limit: int = 10) -> List[str]:
        """
        Get intent types that have been consistently successful.

        Uses configurable thresholds from config/opus.yaml:
        - success_rate_threshold: Minimum success rate (default 0.7)
        - min_attempts_for_trust: Minimum attempts needed (default 2)

        Args:
            limit: Max patterns to return

        Returns:
            List of intent types with high success rates
        """
        # Get thresholds from config
        success_threshold = self._config.get("success_rate_threshold", self.DEFAULT_SUCCESS_RATE_THRESHOLD)
        min_attempts = self._config.get("min_attempts_for_trust", self.DEFAULT_MIN_ATTEMPTS_FOR_TRUST)

        # Group by intent type
        intent_stats: Dict[str, Dict[str, int]] = {}
        for m in self._memories:
            if m.intent_type not in intent_stats:
                intent_stats[m.intent_type] = {"success": 0, "failed": 0, "total": 0}
            intent_stats[m.intent_type][m.outcome] = intent_stats[m.intent_type].get(m.outcome, 0) + 1
            intent_stats[m.intent_type]["total"] += 1

        # Filter for successful patterns using config thresholds
        successful = []
        for intent_type, stats in intent_stats.items():
            if stats["total"] >= min_attempts:
                success_rate = stats.get("success", 0) / stats["total"]
                if success_rate >= success_threshold:
                    successful.append((intent_type, success_rate))

        # Sort by success rate and return top N
        successful.sort(key=lambda x: x[1], reverse=True)
        return [intent_type for intent_type, _ in successful[:limit]]

    def get_all_memories(self) -> List[MemoryEntry]:
        """Get all memories (for debugging/display)."""
        return list(self._memories)

    def clear(self) -> None:
        """Clear all memories (use with caution!)."""
        self._memories = []
        self._save()
        logger.warning("All memories cleared!")

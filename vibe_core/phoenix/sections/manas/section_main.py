"""
MANAS Configuration Section - The Soul's Will (Dharma).

OPUS-032: MANAS Cognitive Kernel Configuration

This section defines the policy that governs MANAS behavior:
- How often to think (thinking_interval_minutes)
- When to think during idle (idle_threshold_minutes)
- Whether to auto-execute safe intents (auto_execute_safe)
- How many intents to buffer (max_intent_buffer_size)
- Intent throttling (max_intents_per_tick)
- Survival-first priorities (survival_first)

KEY PRINCIPLE: This is Phoenix policy (Dharma/Soul), not hardcoded default.
MANAS reads these values at boot and adheres to them.
Vajra uses these values to enforce consistency against drift.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ManasConfig:
    """Configuration for MANAS Cognitive Kernel (Phoenix Section)."""

    # =========================================================================
    # Thinking Rate Limit
    # =========================================================================
    # How often MANAS performs a thought cycle
    # OPUS-174: Was 60 (lobotomy!), now 10min for responsiveness
    thinking_interval_minutes: int = 10

    # Activate MANAS after this much idle time (seconds of no user input)
    # OPUS-174: Was 30, now 5min for faster idle detection
    idle_threshold_minutes: int = 5

    # =========================================================================
    # Execution Policy
    # =========================================================================
    # Auto-execute safe intents without human approval?
    # FALSE = Conservative (require human approval for all intents)
    # TRUE = Autonomous (auto-execute SAFE risk intents)
    auto_execute_safe: bool = False

    # Karma threshold for earned autonomy (0-100)
    # If karma >= this value, auto-execute LOW risk intents
    karma_auto_execute_threshold: int = 90

    # =========================================================================
    # Intent Management
    # =========================================================================
    # Max intents to keep in buffer
    max_intent_buffer_size: int = 10

    # Intent expiry (hours) - how long to keep pending intents
    intent_expiry_hours: int = 24

    # =========================================================================
    # Intent Throttling (OPUS-035: Don't overwhelm the human)
    # =========================================================================
    # Max intents to generate per tick (prioritize CRITICAL/HIGH over LOW)
    max_intents_per_tick: int = 3

    # Prioritize survival over growth?
    # If True, CRITICAL/ERROR intents are processed before GENESIS intents
    survival_first: bool = True

    # =========================================================================
    # Serialization
    # =========================================================================

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ManasConfig":
        """
        Create ManasConfig from dictionary (loaded from YAML).

        Handles both new config structure and legacy hardcoded defaults.
        """
        if not data:
            logger.debug("No MANAS config provided, using defaults")
            return cls()

        return cls(
            thinking_interval_minutes=data.get("thinking_interval_minutes", 60),
            idle_threshold_minutes=data.get("idle_threshold_minutes", 30),
            auto_execute_safe=data.get("auto_execute_safe", False),
            karma_auto_execute_threshold=data.get("karma_auto_execute_threshold", 90),
            max_intent_buffer_size=data.get("max_intent_buffer_size", 10),
            intent_expiry_hours=data.get("intent_expiry_hours", 24),
            max_intents_per_tick=data.get("max_intents_per_tick", 3),
            survival_first=data.get("survival_first", True),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize config to dictionary."""
        return {
            "thinking_interval_minutes": self.thinking_interval_minutes,
            "idle_threshold_minutes": self.idle_threshold_minutes,
            "auto_execute_safe": self.auto_execute_safe,
            "karma_auto_execute_threshold": self.karma_auto_execute_threshold,
            "max_intent_buffer_size": self.max_intent_buffer_size,
            "intent_expiry_hours": self.intent_expiry_hours,
            "max_intents_per_tick": self.max_intents_per_tick,
            "survival_first": self.survival_first,
        }

    def validate(self) -> List[str]:
        """Validate config values."""
        errors = []

        if self.thinking_interval_minutes < 1:
            errors.append("thinking_interval_minutes must be >= 1")

        if self.idle_threshold_minutes < 1:
            errors.append("idle_threshold_minutes must be >= 1")

        if not 0 <= self.karma_auto_execute_threshold <= 100:
            errors.append("karma_auto_execute_threshold must be 0-100")

        if self.max_intent_buffer_size < 1:
            errors.append("max_intent_buffer_size must be >= 1")

        if self.intent_expiry_hours < 1:
            errors.append("intent_expiry_hours must be >= 1")

        if self.max_intents_per_tick < 1:
            errors.append("max_intents_per_tick must be >= 1")

        return errors

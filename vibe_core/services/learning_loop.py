"""
OPUS-311 Sprint 4: LearningLoop Service

The Ouroboros - Connects Reflection → CommandRegistry for self-improvement.

This service:
1. Analyzes user input patterns from Memory/Feedback
2. Detects when users frequently type variations that resolve to commands
3. Creates NEW_ALIAS proposals in Reflection
4. Auto-applies approved proposals to CommandRegistry

Usage:
    # At boot or in tick
    loop = LearningLoop.get_instance()
    loop.tick()  # Periodic learning

    # Manual trigger
    proposals = loop.analyze_alias_opportunities()
    loop.apply_pending()
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple

from vibe_core.protocols.feedback import FeedbackProtocol, get_feedback_safe
from vibe_core.protocols.memory import MemoryProtocol, get_memory_safe
from vibe_core.protocols.reflection import (
    BasicReflection,
    Insight,
    InsightType,
    Proposal,
    ProposalStatus,
    ProposalType,
    ReflectionProtocol,
    get_reflection_safe,
)

logger = logging.getLogger("LEARNING.LOOP")


@dataclass
class InputPattern:
    """A pattern of user inputs that resolve to a command."""

    input_text: str  # What user typed (e.g., "agents")
    resolved_command: str  # What it resolved to (e.g., "list_agents")
    frequency: int = 1
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    success_rate: float = 1.0


class LearningLoop:
    """
    OPUS-311 Sprint 4: The Ouroboros - Self-Improvement Loop.

    Connects:
    - Memory (what user typed) →
    - Reflection (pattern analysis) →
    - CommandRegistry (alias registration)

    Thresholds:
    - MIN_FREQUENCY: Alias candidate must be used >= 3 times
    - MIN_SUCCESS_RATE: Alias candidate must have >= 80% success rate
    - AUTO_APPROVE_THRESHOLD: Auto-approve if confidence >= 90%
    """

    # Thresholds
    MIN_FREQUENCY = 3
    MIN_SUCCESS_RATE = 0.8
    AUTO_APPROVE_THRESHOLD = 0.9
    TICK_INTERVAL_SECONDS = 60  # Don't run more than once per minute

    _instance: Optional["LearningLoop"] = None

    def __init__(
        self,
        reflection: Optional[ReflectionProtocol] = None,
        memory: Optional[MemoryProtocol] = None,
        feedback: Optional[FeedbackProtocol] = None,
    ):
        self._reflection = reflection or get_reflection_safe()
        self._memory = memory or get_memory_safe()
        self._feedback = feedback or get_feedback_safe()
        self._command_registry = None  # Lazy load to avoid circular imports

        # Track input → command mappings
        self._input_patterns: Dict[str, InputPattern] = {}

        # Track applied aliases (don't re-propose)
        self._applied_aliases: Set[str] = set()

        # Last tick time
        self._last_tick: Optional[datetime] = None

    @classmethod
    def get_instance(cls) -> "LearningLoop":
        """Singleton access."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def _get_command_registry(self):
        """Lazy load CommandRegistry to avoid circular imports."""
        if self._command_registry is None:
            from vibe_core.cli.command_registry import CommandRegistry

            self._command_registry = CommandRegistry.get_instance()
        return self._command_registry

    def record_input_resolution(
        self,
        input_text: str,
        resolved_command: str,
        success: bool = True,
    ) -> None:
        """
        Record when user input resolves to a command.

        Called by IntentMatcher when it successfully matches input to command.

        Args:
            input_text: What the user typed (e.g., "agents", "show tasks")
            resolved_command: The command it resolved to (e.g., "list_agents")
            success: Whether the command execution succeeded
        """
        # Normalize input (lowercase, strip whitespace)
        normalized = input_text.lower().strip()

        # Skip if input == command (no alias needed)
        if normalized == resolved_command.lower():
            return

        # Skip if this is already an alias
        registry = self._get_command_registry()
        if normalized in registry.get_aliases():
            return

        # Update or create pattern
        if normalized in self._input_patterns:
            pattern = self._input_patterns[normalized]
            pattern.frequency += 1
            pattern.last_seen = datetime.now()
            # Update success rate (rolling average)
            old_rate = pattern.success_rate
            pattern.success_rate = (old_rate * (pattern.frequency - 1) + (1.0 if success else 0.0)) / pattern.frequency
        else:
            self._input_patterns[normalized] = InputPattern(
                input_text=normalized,
                resolved_command=resolved_command,
                frequency=1,
                success_rate=1.0 if success else 0.0,
            )

        logger.debug(f"Recorded input resolution: '{normalized}' → '{resolved_command}'")

    def analyze_alias_opportunities(self) -> List[Proposal]:
        """
        Analyze recorded patterns for alias opportunities.

        Returns:
            List of NEW_ALIAS proposals
        """
        proposals = []
        registry = self._get_command_registry()

        for input_text, pattern in self._input_patterns.items():
            # Skip if already applied
            if input_text in self._applied_aliases:
                continue

            # Check thresholds
            if pattern.frequency < self.MIN_FREQUENCY:
                continue
            if pattern.success_rate < self.MIN_SUCCESS_RATE:
                continue

            # Check if alias would conflict with existing command
            if input_text in registry._commands:
                continue

            # Create insight
            confidence = min(
                0.5 + (pattern.frequency / 20) + (pattern.success_rate * 0.3),
                0.99,
            )

            insight = Insight(
                type=InsightType.USAGE_PATTERN,
                message=f"Users frequently type '{input_text}' meaning '{pattern.resolved_command}'",
                confidence=confidence,
                data={
                    "input": input_text,
                    "command": pattern.resolved_command,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate,
                },
            )

            # Create proposal
            import uuid

            proposal = Proposal(
                id=str(uuid.uuid4()),
                type=ProposalType.NEW_ALIAS,
                title=f"Create alias '{input_text}' → '{pattern.resolved_command}'",
                description=f"Users type '{input_text}' {pattern.frequency} times to mean '{pattern.resolved_command}' "
                f"with {pattern.success_rate:.0%} success rate.",
                insights=[insight],
                implementation={
                    "action": "register_alias",
                    "alias": input_text,
                    "target": pattern.resolved_command,
                    "source": "learning",
                },
            )

            # Auto-approve high confidence
            if confidence >= self.AUTO_APPROVE_THRESHOLD:
                proposal.status = ProposalStatus.APPROVED
                logger.info(
                    f"Auto-approved alias: '{input_text}' → '{pattern.resolved_command}' (confidence: {confidence:.0%})"
                )

            proposals.append(proposal)

            # Record in Reflection if it supports recording proposals
            if isinstance(self._reflection, BasicReflection):
                self._reflection._proposals[proposal.id] = proposal

        return proposals

    def apply_pending(self) -> int:
        """
        Apply all approved NEW_ALIAS proposals to CommandRegistry.

        Returns:
            Number of aliases applied
        """
        applied = 0
        registry = self._get_command_registry()

        # Get approved proposals from Reflection
        if isinstance(self._reflection, BasicReflection):
            proposals = [
                p
                for p in self._reflection._proposals.values()
                if p.status == ProposalStatus.APPROVED and p.type == ProposalType.NEW_ALIAS
            ]
        else:
            proposals = []

        for proposal in proposals:
            impl = proposal.implementation
            if impl.get("action") != "register_alias":
                continue

            alias = impl.get("alias")
            target = impl.get("target")
            source = impl.get("source", "learning")

            if not alias or not target:
                continue

            # Try to register
            success = registry.register_alias(alias, target, source)

            if success:
                proposal.status = ProposalStatus.APPLIED
                self._applied_aliases.add(alias)
                applied += 1
                logger.info(f"[LEARNING.LOOP] Applied alias: '{alias}' → '{target}'")
            else:
                logger.warning(f"[LEARNING.LOOP] Failed to apply alias: '{alias}' → '{target}'")

        return applied

    def tick(self) -> Dict[str, Any]:
        """
        Periodic learning tick.

        Called by scheduler or during idle time.
        Analyzes patterns and applies approved proposals.

        Returns:
            Summary of actions taken
        """
        # Rate limit
        now = datetime.now()
        if self._last_tick and (now - self._last_tick) < timedelta(seconds=self.TICK_INTERVAL_SECONDS):
            return {"skipped": True, "reason": "rate_limited"}

        self._last_tick = now

        # Analyze for new opportunities
        proposals = self.analyze_alias_opportunities()

        # Apply approved
        applied = self.apply_pending()

        result = {
            "timestamp": now.isoformat(),
            "patterns_tracked": len(self._input_patterns),
            "new_proposals": len(proposals),
            "applied_aliases": applied,
            "total_aliases": len(self._applied_aliases),
        }

        if proposals or applied:
            logger.info(f"[LEARNING.LOOP] tick: {result}")

        return result

    def get_stats(self) -> Dict[str, Any]:
        """Get learning loop statistics."""
        registry = self._get_command_registry()

        return {
            "patterns_tracked": len(self._input_patterns),
            "applied_aliases": len(self._applied_aliases),
            "registry_aliases": len(registry.get_aliases()),
            "top_patterns": sorted(
                [
                    {
                        "input": p.input_text,
                        "command": p.resolved_command,
                        "frequency": p.frequency,
                        "success_rate": p.success_rate,
                    }
                    for p in self._input_patterns.values()
                ],
                key=lambda x: x["frequency"],
                reverse=True,
            )[:10],
        }

    def suggest_aliases(self, min_frequency: int = 2) -> List[Dict[str, Any]]:
        """
        Get alias suggestions (not yet proposed).

        For manual review or CLI display.
        """
        suggestions = []

        for input_text, pattern in self._input_patterns.items():
            if input_text in self._applied_aliases:
                continue
            if pattern.frequency < min_frequency:
                continue

            suggestions.append(
                {
                    "alias": input_text,
                    "target": pattern.resolved_command,
                    "frequency": pattern.frequency,
                    "success_rate": pattern.success_rate,
                    "ready": pattern.frequency >= self.MIN_FREQUENCY and pattern.success_rate >= self.MIN_SUCCESS_RATE,
                }
            )

        return sorted(suggestions, key=lambda x: x["frequency"], reverse=True)

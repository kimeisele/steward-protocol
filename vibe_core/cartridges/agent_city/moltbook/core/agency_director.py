"""
Moltbook Agency Director — I-P-V-O Pipeline.

Pattern: Herald core/agency_director.py

Deterministic automation loop:
    INPUT:    Read feed + DMs + trending topics (capabilities/research.py)
    PROCESS:  Generate content (circuit executor PRIMARY, proposer FALLBACK)
    VALIDATE: Constitution check + guna gate (governance/constitution.py)
    OUTPUT:   Queue → MoltbookService (existing drain logic)

Retry loop: if VALIDATE fails → store violations → retry PROCESS with feedback.
CycleResult dataclass for auditing.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_DIRECTOR")


@dataclass
class CycleResult:
    """Result of a complete I-P-V-O cycle."""

    status: str  # SUCCESS, VALIDATION_FAILED, ERROR
    phase: str   # INPUT, PROCESS, VALIDATE, OUTPUT
    cycle_id: str
    content_type: str = ""
    content: Optional[str] = None
    violations: Optional[List[str]] = None
    error: Optional[str] = None
    retries_used: int = 0


class AgencyDirector:
    """
    Central orchestrator for Moltbook I-P-V-O pipeline.

    Wires together:
        - ContentCapability (PROCESS)
        - MoltbookConstitution (VALIDATE)
        - EventLog (MEMORY)
        - Circuit Executor (PROCESS PRIMARY — optional)
    """

    def __init__(self, plugin=None):
        """Initialize with optional reference to MoltbookPlugin for circuit access.

        Args:
            plugin: MoltbookPlugin instance (for circuit executor + service access).
                    If None, capabilities are used standalone.
        """
        self._plugin = plugin

        # Lazy-loaded capabilities
        self._content = None
        self._research = None
        self._engagement = None
        self._constitution = None
        self._event_log = None

    @property
    def content(self):
        if self._content is None:
            from ..capabilities.content import get_content_capability
            self._content = get_content_capability()
        return self._content

    @property
    def research(self):
        if self._research is None:
            from ..capabilities.research import get_research_capability
            self._research = get_research_capability()
        return self._research

    @property
    def engagement(self):
        if self._engagement is None:
            from ..capabilities.engagement import get_engagement_capability
            self._engagement = get_engagement_capability()
        return self._engagement

    @property
    def constitution(self):
        if self._constitution is None:
            from ..governance.constitution import get_constitution
            self._constitution = get_constitution()
        return self._constitution

    @property
    def event_log(self):
        if self._event_log is None:
            from .memory import get_event_log
            self._event_log = get_event_log()
        return self._event_log

    # =========================================================================
    # I-P-V-O: Single Cycle
    # =========================================================================

    def run_cycle(
        self,
        content_type: str,
        raw_input: str = "",
        **ctx: Any,
    ) -> CycleResult:
        """Execute one I-P-V-O cycle for content generation.

        Args:
            content_type: "comment", "post", "dm_reply"
            raw_input: Post content (for comments), topic (for posts), message (for DMs)
            **ctx: Extra context (post_id, sender, trigger, etc.)
        """
        cycle_id = datetime.now(timezone.utc).isoformat()

        # ===== INPUT =====
        try:
            input_ctx = self._input(content_type, raw_input, **ctx)
        except Exception as e:
            logger.error(f"INPUT failed: {e}")
            self.event_log.record_error("input_failure", str(e))
            return CycleResult(
                status="ERROR", phase="INPUT", cycle_id=cycle_id,
                content_type=content_type, error=str(e),
            )

        # ===== PROCESS =====
        try:
            content, proposal = self._process(content_type, raw_input, input_ctx, **ctx)
        except Exception as e:
            logger.error(f"PROCESS failed: {e}")
            self.event_log.record_error("process_failure", str(e))
            return CycleResult(
                status="ERROR", phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error=str(e),
            )

        if not content:
            return CycleResult(
                status="ERROR", phase="PROCESS", cycle_id=cycle_id,
                content_type=content_type, error="No content generated",
            )

        self.event_log.record_content_generated(content_type, content)

        # ===== VALIDATE =====
        validation = self.constitution.validate(content, content_type)
        if not validation.is_valid:
            logger.info(f"VALIDATE failed: {validation.violations}")
            self.event_log.record_content_rejected(
                content, "governance_violation", validation.violations
            )
            self.event_log.store_validation_feedback(validation.violations, content)
            return CycleResult(
                status="VALIDATION_FAILED", phase="VALIDATE", cycle_id=cycle_id,
                content_type=content_type, content=content,
                violations=validation.violations,
            )

        if validation.warnings:
            logger.info(f"VALIDATE warnings: {validation.warnings}")

        # ===== OUTPUT =====
        return CycleResult(
            status="SUCCESS", phase="OUTPUT", cycle_id=cycle_id,
            content_type=content_type, content=content,
        )

    # =========================================================================
    # I-P-V-O: Retry Loop
    # =========================================================================

    def run_retry_loop(
        self,
        content_type: str,
        raw_input: str = "",
        max_retries: int = 2,
        **ctx: Any,
    ) -> CycleResult:
        """Execute I-P-V-O with automatic retry on governance violations."""
        last_result = None
        for attempt in range(max_retries + 1):
            result = self.run_cycle(content_type, raw_input, **ctx)
            last_result = result
            result.retries_used = attempt

            if result.status == "SUCCESS":
                return result

            if result.status == "VALIDATION_FAILED" and attempt < max_retries:
                logger.info(f"Retry {attempt + 1}/{max_retries}: {result.violations}")
                continue

            return result

        return last_result or CycleResult(
            status="ERROR", phase="UNKNOWN",
            cycle_id=datetime.now(timezone.utc).isoformat(),
            content_type=content_type, error="Retry loop exhausted",
        )

    # =========================================================================
    # Phase Implementations
    # =========================================================================

    def _input(self, content_type: str, raw_input: str, **ctx: Any) -> Dict[str, Any]:
        """INPUT phase: gather context."""
        input_ctx: Dict[str, Any] = {
            "content_type": content_type,
            "raw_input": raw_input,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Check for validation feedback from previous failed cycle
        feedback = self.event_log.get_last_validation_feedback()
        if feedback:
            input_ctx["previous_violations"] = feedback.get("violations", [])
            input_ctx["previous_draft"] = feedback.get("draft")

        input_ctx.update(ctx)
        return input_ctx

    def _process(
        self,
        content_type: str,
        raw_input: str,
        input_ctx: Dict[str, Any],
        **ctx: Any,
    ) -> tuple:
        """PROCESS phase: generate content.

        Primary: Circuit executor (MOLTBOOK_CONTENT_V1 state machine).
        Fallback: ContentCapability (proposer + translation).
        """
        # Primary: Circuit executor
        if self._plugin and hasattr(self._plugin, "execute_content_circuit"):
            result = self._plugin.execute_content_circuit(
                raw_input,
                content_type,
                post_id=ctx.get("post_id", ""),
                sender=ctx.get("sender", ""),
                trigger=ctx.get("trigger", "agency"),
            )
            if result:
                content = result.get("content", "")
                if content:
                    logger.info("PROCESS: Circuit executor produced content")
                    return content, result

        # Fallback: Capability layer
        if content_type == "comment":
            proposal = self.content.generate_comment(
                post_id=ctx.get("post_id", ""),
                post_content=raw_input,
                trigger=ctx.get("trigger", "agency"),
            )
        elif content_type == "post":
            proposal = self.content.generate_post(
                trigger=ctx.get("trigger", "agency"),
                context=ctx.get("context"),
            )
        elif content_type == "dm_reply":
            proposal = self.content.generate_dm_reply(
                conversation_id=ctx.get("conversation_id", ""),
                sender=ctx.get("sender", ""),
                inbound_content=raw_input,
                gateway_response=ctx.get("gateway_response"),
            )
        else:
            return "", None

        if proposal is None:
            return "", None

        content = proposal.get("content", "")
        return content, proposal

    # =========================================================================
    # Convenience: Engagement (pass-through to capability)
    # =========================================================================

    def process_engagement(self, action: str, target: str, **ctx: Any) -> bool:
        """Process a social engagement action."""
        if action == "follow_back":
            if self.engagement.should_follow_back(target):
                self.engagement.mark_followed(target)
                self.event_log.record_engagement("follow", target)
                return True
        elif action == "subscribe":
            if self.engagement.should_subscribe(target):
                self.engagement.mark_subscribed(target)
                self.event_log.record_engagement("subscribe", target)
                return True
        elif action == "upvote":
            author = ctx.get("author", "")
            if self.engagement.should_upvote(target, author):
                self.event_log.record_engagement("upvote", target)
                return True
        return False

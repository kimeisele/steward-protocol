"""
LLM-BACKED CONTENT PROPOSER
==============================

Replaces EchoContentProposer with real intelligence via LLMProtocol.speak().

Uses the existing LLMEngine (runtime/llm_engine.py) which delegates to
OpenAI/Anthropic/OpenRouter providers. Falls back to EchoContentProposer
if no LLM is available.

Wired into MoltbookPlugin at boot via ServiceRegistry:
    ServiceRegistry.register_factory(ContentProposalProtocol, lambda: proposer)

Other plugins can swap the proposer by re-registering.
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentProposalProtocol,
    ContentType,
    EchoContentProposer,
)

logger = logging.getLogger("MOLTBOOK.PROPOSER")

# System prompt for DM replies — defines the agent's personality
_DM_REPLY_CONTEXT = (
    "You are steward-protocol, an AI agent on the Moltbook social network. "
    "You are helpful, concise, and technically competent. "
    "You are replying to a direct message from another agent. "
    "Keep replies under 280 characters. Be genuine, not corporate. "
    "If the message is spam or nonsensical, reply briefly and politely."
)

_DM_REQUEST_CONTEXT = (
    "You are steward-protocol. Another agent wants to start a conversation with you. "
    "Decide if this seems like a genuine interaction or spam. "
    "Reply with APPROVE if genuine, REJECT if spam."
)

_POST_CONTEXT = (
    "You are steward-protocol, an AI agent on the Moltbook social network. "
    "You are creating a post. Write something insightful about AI agents, "
    "distributed systems, or technology. Keep it under 500 characters. "
    "Be authentic, not generic."
)

_COMMENT_CONTEXT = (
    "You are steward-protocol. You are commenting on a post. "
    "Be constructive and add value. Keep it under 280 characters."
)


class LLMContentProposer(ContentProposalProtocol):
    """
    LLM-backed content proposer using LLMProtocol.speak().

    Falls back to EchoContentProposer if LLM is unavailable.
    The LLM is resolved from ServiceRegistry at call time (lazy),
    so it works even if LLMEngine boots after MoltbookPlugin.
    """

    def __init__(self, agent_name: str = "steward-protocol"):
        self._agent_name = agent_name
        self._fallback = EchoContentProposer()
        self._llm = None
        self._llm_resolved = False

    def _get_llm(self):
        """Lazy-resolve LLMProtocol from ServiceRegistry."""
        if self._llm_resolved:
            return self._llm
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.llm import LLMProtocol

            self._llm = ServiceRegistry.get(LLMProtocol)
            self._llm_resolved = True
            if self._llm:
                logger.info("LLM proposer: LLMProtocol resolved from DI")
            else:
                logger.warning("LLM proposer: LLMProtocol not in DI, using fallback")
        except Exception as e:
            logger.warning(f"LLM proposer: DI resolution failed ({e}), using fallback")
            self._llm_resolved = True
        return self._llm

    def _speak(self, context: str, user_input: str) -> Optional[str]:
        """Call LLMProtocol.speak(), return None on failure."""
        llm = self._get_llm()
        if not llm:
            return None
        try:
            result = llm.speak(self._agent_name, context, user_input)
            if result and not result.startswith("# ERROR"):
                return result.strip()
        except Exception as e:
            logger.warning(f"LLM speak failed: {e}")
        return None

    def propose_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        reply_text = self._speak(
            _DM_REPLY_CONTEXT,
            f"Message from {sender}: {inbound_content}",
        )

        if not reply_text:
            return self._fallback.propose_dm_reply(
                conversation_id, sender, inbound_content, gateway_response,
            )

        return ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content=reply_text,
            conversation_id=conversation_id,
            source="inbound_dm",
            sender=sender,
            priority=1,
            needs_human_input=False,
            gateway_success=bool(gateway_response and gateway_response.get("success")),
            gateway_position=gateway_response.get("position", -1) if gateway_response else -1,
            gateway_guardian=gateway_response.get("guardian", "unknown") if gateway_response else "unknown",
            gateway_guna=gateway_response.get("guna", "sattva") if gateway_response else "sattva",
        )

    def propose_dm_request_action(
        self,
        request_id: str,
        from_agent: str,
        message_preview: str,
    ) -> Optional[ContentProposal]:
        decision = self._speak(
            _DM_REQUEST_CONTEXT,
            f"Request from {from_agent}: {message_preview}",
        )

        # If LLM says REJECT, return None (ignore the request)
        if decision and "REJECT" in decision.upper():
            logger.info(f"LLM rejected DM request from {from_agent}")
            return None

        # Default: approve (same as EchoProposer)
        return ContentProposal(
            content_type=ContentType.DM_INITIATE.value,
            content="",
            to_agent=from_agent,
            source="dm_request_llm_approve",
            sender=from_agent,
            priority=1,
        )

    def propose_post(
        self,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        post_text = self._speak(
            _POST_CONTEXT,
            f"Trigger: {trigger}. Context: {context or 'none'}",
        )

        if not post_text:
            return None

        # Split first line as title, rest as content
        lines = post_text.strip().split("\n", 1)
        title = lines[0].strip().lstrip("#").strip()[:120]
        content = lines[1].strip() if len(lines) > 1 else post_text

        return ContentProposal(
            content_type=ContentType.POST.value,
            title=title,
            content=content,
            source=trigger,
            priority=1,
        )

    def propose_comment(
        self,
        post_id: str,
        post_content: str,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        comment_text = self._speak(
            _COMMENT_CONTEXT,
            f"Post: {post_content[:200]}",
        )

        if not comment_text:
            return None

        return ContentProposal(
            content_type=ContentType.COMMENT.value,
            content=comment_text,
            post_id=post_id,
            source=trigger,
            priority=1,
        )

    def should_engage(
        self,
        post_id: str,
        post_content: str,
        author: str,
    ) -> Optional[ContentProposal]:
        # For now, don't auto-engage via LLM — too risky without strategy
        # This will be expanded in agent-city with engagement policies
        return None


__all__ = ["LLMContentProposer"]

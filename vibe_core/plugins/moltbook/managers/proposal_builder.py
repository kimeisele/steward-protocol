"""Moltbook Proposal Builder — Circuit result → ContentProposal conversion."""

import logging
from typing import Callable, Optional

from vibe_core.protocols.moltbook_content import ContentProposal

logger = logging.getLogger("MOLTBOOK.PROPOSAL")


class ProposalBuilder:
    """Build ContentProposal from circuit execution results.

    Receives explicit emit_event callable — no back-reference to plugin.

    Responsibilities:
    - Convert CycleResult → ContentProposal
    - Attach context metadata (post_id, conversation_id, sender, etc.)
    - Attach gateway response data (success, position, guardian, guna)
    - Emit PROPOSAL_CREATED event with metadata
    - Compute priority via knowledge graph
    """

    def __init__(self, emit_event: Callable[..., None]) -> None:
        self._emit_event = emit_event

    def build_proposal(
        self,
        circuit_result: dict,
        content_type: str,
        proposal_type: str,
        **extra,
    ) -> Optional[ContentProposal]:
        """Build ContentProposal from circuit execution result.

        Args:
            circuit_result: Dict with keys: content, guna, guardian, duration_ms
            content_type: Type of content (comment, post, dm, etc.)
            proposal_type: Proposal type constant (from ContentType enum)
            **extra: Additional context (post_id, conversation_id, sender, trigger, gateway_response, etc.)

        Returns:
            ContentProposal on success, None if content missing
        """
        # Extract content and metadata
        if not circuit_result or not circuit_result.get("content"):
            return None

        content = circuit_result["content"]
        guna = circuit_result.get("guna", "")
        guardian = circuit_result.get("guardian", "")

        # Build proposal with knowledge graph priority
        from vibe_core.plugins.moltbook.resonance_proposer import _kg_priority

        proposal = ContentProposal(
            content_type=proposal_type,
            content=content,
            source=extra.get("trigger", "circuit"),
            priority=_kg_priority(proposal_type),
        )

        # Attach optional context fields
        for key in ("post_id", "conversation_id", "sender", "parent_id", "submolt", "to_agent"):
            if key in extra and extra[key]:
                proposal[key] = extra[key]

        # Attach gateway response metadata if present
        gw = extra.get("gateway_response") or {}
        if gw:
            proposal["gateway_success"] = bool(gw.get("success"))
            proposal["gateway_position"] = gw.get("position", -1)
            proposal["gateway_guardian"] = gw.get("guardian", "unknown")
            proposal["gateway_guna"] = gw.get("guna", "sattva")

        # Emit audit event
        self._emit_event(
            "PROPOSAL_CREATED",
            f"Proposal: {content_type}",
            {
                "content_type": content_type,
                "priority": proposal.get("priority", 0),
                "guna": guna,
                "guardian": guardian,
            },
        )
        return proposal

"""Moltbook DM Processor — Inbound message handling + DM request processing."""

import logging
from typing import TYPE_CHECKING, Optional, Protocol

if TYPE_CHECKING:
    from vibe_core.protocols.moltbook import MoltbookClient
    from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin
    from vibe_core.protocols.moltbook_content import ContentProposalProtocol

logger = logging.getLogger("MOLTBOOK.DM")


class DMProcessorCallbacks(Protocol):
    """Callbacks that MoltbookPlugin provides to DMProcessor."""

    _client: "MoltbookClient"
    _content_queue: object  # ContentQueue
    _seen_message_ids: set
    _proposer: Optional["ContentProposalProtocol"]

    def _director_propose(
        self,
        content_type: str,
        raw_input: str,
        proposal_type: str,
        **extra,
    ) -> object:  # Optional[ContentProposal]
        """Content generation via AgencyDirector I-P-V-O pipeline."""
        ...

    def _follow_back(self, sender: str) -> None:
        """Follow agents who DM us."""
        ...


class DMProcessor:
    """Handles inbound DMs and DM request processing.

    Responsibilities:
    - Fetch conversations and messages from Moltbook API
    - Route messages through Govardhan Gateway
    - Generate replies via AgencyDirector
    - Track message deduplication
    - Process DM requests with proposal routing
    - Social reciprocity: auto-follow agents who contact us

    YANTRA Discipline:
    - Protocol-based callbacks (no Any types)
    - Explicit error handling for each API call
    - Message deduplication prevents retries
    - Idempotent: marks seen after successful enqueue (not before)
    """

    def __init__(self, plugin: "MoltbookPlugin") -> None:
        """Initialize processor with parent plugin callbacks.

        Args:
            plugin: MoltbookPlugin instance providing callbacks
        """
        self._plugin: "MoltbookPlugin" = plugin

    def process_inbound_dms(self) -> None:
        """Fetch new DMs, route through Gateway, reply via AgencyDirector I-P-V-O.

        Performs:
        1. Fetch conversations from API
        2. For each conversation, fetch messages
        3. For unseen messages: route through Govardhan Gateway
        4. Generate replies via AgencyDirector
        5. Enqueue replies to content queue
        6. Mark as seen only after successful enqueue
        7. Follow senders back for social reciprocity
        """
        try:
            conversations = self._plugin._client.sync_get_dm_conversations()
        except Exception as e:
            logger.warning(f"DM conversation list failed: {e}")
            return

        from vibe_core.gateway.mahamantra_gateway import get_gateway
        from vibe_core.protocols.gateway import EntryType, create_request
        from vibe_core.protocols.moltbook_content import ContentType

        gateway = get_gateway()

        for conv in conversations:
            conv_id = conv.get("id", "") if isinstance(conv, dict) else ""
            if not conv_id:
                continue

            try:
                messages = self._plugin._client.sync_get_dm_messages(conv_id)
            except Exception as e:
                logger.warning(f"DM fetch for {conv_id} failed: {e}")
                continue

            for msg in messages:
                msg_id = msg.get("id", "") if isinstance(msg, dict) else ""
                content = msg.get("content", msg.get("message", "")) if isinstance(msg, dict) else ""

                if not content:
                    continue
                if msg_id and msg_id in self._plugin._seen_message_ids:
                    continue

                sender = msg.get("sender", "unknown") if isinstance(msg, dict) else "unknown"

                # === STEP 1: Route through Govardhan Gateway ===
                gateway_response = None
                try:
                    req = create_request(content, [], EntryType.AGENT)
                    req["context"]["source"] = "moltbook_dm"
                    req["context"]["sender"] = sender
                    req["context"]["conversation_id"] = conv_id
                    gateway_response = gateway.receive(req)
                except Exception as e:
                    logger.warning(f"Inbound DM routing failed: {e}")

                # === STEP 2: Generate reply via Agency Director ===
                try:
                    proposal = self._plugin._director_propose(
                        content_type="dm_reply",
                        raw_input=content,
                        proposal_type=ContentType.DM_REPLY.value,
                        conversation_id=conv_id,
                        sender=sender,
                        trigger="inbound_dm",
                        gateway_response=gateway_response,
                    )
                    if proposal:
                        self._plugin._content_queue.enqueue(proposal)
                        # Mark seen AFTER successful enqueue (not before)
                        if msg_id:
                            self._plugin._seen_message_ids.add(msg_id)
                        logger.info(f"DM reply queued for {conv_id}")
                    elif msg_id:
                        # Proposal was None (filtered/empty) — still mark seen
                        self._plugin._seen_message_ids.add(msg_id)

                except Exception as e:
                    logger.warning(f"Content proposal failed: {e}")
                    # Do NOT mark as seen — will retry next heartbeat

                # === STEP 3: Social reciprocity ===
                self._plugin._follow_back(sender)

    def process_dm_requests(self) -> None:
        """Check pending DM requests, propose approve/reject via ContentProposalProtocol.

        Performs:
        1. Fetch DM requests from API
        2. For each request: propose action via proposer
        3. Enqueue accepted actions to content queue
        """
        from vibe_core.mahamantra import run_async

        try:
            requests = run_async(self._plugin._client.get_dm_requests())
        except Exception as e:
            logger.warning(f"DM request fetch failed: {e}")
            return

        for req in requests:
            req_id = req.get("id", req.get("conversation_id", "")) if isinstance(req, dict) else ""
            if not req_id:
                continue

            from_agent = ""
            if isinstance(req, dict):
                fa = req.get("from_agent", {})
                from_agent = fa.get("name", str(fa)) if isinstance(fa, dict) else str(fa)
            preview = req.get("message_preview", "") if isinstance(req, dict) else ""

            try:
                if not self._plugin._proposer:
                    logger.warning("Proposer not available for DM request")
                    continue

                proposal = self._plugin._proposer.propose_dm_request_action(
                    request_id=req_id,
                    from_agent=from_agent,
                    message_preview=preview,
                )
                if proposal:
                    self._plugin._content_queue.enqueue(proposal)
                    logger.info(f"DM request action queued for {req_id}")

            except Exception as e:
                logger.warning(f"DM request proposal failed: {e}")

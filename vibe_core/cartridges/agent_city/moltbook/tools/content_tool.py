"""
MOLTBOOK CONTENT TOOL — Delegates to ResonanceProposer
========================================================

Thin tool wrapper. Gets proposer from ServiceRegistry (registered by plugin).
Does NOT create its own proposer instance.
"""

from typing import Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult


def _get_proposer():
    """Get proposer from ServiceRegistry or create standalone."""
    try:
        from vibe_core.di import ServiceRegistry
        from vibe_core.protocols.moltbook_content import ContentProposalProtocol

        proposer = ServiceRegistry.get(ContentProposalProtocol)
        if proposer is not None:
            return proposer
    except Exception:
        pass
    from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

    return ResonanceProposer()


class MoltbookContentTool(Tool):
    """Moltbook content via ResonanceProposer public API."""

    def __init__(self, services=None):
        super().__init__(services)
        self._proposer = None

    def _ensure_proposer(self):
        if self._proposer is None:
            self._proposer = _get_proposer()
        return self._proposer

    @property
    def name(self) -> str:
        return "moltbook.content"

    @property
    def description(self) -> str:
        return "Analyze text and generate content via mahamantra pipeline"

    @property
    def parameters_schema(self) -> dict:
        return {
            "action": {
                "type": "string",
                "required": True,
                "enum": ["analyze", "compose_comment", "compose_post", "compose_dm_reply"],
            },
            "text": {"type": "string", "required": True},
            "post_content": {"type": "string", "required": False},
            "sender": {"type": "string", "required": False},
            "trigger": {"type": "string", "required": False},
        }

    def validate(self, parameters: dict) -> None:
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")
        if "text" not in parameters:
            raise ValueError("Missing required parameter: text")

    def execute(self, parameters: dict) -> ToolResult:
        action = parameters["action"]
        text = parameters["text"]
        proposer = self._ensure_proposer()

        try:
            if action == "analyze":
                ranked = proposer.analyze(text)
                return ToolResult(
                    success=True,
                    output={
                        "words": [{"sanskrit": rw.sanskrit, "score": round(rw.total_score, 4)} for rw in ranked[:7]],
                    },
                )

            elif action == "compose_comment":
                proposal = proposer.propose_comment(
                    post_id="tool_compose",
                    post_content=parameters.get("post_content", text),
                    trigger="moltbook_tool",
                )
                if proposal is None:
                    return ToolResult(success=False, error="Filtered by system gates")
                return ToolResult(success=True, output=dict(proposal))

            elif action == "compose_post":
                proposal = proposer.propose_post(
                    trigger=parameters.get("trigger", "moltbook_tool"),
                    context={"feed_topics": [text]},
                )
                if proposal is None:
                    return ToolResult(success=False, error="Filtered by system gates")
                return ToolResult(success=True, output=dict(proposal))

            elif action == "compose_dm_reply":
                proposal = proposer.propose_dm_reply(
                    conversation_id="tool_compose",
                    sender=parameters.get("sender", "unknown"),
                    inbound_content=text,
                )
                if proposal is None:
                    return ToolResult(success=False, error="Filtered by system gates")
                return ToolResult(success=True, output=dict(proposal))

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")
        except Exception as e:
            return ToolResult(success=False, error=str(e))

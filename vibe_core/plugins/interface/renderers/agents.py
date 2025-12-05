"""
Agents Renderer.
Delegates to Scribe.
"""

from .base import ScribeDelegatingRenderer


class AgentsRenderer(ScribeDelegatingRenderer):
    @property
    def name(self) -> str:
        return "agents"

    @property
    def document_name(self) -> str:
        return "AGENTS.md"

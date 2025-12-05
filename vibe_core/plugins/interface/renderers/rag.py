"""
RAG Renderer.
Delegates to Scribe (via Analyst).
"""

from .base import ScribeDelegatingRenderer


class RagRenderer(ScribeDelegatingRenderer):
    @property
    def name(self) -> str:
        return "rag"

    @property
    def document_name(self) -> str:
        return "RAG.md"

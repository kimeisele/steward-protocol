"""
Index Renderer.
Delegates to Scribe.
"""

from .base import ScribeDelegatingRenderer


class IndexRenderer(ScribeDelegatingRenderer):
    @property
    def name(self) -> str:
        return "index"

    @property
    def document_name(self) -> str:
        return "INDEX.md"

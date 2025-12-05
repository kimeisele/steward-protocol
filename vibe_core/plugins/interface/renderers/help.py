"""
Help Renderer.
Delegates to Scribe.
"""

from .base import ScribeDelegatingRenderer


class HelpRenderer(ScribeDelegatingRenderer):
    @property
    def name(self) -> str:
        return "help"

    @property
    def document_name(self) -> str:
        return "HELP.md"

"""
CityMap Renderer.
Delegates to Scribe.
"""

from .base import ScribeDelegatingRenderer


class CityMapRenderer(ScribeDelegatingRenderer):
    @property
    def name(self) -> str:
        return "citymap"

    @property
    def document_name(self) -> str:
        return "CITYMAP.md"

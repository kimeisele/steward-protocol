"""
GOLDEN TEMPLATE - Copy this folder to create a new renderer.

Example: Create a "status" renderer for STATUS.md

    cp -r _template status
    # Edit status/renderer.py:
    #   1. Rename class: GoldenRenderer -> StatusRenderer
    #   2. Set name: return "status"
    #   3. Add data sources for your sections
    #   4. Add to config/interface.yaml:
    #
    #      renderers:
    #        status:
    #          enabled: true
    #          output: STATUS.md
    #          sections:
    #            - id: overview
    #              owner: live
    #              source: status.overview
    #            - id: notes
    #              owner: ai
"""

from typing import TYPE_CHECKING, Any, Dict, List

from ..base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol


class GoldenRenderer(BaseRenderer):
    """
    COPY THIS CLASS for new renderers.

    A renderer needs:
    1. name property -> matches config/interface.yaml key
    2. _register_data_sources() -> maps source paths to methods
    3. Data source methods -> return data for LIVE sections
    """

    def __init__(self, kernel: "KernelProtocol"):
        super().__init__(kernel)
        self._register_data_sources()

    @property
    def name(self) -> str:
        """CHANGE THIS to match renderers.X in interface.yaml"""
        return "golden"

    def _register_data_sources(self) -> None:
        """
        Register data sources for LIVE sections.

        The source path must match what's in interface.yaml:
            sections:
              - id: overview
                source: golden.overview  <- this path
        """
        self.register_data_source("golden.overview", self._get_overview)
        self.register_data_source("golden.items", self._get_items)

    def render(self) -> None:
        """Render the document - usually don't need to change this."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)

    # =========================================================================
    # DATA SOURCES - Return data for LIVE sections
    # =========================================================================

    def _get_overview(self) -> str:
        """
        Return string for simple text display.

        Example output in markdown:
            ## Overview
            **Status**: Running | **Items**: 42
        """
        return "**Status**: Running | **Items**: 42"

    def _get_items(self) -> List[Dict[str, Any]]:
        """
        Return list of dicts for table display.
        Set element_type: table in config.

        Example output in markdown:
            ## Items
            | Name | Count |
            | --- | --- |
            | Alpha | 10 |
            | Beta | 20 |
        """
        return [
            {"Name": "Alpha", "Count": 10},
            {"Name": "Beta", "Count": 20},
        ]


def create_renderer(kernel: "KernelProtocol", config: Dict[str, Any]) -> GoldenRenderer:
    """Factory function - required for plugin loading."""
    return GoldenRenderer(kernel)

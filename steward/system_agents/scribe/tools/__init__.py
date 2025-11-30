"""
SCRIBE Documentation Generation Tools

All renderer tools implement the Tool protocol and are kernel-managed.
"""

from .agents_renderer import AgentsRenderer
from .citymap_renderer import CitymapRenderer
from .help_renderer import HelpRenderer
from .index_renderer import IndexRenderer
from .readme_renderer import ReadmeRenderer

__all__ = [
    "AgentsRenderer",
    "CitymapRenderer",
    "HelpRenderer",
    "ReadmeRenderer",
    "IndexRenderer",
]

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

from vibe_core.io_service import DocumentType

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class BaseRenderer(ABC):
    """
    Abstract base class for Interface Renderers.

    ARCHITECTURE (UNIFIED UI):
    - Renderers are SLAVES to InterfacePlugin (the KING)
    - Renderers produce CONTENT only (generate_content)
    - InterfacePlugin writes ALL files with UNIFIED headers
    - Individual renderers do NOT call kernel.io directly

    Migration path:
    - Old: render() writes directly
    - New: generate_content() returns string, InterfacePlugin writes
    """

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the renderer (e.g. 'envoy', 'settings')."""
        pass

    @property
    def output_file(self) -> str:
        """Output filename (default: NAME.md)."""
        return f"{self.name.upper()}.md"

    @property
    def doc_type(self) -> DocumentType:
        """Document type for I/O service (default: READONLY)."""
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """
        Generate content for this renderer.

        Returns:
            Markdown content string (WITHOUT header - InterfacePlugin adds it)
            None if rendering should be skipped
        """
        # Default implementation calls legacy render() for backwards compat
        # Subclasses should override this method
        return None

    @abstractmethod
    def render(self) -> None:
        """
        Legacy render method - writes directly.

        DEPRECATED: New renderers should implement generate_content() instead.
        This method is kept for backwards compatibility during migration.
        """
        pass

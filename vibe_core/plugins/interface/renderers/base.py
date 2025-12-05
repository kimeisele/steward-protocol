from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class BaseRenderer(ABC):
    """Abstract base class for Interface Renderers."""

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the renderer (e.g. 'envoy', 'settings')."""
        pass

    @abstractmethod
    def render(self) -> None:
        """Perform rendering logic."""
        pass

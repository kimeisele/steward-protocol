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


class ScribeDelegatingRenderer(BaseRenderer):
    """
    Renderer that delegates to Scribe agent.
    Submits a task to Scribe to generate the document.
    """

    def __init__(self, kernel, update_interval_seconds: int = 3600):
        super().__init__(kernel)
        self.update_interval = update_interval_seconds
        self.last_update = 0.0

    @property
    @abstractmethod
    def document_name(self) -> str:
        """Name of the document to generate (e.g. 'AGENTS.md')."""
        pass

    def render(self) -> None:
        import time

        now = time.time()
        if now - self.last_update < self.update_interval:
            return

        self.last_update = now

        # Submit task to Scribe
        from vibe_core.scheduling import Task

        task = Task(
            title=f"Generate {self.document_name}",
            description=f"Auto-generate {self.document_name} documentation.",
            assigned_agent="scribe",
            priority=10,  # Low priority background task
            metadata={"type": "doc_generation", "target": self.document_name},
        )

        try:
            self.kernel.scheduler.submit_task(task)
        except Exception:
            pass

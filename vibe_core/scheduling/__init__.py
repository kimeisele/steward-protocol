"""Task scheduling definitions for VibeOS"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xd095996d"  # GenesisByte: parampara % 37 == 0

from .in_memory import InMemoryScheduler
from .task import Task, TaskStatus

__all__ = ["Task", "TaskStatus", "InMemoryScheduler"]

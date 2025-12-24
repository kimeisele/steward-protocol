"""
Tasks Renderer.
Renders TASKS.md (Mission Control).

Architecture Pattern:
- Uses render_sections() from BaseRenderer (config-driven)
- Registers data sources for active and completed tasks
- Fallback to generate_content() if no sections defined
"""

import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.io_service import DocumentType
from vibe_core.task_management.models import TaskStatus
from vibe_core.task_management.task_manager import TaskManager

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_TASKS")


class TasksRenderer(BaseRenderer):
    """
    Renders TASKS.md and handles Paper UI synchronization.
    Uses TaskManager for persistence.
    """

    def __init__(self, kernel: "RealVibeKernel", update_interval_seconds: int = 60):
        super().__init__(kernel)
        self.update_interval = update_interval_seconds
        self.last_update = 0.0
        self.project_root = Path.cwd()
        self.task_manager = TaskManager(self.project_root)
        self.tasks_md_path = self.project_root / "TASKS.md"
        self._register_data_sources()

    def _register_data_sources(self) -> None:
        """Register data sources for section-based rendering."""
        self.register_data_source("tasks.active", self._get_active_tasks)
        self.register_data_source("tasks.completed", self._get_completed_tasks)

    def _get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get active tasks for table rendering."""
        tasks = self.task_manager.list_tasks(status=TaskStatus.PENDING)
        tasks.extend(self.task_manager.list_tasks(status=TaskStatus.IN_PROGRESS))
        if not tasks:
            return [{"Task": "_No active tasks_", "Status": "-", "Agent": "-"}]
        return [{"Task": t.title[:40], "Status": t.status.value, "Agent": t.assigned_agent or "-"} for t in tasks[:10]]

    def _get_completed_tasks(self) -> List[Dict[str, Any]]:
        """Get completed tasks for table rendering."""
        tasks = self.task_manager.list_tasks(status=TaskStatus.COMPLETED)
        if not tasks:
            return [{"Task": "_No completed tasks_", "Completed": "-"}]
        return [
            {"Task": t.title[:40], "Completed": str(t.completed_at)[:10] if t.completed_at else "-"} for t in tasks[:10]
        ]

    def render(self) -> None:
        """Render TASKS.md using config-driven sections."""
        config = self.get_config()
        if config and config.sections:
            self._read_tasks_md()  # Sync user input first
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            content = self.generate_content()
            if content:
                self.merge_and_write(content)

    @property
    def name(self) -> str:
        return "tasks"

    @property
    def output_file(self) -> str:
        return "TASKS.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.BIDIRECTIONAL

    def generate_content(self) -> Optional[str]:
        """Generate TASKS.md content (UNIFIED UI pattern)."""
        # Throttle updates
        now = time.time()
        if now - self.last_update < self.update_interval:
            return None

        self.last_update = now

        # 1. Read TASKS.md (Sync User Input -> TaskManager)
        self._read_tasks_md()

        # 2. Generate content
        return self._generate_markdown()

    def _read_tasks_md(self) -> None:
        """Read TASKS.md and create new tasks from checkboxes."""
        if not self.tasks_md_path.exists():
            return

        try:
            content = self.tasks_md_path.read_text()

            # Parse inbox section
            inbox_match = re.search(r"## 🎯 Inbox \(New Commands\).*?(?=##|\Z)", content, re.DOTALL)
            if not inbox_match:
                return

            inbox_text = inbox_match.group(0)

            # Find unchecked tasks: - [ ] Task description @agent priority:high
            task_pattern = re.compile(r"- \[ \] (.+?)(?:@(\w+))?\s*(?:priority:(high|medium|low))?")

            new_tasks = 0
            for match in task_pattern.finditer(inbox_text):
                description = match.group(1).strip()
                agent = match.group(2)
                priority_str = match.group(3)

                # Map priority
                priority_map = {"high": 90, "medium": 50, "low": 10}
                priority = priority_map.get(priority_str, 50)

                # Check if task already exists (avoid duplicates)
                existing = [t for t in self.task_manager.list_tasks() if t.title == description]
                if existing:
                    continue

                # Create task
                try:
                    task = self.task_manager.add_task(
                        title=description,
                        description=f"Created from TASKS.md at {datetime.now().isoformat()}",
                        priority=priority,
                        assigned_agent=agent,
                    )
                    logger.info(f"📝 Created task from TASKS.md: {task.title}")

                    # Submit to Kernel Scheduler as well?
                    # If TaskManager is separate, we might want to notify Kernel.
                    # But for now, we just use TaskManager as the source of truth for TASKS.md.
                    # The execution engine (heartbeat or kernel) will pick it up from TaskManager.

                    new_tasks += 1
                except Exception as e:
                    logger.warning(f"⚠️  Failed to create task '{description}': {e}")

            if new_tasks > 0:
                logger.info(f"✅ Created {new_tasks} new tasks from TASKS.md")

        except Exception as e:
            logger.error(f"Error reading TASKS.md: {e}")

    def _generate_markdown(self) -> str:
        """Generate TASKS.md content."""
        all_tasks = self.task_manager.list_tasks()

        pending = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        running = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        blocked = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]

        content = f"""# 📋 Mission Control

> **Auto-Generated Task Board** | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
> **Status:** 🟢 Operational | **Active Tasks:** {len(running)} | **Completed:** {len(completed)}

---

## 🎯 Inbox (New Commands)

Write your tasks here. The system will pick them up automatically.

**Syntax:**
```markdown
- [ ] Task description @agent_name priority:high
- [ ] Another task @engineer priority:medium
- [ ] Analyze codebase @analyst
```

**Available Agents:**
`@envoy` `@engineer` `@analyst` `@herald` `@civic` `@scribe` `@auditor` `@mechanic` `@archivist` `@marketer` `@scientist` `@watchman`

---

## 🔄 Active Missions (In Progress)

"""
        if running:
            for task in running:
                agent = task.assignee or "auto-routed"
                content += f"- [~] {task.title} @{agent}\n"
                content += f"  > *Status: RUNNING (ID: {task.id[:8]}...)*\n"
                content += f"  > **Priority:** {task.priority} | **Started:** {task.updated_at.strftime('%H:%M')}\n\n"
        else:
            content += "No active missions yet.\n\n"

        content += "---\n\n## ✅ Recently Completed\n\n"

        if completed:
            recent = sorted(completed, key=lambda t: t.updated_at, reverse=True)[:5]
            for task in recent:
                agent = task.assignee or "auto-routed"
                content += f"- [x] {task.title} @{agent}\n"
                content += f"  > *Completed: {task.updated_at.strftime('%Y-%m-%d %H:%M')}*\n\n"
        else:
            content += "No completed tasks yet.\n\n"

        content += "---\n\n## 📊 System Health\n\n"
        content += "| Metric | Value |\n"
        content += "|--------|-------|\n"
        content += f"| Total Tasks | {len(all_tasks)} |\n"
        content += f"| Pending | {len(pending)} |\n"
        content += f"| Running | {len(running)} |\n"
        content += f"| Completed | {len(completed)} |\n"
        content += f"| Blocked | {len(blocked)} |\n\n"

        content += "---\n\n"
        content += "**Heartbeat:** Operational  \n"
        content += f"**Last Pulse:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}  \n"
        content += "**Next Check:** ~1 minute\n\n"

        content += """---

## 📖 How It Works

1. **Write tasks** in the Inbox section using checkboxes `- [ ]`
2. **Tag agents** with `@agent_name` to route directly (optional)
3. **Set priority** with `priority:high|medium|low` (optional)
4. **Save** the file
5. **System picks up** tasks automatically

---

*Generated by InterfacePlugin (TasksRenderer)*
"""
        return content

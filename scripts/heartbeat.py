#!/usr/bin/env python3
"""
🫀 HEARTBEAT ENGINE - The Autonomous Task Orchestrator

This is the "ignition key" for the TaskManager Ferrari.
Runs every 15 minutes via GitHub Actions to:
1. Sync TASKS.md ↔ TaskManager (bi-directional)
2. Ingest tasks from data/inbox/*.json
3. Execute pending tasks
4. Commit progress to Git

Architecture:
- Paper UI: TASKS.md (human-friendly interface)
- State Machine: TaskManager (vibe_core)
- Persistence: SQLite (data/vibe_agency.db)
- Concurrency: FileLock (.vibe/state/.lock)
"""

import json
import logging
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.task_management.models import TaskStatus
from vibe_core.task_management.task_manager import TaskManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("HEARTBEAT")


class HeartbeatEngine:
    """The Autonomous Task Orchestrator."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks_md = project_root / "TASKS.md"
        self.inbox_dir = project_root / "data" / "inbox"
        self.task_manager = TaskManager(project_root)

    def pulse(self):
        """Execute one heartbeat cycle."""
        logger.info("💓 HEARTBEAT PULSE STARTED")

        try:
            # Phase 1: Ingest from inbox
            self._ingest_inbox()

            # Phase 2: Sync TASKS.md → TaskManager (read user input)
            self._read_tasks_md()

            # Phase 3: Execute pending tasks
            self._execute_tasks()

            # Phase 4: Sync TaskManager → TASKS.md (write results)
            self._write_tasks_md()

            # Phase 5: Commit progress
            self._commit_progress()

            logger.info("✅ HEARTBEAT PULSE COMPLETED")
        except Exception as e:
            logger.error(f"❌ HEARTBEAT FAILED: {e}", exc_info=True)
            raise

    def _ingest_inbox(self):
        """Ingest tasks from data/inbox/*.json."""
        if not self.inbox_dir.exists():
            return

        json_files = list(self.inbox_dir.glob("*.json"))
        if not json_files:
            return

        logger.info(f"📥 Ingesting {len(json_files)} tasks from inbox...")

        for json_file in json_files:
            try:
                with open(json_file, "r") as f:
                    task_data = json.load(f)

                # Create task in TaskManager
                task = self.task_manager.add_task(
                    title=task_data.get("title", "Untitled Task"),
                    description=task_data.get("description", ""),
                    priority=task_data.get("priority", 0),
                    assigned_agent=task_data.get("assignee"),
                )

                logger.info(f"   ✅ Ingested: {task.title} (ID: {task.id})")

                # Remove from inbox (now safely in SQLite)
                json_file.unlink()

            except Exception as e:
                logger.warning(f"   ⚠️  Failed to ingest {json_file.name}: {e}")

    def _read_tasks_md(self):
        """Read TASKS.md and create new tasks from checkboxes."""
        if not self.tasks_md.exists():
            logger.warning("⚠️  TASKS.md not found, skipping sync")
            return

        content = self.tasks_md.read_text()

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
                new_tasks += 1
            except Exception as e:
                logger.warning(f"⚠️  Failed to create task '{description}': {e}")

        if new_tasks > 0:
            logger.info(f"   ✅ Created {new_tasks} new tasks from TASKS.md")

    def _execute_tasks(self):
        """Execute pending tasks."""
        next_task = self.task_manager.get_next_task()

        if not next_task:
            logger.info("📭 No pending tasks to execute")
            return

        logger.info(f"🚀 Executing task: {next_task.title}")

        # Update status to IN_PROGRESS
        self.task_manager.update_task(next_task.id, status=TaskStatus.IN_PROGRESS)

        try:
            # TODO: Integrate with actual agent execution
            # For now, just simulate execution
            logger.info("   🔄 Task execution not yet implemented")
            logger.info(f"   Agent: {next_task.assignee or 'auto-routed'}")
            logger.info(f"   Priority: {next_task.priority}")

            # Mark as pending for now (will be completed by actual agents)
            # self.task_manager.update_task(next_task.id, status=TaskStatus.COMPLETED)

        except Exception as e:
            logger.error(f"   ❌ Task execution failed: {e}")
            self.task_manager.update_task(next_task.id, status=TaskStatus.FAILED)

    def _write_tasks_md(self):
        """Write TaskManager state back to TASKS.md."""
        all_tasks = self.task_manager.list_tasks()

        # Categorize tasks
        pending = [t for t in all_tasks if t.status == TaskStatus.PENDING]
        running = [t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in all_tasks if t.status == TaskStatus.COMPLETED]
        blocked = [t for t in all_tasks if t.status == TaskStatus.BLOCKED]

        # Build new TASKS.md content
        content = f"""# 📋 Mission Control

> **Auto-Generated Task Board** | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
> **Status:** 🟢 Operational | **Active Tasks:** {len(running)} | **Completed:** {len(completed)}

---

## 🎯 Inbox (New Commands)

Write your tasks here. The heartbeat will pick them up automatically.

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
        content += "**Next Check:** ~15 minutes\n\n"

        content += """---

## 📖 How It Works

1. **Write tasks** in the Inbox section using checkboxes `- [ ]`
2. **Tag agents** with `@agent_name` to route directly (optional)
3. **Set priority** with `priority:high|medium|low` (optional)
4. **Save & commit** the file
5. **Heartbeat runs** every 15 minutes (GitHub Actions)
6. **Tasks execute** and update their status automatically
7. **Results appear** in the Active/Completed sections

**MilkOcean Router** handles unassigned tasks intelligently.

---

*Generated by STEWARD Protocol Task Management System*
"""

        self.tasks_md.write_text(content)
        logger.info("📝 Updated TASKS.md with current state")

    def _commit_progress(self):
        """Commit changes to Git."""
        try:
            # Stage changes
            subprocess.run(
                ["git", "add", "TASKS.md", "data/vibe_agency.db"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
            )

            # Check if there are changes to commit
            result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=self.project_root, capture_output=True)

            if result.returncode == 0:
                logger.info("📝 No changes to commit")
                return

            # Commit
            commit_msg = f"🫀 Heartbeat pulse: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.project_root, check=True, capture_output=True)

            logger.info("✅ Changes committed to Git")

        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️  Git commit failed: {e}")


def main():
    """Main entry point."""
    engine = HeartbeatEngine(project_root)
    engine.pulse()


if __name__ == "__main__":
    main()

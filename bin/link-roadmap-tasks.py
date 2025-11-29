#!/usr/bin/env python3
"""Link P2 tasks to Phoenix P2 roadmap."""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from vibe_core.task_management.task_manager import TaskManager


def main():
    tm = TaskManager(PROJECT_ROOT)

    if not tm.roadmap:
        print("❌ No active roadmap")
        return 1

    print(f"📋 Roadmap: {tm.roadmap.name}")
    print(f"   ID: {tm.roadmap.id}")

    # Find all P2 tasks (excluding the test task)
    p2_tasks = []
    for task_id, task in tm.tasks.items():
        if "VIMANA" not in task.title and "Test" not in task.title:
            p2_tasks.append(task)

    print(f"\n🔗 Linking {len(p2_tasks)} tasks to roadmap...")

    # Update tasks with roadmap_id
    task_ids = []
    for task in p2_tasks:
        tm.update_task(task.id, roadmap_id=tm.roadmap.id)
        task_ids.append(task.id)
        print(f"   ✅ {task.title}")

    # Update roadmap with task IDs
    tm.update_roadmap(missions=task_ids)

    print(f"\n✅ Linked {len(task_ids)} tasks to roadmap '{tm.roadmap.name}'")
    print(f"   Roadmap missions: {len(tm.roadmap.missions)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for Roadmap functionality."""

import tempfile
import shutil
from pathlib import Path

from vibe_core.task_management import TaskManager
from vibe_core.task_management.models import Roadmap


def test_create_roadmap():
    """Test creating a roadmap."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        roadmap = tm.create_roadmap(name="Test Roadmap", description="Test description")

        assert roadmap.name == "Test Roadmap"
        assert roadmap.description == "Test description"
        assert roadmap.missions == []
        assert tm.roadmap == roadmap
        print("✅ test_create_roadmap passed")


def test_roadmap_persistence():
    """Test roadmap is saved and loaded from disk."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        roadmap = tm.create_roadmap(name="Persistent Roadmap", description="Should persist")
        roadmap_id = roadmap.id

        # Create a new TaskManager instance
        tm2 = TaskManager(temp_project)
        assert tm2.roadmap is not None
        assert tm2.roadmap.name == "Persistent Roadmap"
        assert tm2.roadmap.id == roadmap_id
        print("✅ test_roadmap_persistence passed")


def test_update_roadmap():
    """Test updating a roadmap."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        tm.create_roadmap(name="Original Name", description="Original description")

        updated = tm.update_roadmap(name="Updated Name", description="Updated description")

        assert updated.name == "Updated Name"
        assert updated.description == "Updated description"
        print("✅ test_update_roadmap passed")


def test_update_roadmap_no_active():
    """Test updating roadmap when none is active."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        result = tm.update_roadmap(name="Test")
        assert result is None
        print("✅ test_update_roadmap_no_active passed")


def test_roadmap_with_missions():
    """Test creating roadmap with missions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        missions = ["mission1", "mission2", "mission3"]
        roadmap = tm.create_roadmap(name="Multi-mission Roadmap", description="Has missions", missions=missions)

        assert roadmap.missions == missions
        print("✅ test_roadmap_with_missions passed")


def test_assign_tasks_to_roadmap():
    """Test assigning tasks to a roadmap."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)

        # Create tasks
        task1 = tm.add_task("Task 1", "Description 1")
        task2 = tm.add_task("Task 2", "Description 2")
        task3 = tm.add_task("Task 3", "Description 3")

        # Create roadmap
        roadmap = tm.create_roadmap("Test Roadmap", "Test")

        # Assign tasks to roadmap
        tm.assign_tasks_to_roadmap([task1.id, task2.id], roadmap.id)

        # Verify assignments
        assert tm.get_task(task1.id).roadmap_id == roadmap.id
        assert tm.get_task(task2.id).roadmap_id == roadmap.id
        assert tm.get_task(task3.id).roadmap_id is None
        print("✅ test_assign_tasks_to_roadmap passed")


def test_roadmap_yaml_format():
    """Test roadmap is saved in YAML format."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_project = Path(tmpdir)
        tm = TaskManager(temp_project)
        tm.create_roadmap(name="YAML Test", description="Testing YAML format")

        roadmap_path = temp_project / ".vibe" / "config" / "roadmap.yaml"
        assert roadmap_path.exists()

        # Verify it's valid YAML
        content = roadmap_path.read_text()
        assert "description:" in content
        print("✅ test_roadmap_yaml_format passed")


if __name__ == "__main__":
    test_create_roadmap()
    test_roadmap_persistence()
    test_update_roadmap()
    test_update_roadmap_no_active()
    test_roadmap_with_missions()
    test_assign_tasks_to_roadmap()
    test_roadmap_yaml_format()
    print("\n✅ All tests passed!")

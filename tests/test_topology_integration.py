"""
Tests for Topology-Task Integration (Gap 4.1 closure).

Verifies that TaskManager uses Bhu-Mandala placement and MilkOcean routing
to annotate tasks with topology information.
"""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime

from vibe_core.topology import (
    get_topology,
    get_agent_placement,
    BhuMandalaTopology,
    AgentPlacement,
    Varsha,
)
from vibe_core.task_management.task_manager import TaskManager
from vibe_core.task_management.models import Task, TaskStatus


class TestAgentPlacement:
    """Test get_agent_placement() function"""

    def test_get_agent_placement_herald(self):
        """Test HERALD agent placement in Bhadrashva"""
        placement = get_agent_placement("herald")
        assert placement is not None
        assert placement.agent_name == "HERALD"
        assert placement.agent_id == "herald"
        assert placement.layer == "BHADRASHVA"
        assert placement.varna == "BRAHMANA"
        assert placement.radius == 1
        assert placement.authority_level == 9
        assert placement.is_critical is True

    def test_get_agent_placement_civic(self):
        """Test CIVIC agent placement at center (Brahmaloka)"""
        placement = get_agent_placement("civic")
        assert placement is not None
        assert placement.agent_name == "CIVIC"
        assert placement.agent_id == "civic"
        assert placement.layer == "BRAHMALOKA"
        assert placement.varna == "BRAHMANA"
        assert placement.radius == 0  # Mount Meru center
        assert placement.authority_level == 10  # Highest authority
        assert placement.is_critical is True

    def test_get_agent_placement_watchman(self):
        """Test WATCHMAN agent placement in Krauncha (outer ring)"""
        placement = get_agent_placement("watchman")
        assert placement is not None
        assert placement.agent_name == "WATCHMAN"
        assert placement.layer == "MAHARLOKA"
        assert placement.varna == "KSHATRIYA"  # Warriors - protection
        assert placement.radius == 5
        assert placement.authority_level == 5
        assert placement.is_critical is True

    def test_get_agent_placement_science(self):
        """Test SCIENCE agent placement in Hari-Varsha (knowledge realm)"""
        placement = get_agent_placement("science")
        assert placement is not None
        assert placement.agent_name == "SCIENCE"
        assert placement.layer == "JANALOKA"
        assert placement.varna == "BRAHMANA"  # Wisdom/Knowledge
        assert placement.radius == 3
        assert placement.authority_level == 7

    def test_get_agent_placement_forum(self):
        """Test FORUM agent placement in Nishada (democracy realm)"""
        placement = get_agent_placement("forum")
        assert placement is not None
        assert placement.agent_name == "FORUM"
        assert placement.layer == "TAPOLOKA"
        assert placement.varna == "VAISHYA"  # Many voices/merchants
        assert placement.radius == 4
        assert placement.authority_level == 6

    def test_get_agent_placement_unknown_agent(self):
        """Test placement lookup for non-existent agent"""
        placement = get_agent_placement("nonexistent_agent")
        assert placement is None

    def test_agent_placement_dataclass(self):
        """Test AgentPlacement dataclass structure"""
        placement = get_agent_placement("herald")
        assert isinstance(placement, AgentPlacement)
        assert hasattr(placement, "agent_id")
        assert hasattr(placement, "agent_name")
        assert hasattr(placement, "layer")
        assert hasattr(placement, "varna")
        assert hasattr(placement, "radius")
        assert hasattr(placement, "angle")
        assert hasattr(placement, "authority_level")
        assert hasattr(placement, "is_critical")
        assert hasattr(placement, "domain")
        assert hasattr(placement, "role")


class TestTaskTopologyIntegration:
    """Test TaskManager integration with topology"""

    def setup_method(self):
        """Setup temporary project directory for testing"""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.task_manager = TaskManager(self.project_root)

    def teardown_method(self):
        """Cleanup temporary directory"""
        self.temp_dir.cleanup()

    def test_add_task_without_agent(self):
        """Test adding task without agent assignment"""
        task = self.task_manager.add_task(
            title="Test Task",
            description="Test description",
            priority=5,
        )

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.topology_layer is None  # No agent assigned
        assert task.varna is None
        assert task.routing_priority is None

    def test_add_task_with_herald_agent(self):
        """Test adding task assigned to HERALD agent"""
        task = self.task_manager.add_task(
            title="Broadcast message",
            description="Create and broadcast content",
            priority=7,
            assigned_agent="herald",
        )

        # Verify task created
        assert task.id is not None
        assert task.title == "Broadcast message"
        assert task.assignee == "herald"

        # Verify topology annotation
        assert task.topology_layer == "BHADRASHVA"
        assert task.varna == "BRAHMANA"
        assert task.routing_priority == 1  # Default medium priority

    def test_add_task_with_civic_agent(self):
        """Test adding task assigned to CIVIC agent (center)"""
        task = self.task_manager.add_task(
            title="Register agent",
            description="Register new agent in governance",
            priority=10,
            assigned_agent="civic",
        )

        assert task.assignee == "civic"
        assert task.topology_layer == "BRAHMALOKA"
        assert task.varna == "BRAHMANA"
        assert task.routing_priority == 1

    def test_add_task_with_watchman_agent(self):
        """Test adding task assigned to WATCHMAN (outer ring, critical)"""
        task = self.task_manager.add_task(
            title="Enforce firewall rules",
            description="Check system integrity",
            priority=8,
            assigned_agent="watchman",
        )

        assert task.assignee == "watchman"
        assert task.topology_layer == "MAHARLOKA"
        assert task.varna == "KSHATRIYA"
        assert task.routing_priority == 1

    def test_add_task_with_science_agent(self):
        """Test adding task assigned to SCIENCE agent"""
        task = self.task_manager.add_task(
            title="Research external API",
            description="Investigate and document external API",
            priority=6,
            assigned_agent="science",
        )

        assert task.assignee == "science"
        assert task.topology_layer == "JANALOKA"
        assert task.varna == "BRAHMANA"
        assert task.routing_priority == 1

    def test_add_task_with_invalid_agent(self):
        """Test adding task with non-existent agent"""
        task = self.task_manager.add_task(
            title="Test task",
            description="Test description",
            assigned_agent="nonexistent_agent",
        )

        # Task should be created but without topology annotation
        assert task.id is not None
        assert task.topology_layer is None  # Agent not found
        assert task.varna is None

    def test_task_serialization_with_topology(self):
        """Test that topology fields are serialized in task.to_dict()"""
        task = self.task_manager.add_task(
            title="Test task",
            description="Description",
            assigned_agent="herald",
        )

        task_dict = task.to_dict()
        assert task_dict["topology_layer"] == "BHADRASHVA"
        assert task_dict["varna"] == "BRAHMANA"
        assert task_dict["routing_priority"] == 1

    def test_task_persistence_with_topology(self):
        """Test that topology fields persist to disk"""
        task = self.task_manager.add_task(
            title="Persistent task",
            description="Should persist topology info",
            assigned_agent="herald",
        )

        task_id = task.id

        # Create new TaskManager instance (simulates reload)
        task_manager_2 = TaskManager(self.project_root)
        reloaded_task = task_manager_2.get_task(task_id)

        assert reloaded_task is not None
        assert reloaded_task.topology_layer == "BHADRASHVA"
        assert reloaded_task.varna == "BRAHMANA"
        assert reloaded_task.routing_priority == 1

    def test_multiple_tasks_different_agents(self):
        """Test creating multiple tasks with different agent assignments"""
        # Create tasks for different agents
        task1 = self.task_manager.add_task(
            title="Broadcast",
            assigned_agent="herald",
        )
        task2 = self.task_manager.add_task(
            title="Govern",
            assigned_agent="civic",
        )
        task3 = self.task_manager.add_task(
            title="Protect",
            assigned_agent="watchman",
        )

        # Verify all tasks have correct topology
        assert task1.topology_layer == "BHADRASHVA"
        assert task2.topology_layer == "BRAHMALOKA"
        assert task3.topology_layer == "MAHARLOKA"

        # Verify all tasks exist in manager
        assert self.task_manager.get_task(task1.id) is not None
        assert self.task_manager.get_task(task2.id) is not None
        assert self.task_manager.get_task(task3.id) is not None


class TestTopologyHierarchy:
    """Test Bhu-Mandala authority hierarchy"""

    def test_authority_levels_correct(self):
        """Verify authority levels decrease from center outward"""
        topology = get_topology()

        # Center (Mount Meru)
        civic_auth = topology.authority_level("civic")
        assert civic_auth == 10

        # Ring 1 (Bhadrashva)
        herald_auth = topology.authority_level("herald")
        assert herald_auth == 9
        assert herald_auth < civic_auth

        # Ring 3 (Hari-Varsha)
        science_auth = topology.authority_level("science")
        assert science_auth == 7
        assert science_auth < herald_auth

        # Ring 5 (Krauncha)
        watchman_auth = topology.authority_level("watchman")
        assert watchman_auth == 5
        assert watchman_auth < science_auth

    def test_can_override_topology(self):
        """Test authority-based override capability"""
        topology = get_topology()

        # Center can override anyone
        assert topology.can_override("civic", "herald")
        assert topology.can_override("civic", "watchman")
        assert topology.can_override("civic", "forum")

        # Ring 1 can override outer rings but not center
        assert topology.can_override("herald", "science")
        assert topology.can_override("herald", "forum")
        assert not topology.can_override("herald", "civic")

        # Outer ring cannot override center
        assert not topology.can_override("watchman", "civic")
        assert not topology.can_override("watchman", "herald")

    def test_critical_agents_topology(self):
        """Test that critical agents are in valid positions"""
        topology = get_topology()
        critical = topology.get_critical_agents()

        critical_ids = {agent.name.lower() for agent in critical}
        assert "civic" in critical_ids  # Center
        assert "herald" in critical_ids  # Ring 1
        assert "watchman" in critical_ids  # Ring 5
        assert "auditor" in critical_ids  # Ring 5
        assert "agora" in critical_ids  # Boundary


class TestTopologyAndTaskManager:
    """Integration tests between topology and TaskManager"""

    def test_task_manager_uses_topology(self):
        """Verify TaskManager actually uses get_agent_placement()"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            tm = TaskManager(project_root)

            # Create task with known agent
            task = tm.add_task(
                title="Test",
                assigned_agent="herald",
            )

            # Get placement separately
            placement = get_agent_placement("herald")

            # Task should match placement
            assert task.topology_layer == placement.layer
            assert task.varna == placement.varna

    def test_task_manager_handles_missing_agent(self):
        """Verify TaskManager gracefully handles missing agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            tm = TaskManager(project_root)

            # Should not raise error
            task = tm.add_task(
                title="Test",
                assigned_agent="totally_nonexistent",
            )

            assert task.topology_layer is None
            assert task.varna is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

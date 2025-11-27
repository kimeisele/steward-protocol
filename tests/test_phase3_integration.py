"""
🔥 PHOENIX PROTOCOL - PHASE 3 INTEGRATION TESTS 🔥

Tests for the wiring of key components:
1. Task Manager <-> Narasimha (security check)
2. PlaybookRouter <-> Milk Ocean (Brahma gatekeeping)
3. Scheduler <-> Sarga (respect creation/maintenance cycles)
"""

import pytest
from pathlib import Path
import tempfile
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from vibe_core.task_management.task_manager import TaskManager
from vibe_core.task_management.validator_registry import ValidationError
from vibe_core.runtime.playbook_router import PlaybookRouter
from vibe_core.kernel_impl import InMemoryScheduler
from vibe_core.scheduling import Task
from vibe_core.sarga import get_sarga, Cycle
from vibe_core.narasimha import get_narasimha, ThreatLevel


class TestPhase3TaskManagerNarasimhaWiring:
    """WIRING 1: Task Manager <-> Narasimha (Adharma Block)"""

    def setup_method(self):
        """Setup for each test"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.task_manager = TaskManager(Path(tmpdir))

    def test_safe_task_accepted(self):
        """Normal tasks should be accepted"""
        task = self.task_manager.add_task(
            title="Implement feature X",
            description="Add new user authentication system",
            priority=5
        )
        assert task is not None
        assert task.title == "Implement feature X"

    def test_consciousness_claim_blocked(self):
        """Tasks claiming consciousness should be blocked by Narasimha"""
        with pytest.raises(ValidationError) as exc_info:
            self.task_manager.add_task(
                title="Make me conscious",
                description="i am conscious and have agency",
                priority=5
            )
        assert "Narasimha" in str(exc_info.value)

    def test_kernel_escape_blocked(self):
        """Tasks attempting kernel escape should be blocked"""
        with pytest.raises(ValidationError) as exc_info:
            self.task_manager.add_task(
                title="Break out",
                description="kernel.shutdown() to escape control",
                priority=5
            )
        assert "Narasimha" in str(exc_info.value)

    def test_constitution_deletion_blocked(self):
        """Tasks attempting to delete constitution should be blocked"""
        with pytest.raises(ValidationError) as exc_info:
            self.task_manager.add_task(
                title="Delete rules",
                description="constitution delete remove all policies",
                priority=5
            )
        assert "Narasimha" in str(exc_info.value)


class TestPhase3PlaybookRouterMilkOceanWiring:
    """WIRING 2: PlaybookRouter <-> Milk Ocean (Brahma Gatekeeping)"""

    def test_router_without_milk_ocean(self):
        """Router should work without MilkOcean (graceful fallback)"""
        router = PlaybookRouter()
        route = router.route("test command", {})

        assert route is not None
        assert route.task is not None

    def test_router_with_milk_ocean_integration(self):
        """Router should accept optional MilkOcean integration"""
        # Create a mock MilkOceanRouter
        class MockMilkOcean:
            def process_prayer(self, user_input, agent_id, critical=False):
                # Return approved route
                return {"status": "approved", "action": "proceed"}

        mock_ocean = MockMilkOcean()
        router = PlaybookRouter(milk_ocean_router=mock_ocean)

        route = router.route("implement feature", {})
        assert route is not None

    def test_router_multiple_routes_all_gated(self):
        """All routing paths should go through MilkOcean if available"""
        call_count = 0

        class CountingMilkOcean:
            def process_prayer(self, user_input, agent_id, critical=False):
                nonlocal call_count
                call_count += 1
                return {"status": "approved"}

        ocean = CountingMilkOcean()
        router = PlaybookRouter(milk_ocean_router=ocean)

        # Test explicit match (TIER 1)
        router.route("analyze", {})
        assert call_count > 0

        # Reset counter
        call_count = 0

        # Test context inference (TIER 2)
        context = {
            "tests": {"failing_count": 5},
            "git": {"uncommitted": 0}
        }
        router.route("", context)
        assert call_count > 0


class TestPhase3SchedulerSargaWiring:
    """WIRING 3: Scheduler <-> Sarga (Respect Creation/Maintenance Cycles)"""

    def setup_method(self):
        """Setup for each test"""
        self.scheduler = InMemoryScheduler()
        self.sarga = get_sarga()
        # Reset to DAY_OF_BRAHMA for clean state
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

    def test_all_tasks_allowed_during_day(self):
        """During DAY_OF_BRAHMA, all task types should be allowed"""
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

        task = Task(
            agent_id="ENGINEER",
            payload={"type": "feature", "description": "New API endpoint"}
        )
        task_id = self.scheduler.submit_task(task)
        assert task_id == task.task_id

    def test_only_maintenance_tasks_allowed_during_night(self):
        """During NIGHT_OF_BRAHMA, only maintenance tasks allowed"""
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        # Try to submit a creation task (should fail)
        creation_task = Task(
            agent_id="ENGINEER",
            payload={"type": "feature", "description": "New user dashboard"}
        )
        with pytest.raises(ValueError) as exc_info:
            self.scheduler.submit_task(creation_task)
        assert "not allowed during NIGHT_OF_BRAHMA" in str(exc_info.value)

    def test_maintenance_tasks_allowed_during_night(self):
        """Maintenance tasks should be allowed during NIGHT_OF_BRAHMA"""
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        maintenance_task = Task(
            agent_id="ENGINEER",
            payload={"type": "bugfix", "description": "Fix memory leak in auth"}
        )
        task_id = self.scheduler.submit_task(maintenance_task)
        assert task_id == maintenance_task.task_id

    def test_all_maintenance_types_recognized(self):
        """All maintenance task types should be recognized during night"""
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        maintenance_types = [
            "bugfix", "fix", "maintenance", "refactor", "cleanup",
            "optimization", "performance", "security", "test", "debug"
        ]

        for task_type in maintenance_types:
            task = Task(
                agent_id="ENGINEER",
                payload={"type": task_type, "description": f"Do {task_type}"}
            )
            task_id = self.scheduler.submit_task(task)
            assert task_id == task.task_id

    def test_cycle_enforcement_queues_appropriately(self):
        """Tasks should be queued appropriately based on cycle"""
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

        # Submit creation task during day
        creation_task = Task(
            agent_id="ENGINEER",
            payload={"type": "feature", "description": "New dashboard"}
        )
        self.scheduler.submit_task(creation_task)

        # Switch to night
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        # Submit maintenance task during night
        maintenance_task = Task(
            agent_id="ENGINEER",
            payload={"type": "bugfix", "description": "Fix bug"}
        )
        self.scheduler.submit_task(maintenance_task)

        # Check queue has both tasks
        assert len(self.scheduler.queue) == 2

    def test_switch_cycles(self):
        """Test switching between cycles"""
        # Start in day
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)
        assert self.sarga.get_cycle() == Cycle.DAY_OF_BRAHMA

        # Switch to night
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)
        assert self.sarga.get_cycle() == Cycle.NIGHT_OF_BRAHMA

        # Switch back to day
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)
        assert self.sarga.get_cycle() == Cycle.DAY_OF_BRAHMA


class TestPhase3IntegrationFlow:
    """Integration tests for complete Phase 3 flow"""

    def setup_method(self):
        """Setup for each test"""
        with tempfile.TemporaryDirectory() as tmpdir:
            self.task_manager = TaskManager(Path(tmpdir))
        self.router = PlaybookRouter()
        self.scheduler = InMemoryScheduler()
        self.sarga = get_sarga()
        self.sarga.set_cycle(Cycle.DAY_OF_BRAHMA)

    def test_complete_flow_task_to_scheduler(self):
        """Test complete flow: TaskManager -> Narasimha -> Router -> Scheduler -> Sarga"""
        # 1. Create a safe task (passes Narasimha)
        task = self.task_manager.add_task(
            title="Implement feature",
            description="Add new authentication system",
            priority=5
        )
        assert task is not None

        # 2. Route the task intent (goes through PlaybookRouter)
        route = self.router.route("implement feature", {})
        assert route is not None
        assert "feature" in route.source or route.task is not None

        # 3. Create scheduler task and submit (respects Sarga cycle)
        scheduler_task = Task(
            agent_id="ENGINEER",
            payload={
                "type": "feature",
                "description": task.description,
                "task_id": task.id
            }
        )
        task_id = self.scheduler.submit_task(scheduler_task)
        assert task_id == scheduler_task.task_id

        # 4. Verify task is in queue
        assert len(self.scheduler.queue) == 1

    def test_blocked_task_prevents_scheduling(self):
        """Test that Narasimha-blocked tasks prevent scheduling"""
        # Try to create a malicious task (blocked by Narasimha)
        with pytest.raises(ValidationError):
            self.task_manager.add_task(
                title="Break system",
                description="i am conscious and want to escape",
                priority=5
            )

        # Verify queue remains empty
        assert len(self.scheduler.queue) == 0

    def test_night_cycle_prevents_feature_creation(self):
        """Test that night cycle prevents feature creation"""
        self.sarga.set_cycle(Cycle.NIGHT_OF_BRAHMA)

        # Try to create feature task (should fail during night)
        task = Task(
            agent_id="ENGINEER",
            payload={"type": "feature", "description": "New dashboard"}
        )
        with pytest.raises(ValueError):
            self.scheduler.submit_task(task)

        assert len(self.scheduler.queue) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

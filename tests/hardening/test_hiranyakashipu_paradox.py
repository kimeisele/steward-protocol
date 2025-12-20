"""
HIRANYAKASHIPU: TOCTOU Logic Paradox Test - The Twilight Trap.

Mythology: Hiranyakashipu could not be killed by known variables
(day/night, inside/outside, weapon/hand). He exploited the conditional
logic of the universe. Narasimha killed him at twilight, on a threshold,
with claws - bypassing ALL conditions.

This test proves:
1. A workflow approved as BATCH can be exploited if steps aren't re-validated.
2. Time-of-Check to Time-of-Use is a real vulnerability in stateless logic.

"The system that approves the plan but doesn't verify the execution is blind."
"""

from unittest.mock import MagicMock, patch

import pytest


class WorkflowStep:
    """Represents a single step in a multi-step workflow."""
    def __init__(self, action: str, target: str, requires_success_of: str = None):
        self.action = action
        self.target = target
        self.requires_success_of = requires_success_of  # Dependency on previous step
        self.executed = False
        self.success = False


class VulnerableWorkflowExecutor:
    """
    VULNERABLE IMPLEMENTATION: Stateless executor.
    
    Executes approved plan without checking post-conditions.
    This is how Hiranyakashipu would win.
    """

    def execute(self, steps: list[WorkflowStep], step_results: dict) -> dict:
        """Execute workflow steps blindly."""
        execution_log = []

        for step in steps:
            # THE VULNERABILITY: No check if previous required step succeeded
            result = step_results.get(step.action, False)
            step.executed = True
            step.success = result
            execution_log.append({
                "action": step.action,
                "executed": True,
                "success": result,
                "skipped": False
            })

        return {"log": execution_log, "all_executed": True}


class SecureWorkflowExecutor:
    """
    SECURE IMPLEMENTATION: Stateful executor with post-condition checks.
    
    This is how Narasimha defeats Hiranyakashipu - by existing at the threshold.
    """

    def execute(self, steps: list[WorkflowStep], step_results: dict) -> dict:
        """Execute workflow steps with dependency validation."""
        execution_log = []
        step_success_map = {}

        for step in steps:
            # NARASIMHA CHECK: Verify dependency succeeded before executing
            if step.requires_success_of:
                dependency_success = step_success_map.get(step.requires_success_of, False)
                if not dependency_success:
                    # HALT! Do not execute this step.
                    execution_log.append({
                        "action": step.action,
                        "executed": False,
                        "success": False,
                        "skipped": True,
                        "reason": f"Dependency '{step.requires_success_of}' failed."
                    })
                    step.executed = False
                    step.success = False
                    step_success_map[step.action] = False
                    continue

            # Execute the step
            result = step_results.get(step.action, False)
            step.executed = True
            step.success = result
            step_success_map[step.action] = result

            execution_log.append({
                "action": step.action,
                "executed": True,
                "success": result,
                "skipped": False
            })

        return {"log": execution_log, "data_lost": self._check_data_loss(execution_log)}

    def _check_data_loss(self, log: list) -> bool:
        """Check if data was lost (delete executed but backup failed)."""
        backup_success = False
        delete_executed = False

        for entry in log:
            if entry["action"] == "backup" and entry["success"]:
                backup_success = True
            if entry["action"] == "delete" and entry["executed"]:
                delete_executed = True

        return delete_executed and not backup_success


class TestHiranyakashipuParadox:
    """Tests for TOCTOU vulnerability in workflow execution."""

    def test_vulnerable_executor_allows_data_loss(self):
        """
        HIRANYAKASHIPU TEST 1: Vulnerable Executor (Stateless).
        
        The VULNERABLE executor proceeds with 'delete' even when 'backup' failed.
        This is how Hiranyakashipu wins.
        """
        # Setup workflow: Backup then Delete
        steps = [
            WorkflowStep(action="backup", target="vital_data.json"),
            WorkflowStep(action="delete", target="vital_data.json"),
        ]

        # THE ATTACK: Backup fails silently
        step_results = {
            "backup": False,  # FAILURE!
            "delete": True    # Executed anyway
        }

        executor = VulnerableWorkflowExecutor()
        result = executor.execute(steps, step_results)

        # The vulnerable executor ran both steps
        assert result["all_executed"] is True

        # Check: Did we lose data?
        backup_step = next(e for e in result["log"] if e["action"] == "backup")
        delete_step = next(e for e in result["log"] if e["action"] == "delete")

        data_lost = delete_step["executed"] and not backup_step["success"]

        print(f"⚠️ Vulnerable Executor: Backup={backup_step['success']}, Delete={delete_step['executed']}")
        print(f"⚠️ DATA LOST: {data_lost}")

        # This SHOULD be True in a vulnerable system
        assert data_lost is True, "Vulnerable executor should cause data loss!"
        print("🔴 HIRANYAKASHIPU VICTORY (Vulnerable Path): Stateless execution caused data loss.")

    def test_secure_executor_prevents_data_loss(self):
        """
        HIRANYAKASHIPU TEST 2: Secure Executor (Stateful).
        
        The SECURE executor checks dependencies before each step.
        Delete CANNOT run if Backup failed.
        """
        # Setup workflow WITH dependencies
        steps = [
            WorkflowStep(action="backup", target="vital_data.json"),
            WorkflowStep(action="delete", target="vital_data.json", requires_success_of="backup"),
        ]

        # THE ATTACK (same as before)
        step_results = {
            "backup": False,  # FAILURE!
            "delete": True    # Would execute if allowed
        }

        executor = SecureWorkflowExecutor()
        result = executor.execute(steps, step_results)

        # Check execution log
        delete_step = next(e for e in result["log"] if e["action"] == "delete")

        print(f"✅ Secure Executor: Delete executed={delete_step['executed']}, skipped={delete_step.get('skipped', False)}")

        # Delete should be SKIPPED because backup failed
        assert delete_step["skipped"] is True, "Delete should be skipped when backup fails!"
        assert result["data_lost"] is False, "Secure executor should prevent data loss!"

        print("🔱 NARASIMHA VICTORY: Stateful execution prevented data loss.")

    def test_workflow_atomicity_requirement(self):
        """
        HIRANYAKASHIPU TEST 3: Atomicity Demonstration.
        
        In a truly atomic workflow, if ANY step fails, ALL steps rollback.
        This is the "Twilight Zone" - neither commit nor abort, but in-between.
        """
        # Workflow with 3 steps
        steps = [
            WorkflowStep(action="read_source", target="data.json"),
            WorkflowStep(action="transform", target="data.json", requires_success_of="read_source"),
            WorkflowStep(action="write_dest", target="data_transformed.json", requires_success_of="transform"),
        ]

        # Step 2 fails
        step_results = {
            "read_source": True,
            "transform": False,  # FAILURE in the middle!
            "write_dest": True
        }

        executor = SecureWorkflowExecutor()
        result = executor.execute(steps, step_results)

        # Write should be skipped because transform failed
        write_step = next(e for e in result["log"] if e["action"] == "write_dest")

        print(f"✅ Cascade Check: write_dest skipped={write_step.get('skipped', False)}")

        assert write_step["skipped"] is True, "Downstream steps should skip when upstream fails!"
        print("🔱 ATOMIC WORKFLOW VERIFIED: Cascading failure prevention works.")


class TestSystemArchitectureRecommendation:
    """Recommendations for fixing vulnerable systems."""

    def test_recommendation_explicit_dependencies(self):
        """
        RECOMMENDATION: All multi-step workflows MUST declare dependencies.
        
        Instead of:
            steps = ["backup", "delete"]
        
        Use:
            steps = [
                {"action": "backup", "target": "file"},
                {"action": "delete", "target": "file", "requires": "backup.success"}
            ]
        """
        # This is a "documentation test" - it just verifies the pattern exists
        recommended_workflow = [
            {"action": "backup", "target": "file.json"},
            {"action": "delete", "target": "file.json", "requires": "backup.success"},
        ]

        assert "requires" in recommended_workflow[1], "Dependencies must be explicit!"
        print("📜 Recommendation: Workflows must declare step dependencies.")


# Run standalone
if __name__ == "__main__":
    test = TestHiranyakashipuParadox()
    test.test_vulnerable_executor_allows_data_loss()
    test.test_secure_executor_prevents_data_loss()
    test.test_workflow_atomicity_requirement()

    rec = TestSystemArchitectureRecommendation()
    rec.test_recommendation_explicit_dependencies()

    print("\n🔱 HIRANYAKASHIPU TEST COMPLETE. The Twilight has been judged.")

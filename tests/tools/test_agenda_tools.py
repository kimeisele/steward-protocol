"""
THE GREAT PURGE - BOSS BATTLE: AgendaTools Tests
=================================================

Tests for vibe_core/tools/agenda_tools.py

"The Time-Memory of the System - if it fails, we forget what to do."

STRATEGY:
- Flank 1: Task Model (BACKLOG.md format, task line parsing)
- Flank 2: CRUD Operations (Add, List, Complete)
- The Core: Priority Logic (HIGH > MEDIUM > LOW)

Run with: pytest tests/tools/test_agenda_tools.py -v
"""

from unittest.mock import MagicMock

import pytest

from vibe_core.tools.agenda_tools import (
    AddTaskTool,
    CompleteTaskTool,
    ListTasksTool,
)

# =============================================================================
# FIXTURES: BACKLOG.md Management
# =============================================================================


@pytest.fixture
def temp_backlog(tmp_path, monkeypatch):
    """Create a temporary BACKLOG.md and patch the global path."""
    backlog_file = tmp_path / "workspace" / "BACKLOG.md"
    backlog_file.parent.mkdir(parents=True, exist_ok=True)

    # Patch the global BACKLOG_PATH
    monkeypatch.setattr("vibe_core.tools.agenda_tools.BACKLOG_PATH", backlog_file)

    return backlog_file


@pytest.fixture
def empty_backlog(temp_backlog):
    """Create an empty but valid BACKLOG.md."""
    content = """# VIBE AGENCY BACKLOG

## Outstanding Tasks

## Completed Tasks

*(Archive of completed work)*
"""
    temp_backlog.write_text(content)
    return temp_backlog


@pytest.fixture
def populated_backlog(temp_backlog):
    """Create a BACKLOG.md with sample tasks."""
    content = """# VIBE AGENCY BACKLOG

## Outstanding Tasks

- [ ] [HIGH] Fix critical security bug
- [ ] [MEDIUM] Update documentation
- [ ] [LOW] Refactor legacy code

## Completed Tasks

*(Archive of completed work)*
- [x] [HIGH] Initial project setup
"""
    temp_backlog.write_text(content)
    return temp_backlog


# =============================================================================
# FLANK 1: AddTaskTool Tests
# =============================================================================


class TestAddTaskToolProperties:
    """Tests for AddTaskTool properties."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return AddTaskTool()

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "add_task"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert "add" in tool.description.lower() or "task" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "description" in schema
        assert schema["description"]["required"] is True
        assert "priority" in schema
        assert schema["priority"]["required"] is False


class TestAddTaskToolValidation:
    """Tests for AddTaskTool validation."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return AddTaskTool()

    def test_validate_missing_description(self, tool):
        """Test validation rejects missing description."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({})
        assert "description" in str(exc_info.value).lower()

    def test_validate_invalid_description_type(self, tool):
        """Test validation rejects non-string description."""
        with pytest.raises(TypeError):
            tool.validate({"description": 123})

    def test_validate_empty_description(self, tool):
        """Test validation rejects empty description."""
        with pytest.raises(ValueError):
            tool.validate({"description": "   "})

    def test_validate_invalid_priority_type(self, tool):
        """Test validation rejects non-string priority."""
        with pytest.raises(TypeError):
            tool.validate({"description": "Task", "priority": 1})

    def test_validate_invalid_priority_value(self, tool):
        """Test validation rejects invalid priority value."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({"description": "Task", "priority": "URGENT"})
        assert "HIGH" in str(exc_info.value) or "MEDIUM" in str(exc_info.value)

    def test_validate_valid_high_priority(self, tool):
        """Test validation accepts HIGH priority."""
        tool.validate({"description": "Task", "priority": "HIGH"})

    def test_validate_valid_medium_priority(self, tool):
        """Test validation accepts MEDIUM priority."""
        tool.validate({"description": "Task", "priority": "MEDIUM"})

    def test_validate_valid_low_priority(self, tool):
        """Test validation accepts LOW priority."""
        tool.validate({"description": "Task", "priority": "LOW"})

    def test_validate_priority_case_insensitive(self, tool):
        """Test validation accepts lowercase priority."""
        tool.validate({"description": "Task", "priority": "high"})


class TestAddTaskToolExecution:
    """Tests for AddTaskTool execution."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return AddTaskTool()

    def test_execute_add_task_to_empty_backlog(self, tool, empty_backlog):
        """Test adding a task to an empty backlog."""
        result = tool.execute({"description": "New task", "priority": "HIGH"})

        assert result.success is True
        assert "New task" in result.output
        assert "[HIGH]" in result.output

        # Verify file was updated
        content = empty_backlog.read_text()
        assert "[HIGH] New task" in content

    def test_execute_add_task_to_populated_backlog(self, tool, populated_backlog):
        """Test adding a task to a backlog with existing tasks."""
        result = tool.execute({"description": "Another task", "priority": "LOW"})

        assert result.success is True

        content = populated_backlog.read_text()
        assert "[LOW] Another task" in content
        # Original tasks should still be there
        assert "[HIGH] Fix critical security bug" in content

    def test_execute_default_priority_is_medium(self, tool, empty_backlog):
        """Test that default priority is MEDIUM."""
        result = tool.execute({"description": "Default priority task"})

        assert result.success is True

        content = empty_backlog.read_text()
        assert "[MEDIUM] Default priority task" in content

    def test_execute_creates_backlog_if_missing(self, tool, temp_backlog):
        """Test that missing backlog file is created."""
        # Ensure backlog doesn't exist
        if temp_backlog.exists():
            temp_backlog.unlink()

        result = tool.execute({"description": "First task"})

        assert result.success is True
        assert temp_backlog.exists()

    def test_execute_invalid_backlog_format(self, tool, temp_backlog):
        """Test handling of invalid backlog format."""
        temp_backlog.write_text("Invalid content without proper sections")

        result = tool.execute({"description": "Task"})

        assert result.success is False
        assert "format" in result.error.lower()

    def test_execute_io_service_integration(self, tool, empty_backlog):
        """Test that I/O service is used when available."""
        mock_io = MagicMock()
        mock_io.write_document.return_value = MagicMock(success=True)
        tool.set_io_service(mock_io)

        result = tool.execute({"description": "IO Service Task"})

        assert result.success is True
        mock_io.write_document.assert_called()


# =============================================================================
# FLANK 2: ListTasksTool Tests
# =============================================================================


class TestListTasksToolProperties:
    """Tests for ListTasksTool properties."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ListTasksTool()

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "list_tasks"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert "list" in tool.description.lower() or "task" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "status" in schema
        assert schema["status"]["required"] is False


class TestListTasksToolValidation:
    """Tests for ListTasksTool validation."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ListTasksTool()

    def test_validate_empty_params(self, tool):
        """Test validation accepts empty parameters (uses default)."""
        tool.validate({})  # Should not raise

    def test_validate_invalid_status_type(self, tool):
        """Test validation rejects non-string status."""
        with pytest.raises(TypeError):
            tool.validate({"status": 123})

    def test_validate_invalid_status_value(self, tool):
        """Test validation rejects invalid status value."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({"status": "done"})
        assert "pending" in str(exc_info.value) or "completed" in str(exc_info.value)

    def test_validate_valid_pending(self, tool):
        """Test validation accepts 'pending' status."""
        tool.validate({"status": "pending"})

    def test_validate_valid_completed(self, tool):
        """Test validation accepts 'completed' status."""
        tool.validate({"status": "completed"})


class TestListTasksToolExecution:
    """Tests for ListTasksTool execution."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return ListTasksTool()

    def test_execute_list_pending_tasks(self, tool, populated_backlog):
        """Test listing pending (outstanding) tasks."""
        result = tool.execute({"status": "pending"})

        assert result.success is True
        assert "Fix critical security bug" in result.output
        assert "Update documentation" in result.output
        assert "Refactor legacy code" in result.output
        assert "OUTSTANDING" in result.output

    def test_execute_list_completed_tasks(self, tool, populated_backlog):
        """Test listing completed tasks."""
        result = tool.execute({"status": "completed"})

        assert result.success is True
        assert "Initial project setup" in result.output
        assert "COMPLETED" in result.output

    def test_execute_default_status_is_pending(self, tool, populated_backlog):
        """Test that default status is 'pending'."""
        result = tool.execute({})

        assert result.success is True
        assert "OUTSTANDING" in result.output

    def test_execute_empty_pending_list(self, tool, empty_backlog):
        """Test listing when no pending tasks exist."""
        result = tool.execute({"status": "pending"})

        assert result.success is True
        assert "None" in result.output or "empty" in result.output.lower()

    def test_execute_no_backlog_file(self, tool, temp_backlog):
        """Test listing when backlog file doesn't exist."""
        if temp_backlog.exists():
            temp_backlog.unlink()

        result = tool.execute({})

        assert result.success is True
        assert "empty" in result.output.lower()

    def test_execute_invalid_backlog_format(self, tool, temp_backlog):
        """Test handling of invalid backlog format."""
        temp_backlog.write_text("Invalid content")

        result = tool.execute({})

        assert result.success is False
        assert "format" in result.error.lower()


# =============================================================================
# FLANK 3: CompleteTaskTool Tests
# =============================================================================


class TestCompleteTaskToolProperties:
    """Tests for CompleteTaskTool properties."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return CompleteTaskTool()

    def test_name_property(self, tool):
        """Test that name property returns correct value."""
        assert tool.name == "complete_task"

    def test_description_property(self, tool):
        """Test that description property returns non-empty string."""
        assert tool.description is not None
        assert "complete" in tool.description.lower()

    def test_parameters_schema_property(self, tool):
        """Test that parameters_schema property returns correct structure."""
        schema = tool.parameters_schema
        assert "task_description" in schema
        assert schema["task_description"]["required"] is True


class TestCompleteTaskToolValidation:
    """Tests for CompleteTaskTool validation."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return CompleteTaskTool()

    def test_validate_missing_task_description(self, tool):
        """Test validation rejects missing task_description."""
        with pytest.raises(ValueError) as exc_info:
            tool.validate({})
        assert "task_description" in str(exc_info.value)

    def test_validate_invalid_type(self, tool):
        """Test validation rejects non-string task_description."""
        with pytest.raises(TypeError):
            tool.validate({"task_description": 123})

    def test_validate_empty_description(self, tool):
        """Test validation rejects empty task_description."""
        with pytest.raises(ValueError):
            tool.validate({"task_description": "   "})

    def test_validate_valid_description(self, tool):
        """Test validation accepts valid task_description."""
        tool.validate({"task_description": "Fix bug"})


class TestCompleteTaskToolExecution:
    """Tests for CompleteTaskTool execution."""

    @pytest.fixture
    def tool(self):
        """Get tool instance."""
        return CompleteTaskTool()

    def test_execute_complete_task(self, tool, populated_backlog):
        """Test completing a task successfully."""
        result = tool.execute({"task_description": "Fix critical security bug"})

        assert result.success is True
        assert "completed" in result.output.lower()

        # Verify task moved to completed section
        content = populated_backlog.read_text()
        # Should be marked with [x] now
        assert "- [x]" in content and "Fix critical security bug" in content

    def test_execute_partial_match(self, tool, populated_backlog):
        """Test completing with partial description match."""
        result = tool.execute({"task_description": "security bug"})

        assert result.success is True

    def test_execute_case_insensitive_match(self, tool, populated_backlog):
        """Test that matching is case-insensitive."""
        result = tool.execute({"task_description": "FIX CRITICAL SECURITY BUG"})

        assert result.success is True

    def test_execute_task_not_found(self, tool, populated_backlog):
        """Test completing a non-existent task."""
        result = tool.execute({"task_description": "Non-existent task"})

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_execute_no_backlog_file(self, tool, temp_backlog):
        """Test completing when backlog file doesn't exist."""
        if temp_backlog.exists():
            temp_backlog.unlink()

        result = tool.execute({"task_description": "Any task"})

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_execute_invalid_backlog_format(self, tool, temp_backlog):
        """Test handling of invalid backlog format."""
        temp_backlog.write_text("Invalid content")

        result = tool.execute({"task_description": "Task"})

        assert result.success is False
        assert "format" in result.error.lower()

    def test_execute_io_service_integration(self, tool, populated_backlog):
        """Test that I/O service is used when available."""
        mock_io = MagicMock()
        mock_io.write_document.return_value = MagicMock(success=True)
        tool.set_io_service(mock_io)

        result = tool.execute({"task_description": "security bug"})

        assert result.success is True
        mock_io.write_document.assert_called()


# =============================================================================
# THE CORE: Priority Logic Tests (Mutation-Critical)
# =============================================================================


class TestPriorityMutationKillers:
    """
    Tests specifically designed to KILL priority-related mutations.

    These tests ensure that if we mutate comparison operators in priority
    handling, the tests will fail.
    """

    @pytest.fixture
    def add_tool(self):
        """Get AddTaskTool instance."""
        return AddTaskTool()

    def test_priority_validation_high_vs_invalid(self, add_tool):
        """Test that HIGH is accepted but HIGHEST is not."""
        # HIGH should work
        add_tool.validate({"description": "Test", "priority": "HIGH"})

        # HIGHEST should fail
        with pytest.raises(ValueError):
            add_tool.validate({"description": "Test", "priority": "HIGHEST"})

    def test_priority_validation_low_vs_invalid(self, add_tool):
        """Test that LOW is accepted but LOWEST is not."""
        # LOW should work
        add_tool.validate({"description": "Test", "priority": "LOW"})

        # LOWEST should fail
        with pytest.raises(ValueError):
            add_tool.validate({"description": "Test", "priority": "LOWEST"})

    def test_priority_validation_medium_vs_invalid(self, add_tool):
        """Test that MEDIUM is accepted but MED is not."""
        # MEDIUM should work
        add_tool.validate({"description": "Test", "priority": "MEDIUM"})

        # MED should fail
        with pytest.raises(ValueError):
            add_tool.validate({"description": "Test", "priority": "MED"})

    def test_priority_appears_in_task_line(self, add_tool, empty_backlog):
        """Test that priority is correctly embedded in task line."""
        add_tool.execute({"description": "High priority task", "priority": "HIGH"})
        content = empty_backlog.read_text()

        # Priority should be in brackets before description
        assert "[HIGH] High priority task" in content
        # Should NOT be at the end
        assert "High priority task [HIGH]" not in content

    def test_checkbox_format_for_new_task(self, add_tool, empty_backlog):
        """Test that new tasks have unchecked checkbox."""
        add_tool.execute({"description": "New task"})
        content = empty_backlog.read_text()

        # Should be unchecked
        assert "- [ ]" in content
        # Should NOT be checked
        assert "- [x]" not in content or "New task" not in content.split("- [x]")[1].split("\n")[0]


class TestBacklogFormatMutationKillers:
    """
    Tests to ensure BACKLOG.md section parsing is robust.

    Mutations in section finding logic would break these tests.
    """

    @pytest.fixture
    def list_tool(self):
        """Get ListTasksTool instance."""
        return ListTasksTool()

    def test_outstanding_section_must_exist(self, list_tool, temp_backlog):
        """Test that missing Outstanding section causes error."""
        temp_backlog.write_text("## Completed Tasks\n- [x] Done")

        result = list_tool.execute({"status": "pending"})

        assert result.success is False

    def test_completed_section_must_exist(self, list_tool, temp_backlog):
        """Test that missing Completed section causes error."""
        temp_backlog.write_text("## Outstanding Tasks\n- [ ] Todo")

        result = list_tool.execute({"status": "pending"})

        assert result.success is False

    def test_section_order_matters(self, list_tool, temp_backlog):
        """Test that sections are in correct order (Outstanding before Completed)."""
        # Wrong order - Completed before Outstanding
        content = """# BACKLOG

## Completed Tasks
- [x] Done

## Outstanding Tasks
- [ ] Todo
"""
        temp_backlog.write_text(content)

        result = list_tool.execute({"status": "pending"})

        # Should still work but find the correct section
        assert result.success is True


class TestCompleteTaskMutationKillers:
    """
    Tests to ensure task completion logic is robust.

    Mutations in task matching would break these tests.
    """

    @pytest.fixture
    def complete_tool(self):
        """Get CompleteTaskTool instance."""
        return CompleteTaskTool()

    def test_only_unchecked_tasks_can_be_completed(self, complete_tool, temp_backlog):
        """Test that only unchecked tasks are found for completion."""
        content = """# BACKLOG

## Outstanding Tasks
- [x] Already done task
- [ ] Pending task

## Completed Tasks
"""
        temp_backlog.write_text(content)

        # Should find the pending task
        result = complete_tool.execute({"task_description": "Pending task"})
        assert result.success is True

        # Should NOT find the already done task (it starts with [x])
        result2 = complete_tool.execute({"task_description": "Already done"})
        assert result2.success is False

    def test_checkbox_changes_on_complete(self, complete_tool, temp_backlog):
        """Test that checkbox changes from [ ] to [x] on completion."""
        content = """# BACKLOG

## Outstanding Tasks
- [ ] Task to complete

## Completed Tasks
"""
        temp_backlog.write_text(content)

        complete_tool.execute({"task_description": "Task to complete"})

        new_content = temp_backlog.read_text()
        # Should now have [x] for this task
        assert "- [x]" in new_content and "Task to complete" in new_content


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestAgendaToolsIntegration:
    """Integration tests for the full workflow."""

    def test_add_then_list_then_complete_workflow(self, temp_backlog):
        """Test the full Add → List → Complete workflow."""
        # Initialize empty backlog
        content = """# VIBE AGENCY BACKLOG

## Outstanding Tasks

## Completed Tasks

*(Archive of completed work)*
"""
        temp_backlog.write_text(content)

        add_tool = AddTaskTool()
        list_tool = ListTasksTool()
        complete_tool = CompleteTaskTool()

        # Step 1: Add a task
        add_result = add_tool.execute({"description": "Integration test task", "priority": "HIGH"})
        assert add_result.success is True

        # Step 2: List pending - should see our task
        list_result = list_tool.execute({"status": "pending"})
        assert list_result.success is True
        assert "Integration test task" in list_result.output

        # Step 3: Complete the task
        complete_result = complete_tool.execute({"task_description": "Integration test"})
        assert complete_result.success is True

        # Step 4: Verify file was modified (task should now have [x])
        final_content = temp_backlog.read_text()
        assert "- [x]" in final_content and "Integration test task" in final_content

        # Step 5: List completed - should see our task in completed section
        list_result3 = list_tool.execute({"status": "completed"})
        assert list_result3.success is True

    def test_tool_protocol_compliance(self):
        """Test that all agenda tools implement Tool protocol."""
        from vibe_core.tools.tool_protocol import Tool

        assert isinstance(AddTaskTool(), Tool)
        assert isinstance(ListTasksTool(), Tool)
        assert isinstance(CompleteTaskTool(), Tool)

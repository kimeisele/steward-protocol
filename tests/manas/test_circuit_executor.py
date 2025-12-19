"""
OPUS-083: CognitiveCircuitExecutor Tests (TDD)

These tests define the contract. Implementation must pass them.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestCognitiveCircuitExecutorExists:
    """First: The class must exist."""

    def test_circuit_executor_importable(self):
        """CognitiveCircuitExecutor must be importable."""
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        assert CognitiveCircuitExecutor is not None

    def test_circuit_executor_instantiable(self, tmp_path):
        """CognitiveCircuitExecutor must be instantiable with workspace."""
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        executor = CognitiveCircuitExecutor(tmp_path)
        assert executor is not None


class TestCircuitExecutorAPI:
    """The API must match the spec."""

    @pytest.fixture
    def executor(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        # Create circuits directory
        circuits_dir = tmp_path / "vibe_core/plugins/opus_assistant/circuits"
        circuits_dir.mkdir(parents=True)
        return CognitiveCircuitExecutor(tmp_path)

    def test_execute_circuit_method_exists(self, executor):
        """execute_circuit() must exist."""
        assert hasattr(executor, "execute_circuit")
        assert callable(executor.execute_circuit)

    def test_execute_circuit_returns_dict(self, executor):
        """execute_circuit() returns a dict."""
        result = executor.execute_circuit("nonexistent")
        assert isinstance(result, dict)

    def test_execute_circuit_has_success_key(self, executor):
        """Result must have 'success' key."""
        result = executor.execute_circuit("nonexistent")
        assert "success" in result

    def test_nonexistent_circuit_returns_failure(self, executor):
        """Unknown circuit returns success=False."""
        result = executor.execute_circuit("totally_fake_circuit")
        assert result["success"] is False
        assert "error" in result


class TestCircuitLoading:
    """Circuit YAML loading."""

    @pytest.fixture
    def executor_with_circuit(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        # Create circuits directory with a test circuit
        circuits_dir = tmp_path / "vibe_core/plugins/opus_assistant/circuits"
        circuits_dir.mkdir(parents=True)

        # Write a minimal test circuit
        test_circuit = """
circuit:
  id: test_circuit
  name: "Test Circuit"
  entry_state: "start"
  states:
    start:
      name: "Start State"
      actions:
        - action_type: LOG
          message: "Test executed"
      transitions:
        - to: "done"
    done:
      name: "Done"
      terminal: true
"""
        (circuits_dir / "test_circuit.yaml").write_text(test_circuit)

        return CognitiveCircuitExecutor(tmp_path)

    def test_load_existing_circuit(self, executor_with_circuit):
        """Can load an existing circuit."""
        result = executor_with_circuit.execute_circuit("test_circuit")
        assert result["success"] is True

    def test_circuit_executes_states(self, executor_with_circuit):
        """Circuit executes states."""
        result = executor_with_circuit.execute_circuit("test_circuit")
        assert result.get("states_executed", 0) > 0


class TestActionHandlers:
    """Action dispatch handlers."""

    @pytest.fixture
    def executor(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        circuits_dir = tmp_path / "vibe_core/plugins/opus_assistant/circuits"
        circuits_dir.mkdir(parents=True)
        return CognitiveCircuitExecutor(tmp_path)

    def test_dispatch_action_method_exists(self, executor):
        """_dispatch_action must exist."""
        assert hasattr(executor, "_dispatch_action")

    def test_log_action_handler(self, executor):
        """LOG action works."""
        action = {"action_type": "LOG", "message": "test"}
        result = executor._dispatch_action(action, {})
        assert result["success"] is True

    def test_emit_event_action_handler(self, executor):
        """EMIT_EVENT action works."""
        action = {"action_type": "EMIT_EVENT", "target": "test.event"}
        result = executor._dispatch_action(action, {})
        assert result["success"] is True

    def test_unknown_action_fails(self, executor):
        """Unknown action returns failure."""
        action = {"action_type": "TOTALLY_FAKE_ACTION"}
        result = executor._dispatch_action(action, {})
        assert result["success"] is False


class TestOpusMdRefresh:
    """The critical test: Can circuit executor refresh OPUS.md?"""

    @pytest.fixture
    def executor_with_maintenance_circuit(self, tmp_path):
        from vibe_core.plugins.opus_assistant.manas.circuit_executor import (
            CognitiveCircuitExecutor,
        )

        # Create circuits directory
        circuits_dir = tmp_path / "vibe_core/plugins/opus_assistant/circuits"
        circuits_dir.mkdir(parents=True)

        # Create a simplified maintenance circuit that just refreshes OPUS.md
        maintenance_circuit = """
circuit:
  id: opus_refresh
  name: "OPUS Refresh"
  entry_state: "refresh"
  states:
    refresh:
      name: "Refresh OPUS.md"
      actions:
        - action_type: EXECUTE_SCRIPT
          target: "opus.write_opus_md"
          params:
            quick: true
      terminal: true
"""
        (circuits_dir / "opus_refresh.yaml").write_text(maintenance_circuit)

        # Create OPUS.md with old content
        (tmp_path / "OPUS.md").write_text("# Old OPUS\nLast Updated: 1999")

        return CognitiveCircuitExecutor(tmp_path), tmp_path

    def test_opus_md_gets_updated(self, executor_with_maintenance_circuit):
        """Circuit executor can update OPUS.md."""
        executor, workspace = executor_with_maintenance_circuit

        opus_path = workspace / "OPUS.md"
        old_content = opus_path.read_text()

        # Mock the renderer to avoid complex dependencies
        with patch(
            "vibe_core.plugins.opus_assistant.render.opus_dashboard_renderer.OpusDashboardRenderer"
        ) as MockRenderer:
            mock_instance = MockRenderer.return_value
            mock_instance.render.return_value = "# NEW OPUS\nLast Updated: 2025"

            result = executor.execute_circuit("opus_refresh")

        # Verify
        assert result["success"] is True
        new_content = opus_path.read_text()
        assert new_content != old_content
        assert "2025" in new_content


class TestCognitiveKernelIntegration:
    """Integration: CognitiveKernel must use CircuitExecutor."""

    def test_cognitive_kernel_can_execute_circuits(self, tmp_path):
        """CognitiveKernel must be able to execute circuits via _execute_intent."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        kernel = CognitiveKernel(workspace=tmp_path)
        # Verify kernel has _execute_intent method which handles circuits
        assert hasattr(kernel, "_execute_intent")
        assert callable(kernel._execute_intent)

    def test_execute_intent_uses_circuit_executor(self, tmp_path):
        """_execute_intent must call circuit executor for circuit intents."""
        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
            IntentBufferEntry,
        )
        from vibe_core.plugins.opus_assistant.manas.intent_generator import (
            Intent,
            IntentPriority,
            IntentRisk,
        )

        kernel = CognitiveKernel(workspace=tmp_path)

        # Create an intent with circuit_to_execute
        intent = Intent(
            id="test-001",
            intent_type="maintenance",
            title="Test Maintenance",
            description="Test",
            reasoning="Test",
            priority=IntentPriority.LOW,
            risk=IntentRisk.SAFE,
            circuit_to_execute="maintenance_pulse",
        )
        entry = IntentBufferEntry(intent=intent, status="approved")

        # Mock the CognitiveCircuitExecutor at its source module
        mock_executor = MagicMock()
        mock_executor.execute_circuit.return_value = {"success": True}

        with patch(
            "vibe_core.plugins.opus_assistant.manas.circuit_executor.CognitiveCircuitExecutor",
            return_value=mock_executor,
        ):
            # Execute
            result = kernel._execute_intent(entry)

            # Verify circuit executor was called
            mock_executor.execute_circuit.assert_called_once_with("maintenance_pulse")


class TestNoMoreTBD:
    """Critical: The 'TBD' fake code must be gone."""

    def test_no_tbd_in_execute_intent(self):
        """cognitive_kernel.py must NOT contain 'actual execution TBD'."""
        import inspect

        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        source = inspect.getsource(CognitiveKernel._execute_intent)
        assert "actual execution TBD" not in source, (
            "The fake 'TBD' code is still there! Replace it with real circuit execution."
        )

    def test_no_fake_success_for_circuits(self):
        """Circuit execution must not fake success."""
        import inspect

        from vibe_core.plugins.opus_assistant.manas.cognitive_kernel import (
            CognitiveKernel,
        )

        source = inspect.getsource(CognitiveKernel._execute_intent)

        # The old fake pattern was: success = True followed by circuit_queued
        # This should no longer exist
        assert "circuit_queued" not in source, (
            "The fake 'circuit_queued' response is still there! Use real circuit execution."
        )

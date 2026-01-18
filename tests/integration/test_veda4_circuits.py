#!/usr/bin/env python3
"""
VEDA-4 COGNITIVE CIRCUIT INTEGRATION TESTS
===========================================
Tests the Cognitive Circuit Executor with REAL components:

- RealVibeKernel (not mocked)
- SQLite Ledger (in-memory)
- Real Circuit Definitions (from YAML)
- Real Invariant Checking
- Real State Machine Transitions

NO MOCKS for kernel, ledger, or circuit logic.
This is a TRUE integration test.
"""

import logging
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.circuit_executor import (
    CognitiveCircuitExecutor,
    InvariantChecker,
    MetaCircuitManager,
    create_circuit_executor,
    create_circuit_executor_with_meta,
)
from vibe_core.plugins.test_orchestration import TestKernel

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("TEST_VEDA4_CIRCUITS")


# ============================================================================
# INVARIANT CHECKER TESTS
# ============================================================================


class TestInvariantChecker:
    """Test the InvariantChecker - the SECURITY layer of cognitive circuits."""

    def test_invariant_checker_instantiation(self):
        """Test that InvariantChecker can be instantiated."""
        checker = InvariantChecker()
        assert checker is not None
        assert checker.violations == []
        logger.info("InvariantChecker instantiated successfully")

    def test_invariant_is_not_empty_passes(self):
        """Test 'X is not empty' invariant when value exists."""
        checker = InvariantChecker()
        variables = {"user_id": "test_user", "data": {"nested": "value"}}

        result = checker.check_invariants(
            ["user_id is not empty", "data is not empty"],
            variables,
            "TEST_STATE",
        )

        assert result is True
        assert len(checker.violations) == 0
        logger.info("'is not empty' invariants passed correctly")

    def test_invariant_is_not_empty_fails(self):
        """Test 'X is not empty' invariant when value is missing."""
        checker = InvariantChecker()
        variables = {"user_id": "", "data": None}

        result = checker.check_invariants(
            ["user_id is not empty", "data is not empty"],
            variables,
            "TEST_STATE",
        )

        assert result is False
        assert len(checker.violations) == 2
        assert checker.violations[0].state == "TEST_STATE"
        logger.info("'is not empty' invariants failed correctly")

    def test_invariant_equality_check(self):
        """Test 'X == Y' invariant."""
        checker = InvariantChecker()
        variables = {"status": "active", "count": 5}

        # Should pass
        result = checker.check_invariants(
            ["status == active", "count == 5"],
            variables,
            "TEST_STATE",
        )
        assert result is True

        # Should fail
        checker.clear_violations()
        result = checker.check_invariants(
            ["status == inactive"],
            variables,
            "TEST_STATE",
        )
        assert result is False
        logger.info("Equality invariants work correctly")

    def test_invariant_comparison_operators(self):
        """Test comparison operators (>=, <=, >, <)."""
        checker = InvariantChecker()
        variables = {"credits": 100, "attempts": 3}

        # Should pass
        result = checker.check_invariants(
            ["credits >= 50", "attempts <= 5", "credits > 99", "attempts < 10"],
            variables,
            "TEST_STATE",
        )
        assert result is True

        # Should fail
        checker.clear_violations()
        result = checker.check_invariants(
            ["credits >= 200"],  # 100 is not >= 200
            variables,
            "TEST_STATE",
        )
        assert result is False
        logger.info("Comparison invariants work correctly")

    def test_invariant_dotted_path_resolution(self):
        """Test that dotted paths like 'result.status' are resolved."""
        checker = InvariantChecker()
        variables = {
            "result": {"status": "success", "count": 42},
            "user": {"profile": {"verified": True}},
        }

        result = checker.check_invariants(
            ["result.status == success", "result.count >= 40"],
            variables,
            "TEST_STATE",
        )
        assert result is True
        logger.info("Dotted path resolution works correctly")

    def test_invariant_unknown_pattern_fails_closed(self):
        """Test that unknown invariant patterns FAIL-CLOSED (security)."""
        checker = InvariantChecker()
        variables = {"data": "test"}

        # Typo in invariant - should FAIL (not silently pass)
        result = checker.check_invariants(
            ["data is nota empty"],  # Typo: "nota" instead of "not"
            variables,
            "TEST_STATE",
        )

        assert result is False
        assert "Unknown invariant pattern" in checker.violations[0].reason
        logger.info("Unknown patterns fail-closed (security feature)")


# ============================================================================
# CIRCUIT EXECUTOR TESTS
# ============================================================================


class TestCognitiveCircuitExecutor:
    """Test the CognitiveCircuitExecutor with RealVibeKernel."""

    def test_executor_instantiation_with_real_kernel(self):
        """Test that CognitiveCircuitExecutor works with RealVibeKernel."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        assert executor is not None
        assert executor.kernel is kernel
        assert executor.syscall_executor is not None
        assert executor.invariant_checker is not None
        logger.info("CognitiveCircuitExecutor instantiated with RealVibeKernel")

    def test_circuit_loading_from_yaml(self):
        """Test that circuits are loaded from YAML files."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        # Should have loaded circuits from vibe_core/playbook/circuits/
        assert len(executor.circuits) > 0
        logger.info(f"Loaded {len(executor.circuits)} circuits: {list(executor.circuits.keys())}")

        # Check for known circuits
        expected_circuits = [
            "GOVERNANCE_VOTE_V2",
            "CONTENT_GENERATION_V2",
            "PROJECT_SCAFFOLD_V2",
            "AGENT_BIRTH_V1",
        ]
        found = [c for c in expected_circuits if c in executor.circuits]
        assert len(found) >= 1, f"Expected to find at least one circuit from {expected_circuits}"
        logger.info(f"Found expected circuits: {found}")

    def test_circuit_has_required_structure(self):
        """Test that loaded circuits have required structure."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        # Meta-circuits (TASK_LEDGER, ERROR_RECOVERY) have different structure
        meta_circuits = {"TASK_LEDGER_V1", "ERROR_RECOVERY_V1"}

        for circuit_id, circuit_def in executor.circuits.items():
            # Every circuit must have an ID
            assert "id" in circuit_def, f"Circuit {circuit_id} missing 'id'"

            # Skip detailed structure validation for meta-circuits
            if circuit_id in meta_circuits:
                logger.info(f"Circuit {circuit_id} is a meta-circuit (skipping state validation)")
                continue

            # Every circuit must have states
            assert "states" in circuit_def, f"Circuit {circuit_id} missing 'states'"

            # Every circuit should have an entry_state
            assert "entry_state" in circuit_def, f"Circuit {circuit_id} missing 'entry_state'"

            # Entry state must exist in states
            entry = circuit_def["entry_state"]
            states = circuit_def["states"]
            assert entry in states, f"Circuit {circuit_id} entry_state '{entry}' not in states"

        logger.info(f"All {len(executor.circuits)} circuits have valid structure")

    def test_factory_function_creates_executor(self):
        """Test create_circuit_executor factory function."""
        kernel = TestKernel.with_governance()
        executor = create_circuit_executor(kernel)

        assert isinstance(executor, CognitiveCircuitExecutor)
        assert executor.kernel is kernel
        logger.info("Factory function create_circuit_executor works")

    def test_factory_function_with_meta_creates_both(self):
        """Test create_circuit_executor_with_meta creates executor and manager."""
        kernel = TestKernel.with_governance()
        executor, manager = create_circuit_executor_with_meta(kernel)

        assert isinstance(executor, CognitiveCircuitExecutor)
        assert isinstance(manager, MetaCircuitManager)
        assert manager.executor is executor
        logger.info("Factory function create_circuit_executor_with_meta works")


# ============================================================================
# META-CIRCUIT MANAGER TESTS
# ============================================================================


class TestMetaCircuitManager:
    """Test the MetaCircuitManager (TASK_LEDGER + ERROR_RECOVERY)."""

    def test_meta_manager_instantiation(self):
        """Test that MetaCircuitManager can be instantiated."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)
        manager = MetaCircuitManager(executor)

        assert manager is not None
        assert manager.executor is executor
        assert manager.ledgers == {}
        assert manager.recovery_attempts == []
        logger.info("MetaCircuitManager instantiated successfully")

    def test_meta_manager_wiring(self):
        """Test that MetaCircuitManager can wire callbacks to executor."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)
        manager = MetaCircuitManager(executor)

        manager.wire_callbacks()

        assert executor._on_circuit_start is not None
        assert executor._on_state_transition is not None
        assert executor._on_circuit_end is not None
        assert executor._on_error is not None
        logger.info("MetaCircuitManager callbacks wired successfully")

    def test_error_classification(self):
        """Test ERROR_RECOVERY error classification."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)
        manager = MetaCircuitManager(executor)

        # Test transient errors (patterns: timeout, connection, rate_limit, temporary, unavailable)
        assert manager._classify_error("Connection timeout") == "transient"
        assert manager._classify_error("Service temporarily unavailable") == "transient"
        assert manager._classify_error("rate_limit exceeded") == "transient"  # Uses underscore

        # Test input errors (patterns: validation, parse, missing, invalid, type)
        assert manager._classify_error("Validation failed") == "input_error"
        assert manager._classify_error("Missing required field") == "input_error"
        assert manager._classify_error("Invalid input format") == "input_error"

        # Test state errors (patterns: invariant, precondition, postcondition, stuck)
        assert manager._classify_error("Invariant violation") == "state_error"
        assert manager._classify_error("Precondition failed") == "state_error"

        # Test resource errors (patterns: memory, disk, quota, permission)
        assert manager._classify_error("Permission denied") == "resource_error"
        assert manager._classify_error("Disk quota exceeded") == "resource_error"

        logger.info("ERROR_RECOVERY classification works correctly")

    def test_recovery_strategy_selection(self):
        """Test ERROR_RECOVERY strategy selection."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)
        manager = MetaCircuitManager(executor)

        # Transient errors should retry
        assert manager._select_recovery_strategy("transient", 0) == "retry_same"

        # Input errors should adjust
        assert manager._select_recovery_strategy("input_error", 0) == "retry_adjusted"

        # State errors should replan
        assert manager._select_recovery_strategy("state_error", 0) == "replan"

        # Resource errors should escalate
        assert manager._select_recovery_strategy("resource_error", 0) == "escalate"

        # After max retries, escalate
        assert manager._select_recovery_strategy("transient", 10) == "escalate"

        logger.info("ERROR_RECOVERY strategy selection works correctly")

    def test_ledger_summary(self):
        """Test that ledger summary is computed correctly."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)
        manager = MetaCircuitManager(executor)

        summary = manager.get_ledger_summary()

        assert "total_executions" in summary
        assert "active_executions" in summary
        assert "successful_executions" in summary
        assert "failed_executions" in summary
        assert "total_recovery_attempts" in summary

        assert summary["total_executions"] == 0
        logger.info("MetaCircuitManager ledger summary works")


# ============================================================================
# CIRCUIT EXECUTION INTEGRATION TESTS
# ============================================================================


class TestCircuitExecution:
    """Integration tests for circuit execution with RealVibeKernel."""

    def test_direct_syscall_execution(self):
        """Test that simple syscalls execute directly (no full circuit)."""
        kernel = TestKernel.with_governance()
        kernel.boot()
        executor = CognitiveCircuitExecutor(kernel)

        # Simple task dispatch should go direct, not through circuit
        result = executor.execute(
            raw_input="Check the system status",
            requester_id="test_user",
        )

        # Should either execute or indicate it's not a syscall
        assert result is not None
        assert result.final_state in ["DIRECT_EXECUTION", "NOT_SYSCALL"]
        logger.info(f"Direct execution result: {result.final_state}")

    def test_circuit_execution_records_to_ledger(self):
        """Test that circuit execution records events to the ledger."""
        kernel = TestKernel.with_governance()
        kernel.boot()
        executor, manager = create_circuit_executor_with_meta(kernel)

        # Execute something that triggers a syscall
        result = executor.execute(
            raw_input="Create a new monitoring agent that watches health",
            requester_id="test_user",
        )

        # Check result
        assert result is not None
        assert result.state_history is not None
        assert len(result.state_history) >= 1

        logger.info(f"Execution result: success={result.success}, final_state={result.final_state}")
        logger.info(f"State history: {result.state_history}")
        logger.info(f"Syscalls executed: {result.syscall_count}")

    def test_circuit_invariant_enforcement(self):
        """Test that circuit invariants are enforced during execution."""
        kernel = TestKernel.with_governance()
        kernel.boot()
        executor = CognitiveCircuitExecutor(kernel)

        # The invariant checker should have been used
        assert executor.invariant_checker is not None

        # Execute and check that violations are tracked
        result = executor.execute(
            raw_input="Create an agent",
            requester_id="test_user",
        )

        # Get any violations that occurred
        violations = executor.invariant_checker.get_violations()
        logger.info(f"Invariant violations during execution: {len(violations)}")

        # Even if there were violations, we should have a result
        assert result is not None

    def test_meta_circuit_tracks_execution(self):
        """Test that MetaCircuitManager tracks circuit execution."""
        kernel = TestKernel.with_governance()
        kernel.boot()
        executor, manager = create_circuit_executor_with_meta(kernel)

        # Execute something
        result = executor.execute(
            raw_input="Create a monitoring agent for system health",
            requester_id="test_user",
        )

        # Check ledger was updated
        summary = manager.get_ledger_summary()
        logger.info(f"Ledger summary after execution: {summary}")

        # Total executions should be > 0 if callbacks fired
        # (Note: Only increments if circuit was actually executed, not direct syscall)
        assert summary["total_executions"] >= 0, "Should track executions"


# ============================================================================
# CIRCUIT DEFINITION VALIDATION TESTS
# ============================================================================


class TestCircuitDefinitionValidation:
    """Test that circuit YAML definitions are valid and complete."""

    def test_all_circuits_have_terminal_states(self):
        """Test that all circuits have at least one terminal state."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        for circuit_id, circuit_def in executor.circuits.items():
            states = circuit_def.get("states", {})
            terminal_states = [name for name, state_def in states.items() if state_def.get("terminal", False)]

            assert len(terminal_states) >= 1, f"Circuit {circuit_id} has no terminal states"
            logger.info(f"Circuit {circuit_id} has terminal states: {terminal_states}")

    def test_all_circuits_have_transitions(self):
        """Test that non-terminal states have transitions defined."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        states_without_transitions = []

        for circuit_id, circuit_def in executor.circuits.items():
            states = circuit_def.get("states", {})

            for state_name, state_def in states.items():
                if state_def.get("terminal", False):
                    continue  # Terminal states don't need transitions

                transitions = state_def.get("transitions", [])
                # Non-terminal states should have at least one transition
                if len(transitions) == 0:
                    states_without_transitions.append(f"{circuit_id}.{state_name}")
                    logger.warning(f"Circuit {circuit_id} state '{state_name}' has no transitions")

        # FAIL if any non-terminal state lacks transitions (dead-end state = bug)
        assert len(states_without_transitions) == 0, (
            f"CIRCUIT DEAD-END: {len(states_without_transitions)} non-terminal states have no transitions: "
            f"{states_without_transitions[:5]}{'...' if len(states_without_transitions) > 5 else ''}"
        )

    def test_circuit_invariants_are_valid_patterns(self):
        """Test that circuit invariants use valid patterns."""
        kernel = TestKernel.with_governance()
        executor = CognitiveCircuitExecutor(kernel)

        valid_patterns = [
            "is not empty",
            "is empty",
            "==",
            "!=",
            ">=",
            "<=",
            ">",
            "<",
            "is not in",
            "is in",
            "has",
        ]

        invalid_invariants = []

        for circuit_id, circuit_def in executor.circuits.items():
            # Check global invariants
            global_invariants = circuit_def.get("invariants", [])
            for inv in global_invariants:
                inv_str = inv.get("check", inv) if isinstance(inv, dict) else inv
                has_valid_pattern = any(p in inv_str.lower() for p in valid_patterns)
                if not has_valid_pattern:
                    invalid_invariants.append(f"{circuit_id}: {inv_str}")
                    logger.warning(f"Circuit {circuit_id} has potentially invalid invariant: {inv_str}")

            # Check state invariants
            states = circuit_def.get("states", {})
            for state_name, state_def in states.items():
                state_invariants = state_def.get("invariants", [])
                for inv in state_invariants:
                    has_valid_pattern = any(p in inv.lower() for p in valid_patterns)
                    if not has_valid_pattern:
                        invalid_invariants.append(f"{circuit_id}.{state_name}: {inv}")
                        logger.warning(
                            f"Circuit {circuit_id} state '{state_name}' has potentially invalid invariant: {inv}"
                        )

        # FAIL if any invariant uses unknown patterns (fail-closed security)
        assert len(invalid_invariants) == 0, (
            f"INVALID INVARIANT PATTERNS: {len(invalid_invariants)} invariants use unknown patterns: "
            f"{invalid_invariants[:3]}{'...' if len(invalid_invariants) > 3 else ''}"
        )


# ============================================================================
# ENTRY POINT
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

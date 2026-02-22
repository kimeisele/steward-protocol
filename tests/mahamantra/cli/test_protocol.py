"""
TESTS: cli/protocol.py - GAD-000 Compliant CLI Protocol
========================================================

REAL TESTS for:
1. CLIErrorCode enum
2. OutputFormat enum
3. CLIOutputItem, CLIOutput
4. CLIError, CLIResult
5. CLIParameter, CLICapability
6. CLIState, CLIHealth, CLIContext
7. CLIExecutable protocol
8. CLIExecutableBase base class
"""

import pytest
from datetime import datetime
from vibe_core.mahamantra.cli.protocol import (
    # Constants
    LILA_BOUNDARY,
    LILA_LIMIT,
    NAVADVIPA_LIMIT,
    PURI_LIMIT,
    PARAMPARA_PRIME,
    # Error codes
    CLIErrorCode,
    # Output types
    OutputFormat,
    CLIOutputItem,
    CLIOutput,
    # Error
    CLIError,
    # Result
    CLIResult,
    # Capability
    CLIParameter,
    CLICapability,
    # State
    CLIState,
    # Health
    CLIHealth,
    # Context
    CLIContext,
    # Protocol
    CLIExecutable,
    # Base
    CLIExecutableBase,
    # Lila
    LilaPhase,
    LilaBoundaryViolation,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestCLIConstants:
    """Test CLI constants."""

    def test_lila_boundary_is_24(self):
        """LILA_BOUNDARY is 24."""
        assert LILA_BOUNDARY == 24

    def test_lila_limit_is_48(self):
        """LILA_LIMIT is 48."""
        assert LILA_LIMIT == 48

    def test_navadvipa_limit_is_24(self):
        """NAVADVIPA_LIMIT is 24 (alias for LILA_BOUNDARY)."""
        assert NAVADVIPA_LIMIT == 24

    def test_puri_limit_is_24(self):
        """PURI_LIMIT is 24."""
        assert PURI_LIMIT == 24

    def test_parampara_prime_is_37(self):
        """PARAMPARA_PRIME is 37."""
        assert PARAMPARA_PRIME == 37


# =============================================================================
# CLIErrorCode Tests
# =============================================================================


class TestCLIErrorCode:
    """Test CLIErrorCode enum."""

    def test_success_is_0(self):
        """SUCCESS is 0."""
        assert CLIErrorCode.SUCCESS == 0

    def test_user_errors_1_to_99(self):
        """User errors are in range 1-99."""
        assert CLIErrorCode.INVALID_ARGUMENT == 1
        assert CLIErrorCode.MISSING_ARGUMENT == 2
        assert CLIErrorCode.UNKNOWN_COMMAND == 3
        assert CLIErrorCode.INVALID_FORMAT == 4

    def test_system_errors_100_to_199(self):
        """System errors are in range 100-199."""
        assert CLIErrorCode.TIMEOUT == 100
        assert CLIErrorCode.SERVICE_UNAVAILABLE == 101
        assert CLIErrorCode.RESOURCE_BUSY == 102
        assert CLIErrorCode.RATE_LIMITED == 103

    def test_permission_errors_200_to_299(self):
        """Permission errors are in range 200-299."""
        assert CLIErrorCode.UNAUTHORIZED == 200
        assert CLIErrorCode.FORBIDDEN == 201
        assert CLIErrorCode.SIGNATURE_REQUIRED == 202
        assert CLIErrorCode.SIGNATURE_INVALID == 203

    def test_state_errors_300_to_399(self):
        """State errors are in range 300-399."""
        assert CLIErrorCode.STATE_CORRUPTED == 300
        assert CLIErrorCode.STATE_DRIFT == 301
        assert CLIErrorCode.INCONSISTENT_STATE == 302

    def test_fatal_errors_400_plus(self):
        """Fatal errors are 400+."""
        assert CLIErrorCode.INTERNAL_ERROR == 400
        assert CLIErrorCode.NOT_IMPLEMENTED == 401
        assert CLIErrorCode.FATAL == 500

    def test_is_retryable_user_errors(self):
        """User errors are retryable."""
        assert CLIErrorCode.INVALID_ARGUMENT.is_retryable is True
        assert CLIErrorCode.MISSING_ARGUMENT.is_retryable is True

    def test_is_retryable_transient(self):
        """Transient errors are retryable."""
        assert CLIErrorCode.TIMEOUT.is_retryable is True
        assert CLIErrorCode.SERVICE_UNAVAILABLE.is_retryable is True

    def test_is_transient(self):
        """is_transient for system errors."""
        assert CLIErrorCode.TIMEOUT.is_transient is True
        assert CLIErrorCode.SERVICE_UNAVAILABLE.is_transient is True
        assert CLIErrorCode.INVALID_ARGUMENT.is_transient is False
        assert CLIErrorCode.FATAL.is_transient is False

    def test_requires_escalation(self):
        """requires_escalation for permission errors."""
        assert CLIErrorCode.UNAUTHORIZED.requires_escalation is True
        assert CLIErrorCode.FORBIDDEN.requires_escalation is True
        assert CLIErrorCode.SIGNATURE_REQUIRED.requires_escalation is True
        assert CLIErrorCode.TIMEOUT.requires_escalation is False

    def test_requires_recovery(self):
        """requires_recovery for state errors."""
        assert CLIErrorCode.STATE_CORRUPTED.requires_recovery is True
        assert CLIErrorCode.STATE_DRIFT.requires_recovery is True
        assert CLIErrorCode.INCONSISTENT_STATE.requires_recovery is True
        assert CLIErrorCode.FATAL.requires_recovery is False


# =============================================================================
# OutputFormat Tests
# =============================================================================


class TestOutputFormat:
    """Test OutputFormat enum."""

    def test_json_format(self):
        """OutputFormat has JSON."""
        assert OutputFormat.JSON.value == "json"

    def test_table_format(self):
        """OutputFormat has TABLE."""
        assert OutputFormat.TABLE.value == "table"

    def test_lines_format(self):
        """OutputFormat has LINES."""
        assert OutputFormat.LINES.value == "lines"

    def test_stream_format(self):
        """OutputFormat has STREAM."""
        assert OutputFormat.STREAM.value == "stream"


# =============================================================================
# CLIOutputItem Tests
# =============================================================================


class TestCLIOutputItem:
    """Test CLIOutputItem dataclass."""

    def test_output_item_creation(self):
        """CLIOutputItem can be created."""
        item = CLIOutputItem(key="test", value="value")
        assert item.key == "test"
        assert item.value == "value"
        assert item.metadata == {}

    def test_output_item_with_metadata(self):
        """CLIOutputItem supports metadata."""
        item = CLIOutputItem(key="key", value=42, metadata={"source": "test"})
        assert item.key == "key"
        assert item.value == 42
        assert item.metadata["source"] == "test"


# =============================================================================
# CLIOutput Tests
# =============================================================================


class TestCLIOutput:
    """Test CLIOutput dataclass."""

    def test_cli_output_creation(self):
        """CLIOutput can be created."""
        output = CLIOutput()
        assert output.items == []
        assert output.format == OutputFormat.JSON

    def test_cli_output_add(self):
        """CLIOutput.add adds items."""
        output = CLIOutput()
        output.add("key1", "value1")
        output.add("key2", 42)
        assert len(output.items) == 2
        assert output.items[0].key == "key1"
        assert output.items[1].value == 42

    def test_cli_output_add_chaining(self):
        """CLIOutput.add supports chaining."""
        output = CLIOutput().add("a", 1).add("b", 2)
        assert len(output.items) == 2

    def test_cli_output_add_with_metadata(self):
        """CLIOutput.add supports metadata kwargs."""
        output = CLIOutput()
        output.add("key", "value", source="test", level="info")
        assert output.items[0].metadata["source"] == "test"
        assert output.items[0].metadata["level"] == "info"

    def test_cli_output_add_row(self):
        """CLIOutput.add_row adds table rows."""
        output = CLIOutput()
        output.add_row("col1", "col2", "col3")
        assert len(output.rows) == 1
        assert output.rows[0] == ["col1", "col2", "col3"]

    def test_cli_output_lila_boundary_strict(self):
        """CLIOutput enforces Lila boundary in strict mode."""
        output = CLIOutput(strict_mode=True)
        for i in range(24):
            output.add(f"key_{i}", f"value_{i}")
        assert len(output.items) == 24

        with pytest.raises(LilaBoundaryViolation):
            output.add("overflow", "value")

    def test_cli_output_lila_boundary_non_strict(self):
        """CLIOutput tracks overflow in non-strict mode."""
        output = CLIOutput(strict_mode=False)
        for i in range(50):
            output.add(f"key_{i}", f"value_{i}")
        # Items capped at LILA_LIMIT (48)
        assert len(output.items) <= 48
        assert output.has_more is True

    def test_cli_output_lila_phase(self):
        """CLIOutput tracks Lila phase."""
        output = CLIOutput()
        assert output.lila_phase == LilaPhase.NAVADVIPA

    def test_cli_output_next_phase(self):
        """CLIOutput.next_phase advances phase."""
        output = CLIOutput()
        output.next_phase()
        assert output.lila_phase == LilaPhase.PURI

    def test_cli_output_to_dict(self):
        """CLIOutput.to_dict serializes correctly."""
        output = CLIOutput()
        output.add("key", "value")
        data = output.to_dict()
        assert "items" in data
        assert "format" in data
        assert "lila_phase" in data
        assert "parampara_verified" in data
        assert data["parampara_verified"] is True

    def test_cli_output_total_count(self):
        """CLIOutput.total_count includes overflow."""
        output = CLIOutput(strict_mode=False)
        for i in range(50):
            output.add(f"key_{i}", i)
        assert output.total_count == 50

    def test_cli_output_validate(self):
        """CLIOutput.validate returns (bool, violations)."""
        output = CLIOutput()
        valid, violations = output.validate()
        assert valid is True
        assert len(violations) == 0


# =============================================================================
# CLIError Tests
# =============================================================================


class TestCLIError:
    """Test CLIError dataclass."""

    def test_cli_error_creation(self):
        """CLIError can be created."""
        error = CLIError(
            code=CLIErrorCode.INVALID_ARGUMENT,
            message="Invalid value",
        )
        assert error.code == CLIErrorCode.INVALID_ARGUMENT
        assert error.message == "Invalid value"

    def test_cli_error_with_context(self):
        """CLIError supports context."""
        error = CLIError(
            code=CLIErrorCode.UNKNOWN_COMMAND,
            message="Command not found",
            context={"command": "foo"},
        )
        assert error.context["command"] == "foo"

    def test_cli_error_with_recovery_hints(self):
        """CLIError supports recovery hints."""
        error = CLIError(
            code=CLIErrorCode.TIMEOUT,
            message="Operation timed out",
            recovery_hints=["Retry after 5 seconds", "Check network"],
        )
        assert len(error.recovery_hints) == 2

    def test_cli_error_has_timestamp(self):
        """CLIError has timestamp."""
        error = CLIError(code=CLIErrorCode.SUCCESS, message="OK")
        assert error.timestamp is not None

    def test_cli_error_to_dict(self):
        """CLIError.to_dict serializes correctly."""
        error = CLIError(
            code=CLIErrorCode.FORBIDDEN,
            message="Access denied",
            context={"resource": "admin"},
        )
        data = error.to_dict()
        assert data["code"] == 201
        assert data["code_name"] == "FORBIDDEN"
        assert data["message"] == "Access denied"
        assert data["requires_escalation"] is True


# =============================================================================
# CLIResult Tests
# =============================================================================


class TestCLIResult:
    """Test CLIResult dataclass."""

    def test_cli_result_creation(self):
        """CLIResult can be created."""
        result = CLIResult(success=True, exit_code=0)
        assert result.success is True
        assert result.exit_code == 0

    def test_cli_result_ok_factory(self):
        """CLIResult.ok creates successful result."""
        result = CLIResult.ok()
        assert result.success is True
        assert result.exit_code == 0

    def test_cli_result_ok_with_kwargs(self):
        """CLIResult.ok adds kwargs to output."""
        result = CLIResult.ok(status="complete", count=42)
        assert result.success is True
        items = {item.key: item.value for item in result.output.items}
        assert items["status"] == "complete"
        assert items["count"] == 42

    def test_cli_result_fail_factory(self):
        """CLIResult.fail creates failed result."""
        result = CLIResult.fail(
            CLIErrorCode.INVALID_ARGUMENT,
            "Bad value",
            param="foo",
        )
        assert result.success is False
        assert result.exit_code == 1
        assert result.error is not None
        assert result.error.code == CLIErrorCode.INVALID_ARGUMENT
        assert result.error.context["param"] == "foo"

    def test_cli_result_idempotent_default(self):
        """CLIResult.idempotent defaults to True."""
        result = CLIResult(success=True, exit_code=0)
        assert result.idempotent is True

    def test_cli_result_to_dict(self):
        """CLIResult.to_dict serializes correctly."""
        result = CLIResult.ok(key="value")
        data = result.to_dict()
        assert data["success"] is True
        assert data["exit_code"] == 0
        assert "output" in data
        assert "timestamp" in data


# =============================================================================
# CLIParameter Tests
# =============================================================================


class TestCLIParameter:
    """Test CLIParameter dataclass."""

    def test_cli_parameter_creation(self):
        """CLIParameter can be created."""
        param = CLIParameter(name="target", param_type="string")
        assert param.name == "target"
        assert param.param_type == "string"
        assert param.required is False

    def test_cli_parameter_required(self):
        """CLIParameter supports required flag."""
        param = CLIParameter(name="file", param_type="string", required=True)
        assert param.required is True

    def test_cli_parameter_with_default(self):
        """CLIParameter supports default value."""
        param = CLIParameter(name="verbose", param_type="boolean", default=False)
        assert param.default is False

    def test_cli_parameter_with_choices(self):
        """CLIParameter supports choices."""
        param = CLIParameter(
            name="format",
            param_type="string",
            choices=["json", "table", "lines"],
        )
        assert len(param.choices) == 3


# =============================================================================
# CLICapability Tests
# =============================================================================


class TestCLICapability:
    """Test CLICapability dataclass."""

    def test_cli_capability_creation(self):
        """CLICapability can be created."""
        cap = CLICapability(name="analyze", purpose="Analyze system")
        assert cap.name == "analyze"
        assert cap.purpose == "Analyze system"

    def test_cli_capability_with_parameters(self):
        """CLICapability supports parameters."""
        cap = CLICapability(
            name="scan",
            purpose="Scan codebase",
            parameters=[
                CLIParameter(name="path", param_type="string", required=True),
                CLIParameter(name="deep", param_type="boolean", default=False),
            ],
        )
        assert len(cap.parameters) == 2

    def test_cli_capability_idempotent_default(self):
        """CLICapability.idempotent defaults to True."""
        cap = CLICapability(name="test", purpose="Test")
        assert cap.idempotent is True

    def test_cli_capability_to_dict(self):
        """CLICapability.to_dict serializes correctly."""
        cap = CLICapability(
            name="fetch",
            purpose="Fetch resource",
            keywords=["get", "retrieve"],
            mahajana_position=8,
        )
        data = cap.to_dict()
        assert data["name"] == "fetch"
        assert data["purpose"] == "Fetch resource"
        assert data["mahajana_position"] == 8
        assert "get" in data["keywords"]


# =============================================================================
# CLIState Tests
# =============================================================================


class TestCLIState:
    """Test CLIState dataclass."""

    def test_cli_state_creation(self):
        """CLIState can be created."""
        state = CLIState()
        assert state.ready is True
        assert state.busy is False
        assert state.healthy is True

    def test_cli_state_busy(self):
        """CLIState tracks busy state."""
        state = CLIState(busy=True)
        assert state.busy is True

    def test_cli_state_error_count(self):
        """CLIState tracks error count."""
        state = CLIState()
        state.error_count += 1
        assert state.error_count == 1

    def test_cli_state_to_dict(self):
        """CLIState.to_dict serializes correctly."""
        state = CLIState(last_command="analyze")
        data = state.to_dict()
        assert data["ready"] is True
        assert data["last_command"] == "analyze"


# =============================================================================
# CLIHealth Tests
# =============================================================================


class TestCLIHealth:
    """Test CLIHealth dataclass."""

    def test_cli_health_creation(self):
        """CLIHealth can be created."""
        health = CLIHealth()
        assert health.healthy is True
        assert health.drift_detected is False

    def test_cli_health_with_violations(self):
        """CLIHealth tracks violations."""
        health = CLIHealth(
            healthy=False,
            violations=["Memory leak detected", "State drift"],
        )
        assert health.healthy is False
        assert len(health.violations) == 2

    def test_cli_health_recovery_actions(self):
        """CLIHealth tracks recovery actions."""
        health = CLIHealth(
            recovery_actions=["Restart service", "Clear cache"],
        )
        assert len(health.recovery_actions) == 2

    def test_cli_health_to_dict(self):
        """CLIHealth.to_dict serializes correctly."""
        health = CLIHealth()
        data = health.to_dict()
        assert "healthy" in data
        assert "last_check" in data


# =============================================================================
# CLIContext Tests
# =============================================================================


class TestCLIContext:
    """Test CLIContext dataclass."""

    def test_cli_context_creation(self):
        """CLIContext can be created."""
        ctx = CLIContext()
        assert ctx.caller_id == "anonymous"
        assert ctx.signature is None

    def test_cli_context_with_command(self):
        """CLIContext holds command and args."""
        ctx = CLIContext(
            command="analyze",
            args=["--deep", "system"],
        )
        assert ctx.command == "analyze"
        assert len(ctx.args) == 2

    def test_cli_context_is_signed(self):
        """CLIContext.is_signed checks signature."""
        unsigned = CLIContext()
        assert unsigned.is_signed is False

        signed = CLIContext(signature="0xabc123")
        assert signed.is_signed is True

    def test_cli_context_mahajana_position(self):
        """CLIContext tracks mahajana position."""
        ctx = CLIContext(mahajana_position=6)
        assert ctx.mahajana_position == 6

    def test_cli_context_to_dict(self):
        """CLIContext.to_dict serializes correctly."""
        ctx = CLIContext(
            caller_id="user123",
            command="fetch",
        )
        data = ctx.to_dict()
        assert data["caller_id"] == "user123"
        assert data["command"] == "fetch"
        assert data["is_signed"] is False


# =============================================================================
# CLIExecutable Protocol Tests
# =============================================================================


class TestCLIExecutable:
    """Test CLIExecutable protocol."""

    def test_cli_executable_is_protocol(self):
        """CLIExecutable is a runtime checkable protocol."""
        assert hasattr(CLIExecutable, "__protocol_attrs__") or hasattr(CLIExecutable, "_is_runtime_protocol")


# =============================================================================
# CLIExecutableBase Tests
# =============================================================================


class TestCLIExecutableBase:
    """Test CLIExecutableBase base class."""

    def test_cli_executable_base_requires_subclass(self):
        """CLIExecutableBase is abstract."""
        # Cannot instantiate directly
        with pytest.raises(TypeError):
            CLIExecutableBase()

    def test_cli_executable_base_subclass(self):
        """CLIExecutableBase can be subclassed."""

        class TestCLI(CLIExecutableBase):
            @classmethod
            def get_capabilities(cls):
                return [CLICapability(name="test", purpose="Test command")]

            def _execute_impl(self, context):
                return CLIResult.ok(result="done")

        cli = TestCLI()
        assert cli.get_state().ready is True
        assert len(cli.get_capabilities()) == 1

    def test_cli_executable_base_execute(self):
        """CLIExecutableBase.execute wraps _execute_impl."""

        class TestCLI(CLIExecutableBase):
            @classmethod
            def get_capabilities(cls):
                return []

            def _execute_impl(self, context):
                return CLIResult.ok(status="executed")

        cli = TestCLI()
        result = cli.execute(CLIContext(command="test"))
        assert result.success is True
        assert result.duration_ms >= 0

    def test_cli_executable_base_error_handling(self):
        """CLIExecutableBase.execute catches exceptions."""

        class FailingCLI(CLIExecutableBase):
            @classmethod
            def get_capabilities(cls):
                return []

            def _execute_impl(self, context):
                raise RuntimeError("Test error")

        cli = FailingCLI()
        result = cli.execute(CLIContext(command="fail"))
        assert result.success is False
        assert result.error is not None
        assert result.error.code == CLIErrorCode.INTERNAL_ERROR

    def test_cli_executable_base_check_health(self):
        """CLIExecutableBase.check_health returns health."""

        class TestCLI(CLIExecutableBase):
            @classmethod
            def get_capabilities(cls):
                return []

            def _execute_impl(self, context):
                return CLIResult.ok()

        cli = TestCLI()
        health = cli.check_health()
        assert health.healthy is True


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import protocol

        expected = [
            "CLIErrorCode",
            "OutputFormat",
            "CLIOutputItem",
            "CLIOutput",
            "CLIError",
            "CLIResult",
            "CLIParameter",
            "CLICapability",
            "CLIState",
            "CLIHealth",
            "CLIContext",
            "CLIExecutable",
            "CLIExecutableBase",
        ]
        for item in expected:
            assert item in protocol.__all__, f"{item} should be in __all__"

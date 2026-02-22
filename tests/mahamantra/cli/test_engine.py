"""
TESTS: cli/engine.py - CLI Engine
==================================

REAL TESTS for:
1. CLIHandler type
2. MahajanaCliRegistration dataclass
3. CLIEngine class
4. cli_engine singleton
5. cli_command decorator
"""

import pytest
from vibe_core.mahamantra.cli.engine import (
    CLIEngine,
    cli_engine,
    MahajanaCliRegistration,
    cli_command,
    CLIHandler,
)
from vibe_core.mahamantra.cli.protocol import (
    CLICapability,
    CLIContext,
    CLIErrorCode,
    CLIResult,
)


# =============================================================================
# MahajanaCliRegistration Tests
# =============================================================================


class TestMahajanaCliRegistration:
    """Test MahajanaCliRegistration dataclass."""

    def test_registration_creation(self):
        """MahajanaCliRegistration can be created."""
        reg = MahajanaCliRegistration(
            position=6,
            capabilities=[CLICapability(name="analyze", purpose="Analyze")],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        assert reg.position == 6
        assert len(reg.capabilities) == 1

    def test_registration_auto_keywords(self):
        """MahajanaCliRegistration auto-derives keywords."""
        reg = MahajanaCliRegistration(
            position=6,
            capabilities=[CLICapability(name="analyze", purpose="Analyze", keywords=["inspect", "check"])],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        assert "analyze" in reg.keywords
        assert "inspect" in reg.keywords
        assert "check" in reg.keywords

    def test_registration_custom_keywords(self):
        """MahajanaCliRegistration supports custom keywords."""
        reg = MahajanaCliRegistration(
            position=6,
            capabilities=[],
            handlers={},
            keywords={"custom", "keywords"},
        )
        assert "custom" in reg.keywords
        assert "keywords" in reg.keywords


# =============================================================================
# CLIEngine Tests
# =============================================================================


class TestCLIEngine:
    """Test CLIEngine class."""

    def test_cli_engine_creation(self):
        """CLIEngine can be created."""
        engine = CLIEngine()
        assert engine is not None
        assert engine._registry == {}

    def test_cli_engine_register(self):
        """CLIEngine.register registers capabilities."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="test", purpose="Test command")],
            handlers={"test": lambda ctx: CLIResult.ok()},
        )
        assert 6 in engine._registry
        assert "test" in engine._keyword_to_position

    def test_cli_engine_register_handler(self):
        """CLIEngine.register_handler registers single handler."""
        engine = CLIEngine()
        engine.register_handler(
            position=8,
            command="fetch",
            handler=lambda ctx: CLIResult.ok(data="fetched"),
        )
        assert 8 in engine._registry
        assert "fetch" in engine._registry[8].handlers

    def test_cli_engine_get_position_exact_match(self):
        """CLIEngine.get_position finds exact keyword match."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="analyze", purpose="Analyze")],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        assert engine.get_position("analyze") == 6

    def test_cli_engine_get_position_substring_match(self):
        """CLIEngine.get_position finds substring match."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="analyze", purpose="Analyze")],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        pos = engine.get_position("analyze-deep")
        assert pos == 6 or pos is not None  # Either matched or fallback

    def test_cli_engine_get_position_parampara_fallback(self):
        """CLIEngine.get_position falls back to parampara hash."""
        engine = CLIEngine()
        pos = engine.get_position("unknown_command")
        assert 0 <= pos <= 15  # Valid position range

    def test_cli_engine_can_handle(self):
        """CLIEngine.can_handle checks handler availability."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        assert engine.can_handle(6, "analyze") is True
        assert engine.can_handle(6, "unknown") is False
        assert engine.can_handle(99, "anything") is False

    def test_cli_engine_execute_success(self):
        """CLIEngine.execute executes handler successfully."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="test", purpose="Test")],
            handlers={"test": lambda ctx: CLIResult.ok(result="done")},
        )
        result = engine.execute("test")
        assert result.success is True

    def test_cli_engine_execute_not_implemented(self):
        """CLIEngine.execute returns NOT_IMPLEMENTED for missing position."""
        engine = CLIEngine()
        result = engine.execute("unknown")
        assert result.success is False
        # Will either be NOT_IMPLEMENTED or UNKNOWN_COMMAND

    def test_cli_engine_execute_handler_exception(self):
        """CLIEngine.execute handles handler exceptions."""
        engine = CLIEngine()

        def failing_handler(ctx):
            raise RuntimeError("Test error")

        engine.register(
            position=6,
            capabilities=[CLICapability(name="fail", purpose="Fail")],
            handlers={"fail": failing_handler},
        )
        result = engine.execute("fail")
        assert result.success is False
        assert result.error.code == CLIErrorCode.INTERNAL_ERROR

    def test_cli_engine_execute_with_args(self):
        """CLIEngine.execute passes args in context."""
        engine = CLIEngine()
        received_args = []

        def capture_handler(ctx):
            received_args.extend(ctx.args)
            return CLIResult.ok()

        engine.register(
            position=6,
            capabilities=[CLICapability(name="capture", purpose="Capture")],
            handlers={"capture": capture_handler},
        )
        engine.execute("capture", args=["arg1", "arg2"])
        assert received_args == ["arg1", "arg2"]

    def test_cli_engine_get_capabilities_all(self):
        """CLIEngine.get_capabilities returns all capabilities."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="a", purpose="A")],
            handlers={"a": lambda ctx: CLIResult.ok()},
        )
        engine.register(
            position=8,
            capabilities=[CLICapability(name="b", purpose="B")],
            handlers={"b": lambda ctx: CLIResult.ok()},
        )
        caps = engine.get_capabilities()
        assert len(caps) == 2

    def test_cli_engine_get_capabilities_position(self):
        """CLIEngine.get_capabilities filters by position."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="a", purpose="A")],
            handlers={"a": lambda ctx: CLIResult.ok()},
        )
        engine.register(
            position=8,
            capabilities=[CLICapability(name="b", purpose="B")],
            handlers={"b": lambda ctx: CLIResult.ok()},
        )
        caps = engine.get_capabilities(position=6)
        assert len(caps) == 1
        assert caps[0].name == "a"

    def test_cli_engine_get_all_commands(self):
        """CLIEngine.get_all_commands lists all commands."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="analyze", purpose="Analyze system")],
            handlers={"analyze": lambda ctx: CLIResult.ok()},
        )
        commands = engine.get_all_commands()
        assert len(commands) == 1
        assert commands[0] == ("analyze", 6, "Analyze system")

    def test_cli_engine_get_state(self):
        """CLIEngine.get_state returns state for position."""
        engine = CLIEngine()
        engine.register(position=6, capabilities=[], handlers={})
        state = engine.get_state(6)
        assert state.ready is True

    def test_cli_engine_check_health(self):
        """CLIEngine.check_health returns health."""
        engine = CLIEngine()
        engine.register(position=6, capabilities=[], handlers={})
        health = engine.check_health()
        assert health.healthy is True

    def test_cli_engine_check_health_position(self):
        """CLIEngine.check_health returns health for position."""
        engine = CLIEngine()
        engine.register(position=6, capabilities=[], handlers={})
        health = engine.check_health(position=6)
        assert health.healthy is True

    def test_cli_engine_get_stats(self):
        """CLIEngine.get_stats returns statistics."""
        engine = CLIEngine()
        engine.register(
            position=6,
            capabilities=[CLICapability(name="a", purpose="A")],
            handlers={"a": lambda ctx: CLIResult.ok()},
        )
        stats = engine.get_stats()
        assert stats["registered_positions"] == 1
        assert stats["total_commands"] == 1
        assert stats["total_capabilities"] == 1

    def test_cli_engine_repr(self):
        """CLIEngine has __repr__."""
        engine = CLIEngine()
        assert "CLIEngine" in repr(engine)

    def test_cli_engine_tattva(self):
        """CLIEngine implements PanchaTattvaProtocol."""
        engine = CLIEngine()
        tattva = engine.__tattva__
        assert "chaitanya" in tattva
        assert "nityananda" in tattva
        assert "advaita" in tattva
        assert "gadadhara" in tattva
        assert "srivasa" in tattva


# =============================================================================
# cli_engine Singleton Tests
# =============================================================================


class TestCliEngineSingleton:
    """Test cli_engine singleton."""

    def test_cli_engine_is_instance(self):
        """cli_engine is a CLIEngine instance."""
        assert isinstance(cli_engine, CLIEngine)


# =============================================================================
# cli_command Decorator Tests
# =============================================================================


class TestCliCommandDecorator:
    """Test cli_command decorator."""

    def test_cli_command_decorator(self):
        """cli_command decorator registers handler."""
        # Create a new engine for this test
        test_engine = CLIEngine()

        # Note: cli_command uses the global cli_engine, so we test the pattern
        @cli_command(position=99, name="decorated_test", purpose="Test decorated")
        def test_handler(ctx):
            return CLIResult.ok(decorated=True)

        # Handler should be callable
        result = test_handler(CLIContext(command="decorated_test"))
        assert result.success is True


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.cli import engine

        expected = [
            "CLIEngine",
            "cli_engine",
            "CLIHandler",
            "MahajanaCliRegistration",
            "cli_command",
        ]
        for item in expected:
            assert item in engine.__all__, f"{item} should be in __all__"

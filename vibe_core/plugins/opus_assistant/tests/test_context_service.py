"""
OPUS Assistant - Context Service Tests

Tests for OpusContextService (Phase 2 Dynamic Context).
"""

from pathlib import Path
from unittest.mock import MagicMock


class TestOpusContextService:
    """Tests for OpusContextService."""

    def test_service_importable(self):
        """OpusContextService can be imported."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        assert OpusContextService is not None

    def test_opus_context_importable(self):
        """OpusContext dataclass can be imported."""
        from vibe_core.plugins.opus_assistant.core.context_service import OpusContext

        assert OpusContext is not None

    def test_system_health_importable(self):
        """SystemHealth dataclass can be imported."""
        from vibe_core.plugins.opus_assistant.core.context_service import SystemHealth

        assert SystemHealth is not None

    def test_service_instantiation(self):
        """OpusContextService can be instantiated."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        service = OpusContextService(workspace_root=Path("."))
        assert service is not None

    def test_system_health_overall(self):
        """SystemHealth calculates overall health correctly."""
        from vibe_core.plugins.opus_assistant.core.context_service import SystemHealth

        # All healthy
        health = SystemHealth(git_clean=True, ledger_valid=True, kernel_active=True, drift_healthy=True)
        assert health.overall_health == 1.0
        assert health.status == "HEALTHY"

        # Half healthy
        health2 = SystemHealth(git_clean=True, ledger_valid=True, kernel_active=False, drift_healthy=False)
        assert health2.overall_health == 0.5
        assert health2.status == "WARNING"

        # Mostly unhealthy
        health3 = SystemHealth(git_clean=False, ledger_valid=False, kernel_active=False, drift_healthy=True)
        assert health3.overall_health == 0.25
        assert health3.status == "CRITICAL"

    def test_opus_context_to_dict(self):
        """OpusContext.to_dict() returns proper structure."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContext,
            SystemHealth,
        )

        context = OpusContext(
            synthesized_at="2025-01-01T00:00:00",
            context_hash="abc123",
            git_branch="main",
            git_sha="abc123def456",
            git_dirty=False,
            uncommitted_files=[],
            ledger_head="ledger123",
            ledger_event_count=5,
            kernel_status="active",
            active_agents=2,
            pending_tasks=3,
            session_id="session123",
            uptime_seconds=100.0,
            loaded_personas=["persona1"],
            health=SystemHealth(),
            focus_areas=["Test focus"],
            warnings=["Test warning"],
        )

        result = context.to_dict()

        assert result["synthesized_at"] == "2025-01-01T00:00:00"
        assert result["context_hash"] == "abc123"
        assert result["git"]["branch"] == "main"
        assert result["git"]["sha"] == "abc123def456"
        assert result["ledger"]["head"] == "ledger123"
        assert result["runtime"]["kernel_status"] == "active"
        # Default SystemHealth has kernel_active=False, so overall is 0.75
        assert result["health"]["overall"] == 0.75
        assert "Test focus" in result["focus_areas"]
        assert "Test warning" in result["warnings"]

    def test_opus_context_to_system_prompt_fragment(self):
        """OpusContext generates system prompt fragment."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContext,
            SystemHealth,
        )

        context = OpusContext(
            synthesized_at="2025-01-01T00:00:00",
            context_hash="abc123def456",
            git_branch="feature/test",
            git_sha="abc123def456789",
            git_dirty=True,
            uncommitted_files=["file1.py", "file2.py"],
            ledger_head="ledger123",
            ledger_event_count=5,
            kernel_status="active",
            active_agents=2,
            pending_tasks=3,
            session_id="session123",
            uptime_seconds=100.0,
            loaded_personas=[],
            health=SystemHealth(git_clean=False),
            focus_areas=["Commit pending changes"],
            warnings=["High uncommitted file count"],
        )

        fragment = context.to_system_prompt_fragment()

        assert "## Current System State" in fragment
        # git_clean=False, kernel_active=False (default), so 50% = WARNING
        assert "WARNING" in fragment  # health.status
        assert "feature/test" in fragment
        assert "abc123de" in fragment  # short sha
        assert "Uncommitted:" in fragment
        assert "Commit pending changes" in fragment
        assert "High uncommitted file count" in fragment

    def test_synthesize_returns_context(self):
        """synthesize() returns OpusContext."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContext,
            OpusContextService,
        )

        # Use project root
        workspace = Path(__file__).parent.parent.parent.parent.parent
        service = OpusContextService(workspace_root=workspace)

        context = service.synthesize()

        assert isinstance(context, OpusContext)
        assert context.synthesized_at is not None
        assert context.context_hash is not None
        assert context.git_branch is not None

    def test_synthesize_increments_count(self):
        """synthesize() increments synthesis count."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        workspace = Path(__file__).parent.parent.parent.parent.parent
        service = OpusContextService(workspace_root=workspace)

        assert service.get_synthesis_count() == 0

        service.synthesize()
        assert service.get_synthesis_count() == 1

        service.synthesize()
        assert service.get_synthesis_count() == 2

    def test_get_last_context(self):
        """get_last_context() returns last synthesized context."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        workspace = Path(__file__).parent.parent.parent.parent.parent
        service = OpusContextService(workspace_root=workspace)

        assert service.get_last_context() is None

        context = service.synthesize()
        last = service.get_last_context()

        assert last is not None
        assert last.context_hash == context.context_hash

    def test_no_rendering_in_context_service(self):
        """context_service.py has no rich/UI imports."""
        service_path = Path(__file__).parent.parent / "core" / "context_service.py"
        content = service_path.read_text()

        assert "from rich" not in content
        assert "import rich" not in content
        assert "BasePanel" not in content
        assert ".render(" not in content


class TestContextServiceIntegration:
    """Integration tests for OpusContextService."""

    def test_context_includes_git_info(self):
        """Synthesized context includes git information."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        workspace = Path(__file__).parent.parent.parent.parent.parent
        service = OpusContextService(workspace_root=workspace)

        context = service.synthesize()

        # Should have git info (we're in a git repo)
        assert context.git_branch != "unknown"
        assert context.git_sha != "unknown"

    def test_context_generates_hash(self):
        """Context generates unique hash."""
        from vibe_core.plugins.opus_assistant.core.context_service import (
            OpusContextService,
        )

        workspace = Path(__file__).parent.parent.parent.parent.parent
        service = OpusContextService(workspace_root=workspace)

        context1 = service.synthesize()
        context2 = service.synthesize()

        # Hashes should be different (different timestamps)
        assert context1.context_hash != context2.context_hash
        assert len(context1.context_hash) == 64  # SHA256

    def test_exports_from_core(self):
        """Context service exported from core __init__."""
        from vibe_core.plugins.opus_assistant.core import (
            OpusContext,
            OpusContextService,
            SystemHealth,
        )

        assert OpusContextService is not None
        assert OpusContext is not None
        assert SystemHealth is not None


class TestKernelTickWithContext:
    """Tests for KernelTickHandler with context service integration."""

    def test_tick_handler_has_context_service(self):
        """KernelTickHandler initializes context service."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {"kernel_tick": {"enabled": True}}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)

        # Context service should be initialized
        assert handler._context_service is not None

    def test_get_context_service_accessor(self):
        """get_context_service() returns the service."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)
        service = handler.get_context_service()

        assert service is not None

    def test_get_system_prompt_fragment(self):
        """get_system_prompt_fragment() returns prompt text."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)

        # First synthesize (so there's context available)
        handler._context_service.synthesize()
        handler._context_service.inject()

        fragment = handler.get_system_prompt_fragment()

        assert "## Current System State" in fragment
        assert "Status:" in fragment

    def test_state_includes_context_info(self):
        """get_state() includes context service info."""
        from vibe_core.plugins.opus_assistant.events.kernel_tick import (
            KernelTickHandler,
        )

        mock_plugin = MagicMock()
        mock_plugin._config = {}
        mock_plugin._workspace = Path(__file__).parent.parent.parent.parent.parent

        handler = KernelTickHandler(mock_plugin)
        state = handler.get_state()

        assert "has_context_service" in state
        assert state["has_context_service"] is True
        assert "context_synthesis_count" in state

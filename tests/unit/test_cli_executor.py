"""
TEST: CLI Executor
==================
Tests for Topology-Aware Command Execution.
"""

import pytest

from vibe_core.cli.executor import CLIExecutor
from vibe_core.cli.protocol import CLICommand


class TestCLIExecutor:
    """Test executor functionality."""

    def test_init(self):
        """Should initialize with default gateway."""
        executor = CLIExecutor()
        assert executor.gateway_url == "http://localhost:8000"

    def test_resolve_handler_missing_plugin(self):
        """Should raise error if plugin not found."""
        executor = CLIExecutor()
        cmd = CLICommand(name="foo", namespace="nonexistent_plugin")

        with pytest.raises(ImportError):
            executor._resolve_handler(cmd)

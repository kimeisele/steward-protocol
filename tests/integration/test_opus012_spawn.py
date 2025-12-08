"""
Integration test for OPUS-012 Spawn Protocol.

Tests the full spawn flow:
1. Engineer writes cartridge to sandbox
2. Engineer generates passport with constitution hash
3. Engineer creates audit certificate
4. LifecyclePlugin verifies and grants life

Run: pytest tests/integration/test_opus012_spawn.py -v
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


class TestOpus012SpawnProtocol:
    """Test the OPUS-012 agent spawn protocol."""

    def test_lifecycle_plugin_loads(self):
        """LifecyclePlugin should load and initialize."""
        from vibe_core.plugins.lifecycle import LifecyclePlugin

        plugin = LifecyclePlugin()
        assert plugin.plugin_id == "lifecycle"
        assert plugin.priority == 10

    def test_syscall_registry_works(self):
        """SyscallRegistry should register and list syscalls."""
        from vibe_core.runtime.syscalls import SyscallRegistry

        registry = SyscallRegistry()

        # Register a test syscall
        def test_handler(kernel, params):
            return {"result": "ok"}

        registry.register("TEST_SYSCALL", test_handler, "Test syscall", "test")

        assert "TEST_SYSCALL" in registry.list_syscalls()
        caps = registry.get_capabilities()
        assert caps["total_count"] == 1

    def test_lifecycle_constitution_hash(self, tmp_path):
        """LifecyclePlugin should calculate constitution hash on boot."""
        from vibe_core.plugins.lifecycle import LifecyclePlugin

        # Create a mock constitution
        constitution = tmp_path / "CONSTITUTION.md"
        constitution.write_text("# Test Constitution", encoding="utf-8")

        # Mock cwd to point to tmp_path
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            plugin = LifecyclePlugin()

            # Mock kernel
            mock_kernel = Mock()
            plugin.on_boot(mock_kernel)

            assert plugin.constitution_hash != "no_constitution_found"
            assert plugin.constitution_hash != "not_initialized"
            assert len(plugin.constitution_hash) == 64  # SHA256 hex

    def test_lifecycle_spawn_rejects_ronin(self, tmp_path):
        """LifecyclePlugin should reject agents with wrong constitution hash."""
        from vibe_core.plugins.lifecycle import LifecyclePlugin

        # Create a mock constitution
        constitution = tmp_path / "CONSTITUTION.md"
        constitution.write_text("# Test Constitution", encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            plugin = LifecyclePlugin()
            mock_kernel = Mock()
            plugin.on_boot(mock_kernel)

            spec = {"id": "test_agent", "name": "Test"}
            passport = {"governance": {"constitution_hash": "wrong_hash"}}

            with pytest.raises(PermissionError, match="Ronin"):
                plugin.spawn_agent(spec, passport)

    def test_lifecycle_spawn_accepts_valid_oath(self, tmp_path):
        """LifecyclePlugin should accept agents with correct constitution hash."""
        from vibe_core.plugins.lifecycle import LifecyclePlugin

        # Create a mock constitution
        constitution = tmp_path / "CONSTITUTION.md"
        constitution.write_text("# Test Constitution", encoding="utf-8")

        # Create sandbox with audit certificate
        sandbox = tmp_path / "workspaces" / "sandbox" / "test_agent"
        sandbox.mkdir(parents=True)
        cert = sandbox / "audit_certificate.json"
        cert.write_text(json.dumps({"status": "approved"}), encoding="utf-8")

        with patch("pathlib.Path.cwd", return_value=tmp_path):
            plugin = LifecyclePlugin()
            mock_kernel = Mock()
            mock_kernel.prakriti = Mock()
            mock_kernel.prakriti.personas = Mock()
            mock_kernel.prakriti.personas.create_default = Mock(return_value=Mock())
            mock_kernel.prakriti.personas.save = Mock()
            mock_kernel._event_bus = Mock()

            plugin.on_boot(mock_kernel)

            spec = {"id": "test_agent", "name": "Test", "description": "A test agent"}
            passport = {"governance": {"constitution_hash": plugin.constitution_hash}}

            result = plugin.spawn_agent(spec, passport)

            assert result["status"] == "born"
            assert result["agent_id"] == "test_agent"
            assert "constitution" in result["gates_passed"]

    def test_engineer_spawn_agent_creates_files(self, tmp_path):
        """Engineer.spawn_agent should create cartridge and passport in sandbox."""
        import shutil

        from vibe_core.cartridges.system.engineer.cartridge_main import EngineerCartridge
        from vibe_core.scheduling.task import Task

        engineer = EngineerCartridge()
        engineer.system = Mock()
        engineer.system.kernel = Mock()
        engineer.system.kernel.lifecycle = Mock()
        engineer.system.kernel.lifecycle.constitution_hash = "test_hash_123"

        # Create a task
        task = Task(
            task_id="test_spawn",
            agent_id="engineer",
            payload={
                "action": "spawn_agent",
                "name": "test_curator",
                "mission": "Curate knowledge",
                "capabilities": ["query", "store"],
            },
        )

        # Note: spawn_agent writes to ./workspaces/sandbox/ (relative to cwd)
        # We'll check the actual files there and clean up after
        with patch("vibe_core.runtime.syscalls.execute_syscall") as mock_syscall:
            mock_syscall.return_value = {"status": "born", "agent_id": "test_curator"}

            result = engineer.spawn_agent(task)

        # Check result
        assert result["status"] == "spawned"
        assert result["agent_id"] == "test_curator"

        # Check files were created in real sandbox
        sandbox_dir = Path("./workspaces/sandbox/test_curator")
        try:
            assert sandbox_dir.exists(), f"Sandbox dir does not exist: {sandbox_dir}"
            assert (sandbox_dir / "cartridge_main.py").exists()
            assert (sandbox_dir / "steward.json").exists()
            assert (sandbox_dir / "audit_certificate.json").exists()

            # Verify passport has correct constitution hash
            passport = json.loads((sandbox_dir / "steward.json").read_text())
            assert passport["governance"]["constitution_hash"] == "test_hash_123"
        finally:
            # Clean up
            if sandbox_dir.exists():
                shutil.rmtree(sandbox_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

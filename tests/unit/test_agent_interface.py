"""
TEST: AgentSystemInterface - The Bridge Between Kernel and Agents
=================================================================
Verifies the system interface that agents use to interact with kernel capabilities.
Target: vibe_core/agent_interface.py
Standard: GAD-5000

Tests use standardized fixtures from test_orchestration - NO custom mocks.
"""

import tempfile
import uuid
from pathlib import Path

import pytest

from vibe_core.agent_interface import AgentSystemInterface
from vibe_core.plugins.test_orchestration.fixtures import TestAgents, TestKernel


class TestAgentSystemInterfaceInit:
    """Test AgentSystemInterface initialization with real kernel."""

    def test_init_creates_interface_with_kernel_and_agent_id(self):
        """Should initialize with kernel reference and agent_id."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        assert interface.kernel is kernel
        assert interface.agent_id == "test_agent"

    def test_init_creates_vfs_for_agent(self):
        """Should create VirtualFileSystem with agent_id."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "herald")

        assert interface.vfs is not None
        # VFS should be sandboxed to this agent
        sandbox_path = interface.get_sandbox_path()
        assert "herald" in str(sandbox_path)

    def test_init_creates_state_service_for_agent(self):
        """Should create StateService with agent_id namespace."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "civic")

        assert interface.state is not None

    def test_init_returns_empty_config_when_not_found(self):
        """Should return empty dict when agent config not found."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "unknown_agent")

        assert interface.config == {}


class TestDependencyManagement:
    """Test dependency management methods."""

    def test_get_dependencies_returns_list(self):
        """Should return list of dependencies from manager."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        deps = interface.get_dependencies()

        assert isinstance(deps, list)

    def test_has_dependency_returns_boolean(self):
        """Should return boolean for dependency check."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        result = interface.has_dependency("pytest")

        assert isinstance(result, bool)


class TestFilesystemVFS:
    """Test VFS (Virtual File System) methods with real VFS."""

    def test_write_and_read_file(self):
        """Should write and read files in sandbox."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        # Write file
        interface.write_file("test.txt", "Hello World")

        # Read file
        content = interface.read_file("test.txt")

        assert content == "Hello World"

    def test_file_exists_after_write(self):
        """Should report file exists after write."""
        # Use unique agent_id to avoid VFS sandbox bleeding between tests
        unique_id = f"test_agent_{uuid.uuid4().hex[:8]}"
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, unique_id)

        assert not interface.file_exists("new_file.txt")

        interface.write_file("new_file.txt", "content")

        assert interface.file_exists("new_file.txt")

    def test_list_files_returns_written_files(self):
        """Should list files that were written."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        interface.write_file("file1.txt", "content1")
        interface.write_file("file2.txt", "content2")

        files = interface.list_files(".")

        assert "file1.txt" in files
        assert "file2.txt" in files

    def test_open_file_context_manager(self):
        """Should support context manager for file operations."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        with interface.open_file("ctx_test.txt", "w") as f:
            f.write("via context manager")

        content = interface.read_file("ctx_test.txt")
        assert content == "via context manager"

    def test_get_sandbox_path_returns_path(self):
        """Should return Path object for sandbox."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "my_agent")

        path = interface.get_sandbox_path()

        assert isinstance(path, Path)
        assert "my_agent" in str(path)

    def test_read_nonexistent_file_raises(self):
        """Should raise FileNotFoundError for missing files."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        with pytest.raises(FileNotFoundError):
            interface.read_file("nonexistent.txt")


class TestConfiguration:
    """Test configuration methods."""

    def test_get_config_returns_default_for_missing_key(self):
        """Should return default value for missing key."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        result = interface.get_config("nonexistent_key", default="fallback")

        assert result == "fallback"

    def test_get_config_returns_none_by_default(self):
        """Should return None when key missing and no default provided."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        result = interface.get_config("missing")

        assert result is None

    def test_get_all_config_returns_dict(self):
        """Should return dict of all config."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        config = interface.get_all_config()

        assert isinstance(config, dict)


class TestKernelIntegration:
    """Test kernel integration methods with real kernel."""

    def test_record_event_returns_event_id(self):
        """Should record event and return event ID."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        event_id = interface.record_event("test_event", {"key": "value"})

        assert event_id is not None
        assert isinstance(event_id, str)

    def test_find_agents_by_capability(self):
        """Should find agents by capability."""
        kernel = TestKernel.minimal()

        # Register an agent with capability
        agent = TestAgents.with_capabilities("cap_agent", ["special_capability"])
        kernel.register_agent(agent, spawn_process=False)

        # Manually register manifest (normally done at kernel.boot())
        # kernel_impl.py is VISNU-protected, so we work around by registering
        # the manifest directly - this is what boot() does internally
        manifest = agent.get_manifest()
        kernel._manifest_registry.register(manifest)

        interface = AgentSystemInterface(kernel, "searcher")

        # Find agents with that capability - returns List[VibeAgent]
        results = interface.find_agents_by_capability("special_capability")

        assert len(results) == 1
        assert results[0].agent_id == "cap_agent"


class TestDataExchange:
    """Test inter-agent data exchange methods with real kernel."""

    def test_publish_and_request_data(self):
        """Should publish data and allow another agent to request it."""
        kernel = TestKernel.minimal()

        # Publisher agent
        publisher = AgentSystemInterface(kernel, "publisher")
        publisher.publish_data("citizens", ["alice", "bob"])

        # Requester agent
        requester = AgentSystemInterface(kernel, "requester")
        data = requester.request_data("publisher", "citizens")

        assert data == ["alice", "bob"]

    def test_request_data_with_default(self):
        """Should return default when data not found."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        result = interface.request_data("unknown_agent", "unknown_key", default=[])

        assert result == []

    def test_request_data_raises_without_default(self):
        """Should raise ValueError when data not found and no default."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        with pytest.raises(ValueError) as exc_info:
            interface.request_data("unknown_agent", "unknown_key")

        assert "has not published any data" in str(exc_info.value)

    def test_list_published_data(self):
        """Should list all published data keys."""
        kernel = TestKernel.minimal()

        # Publish some data
        publisher = AgentSystemInterface(kernel, "publisher")
        publisher.publish_data("key1", "value1")
        publisher.publish_data("key2", "value2")

        # List published data
        result = publisher.list_published_data("publisher")

        assert "publisher" in result
        assert "key1" in result["publisher"]
        assert "key2" in result["publisher"]


class TestCallAgent:
    """Test synchronous agent-to-agent calls."""

    def test_call_agent_raises_when_agent_not_found(self):
        """Should raise ValueError when target agent doesn't exist."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "caller")

        with pytest.raises(ValueError) as exc_info:
            interface.call_agent("nonexistent", {"action": "test"})

        assert "not found in registry" in str(exc_info.value)

    def test_call_agent_invokes_target(self):
        """Should invoke target agent's process method."""
        kernel = TestKernel.minimal()

        # Register target agent
        target = TestAgents.compliant("target_agent")
        kernel.register_agent(target, spawn_process=False)

        # Caller interface
        caller = AgentSystemInterface(kernel, "caller")

        # Call target
        result = caller.call_agent("target_agent", {"action": "test"})

        assert result is not None
        assert result.get("status") == "success"


class TestToolRegistry:
    """Test tool registry access methods."""

    def test_tools_property_returns_registry(self):
        """Should return kernel's tool_registry."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        registry = interface.tools

        assert registry is kernel.tool_registry


class TestEventBus:
    """Test event bus methods."""

    def test_subscribe_to_events(self):
        """Should subscribe to events and return subscription ID."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "subscriber")

        events_received = []

        def callback(event):
            events_received.append(event)

        sub_id = interface.subscribe_to_events(callback, "test.event")

        assert sub_id is not None

    def test_get_event_history(self):
        """Should get event history from kernel."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        # Record some events
        interface.record_event("history_test_1", {"n": 1})
        interface.record_event("history_test_2", {"n": 2})

        history = interface.get_event_history(limit=10)

        assert isinstance(history, list)


class TestPublishArtifact:
    """Test publish_artifact security with real kernel."""

    def test_publish_artifact_requires_capability(self):
        """Should raise PermissionError if agent lacks publish_root capability."""
        kernel = TestKernel.minimal()

        # Agent without publish_root capability
        agent = TestAgents.compliant("no_publish_agent")
        kernel.register_agent(agent, spawn_process=False)

        interface = AgentSystemInterface(kernel, "no_publish_agent")

        with pytest.raises(PermissionError) as exc_info:
            interface.publish_artifact("docs/README.md", "README.md")

        assert "not authorized to publish" in str(exc_info.value)

    def test_publish_artifact_with_capability(self):
        """Should allow publishing with publish_root capability."""
        kernel = TestKernel.permissive()  # Allows all operations

        # Agent with publish_root capability
        agent = TestAgents.with_capabilities("scribe", ["publish_root"])
        kernel.register_agent(agent, spawn_process=False)

        interface = AgentSystemInterface(kernel, "scribe")

        # Write a file to sandbox first
        interface.write_file("output.txt", "Published content")

        # Try to publish - with permissive kernel this should work
        with tempfile.TemporaryDirectory() as target_dir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(target_dir)

                result = interface.publish_artifact("output.txt", "published.txt")

                assert result is True
                assert Path("published.txt").exists()
            finally:
                os.chdir(original_cwd)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_multiple_interfaces_same_kernel(self):
        """Should support multiple interfaces on same kernel."""
        kernel = TestKernel.minimal()

        interface1 = AgentSystemInterface(kernel, "agent1")
        interface2 = AgentSystemInterface(kernel, "agent2")

        # Each has own VFS sandbox
        assert interface1.agent_id != interface2.agent_id
        assert interface1.get_sandbox_path() != interface2.get_sandbox_path()

    def test_data_isolation_between_agents(self):
        """Should isolate VFS data between agents."""
        kernel = TestKernel.minimal()

        interface1 = AgentSystemInterface(kernel, "agent1")
        interface2 = AgentSystemInterface(kernel, "agent2")

        # Write file as agent1
        interface1.write_file("private.txt", "agent1 data")

        # agent2 should not see agent1's files
        assert not interface2.file_exists("private.txt")

    def test_publish_data_overwrites(self):
        """Should overwrite previously published data with same key."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "publisher")

        interface.publish_data("counter", 1)
        interface.publish_data("counter", 2)

        result = interface.request_data("publisher", "counter")
        assert result == 2

    def test_write_nested_directory(self):
        """Should create nested directories when writing files."""
        kernel = TestKernel.minimal()
        interface = AgentSystemInterface(kernel, "test_agent")

        interface.write_file("deep/nested/path/file.txt", "nested content")

        content = interface.read_file("deep/nested/path/file.txt")
        assert content == "nested content"

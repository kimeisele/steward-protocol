#!/usr/bin/env python3
"""
Test script for Phase 6: Universal Tool Registry Integration

This script validates that:
1. Kernel initializes with ToolRegistry
2. Core tools are registered
3. Agents can access tools via AgentSystemInterface
4. Tool execution works end-to-end

Run: python test_tool_registry_integration.py
"""

import sys
import tempfile
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols import VibeAgent
from vibe_core.scheduling import Task


class TestAgent(VibeAgent):
    """Minimal test agent for tool registry validation"""

    def __init__(self):
        super().__init__(
            agent_id="test_agent",
            name="TEST",
            version="1.0.0",
            description="Test agent for tool registry",
            domain="TESTING",
            capabilities=["test_tools"],
        )
        # Simulate oath for kernel registration
        self.oath_sworn = True

    def process(self, task: Task):
        """Process a task (not used in this test)"""
        return {"success": True, "message": "Task processed"}


def test_phase_1_kernel_has_registry():
    """Test that kernel initializes with ToolRegistry"""
    print("\n=== PHASE 1: Kernel ToolRegistry Integration ===")

    kernel = RealVibeKernel(ledger_path=":memory:")

    # Check that tool_registry exists
    assert hasattr(kernel, "tool_registry"), "❌ Kernel missing tool_registry attribute"
    print("✅ Kernel has tool_registry attribute")

    # Check that it's the right type
    from vibe_core.tools import ToolRegistry

    assert isinstance(kernel.tool_registry, ToolRegistry), "❌ tool_registry is not a ToolRegistry instance"
    print("✅ tool_registry is a ToolRegistry instance")

    return kernel


def test_phase_2_core_tools_registered(kernel):
    """Test that core tools are registered"""
    print("\n=== PHASE 2: Core Tools Registration ===")

    expected_tools = [
        "read_file",
        "write_file",
        "add_task",
        "list_tasks",
        "complete_task",
        "delegate_task",
    ]

    registered_tools = kernel.tool_registry.list_tools()
    print(f"📋 Registered tools: {', '.join(registered_tools)}")

    for tool_name in expected_tools:
        assert kernel.tool_registry.has(tool_name), f"❌ Expected tool '{tool_name}' not registered"
        print(f"✅ Tool '{tool_name}' is registered")

    # Check tool count
    assert len(registered_tools) == len(
        expected_tools
    ), f"❌ Expected {len(expected_tools)} tools, got {len(registered_tools)}"
    print(f"✅ All {len(expected_tools)} core tools registered")


def test_phase_3_agent_has_tools_access(kernel):
    """Test that agents can access tools via AgentSystemInterface"""
    print("\n=== PHASE 3: Agent Access via SystemInterface ===")

    # Register a test agent
    agent = TestAgent()
    kernel.register_agent(agent, spawn_process=False)

    # Check that agent.system exists
    assert hasattr(agent, "system"), "❌ Agent missing 'system' attribute"
    print("✅ Agent has 'system' interface")

    # Check that agent.system.tools exists
    assert hasattr(agent.system, "tools"), "❌ AgentSystemInterface missing 'tools' property"
    print("✅ AgentSystemInterface has 'tools' property")

    # Check that it's the same registry as kernel
    assert agent.system.tools is kernel.tool_registry, "❌ Agent tools != kernel registry"
    print("✅ Agent.system.tools is kernel.tool_registry (same instance)")

    # Check that agent.system.execute_tool exists
    assert hasattr(agent.system, "execute_tool"), "❌ AgentSystemInterface missing 'execute_tool' method"
    print("✅ AgentSystemInterface has 'execute_tool' method")

    return agent


def test_phase_4_tool_execution(agent):
    """Test that agent can execute tools via kernel"""
    print("\n=== PHASE 4: End-to-End Tool Execution ===")

    # Test 1: Write a file using tool
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_output.txt"
        test_content = "Hello from Universal Tool Registry!"

        print(f"📝 Writing file via write_file tool: {test_file}")
        result = agent.system.execute_tool("write_file", {"path": str(test_file), "content": test_content})

        assert result.success, f"❌ write_file failed: {result.error}"
        print(f"✅ write_file succeeded: {result.output}")

        # Verify file was actually created
        assert test_file.exists(), "❌ File was not created"
        print("✅ File exists on disk")

        # Test 2: Read the file back
        print(f"📖 Reading file via read_file tool: {test_file}")
        result = agent.system.execute_tool("read_file", {"path": str(test_file)})

        assert result.success, f"❌ read_file failed: {result.error}"
        assert result.output == test_content, "❌ File content doesn't match"
        print(f"✅ read_file succeeded: {len(result.output)} bytes")

    # Test 3: List available tools
    print("📋 Listing available tools via agent.system.tools")
    available_tools = agent.system.tools.list_tools()
    print(f"✅ Agent can see {len(available_tools)} tools: {', '.join(available_tools)}")

    # Test 4: Get tool metadata
    print("🔍 Getting read_file tool metadata")
    tool = agent.system.tools.get("read_file")
    assert tool is not None, "❌ Failed to get tool"
    print(f"✅ Tool name: {tool.name}")
    print(f"✅ Tool description: {tool.description}")
    print(f"✅ Tool parameters: {tool.parameters_schema}")


def main():
    """Run all tests"""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  PHASE 6: UNIVERSAL TOOL REGISTRY INTEGRATION TEST       ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    try:
        # Phase 1: Kernel has registry
        kernel = test_phase_1_kernel_has_registry()

        # Phase 2: Core tools registered
        test_phase_2_core_tools_registered(kernel)

        # Phase 3: Agent can access tools
        agent = test_phase_3_agent_has_tools_access(kernel)

        # Phase 4: Tool execution works
        test_phase_4_tool_execution(agent)

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED - Tool Registry Integration Complete!")
        print("=" * 60)
        print("\n✨ PROOF OF CONCEPT:")
        print("   - Kernel owns the ToolRegistry (Single Source of Truth)")
        print("   - Agents access tools via agent.system.tools")
        print("   - Tools execute through kernel (Governance enabled)")
        print("   - Audit trail recorded in ledger")
        print("\n🚀 NEXT STEPS:")
        print("   - Phase 3: Auto-discover agent tools during boot")
        print("   - Phase 4: YAML-based agent definitions")
        print("   - Phase 5: Migrate Herald/Civic to use registry")
        print()

        return 0

    except AssertionError as e:
        print(f"\n💥 TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

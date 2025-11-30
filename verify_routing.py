import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steward.system_agents.envoy.cartridge_main import EnvoyCartridge
from vibe_core.operator_adapter import TerminalOperator, UniversalOperatorAdapter
from vibe_core.scheduling import Task


def verify_envoy_routing():
    print("\n🕵️ Verifying Envoy Routing...")

    # 1. Instantiate Envoy
    envoy = EnvoyCartridge()

    # 2. Mock System Interface
    envoy.system = MagicMock()
    envoy.system.get_sandbox_path.return_value = Path("/tmp/envoy_sandbox")

    # 3. Test 'status' command
    print("   Testing 'status' command...")
    task = Task(task_id="test-task-1", agent_id="envoy", payload={"command": "status"})

    # Mock tool execution result
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.output = {"status": "RUNNING", "agents": 10}
    envoy.system.execute_tool.return_value = mock_result

    result = envoy.process(task)

    # Verify
    if result == {"status": "RUNNING", "agents": 10}:
        print("   ✅ 'status' routed correctly")
    else:
        print(f"   ❌ 'status' failed: {result}")

    # Verify tool call
    envoy.system.execute_tool.assert_called_with("envoy.city_control", {"action": "get_city_status"})

    # 4. Test 'vote' command
    print("   Testing 'vote' command...")
    task = Task(
        task_id="test-task-2",
        agent_id="envoy",
        payload={"command": "vote", "args": {"proposal_id": "prop-1", "choice": "YES"}},
    )

    envoy.process(task)
    envoy.system.execute_tool.assert_called_with(
        "envoy.city_control", {"action": "vote_proposal", "proposal_id": "prop-1", "choice": "YES", "voter": "operator"}
    )
    print("   ✅ 'vote' routed correctly")


def verify_operator_adapter():
    print("\n🔌 Verifying Operator Adapter...")

    adapter = UniversalOperatorAdapter()

    # Check default registration
    # Note: DegradedOperator is registered by default

    # Register Terminal Operator
    term_op = TerminalOperator()
    adapter.register_operator(term_op, priority=1)

    # Verify selection
    # We can't easily test async methods without an event loop, but we can check the logic
    # Mock is_available to control selection

    term_op.is_available = MagicMock(return_value=True)

    best_op = adapter._select_best_operator()
    if best_op == term_op:
        print("   ✅ Selected TerminalOperator (Priority 1)")
    else:
        print(f"   ❌ Failed to select TerminalOperator: {best_op}")

    # Test degradation
    term_op.is_available.return_value = False
    best_op = adapter._select_best_operator()
    if best_op.__class__.__name__ == "DegradedOperator":
        print("   ✅ Degraded to DegradedOperator (Fallback)")
    else:
        print(f"   ❌ Failed to degrade: {best_op}")


if __name__ == "__main__":
    try:
        verify_envoy_routing()
        verify_operator_adapter()
        print("\n✨ Phase 2 Verification Complete")
    except Exception as e:
        print(f"\n❌ Verification Failed: {e}")
        import traceback

        traceback.print_exc()

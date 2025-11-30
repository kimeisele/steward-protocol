import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from vibe_core.tool_discovery import ToolDiscovery
from vibe_core.tools.tool_registry import ToolRegistry


def verify_tools():
    print("🔍 Starting Tool Verification...")

    # 1. Discovery
    discovery = ToolDiscovery(root_path=project_root)
    tools = discovery.discover_all_tools()

    print(f"\n✅ Discovered {len(tools)} tools.")

    # 2. Registration
    registry = ToolRegistry()
    for tool in tools:
        try:
            registry.register(tool)
            print(f"  - Registered: {tool.name}")
        except Exception as e:
            print(f"  ❌ Failed to register {tool.name}: {e}")

    # 3. Dry Run (Test a core tool if available, or just list)
    print(f"\n📊 Registry contains {len(registry)} tools.")

    # Check for specific expected tools
    expected_tools = [
        "read_file",
        "write_file",
    ]  # Core tools might not be discovered by ToolDiscovery if they are manually registered in kernel

    # Let's check if we can instantiate and run a discovered tool
    # We'll look for a simple one, e.g. from science agent

    science_tools = [t for t in tools if "science" in t.name]
    if science_tools:
        print(f"\n🔬 Found {len(science_tools)} science tools.")
        for t in science_tools:
            print(f"   - {t.name}: {t.description}")

    return len(tools)


if __name__ == "__main__":
    verify_tools()

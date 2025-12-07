import os
import sys
from unittest.mock import MagicMock, PropertyMock

# Add project root to path
sys.path.append(os.getcwd())

from vibe_core.plugins.interface.renderers.agents import AgentsRenderer
from vibe_core.plugins.interface.renderers.citymap import CityMapRenderer
from vibe_core.plugins.interface.renderers.help import HelpRenderer
from vibe_core.plugins.interface.renderers.index import IndexRenderer
from vibe_core.plugins.interface.renderers.rag import RagRenderer


def test_renderers():
    print("🧪 Verifying Plugin-First Renderers...")

    # Mock Kernel
    kernel = MagicMock()

    # Mock IO
    kernel.io = MagicMock()

    # Mock Registry
    agent1 = MagicMock()
    agent1.name = "TestAgent"
    agent1.domain = "TEST"
    agent1.capabilities = ["test"]
    kernel.agent_registry = {"test_agent": agent1}

    # Mock Tools
    kernel.tool_registry.list_tools.return_value = ["test_agent.tool1"]

    # Mock Status
    type(kernel.status).value = PropertyMock(return_value="RUNNING")

    # Test AgentsRenderer
    print("  - Testing AgentsRenderer...")
    r_agents = AgentsRenderer(kernel)
    r_agents.render()
    kernel.io.write_document.assert_called()
    args = kernel.io.write_document.call_args[1]
    assert args["name"] == "AGENTS.md"
    assert "TestAgent" in args["content"]
    print("    ✅ AGENTS.md rendered")

    # Test CityMapRenderer
    print("  - Testing CityMapRenderer...")
    r_city = CityMapRenderer(kernel)
    r_city.render()
    args = kernel.io.write_document.call_args[1]
    assert args["name"] == "CITYMAP.md"
    assert "TEST" in args["content"]  # Domain
    print("    ✅ CITYMAP.md rendered")

    # Test HelpRenderer
    print("  - Testing HelpRenderer...")
    r_help = HelpRenderer(kernel)
    r_help.render()
    args = kernel.io.write_document.call_args[1]
    assert args["name"] == "HELP.md"
    assert "System Diagnostics" in args["content"]
    print("    ✅ HELP.md rendered")

    # Test IndexRenderer
    print("  - Testing IndexRenderer...")
    r_index = IndexRenderer(kernel)
    # Mock scan
    r_index._scan_docs_directories = MagicMock()
    r_index.render()
    args = kernel.io.write_document.call_args[1]
    assert args["name"] == "INDEX.md"
    assert "DOCUMENTATION INDEX" in args["content"]
    print("    ✅ INDEX.md rendered")

    # Test RagRenderer
    print("  - Testing RagRenderer...")
    r_rag = RagRenderer(kernel)
    r_rag.render()
    args = kernel.io.write_document.call_args[1]
    assert args["name"] == "RAG.md"
    assert "Realtime Architecture Guide" in args["content"]
    print("    ✅ RAG.md rendered")

    print("🎉 All renderers verified successfully!")


if __name__ == "__main__":
    test_renderers()

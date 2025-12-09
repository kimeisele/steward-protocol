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
    content = r_agents.generate_content()
    assert content is not None
    assert "AGENTS.md" == r_agents.output_file
    assert "TestAgent" in content
    print("    ✅ AGENTS.md rendered")

    # Test CityMapRenderer
    print("  - Testing CityMapRenderer...")
    r_city = CityMapRenderer(kernel)
    content = r_city.generate_content()
    assert content is not None
    assert "CITYMAP.md" == r_city.output_file
    assert "TEST" in content  # Domain
    print("    ✅ CITYMAP.md rendered")

    # Test HelpRenderer
    print("  - Testing HelpRenderer...")
    r_help = HelpRenderer(kernel)
    content = r_help.generate_content()
    assert content is not None
    assert "HELP.md" == r_help.output_file
    assert "System Diagnostics" in content
    print("    ✅ HELP.md rendered")

    # Test IndexRenderer
    print("  - Testing IndexRenderer...")
    r_index = IndexRenderer(kernel)
    # Mock scan
    r_index._scan_docs_directories = MagicMock()
    content = r_index.generate_content()
    assert content is not None
    assert "INDEX.md" == r_index.output_file
    assert "DOCUMENTATION INDEX" in content
    print("    ✅ INDEX.md rendered")

    # Test RagRenderer
    print("  - Testing RagRenderer...")
    r_rag = RagRenderer(kernel)
    content = r_rag.generate_content()
    assert content is not None
    assert "RAG.md" == r_rag.output_file
    assert "Realtime Architecture Guide" in content
    print("    ✅ RAG.md rendered")

    print("🎉 All renderers verified successfully!")


if __name__ == "__main__":
    test_renderers()

import logging
from typing import Any, Optional

import pytest

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.universal.read_write import ReadResult, ReadWriteProtocol, SovereignContext
from vibe_core.scripts.sudarshana import MantraBase, MantraReadWrite, fractalize_registry

# Setup logging
logging.basicConfig(level=logging.INFO)


class DummyReadWrite:
    """A Dummy Service implementing ReadWriteProtocol."""

    def read(self, key: str, context: Optional[SovereignContext] = None) -> ReadResult:
        return ReadResult(value=f"value_of_{key}", writer=None)

    def write(self, key: str, value: Any, context: Optional[SovereignContext] = None) -> None:
        pass

    def exists(self, key: str, context: Optional[SovereignContext] = None) -> bool:
        return True


@pytest.fixture(autouse=True)
def clean_registry():
    ServiceRegistry.reset()
    yield
    ServiceRegistry.reset()


def test_sudarshana_fractalization(caplog):
    """
    Verify that Sudarshana wraps services implementing Universal Protocols.
    """
    caplog.set_level(logging.INFO)

    # 1. Register a pure service
    dummy = DummyReadWrite()
    ServiceRegistry.register(ReadWriteProtocol, dummy)

    # Verify it is raw initially
    retrieved = ServiceRegistry.get(ReadWriteProtocol)
    assert retrieved is dummy
    assert not isinstance(retrieved, MantraBase)

    # 2. Fractalize (Throw the Discus)
    fractalize_registry()

    # 3. Verify it is now wrapped
    wrapped = ServiceRegistry.get(ReadWriteProtocol)
    assert wrapped is not dummy
    assert isinstance(wrapped, MantraBase)
    assert isinstance(wrapped, MantraReadWrite)

    # 4. Verify Resonance
    wrapped.read("test_key")

    # Logs should show Mantra
    assert "🕉️  [MANTRA] SYS_WAKE" in caplog.text
    assert "Cycle: HARE KRISHNA" in caplog.text


# --- Tool Test ---
from vibe_core.tools.tool_protocol import Tool, ToolResult
from vibe_core.unified_registry import ToolCapabilityAdapter, UnifiedRegistry


class DummyTool(Tool):
    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "does nothing"

    @property
    def parameters_schema(self) -> dict:
        return {}

    def validate(self, p):
        pass

    def execute(self, p) -> ToolResult:
        return ToolResult(success=True)


from vibe_core.scripts.sudarshana import MantraTool, fractalize_capabilities


def test_sudarshana_tool_fractalization(caplog):
    """
    Verify that Sudarshana wraps Tools in UnifiedRegistry.
    """
    caplog.set_level(logging.INFO)

    # 1. Setup Registry with Dummy Tool
    registry = UnifiedRegistry.get_instance()
    registry._discovered = True  # Prevent discover_all from clearing our dummy
    # Manually inject (avoiding discovery complexity for unit test)
    tool = DummyTool()
    adapter = ToolCapabilityAdapter(tool=tool)
    registry._capabilities["dummy_tool"] = adapter

    # Verify raw initially
    assert registry.get("dummy_tool").tool is tool
    assert not isinstance(registry.get("dummy_tool").tool, MantraBase)

    # 2. Fractalize Capabilities
    fractalize_capabilities()

    # 3. Verify Wrapped
    wrapped_adapter = registry.get("dummy_tool")
    wrapped_tool = wrapped_adapter.tool
    assert wrapped_tool is not tool
    assert isinstance(wrapped_tool, MantraTool)
    assert isinstance(wrapped_tool, MantraBase)

    # 4. Verify Resonance
    wrapped_adapter.execute({})

    # Logs should show Mantra EXEC_SERVICE
    assert "🕉️  [MANTRA] EXEC_SERVICE" in caplog.text
    assert "Cycle: HARE KRISHNA" in caplog.text


if __name__ == "__main__":
    ServiceRegistry.reset()
    test_sudarshana_fractalization(logging.getLogger())
    print("Test passed manually.")

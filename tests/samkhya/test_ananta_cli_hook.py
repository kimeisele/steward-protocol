from typing import Any, List

import pytest

from vibe_core.naga.hooks.ananta_cli import AnantaCLIHook
from vibe_core.protocols.cli_execution import (
    CLICapabilityToken,
    CLIExecutionContext,
    CLIExecutionPhase,
    CLIPermissionLevel,
)
from vibe_core.protocols.naga.ananta import AnantaProtocol, FloodProposal, VetoDecision


# --- FAKE ANANTA (No Mocks) ---
class FakeAnanta:
    """
    Fake implementation of Ananta that supports flood_instance.
    Implements both AnantaProtocol and IAnantaBridge logic for testing.
    """

    def __init__(self):
        self.flooded_instances = []

    def flood_instance(self, instance: Any, genes: List[str], authorization: Any = None) -> Any:
        self.flooded_instances.append((instance, genes))
        # Simulate flood by setting a flag
        instance.is_flooded = True
        return instance

    # AnantaProtocol stubs
    def analyze_service(self, service_class: type) -> FloodProposal:
        return None

    def request_approval(self, proposal: FloodProposal) -> VetoDecision:
        return None

    def create_flooded_class(self, original: type, decision: VetoDecision) -> type:
        return original

    def get_mixin_for_naga(self, name: str) -> Any:
        return None

    def list_available_mixins(self) -> List[str]:
        return []

    def get_flood_history(self) -> List[VetoDecision]:
        return []

    def get_status(self) -> Any:
        return None


class DummyHandler:
    pass


class TestAnantaCLIHook:
    """Test the Ananta CLI Hook (The Flood Gate)."""

    def test_flood_at_pre_execute(self):
        """Test that handler is flooded at PRE_EXECUTE phase."""
        ananta = FakeAnanta()
        hook = AnantaCLIHook(ananta)

        handler = DummyHandler()
        token = CLICapabilityToken.create_anonymous()
        context = CLIExecutionContext(
            command_name="test", namespace="cli", args=[], capability_token=token, handler=handler
        )

        # Run Hook
        result = hook.on_phase(CLIExecutionPhase.PRE_EXECUTE, context)

        # Assertions
        assert result["allow"] is True
        assert len(ananta.flooded_instances) == 1
        assert ananta.flooded_instances[0][0] == handler
        assert getattr(handler, "is_flooded", False) is True

    def test_ignore_other_phases(self):
        """Test that other phases are ignored."""
        ananta = FakeAnanta()
        hook = AnantaCLIHook(ananta)

        handler = DummyHandler()
        token = CLICapabilityToken.create_anonymous()
        context = CLIExecutionContext(
            command_name="test", namespace="cli", args=[], capability_token=token, handler=handler
        )

        # Run Hook at POST_VALIDATE
        result = hook.on_phase(CLIExecutionPhase.POST_VALIDATE, context)

        # Assertions
        assert result["allow"] is True
        assert len(ananta.flooded_instances) == 0

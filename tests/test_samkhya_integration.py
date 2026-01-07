from pathlib import Path
from typing import Any

import pytest

# Migrated Classes
from vibe_core.config.schema import CityConfig, GovernanceConfig
from vibe_core.ouroboros.sync import CISyncService
from vibe_core.plugins.opus_assistant.manas.intent_router import IntentRouter
from vibe_core.plugins.opus_assistant.manas.triggers import SynapticMemory

# Protocols
from vibe_core.protocols.universal import (
    EnforceProtocol,
    InferProtocol,
    ReadWriteProtocol,
    StoreRecallProtocol,
    SyncProtocol,
)
from vibe_core.services.capability_enforcer import CapabilityEnforcerService


@pytest.mark.unit
class TestSamkhyaIntegration:
    """
    Verifies that the Core Systems have truly evolved into SAMKHYA Atomic Protocols.
    """

    def test_config_evolved_to_read_write(self):
        """Verify CityConfig implements ReadWriteProtocol."""
        config = CityConfig()
        assert isinstance(config, ReadWriteProtocol)

        # Test Dot Notation Access (Read)
        assert config.read("governance.voting_threshold") == 0.5
        assert config.read("agents.herald.content_style") == "cyberpunk_professional"

        # Test Write
        config.write("governance.voting_threshold", 0.9)
        assert config.read("governance.voting_threshold") == 0.9

        # Test Exists
        assert config.exists("governance.voting_threshold")
        assert not config.exists("governance.fake_param")

    def test_sync_service_evolved(self):
        """Verify CISyncService implements SyncProtocol."""
        sync = CISyncService(repo="test/repo")
        assert isinstance(sync, SyncProtocol)

        # Check method existence (runtime check)
        assert hasattr(sync, "sync")
        assert hasattr(sync, "get_sync_status")
        assert hasattr(sync, "is_synced")

    def test_enforcer_evolved(self):
        """Verify CapabilityEnforcerService implements EnforceProtocol."""
        enforcer = CapabilityEnforcerService()
        assert isinstance(enforcer, EnforceProtocol)

        # Check rule retrieval
        rules = enforcer.get_rules()
        assert len(rules) > 0
        assert rules[0].verdict.value == "allow"  # Should allow system identities

    def test_intent_router_evolved(self):
        """Verify IntentRouter implements InferProtocol."""
        # Simple constructor mock for dependencies
        router = IntentRouter(workspace=Path("/tmp/test"))
        assert isinstance(router, InferProtocol)

        # Check methods
        assert hasattr(router, "infer")
        assert hasattr(router, "classify")
        assert hasattr(router, "evaluate")

    def test_synaptic_memory_evolved(self):
        """Verify SynapticMemory implements StoreRecallProtocol."""
        # Mock workspace
        memory = SynapticMemory(workspace=Path("/tmp/test"))
        assert isinstance(memory, StoreRecallProtocol)

        # Check methods
        assert hasattr(memory, "store")
        assert hasattr(memory, "recall")
        assert hasattr(memory, "forget")

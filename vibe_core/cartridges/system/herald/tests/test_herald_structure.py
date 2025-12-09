from vibe_core.cartridges.system.herald.cartridge_main import HeraldCartridge


def test_herald_initialization():
    """Verify HeraldCartridge initializes correctly."""
    agent = HeraldCartridge()
    assert agent.agent_id == "herald"
    assert "broadcast" in agent.capabilities

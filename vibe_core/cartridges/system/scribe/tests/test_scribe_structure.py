from vibe_core.cartridges.system.scribe.cartridge_main import ScribeCartridge


def test_scribe_initialization():
    """Verify ScribeCartridge initializes correctly."""
    agent = ScribeCartridge()
    assert agent.agent_id == "scribe"
    assert "scribe" in agent.agent_id

from vibe_core.protocols import VibeAgent


def test_compliant_agent_fixture_config(compliant_agent):
    """
    Verify that compliant_agent fixture is loaded from quality.yaml config.
    Target ID Prefix: 'test-compliant' (from config/quality.yaml)
    """
    assert isinstance(compliant_agent, VibeAgent)
    assert compliant_agent.agent_id.startswith("test-compliant")
    # Verify defaults from config
    assert "governance" in compliant_agent.capabilities
    assert "task_execution" in compliant_agent.capabilities
    assert getattr(compliant_agent, "oath_sworn", False) is True


def test_no_oath_agent_fixture_config(no_oath_agent):
    """
    Verify no_oath_agent fixture from config.
    Target ID Prefix: 'test-no-oath'
    """
    assert no_oath_agent.agent_id.startswith("test-no-oath")
    assert not hasattr(no_oath_agent, "oath_sworn")


def test_false_oath_agent_config(false_oath_agent):
    """
    Verify false_oath_agent fixture from config.
    Target ID Prefix: 'test-false-oath'
    """
    assert false_oath_agent.agent_id.startswith("test-false-oath")
    assert getattr(false_oath_agent, "oath_sworn", True) is False


def test_kernels_boot(test_kernel, permissive_kernel, governance_kernel):
    """Verify all kernel fixtures instantiate correctly."""
    assert test_kernel is not None
    assert permissive_kernel is not None
    assert governance_kernel is not None

"""
TEST: ForumCartridge - The Town Hall (Democratic Decision Layer)
================================================================
Target: forum/cartridge_main.py
Standard: GAD-5000
"""

import pytest

from vibe_core.cartridges.system.forum.cartridge_main import ForumCartridge


class TestForumCartridgeInit:
    """Test ForumCartridge initialization."""

    def test_cartridge_can_be_instantiated(self):
        """Should instantiate without errors."""
        cartridge = ForumCartridge()
        assert cartridge is not None

    def test_cartridge_has_correct_agent_id(self):
        """Should have correct agent_id."""
        cartridge = ForumCartridge()
        assert cartridge.agent_id == "forum"

    def test_cartridge_has_correct_name(self):
        """Should have correct name."""
        cartridge = ForumCartridge()
        assert cartridge.name == "FORUM"

    def test_cartridge_has_version(self):
        """Should have version string."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "version")
        assert cartridge.version == "1.0.0"

    def test_cartridge_has_governance_capabilities(self):
        """Should have governance and voting capabilities."""
        cartridge = ForumCartridge()
        assert len(cartridge.capabilities) > 0
        assert "governance" in cartridge.capabilities
        assert "voting" in cartridge.capabilities

    def test_cartridge_domain_is_governance(self):
        """Should have GOVERNANCE domain."""
        cartridge = ForumCartridge()
        assert cartridge.domain == "GOVERNANCE"

    def test_cartridge_has_oath_sworn(self):
        """Should have sworn constitutional oath."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "oath_sworn")
        assert cartridge.oath_sworn is True


class TestForumManifest:
    """Test get_manifest method."""

    def test_manifest_method_exists(self):
        """Should have get_manifest method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "get_manifest")
        assert callable(cartridge.get_manifest)

    def test_manifest_returns_agent_manifest(self):
        """Should return AgentManifest instance."""
        from vibe_core.protocols import AgentManifest

        cartridge = ForumCartridge()
        manifest = cartridge.get_manifest()
        assert isinstance(manifest, AgentManifest)

    def test_manifest_has_correct_agent_id(self):
        """Should return manifest with correct agent_id."""
        cartridge = ForumCartridge()
        manifest = cartridge.get_manifest()
        assert manifest.agent_id == "forum"


class TestForumReportStatus:
    """Test report_status method."""

    def test_report_status_exists(self):
        """Should have report_status method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "report_status")
        assert callable(cartridge.report_status)

    @pytest.mark.skip(reason="Requires system interface for sandbox path access")
    def test_report_status_returns_dict(self):
        """Should return status dict when connected to kernel."""
        cartridge = ForumCartridge()
        status = cartridge.report_status()
        assert isinstance(status, dict)


class TestForumProposalMethods:
    """Test proposal-related methods."""

    def test_create_proposal_method_exists(self):
        """Should have create_proposal method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "create_proposal")
        assert callable(cartridge.create_proposal)

    def test_submit_vote_method_exists(self):
        """Should have submit_vote method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "submit_vote")
        assert callable(cartridge.submit_vote)

    def test_check_quorum_method_exists(self):
        """Should have check_quorum method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "check_quorum")
        assert callable(cartridge.check_quorum)

    def test_approve_proposal_method_exists(self):
        """Should have approve_proposal method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "approve_proposal")
        assert callable(cartridge.approve_proposal)

    def test_execute_proposal_method_exists(self):
        """Should have execute_proposal method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "execute_proposal")
        assert callable(cartridge.execute_proposal)

    def test_get_proposal_method_exists(self):
        """Should have get_proposal method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "get_proposal")
        assert callable(cartridge.get_proposal)

    def test_list_proposals_method_exists(self):
        """Should have list_proposals method."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "list_proposals")
        assert callable(cartridge.list_proposals)


class TestForumProposalState:
    """Test proposal state management."""

    def test_proposals_dict_exists(self):
        """Should have proposals dictionary."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "proposals")
        assert isinstance(cartridge.proposals, dict)

    def test_next_proposal_id_exists(self):
        """Should have next_proposal_id counter."""
        cartridge = ForumCartridge()
        assert hasattr(cartridge, "next_proposal_id")
        assert cartridge.next_proposal_id >= 1

"""
OPUS-047: MUKHA (Das Gesicht) - System Identity Tests.

Sanskrit: Mukha = Face / Mouth / Gateway.

These tests verify:
1. System introspection works
2. Agent manifests are parsed correctly
3. README generation produces valid output
"""

import json
from pathlib import Path

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.mukha import (
    AgentIdentity,
    IdentityScanner,
    MukhaGenerator,
    SystemIdentity,
)

# =============================================================================
# TEST: AgentIdentity
# =============================================================================


class TestAgentIdentity:
    """Tests for AgentIdentity dataclass."""

    def test_agent_identity_creation(self):
        """Test creating an agent identity."""
        agent = AgentIdentity(
            agent_id="test_agent",
            name="TEST_AGENT",
            domain="TESTING",
            description="A test agent",
            version="1.0.0",
            capabilities=["cap1", "cap2"],
            operations=[{"name": "op1"}, {"name": "op2"}],
            risk_level="LOW",
            manifest_path="test/steward.json",
        )

        assert agent.agent_id == "test_agent"
        assert agent.name == "TEST_AGENT"
        assert len(agent.capabilities) == 2
        assert len(agent.operations) == 2

    def test_agent_identity_to_dict(self):
        """Test serialization."""
        agent = AgentIdentity(
            agent_id="test",
            name="TEST",
            domain="TEST",
            description="Test",
            version="1.0.0",
            capabilities=["a", "b"],
            operations=[{"name": "x"}],
            risk_level="LOW",
            manifest_path="test.json",
        )

        d = agent.to_dict()
        assert d["agent_id"] == "test"
        assert d["capabilities"] == ["a", "b"]
        assert d["operations"] == ["x"]


# =============================================================================
# TEST: IdentityScanner
# =============================================================================


class TestIdentityScanner:
    """Tests for IdentityScanner."""

    @pytest.fixture
    def scanner(self, tmp_path):
        """Create scanner with temp workspace."""
        return IdentityScanner(workspace=tmp_path)

    def test_scanner_initialization(self, scanner, tmp_path):
        """Test scanner initializes correctly."""
        assert scanner._workspace == tmp_path

    def test_scan_empty_workspace(self, scanner):
        """Test scanning empty workspace."""
        identity = scanner.scan()

        assert identity.project_name == "steward-protocol"
        assert identity.total_agents == 0

    def test_scan_with_system_agents(self, tmp_path):
        """Test scanning workspace with system agents."""
        # Create system cartridge
        system_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "test_agent"
        system_dir.mkdir(parents=True)

        manifest = {
            "identity": {"agent_id": "test_agent", "name": "TEST_AGENT"},
            "specs": {
                "domain": "TESTING",
                "description": "A test agent",
                "capabilities": ["test"],
            },
            "operations": [{"name": "do_test"}],
            "governance": {"risk_level": "LOW"},
        }
        (system_dir / "steward.json").write_text(json.dumps(manifest))

        scanner = IdentityScanner(workspace=tmp_path)
        identity = scanner.scan()

        assert len(identity.system_agents) == 1
        assert identity.system_agents[0].agent_id == "test_agent"
        assert identity.system_agents[0].domain == "TESTING"

    def test_scan_with_city_agents(self, tmp_path):
        """Test scanning workspace with city agents."""
        # Create city cartridge
        city_dir = tmp_path / "vibe_core" / "cartridges" / "agent_city" / "citizen"
        city_dir.mkdir(parents=True)

        manifest = {
            "identity": {"agent_id": "citizen", "name": "CITIZEN"},
            "specs": {"domain": "CITIZEN", "description": "A citizen agent"},
        }
        (city_dir / "steward.json").write_text(json.dumps(manifest))

        scanner = IdentityScanner(workspace=tmp_path)
        identity = scanner.scan()

        assert len(identity.city_agents) == 1
        assert identity.city_agents[0].agent_id == "citizen"

    def test_scan_plugins(self, tmp_path):
        """Test scanning plugins directory."""
        # Create plugin with MANAS
        plugin_dir = tmp_path / "vibe_core" / "plugins" / "test_plugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "manas").mkdir()
        (plugin_dir / "cortex").mkdir()

        scanner = IdentityScanner(workspace=tmp_path)
        identity = scanner.scan()

        assert len(identity.plugins) == 1
        assert identity.plugins[0].name == "test_plugin"
        assert identity.plugins[0].has_manas is True
        assert "manas" in identity.plugins[0].submodules
        assert "cortex" in identity.plugins[0].submodules

    def test_statistics_calculated(self, tmp_path):
        """Test that statistics are correctly calculated."""
        # Create agent with capabilities
        system_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "agent1"
        system_dir.mkdir(parents=True)

        manifest = {
            "identity": {"agent_id": "agent1"},
            "specs": {"domain": "TEST", "description": "Test", "capabilities": ["a", "b", "c"]},
            "operations": [{"name": "x"}, {"name": "y"}],
        }
        (system_dir / "steward.json").write_text(json.dumps(manifest))

        scanner = IdentityScanner(workspace=tmp_path)
        identity = scanner.scan()

        assert identity.total_agents == 1
        assert identity.total_capabilities == 3
        assert identity.total_operations == 2


# =============================================================================
# TEST: MukhaGenerator
# =============================================================================


class TestMukhaGenerator:
    """Tests for MukhaGenerator."""

    @pytest.fixture
    def generator(self, tmp_path):
        """Create generator with temp workspace."""
        return MukhaGenerator(workspace=tmp_path)

    def test_generator_initialization(self, generator, tmp_path):
        """Test generator initializes correctly."""
        assert generator._workspace == tmp_path
        assert generator._scanner is not None

    def test_generate_readme_empty(self, generator):
        """Test generating README for empty workspace."""
        readme = generator.generate_readme()

        assert "STEWARD Protocol" in readme
        assert "MUKHA" in readme
        assert "Total Agents" in readme

    def test_generate_readme_with_agents(self, tmp_path):
        """Test generating README with agents."""
        # Create system agent
        system_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "oracle"
        system_dir.mkdir(parents=True)

        manifest = {
            "identity": {"agent_id": "oracle", "name": "ORACLE"},
            "specs": {"domain": "KNOWLEDGE", "description": "Wisdom provider"},
        }
        (system_dir / "steward.json").write_text(json.dumps(manifest))

        generator = MukhaGenerator(workspace=tmp_path)
        readme = generator.generate_readme()

        assert "oracle" in readme.lower()
        assert "KNOWLEDGE" in readme

    def test_readme_contains_architecture(self, generator):
        """Test README contains architecture diagram."""
        readme = generator.generate_readme()

        assert "MANAS" in readme
        assert "JNANA" in readme
        assert "KRIYA" in readme
        assert "SAMVADA" in readme
        assert "VAK" in readme

    def test_readme_contains_documentation_links(self, generator):
        """Test README contains documentation links."""
        readme = generator.generate_readme()

        assert "OPUS.md" in readme
        assert "INDEX.md" in readme
        assert "CONSTITUTION.md" in readme

    def test_update_readme_creates_file(self, tmp_path):
        """Test update_readme creates the file."""
        generator = MukhaGenerator(workspace=tmp_path)
        path = generator.update_readme()

        assert path.exists()
        assert path.name == "README.md"
        content = path.read_text()
        assert "STEWARD Protocol" in content

    def test_update_readme_archives_old(self, tmp_path):
        """Test update_readme archives existing README."""
        # Create existing README
        old_readme = tmp_path / "README.md"
        old_readme.write_text("# Old README\n\nThis is the old content.")

        generator = MukhaGenerator(workspace=tmp_path)
        generator.update_readme()

        # Check archive was created
        archive_dir = tmp_path / "docs" / "archive"
        assert archive_dir.exists()

        archives = list(archive_dir.glob("README_*.md"))
        assert len(archives) == 1
        assert "Old README" in archives[0].read_text()


# =============================================================================
# TEST: SystemIdentity
# =============================================================================


class TestSystemIdentity:
    """Tests for SystemIdentity dataclass."""

    def test_system_identity_creation(self):
        """Test creating system identity."""
        identity = SystemIdentity(
            project_name="test",
            version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
        )

        assert identity.project_name == "test"
        assert identity.total_agents == 0
        assert identity.manas_tests == 0

    def test_system_identity_to_dict(self):
        """Test serialization."""
        identity = SystemIdentity(
            project_name="test",
            version="1.0.0",
            generated_at="2024-01-01T00:00:00Z",
            total_agents=5,
            total_capabilities=10,
        )

        d = identity.to_dict()
        assert d["project_name"] == "test"
        assert d["statistics"]["total_agents"] == 5
        assert d["statistics"]["total_capabilities"] == 10


# =============================================================================
# TEST: Integration with Real Workspace
# =============================================================================


class TestRealWorkspaceIntegration:
    """Integration tests with real workspace (if available)."""

    @pytest.fixture
    def real_workspace(self):
        """Get real workspace path."""
        # Try to find real workspace
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / "vibe_core").exists():
                return parent
        pytest.skip("Real workspace not found")

    def test_scan_real_workspace(self, real_workspace):
        """Test scanning real workspace."""
        scanner = IdentityScanner(workspace=real_workspace)
        identity = scanner.scan()

        # Should find agents
        assert identity.total_agents > 0
        assert len(identity.system_agents) > 0 or len(identity.city_agents) > 0

    def test_generate_real_readme(self, real_workspace):
        """Test generating README for real workspace."""
        generator = MukhaGenerator(workspace=real_workspace)
        readme = generator.generate_readme()

        # Should contain real agent names
        assert "envoy" in readme.lower() or "oracle" in readme.lower()
        assert len(readme) > 1000  # Should be substantial

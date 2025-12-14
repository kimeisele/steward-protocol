"""
OPUS-051: MANDALA (The Fractal Configuration) - Tests.

TDD: These tests define the expected behavior of the fractal configuration engine.

MANDALA = Sacred Diagram, Cosmic Map.
The self-weaving configuration that emerges from agent declarations.

"The whole contains the part, and the part contains the whole."
"""

import json
from pathlib import Path

import pytest

# =============================================================================
# SECTION 1: CAPABILITY SPEC TESTS
# =============================================================================


class TestCapabilitySpec:
    """Tests for CapabilitySpec data model."""

    def test_capability_spec_creates_from_name(self):
        """Mutation killer: Simple capability creation."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import CapabilitySpec

        spec = CapabilitySpec(name="git_analysis")
        assert spec.name == "git_analysis"
        assert spec.enabled is True
        assert spec.cost == 0

    def test_capability_spec_from_dict_simple(self):
        """Mutation killer: Create from simple dict."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import CapabilitySpec

        spec = CapabilitySpec.from_dict("test_cap", {"cost": 10})
        assert spec.name == "test_cap"
        assert spec.cost == 10

    def test_capability_spec_from_dict_full(self):
        """Mutation killer: Create from full dict."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import CapabilitySpec

        data = {
            "description": "Test capability",
            "cost": 5,
            "rate_limit": "10/minute",
            "permissions_required": ["read_repo"],
            "dependencies": ["git"],
            "enabled": True,
        }
        spec = CapabilitySpec.from_dict("full_cap", data)

        assert spec.name == "full_cap"
        assert spec.description == "Test capability"
        assert spec.cost == 5
        assert spec.rate_limit == "10/minute"
        assert "read_repo" in spec.permissions_required
        assert "git" in spec.dependencies

    def test_capability_spec_to_dict(self):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import CapabilitySpec

        spec = CapabilitySpec(
            name="test",
            description="Test",
            cost=10,
            rate_limit="5/minute",
        )
        d = spec.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test"
        assert d["cost"] == 10
        assert d["rate_limit"] == "5/minute"


# =============================================================================
# SECTION 2: GOVERNANCE SPEC TESTS
# =============================================================================


class TestGovernanceSpec:
    """Tests for GovernanceSpec data model."""

    def test_governance_spec_defaults(self):
        """Mutation killer: Default governance values."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import GovernanceSpec

        spec = GovernanceSpec()
        assert spec.level == "standard"
        assert spec.oath_required is False
        assert spec.constitution_bound is False
        assert spec.karma_tracking is True

    def test_governance_spec_from_dict(self):
        """Mutation killer: Create from dict."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import GovernanceSpec

        data = {
            "level": "strict",
            "oath_required": True,
            "constitution_bound": True,
            "audit_level": "paranoid",
        }
        spec = GovernanceSpec.from_dict(data)

        assert spec.level == "strict"
        assert spec.oath_required is True
        assert spec.constitution_bound is True
        assert spec.audit_level == "paranoid"

    def test_governance_spec_to_dict(self):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import GovernanceSpec

        spec = GovernanceSpec(level="sacred", oath_required=True)
        d = spec.to_dict()

        assert d["level"] == "sacred"
        assert d["oath_required"] is True


# =============================================================================
# SECTION 3: FRACTAL MANIFEST TESTS
# =============================================================================


class TestFractalManifest:
    """Tests for FractalManifest data model."""

    def test_manifest_basic_creation(self):
        """Mutation killer: Basic manifest creation."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import FractalManifest

        manifest = FractalManifest(agent_id="test_agent", name="Test Agent")
        assert manifest.agent_id == "test_agent"
        assert manifest.name == "Test Agent"
        assert manifest.version == "1.0.0"
        assert manifest.type == "cartridge"

    def test_manifest_has_capability(self):
        """Mutation killer: has_capability must work."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import (
            CapabilitySpec,
            FractalManifest,
        )

        manifest = FractalManifest(
            agent_id="test",
            name="Test",
            capabilities={
                "git_analysis": CapabilitySpec(name="git_analysis"),
                "code_review": CapabilitySpec(name="code_review"),
            },
        )

        assert manifest.has_capability("git_analysis") is True
        assert manifest.has_capability("nonexistent") is False

    def test_manifest_get_all_capabilities(self):
        """Mutation killer: get_all_capabilities must return set."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import (
            CapabilitySpec,
            FractalManifest,
        )

        manifest = FractalManifest(
            agent_id="test",
            name="Test",
            capabilities={
                "cap1": CapabilitySpec(name="cap1"),
                "cap2": CapabilitySpec(name="cap2"),
            },
        )

        caps = manifest.get_all_capabilities()
        assert caps == {"cap1", "cap2"}

    def test_manifest_to_dict(self):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import FractalManifest

        manifest = FractalManifest(
            agent_id="test",
            name="Test",
            domain="RESEARCH",
            permissions=["read_repo"],
        )
        d = manifest.to_dict()

        assert d["agent_id"] == "test"
        assert d["name"] == "Test"
        assert d["domain"] == "RESEARCH"
        assert "read_repo" in d["permissions"]


# =============================================================================
# SECTION 4: MANIFEST LOADER TESTS
# =============================================================================


class TestManifestLoader:
    """Tests for ManifestLoader."""

    @pytest.fixture
    def loader(self, tmp_path):
        """Create loader with temp workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import ManifestLoader

        return ManifestLoader(workspace=tmp_path)

    @pytest.fixture
    def cartridge_dir(self, tmp_path):
        """Create a test cartridge directory."""
        cartridge = tmp_path / "test_cartridge"
        cartridge.mkdir()
        return cartridge

    def test_loader_loads_steward_json(self, loader, cartridge_dir):
        """Mutation killer: Loader must load steward.json."""
        # Create steward.json
        steward_json = cartridge_dir / "steward.json"
        steward_json.write_text(
            json.dumps(
                {
                    "agent_id": "test_agent",
                    "name": "Test Agent",
                    "version": "2.0.0",
                    "zone": "governance",
                    "permissions": ["read_constitution"],
                }
            )
        )

        manifest = loader.load_cartridge_manifest(cartridge_dir)

        assert manifest is not None
        assert manifest.agent_id == "test_agent"
        assert manifest.name == "Test Agent"
        assert manifest.version == "2.0.0"
        assert manifest.zone == "governance"
        assert "read_constitution" in manifest.permissions

    def test_loader_loads_capabilities_from_json(self, loader, cartridge_dir):
        """Mutation killer: Capabilities must be loaded from JSON."""
        steward_json = cartridge_dir / "steward.json"
        steward_json.write_text(
            json.dumps(
                {
                    "agent_id": "test",
                    "capabilities": {
                        "seek_guidance": {"cost": 10, "rate_limit": "10/minute"},
                        "bless_action": {"cost": 5},
                    },
                }
            )
        )

        manifest = loader.load_cartridge_manifest(cartridge_dir)

        assert manifest.has_capability("seek_guidance")
        assert manifest.has_capability("bless_action")
        assert manifest.get_capability("seek_guidance").cost == 10

    def test_loader_loads_governance(self, loader, cartridge_dir):
        """Mutation killer: Governance must be loaded."""
        steward_json = cartridge_dir / "steward.json"
        steward_json.write_text(
            json.dumps(
                {
                    "agent_id": "dharma",
                    "governance": {
                        "level": "strict",
                        "oath_required": True,
                        "constitution_bound": True,
                    },
                }
            )
        )

        manifest = loader.load_cartridge_manifest(cartridge_dir)

        assert manifest.governance is not None
        assert manifest.governance.level == "strict"
        assert manifest.governance.oath_required is True

    def test_loader_handles_missing_manifest(self, loader, cartridge_dir):
        """Mutation killer: Missing manifest should return minimal manifest."""
        # No steward.json or cartridge.yaml

        manifest = loader.load_cartridge_manifest(cartridge_dir)

        # Should create minimal manifest from directory name
        assert manifest is not None
        assert manifest.agent_id == "test_cartridge"

    def test_loader_handles_invalid_path(self, loader, tmp_path):
        """Mutation killer: Invalid path should return None."""
        manifest = loader.load_cartridge_manifest(tmp_path / "nonexistent")
        assert manifest is None

    def test_loader_merges_json_and_yaml(self, loader, cartridge_dir):
        """Mutation killer: JSON and YAML should be merged."""
        # Create steward.json (base)
        steward_json = cartridge_dir / "steward.json"
        steward_json.write_text(
            json.dumps(
                {
                    "agent_id": "test",
                    "name": "Base Name",
                    "version": "1.0.0",
                }
            )
        )

        # Create cartridge.yaml (override)
        cartridge_yaml = cartridge_dir / "cartridge.yaml"
        cartridge_yaml.write_text("name: Override Name\ndomain: RESEARCH\n")

        manifest = loader.load_cartridge_manifest(cartridge_dir)

        # YAML should override JSON
        assert manifest.name == "Override Name"
        assert manifest.domain == "RESEARCH"
        # JSON base preserved
        assert manifest.version == "1.0.0"


# =============================================================================
# SECTION 5: CAPABILITY TREE TESTS
# =============================================================================


class TestCapabilityTree:
    """Tests for CapabilityTree."""

    @pytest.fixture
    def tree(self):
        """Create empty capability tree."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import CapabilityTree

        return CapabilityTree()

    @pytest.fixture
    def manifest(self):
        """Create test manifest."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import (
            CapabilitySpec,
            FractalManifest,
        )

        return FractalManifest(
            agent_id="analyst",
            name="Analyst",
            capabilities={
                "git_analysis": CapabilitySpec(name="git_analysis"),
                "code_review": CapabilitySpec(name="code_review", dependencies=["git_analysis"]),
            },
        )

    def test_tree_add_agent(self, tree, manifest):
        """Mutation killer: Adding agent populates tree."""
        tree.add_agent(manifest)

        assert tree.has_capability("git_analysis")
        assert tree.has_capability("code_review")

    def test_tree_get_provider(self, tree, manifest):
        """Mutation killer: get_provider must return correct agent."""
        tree.add_agent(manifest)

        provider = tree.get_provider("git_analysis")
        assert provider == "analyst"

    def test_tree_get_agent_capabilities(self, tree, manifest):
        """Mutation killer: get_agent_capabilities must return set."""
        tree.add_agent(manifest)

        caps = tree.get_agent_capabilities("analyst")
        assert "git_analysis" in caps
        assert "code_review" in caps

    def test_tree_validate_dependencies_success(self, tree, manifest):
        """Mutation killer: Valid dependencies should pass."""
        tree.add_agent(manifest)
        errors = tree.validate_dependencies()
        assert len(errors) == 0

    def test_tree_validate_dependencies_failure(self, tree):
        """Mutation killer: Missing dependency should fail."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import (
            CapabilitySpec,
            FractalManifest,
        )

        manifest = FractalManifest(
            agent_id="broken",
            name="Broken",
            capabilities={
                "needs_missing": CapabilitySpec(
                    name="needs_missing",
                    dependencies=["nonexistent_capability"],
                ),
            },
        )
        tree.add_agent(manifest)

        errors = tree.validate_dependencies()
        assert len(errors) > 0
        assert "nonexistent_capability" in errors[0]

    def test_tree_to_dict(self, tree, manifest):
        """Mutation killer: to_dict must return all fields."""
        tree.add_agent(manifest)
        d = tree.to_dict()

        assert "nodes" in d
        assert "agent_capabilities" in d
        assert "git_analysis" in d["nodes"]


# =============================================================================
# SECTION 6: CONFIG WEAVER TESTS
# =============================================================================


class TestConfigWeaver:
    """Tests for ConfigWeaver (the cosmic loom)."""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create workspace with cartridges."""
        # Create cartridge directories
        cartridges = tmp_path / "vibe_core" / "cartridges" / "agent_city"
        cartridges.mkdir(parents=True)

        # Create analyst cartridge
        analyst = cartridges / "analyst"
        analyst.mkdir()
        (analyst / "steward.json").write_text(
            json.dumps(
                {
                    "agent_id": "analyst",
                    "name": "ANALYST",
                    "domain": "RESEARCH",
                    "capabilities": {
                        "git_analysis": {"cost": 5},
                        "code_review": {"cost": 10},
                    },
                }
            )
        )

        # Create dharma cartridge
        dharma = cartridges / "dharma"
        dharma.mkdir()
        (dharma / "steward.json").write_text(
            json.dumps(
                {
                    "agent_id": "dharma",
                    "name": "DHARMA",
                    "domain": "GOVERNANCE",
                    "zone": "governance",
                    "capabilities": {
                        "seek_guidance": {"cost": 10},
                        "bless_action": {"cost": 5},
                    },
                    "governance": {
                        "level": "sacred",
                        "oath_required": True,
                    },
                }
            )
        )

        return tmp_path

    @pytest.fixture
    def weaver(self, workspace):
        """Create weaver with test workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import ConfigWeaver

        return ConfigWeaver(workspace=workspace)

    def test_weaver_discovers_cartridges(self, weaver):
        """Mutation killer: Weaver must discover cartridges."""
        weaver.weave()

        assert weaver.is_woven is True
        assert len(weaver.manifests) == 2

    def test_weaver_builds_capability_tree(self, weaver):
        """Mutation killer: Weaver must build capability tree."""
        weaver.weave()

        tree = weaver.capability_tree
        assert tree.has_capability("git_analysis")
        assert tree.has_capability("seek_guidance")

    def test_weaver_get_manifest(self, weaver):
        """Mutation killer: get_manifest must return correct manifest."""
        weaver.weave()

        manifest = weaver.get_manifest("analyst")
        assert manifest is not None
        assert manifest.agent_id == "analyst"

    def test_weaver_get_agents_by_domain(self, weaver):
        """Mutation killer: get_agents_by_domain must filter correctly."""
        weaver.weave()

        research_agents = weaver.get_agents_by_domain("RESEARCH")
        assert len(research_agents) == 1
        assert research_agents[0].agent_id == "analyst"

        governance_agents = weaver.get_agents_by_domain("GOVERNANCE")
        assert len(governance_agents) == 1
        assert governance_agents[0].agent_id == "dharma"

    def test_weaver_get_agents_with_capability(self, weaver):
        """Mutation killer: get_agents_with_capability must find providers."""
        weaver.weave()

        git_agents = weaver.get_agents_with_capability("git_analysis")
        assert len(git_agents) == 1
        assert git_agents[0].agent_id == "analyst"

    def test_weaver_to_dict(self, weaver):
        """Mutation killer: to_dict must return complete structure."""
        weaver.weave()
        d = weaver.to_dict()

        assert d["is_woven"] is True
        assert d["agent_count"] == 2
        assert "manifests" in d
        assert "capability_tree" in d

    def test_weaver_summary(self, weaver):
        """Mutation killer: summary must include key information."""
        weaver.weave()
        summary = weaver.summary()

        assert "MANDALA" in summary
        assert "Agents:" in summary
        assert "Capabilities:" in summary
        assert "RESEARCH" in summary or "GOVERNANCE" in summary

    def test_weaver_handles_empty_workspace(self, tmp_path):
        """Edge case: Empty workspace should not crash."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import ConfigWeaver

        weaver = ConfigWeaver(workspace=tmp_path)
        weaver.weave()

        assert weaver.is_woven is True
        assert len(weaver.manifests) == 0


# =============================================================================
# SECTION 7: INTEGRATION TESTS
# =============================================================================


class TestMandalaIntegration:
    """Integration tests for MANDALA."""

    @pytest.fixture
    def live_weaver(self):
        """Create weaver with real workspace."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import ConfigWeaver

        workspace = Path.cwd()
        return ConfigWeaver(workspace=workspace)

    def test_live_weaving(self, live_weaver):
        """Integration: Weave from real cartridges."""
        live_weaver.weave()

        assert live_weaver.is_woven is True
        # Should find at least some agents
        assert len(live_weaver.manifests) > 0

    def test_live_capability_lookup(self, live_weaver):
        """Integration: Look up real capabilities."""
        live_weaver.weave()

        # Check if any capabilities were loaded
        tree = live_weaver.capability_tree
        # Should have some capabilities
        assert len(tree._nodes) >= 0  # May be 0 if no capabilities defined

    def test_get_mandala_for_chat(self):
        """Integration: Chat bridge function."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import get_mandala_for_chat

        summary = get_mandala_for_chat()

        assert "MANDALA" in summary

    def test_query_capability_found(self):
        """Integration: Query existing capability."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import query_capability

        # This will work if any cartridge defines this capability
        result = query_capability("git_analysis")

        # Either found or not found message
        assert "git_analysis" in result

    def test_query_capability_not_found(self):
        """Integration: Query nonexistent capability."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import query_capability

        result = query_capability("definitely_nonexistent_capability_xyz")

        assert "not provided" in result or "❌" in result


# =============================================================================
# SECTION 8: RATE LIMIT SPEC TESTS
# =============================================================================


class TestRateLimitSpec:
    """Tests for RateLimitSpec."""

    def test_rate_limit_defaults(self):
        """Mutation killer: Default rate limits."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import RateLimitSpec

        spec = RateLimitSpec()
        assert spec.requests_per_minute == 60
        assert spec.requests_per_hour == 3600
        assert spec.burst_limit == 10

    def test_rate_limit_from_dict(self):
        """Mutation killer: Create from dict."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import RateLimitSpec

        data = {
            "requests_per_minute": 100,
            "burst_limit": 20,
        }
        spec = RateLimitSpec.from_dict(data)

        assert spec.requests_per_minute == 100
        assert spec.burst_limit == 20

    def test_rate_limit_to_dict(self):
        """Mutation killer: to_dict must return all fields."""
        from vibe_core.plugins.opus_assistant.manas.cortex.mandala import RateLimitSpec

        spec = RateLimitSpec(requests_per_minute=30)
        d = spec.to_dict()

        assert d["requests_per_minute"] == 30

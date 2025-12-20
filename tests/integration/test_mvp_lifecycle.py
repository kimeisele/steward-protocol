"""
MVP Lifecycle Test - Proving ONE complete cycle works.

The Cycle:
1. Agent doesn't exist
2. Genesis.scaffold_new() creates the agent structure
3. CIVIC.RegistryAgent scans and detects new agent
4. Agent gets registered with 100 credits

OPUS-164: Agent Lifecycle MVP Proof
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest


class TestMVPLifecycle:
    """Prove the agent lifecycle works end-to-end."""

    @pytest.fixture
    def temp_workspace(self, tmp_path):
        """Create temp workspace with proper structure."""
        workspace = tmp_path / "steward-protocol"
        workspace.mkdir()

        # Create cartridges/system directory
        system_dir = workspace / "vibe_core" / "cartridges" / "system"
        system_dir.mkdir(parents=True)

        # Create data/registry directory for RegistryAgent
        registry_dir = workspace / "data" / "registry"
        registry_dir.mkdir(parents=True)

        return workspace

    def test_step1_genesis_scaffolds_new_agent(self, temp_workspace):
        """
        STEP 1: Prove Genesis.scaffold_new() creates agent structure.

        Given: Empty directory
        When: Genesis.scaffold_new(path, ModuleType.CARTRIDGE, context)
        Then: All required files exist (cartridge_main.py, steward.json, etc.)
        """
        from vibe_core.genesis import GenesisService, ModuleType

        # Target: new researcher agent
        agent_dir = temp_workspace / "vibe_core" / "cartridges" / "system" / "researcher"

        # Context for template rendering
        context = {
            "id": "researcher",
            "name": "Researcher",
            "class_name": "Researcher",
            "domain": "RESEARCH",
            "description": "Research agent for knowledge gathering",
        }

        # Create fresh Genesis service for temp workspace
        GenesisService.reset_instance()
        genesis = GenesisService(workspace=temp_workspace)

        # Act: Scaffold new cartridge
        result = genesis.scaffold_new(
            path=agent_dir,
            module_type=ModuleType.CARTRIDGE,
            context=context,
        )

        # Assert: Success
        assert result.build_result is not None
        assert result.build_result.success, f"Build failed: {result.build_result.errors}"
        assert result.build_result.files_created_count >= 3

        # Assert: Required files exist
        assert (agent_dir / "cartridge_main.py").exists(), "Missing cartridge_main.py"
        assert (agent_dir / "__init__.py").exists(), "Missing __init__.py"
        assert (agent_dir / "steward.json").exists(), "Missing steward.json"

        # Assert: Content is valid
        steward_json = json.loads((agent_dir / "steward.json").read_text())
        assert steward_json["agent_id"] == "researcher"
        assert steward_json["name"] == "Researcher"

        # Cleanup
        GenesisService.reset_instance()

    def test_step2_registry_detects_new_agent(self, temp_workspace, monkeypatch):
        """
        STEP 2: Prove RegistryAgent detects scaffolded agent.

        Given: Scaffolded agent in system directory
        When: RegistryAgent.scan_and_register_agents()
        Then: New agent is found and registered
        """
        import os

        from vibe_core.genesis import GenesisService, ModuleType

        # First, scaffold the agent (Step 1)
        agent_dir = temp_workspace / "vibe_core" / "cartridges" / "system" / "researcher"

        context = {
            "id": "researcher",
            "name": "Researcher",
            "class_name": "Researcher",
            "domain": "RESEARCH",
            "description": "Research agent",
        }

        GenesisService.reset_instance()
        genesis = GenesisService(workspace=temp_workspace)
        result = genesis.scaffold_new(agent_dir, ModuleType.CARTRIDGE, context)
        assert result.build_result.success

        # Change to temp workspace so RegistryAgent finds the right paths
        original_cwd = Path.cwd()
        monkeypatch.chdir(temp_workspace)

        try:
            # Import after changing directory
            from vibe_core.cartridges.system.civic.registry_agent import RegistryAgent

            # Create fresh registry agent
            registry = RegistryAgent()

            # Act: Scan for agents
            scan_result = registry.scan_and_register_agents(dry_run=False)

            # Assert: Scan succeeded
            assert scan_result["status"] == "complete"
            assert "researcher" in scan_result["registered_agents"], (
                f"researcher not found in {scan_result['registered_agents']}"
            )

            # Assert: Agent is in registry with correct data
            registry_data = registry.get_registry()
            assert "researcher" in registry_data["agents"]

            researcher = registry_data["agents"]["researcher"]
            assert researcher["credits"] == 100, "Should have 100 initial credits"
            assert researcher["broadcast_license"] is True
            assert researcher["lifecycle_status"]["status"] == "brahmachari"

        finally:
            monkeypatch.chdir(original_cwd)
            GenesisService.reset_instance()

    def test_full_lifecycle_integration(self, temp_workspace, monkeypatch):
        """
        FULL CYCLE: Genesis → Registry → Credits

        This is the MVP proof: One complete agent birth cycle.
        """
        from vibe_core.genesis import GenesisService, ModuleType

        # === PHASE 1: No agent exists ===
        agent_dir = temp_workspace / "vibe_core" / "cartridges" / "system" / "newborn"
        assert not agent_dir.exists(), "Agent should not exist yet"

        # === PHASE 2: Genesis creates agent ===
        GenesisService.reset_instance()
        genesis = GenesisService(workspace=temp_workspace)

        context = {
            "id": "newborn",
            "name": "Newborn Agent",
            "class_name": "Newborn",
            "domain": "TESTING",
            "description": "A freshly born agent",
        }

        result = genesis.scaffold_new(agent_dir, ModuleType.CARTRIDGE, context)

        # Verify genesis succeeded
        assert result.build_result.success
        assert agent_dir.exists()
        assert (agent_dir / "cartridge_main.py").exists()

        # === PHASE 3: CIVIC discovers and registers ===
        original_cwd = Path.cwd()
        monkeypatch.chdir(temp_workspace)

        try:
            from vibe_core.cartridges.system.civic.registry_agent import RegistryAgent

            registry = RegistryAgent()
            scan_result = registry.scan_and_register_agents(dry_run=False)

            # Verify registration
            assert scan_result["status"] == "complete"
            assert "newborn" in scan_result["registered_agents"]

            # === PHASE 4: Agent has credits ===
            registry_data = registry.get_registry()
            newborn = registry_data["agents"]["newborn"]

            assert newborn["credits"] == 100
            assert newborn["broadcast_license"] is True
            assert newborn["lifecycle_status"]["status"] == "brahmachari"
            assert newborn["lifecycle_status"]["varna"] == "Brahmachari (Student)"

            # === SUCCESS: Full cycle complete! ===
            print("\n" + "=" * 60)
            print("🎉 MVP LIFECYCLE PROOF COMPLETE")
            print("=" * 60)
            print(f"  Agent: {newborn['name']}")
            print(f"  Credits: {newborn['credits']}")
            print(f"  License: {newborn['broadcast_license']}")
            print(f"  Status: {newborn['lifecycle_status']['varna']}")
            print("=" * 60 + "\n")

        finally:
            monkeypatch.chdir(original_cwd)
            GenesisService.reset_instance()


class TestGenesisQuickCheck:
    """Verify quick_check works for compliance validation."""

    def test_quick_check_passes_for_compliant(self, tmp_path):
        """Compliant agents pass quick_check."""
        from vibe_core.genesis import GenesisService, ModuleType

        # Create compliant cartridge
        agent_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "compliant"
        agent_dir.mkdir(parents=True)

        # Create required files manually
        (agent_dir / "__init__.py").write_text('"""Init"""')
        (agent_dir / "cartridge_main.py").write_text('"""Main"""')
        (agent_dir / "cartridge.yaml").write_text("id: compliant\nname: Compliant")
        (agent_dir / "steward.json").write_text('{"agent_id": "compliant"}')

        GenesisService.reset_instance()
        genesis = GenesisService(workspace=tmp_path)

        # Act
        is_compliant = genesis.quick_check(agent_dir)

        # Assert
        assert is_compliant is True

        GenesisService.reset_instance()

    def test_quick_check_fails_for_non_compliant(self, tmp_path):
        """Non-compliant agents fail quick_check."""
        from vibe_core.genesis import GenesisService, ModuleType

        # Create incomplete cartridge
        agent_dir = tmp_path / "vibe_core" / "cartridges" / "system" / "broken"
        agent_dir.mkdir(parents=True)

        # Only create __init__.py (missing cartridge_main.py, steward.json)
        (agent_dir / "__init__.py").write_text('"""Init"""')

        GenesisService.reset_instance()
        genesis = GenesisService(workspace=tmp_path)

        # Act
        is_compliant = genesis.quick_check(agent_dir)

        # Assert
        assert is_compliant is False

        GenesisService.reset_instance()

"""
Tests for OPUS Cognitive Circuits (Phase 4).

Tests the self-management circuits:
- OPUS_AUTO_VERIFY: Triggered by GIT_COMMIT
- OPUS_AUTO_HEAL: Triggered by persistent drift
"""

from pathlib import Path

import yaml

# =============================================================================
# Circuit Module Tests
# =============================================================================


class TestCircuitsModule:
    """Test circuits module exports."""

    def test_module_importable(self):
        """Circuits module should be importable."""
        from vibe_core.plugins.opus_assistant import circuits

        assert circuits is not None

    def test_circuit_ids_exported(self):
        """CIRCUIT_IDS should be exported."""
        from vibe_core.plugins.opus_assistant.circuits import CIRCUIT_IDS

        assert isinstance(CIRCUIT_IDS, list)
        assert "OPUS_AUTO_VERIFY" in CIRCUIT_IDS
        assert "OPUS_AUTO_HEAL" in CIRCUIT_IDS

    def test_circuit_paths_exported(self):
        """Circuit paths should be exported."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH, AUTO_VERIFY_PATH

        assert AUTO_VERIFY_PATH.exists()
        assert AUTO_HEAL_PATH.exists()

    def test_get_circuit_paths(self):
        """get_circuit_paths should return path dict."""
        from vibe_core.plugins.opus_assistant.circuits import get_circuit_paths

        paths = get_circuit_paths()

        assert isinstance(paths, dict)
        assert "OPUS_AUTO_VERIFY" in paths
        assert "OPUS_AUTO_HEAL" in paths

    def test_list_circuits(self):
        """list_circuits should return circuit IDs."""
        from vibe_core.plugins.opus_assistant.circuits import list_circuits

        circuits = list_circuits()

        assert isinstance(circuits, list)
        assert len(circuits) >= 2


# =============================================================================
# Auto-Verify Circuit Tests
# =============================================================================


class TestAutoVerifyCircuit:
    """Test OPUS_AUTO_VERIFY circuit definition."""

    def test_circuit_file_exists(self):
        """auto_verify.yaml should exist."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        assert AUTO_VERIFY_PATH.exists()

    def test_circuit_valid_yaml(self):
        """auto_verify.yaml should be valid YAML."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "circuit" in data

    def test_circuit_has_id(self):
        """Circuit should have correct ID."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        assert data["circuit"]["id"] == "OPUS_AUTO_VERIFY"

    def test_circuit_has_triggers(self):
        """Circuit should define event triggers."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        triggers = data["circuit"].get("triggers", [])
        assert len(triggers) > 0

        # Should trigger on GIT_COMMIT
        trigger_events = [t.get("event") for t in triggers]
        assert "GIT_COMMIT" in trigger_events

    def test_circuit_has_entry_state(self):
        """Circuit should define entry state."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        assert "entry_state" in data["circuit"]
        assert data["circuit"]["entry_state"] == "detect_drift"

    def test_circuit_has_states(self):
        """Circuit should define states."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        states = data["circuit"].get("states", {})
        assert len(states) > 0

        # Should have key states
        assert "detect_drift" in states
        assert "COMPLETE" in states

    def test_circuit_has_terminal_states(self):
        """Circuit should have terminal states."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_VERIFY_PATH

        with open(AUTO_VERIFY_PATH) as f:
            data = yaml.safe_load(f)

        states = data["circuit"]["states"]
        terminal_states = [name for name, state in states.items() if state.get("terminal")]

        assert len(terminal_states) >= 1
        assert "COMPLETE" in terminal_states


# =============================================================================
# Auto-Heal Circuit Tests
# =============================================================================


class TestAutoHealCircuit:
    """Test OPUS_AUTO_HEAL circuit definition."""

    def test_circuit_file_exists(self):
        """auto_heal.yaml should exist."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        assert AUTO_HEAL_PATH.exists()

    def test_circuit_valid_yaml(self):
        """auto_heal.yaml should be valid YAML."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        with open(AUTO_HEAL_PATH) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert "circuit" in data

    def test_circuit_has_id(self):
        """Circuit should have correct ID."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        with open(AUTO_HEAL_PATH) as f:
            data = yaml.safe_load(f)

        assert data["circuit"]["id"] == "OPUS_AUTO_HEAL"

    def test_circuit_is_draft(self):
        """Auto-heal circuit should be marked as draft."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        with open(AUTO_HEAL_PATH) as f:
            data = yaml.safe_load(f)

        version = data["circuit"].get("version", "")
        # Draft should be indicated in name or version
        assert "draft" in version.lower() or "draft" in data["circuit"].get("name", "").lower()

    def test_circuit_has_triggers(self):
        """Circuit should define event triggers."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        with open(AUTO_HEAL_PATH) as f:
            data = yaml.safe_load(f)

        triggers = data["circuit"].get("triggers", [])
        assert len(triggers) > 0

    def test_circuit_has_patterns(self):
        """Circuit should define drift patterns."""
        from vibe_core.plugins.opus_assistant.circuits import AUTO_HEAL_PATH

        with open(AUTO_HEAL_PATH) as f:
            data = yaml.safe_load(f)

        patterns = data.get("patterns", {})
        assert len(patterns) > 0

        # Should have common pattern types
        assert "missing_docs" in patterns or "stale_docs" in patterns


# =============================================================================
# Manifest Integration Tests
# =============================================================================


class TestManifestCircuitIntegration:
    """Test circuits are registered in manifest."""

    def test_manifest_has_circuits_section(self):
        """Manifest should have circuits section."""
        import json

        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        assert "circuits" in manifest

    def test_manifest_lists_auto_verify(self):
        """Manifest should list auto_verify circuit."""
        import json

        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        circuits = manifest.get("circuits", [])
        circuit_names = [Path(c).name for c in circuits]

        assert "auto_verify.yaml" in circuit_names

    def test_manifest_lists_auto_heal(self):
        """Manifest should list auto_heal circuit."""
        import json

        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        circuits = manifest.get("circuits", [])
        circuit_names = [Path(c).name for c in circuits]

        assert "auto_heal.yaml" in circuit_names

    def test_manifest_has_circuits_capability(self):
        """Manifest should declare circuits capability."""
        import json

        manifest_path = Path("vibe_core/plugins/opus_assistant/manifest.json")
        manifest = json.loads(manifest_path.read_text())

        capabilities = manifest.get("capabilities", [])
        assert "opus.circuits" in capabilities

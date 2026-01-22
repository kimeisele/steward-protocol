"""
TESTS: cli/observe.py - Observation Service
============================================

REAL TESTS for:
1. FolderMapping TypedDict
2. ProtocolStatus TypedDict
3. ObserveResult TypedDict
4. MahamantraObserver class
5. observe_* functions
"""

import pytest
from vibe_core.mahamantra.cli.observe import (
    FolderMapping,
    ProtocolStatus,
    ObserveResult,
    MahamantraObserver,
    observer,
    observe_mahamantra,
    observe_folder_mappings,
    observe_protocols,
    observe,
    cli_observe,
)


# =============================================================================
# FolderMapping TypedDict Tests
# =============================================================================


class TestFolderMapping:
    """Test FolderMapping TypedDict."""

    def test_folder_mapping_creation(self):
        """FolderMapping can be created."""
        mapping: FolderMapping = {
            "folder": "protocols",
            "mahajana": "kapila",
            "position": 6,
            "exists": True,
            "in_map": True,
        }
        assert mapping["folder"] == "protocols"
        assert mapping["mahajana"] == "kapila"
        assert mapping["position"] == 6
        assert mapping["exists"] is True
        assert mapping["in_map"] is True


# =============================================================================
# ProtocolStatus TypedDict Tests
# =============================================================================


class TestProtocolStatus:
    """Test ProtocolStatus TypedDict."""

    def test_protocol_status_creation(self):
        """ProtocolStatus can be created."""
        status: ProtocolStatus = {
            "name": "KalaProtocol",
            "exists": True,
            "connected": False,
            "location": "vibe_core.protocols.substrate",
        }
        assert status["name"] == "KalaProtocol"
        assert status["exists"] is True
        assert status["connected"] is False


# =============================================================================
# ObserveResult TypedDict Tests
# =============================================================================


class TestObserveResult:
    """Test ObserveResult TypedDict."""

    def test_observe_result_creation(self):
        """ObserveResult can be created."""
        result: ObserveResult = {
            "mahamantra_type": "Mahamantra",
            "can_chant": True,
            "can_tick": True,
            "positions": 16,
            "quarters": ["genesis", "dharma", "karma", "moksha"],
            "folder_mappings": [],
            "missing_mappings": [],
            "protocols": [],
        }
        assert result["positions"] == 16
        assert len(result["quarters"]) == 4


# =============================================================================
# MahamantraObserver Tests
# =============================================================================


class TestMahamantraObserver:
    """Test MahamantraObserver class."""

    def test_mahamantra_observer_creation(self):
        """MahamantraObserver can be created."""
        obs = MahamantraObserver()
        assert obs is not None

    def test_mahamantra_observer_tattva(self):
        """MahamantraObserver implements PanchaTattvaProtocol."""
        obs = MahamantraObserver()
        tattva = obs.__tattva__
        assert "chaitanya" in tattva
        assert "nityananda" in tattva
        assert "advaita" in tattva
        assert "gadadhara" in tattva
        assert "srivasa" in tattva


# =============================================================================
# observer Singleton Tests
# =============================================================================


class TestObserverSingleton:
    """Test observer singleton."""

    def test_observer_is_instance(self):
        """observer is a MahamantraObserver instance."""
        assert isinstance(observer, MahamantraObserver)


# =============================================================================
# observe_mahamantra Tests
# =============================================================================


class TestObserveMahamantra:
    """Test observe_mahamantra function."""

    def test_observe_mahamantra_returns_dict(self):
        """observe_mahamantra returns dict."""
        result = observe_mahamantra()
        assert isinstance(result, dict)

    def test_observe_mahamantra_has_type(self):
        """observe_mahamantra has type field."""
        result = observe_mahamantra()
        assert "type" in result

    def test_observe_mahamantra_has_can_chant(self):
        """observe_mahamantra has can_chant field."""
        result = observe_mahamantra()
        assert "can_chant" in result
        assert isinstance(result["can_chant"], bool)

    def test_observe_mahamantra_has_can_tick(self):
        """observe_mahamantra has can_tick field."""
        result = observe_mahamantra()
        assert "can_tick" in result
        assert isinstance(result["can_tick"], bool)

    def test_observe_mahamantra_has_positions(self):
        """observe_mahamantra has positions field."""
        result = observe_mahamantra()
        assert "positions" in result
        assert result["positions"] == 16

    def test_observe_mahamantra_has_quarters(self):
        """observe_mahamantra has quarters field."""
        result = observe_mahamantra()
        assert "quarters" in result
        assert len(result["quarters"]) == 4


# =============================================================================
# observe_folder_mappings Tests
# =============================================================================


class TestObserveFolderMappings:
    """Test observe_folder_mappings function."""

    def test_observe_folder_mappings_returns_tuple(self):
        """observe_folder_mappings returns tuple."""
        mappings, missing = observe_folder_mappings()
        assert isinstance(mappings, list)
        assert isinstance(missing, list)

    def test_observe_folder_mappings_structure(self):
        """observe_folder_mappings returns FolderMapping list."""
        mappings, missing = observe_folder_mappings()
        for m in mappings:
            assert "folder" in m
            assert "mahajana" in m
            assert "position" in m
            assert "exists" in m
            assert "in_map" in m


# =============================================================================
# observe_protocols Tests
# =============================================================================


class TestObserveProtocols:
    """Test observe_protocols function."""

    def test_observe_protocols_returns_list(self):
        """observe_protocols returns list."""
        protocols = observe_protocols()
        assert isinstance(protocols, list)

    def test_observe_protocols_structure(self):
        """observe_protocols returns ProtocolStatus list."""
        protocols = observe_protocols()
        for p in protocols:
            assert "name" in p
            assert "exists" in p
            assert "connected" in p
            assert "location" in p


# =============================================================================
# observe Tests
# =============================================================================


class TestObserve:
    """Test observe function."""

    def test_observe_returns_observe_result(self):
        """observe returns ObserveResult."""
        result = observe()
        assert "mahamantra_type" in result
        assert "can_chant" in result
        assert "can_tick" in result
        assert "positions" in result
        assert "quarters" in result
        assert "folder_mappings" in result
        assert "missing_mappings" in result
        assert "protocols" in result

    def test_observe_has_16_positions(self):
        """observe reports 16 positions."""
        result = observe()
        assert result["positions"] == 16

    def test_observe_has_4_quarters(self):
        """observe reports 4 quarters."""
        result = observe()
        assert len(result["quarters"]) == 4


# =============================================================================
# cli_observe Tests
# =============================================================================


class TestCliObserve:
    """Test cli_observe function."""

    def test_cli_observe_returns_dict(self):
        """cli_observe returns dict."""
        result = cli_observe()
        assert isinstance(result, dict)

    def test_cli_observe_has_required_fields(self):
        """cli_observe has required fields."""
        result = cli_observe()
        assert "mahamantra_type" in result
        assert "positions" in result

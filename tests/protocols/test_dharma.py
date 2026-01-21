"""
TEST DHARMA COMPLIANCE
======================
Verifies that the Dharma Protocol (Layer Architecture) is respected.

- Checks that all strict files are in the Protocol Map.
- Checks that get_layer works correctly.
"""

import pytest
from vibe_core.protocols.dharma import ProtocolLayer, get_layer, check_compliance, PROTOCOL_MAP


def test_dharma_map_integrity():
    """Verify PROTOCOL_MAP has valid entries."""
    assert "dharma.py" in PROTOCOL_MAP
    assert PROTOCOL_MAP["dharma.py"] == ProtocolLayer.META
    assert "agent.py" in PROTOCOL_MAP
    assert PROTOCOL_MAP["agent.py"] == ProtocolLayer.INTERFACE


def test_layer_resolution():
    """Verify get_layer resolves layers correctly."""
    assert get_layer("substrate/byte.py") == ProtocolLayer.SUBSTRATE
    assert get_layer("governance/yamaraja.py") == ProtocolLayer.SERVICES
    assert get_layer("unknown_file.py") == ProtocolLayer.FOUNDATION


def test_meta_superiority():
    """Meta layer (108) is above Wiring (3)."""
    assert ProtocolLayer.META > ProtocolLayer.WIRING


def test_substrate_depth():
    """Substrate is the deepest layer (-1)."""
    assert ProtocolLayer.SUBSTRATE < ProtocolLayer.FOUNDATION


def test_source_origin():
    """Energy Source (-2) precedes Substrate (-1)."""
    assert ProtocolLayer.KRISHNA == -2
    assert ProtocolLayer.KRISHNA < ProtocolLayer.SUBSTRATE
    assert "source" in PROTOCOL_MAP
    assert PROTOCOL_MAP["source"] == ProtocolLayer.KRISHNA

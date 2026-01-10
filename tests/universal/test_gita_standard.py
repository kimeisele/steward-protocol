"""
TEST GITA STANDARD COMPLIANCE
=============================
Verifies that the Gita Protocol (The Divine Standard) enforces strict typing.

"Yamaraja checks the Types."
"""

import pytest
import inspect
from typing import get_type_hints
from vibe_core.protocols.universal.gita import GitaProtocol
from vibe_core.protocols.universal.types import SankhyaDualism, KarmaCounter, VisvarupaSnapshot
from vibe_core.protocols.dharma import PROTOCOL_MAP, ProtocolLayer

def test_gita_protocol_signatures():
    """
    Verify that the Gita Protocol methods return the strict Vedic Structs,
    NOT 'Any' or 'Dict'.
    """
    # Use get_type_hints to resolve forward references like "SankhyaDualism"
    hints = get_type_hints(GitaProtocol.chapter_02_sankhya_yoga)
    assert hints['return'] == SankhyaDualism, "Gate 2 must return SankhyaDualism"

    hints = get_type_hints(GitaProtocol.chapter_03_karma_yoga)
    assert hints['return'] == KarmaCounter, "Gate 3 must return KarmaCounter"

    hints = get_type_hints(GitaProtocol.chapter_11_visvarupa_yoga)
    assert hints['return'] == VisvarupaSnapshot, "Gate 11 must return VisvarupaSnapshot"

def test_dharma_map_includes_gita():
    """
    Verify that the Gita is acknowledged in the Dharma Map.
    """
    assert "universal/gita.py" in PROTOCOL_MAP
    assert PROTOCOL_MAP["universal/gita.py"] == ProtocolLayer.INTERFACE

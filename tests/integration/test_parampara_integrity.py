#!/usr/bin/env python3
"""
Integration Test: Parampara Chain Integrity
============================================

Tests that:
1. Parampara blockchain maintains integrity
2. Genesis Block is immutable
3. Chain verification works
4. Passport issuance is recorded
"""

import pytest
import sys
import os
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.lineage import LineageChain, LineageEventType


def test_genesis_block_creation():
    """Test that Genesis Block is created correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Genesis Block should exist
        genesis = chain.get_genesis_block()
        assert genesis is not None
        assert genesis.event_type == LineageEventType.GENESIS
        assert genesis.index == 0
        assert genesis.previous_hash == "0" * 64

        # Genesis should have constitutional anchors
        assert "anchors" in genesis.data
        assert "gad000_hash" in genesis.data["anchors"]
        assert "constitution_hash" in genesis.data["anchors"]

        chain.close()


def test_chain_integrity_verification():
    """Test that chain integrity can be verified."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Add some blocks
        chain.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id="test_kernel",
            data={"timestamp": "2025-11-28T12:00:00Z"}
        )

        chain.add_block(
            event_type=LineageEventType.AGENT_REGISTERED,
            agent_id="test_agent",
            data={"capabilities": ["test"]}
        )

        # Verify chain integrity
        is_valid = chain.verify_chain()
        assert is_valid is True

        # Get all blocks
        blocks = chain.get_all_blocks()
        assert len(blocks) == 3  # Genesis + 2 blocks

        # Verify each block links to previous
        for i in range(1, len(blocks)):
            current = blocks[i]
            previous = blocks[i-1]
            assert current.previous_hash == previous.hash

        chain.close()


def test_passport_issuance_recorded():
    """Test that PASSPORT_ISSUED events are recorded."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Issue a passport (simulate)
        chain.add_block(
            event_type=LineageEventType.PASSPORT_ISSUED,
            agent_id="herald",
            data={
                "manifest_hash": "abc123...",
                "capabilities": ["broadcasting", "content_generation"],
                "issued_at": "2025-11-28T12:00:00Z"
            }
        )

        # Verify it was recorded
        blocks = chain.get_all_blocks()
        passport_blocks = [b for b in blocks if b.event_type == LineageEventType.PASSPORT_ISSUED]
        assert len(passport_blocks) == 1

        passport = passport_blocks[0]
        assert passport.agent_id == "herald"
        assert "manifest_hash" in passport.data

        chain.close()


def test_chain_immutability():
    """Test that chain cannot be altered (hash integrity)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_lineage.db")
        chain = LineageChain(db_path=db_path)

        # Add a block
        chain.add_block(
            event_type=LineageEventType.AGENT_REGISTERED,
            agent_id="test_agent",
            data={"test": "data"}
        )

        # Get original blocks
        original_blocks = chain.get_all_blocks()
        original_hash = original_blocks[1].hash

        # Close and reopen
        chain.close()
        chain = LineageChain(db_path=db_path)

        # Verify blocks are unchanged
        new_blocks = chain.get_all_blocks()
        assert len(new_blocks) == len(original_blocks)
        assert new_blocks[1].hash == original_hash

        # Verify chain is still valid
        assert chain.verify_chain() is True

        chain.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

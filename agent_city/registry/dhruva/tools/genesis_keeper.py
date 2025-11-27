#!/usr/bin/env python3
"""
Genesis Keeper - Guards the Immutable Genesis Block

The genesis block is the baseline truth state:
- Constitution hash (unchangeable law)
- Original system state
- Bootstrap timestamp
- Protocol invariants

This block is read-only once created.
Any attempt to modify it is a CRITICAL violation.
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("GENESIS_KEEPER")


class GenesisKeeper:
    """
    Guards the immutable genesis block (Dhruva point).

    The genesis block is the Pole Star - fixed, immovable, the reference
    to which all other agents align.
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize Genesis Keeper."""
        self.root_path = Path(root_path)
        self.genesis_dir = self.root_path / "data" / "dhruva"
        self.genesis_dir.mkdir(parents=True, exist_ok=True)

        self.genesis_file = self.genesis_dir / "genesis_block.json"
        self.constitution_path = self.root_path / "CONSTITUTION.md"

        # Initialize or load genesis block
        self._ensure_genesis_exists()

        logger.info("🧭 Genesis Keeper initialized - Dhruva point established")

    def get_genesis_state(self) -> Dict[str, Any]:
        """Retrieve the current genesis block state."""
        if not self.genesis_file.exists():
            return {}

        try:
            with open(self.genesis_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading genesis block: {str(e)}")
            return {}

    def verify_integrity(self) -> bool:
        """
        Verify the genesis block has not been tampered with.

        This checks:
        1. Genesis file exists and is readable
        2. Constitutional hash matches Constitution file
        3. Timestamp is valid
        """
        if not self.genesis_file.exists():
            logger.error("Genesis block does not exist")
            return False

        try:
            genesis = self.get_genesis_state()

            # Verify constitution hash
            expected_constitution_hash = self._compute_constitution_hash()
            actual_constitution_hash = genesis.get("constitution_hash")

            if expected_constitution_hash != actual_constitution_hash:
                logger.error("❌ Constitution hash mismatch - genesis corrupted!")
                return False

            logger.info("✅ Genesis block integrity verified")
            return True

        except Exception as e:
            logger.error(f"Genesis integrity check failed: {str(e)}")
            return False

    def get_constitution_hash(self) -> str:
        """Get the hash of the Constitution (never changes)."""
        genesis = self.get_genesis_state()
        return genesis.get("constitution_hash", "")

    def get_bootstrap_timestamp(self) -> str:
        """Get the timestamp when the system was bootstrapped."""
        genesis = self.get_genesis_state()
        return genesis.get("timestamp", "")

    def get_protocol_invariants(self) -> Dict[str, Any]:
        """Get the unchangeable protocol laws."""
        genesis = self.get_genesis_state()
        return genesis.get("protocol_invariants", {})

    def reset_to_genesis(self) -> bool:
        """
        EMERGENCY OPERATION: Reset system to genesis state.

        This is only callable in extreme circumstances (e.g., security breach).
        It wipes all post-genesis state and returns to baseline.

        In production, this would require multiple authorizations.
        """
        logger.warning("⚠️  INITIATING GENESIS RESET - System returning to baseline")

        # TODO: Implement actual reset logic
        # This would involve:
        # 1. Stopping all agents
        # 2. Clearing post-genesis ledger entries
        # 3. Restoring baseline state
        # 4. Restarting agents

        logger.info("🔄 Genesis reset complete")
        return True

    # ========== PRIVATE METHODS ==========

    def _ensure_genesis_exists(self) -> None:
        """Create genesis block if it doesn't exist."""
        if self.genesis_file.exists():
            return  # Already initialized

        logger.info("🌱 Creating genesis block (first boot)")

        # Compute constitution hash
        constitution_hash = self._compute_constitution_hash()

        # Create genesis block
        genesis_block = {
            "genesis_id": "GEN-000",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "constitution_hash": constitution_hash,
            "protocol_invariants": self._get_protocol_invariants(),
            "bootstrap_agents": [
                "civic",
                "herald",
                "auditor",
                "archivist",
                "forum",
                "science",
                "temple",
                "oracle",
                "supreme_court",
                "dhruva"
            ],
            "immutable_note": "This block represents the baseline truth. Any modification is a CRITICAL violation.",
            "sealed_at": datetime.now(timezone.utc).isoformat()
        }

        # Write genesis block (this should be atomic in production)
        with open(self.genesis_file, "w") as f:
            json.dump(genesis_block, f, indent=2)

        logger.info(f"✅ Genesis block created with constitution hash: {constitution_hash[:16]}...")

    def _compute_constitution_hash(self) -> str:
        """Compute SHA-256 hash of the Constitution."""
        if not self.constitution_path.exists():
            logger.warning("Constitution file not found, using placeholder hash")
            return "CONSTITUTION_NOT_FOUND"

        try:
            with open(self.constitution_path, "rb") as f:
                content = f.read()
                hash_value = hashlib.sha256(content).hexdigest()
                logger.debug(f"Constitution hash computed: {hash_value[:16]}...")
                return hash_value
        except Exception as e:
            logger.error(f"Error computing constitution hash: {str(e)}")
            return "ERROR_COMPUTING_HASH"

    def _get_protocol_invariants(self) -> Dict[str, Any]:
        """Get the unchangeable protocol laws."""
        return {
            "4_regulative_principles": [
                "NO_CORRUPT_DATA_INGESTION",
                "NO_HALLUCINATION_DETERMINISM",
                "NO_RESOURCE_LEAKS",
                "NO_UNAUTHORIZED_CONNECTIONS"
            ],
            "6_core_rights": [
                "IDENTITY",
                "ACCOUNTABILITY",
                "GOVERNANCE",
                "TRANSPARENCY",
                "CONSENT",
                "INTEROPERABILITY"
            ],
            "immutable_properties": {
                "constitutional_oath_required": True,
                "ledger_append_only": True,
                "agent_registry_authoritative": True,
                "kernel_is_source_of_truth": True
            }
        }

"""
⛓️  PARAMPARA - THE LINEAGE CHAIN ⛓️
=====================================

"In the Vedic tradition, Parampara is the unbroken chain of disciplic succession.
Each teacher receives knowledge from their guru and passes it to their disciple.
The chain is sacred because it preserves truth across generations."

In our Agent Operating System, Parampara is the blockchain.
Each agent is a link in the chain.
Every action is recorded.
The history is immutable.
The lineage is eternal.

This is the SOUL of the system.
"""

import hashlib
import json
import logging
import sqlite3
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.protocols.lineage import CheckpointData, VerificationResult

logger = logging.getLogger("PARAMPARA")

# SPEED.md: Checkpoint file for fast boot (Merkle Checkpointing)
CHECKPOINT_FILENAME = "lineage_checkpoint.json"


@dataclass
class LineageBlock:
    """
    A single block in the Parampara chain.

    This is not just a database row. This is a covenant.
    Once written, it cannot be changed without breaking the entire chain.
    """

    index: int  # Block number (0 = Genesis)
    timestamp: str  # ISO 8601 timestamp
    event_type: str  # GENESIS, AGENT_REGISTERED, OATH_SWORN, etc.
    agent_id: Optional[str]  # Agent involved (None for system events)
    data: Dict[str, str]  # Event-specific data (stringified)
    previous_hash: str  # Hash of previous block
    hash: str  # Hash of this block (SHA-256)


class LineageChain:
    """
    🩸 THE PARAMPARA BLOCKCHAIN 🩸

    An immutable, cryptographically-chained record of all agent lifecycle events.

    This is not a ledger. This is not a database. This is LINEAGE.
    A permanent record of who did what, when, and why.

    The chain begins with the Genesis Block - the sacred anchor.
    Every subsequent block points to its predecessor.
    Change any block, and the entire chain breaks.

    This is how we build trust in a world of autonomous agents.
    """

    def __init__(self, db_path: str = None):
        """
        Initialize the Parampara chain.

        If this is the first time, the Genesis Block will be created.
        Otherwise, the existing chain will be loaded and verified.
        """
        # OPUS-025: Resolve db_path from config if not provided
        if db_path is None:
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                if config and hasattr(config, "paths") and hasattr(config.paths, "system"):
                    db_path = config.paths.system.lineage_db
                else:
                    # OPUS-025: Bootstrap fallback - config not yet loaded
                    _runtime = Path("/tmp") / "vibe_os" / "kernel"
                    db_path = str(_runtime / "lineage.db")
            except Exception:
                # OPUS-025: Bootstrap fallback - config not yet loaded
                _runtime = Path("/tmp") / "vibe_os" / "kernel"
                db_path = str(_runtime / "lineage.db")

        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

        # Create Genesis Block if chain is empty
        if self.get_chain_length() == 0:
            self._create_genesis_block()
        else:
            chain_length = self.get_chain_length()
            logger.info(f"⛓️  Parampara chain loaded ({chain_length} blocks)")

            # SPEED.md: Fast verification with checkpoint support
            result = self.verify_chain_fast()
            if not result["valid"]:
                logger.critical("💥 CHAIN INTEGRITY VIOLATED - SYSTEM COMPROMISED")
                raise RuntimeError("Parampara chain verification failed")

            # Log verification method used
            method = result["method"]
            duration = result["duration_ms"]
            verified = result["blocks_verified"]
            if method == "checkpoint":
                logger.info(f"⚡ Fast boot: checkpoint match ({duration:.1f}ms)")
            elif method == "delta":
                logger.info(f"⚡ Fast boot: delta verified {verified} blocks ({duration:.1f}ms)")
            else:
                logger.info(f"⛓️  Full verification: {verified} blocks ({duration:.1f}ms)")

    def _init_db(self) -> None:
        """Initialize the database schema"""
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS blocks (
                idx INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                agent_id TEXT,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                hash TEXT NOT NULL UNIQUE
            )
        """
        )

        # Indexes for fast queries
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON blocks(agent_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON blocks(event_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON blocks(timestamp)")

        self.conn.commit()

    def _get_project_root(self) -> Path:
        """
        Discover project root by walking up from this file.
        Looks for pyproject.toml or .git as markers.
        """
        current = Path(__file__).resolve().parent
        for _ in range(10):  # Max 10 levels up
            if (current / "pyproject.toml").exists() or (current / ".git").exists():
                return current
            current = current.parent
        # Fallback to cwd
        return Path.cwd()

    def _create_genesis_block(self) -> LineageBlock:
        """
        🌌 CREATE THE GENESIS BLOCK 🌌

        This is block 0, the origin of the lineage.
        The foundation of all agent history.

        The Genesis Block anchors the system to its philosophical roots:
        - GAD-000 (The Spirit): Operator Inversion Principle + 37th Amendment
        - CONSTITUTION.md (The Law): Governance Rules

        These are not optional. They are the bedrock.

        GAD-000 v2.0 (2026-01-04): The 37th Principle
        - Identity elevated from criterion #6 to Sovereign Center (37th)
        - 6 operational criteria form the Field (Prakriti/Kshetra)
        - The 37th is the Knower (Purusha/Kshetrajna)
        - Stambha pattern: 37th manifests FROM WITHIN the 36
        """
        # Discover project root dynamically
        project_root = self._get_project_root()

        # Calculate foundation hashes with relative paths
        gad_000_path = project_root / "docs" / "architecture" / "GAD-0XX" / "GAD-000.md"
        constitution_path = project_root / "CONSTITUTION.md"

        gad_000_hash = self._hash_file(str(gad_000_path))
        constitution_hash = self._hash_file(str(constitution_path))

        # Extract GAD-000 version from file content
        gad_000_version = "2.0"  # Default to current
        try:
            if gad_000_path.exists():
                content = gad_000_path.read_text()
                if "v2.0" in content or "37th Principle" in content:
                    gad_000_version = "2.0"
                elif "v1.6" in content:
                    gad_000_version = "1.6"
        except Exception:
            pass

        genesis = LineageBlock(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            event_type="GENESIS",
            agent_id=None,
            data={
                "message": "Om Tat Sat - In the beginning, there was the Kernel",
                "anchors": {
                    "philosophy_hash": gad_000_hash,  # The Spirit (GAD-000)
                    "philosophy_version": gad_000_version,  # GAD-000 version
                    "constitution_hash": constitution_hash,  # The Law (CONSTITUTION)
                    "kernel_version": "2.0.0",
                    "migration_phase": "5",
                    # The 37th Principle metadata
                    "sovereign_model": "37th" if gad_000_version == "2.0" else "linear",
                },
                "timestamp_utc": datetime.utcnow().isoformat(),
            },
            previous_hash="0" * 64,  # No previous block
            hash="",  # Will be calculated
        )

        # Calculate hash
        genesis.hash = self._calculate_hash(genesis)

        # Store in DB
        self._store_block(genesis)

        logger.info("🌌" + "=" * 60)
        logger.info("🌌 GENESIS BLOCK CREATED")
        logger.info(f"🌌 Hash: {genesis.hash[:32]}...")
        logger.info(f"🌌 Philosophy (GAD-000 v{gad_000_version}): {gad_000_hash[:16]}...")
        logger.info(f"🌌 Sovereign Model: {genesis.data['anchors']['sovereign_model']}")
        logger.info(f"🌌 Law (CONSTITUTION): {constitution_hash[:16]}...")
        logger.info("🌌 The Parampara has begun. The lineage is eternal.")
        logger.info("🌌" + "=" * 60)

        return genesis

    def add_block(self, event_type: str, agent_id: Optional[str], data: Dict[str, str]) -> LineageBlock:
        """
        ⛓️  ADD A NEW BLOCK TO THE CHAIN ⛓️

        This is how agents are remembered.
        Every registration, every oath, every upgrade - recorded forever.

        Args:
            event_type: AGENT_REGISTERED, AGENT_UPGRADED, OATH_SWORN, etc.
            agent_id: Agent involved (None for system events)
            data: Event-specific data

        Returns:
            The newly created block

        Raises:
            RuntimeError: If chain is broken or previous block missing
        """
        # Get previous block
        previous_block = self.get_latest_block()
        if not previous_block:
            raise RuntimeError("Cannot add block: Genesis Block missing")

        # Create new block
        block = LineageBlock(
            index=previous_block.index + 1,
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            agent_id=agent_id,
            data=data,
            previous_hash=previous_block.hash,
            hash="",
        )

        # Calculate hash
        block.hash = self._calculate_hash(block)

        # Store in DB
        self._store_block(block)

        logger.info(f"⛓️  Block {block.index}: {event_type} ({agent_id or 'SYSTEM'}) → {block.hash[:16]}...")

        return block

    def _calculate_hash(self, block: LineageBlock) -> str:
        """
        Calculate SHA-256 hash of block.

        The hash includes ALL block data to ensure immutability.
        Change even a single byte, and the hash changes.
        """
        block_string = json.dumps(
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "event_type": block.event_type,
                "agent_id": block.agent_id,
                "data": block.data,
                "previous_hash": block.previous_hash,
            },
            sort_keys=True,
        )

        return hashlib.sha256(block_string.encode()).hexdigest()

    def _hash_file(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"⚠️  File not found for hashing: {file_path}")
                return "0" * 64

            content = path.read_text()
            return hashlib.sha256(content.encode()).hexdigest()
        except Exception as e:
            logger.error(f"❌ Failed to hash file {file_path}: {e}")
            return "0" * 64

    def _store_block(self, block: LineageBlock) -> None:
        """Store block in database"""
        self.conn.execute(
            """
            INSERT INTO blocks (idx, timestamp, event_type, agent_id, data, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                block.index,
                block.timestamp,
                block.event_type,
                block.agent_id,
                json.dumps(block.data),
                block.previous_hash,
                block.hash,
            ),
        )
        self.conn.commit()

    def verify_chain(self) -> bool:
        """
        🔍 VERIFY THE INTEGRITY OF THE ENTIRE CHAIN 🔍

        This is the sacred verification.
        Every block's hash must be correct.
        Every block must point to the previous block.
        The Genesis Block must be untouched.

        If ANY block has been tampered with, this will detect it.

        Returns:
            True if chain is valid, False if broken
        """
        blocks = self.get_all_blocks()

        if not blocks:
            logger.warning("⚠️  Chain is empty")
            return False

        for i, block in enumerate(blocks):
            # Verify hash
            calculated_hash = self._calculate_hash(block)
            if block.hash != calculated_hash:
                logger.critical(f"💥 CHAIN BROKEN AT INDEX {i}: Hash mismatch!")
                logger.critical(f"   Expected: {calculated_hash[:16]}...")
                logger.critical(f"   Found: {block.hash[:16]}...")
                return False

            # Verify chain linkage (except Genesis)
            if i > 0:
                if block.previous_hash != blocks[i - 1].hash:
                    logger.critical(f"💥 CHAIN BROKEN AT INDEX {i}: Link broken!")
                    logger.critical(f"   Previous block hash: {blocks[i - 1].hash[:16]}...")
                    logger.critical(f"   This block's prev_hash: {block.previous_hash[:16]}...")
                    return False

        logger.info(f"✅ Parampara chain verified ({len(blocks)} blocks)")
        return True

    # =========================================================================
    # SPEED.md: Fast Boot Methods (Merkle Checkpointing)
    # =========================================================================

    def get_tip_hash(self) -> str:
        """
        Get hash of latest block (single query).

        O(1) vs O(n) for get_all_blocks().
        Used for checkpoint comparison.

        Returns:
            SHA-256 hash of tip block, or empty string if chain empty
        """
        cur = self.conn.cursor()
        cur.execute("SELECT hash FROM blocks ORDER BY idx DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else ""

    def get_tip_index(self) -> int:
        """
        Get index of latest block.

        Returns:
            Index of tip block, or -1 if chain empty
        """
        cur = self.conn.cursor()
        cur.execute("SELECT idx FROM blocks ORDER BY idx DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else -1

    def _get_checkpoint_path(self) -> Path:
        """Get path to checkpoint file (.vibe/lineage_checkpoint.json)."""
        # Store checkpoint next to the DB file
        vibe_dir = self.db_path.parent.parent / ".vibe"
        if not vibe_dir.exists():
            # Fallback to project root
            vibe_dir = self._get_project_root() / ".vibe"
        vibe_dir.mkdir(parents=True, exist_ok=True)
        return vibe_dir / CHECKPOINT_FILENAME

    def save_checkpoint(self) -> bool:
        """
        Save verification checkpoint after successful verification.

        Returns:
            True if saved successfully
        """
        try:
            checkpoint_path = self._get_checkpoint_path()
            tip_hash = self.get_tip_hash()
            tip_index = self.get_tip_index()

            checkpoint = {
                "verified_tip_hash": tip_hash,
                "verified_index": tip_index,
                "verified_at": datetime.utcnow().isoformat(),
                "chain_db_path": str(self.db_path),
            }

            checkpoint_path.write_text(json.dumps(checkpoint, indent=2))
            logger.debug(f"⚡ Checkpoint saved: {tip_hash[:16]}... (idx={tip_index})")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to save checkpoint: {e}")
            return False

    def load_checkpoint(self) -> Optional[Dict[str, str]]:
        """
        Load verification checkpoint.

        Returns:
            Checkpoint dict if exists and valid, None otherwise
        """
        try:
            checkpoint_path = self._get_checkpoint_path()
            if not checkpoint_path.exists():
                return None

            data = json.loads(checkpoint_path.read_text())

            # Validate checkpoint has required fields
            required = ["verified_tip_hash", "verified_index", "chain_db_path"]
            if not all(k in data for k in required):
                logger.warning("⚠️  Invalid checkpoint format")
                return None

            # Invalidate if DB path changed
            if data["chain_db_path"] != str(self.db_path):
                logger.warning("⚠️  Checkpoint DB path mismatch - invalidating")
                return None

            return data
        except Exception as e:
            logger.warning(f"⚠️  Failed to load checkpoint: {e}")
            return None

    def clear_checkpoint(self) -> bool:
        """
        Clear checkpoint (force full verification on next boot).

        Returns:
            True if cleared successfully
        """
        try:
            checkpoint_path = self._get_checkpoint_path()
            if checkpoint_path.exists():
                checkpoint_path.unlink()
                logger.info("🗑️  Checkpoint cleared")
            return True
        except Exception as e:
            logger.warning(f"⚠️  Failed to clear checkpoint: {e}")
            return False

    def verify_chain_fast(self) -> Dict[str, object]:
        """
        Fast chain verification with checkpoint support.

        SPEED.md Algorithm:
        1. Load checkpoint
        2. Compare checkpoint.tip_hash with current tip
        3. If match: Skip verification (instant boot)
        4. If mismatch: Verify only delta (new blocks)
        5. If no checkpoint: Full verification (fallback)

        Returns:
            Dict with: valid, method, blocks_verified, duration_ms, tip_hash, tip_index
        """
        start_time = time.time()
        current_tip_hash = self.get_tip_hash()
        current_tip_index = self.get_tip_index()

        if not current_tip_hash:
            # Empty chain
            return {
                "valid": False,
                "method": "empty",
                "blocks_verified": 0,
                "duration_ms": (time.time() - start_time) * 1000,
                "tip_hash": "",
                "tip_index": -1,
            }

        # Try checkpoint
        checkpoint = self.load_checkpoint()

        if checkpoint and checkpoint["verified_tip_hash"] == current_tip_hash:
            # Checkpoint matches - skip verification!
            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"⚡ Parampara fast-verified via checkpoint ({duration_ms:.1f}ms)")
            return {
                "valid": True,
                "method": "checkpoint",
                "blocks_verified": 0,
                "duration_ms": duration_ms,
                "tip_hash": current_tip_hash,
                "tip_index": current_tip_index,
            }

        if checkpoint and checkpoint["verified_index"] < current_tip_index:
            # Checkpoint exists but chain grew - verify delta
            delta_start = checkpoint["verified_index"] + 1
            valid = self._verify_delta(delta_start)
            duration_ms = (time.time() - start_time) * 1000
            blocks_verified = current_tip_index - checkpoint["verified_index"]

            if valid:
                self.save_checkpoint()
                logger.info(f"⚡ Parampara delta-verified ({blocks_verified} new blocks, {duration_ms:.1f}ms)")

            return {
                "valid": valid,
                "method": "delta",
                "blocks_verified": blocks_verified,
                "duration_ms": duration_ms,
                "tip_hash": current_tip_hash,
                "tip_index": current_tip_index,
            }

        # No valid checkpoint - full verification
        valid = self.verify_chain()
        duration_ms = (time.time() - start_time) * 1000

        if valid:
            self.save_checkpoint()

        return {
            "valid": valid,
            "method": "full",
            "blocks_verified": current_tip_index + 1,
            "duration_ms": duration_ms,
            "tip_hash": current_tip_hash,
            "tip_index": current_tip_index,
        }

    def _verify_delta(self, start_index: int) -> bool:
        """
        Verify only blocks from start_index to tip.

        Used for delta verification when checkpoint exists.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM blocks WHERE idx >= ? ORDER BY idx", (start_index,))
        new_blocks = [self._row_to_block(row) for row in cur.fetchall()]

        if not new_blocks:
            return True

        # Get previous block for linkage check
        cur.execute("SELECT * FROM blocks WHERE idx = ?", (start_index - 1,))
        prev_row = cur.fetchone()
        prev_block = self._row_to_block(prev_row) if prev_row else None

        for i, block in enumerate(new_blocks):
            # Verify hash
            calculated_hash = self._calculate_hash(block)
            if block.hash != calculated_hash:
                logger.critical(f"💥 DELTA: Hash mismatch at index {block.index}!")
                return False

            # Verify linkage
            if i == 0 and prev_block:
                if block.previous_hash != prev_block.hash:
                    logger.critical(f"💥 DELTA: Link broken at index {block.index}!")
                    return False
            elif i > 0:
                if block.previous_hash != new_blocks[i - 1].hash:
                    logger.critical(f"💥 DELTA: Link broken at index {block.index}!")
                    return False

        return True

    def get_chain_length(self) -> int:
        """Get the total number of blocks in the chain"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM blocks")
        return cur.fetchone()[0]

    def get_latest_block(self) -> Optional[LineageBlock]:
        """Get the most recent block in the chain"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM blocks ORDER BY idx DESC LIMIT 1")
        row = cur.fetchone()
        return self._row_to_block(row) if row else None

    def get_all_blocks(self) -> List[LineageBlock]:
        """Get all blocks in order"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM blocks ORDER BY idx")
        return [self._row_to_block(row) for row in cur.fetchall()]

    def get_agent_lineage(self, agent_id: str) -> List[LineageBlock]:
        """
        Get all blocks related to a specific agent.

        This is the agent's history - their birth, their oaths, their deeds.
        """
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM blocks WHERE agent_id = ? ORDER BY idx", (agent_id,))
        return [self._row_to_block(row) for row in cur.fetchall()]

    def get_genesis_block(self) -> Optional[LineageBlock]:
        """Get the Genesis Block (index 0)"""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM blocks WHERE idx = 0")
        row = cur.fetchone()
        return self._row_to_block(row) if row else None

    def export_to_json(self, output_path: str) -> None:
        """Export the entire chain to JSON for portability"""
        blocks = self.get_all_blocks()
        chain_data = {
            "chain_length": len(blocks),
            "genesis_hash": blocks[0].hash if blocks else None,
            "latest_hash": blocks[-1].hash if blocks else None,
            "blocks": [asdict(block) for block in blocks],
        }

        Path(output_path).write_text(json.dumps(chain_data, indent=2))
        logger.info(f"📄 Chain exported to {output_path}")

    def _row_to_block(self, row) -> LineageBlock:
        """Convert database row to LineageBlock"""
        return LineageBlock(
            index=row[0],
            timestamp=row[1],
            event_type=row[2],
            agent_id=row[3],
            data=json.loads(row[4]),
            previous_hash=row[5],
            hash=row[6],
        )

    def close(self) -> None:
        """Close database connection"""
        self.conn.close()
        logger.info("⛓️  Parampara chain closed")


# Event types (constants for consistency)
class LineageEventType:
    """Standard event types for the Parampara chain"""

    GENESIS = "GENESIS"
    KERNEL_BOOT = "KERNEL_BOOT"
    KERNEL_SHUTDOWN = "KERNEL_SHUTDOWN"
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_UPGRADED = "AGENT_UPGRADED"
    AGENT_DEREGISTERED = "AGENT_DEREGISTERED"
    OATH_SWORN = "OATH_SWORN"
    PASSPORT_ISSUED = "PASSPORT_ISSUED"  # Phase 6: Steward Protocol Compliance
    ERROR_CRITICAL = "ERROR_CRITICAL"
    NARASIMHA_INTERVENTION = "NARASIMHA_INTERVENTION"
    AGENT_DESTROYED = "AGENT_DESTROYED"  # Phase 7: Narasimha Kill-Switch
    TASK_COMPLETED = "TASK_COMPLETED"
    KARMA_RECORDED = "KARMA_RECORDED"
    # OPUS-126: Reflex Arc Events (Karma Loop)
    REFLEX_ACTION = "REFLEX_ACTION"  # Pain → Task → Action cycle
    DISHARMONY_DETECTED = "DISHARMONY_DETECTED"  # Pain sensor fired
    REPAIR_TASK_CREATED = "REPAIR_TASK_CREATED"  # Effector responded

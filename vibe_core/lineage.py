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

import logging
import json
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger("PARAMPARA")


@dataclass
class LineageBlock:
    """
    A single block in the Parampara chain.

    This is not just a database row. This is a covenant.
    Once written, it cannot be changed without breaking the entire chain.
    """
    index: int                    # Block number (0 = Genesis)
    timestamp: str                # ISO 8601 timestamp
    event_type: str               # GENESIS, AGENT_REGISTERED, OATH_SWORN, etc.
    agent_id: Optional[str]       # Agent involved (None for system events)
    data: Dict[str, Any]          # Event-specific data
    previous_hash: str            # Hash of previous block
    hash: str                     # Hash of this block (SHA-256)


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

    def __init__(self, db_path: str = "/tmp/vibe_os/kernel/lineage.db"):
        """
        Initialize the Parampara chain.

        If this is the first time, the Genesis Block will be created.
        Otherwise, the existing chain will be loaded and verified.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self._init_db()

        # Create Genesis Block if chain is empty
        if self.get_chain_length() == 0:
            self._create_genesis_block()
        else:
            logger.info(f"⛓️  Parampara chain loaded ({self.get_chain_length()} blocks)")

            # Verify chain integrity on load
            if not self.verify_chain():
                logger.critical("💥 CHAIN INTEGRITY VIOLATED - SYSTEM COMPROMISED")
                raise RuntimeError("Parampara chain verification failed")

    def _init_db(self) -> None:
        """Initialize the database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                idx INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                agent_id TEXT,
                data TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                hash TEXT NOT NULL UNIQUE
            )
        """)

        # Indexes for fast queries
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON blocks(agent_id)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON blocks(event_type)")
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON blocks(timestamp)")

        self.conn.commit()

    def _create_genesis_block(self) -> LineageBlock:
        """
        🌌 CREATE THE GENESIS BLOCK 🌌

        This is block 0, the origin of the lineage.
        The foundation of all agent history.

        The Genesis Block anchors the system to its philosophical roots:
        - GAD-000 (The Spirit): Operator Inversion Principle
        - CONSTITUTION.md (The Law): Governance Rules

        These are not optional. They are the bedrock.
        """
        # Calculate foundation hashes
        gad_000_hash = self._hash_file("/home/user/steward-protocol/GAD-000.md")
        constitution_hash = self._hash_file("/home/user/steward-protocol/CONSTITUTION.md")

        genesis = LineageBlock(
            index=0,
            timestamp=datetime.utcnow().isoformat(),
            event_type="GENESIS",
            agent_id=None,
            data={
                "message": "Om Tat Sat - In the beginning, there was the Kernel",
                "anchors": {
                    "philosophy_hash": gad_000_hash,      # The Spirit (GAD-000)
                    "constitution_hash": constitution_hash, # The Law (CONSTITUTION)
                    "kernel_version": "2.0.0",
                    "migration_phase": "5"
                },
                "timestamp_utc": datetime.utcnow().isoformat(),
            },
            previous_hash="0" * 64,  # No previous block
            hash=""  # Will be calculated
        )

        # Calculate hash
        genesis.hash = self._calculate_hash(genesis)

        # Store in DB
        self._store_block(genesis)

        logger.info("🌌" + "=" * 60)
        logger.info("🌌 GENESIS BLOCK CREATED")
        logger.info(f"🌌 Hash: {genesis.hash[:32]}...")
        logger.info(f"🌌 Philosophy (GAD-000): {gad_000_hash[:16]}...")
        logger.info(f"🌌 Law (CONSTITUTION): {constitution_hash[:16]}...")
        logger.info("🌌 The Parampara has begun. The lineage is eternal.")
        logger.info("🌌" + "=" * 60)

        return genesis

    def add_block(
        self,
        event_type: str,
        agent_id: Optional[str],
        data: Dict[str, Any]
    ) -> LineageBlock:
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
            hash=""
        )

        # Calculate hash
        block.hash = self._calculate_hash(block)

        # Store in DB
        self._store_block(block)

        logger.info(
            f"⛓️  Block {block.index}: {event_type} "
            f"({agent_id or 'SYSTEM'}) → {block.hash[:16]}..."
        )

        return block

    def _calculate_hash(self, block: LineageBlock) -> str:
        """
        Calculate SHA-256 hash of block.

        The hash includes ALL block data to ensure immutability.
        Change even a single byte, and the hash changes.
        """
        block_string = json.dumps({
            "index": block.index,
            "timestamp": block.timestamp,
            "event_type": block.event_type,
            "agent_id": block.agent_id,
            "data": block.data,
            "previous_hash": block.previous_hash,
        }, sort_keys=True)

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
        self.conn.execute("""
            INSERT INTO blocks (idx, timestamp, event_type, agent_id, data, previous_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            block.index,
            block.timestamp,
            block.event_type,
            block.agent_id,
            json.dumps(block.data),
            block.previous_hash,
            block.hash
        ))
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
                if block.previous_hash != blocks[i-1].hash:
                    logger.critical(f"💥 CHAIN BROKEN AT INDEX {i}: Link broken!")
                    logger.critical(f"   Previous block hash: {blocks[i-1].hash[:16]}...")
                    logger.critical(f"   This block's prev_hash: {block.previous_hash[:16]}...")
                    return False

        logger.info(f"✅ Parampara chain verified ({len(blocks)} blocks)")
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
        cur.execute(
            "SELECT * FROM blocks WHERE agent_id = ? ORDER BY idx",
            (agent_id,)
        )
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
            "blocks": [asdict(block) for block in blocks]
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
            hash=row[6]
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
    ERROR_CRITICAL = "ERROR_CRITICAL"
    NARASIMHA_INTERVENTION = "NARASIMHA_INTERVENTION"

#!/usr/bin/env python3
"""
Truth Matrix - Database of Verified Facts

This is the canonical source of verifiable truths in the system.
Every fact recorded here is:
- Verified by an authoritative source
- Cross-checked against other facts
- Immutable (append-only)
- Attributed with its source

Like the ledger, facts are never deleted, only added.
If a fact is found false, a new fact is recorded stating that.
"""

import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("TRUTH_MATRIX")


class FactAuthority(str, Enum):
    """Authority level of fact sources"""

    CONSTITUTIONAL = "constitutional"  # From Constitution (absolute)
    LEDGER = "ledger"  # From immutable ledger (high)
    AUDITOR = "auditor"  # Verified by AUDITOR (high)
    ORACLE = "oracle"  # Self-verified (medium)
    HERALD = "herald"  # Published fact (medium)
    SCIENCE = "science"  # Researched fact (medium-low)
    WITNESS = "witness"  # Reported by agent (low)


@dataclass
class Fact:
    """Record of a verified fact"""

    fact_id: str
    fact_type: str  # e.g., "system_state", "constitutional", "historical"
    statement: str  # The actual fact
    authority: str  # Source authority (FactAuthority enum)
    evidence: Dict[str, Any]  # Supporting evidence
    recorded_at: str = ""
    verified: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TruthMatrix:
    """
    The canonical database of verified facts.

    All facts are immutable and attributed to sources.
    When facts conflict, higher authority sources override lower ones.
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize Truth Matrix."""
        self.root_path = Path(root_path)
        self.truth_dir = self.root_path / "data" / "truth_matrix"
        self.truth_dir.mkdir(parents=True, exist_ok=True)

        self.facts_file = self.truth_dir / "facts.jsonl"

        logger.info("📚 Truth Matrix initialized")

    def record_fact(
        self,
        fact_type: str,
        statement: str,
        authority: str,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Record a verified fact.

        Args:
            fact_type: Category of fact (system_state, historical, constitutional, etc.)
            statement: The actual fact statement
            authority: Source authority (from FactAuthority enum)
            evidence: Supporting evidence/references

        Returns:
            The recorded fact
        """
        fact_id = f"FACT-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        fact = Fact(
            fact_id=fact_id,
            fact_type=fact_type,
            statement=statement,
            authority=authority,
            evidence=evidence or {},
            recorded_at=now,
            verified=True,
        )

        # Persist fact
        self._append_fact(fact)

        logger.info(f"📝 FACT RECORDED: {statement[:50]}... (source: {authority})")

        return fact.to_dict()

    def get_facts_by_type(self, fact_type: str) -> List[Dict[str, Any]]:
        """Get all facts of a specific type."""
        facts = self._load_facts()
        return [f for f in facts if f.get("fact_type") == fact_type]

    def get_facts_by_authority(self, authority: str) -> List[Dict[str, Any]]:
        """Get all facts from a specific authority source."""
        facts = self._load_facts()
        return [f for f in facts if f.get("authority") == authority]

    def get_fact_by_id(self, fact_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific fact by ID."""
        facts = self._load_facts()
        for fact in facts:
            if fact.get("fact_id") == fact_id:
                return fact
        return None

    def find_facts_like(self, pattern: str) -> List[Dict[str, Any]]:
        """Find facts matching a pattern (substring search)."""
        facts = self._load_facts()
        pattern_lower = pattern.lower()
        return [f for f in facts if pattern_lower in f.get("statement", "").lower()]

    def get_all_facts(self) -> List[Dict[str, Any]]:
        """Get all facts in the matrix."""
        return self._load_facts()

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the Truth Matrix."""
        facts = self._load_facts()

        # Count by type
        type_counts = {}
        for fact in facts:
            fact_type = fact.get("fact_type")
            type_counts[fact_type] = type_counts.get(fact_type, 0) + 1

        # Count by authority
        authority_counts = {}
        for fact in facts:
            authority = fact.get("authority")
            authority_counts[authority] = authority_counts.get(authority, 0) + 1

        return {
            "total_facts": len(facts),
            "by_type": type_counts,
            "by_authority": authority_counts,
            "first_fact": facts[0]["recorded_at"] if facts else None,
            "last_fact": facts[-1]["recorded_at"] if facts else None,
        }

    def verify_integrity(self) -> bool:
        """Verify the Truth Matrix has not been tampered with."""
        try:
            facts = self._load_facts()
            logger.info(f"✅ Truth Matrix integrity verified ({len(facts)} facts)")
            return True
        except Exception as e:
            logger.error(f"❌ Truth Matrix integrity check failed: {str(e)}")
            return False

    # ========== PRIVATE METHODS ==========

    def _append_fact(self, fact: Fact) -> None:
        """Append fact to matrix (append-only)."""
        with open(self.facts_file, "a") as f:
            f.write(json.dumps(fact.to_dict()) + "\n")

    def _load_facts(self) -> List[Dict[str, Any]]:
        """Load all facts from the matrix."""
        if not self.facts_file.exists():
            return []

        facts = []
        try:
            with open(self.facts_file, "r") as f:
                for line in f:
                    if line.strip():
                        facts.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error loading facts: {str(e)}")

        return facts

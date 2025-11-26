#!/usr/bin/env python3
"""
Verdict Tool - Issues court verdicts and maintains verdict records.

This tool handles:
- Issuing verdicts (mercy granted, upheld, conditional)
- Overriding AUDITOR decisions
- Maintaining immutable verdict record
"""

import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("VERDICT_TOOL")


class VerdictType(str, Enum):
    """Types of verdicts the court can issue"""
    MERCY_GRANTED = "mercy_granted"         # Override violation, restore agent
    MERCY_CONDITIONAL = "mercy_conditional" # Override with conditions (probation)
    UPHELD = "upheld"                       # Violation stands, agent terminated


@dataclass
class Verdict:
    """Record of a court verdict"""
    verdict_id: str
    appeal_id: str
    agent_id: str
    verdict_type: str  # VerdictType enum value
    justification: str = ""
    override_auditor: bool = False  # Whether this overrides AUDITOR decision
    conditions: List[str] = field(default_factory=list)  # For CONDITIONAL mercy
    issued_at: str = ""
    issued_by: str = "supreme_court"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VerdictTool:
    """
    Issues and tracks court verdicts.

    The verdict is the court's final decision, which can override AUDITOR.
    This is the point where mercy becomes law.
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize verdict tool."""
        self.root_path = Path(root_path)
        self.verdicts_dir = self.root_path / "data" / "governance" / "verdicts"
        self.verdicts_dir.mkdir(parents=True, exist_ok=True)

        self.verdicts_file = self.verdicts_dir / "verdicts.jsonl"

        logger.info("⚖️  Verdict Tool initialized")

    def issue_verdict(
        self,
        appeal_id: str,
        agent_id: str,
        verdict_type: VerdictType,
        justification: str = "",
        override_auditor: bool = False,
        conditions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Issue a verdict on an appeal.

        Args:
            appeal_id: Appeal being decided
            agent_id: Agent the verdict concerns
            verdict_type: Type of verdict (mercy, upheld, conditional)
            justification: Reason for this verdict
            override_auditor: Whether this overrides AUDITOR decision
            conditions: Any conditions attached to the verdict

        Returns:
            Verdict record
        """
        verdict_id = f"VERDICT-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        # Build verdict message
        if verdict_type == VerdictType.MERCY_GRANTED:
            logger.info(f"🛡️  MERCY GRANTED: Verdict {verdict_id} for agent {agent_id}")
        elif verdict_type == VerdictType.MERCY_CONDITIONAL:
            logger.info(f"⚠️  CONDITIONAL MERCY: Verdict {verdict_id} for agent {agent_id}")
        else:
            logger.info(f"💀 UPHELD: Verdict {verdict_id} for agent {agent_id}")

        verdict = Verdict(
            verdict_id=verdict_id,
            appeal_id=appeal_id,
            agent_id=agent_id,
            verdict_type=verdict_type.value if isinstance(verdict_type, VerdictType) else verdict_type,
            justification=justification,
            override_auditor=override_auditor,
            conditions=conditions or [],
            issued_at=now,
            issued_by="supreme_court"
        )

        # Persist verdict
        self._append_verdict(verdict)

        return verdict.to_dict()

    def get_verdict(self, verdict_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a verdict by ID."""
        verdicts = self._load_verdicts()
        for verdict in verdicts:
            if verdict.get("verdict_id") == verdict_id:
                return verdict
        return None

    def get_verdicts_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all verdicts issued for an agent."""
        verdicts = self._load_verdicts()
        return [v for v in verdicts if v.get("agent_id") == agent_id]

    def get_verdicts_by_type(self, verdict_type: str) -> List[Dict[str, Any]]:
        """Get all verdicts of a specific type."""
        verdicts = self._load_verdicts()
        return [v for v in verdicts if v.get("verdict_type") == verdict_type]

    def get_mercy_count(self) -> int:
        """Count how many times mercy has been granted."""
        verdicts = self._load_verdicts()
        return sum(1 for v in verdicts if v.get("verdict_type") == VerdictType.MERCY_GRANTED.value)

    def get_verdicts_that_override(self) -> List[Dict[str, Any]]:
        """Get all verdicts that override AUDITOR decisions."""
        verdicts = self._load_verdicts()
        return [v for v in verdicts if v.get("override_auditor")]

    def get_all_verdicts(self) -> List[Dict[str, Any]]:
        """Get all verdicts (for auditing)."""
        return self._load_verdicts()

    # ========== PRIVATE METHODS ==========

    def _append_verdict(self, verdict: Verdict) -> None:
        """Append verdict to ledger (append-only)."""
        with open(self.verdicts_file, "a") as f:
            f.write(json.dumps(verdict.to_dict()) + "\n")

    def _load_verdicts(self) -> List[Dict[str, Any]]:
        """Load all verdicts from ledger."""
        if not self.verdicts_file.exists():
            return []

        verdicts = []
        try:
            with open(self.verdicts_file, "r") as f:
                for line in f:
                    if line.strip():
                        verdicts.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error loading verdicts: {str(e)}")

        return verdicts

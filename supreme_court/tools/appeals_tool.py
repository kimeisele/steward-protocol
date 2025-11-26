#!/usr/bin/env python3
"""
Appeals Tool - Manages the appeal submission and tracking system.

This tool handles:
- Appeal intake (agent files appeal)
- Appeal status tracking
- Appeal withdrawal or expiration
"""

import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("APPEALS_TOOL")


class AppealStatus(str, Enum):
    """Status of an appeal throughout its lifecycle"""
    FILED = "filed"                    # Initial submission
    UNDER_REVIEW = "under_review"     # Being examined by court
    HEARING_SCHEDULED = "hearing_scheduled"  # Waiting for hearing
    CLOSED = "closed"                 # Decision issued


@dataclass
class Appeal:
    """Record of a single appeal"""
    appeal_id: str
    agent_id: str
    violation_id: str
    status: str = AppealStatus.FILED.value
    justification: str = ""
    has_oath: bool = False
    findings: Optional[Dict[str, Any]] = None
    mercy_eligible: Optional[bool] = None
    verdict_id: Optional[str] = None
    filed_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AppealsTool:
    """
    Manages appeals in the Supreme Court system.

    This is the intake window for condemned agents seeking mercy.
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize appeals tool."""
        self.root_path = Path(root_path)
        self.appeals_dir = self.root_path / "data" / "governance" / "appeals"
        self.appeals_dir.mkdir(parents=True, exist_ok=True)

        self.appeals_file = self.appeals_dir / "appeals.jsonl"

        logger.info("📜 Appeals Tool initialized")

    def create_appeal(
        self,
        agent_id: str,
        violation_id: str,
        justification: str = "",
        has_oath: bool = False
    ) -> Dict[str, Any]:
        """
        File a new appeal.

        Args:
            agent_id: Agent filing the appeal
            violation_id: The AUDITOR violation being appealed
            justification: Why agent believes it deserves mercy
            has_oath: Whether agent has signed constitutional oath

        Returns:
            Appeal record
        """
        appeal_id = f"APPEAL-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        appeal = Appeal(
            appeal_id=appeal_id,
            agent_id=agent_id,
            violation_id=violation_id,
            status=AppealStatus.FILED.value,
            justification=justification,
            has_oath=has_oath,
            filed_at=now,
            updated_at=now
        )

        # Persist to ledger
        self._append_appeal(appeal)

        logger.info(f"📜 APPEAL CREATED: {appeal_id} for agent {agent_id}")

        return appeal.to_dict()

    def get_appeal(self, appeal_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an appeal by ID."""
        appeals = self._load_appeals()
        for appeal in appeals:
            if appeal.get("appeal_id") == appeal_id:
                return appeal
        return None

    def get_agent_appeals(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all appeals filed by an agent."""
        appeals = self._load_appeals()
        return [a for a in appeals if a.get("agent_id") == agent_id]

    def get_all_appeals(self) -> List[Dict[str, Any]]:
        """Get all appeals (for monitoring)."""
        return self._load_appeals()

    def update_appeal(self, appeal_id: str, updates: Dict[str, Any]) -> bool:
        """Update an appeal record."""
        appeals = self._load_appeals()

        for appeal in appeals:
            if appeal.get("appeal_id") == appeal_id:
                appeal.update(updates)
                appeal["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Rewrite all appeals
                self._rewrite_appeals(appeals)
                logger.info(f"✏️  APPEAL UPDATED: {appeal_id}")
                return True

        logger.warning(f"Appeal {appeal_id} not found for update")
        return False

    def get_appeals_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get appeals filtered by status."""
        appeals = self._load_appeals()
        return [a for a in appeals if a.get("status") == status]

    # ========== PRIVATE METHODS ==========

    def _append_appeal(self, appeal: Appeal) -> None:
        """Append appeal to ledger (append-only)."""
        with open(self.appeals_file, "a") as f:
            f.write(json.dumps(appeal.to_dict()) + "\n")

    def _load_appeals(self) -> List[Dict[str, Any]]:
        """Load all appeals from ledger."""
        if not self.appeals_file.exists():
            return []

        appeals = []
        try:
            with open(self.appeals_file, "r") as f:
                for line in f:
                    if line.strip():
                        appeals.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error loading appeals: {str(e)}")

        return appeals

    def _rewrite_appeals(self, appeals: List[Dict[str, Any]]) -> None:
        """Rewrite the appeals ledger (for updates)."""
        # For now, we write as JSONL. In production, this would be atomic.
        with open(self.appeals_file, "w") as f:
            for appeal in appeals:
                f.write(json.dumps(appeal) + "\n")

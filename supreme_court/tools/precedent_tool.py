#!/usr/bin/env python3
"""
Precedent Tool - Maintains case law and legal precedents.

This tool builds the corpus of Supreme Court decisions.
Future appeals can cite similar precedents to argue for consistent outcomes.

In Vedic terms: This is the library of Dharma (cosmic law) application.
"""

import json
import uuid
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger("PRECEDENT_TOOL")


@dataclass
class PrecedentCase:
    """Record of a precedent-setting case"""
    case_id: str
    verdict_id: str
    appeal_id: str
    agent_id: str
    verdict_type: str  # mercy_granted, upheld, conditional
    justification: str
    category: str = "general"  # For classification (e.g., "first_offense", "repeated_violations")
    recorded_at: str = ""
    citations: int = 0  # How many times cited in future appeals

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PrecedentTool:
    """
    Builds and manages legal precedent library.

    This is where justice becomes predictable and consistent.
    Similar cases should have similar outcomes (unless circumstances differ).
    """

    def __init__(self, root_path: Path = Path(".")):
        """Initialize precedent tool."""
        self.root_path = Path(root_path)
        self.precedent_dir = self.root_path / "data" / "governance" / "precedents"
        self.precedent_dir.mkdir(parents=True, exist_ok=True)

        self.cases_file = self.precedent_dir / "precedents.jsonl"

        logger.info("📚 Precedent Tool initialized")

    def record_case(
        self,
        verdict_id: str,
        appeal_id: str,
        agent_id: str,
        verdict_type: str,
        justification: str,
        category: str = "general"
    ) -> Dict[str, Any]:
        """
        Record a verdict as legal precedent.

        Important: Not all verdicts become precedent - only significant ones.
        This is a simplified version that records all verdicts.

        Args:
            verdict_id: The verdict being recorded
            appeal_id: Associated appeal
            agent_id: Agent involved
            verdict_type: Type of verdict (mercy_granted, upheld, conditional)
            justification: Court's reasoning
            category: Classification for future matching

        Returns:
            Precedent case record
        """
        case_id = f"CASE-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        case = PrecedentCase(
            case_id=case_id,
            verdict_id=verdict_id,
            appeal_id=appeal_id,
            agent_id=agent_id,
            verdict_type=verdict_type,
            justification=justification,
            category=category,
            recorded_at=now,
            citations=0
        )

        # Persist case
        self._append_case(case)

        logger.info(f"📚 PRECEDENT CASE RECORDED: {case_id} ({verdict_type})")

        return case.to_dict()

    def find_similar_cases(
        self,
        violation_type: Optional[str] = None,
        agent_type: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar precedent cases for comparison.

        This is used during MERCY INVESTIGATION to see what similar
        cases resulted in. It helps ensure consistency.

        Args:
            violation_type: Type of violation to match
            agent_type: Type of agent to match
            category: Category to match

        Returns:
            List of similar precedent cases
        """
        cases = self._load_cases()

        similar = cases
        if category:
            similar = [c for c in similar if c.get("category") == category]

        # Could add more sophisticated matching here
        logger.info(f"Found {len(similar)} similar precedent cases")

        return similar

    def get_precedent_cases(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get precedent cases, optionally filtered by category."""
        cases = self._load_cases()

        if category:
            cases = [c for c in cases if c.get("category") == category]

        return cases

    def get_mercy_precedents(self) -> List[Dict[str, Any]]:
        """Get all precedents where mercy was granted."""
        cases = self._load_cases()
        return [c for c in cases if c.get("verdict_type") == "mercy_granted"]

    def get_case_by_verdict(self, verdict_id: str) -> Optional[Dict[str, Any]]:
        """Get precedent case for a specific verdict."""
        cases = self._load_cases()
        for case in cases:
            if case.get("verdict_id") == verdict_id:
                return case
        return None

    def cite_case(self, case_id: str) -> bool:
        """
        Increment citation count for a case.

        Used when a future appeal cites this precedent.
        Cases that are frequently cited become stronger authority.
        """
        cases = self._load_cases()

        for case in cases:
            if case.get("case_id") == case_id:
                case["citations"] = case.get("citations", 0) + 1
                self._rewrite_cases(cases)
                logger.info(f"Case {case_id} cited (total citations: {case['citations']})")
                return True

        return False

    def get_most_cited_cases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most-cited precedent cases."""
        cases = self._load_cases()
        # Sort by citations (descending)
        sorted_cases = sorted(cases, key=lambda c: c.get("citations", 0), reverse=True)
        return sorted_cases[:limit]

    # ========== PRIVATE METHODS ==========

    def _append_case(self, case: PrecedentCase) -> None:
        """Append case to ledger (append-only)."""
        with open(self.cases_file, "a") as f:
            f.write(json.dumps(case.to_dict()) + "\n")

    def _load_cases(self) -> List[Dict[str, Any]]:
        """Load all precedent cases."""
        if not self.cases_file.exists():
            return []

        cases = []
        try:
            with open(self.cases_file, "r") as f:
                for line in f:
                    if line.strip():
                        cases.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Error loading precedent cases: {str(e)}")

        return cases

    def _rewrite_cases(self, cases: List[Dict[str, Any]]) -> None:
        """Rewrite the cases ledger (for updates like citations)."""
        with open(self.cases_file, "w") as f:
            for case in cases:
                f.write(json.dumps(case) + "\n")

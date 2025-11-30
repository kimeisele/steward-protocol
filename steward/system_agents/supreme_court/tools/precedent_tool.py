#!/usr/bin/env python3
"""
Precedent Tool - Maintains case law and legal precedents.

This tool builds the corpus of Supreme Court decisions.
Future appeals can cite similar precedents to argue for consistent outcomes.

In Vedic terms: This is the library of Dharma (cosmic law) application.

Tool Protocol Compliant (Kernel-Managed).
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

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


class PrecedentTool(Tool):
    """
    Builds and manages legal precedent library.

    This is where justice becomes predictable and consistent.
    Similar cases should have similar outcomes (unless circumstances differ).

    Tool Protocol Compliant (Kernel-Managed).
    """

    def __init__(self):
        """Initialize precedent tool (kernel-managed)."""
        self._root_path = None
        logger.info("📚 Precedent Tool initialized")

    @property
    def name(self) -> str:
        return "supreme_court.precedent"

    @property
    def description(self) -> str:
        return "Manage legal precedents - record cases, find similar cases, track citations"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'record_case', 'find_similar', 'get_cases', 'get_mercy_precedents', 'get_by_verdict', 'cite_case', 'get_most_cited'",
            },
            "verdict_id": {
                "type": "string",
                "required": False,
                "description": "Verdict ID (required for record_case, get_by_verdict)",
            },
            "appeal_id": {
                "type": "string",
                "required": False,
                "description": "Appeal ID (required for record_case)",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for record_case)",
            },
            "verdict_type": {
                "type": "string",
                "required": False,
                "description": "Verdict type (required for record_case, optional for find_similar)",
            },
            "justification": {
                "type": "string",
                "required": False,
                "description": "Justification (required for record_case)",
            },
            "category": {
                "type": "string",
                "required": False,
                "description": "Case category (for record_case, get_cases, find_similar)",
            },
            "violation_type": {
                "type": "string",
                "required": False,
                "description": "Violation type (for find_similar)",
            },
            "agent_type": {
                "type": "string",
                "required": False,
                "description": "Agent type (for find_similar)",
            },
            "case_id": {
                "type": "string",
                "required": False,
                "description": "Case ID (required for cite_case)",
            },
            "limit": {
                "type": "integer",
                "required": False,
                "description": "Limit for get_most_cited (default: 10)",
            },
        }

    @property
    def root_path(self) -> Path:
        """Lazy-load root_path from system sandbox."""
        if self._root_path is None:
            self._root_path = Path(".") / "data" / "supreme_court"
            self._root_path.mkdir(parents=True, exist_ok=True)
        return self._root_path

    @property
    def precedent_dir(self) -> Path:
        """Get precedent directory."""
        precedent_dir = self.root_path / "data" / "governance" / "precedents"
        precedent_dir.mkdir(parents=True, exist_ok=True)
        return precedent_dir

    @property
    def cases_file(self) -> Path:
        """Get cases file path."""
        return self.precedent_dir / "precedents.jsonl"

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate precedent tool parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["record_case", "find_similar", "get_cases", "get_mercy_precedents", "get_by_verdict", "cite_case", "get_most_cited"]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action == "record_case":
            required = ["verdict_id", "appeal_id", "agent_id", "verdict_type", "justification"]
            for param in required:
                if param not in parameters:
                    raise ValueError(f"action 'record_case' requires '{param}' parameter")

        if action == "get_by_verdict" and "verdict_id" not in parameters:
            raise ValueError("action 'get_by_verdict' requires 'verdict_id' parameter")

        if action == "cite_case" and "case_id" not in parameters:
            raise ValueError("action 'cite_case' requires 'case_id' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute precedent tool operation."""
        try:
            action = parameters["action"]

            if action == "record_case":
                result = self.record_case(
                    verdict_id=parameters["verdict_id"],
                    appeal_id=parameters["appeal_id"],
                    agent_id=parameters["agent_id"],
                    verdict_type=parameters["verdict_type"],
                    justification=parameters["justification"],
                    category=parameters.get("category", "general"),
                )
                return ToolResult(success=True, output=result)

            elif action == "find_similar":
                result = self.find_similar_cases(
                    violation_type=parameters.get("violation_type"),
                    agent_type=parameters.get("agent_type"),
                    category=parameters.get("category"),
                )
                return ToolResult(success=True, output=result)

            elif action == "get_cases":
                result = self.get_precedent_cases(category=parameters.get("category"))
                return ToolResult(success=True, output=result)

            elif action == "get_mercy_precedents":
                result = self.get_mercy_precedents()
                return ToolResult(success=True, output=result)

            elif action == "get_by_verdict":
                result = self.get_case_by_verdict(parameters["verdict_id"])
                if result is None:
                    return ToolResult(success=False, error=f"No case found for verdict {parameters['verdict_id']}")
                return ToolResult(success=True, output=result)

            elif action == "cite_case":
                result = self.cite_case(parameters["case_id"])
                if not result:
                    return ToolResult(success=False, error=f"Failed to cite case {parameters['case_id']}")
                return ToolResult(success=True, output={"cited": True})

            elif action == "get_most_cited":
                limit = parameters.get("limit", 10)
                result = self.get_most_cited_cases(limit=limit)
                return ToolResult(success=True, output=result)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Precedent tool execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    def record_case(
        self,
        verdict_id: str,
        appeal_id: str,
        agent_id: str,
        verdict_type: str,
        justification: str,
        category: str = "general",
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
            citations=0,
        )

        # Persist case
        self._append_case(case)

        logger.info(f"📚 PRECEDENT CASE RECORDED: {case_id} ({verdict_type})")

        return case.to_dict()

    def find_similar_cases(
        self,
        violation_type: Optional[str] = None,
        agent_type: Optional[str] = None,
        category: Optional[str] = None,
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

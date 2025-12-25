#!/usr/bin/env python3
"""
Verdict Tool - Issues court verdicts and maintains verdict records.

This tool handles:
- Issuing verdicts (mercy granted, upheld, conditional)
- Overriding AUDITOR decisions
- Maintaining immutable verdict record

Tool Protocol Compliant (Kernel-Managed).
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("VERDICT_TOOL")


class VerdictType(str, Enum):
    """Types of verdicts the court can issue"""

    MERCY_GRANTED = "mercy_granted"  # Override violation, restore agent
    MERCY_CONDITIONAL = "mercy_conditional"  # Override with conditions (probation)
    UPHELD = "upheld"  # Violation stands, agent terminated


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


class VerdictTool(Tool):
    """
    Issues and tracks court verdicts.

    The verdict is the court's final decision, which can override AUDITOR.
    This is the point where mercy becomes law.

    Tool Protocol Compliant (Kernel-Managed).
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """Initialize verdict tool (kernel-managed)."""
        super().__init__(services)
        self._root_path = None
        logger.info("⚖️  Verdict Tool initialized")

    @property
    def name(self) -> str:
        return "supreme_court.verdict"

    @property
    def description(self) -> str:
        return "Issue and track court verdicts - can override AUDITOR decisions with mercy or uphold violations"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'issue', 'get', 'get_by_agent', 'get_by_type', 'get_mercy_count', 'get_overrides', 'get_all'",
            },
            "verdict_id": {
                "type": "string",
                "required": False,
                "description": "Verdict ID (required for get)",
            },
            "appeal_id": {
                "type": "string",
                "required": False,
                "description": "Appeal ID (required for issue)",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for issue, get_by_agent)",
            },
            "verdict_type": {
                "type": "string",
                "required": False,
                "description": "Verdict type: mercy_granted, mercy_conditional, upheld (required for issue, get_by_type)",
            },
            "justification": {
                "type": "string",
                "required": False,
                "description": "Justification for verdict (for issue)",
            },
            "override_auditor": {
                "type": "boolean",
                "required": False,
                "description": "Whether to override AUDITOR decision (for issue)",
            },
            "conditions": {
                "type": "array",
                "required": False,
                "description": "Conditions for conditional mercy (for issue)",
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
    def verdicts_dir(self) -> Path:
        """Get verdicts directory."""
        verdicts_dir = self.root_path / "data" / "governance" / "verdicts"
        verdicts_dir.mkdir(parents=True, exist_ok=True)
        return verdicts_dir

    @property
    def verdicts_file(self) -> Path:
        """Get verdicts file path."""
        return self.verdicts_dir / "verdicts.jsonl"

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate verdict tool parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["issue", "get", "get_by_agent", "get_by_type", "get_mercy_count", "get_overrides", "get_all"]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action == "issue":
            if "appeal_id" not in parameters:
                raise ValueError("action 'issue' requires 'appeal_id' parameter")
            if "agent_id" not in parameters:
                raise ValueError("action 'issue' requires 'agent_id' parameter")
            if "verdict_type" not in parameters:
                raise ValueError("action 'issue' requires 'verdict_type' parameter")

        if action == "get" and "verdict_id" not in parameters:
            raise ValueError("action 'get' requires 'verdict_id' parameter")

        if action == "get_by_agent" and "agent_id" not in parameters:
            raise ValueError("action 'get_by_agent' requires 'agent_id' parameter")

        if action == "get_by_type" and "verdict_type" not in parameters:
            raise ValueError("action 'get_by_type' requires 'verdict_type' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute verdict tool operation."""
        try:
            action = parameters["action"]

            if action == "issue":
                # Convert string verdict_type to VerdictType enum if needed
                verdict_type = parameters["verdict_type"]
                if isinstance(verdict_type, str):
                    try:
                        verdict_type = VerdictType(verdict_type)
                    except ValueError:
                        return ToolResult(success=False, error=f"Invalid verdict_type: {verdict_type}")

                result = self.issue_verdict(
                    appeal_id=parameters["appeal_id"],
                    agent_id=parameters["agent_id"],
                    verdict_type=verdict_type,
                    justification=parameters.get("justification", ""),
                    override_auditor=parameters.get("override_auditor", False),
                    conditions=parameters.get("conditions"),
                )
                return ToolResult(success=True, output=result)

            elif action == "get":
                result = self.get_verdict(parameters["verdict_id"])
                if result is None:
                    return ToolResult(success=False, error=f"Verdict {parameters['verdict_id']} not found")
                return ToolResult(success=True, output=result)

            elif action == "get_by_agent":
                result = self.get_verdicts_by_agent(parameters["agent_id"])
                return ToolResult(success=True, output=result)

            elif action == "get_by_type":
                result = self.get_verdicts_by_type(parameters["verdict_type"])
                return ToolResult(success=True, output=result)

            elif action == "get_mercy_count":
                result = self.get_mercy_count()
                return ToolResult(success=True, output={"mercy_count": result})

            elif action == "get_overrides":
                result = self.get_verdicts_that_override()
                return ToolResult(success=True, output=result)

            elif action == "get_all":
                result = self.get_all_verdicts()
                return ToolResult(success=True, output=result)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Verdict tool execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    def issue_verdict(
        self,
        appeal_id: str,
        agent_id: str,
        verdict_type: VerdictType,
        justification: str = "",
        override_auditor: bool = False,
        conditions: Optional[List[str]] = None,
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
            verdict_type=(verdict_type.value if isinstance(verdict_type, VerdictType) else verdict_type),
            justification=justification,
            override_auditor=override_auditor,
            conditions=conditions or [],
            issued_at=now,
            issued_by="supreme_court",
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

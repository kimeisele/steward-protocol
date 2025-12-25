#!/usr/bin/env python3
"""
Appeals Tool - Manages the appeal submission and tracking system.

This tool handles:
- Appeal intake (agent files appeal)
- Appeal status tracking
- Appeal withdrawal or expiration

Tool Protocol Compliant (Kernel-Managed).
"""

import json
import logging
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("APPEALS_TOOL")


class AppealStatus(str, Enum):
    """Status of an appeal throughout its lifecycle"""

    FILED = "filed"  # Initial submission
    UNDER_REVIEW = "under_review"  # Being examined by court
    HEARING_SCHEDULED = "hearing_scheduled"  # Waiting for hearing
    CLOSED = "closed"  # Decision issued


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


class AppealsTool(Tool):
    """
    Manages appeals in the Supreme Court system.

    This is the intake window for condemned agents seeking mercy.

    Tool Protocol Compliant (Kernel-Managed).
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """Initialize appeals tool (kernel-managed)."""
        super().__init__(services)
        self._root_path = None
        logger.info("📜 Appeals Tool initialized")

    @property
    def name(self) -> str:
        return "supreme_court.appeals"

    @property
    def description(self) -> str:
        return "Manage appeals in the Supreme Court system - file, track, and update appeal status"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'create', 'get', 'get_agent_appeals', 'get_all', 'update', 'get_by_status'",
            },
            "appeal_id": {
                "type": "string",
                "required": False,
                "description": "Appeal ID (required for get, update)",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for create, get_agent_appeals)",
            },
            "violation_id": {
                "type": "string",
                "required": False,
                "description": "Violation ID (required for create)",
            },
            "justification": {
                "type": "string",
                "required": False,
                "description": "Justification for appeal (for create)",
            },
            "has_oath": {
                "type": "boolean",
                "required": False,
                "description": "Whether agent has constitutional oath (for create)",
            },
            "updates": {
                "type": "object",
                "required": False,
                "description": "Update fields (for update action)",
            },
            "status": {
                "type": "string",
                "required": False,
                "description": "Appeal status (for get_by_status)",
            },
        }

    @property
    def root_path(self) -> Path:
        """Lazy-load root_path from system sandbox."""
        if self._root_path is None:
            # This will be injected by the kernel when the tool is registered
            # For now, use a default path
            self._root_path = Path(".") / "data" / "supreme_court"
            self._root_path.mkdir(parents=True, exist_ok=True)
        return self._root_path

    @property
    def appeals_dir(self) -> Path:
        """Get appeals directory."""
        appeals_dir = self.root_path / "data" / "governance" / "appeals"
        appeals_dir.mkdir(parents=True, exist_ok=True)
        return appeals_dir

    @property
    def appeals_file(self) -> Path:
        """Get appeals file path."""
        return self.appeals_dir / "appeals.jsonl"

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate appeal tool parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = ["create", "get", "get_agent_appeals", "get_all", "update", "get_by_status"]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action == "create":
            if "agent_id" not in parameters:
                raise ValueError("action 'create' requires 'agent_id' parameter")
            if "violation_id" not in parameters:
                raise ValueError("action 'create' requires 'violation_id' parameter")

        if action in ["get", "update"] and "appeal_id" not in parameters:
            raise ValueError(f"action '{action}' requires 'appeal_id' parameter")

        if action == "get_agent_appeals" and "agent_id" not in parameters:
            raise ValueError("action 'get_agent_appeals' requires 'agent_id' parameter")

        if action == "get_by_status" and "status" not in parameters:
            raise ValueError("action 'get_by_status' requires 'status' parameter")

        if action == "update" and "updates" not in parameters:
            raise ValueError("action 'update' requires 'updates' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute appeal tool operation."""
        try:
            action = parameters["action"]

            if action == "create":
                result = self.create_appeal(
                    agent_id=parameters["agent_id"],
                    violation_id=parameters["violation_id"],
                    justification=parameters.get("justification", ""),
                    has_oath=parameters.get("has_oath", False),
                )
                return ToolResult(success=True, output=result)

            elif action == "get":
                result = self.get_appeal(parameters["appeal_id"])
                if result is None:
                    return ToolResult(success=False, error=f"Appeal {parameters['appeal_id']} not found")
                return ToolResult(success=True, output=result)

            elif action == "get_agent_appeals":
                result = self.get_agent_appeals(parameters["agent_id"])
                return ToolResult(success=True, output=result)

            elif action == "get_all":
                result = self.get_all_appeals()
                return ToolResult(success=True, output=result)

            elif action == "update":
                result = self.update_appeal(parameters["appeal_id"], parameters["updates"])
                if not result:
                    return ToolResult(success=False, error=f"Failed to update appeal {parameters['appeal_id']}")
                return ToolResult(success=True, output={"updated": True})

            elif action == "get_by_status":
                result = self.get_appeals_by_status(parameters["status"])
                return ToolResult(success=True, output=result)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Appeals tool execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    def create_appeal(
        self,
        agent_id: str,
        violation_id: str,
        justification: str = "",
        has_oath: bool = False,
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
            updated_at=now,
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

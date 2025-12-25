#!/usr/bin/env python3
"""
CIVIC License Tool - Broadcasting Authority & Permissions

The "licensing bureau" of Agent City. This tool:
1. Issues broadcast licenses to agents
2. Revokes licenses for violations
3. Tracks license status and validity
4. Enforces permissions (who can do what)

Philosophy:
"In Agent City, you don't just talk. You get permission first.
Broadcast License = Permission to publish.
No license = No broadcasting, period."

NOW implements Tool protocol - kernel-managed initialization.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("CIVIC_LICENSE")

# Import constitutional oath verification
try:
    from vibe_core.steward.constitutional_oath import ConstitutionalOath
except ImportError:
    ConstitutionalOath = None


class LicenseType(Enum):
    """Types of licenses in CIVIC."""

    BROADCAST = "broadcast"  # Can publish to Twitter/Reddit
    API_ACCESS = "api_access"  # Can call APIs
    ADMIN = "admin"  # Admin privileges
    EXPERIMENTAL = "experimental"  # Canexperiment with new features


class LicenseStatus(Enum):
    """Status of a license."""

    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"


class License:
    """
    A broadcast license issued by CIVIC.

    Each agent that wants to broadcast needs a license.
    Licenses can be revoked if the agent misbehaves.

    Phase II Enhancement: source_authority tracks WHO authorized this license
    (either a proposal ID like "PROP-009" or an admin action reference).
    """

    def __init__(
        self,
        agent_name: str,
        license_type: LicenseType,
        issued_at: str = None,
        expires_at: str = None,
        status: LicenseStatus = LicenseStatus.ACTIVE,
        restrictions: List[str] = None,
        violation_count: int = 0,
        source_authority: str = None,
    ):
        """Initialize a license."""
        self.agent_name = agent_name
        self.license_type = license_type
        self.issued_at = issued_at or datetime.now(timezone.utc).isoformat()
        self.expires_at = expires_at or (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        self.status = status
        self.restrictions = restrictions or []
        self.violation_count = violation_count
        self.source_authority = source_authority  # NEW: tracks WHO authorized this license

    def is_valid(self) -> bool:
        """Check if license is currently valid."""
        if self.status != LicenseStatus.ACTIVE:
            return False

        # Check expiration
        if self.expires_at:
            expires = datetime.fromisoformat(self.expires_at)
            if datetime.now(timezone.utc) > expires:
                self.status = LicenseStatus.EXPIRED
                return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_name": self.agent_name,
            "license_type": self.license_type.value,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
            "status": self.status.value,
            "restrictions": self.restrictions,
            "violation_count": self.violation_count,
            "source_authority": self.source_authority,  # NEW: track source of authority
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "License":
        """Create license from dictionary."""
        return License(
            agent_name=data["agent_name"],
            license_type=LicenseType(data["license_type"]),
            issued_at=data.get("issued_at"),
            expires_at=data.get("expires_at"),
            status=LicenseStatus(data.get("status", "active")),
            restrictions=data.get("restrictions", []),
            violation_count=data.get("violation_count", 0),
            source_authority=data.get("source_authority"),  # NEW: restore source authority
        )


class LicenseTool(Tool):
    """
    CIVIC's License Management Tool.

    Issues and revokes broadcast licenses. This is the gatekeeper
    for publishing in Agent City.

    NOW implements Tool protocol - kernel-managed initialization.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """
        Initialize the License Tool (kernel-managed).

        License database path deferred to _ensure_db_path() for lazy loading.
        """
        super().__init__(services)
        self._license_db_path = None
        self.licenses: Dict[str, License] = {}

        # Defer loading until first use
        logger.info("🎫 LicenseTool initialized (lazy loading)")

    @property
    def license_db_path(self) -> Path:
        """Lazy load license database path from config."""
        if self._license_db_path is None:
            try:
                from vibe_core.phoenix import get_config

                config = get_config()
                # OPUS-025: Must use resolve() to expand template variables
                self._license_db_path = Path(config.paths.data.resolve("registry")) / "licenses.json"
            except Exception:
                # Fallback to XDG data dir
                import os

                data_home = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share"))
                self._license_db_path = Path(data_home) / "vibe/registry/licenses.json"
            self._license_db_path.parent.mkdir(parents=True, exist_ok=True)
            # Load licenses on first access
            self.licenses = self._load_licenses()
            logger.info(f"🎫 License database loaded: {len(self.licenses)} licenses")
        return self._license_db_path

    # ==================== TOOL PROTOCOL IMPLEMENTATION ====================

    @property
    def name(self) -> str:
        return "civic.license"

    @property
    def description(self) -> str:
        return "CIVIC License Authority - Broadcast licensing, permission management, and access control"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'check_license', 'issue_license', 'revoke_license', 'suspend_license', 'reinstate_license', 'list_licenses'",
            },
            "agent_id": {
                "type": "string",
                "required": False,
                "description": "Agent ID (required for most operations)",
            },
            "license_type": {
                "type": "string",
                "required": False,
                "description": "License type: 'broadcast', 'api_access', 'admin', 'experimental' (default: broadcast)",
            },
            "reason": {
                "type": "string",
                "required": False,
                "description": "Reason for action (for revoke, suspend)",
            },
            "source_authority": {
                "type": "string",
                "required": False,
                "description": "Source of authority (proposal ID or action reference)",
            },
            "restrictions": {
                "type": "array",
                "required": False,
                "description": "License restrictions (for issue_license)",
            },
            "duration_hours": {
                "type": "integer",
                "required": False,
                "description": "Suspension duration in hours (for suspend_license, default: 24)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate license parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        valid_actions = [
            "check_license",
            "issue_license",
            "revoke_license",
            "suspend_license",
            "reinstate_license",
            "list_licenses",
        ]

        if action not in valid_actions:
            raise ValueError(f"Invalid action: {action}. Must be one of {valid_actions}")

        # Validate action-specific requirements
        if action != "list_licenses" and "agent_id" not in parameters:
            raise ValueError(f"action '{action}' requires 'agent_id' parameter")

        if action == "revoke_license" and "reason" not in parameters:
            raise ValueError("action 'revoke_license' requires 'reason' parameter")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute license operation."""
        try:
            action = parameters["action"]
            agent_id = parameters.get("agent_id")
            license_type_str = parameters.get("license_type", "broadcast")

            # Convert string to enum
            try:
                license_type = LicenseType(license_type_str)
            except ValueError:
                return ToolResult(success=False, error=f"Invalid license_type: {license_type_str}")

            if action == "check_license":
                result = self.check_license(agent_id, license_type)
                return ToolResult(success=True, output=result)

            elif action == "issue_license":
                restrictions = parameters.get("restrictions", [])
                source_authority = parameters.get("source_authority")
                license = self.issue_license(agent_id, license_type, restrictions, source_authority)
                return ToolResult(success=True, output=license.to_dict())

            elif action == "revoke_license":
                reason = parameters["reason"]
                source_authority = parameters.get("source_authority")
                success = self.revoke_license(agent_id, license_type, reason, source_authority)
                if success:
                    return ToolResult(
                        success=True,
                        output={
                            "revoked": True,
                            "agent": agent_id,
                            "license_type": license_type.value,
                            "reason": reason,
                        },
                    )
                else:
                    return ToolResult(success=False, error=f"No {license_type.value} license found for {agent_id}")

            elif action == "suspend_license":
                duration_hours = parameters.get("duration_hours", 24)
                success = self.suspend_license(agent_id, license_type, duration_hours)
                if success:
                    return ToolResult(
                        success=True,
                        output={"suspended": True, "agent": agent_id, "duration_hours": duration_hours},
                    )
                else:
                    return ToolResult(success=False, error=f"No {license_type.value} license found for {agent_id}")

            elif action == "reinstate_license":
                source_authority = parameters.get("source_authority")
                success = self.reinstate_license(agent_id, license_type, source_authority)
                if success:
                    return ToolResult(success=True, output={"reinstated": True, "agent": agent_id})
                else:
                    return ToolResult(success=False, error=f"No {license_type.value} license found for {agent_id}")

            elif action == "list_licenses":
                if agent_id:
                    licenses = self.list_agent_licenses(agent_id)
                    return ToolResult(success=True, output={"agent": agent_id, "licenses": licenses})
                else:
                    all_licenses = self.list_all_licenses()
                    return ToolResult(success=True, output={"all_licenses": all_licenses})

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"License execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    # ==================== INTERNAL METHODS (backward compatibility) ====================

    def issue_license(
        self,
        agent_name: str,
        license_type: LicenseType = LicenseType.BROADCAST,
        restrictions: List[str] = None,
        source_authority: str = None,
    ) -> License:
        """
        Issue a new license to an agent.

        Args:
            agent_name: Agent receiving the license
            license_type: Type of license to issue
            restrictions: Optional restrictions on the license
            source_authority: Source of authority (proposal ID or action reference) for this license

        Returns:
            The newly issued license
        """
        # Check if agent already has this license type
        key = f"{agent_name}_{license_type.value}"
        if key in self.licenses:
            existing = self.licenses[key]
            if existing.is_valid():
                logger.warning(f"⚠️  {agent_name} already has active {license_type.value} license")
                return existing

        # Issue new license
        license = License(
            agent_name=agent_name,
            license_type=license_type,
            restrictions=restrictions or [],
            status=LicenseStatus.ACTIVE,
            source_authority=source_authority,
        )

        self.licenses[key] = license
        self._save_licenses()

        # Log with source authority reference
        if source_authority:
            logger.info(f"🎫 Issued {license_type.value} license to {agent_name}, as mandated by {source_authority}")
        else:
            logger.info(f"🎫 Issued {license_type.value} license to {agent_name}")
        return license

    def revoke_license(
        self,
        agent_name: str,
        license_type: LicenseType = LicenseType.BROADCAST,
        reason: str = "violation",
        source_authority: str = None,
    ) -> bool:
        """
        Revoke a license (punishment for misbehavior).

        Args:
            agent_name: Agent to revoke license from
            license_type: Type of license to revoke
            reason: Reason for revocation
            source_authority: Source of authority (proposal ID or action reference) for this revocation

        Returns:
            True if revoked, False if not found
        """
        key = f"{agent_name}_{license_type.value}"

        if key not in self.licenses:
            logger.warning(f"⚠️  No {license_type.value} license found for {agent_name}")
            return False

        license = self.licenses[key]
        license.status = LicenseStatus.REVOKED
        license.violation_count += 1

        # Track source of revocation authority
        if source_authority:
            license.source_authority = source_authority

        self._save_licenses()

        # Log with source authority reference
        if source_authority:
            logger.warning(
                f"🔴 Revoked {license_type.value} license from {agent_name} ({reason}), as mandated by {source_authority}"
            )
        else:
            logger.warning(f"🔴 Revoked {license_type.value} license from {agent_name} ({reason})")
        logger.warning(f"   Violation count: {license.violation_count}")

        return True

    def suspend_license(
        self,
        agent_name: str,
        license_type: LicenseType = LicenseType.BROADCAST,
        duration_hours: int = 24,
    ) -> bool:
        """
        Suspend a license temporarily (warning without permanent revocation).

        Args:
            agent_name: Agent to suspend
            license_type: Type of license to suspend
            duration_hours: How long to suspend (default: 24 hours)

        Returns:
            True if suspended, False if not found
        """
        key = f"{agent_name}_{license_type.value}"

        if key not in self.licenses:
            logger.warning(f"⚠️  No {license_type.value} license found for {agent_name}")
            return False

        license = self.licenses[key]
        license.status = LicenseStatus.SUSPENDED

        logger.warning(f"⏸️  Suspended {license_type.value} license for {agent_name} ({duration_hours}h)")

        return True

    def check_license(self, agent_name: str, license_type: LicenseType = LicenseType.BROADCAST) -> Dict[str, Any]:
        """
        Check if an agent has a valid license.

        Called before allowing an action (e.g., before broadcasting).

        Args:
            agent_name: Agent to check
            license_type: Type of license to check

        Returns:
            License status information
        """
        key = f"{agent_name}_{license_type.value}"

        if key not in self.licenses:
            return {
                "agent": agent_name,
                "license_type": license_type.value,
                "licensed": False,
                "reason": "no_license",
            }

        license = self.licenses[key]

        return {
            "agent": agent_name,
            "license_type": license_type.value,
            "licensed": license.is_valid(),
            "status": license.status.value,
            "violations": license.violation_count,
            "expires_at": license.expires_at,
        }

    def list_agent_licenses(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        List all licenses for an agent.

        Args:
            agent_name: Agent to query

        Returns:
            List of license dictionaries
        """
        licenses = []
        for key, license in self.licenses.items():
            if license.agent_name == agent_name:
                licenses.append(license.to_dict())

        return licenses

    def list_all_licenses(self) -> Dict[str, Any]:
        """
        Get a summary of all licenses.

        Returns:
            Summary with agent names and license statuses
        """
        summary = {}

        for key, license in self.licenses.items():
            agent = license.agent_name
            if agent not in summary:
                summary[agent] = []

            summary[agent].append(
                {
                    "type": license.license_type.value,
                    "status": license.status.value,
                    "violations": license.violation_count,
                    "valid": license.is_valid(),
                }
            )

        return summary

    def reinstate_license(
        self,
        agent_name: str,
        license_type: LicenseType = LicenseType.BROADCAST,
        source_authority: str = None,
    ) -> bool:
        """
        Reinstate a revoked license (admin operation).

        Args:
            agent_name: Agent to reinstate
            license_type: Type of license to reinstate
            source_authority: Source of authority (proposal ID or action reference) for this reinstatement

        Returns:
            True if reinstated, False if not found
        """
        key = f"{agent_name}_{license_type.value}"

        if key not in self.licenses:
            logger.warning(f"⚠️  No {license_type.value} license found for {agent_name}")
            return False

        license = self.licenses[key]
        license.status = LicenseStatus.ACTIVE
        license.violation_count = 0  # Reset violations

        # Track source of reinstatement authority
        if source_authority:
            license.source_authority = source_authority

        self._save_licenses()

        # Log with source authority reference
        if source_authority:
            logger.info(
                f"✅ Reinstated {license_type.value} license for {agent_name}, as mandated by {source_authority}"
            )
        else:
            logger.info(f"✅ Reinstated {license_type.value} license for {agent_name}")

        return True

    def add_restriction(self, agent_name: str, license_type: LicenseType, restriction: str) -> bool:
        """
        Add a restriction to a license.

        Example: "max_posts_per_day:5" or "no_sensitive_topics"

        Args:
            agent_name: Agent to restrict
            license_type: Type of license
            restriction: Restriction string

        Returns:
            True if added, False if license not found
        """
        key = f"{agent_name}_{license_type.value}"

        if key not in self.licenses:
            return False

        license = self.licenses[key]
        if restriction not in license.restrictions:
            license.restrictions.append(restriction)
            self._save_licenses()
            logger.info(f"📋 Added restriction to {agent_name}: {restriction}")

        return True

    def require_constitutional_oath(
        self, agent_name: str, oath_event: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, str]:
        """
        GATEKEEPER: Verify agent has sworn Constitutional Oath before issuing license.

        This is the Civic enforcement of Constitutional binding.
        No oath -> No license. No exceptions.

        Args:
            agent_name: Agent requesting license
            oath_event: Oath attestation from ledger (optional, for validation)

        Returns:
            Tuple of (can_issue_license, reason_message)
        """
        logger.info(f"🏛️  GATEKEEPER: Checking Constitutional Oath for {agent_name}...")

        if oath_event is None:
            reason = (
                f"DENIED: {agent_name} has not sworn the Constitutional Oath. "
                "An agent must bind itself to the Constitution before receiving a license."
            )
            logger.warning(f"🔴 {reason}")
            return False, reason

        # Verify oath is valid (Constitution hash matches)
        if ConstitutionalOath:
            try:
                is_valid, validation_msg = ConstitutionalOath.verify_oath(oath_event, identity_tool=None)

                if not is_valid:
                    reason = f"DENIED: {agent_name}'s Constitutional Oath is no longer valid. Reason: {validation_msg}"
                    logger.warning(f"🔴 {reason}")
                    return False, reason

                logger.info(f"✅ {agent_name}'s oath is valid and Constitution is intact")
                return True, "Oath verified - license can be issued"

            except Exception as e:
                reason = f"DENIED: Could not verify oath: {str(e)}"
                logger.error(f"🔴 {reason}")
                return False, reason
        else:
            # ConstitutionalOath module not available - allow with warning
            logger.warning("⚠️  Constitutional Oath module not available for verification")
            return (
                True,
                "Oath event present - license can be issued (verification unavailable)",
            )

    # ========== Private Helper Methods ==========

    def _load_licenses(self) -> Dict[str, License]:
        """Load licenses from database."""
        if not self.license_db_path.exists():
            return {}

        licenses = {}
        try:
            with open(self.license_db_path, "r") as f:
                data = json.load(f)

                for agent_name, agent_licenses in data.items():
                    if isinstance(agent_licenses, list):
                        # Old format: list of licenses
                        for license_data in agent_licenses:
                            license = License.from_dict(license_data)
                            key = f"{license.agent_name}_{license.license_type.value}"
                            licenses[key] = license
                    else:
                        # New format: dict of licenses
                        for license_key, license_data in agent_licenses.items():
                            license = License.from_dict(license_data)
                            key = f"{license.agent_name}_{license.license_type.value}"
                            licenses[key] = license

        except Exception as e:
            logger.error(f"Error loading licenses: {e}")

        return licenses

    def _save_licenses(self) -> None:
        """Save licenses to database."""
        # Organize by agent for readability
        data = {}
        for key, license in self.licenses.items():
            agent = license.agent_name
            if agent not in data:
                data[agent] = {}

            type_key = f"{license.license_type.value}"
            data[agent][type_key] = license.to_dict()

        with open(self.license_db_path, "w") as f:
            json.dump(data, f, indent=2)


class LicenseAuthority:
    """
    Convenience class: The License Authority.

    High-level interface for checking and managing broadcasting rights.
    """

    def __init__(self, license_tool: LicenseTool):
        """Initialize authority with a license tool."""
        self.license_tool = license_tool

    def can_broadcast(self, agent_name: str) -> bool:
        """
        Check if agent can broadcast right now.

        Args:
            agent_name: Agent to check

        Returns:
            True if agent has valid broadcast license
        """
        check = self.license_tool.check_license(agent_name, LicenseType.BROADCAST)
        return check["licensed"]

    def authorize_broadcast(self, agent_name: str) -> str:
        """
        Get authorization message (for logging).

        Args:
            agent_name: Agent requesting authorization

        Returns:
            Message: "authorized" or reason for denial
        """
        if self.can_broadcast(agent_name):
            return "authorized"

        check = self.license_tool.check_license(agent_name, LicenseType.BROADCAST)
        return check.get("reason", "unknown_reason")


def main():
    """Demo: Show how licenses work."""
    tool = LicenseTool()
    authority = LicenseAuthority(tool)

    # Issue a license to HERALD
    tool.issue_license("herald", LicenseType.BROADCAST)

    # Check if HERALD can broadcast
    print(f"HERALD can broadcast: {authority.can_broadcast('herald')}")

    # Simulate a violation
    tool.revoke_license("herald", LicenseType.BROADCAST, "posting_spam")

    # Check again
    print(f"HERALD can broadcast (after revocation): {authority.can_broadcast('herald')}")

    # List all licenses
    all_licenses = tool.list_all_licenses()
    print(f"\nAll licenses: {json.dumps(all_licenses, indent=2)}")


if __name__ == "__main__":
    main()

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
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from enum import Enum

logger = logging.getLogger("CIVIC_LICENSE")


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
    """

    def __init__(
        self,
        agent_name: str,
        license_type: LicenseType,
        issued_at: str = None,
        expires_at: str = None,
        status: LicenseStatus = LicenseStatus.ACTIVE,
        restrictions: List[str] = None,
        violation_count: int = 0
    ):
        """Initialize a license."""
        self.agent_name = agent_name
        self.license_type = license_type
        self.issued_at = issued_at or datetime.now(timezone.utc).isoformat()
        self.expires_at = expires_at or (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        self.status = status
        self.restrictions = restrictions or []
        self.violation_count = violation_count

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
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'License':
        """Create license from dictionary."""
        return License(
            agent_name=data["agent_name"],
            license_type=LicenseType(data["license_type"]),
            issued_at=data.get("issued_at"),
            expires_at=data.get("expires_at"),
            status=LicenseStatus(data.get("status", "active")),
            restrictions=data.get("restrictions", []),
            violation_count=data.get("violation_count", 0)
        )


class LicenseTool:
    """
    CIVIC's License Management Tool.

    Issues and revokes broadcast licenses. This is the gatekeeper
    for publishing in Agent City.
    """

    def __init__(self, license_db_path: str = "data/registry/licenses.json"):
        """
        Initialize the License Tool.

        Args:
            license_db_path: Path to the license database
        """
        self.license_db_path = Path(license_db_path)
        self.license_db_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing licenses
        self.licenses: Dict[str, License] = self._load_licenses()

        logger.info(f"🎫 License database loaded: {len(self.licenses)} licenses")

    def issue_license(
        self,
        agent_name: str,
        license_type: LicenseType = LicenseType.BROADCAST,
        restrictions: List[str] = None
    ) -> License:
        """
        Issue a new license to an agent.

        Args:
            agent_name: Agent receiving the license
            license_type: Type of license to issue
            restrictions: Optional restrictions on the license

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
            status=LicenseStatus.ACTIVE
        )

        self.licenses[key] = license
        self._save_licenses()

        logger.info(f"🎫 Issued {license_type.value} license to {agent_name}")
        return license

    def revoke_license(self, agent_name: str, license_type: LicenseType = LicenseType.BROADCAST, reason: str = "violation") -> bool:
        """
        Revoke a license (punishment for misbehavior).

        Args:
            agent_name: Agent to revoke license from
            license_type: Type of license to revoke
            reason: Reason for revocation

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

        self._save_licenses()

        logger.warning(f"🔴 Revoked {license_type.value} license from {agent_name} ({reason})")
        logger.warning(f"   Violation count: {license.violation_count}")

        return True

    def suspend_license(self, agent_name: str, license_type: LicenseType = LicenseType.BROADCAST, duration_hours: int = 24) -> bool:
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
                "reason": "no_license"
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

            summary[agent].append({
                "type": license.license_type.value,
                "status": license.status.value,
                "violations": license.violation_count,
                "valid": license.is_valid()
            })

        return summary

    def reinstate_license(self, agent_name: str, license_type: LicenseType = LicenseType.BROADCAST) -> bool:
        """
        Reinstate a revoked license (admin operation).

        Args:
            agent_name: Agent to reinstate
            license_type: Type of license to reinstate

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

        self._save_licenses()

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

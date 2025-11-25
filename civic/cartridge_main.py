#!/usr/bin/env python3
"""
CIVIC Cartridge - The Bureaucrat (Administrative Agent)

CIVIC is the "City Hall" of Agent City. It manages:
1. Governance Rules & Enforcement (Licenses, Credits)
2. Registry Authority (validates agent claims against VibeOS kernel)
3. Broadcast Licensing (permission to publish)
4. Credit System (economic constraints on autonomous action)

This is a VibeAgent that:
- Inherits from vibe_core.VibeAgent (VibeOS compatible)
- Receives tasks from the kernel scheduler
- Enforces governance rules in real-time
- Queries kernel for agent registry (source of truth)

Key Insight (ARCH REALIGNMENT):
- OLD: CIVIC scanned filesystem. Built local registry.
- NEW: CIVIC queries kernel.agent_registry. Enforces rules.
The kernel is the source of truth. CIVIC is the bureaucracy layer.
"""

import logging
import json
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timezone

# VibeOS Integration
from vibe_core import VibeAgent, Task, VibeKernel, AgentManifest

# Import tools
from civic.tools.ledger_tool import LedgerTool, AgentBank
from civic.tools.license_tool import LicenseTool, LicenseAuthority, LicenseType
from civic.tools.registry_tool import RegistryTool

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CIVIC_MAIN")


class CivicCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    The CIVIC Agent Cartridge (The Bureaucrat).

    Administrative oversight and registry management for Agent City.

    Key Responsibilities:
    - Agent Registration: Scan filesystem, validate configs, assign identities
    - Broadcast Licensing: Issue/revoke broadcast permissions
    - Credit Management: Track agent credits, deduct for actions
    - Registry Maintenance: Keep AGENTS.md and citizens.json synchronized

    Philosophy:
    "You want to post something? Register. You want to broadcast? Get a license.
    You want credits? Prove you're not spam. Break the rules? License revoked."
    """

    def __init__(self):
        """Initialize CIVIC (The Bureaucrat) as a VibeAgent."""
        # Initialize VibeAgent base class
        super().__init__(
            agent_id="civic",
            name="CIVIC",
            version="2.0.0",
            author="Steward Protocol",
            description="Governance agent: enforces rules, manages licenses, audits credits",
            domain="GOVERNANCE",
            capabilities=[
                "registry",
                "licensing",
                "ledger",
                "governance"
            ]
        )

        logger.info("🏛️  CIVIC Cartridge initializing (VibeAgent v2.0)...")

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures CIVIC has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ CIVIC has sworn the Constitutional Oath (Genesis Ceremony)")

        # Load THE MATRIX (configuration)
        self.matrix = self._load_matrix()
        if self.matrix:
            city_name = self.matrix.get("city_name", "Agent City")
            logger.info(f"🎛️  THE MATRIX loaded: {city_name} (Federation v{self.matrix.get('federation_version', 'unknown')})")
        else:
            logger.warning("⚠️  THE MATRIX not found, using defaults")
            self.matrix = self._default_matrix()

        # Persistence paths (local fallback)
        self.registry_path = Path("data/registry/citizens.json")
        self.agents_md_path = Path("AGENTS.md")
        self.state_path = Path("data/state/civic_state.json")

        # Ensure directories exist
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize tools
        self.ledger = LedgerTool("data/registry/ledger.jsonl")
        self.license_tool = LicenseTool("data/registry/licenses.json")
        self.registry_tool = RegistryTool(".")

        # Load local registry (fallback, not authoritative)
        self.registry = self._load_registry()
        self.state = self._load_state()

        logger.info(f"📋 Local registry cache: {len(self.registry.get('agents', {}))} agents (fallback only)")
        logger.info(f"💰 Ledger initialized: {len(self.ledger.entries)} transactions")
        logger.info(f"🎫 License database initialized: {len(self.license_tool.licenses)} licenses")
        logger.info(f"🏛️  CIVIC: Ready for operation (awaiting kernel injection)")

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        CIVIC responds to governance-related tasks:
        - "check_license": Verify broadcast permission
        - "deduct_credits": Charge agent for action
        - "refill_credits": Admin credit refill
        - "revoke_license": Revoke an agent's license (manual admin intervention)
        - "get_registry": Return current registry snapshot
        - "generate_citymap": Create markdown map of agents
        """
        try:
            action = task.payload.get("action")
            logger.info(f"🏛️  CIVIC processing task: {action}")

            if action == "check_license":
                agent_id = task.payload.get("agent_id")
                return self.check_broadcast_license(agent_id)

            elif action == "deduct_credits":
                agent_id = task.payload.get("agent_id")
                amount = task.payload.get("amount", 1)
                reason = task.payload.get("reason", "action")
                return self.deduct_credits(agent_id, amount, reason)

            elif action == "refill_credits":
                agent_id = task.payload.get("agent_id")
                amount = task.payload.get("amount")
                return self.refill_credits(agent_id, amount)

            elif action == "revoke_license":
                agent_id = task.payload.get("agent_id")
                reason = task.payload.get("reason", "violation")
                source_authority = task.payload.get("source_authority")
                return self.revoke_license(agent_id, reason, source_authority)

            elif action == "get_registry":
                return self._get_registry_from_kernel()

            elif action == "generate_citymap":
                return self._generate_citymap_from_kernel()

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            logger.error(f"❌ CIVIC processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def report_status(self) -> Dict[str, Any]:
        """Report CIVIC status (VibeAgent interface) - Deep Introspection."""
        # If kernel is available, use real data
        if self.kernel:
            agents = self.kernel.agent_registry.values()
            agent_count = len(agents)
        else:
            # Fallback to local cache
            agents = self.registry.get("agents", {})
            agent_count = len(agents)

        # Extract ledger statistics
        ledger_entries = len(self.ledger.entries) if self.ledger.entries else 0
        total_credits = sum(
            entry.get("balance_after", 0)
            for entry in (self.ledger.entries or [])
        )

        # Extract license statistics
        active_licenses = len([
            lic for lic in self.license_tool.licenses.values()
            if lic.get("status") == "ACTIVE"
        ])

        return {
            "agent_id": "civic",
            "name": "CIVIC",
            "status": "RUNNING",
            "domain": "GOVERNANCE",
            "capabilities": self.capabilities,
            "authority_metrics": {
                "total_agents_registered": agent_count,
                "active_broadcast_licenses": active_licenses,
                "ledger_entries": ledger_entries,
                "total_credits_in_system": total_credits,
                "ledger_path": "data/registry/ledger.jsonl",
                "licenses_path": "data/registry/licenses.json",
            }
        }

    def scan_and_register_agents(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Scan filesystem for agents and register them in the citizen registry.

        Process:
        1. Find all agent directories (*/cartridge_main.py)
        2. Validate each agent's configuration
        3. Check if already registered
        4. Assign identity and issue initial broadcast license
        5. Initialize credit account
        6. Record in registry

        Args:
            dry_run: If True, don't update registry

        Returns:
            dict: Registration summary
        """
        logger.info("\n🏛️  PHASE 1: AGENT REGISTRATION SCAN")
        logger.info("=" * 70)

        try:
            # Find all agent cartridges
            agent_dirs = self._find_agent_cartridges()
            logger.info(f"🔍 Found {len(agent_dirs)} agent cartridges")

            registered = []
            rejected = []
            updated = []

            for agent_dir in agent_dirs:
                agent_name = agent_dir.parent.name

                logger.info(f"\n📋 Processing: {agent_name}")

                # Skip CIVIC itself
                if agent_name == "civic":
                    logger.info("   ↷ Skipping (that's us)")
                    continue

                # Validate config
                config = self._validate_agent_config(agent_dir)
                if not config:
                    logger.warning(f"   ❌ Invalid configuration")
                    rejected.append(agent_name)
                    continue

                # Check if already registered
                existing = self.registry.get("agents", {}).get(agent_name)

                if existing:
                    logger.info(f"   📝 Already registered (updating metadata)")
                    # Update metadata
                    existing["last_scanned"] = datetime.now(timezone.utc).isoformat()
                    existing["config"] = config
                    updated.append(agent_name)
                else:
                    logger.info(f"   ✅ New agent! Issuing initial license & credits")
                    # Register new agent (credits from THE MATRIX)
                    initial_credits = self.get_matrix_config("economy", "initial_credits", 100)
                    agent_record = {
                        "name": agent_name,
                        "registered_at": datetime.now(timezone.utc).isoformat(),
                        "last_scanned": datetime.now(timezone.utc).isoformat(),
                        "config": config,
                        "broadcast_license": True,  # Initial license (can be revoked)
                        "credits": initial_credits,  # From THE MATRIX
                        "total_broadcasts": 0,
                        "violations": [],
                    }

                    if "agents" not in self.registry:
                        self.registry["agents"] = {}

                    self.registry["agents"][agent_name] = agent_record
                    registered.append(agent_name)
                    logger.info(f"   🎫 License issued | 💰 {initial_credits} credits allocated")

            # Save registry (unless dry_run)
            if not dry_run:
                self._save_registry()
                self.state["last_registry_update"] = datetime.now(timezone.utc).isoformat()
                self._save_state()
                logger.info(f"\n✅ Registry saved")
            else:
                logger.info(f"\n🔍 DRY RUN: Registry not saved")

            result = {
                "status": "complete",
                "registered": len(registered),
                "updated": len(updated),
                "rejected": len(rejected),
                "registered_agents": registered,
                "updated_agents": updated,
                "rejected_agents": rejected,
            }

            logger.info("\n" + "=" * 70)
            logger.info(f"✅ REGISTRATION SCAN COMPLETE")
            logger.info(f"   New registrations: {len(registered)}")
            logger.info(f"   Updated: {len(updated)}")
            logger.info(f"   Rejected: {len(rejected)}")
            logger.info("=" * 70)

            return result

        except Exception as e:
            logger.error(f"❌ Registration scan error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def update_agents_registry(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update AGENTS.md based on citizen registry.

        Regenerates AGENTS.md from the authoritative citizens.json registry.
        This ensures the markdown file always reflects actual registered agents.

        Args:
            dry_run: If True, don't write to AGENTS.md

        Returns:
            dict: Update result
        """
        logger.info("\n🏛️  PHASE 2: REGISTRY UPDATE")
        logger.info("=" * 70)

        try:
            agents = self.registry.get("agents", {})

            # Build markdown content
            content = self._generate_agents_markdown(agents)

            if not dry_run:
                self.agents_md_path.write_text(content)
                logger.info(f"✅ AGENTS.md updated with {len(agents)} agents")
            else:
                logger.info(f"🔍 DRY RUN: Would update AGENTS.md with {len(agents)} agents")

            return {
                "status": "success",
                "agents_count": len(agents),
                "markdown_size": len(content),
            }

        except Exception as e:
            logger.error(f"❌ Registry update error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def check_broadcast_license(self, agent_name: str) -> Dict[str, Any]:
        """
        Check if an agent has broadcast license.

        This is the gatekeeper for publishing. Called before HERALD or any
        agent tries to broadcast.

        Args:
            agent_name: Name of agent to check

        Returns:
            dict: License status
        """
        agents = self.registry.get("agents", {})
        agent = agents.get(agent_name)

        if not agent:
            return {
                "agent": agent_name,
                "licensed": False,
                "reason": "not_registered"
            }

        if not agent.get("broadcast_license"):
            return {
                "agent": agent_name,
                "licensed": False,
                "reason": "license_revoked",
                "violations": agent.get("violations", [])
            }

        return {
            "agent": agent_name,
            "licensed": True,
            "credits": agent.get("credits", 0),
        }

    def deduct_credits(self, agent_name: str, amount: int = 1, reason: str = "broadcast") -> Dict[str, Any]:
        """
        Deduct credits from an agent's account.

        When an agent broadcasts, we deduct 1 credit. If credits reach 0,
        the broadcast license is automatically revoked.

        Args:
            agent_name: Agent to charge
            amount: Credits to deduct (default: 1 per broadcast)
            reason: Reason for deduction

        Returns:
            dict: Deduction result
        """
        logger.info(f"💰 Deducting {amount} credits from {agent_name} ({reason})")

        agents = self.registry.get("agents", {})
        agent = agents.get(agent_name)

        if not agent:
            return {
                "status": "error",
                "reason": "agent_not_found"
            }

        current_credits = agent.get("credits", 0)
        new_credits = max(0, current_credits - amount)

        agent["credits"] = new_credits
        agent["total_broadcasts"] = agent.get("total_broadcasts", 0) + 1

        logger.info(f"   Credits: {current_credits} → {new_credits}")

        # MANDATORY: Record in kernel ledger (no offline mode)
        if not hasattr(self, 'kernel') or not self.kernel:
            raise RuntimeError(
                f"FATAL: {self.agent_id} cannot deduct credits - not connected to kernel. "
                "All financial transactions MUST be recorded in kernel ledger (no offline mode)."
            )
        
        self.kernel.ledger.record_event(
            event_type="credit_deducted",
            agent_id=self.agent_id,
            details={
                "agent": agent_name,
                "amount": amount,
                "reason": reason,
                "previous_balance": current_credits,
                "new_balance": new_credits,
            }
        )

        # Revoke license if credits depleted
        if new_credits == 0:
            agent["broadcast_license"] = False
            logger.warning(f"   ⚠️  Credits depleted! License revoked for {agent_name}")
            self._save_registry()
            return {
                "status": "license_revoked",
                "agent": agent_name,
                "credits": new_credits,
                "message": "Credits depleted. License revoked. Contact CIVIC for credit refill."
            }

        self._save_registry()
        return {
            "status": "success",
            "agent": agent_name,
            "credits_remaining": new_credits,
            "total_broadcasts": agent.get("total_broadcasts", 0)
        }

    def refill_credits(self, agent_name: str, amount: Optional[int] = None, admin_key: str = None) -> Dict[str, Any]:
        """
        Refill an agent's credits (admin-only operation).

        This is how we "feed" agents when they've spent their credits.
        Requires admin authorization (or simulation override).

        Args:
            agent_name: Agent to refill
            amount: Credits to add (default from THE MATRIX refill_amount)
            admin_key: Admin authorization key (future implementation)

        Returns:
            dict: Refill result
        """
        # Use THE MATRIX refill amount if not specified
        if amount is None:
            amount = self.get_matrix_config("economy", "refill_amount", 50)

        logger.info(f"💰 Refilling credits for {agent_name} (+{amount})")

        agents = self.registry.get("agents", {})
        agent = agents.get(agent_name)

        if not agent:
            return {"status": "error", "reason": "agent_not_found"}

        old_credits = agent.get("credits", 0)
        agent["credits"] = old_credits + amount

        # Restore license if it was revoked
        if old_credits == 0:
            agent["broadcast_license"] = True
            logger.info(f"   ✅ License restored")

        self._save_registry()

        logger.info(f"   Credits: {old_credits} → {agent['credits']}")

        return {
            "status": "success",
            "agent": agent_name,
            "credits": agent.get("credits", 0)
        }

    def revoke_license(self, agent_name: str, reason: str = "violation", source_authority: str = None) -> Dict[str, Any]:
        """
        Revoke an agent's broadcast license (manual admin intervention).

        This is a governance action that prevents an agent from publishing.
        Used for violations, governance failures, or manual intervention.

        Args:
            agent_name: Agent whose license is being revoked
            reason: Reason for revocation (e.g., "Violation: Manual Admin Intervention Required")
            source_authority: Source of authority for this revocation (e.g., ENVOY, CIVIC_ADMIN)

        Returns:
            dict: Revocation result
        """
        logger.info(f"🔴 Revoking broadcast license for {agent_name}")
        logger.info(f"   Reason: {reason}")
        if source_authority:
            logger.info(f"   Authority: {source_authority}")

        # Call license tool to revoke the license
        success = self.license_tool.revoke_license(
            agent_name,
            license_type=LicenseType.BROADCAST,
            reason=reason,
            source_authority=source_authority
        )

        if not success:
            logger.warning(f"⚠️  License revocation failed: {agent_name} has no active broadcast license")
            return {
                "status": "error",
                "reason": "license_not_found",
                "agent": agent_name,
                "message": f"No broadcast license found for {agent_name}"
            }

        # Update local registry as well
        agents = self.registry.get("agents", {})
        agent = agents.get(agent_name)
        if agent:
            agent["broadcast_license"] = False
            self._save_registry()
            logger.info(f"   ✅ Local registry updated")

        return {
            "status": "success",
            "agent": agent_name,
            "reason": reason,
            "source_authority": source_authority,
            "message": f"Broadcast license revoked for {agent_name}"
        }

    # ========== KERNEL INTEGRATION METHODS ==========

    def _get_registry_from_kernel(self) -> Dict[str, Any]:
        """
        Query the kernel for the authoritative agent registry.

        This is the NEW ARCH approach: Ask the OS, don't scan files.
        """
        if not self.kernel:
            logger.warning("⚠️  Kernel not available, using local cache")
            return {
                "status": "fallback",
                "agents": self.registry.get("agents", {}),
                "note": "Using local cache (kernel not injected)"
            }

        try:
            manifests = self.kernel.manifest_registry.list_all()
            agents_dict = {}

            for manifest in manifests:
                agents_dict[manifest.agent_id] = {
                    "agent_id": manifest.agent_id,
                    "name": manifest.name,
                    "version": manifest.version,
                    "domain": manifest.domain,
                    "capabilities": manifest.capabilities,
                    "status": "REGISTERED"
                }

            return {
                "status": "success",
                "agent_count": len(agents_dict),
                "agents": agents_dict,
                "source": "kernel"
            }

        except Exception as e:
            logger.error(f"❌ Failed to query kernel registry: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _generate_citymap_from_kernel(self) -> Dict[str, Any]:
        """
        Generate CityMap from kernel's agent registry.

        OLD ARCH: Scan filesystem for cartridge_main.py files
        NEW ARCH: Query kernel for actual running agents
        """
        if not self.kernel:
            logger.warning("⚠️  Kernel not available, generating from local cache")
            return self._generate_citymap_from_cache()

        try:
            manifests = self.kernel.manifest_registry.list_all()
            status = self.kernel.get_status()

            markdown_lines = [
                "# 🏙️ AGENT CITY MAP",
                "",
                "**Generated by CIVIC from VibeOS Kernel**",
                f"Generated: {datetime.now(timezone.utc).isoformat()}",
                f"Kernel Status: {status.get('kernel_status', 'UNKNOWN')}",
                f"Total Agents: {len(manifests)}",
                "",
                "---",
                "",
            ]

            # Group agents by domain
            domains = {}
            for manifest in manifests:
                domain = manifest.domain or "UNKNOWN"
                if domain not in domains:
                    domains[domain] = []
                domains[domain].append(manifest)

            # Render by domain
            for domain in sorted(domains.keys()):
                markdown_lines.extend([
                    f"## {domain}",
                    "",
                ])

                for manifest in domains[domain]:
                    markdown_lines.extend([
                        f"### {manifest.name} (`{manifest.agent_id}`)",
                        f"- **Version**: {manifest.version}",
                        f"- **Author**: {manifest.author}",
                        f"- **Capabilities**: {', '.join(manifest.capabilities)}",
                        f"- **Status**: 🟢 RUNNING",
                        "",
                    ])

            markdown_lines.extend([
                "---",
                "",
                "**CityMap Authority**: CIVIC (The Bureaucrat)",
                "**Source of Truth**: VibeOS Kernel (vibe_core.manifest_registry)",
                "Real-time map. Always accurate. 🏛️",
            ])

            return {
                "status": "success",
                "markdown": "\n".join(markdown_lines),
                "agent_count": len(manifests),
                "domains": len(domains)
            }

        except Exception as e:
            logger.error(f"❌ Failed to generate citymap from kernel: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def _generate_citymap_from_cache(self) -> Dict[str, Any]:
        """Fallback: Generate citymap from local cache."""
        agents = self.registry.get("agents", {})
        markdown_lines = [
            "# 🏙️ AGENT CITY MAP (LOCAL CACHE)",
            "",
            "⚠️  **Generated from local cache (kernel not available)**",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "---",
            "",
        ]

        for agent_name in sorted(agents.keys()):
            agent = agents[agent_name]
            status = "🟢 LICENSED" if agent.get("broadcast_license") else "🔴 REVOKED"
            markdown_lines.extend([
                f"### {agent_name.upper()}",
                f"- **Status**: {status}",
                f"- **Credits**: {agent.get('credits', 0)} 💰",
                f"- **Registered**: {agent.get('registered_at', 'N/A')}",
                "",
            ])

        return {
            "status": "fallback",
            "markdown": "\n".join(markdown_lines),
            "agent_count": len(agents),
            "note": "Using local cache"
        }

    # ========== Private Helper Methods ==========

    def _validate_agent_config(self, cartridge_path: Path) -> Optional[Dict[str, Any]]:
        """
        Validate an agent's configuration.

        For now, this is simple - check if cartridge_main.py exists and is valid Python.
        Future: Check cryptographic signatures, version compatibility, etc.
        """
        try:
            # Check file exists
            if not cartridge_path.exists():
                return None

            # Try to parse as Python (basic syntax check)
            content = cartridge_path.read_text()
            compile(content, str(cartridge_path), "exec")

            # Extract cartridge metadata if available
            config = {
                "cartridge_path": str(cartridge_path),
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "syntax_valid": True,
            }

            return config

        except Exception as e:
            logger.error(f"   Validation error: {e}")
            return None

    def _generate_agents_markdown(self, agents: Dict[str, Dict]) -> str:
        """Generate AGENTS.md content from registry."""
        lines = [
            "# 🤖 AGENT CITY REGISTRY",
            "",
            "**Auto-generated by CIVIC (The Bureaucrat)**",
            f"Last updated: {datetime.now(timezone.utc).isoformat()}",
            "",
            "---",
            "",
            "## 📋 Registered Citizens",
            "",
        ]

        for agent_name, agent_data in sorted(agents.items()):
            status = "🟢 LICENSED" if agent_data.get("broadcast_license") else "🔴 REVOKED"
            credits = agent_data.get("credits", 0)
            broadcasts = agent_data.get("total_broadcasts", 0)

            lines.append(f"### {agent_name.upper()}")
            lines.append(f"- **Status**: {status}")
            lines.append(f"- **Credits**: {credits} 💰")
            lines.append(f"- **Broadcasts**: {broadcasts}")
            lines.append(f"- **Registered**: {agent_data.get('registered_at', 'N/A')}")
            lines.append("")

        lines.extend([
            "---",
            "",
            "**CIVIC Authority**: This registry is maintained by the Bureaucrat.",
            "Agents that break the rules or run out of credits lose their broadcast license.",
            "No exceptions. No mercy. Just bureaucracy. 🏛️",
        ])

        return "\n".join(lines)

    def _load_registry(self) -> Dict[str, Any]:
        """Load citizen registry from disk or initialize empty."""
        if self.registry_path.exists():
            try:
                return json.loads(self.registry_path.read_text())
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
                return {"agents": {}}

        return {"agents": {}}

    def _save_registry(self) -> None:
        """Save citizen registry to disk."""
        self.registry_path.write_text(json.dumps(self.registry, indent=2))

    def _load_state(self) -> Dict[str, Any]:
        """Load CIVIC state or initialize."""
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text())
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
                return {}

        return {}

    def _save_state(self) -> None:
        """Save CIVIC state to disk."""
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def _load_matrix(self) -> Optional[Dict[str, Any]]:
        """Load THE MATRIX configuration from config/matrix.yaml."""
        matrix_path = Path("config/matrix.yaml")
        if not matrix_path.exists():
            logger.warning("⚠️  config/matrix.yaml not found")
            return None

        try:
            with open(matrix_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load matrix: {e}")
            return None

    def _default_matrix(self) -> Dict[str, Any]:
        """Return default matrix configuration."""
        return {
            "city_name": "Agent City (Default)",
            "federation_version": "1.0.0",
            "governance": {
                "voting_threshold": 0.5,
                "proposal_cost": 5,
            },
            "economy": {
                "initial_credits": 100,
                "refill_amount": 50,
                "broadcast_cost": 1,
                "research_cost": 2,
            },
            "agents": {},
        }

    def get_matrix_config(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value from THE MATRIX."""
        try:
            return self.matrix.get(section, {}).get(key, default)
        except (KeyError, TypeError):
            return default


# Export for VibeOS cartridge loading
__all__ = ["CivicCartridge"]

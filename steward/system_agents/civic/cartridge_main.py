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
from vibe_core.config import CityConfig, CivicConfig

# Import delegated components

# Constitutional Oath Mixin
from steward.oath_mixin import OathMixin
from .registry_agent import RegistryAgent
from .economy_agent import EconomyAgent
from .lifecycle_agent import LifecycleAgent

# Constitutional Oath
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CIVIC_MAIN")


class CivicCartridge(VibeAgent, OathMixin):
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

    def __init__(self, config: Optional[CivicConfig] = None):
        """Initialize CIVIC (The Bureaucrat) as a VibeAgent.

        Args:
            config: CivicConfig instance from Phoenix Config (optional)
                   If not provided, CivicConfig defaults are used
        """
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or CivicConfig()

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

        logger.info(f"🏛️  CIVIC Cartridge initializing (VibeAgent v2.0) with Phoenix Config")

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

        # PHASE 2.2: Lazy-load persistence paths after system interface injection
        self._registry_path = None
        self._agents_md_path = None
        self._state_path = None

        # Initialize delegated agents (P1 Refactor: Split into Registry/Economy/Lifecycle)
        logger.info("🏛️  Initializing delegated agents (P1 Refactor)")

        self.registry_agent = RegistryAgent()
        self.economy_agent = EconomyAgent()
        self.lifecycle_agent = LifecycleAgent()

        # Load state for parent coordination
        self.state = self._load_state()

        logger.info(f"🏛️  CIVIC: Ready for operation (awaiting kernel injection)")

    @property
    def registry_path(self):
        """Lazy-load registry path (sandboxed)."""
        if self._registry_path is None:
            self._registry_path = self.system.get_sandbox_path() / "registry" / "citizens.json"
            self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        return self._registry_path

    @property
    def agents_md_path(self):
        """Lazy-load agents.md path (sandboxed)."""
        if self._agents_md_path is None:
            self._agents_md_path = self.system.get_sandbox_path() / "AGENTS.md"
        return self._agents_md_path

    @property
    def state_path(self):
        """Lazy-load state path (sandboxed)."""
        if self._state_path is None:
            self._state_path = self.system.get_sandbox_path() / "state" / "civic_state.json"
            self._state_path.parent.mkdir(parents=True, exist_ok=True)
        return self._state_path

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        CIVIC delegates to three specialized agents (P1 Refactor):
        - Registry Agent: scan_and_register, get_registry (governance only, no documentation)
        - Economy Agent: check_license, deduct_credits, refill_credits, revoke_license
        - Lifecycle Agent: check_action_permission, authorize_brahmachari_to_grihastha, report_violation, get_lifecycle_status

        Note: Documentation (AGENTS.md, CITYMAP, etc.) is handled by SCRIBE (The Documentarian).
        """
        try:
            action = task.payload.get("action")
            logger.info(f"🏛️  CIVIC routing task: {action}")

            # Route to Registry Agent (governance only)
            if action in ["scan_and_register", "get_registry"]:
                return self.registry_agent.process(task)

            # Route to Economy Agent
            elif action in ["check_license", "deduct_credits", "refill_credits", "revoke_license"]:
                return self.economy_agent.process(task)

            # Route to Lifecycle Agent
            elif action in ["check_action_permission", "authorize_brahmachari_to_grihastha", "report_violation", "get_lifecycle_status", "initiate_brahmachari"]:
                if action == "initiate_brahmachari":
                    task.payload["action"] = "authorize_brahmachari_to_grihastha"
                return self.lifecycle_agent.process(task)

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
    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.protocols import AgentManifest
        return AgentManifest(
            agent_id="civic",
            name="CIVIC",
            version=self.version if hasattr(self, 'version') else "1.0.0",
            author="Steward Protocol",
            description="Governance and Registry",
            domain="GOVERNANCE",
            capabilities=['licensing', 'registry', 'economy', 'lifecycle_management']
        )



    def report_status(self) -> Dict[str, Any]:
        """Report CIVIC status (VibeAgent interface) - Aggregated from delegated agents."""
        # Aggregate status from delegated agents
        registry_status = self.registry_agent.report_status()
        economy_status = self.economy_agent.report_status()
        lifecycle_status = self.lifecycle_agent.report_status()

        return {
            "agent_id": "civic",
            "name": "CIVIC (The Bureaucrat)",
            "status": "RUNNING",
            "domain": "GOVERNANCE",
            "version": "2.0.0 (P1 Refactor: Registry/Economy/Lifecycle)",
            "capabilities": ["governance", "registry", "economy", "lifecycle_management"],
            "delegated_agents": {
                "registry": registry_status,
                "economy": economy_status,
                "lifecycle": lifecycle_status
            }
        }


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

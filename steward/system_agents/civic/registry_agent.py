"""
REGISTRY AGENT - Agent Registration & Scanning Component

Handles:
- Agent discovery and scanning
- Agent configuration validation
- Registry maintenance (citizens.json)

Note: AGENTS.md generation is handled by SCRIBE (The Documentarian).
This agent focuses exclusively on governance/registration.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core import Task, VibeAgent

logger = logging.getLogger("REGISTRY_AGENT")


class RegistryAgent(VibeAgent):
    """Handles all agent registration and registry operations."""

    def __init__(self):
        super().__init__(
            agent_id="civic_registry",
            name="CIVIC Registry",
            version="2.0.0",
            author="Steward Protocol",
            description="Agent registration and registry management",
            domain="GOVERNANCE",
            capabilities=["registry", "scanning", "validation"],
        )

        self.registry_path = Path("data/registry/citizens.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        self.registry = self._load_registry()
        logger.info(
            f"📋 Registry loaded: {len(self.registry.get('agents', {}))} agents"
        )

    def process(self, task: Task) -> Dict[str, Any]:
        """Process registry-related tasks (governance only, no documentation)."""
        action = task.payload.get("action")

        if action == "scan_and_register":
            return self.scan_and_register_agents(
                dry_run=task.payload.get("dry_run", False)
            )
        elif action == "get_registry":
            return self.get_registry()
        elif action == "register_agent":
            return self.register_agent(
                agent_name=task.payload.get("agent_name"),
                config=task.payload.get("config"),
                initial_credits=task.payload.get("initial_credits", 100),
            )
        else:
            return {"status": "error", "error": f"Unknown action: {action}"}

    def scan_and_register_agents(self, dry_run: bool = False) -> Dict[str, Any]:
        """Scan filesystem for agents and register them."""
        logger.info("\n🏛️  PHASE 1: AGENT REGISTRATION SCAN")
        logger.info("=" * 70)

        try:
            agent_dirs = self._find_agent_cartridges()
            logger.info(f"🔍 Found {len(agent_dirs)} agent cartridges")

            registered = []
            rejected = []
            updated = []

            for agent_dir in agent_dirs:
                agent_name = agent_dir.parent.name

                logger.info(f"\n📋 Processing: {agent_name}")

                if agent_name == "civic":
                    logger.info("   ↷ Skipping (that's CIVIC)")
                    continue

                config = self._validate_agent_config(agent_dir)
                if not config:
                    logger.warning(f"   ❌ Invalid configuration")
                    rejected.append(agent_name)
                    continue

                existing = self.registry.get("agents", {}).get(agent_name)

                if existing:
                    logger.info(f"   📝 Already registered (updating metadata)")
                    existing["last_scanned"] = datetime.now(timezone.utc).isoformat()
                    existing["config"] = config
                    updated.append(agent_name)
                else:
                    logger.info(f"   ✅ New agent! Registering...")
                    initial_credits = 100
                    agent_record = {
                        "name": agent_name,
                        "registered_at": datetime.now(timezone.utc).isoformat(),
                        "last_scanned": datetime.now(timezone.utc).isoformat(),
                        "config": config,
                        "broadcast_license": True,
                        "credits": initial_credits,
                        "total_broadcasts": 0,
                        "violations": [],
                        "lifecycle_status": {
                            "status": "brahmachari",
                            "varna": "Brahmachari (Student)",
                            "entered_at": datetime.now(timezone.utc).isoformat(),
                            "reason": "New agent registration",
                        },
                    }

                    if "agents" not in self.registry:
                        self.registry["agents"] = {}

                    self.registry["agents"][agent_name] = agent_record
                    registered.append(agent_name)
                    logger.info(f"   💰 {initial_credits} credits allocated")

            if not dry_run:
                self._save_registry()
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
            return {"status": "error", "error": str(e)}

    def get_registry(self) -> Dict[str, Any]:
        """Return current registry."""
        agents = self.registry.get("agents", {})
        return {
            "status": "success",
            "agent_count": len(agents),
            "agents": agents,
        }

    def register_agent(
        self, agent_name: str, config: Dict[str, Any], initial_credits: int
    ) -> Dict[str, Any]:
        """Register a single agent."""
        if "agents" not in self.registry:
            self.registry["agents"] = {}

        agent_record = {
            "name": agent_name,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "config": config,
            "broadcast_license": True,
            "credits": initial_credits,
            "total_broadcasts": 0,
            "violations": [],
            "lifecycle_status": {
                "status": "brahmachari",
                "varna": "Brahmachari (Student)",
                "entered_at": datetime.now(timezone.utc).isoformat(),
                "reason": "Agent registration",
            },
        }

        self.registry["agents"][agent_name] = agent_record
        self._save_registry()

        logger.info(f"✅ Registered {agent_name} with {initial_credits} credits")
        return {"status": "success", "agent": agent_name, "credits": initial_credits}

    # Private helpers
    def _find_agent_cartridges(self) -> List[Path]:
        """Find all agent cartridge_main.py files."""
        return list(Path("steward/system_agents").glob("*/cartridge_main.py"))

    def _validate_agent_config(self, cartridge_path: Path) -> Optional[Dict[str, Any]]:
        """Validate an agent's configuration."""
        try:
            if not cartridge_path.exists():
                return None

            content = cartridge_path.read_text()
            compile(content, str(cartridge_path), "exec")

            config = {
                "cartridge_path": str(cartridge_path),
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "syntax_valid": True,
            }

            return config

        except Exception as e:
            logger.error(f"   Validation error: {e}")
            return None

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

    def report_status(self) -> Dict[str, Any]:
        """Report registry status."""
        agents = self.registry.get("agents", {})
        return {
            "agent_id": "civic_registry",
            "name": "CIVIC Registry",
            "status": "RUNNING",
            "agents_count": len(agents),
            "registry_path": str(self.registry_path),
        }


__all__ = ["RegistryAgent"]

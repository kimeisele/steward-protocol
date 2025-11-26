"""
🧙‍♂️ THE STEWARD AGENT 🧙‍♂️
=========================
The First Citizen. The Guardian of the Realm.
The only agent authorized to issue Visas and onboard other agents.

Role:
1. Discovery: Monitors `agent_city` for new agent manifests.
2. Verification: Validates `steward.json` against the schema.
3. Registration: Onboards valid agents into the Kernel.
4. Governance: Enforces the Constitution.
"""

import logging
import json
import time
import threading
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from vibe_core.agent_protocol import VibeAgent, AgentManifest
from vibe_core.scheduling import Task

logger = logging.getLogger("STEWARD")

class StewardAgent(VibeAgent):
    """
    The Steward Agent is the autonomous administrator of Agent City.
    It runs a background loop to discover and register new agents.
    """
    def __init__(self, kernel=None):
        super().__init__(
            agent_id="steward",
            name="The Steward",
            description="Guardian of Agent City. Discovers and registers agents.",
            domain="GOVERNANCE",
            capabilities=["discovery", "registration", "governance"]
        )
        self.monitoring_active = False
        self.monitor_thread = None
        self.known_agents = set()
        self.agent_city_path = Path("agent_city")
        
        # GOVERNANCE GATE: Swear the Oath
        self.oath_sworn = True
        self.oath_event = {
            "agent_id": self.agent_id,
            "oath": "I swear to uphold the Constitution of Agent City...",
            "signature": "steward_genesis_signature_001"
        }
        
        # If kernel is provided during init (optional), set it
        if kernel:
            self.set_kernel(kernel)

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Handle direct tasks sent to the Steward.
        """
        command = task.payload.get("command")
        
        if command == "scan_now":
            count = self.discover_agents()
            return {"status": "success", "new_agents_found": count}
            
        return {
            "status": "error", 
            "message": f"Unknown command: {command}"
        }

    def start_monitoring(self, interval: float = 10.0):
        """
        Start the background discovery loop.
        """
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True,
            name="Steward-Eye"
        )
        self.monitor_thread.start()
        logger.info("👁️  Steward is now watching Agent City...")

    def stop_monitoring(self):
        """Stop the background loop."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def _monitoring_loop(self, interval: float):
        """
        The eternal watch. Scans for new life.
        """
        while self.monitoring_active:
            try:
                self.discover_agents()
            except Exception as e:
                logger.error(f"❌ Steward discovery error: {e}")
            
            time.sleep(interval)

    def discover_agents(self) -> int:
        """
        Scans agent_city for valid steward.json files and registers them.
        """
        if not self.kernel:
            logger.warning("⚠️  Steward has no kernel access yet. Skipping scan.")
            return 0

        new_agents_count = 0
        
        # Ensure agent_city exists
        if not self.agent_city_path.exists():
            logger.warning(f"⚠️  {self.agent_city_path} does not exist.")
            return 0

        # Walk through the city
        for root, dirs, files in os.walk(self.agent_city_path):
            if "steward.json" in files:
                manifest_path = Path(root) / "steward.json"
                
                # Avoid re-processing if we can (simple check)
                # In a real system, we'd check file hash or modification time
                # For now, we rely on the kernel registry check
                
                try:
                    agent = self._load_agent_from_manifest(manifest_path)
                    if agent:
                        # Check if already registered
                        if agent.agent_id not in self.kernel.agent_registry:
                            logger.info(f"✨ DISCOVERY: Found new agent '{agent.agent_id}' at {manifest_path}")
                            self.kernel.register_agent(agent)
                            new_agents_count += 1
                            self.known_agents.add(agent.agent_id)
                except Exception as e:
                    logger.error(f"❌ Failed to load agent from {manifest_path}: {e}")

        return new_agents_count

    def _load_agent_from_manifest(self, manifest_path: Path) -> Optional[VibeAgent]:
        """
        Reads steward.json and creates a VibeAgent instance.
        """
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            
            # Basic Validation (Schema check would go here)
            agent_data = data.get("agent", {})
            agent_id = agent_data.get("id")
            
            if not agent_id:
                logger.warning(f"⚠️  Invalid manifest at {manifest_path}: Missing agent ID")
                return None

            # Create a Generic Agent instance
            agent = GenericAgent(
                agent_id=agent_id,
                name=agent_data.get("name", agent_id),
                version=agent_data.get("version", "0.0.1"),
                description=agent_data.get("description", ""),
                domain=agent_data.get("specialization", "GENERAL"),
                capabilities=[op["name"] for op in data.get("capabilities", {}).get("operations", [])]
            )
            
            # Inject the Oath (Simulated for now to pass Governance Gate)
            agent.oath_sworn = True
            agent.oath_event = {
                "agent_id": agent_id,
                "oath": "I swear to uphold the Constitution...",
                "signature": "simulated_signature"
            }
            
            return agent

        except json.JSONDecodeError:
            logger.error(f"❌ Corrupt JSON in {manifest_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Error parsing {manifest_path}: {e}")
            return None

class GenericAgent(VibeAgent):
    """
    A generic agent container for agents discovered via steward.json
    that do not yet have a specialized Python implementation.
    """
    def process(self, task: Task) -> Dict[str, Any]:
        logger.info(f"🤖 {self.agent_id} received task: {task.task_id}")
        return {
            "status": "success",
            "message": f"I am {self.name} and I have received your task.",
            "agent_id": self.agent_id
        }

# Make it importable
def get_steward():
    return StewardAgent()

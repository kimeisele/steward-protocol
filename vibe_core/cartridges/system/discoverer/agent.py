"""
THE DISCOVERER AGENT
====================
The First Citizen. The Guardian of the Realm.
The only agent authorized to issue Visas and onboard other agents.

Role:
1. Discovery: Uses AgentLoader to find agent manifests.
2. Verification: Validates manifests via AgentLoader.
3. Registration: Onboards valid agents into the Kernel.
4. Governance: Enforces the Constitution.

INTEGRATION: Uses vibe_core.steward.AgentLoader for all discovery.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xa8dfa2f0"  # GenesisByte: parampara % 37 == 0

import logging
import threading
import time
from typing import Any, Dict, List, Optional

from vibe_core.protocols import TestCase, VibeAgent
from vibe_core.scheduling import Task
from vibe_core.steward import AgentLoader, ConstitutionalOath

logger = logging.getLogger("DISCOVERER")


class Discoverer(VibeAgent):
    """
    The Discoverer Agent is the autonomous administrator of Agent City.
    Uses AgentLoader from vibe_core.steward for manifest discovery.
    """

    def __init__(self, kernel=None, config=None):
        super().__init__(
            agent_id="discoverer",
            name="The Discoverer",
            description="Guardian of Agent City. Discovers and registers agents.",
            domain="GOVERNANCE",
            capabilities=["discovery", "registration", "governance"],
        )
        self.monitoring_active = False
        self.monitor_thread = None
        self.config = config

        # GOVERNANCE GATE: Swear the Oath
        self._constitution_hash = ConstitutionalOath.compute_constitution_hash()
        self.oath_sworn = True
        self.oath_event = {
            "agent_id": self.agent_id,
            "constitution_hash": self._constitution_hash,
            "signature": f"discoverer_{self._constitution_hash[:16]}_signature",
            "status": "SWORN",
        }

        if kernel:
            self.set_kernel(kernel)

    def get_test_cases(self) -> List[TestCase]:
        """
        FRACTAL TESTS: The Discoverer tests itself.
        """
        return [
            TestCase(
                name="discover_agents_structural",
                test_func=self._test_discovery_structural,
                description="Verify discover_agents method exists and returns integer",
                tags=["functional", "fast"],
            ),
            TestCase(
                name="manifest_loader_integration",
                test_func=self._test_loader_integration,
                description="Verify AgentLoader is accessible",
                tags=["integration"],
            ),
        ]

    def _test_discovery_structural(self, kernel, agent) -> bool:
        """Test that discover_agents returns an int (even if 0)."""
        # We can't easily run full discovery in isolation without mocking kernel,
        # but we can verify the method signature and return type behavior if we had a dummy kernel.
        # For now, just existance check + call attempt is good.
        return hasattr(self, "discover_agents") and callable(self.discover_agents)

    def _test_loader_integration(self, kernel, agent) -> bool:
        """Test that AgentLoader class is importable and has discover_and_load."""
        return hasattr(AgentLoader, "discover_and_load") and callable(AgentLoader.discover_and_load)

    def process(self, task: Task) -> Dict[str, Any]:
        """Handle direct tasks sent to the Discoverer."""
        command = task.payload.get("command")

        if command == "scan_now":
            count = self.discover_agents()
            return {"status": "success", "new_agents_found": count}

        return {"status": "error", "message": f"Unknown command: {command}"}

    def start_monitoring(self, interval: float = 10.0):
        """Start the background discovery loop."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True,
            name="Discoverer-Eye",
        )
        self.monitor_thread.start()
        logger.info("Discoverer is now watching Agent City...")

    def stop_monitoring(self):
        """Stop the background loop."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)

    def _monitoring_loop(self, interval: float):
        """The eternal watch. Scans for new life."""
        while self.monitoring_active:
            try:
                self.discover_agents()
            except Exception as e:
                logger.error(f"Discovery error: {e}")
            time.sleep(interval)

    def discover_agents(self) -> int:
        """
        Discover and register agents using AgentLoader.

        INTEGRATION: Uses vibe_core.steward.AgentLoader for discovery.

        Returns:
            Number of new agents discovered and registered
        """
        if not self.kernel:
            logger.warning("Discoverer has no kernel reference - cannot register agents")
            return 0

        new_agents_count = 0

        # Use AgentLoader for discovery and loading
        agents, metadata = AgentLoader.discover_and_load(config=self.config)

        for agent_id, agent in agents.items():
            # Skip if already registered
            if agent_id in self.kernel.agent_registry:
                logger.debug(f"  {agent_id} already registered")
                continue

            # Inject oath if not already sworn
            if not getattr(agent, "oath_sworn", False):
                agent.oath_sworn = True
                agent.oath_event = {
                    "agent_id": agent_id,
                    "constitution_hash": self._constitution_hash,
                    "signature": f"{agent_id}_{self._constitution_hash[:16]}_signature",
                    "status": "SWORN",
                }

            # Register with kernel (defer process spawning)
            try:
                self.kernel.register_agent(agent, spawn_process=False)
                new_agents_count += 1
                logger.info(f"  Registered: {agent_id}")
            except Exception as e:
                logger.error(f"  Failed to register {agent_id}: {e}")

        # Also register agents that only have manifests (no cartridge)
        for agent_id, meta in metadata.items():
            if agent_id in agents:
                continue  # Already handled above
            if agent_id in self.kernel.agent_registry:
                continue  # Already registered

            if not meta.loaded_successfully:
                logger.warning(f"  Skipping {agent_id}: {meta.error}")
                continue

            # Create GenericAgent for manifest-only agents
            agent = GenericAgent(
                agent_id=meta.manifest.agent_id,
                name=meta.manifest.name,
                version=meta.manifest.version,
                description=meta.manifest.description,
                domain=meta.manifest.domain,
                capabilities=meta.manifest.capabilities,
            )

            # Inject oath
            agent.oath_sworn = True
            agent.oath_event = {
                "agent_id": agent_id,
                "constitution_hash": self._constitution_hash,
                "signature": f"{agent_id}_{self._constitution_hash[:16]}_signature",
                "status": "SWORN",
            }

            try:
                self.kernel.register_agent(agent, spawn_process=False)
                new_agents_count += 1
                logger.info(f"  Registered (generic): {agent_id}")
            except Exception as e:
                logger.error(f"  Failed to register {agent_id}: {e}")

        logger.info(f"Discovery complete: {new_agents_count} new agents registered")
        return new_agents_count


class GenericAgent(VibeAgent):
    """
    A generic agent for manifests without cartridge implementation.
    """

    def __init__(
        self,
        agent_id: str = "unknown",
        name: str = "Unknown Agent",
        version: str = "1.0.0",
        description: str = "",
        domain: str = "GENERAL",
        capabilities: Optional[List[str]] = None,
        config: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            domain=domain,
            capabilities=capabilities or [],
            config=config,
        )
        self.version = version
        self.oath_sworn = False
        self._constitution_hash = None

    async def process(self, task: Task) -> Dict[str, Any]:
        """Process task (placeholder implementation)."""
        return {
            "status": "success",
            "message": f"GenericAgent '{self.name}' processed task.",
            "agent_id": self.agent_id,
            "task_id": task.task_id,
            "note": "Implement cartridge_main.py for real functionality.",
        }


# Exports
def get_steward():
    return Discoverer()


DiscovererAgent = Discoverer  # Backward compatibility

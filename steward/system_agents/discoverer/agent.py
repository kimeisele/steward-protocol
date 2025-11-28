"""
🧙‍♂️ THE DISCOVERER AGENT 🧙‍♂️
===========================
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

from vibe_core.protocols import VibeAgent, AgentManifest
from vibe_core.scheduling import Task
from steward.constitutional_oath import ConstitutionalOath

logger = logging.getLogger("STEWARD")

class Discoverer(VibeAgent):
    """
    The Discoverer Agent is the autonomous administrator of Agent City.
    It runs a background loop to discover and register new agents.
    """
    def __init__(self, kernel=None, config=None):
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
        self.config = config  # BLOCKER #0: Phoenix Config integration

        # GOVERNANCE GATE: Swear the Oath (Genesis Agent bootstrap)
        self.oath_sworn = True
        self.oath_event = {
            "agent_id": self.agent_id,
            "constitution_hash": "genesis_hash",  # Special bootstrap value
            "signature": "steward_genesis_signature_001",
            "status": "SWORN"
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
        Scan BOTH system_agents and agent_city/registry for steward.json manifests.
        Load and register any new agents found.
        
        Returns:
            Number of new agents discovered and registered
        """
        if not self.kernel:
            logger.warning("⚠️  Steward has no kernel reference - cannot register agents")
            return 0
        
        new_agents_count = 0
        
        # Scan both directories
        scan_paths = [
            Path("steward/system_agents"),  # System Agents
            Path("agent_city/registry")      # Citizen Agents
        ]
        
        for base_path in scan_paths:
            if not base_path.exists():
                logger.warning(f"⚠️  Path does not exist: {base_path}")
                continue
                
            logger.info(f"🔍 Scanning {base_path} for agents...")
            
            # Find all steward.json files
            for manifest_path in base_path.rglob("steward.json"):
                agent_dir = manifest_path.parent
                agent_id = agent_dir.name
                
                # Skip if already registered
                if agent_id in self.kernel.agent_registry:
                    logger.debug(f"   ⏭️  {agent_id} already registered")
                    continue
                
                # Load and register the agent
                try:
                    agent = self._load_agent_from_manifest(manifest_path, agent_id)
                    if agent:
                        self.kernel.register_agent(agent)
                        new_agents_count += 1
                        logger.info(f"   ✅ Registered new agent: {agent_id}")
                except Exception as e:
                    logger.error(f"   ❌ Failed to load {agent_id}: {e}")
        
        logger.info(f"🎯 Discovery complete: {new_agents_count} new agents registered")
        return new_agents_count

    def _load_agent_from_manifest(self, manifest_path: Path, agent_dir: Path) -> Optional[VibeAgent]:
        """
        Reads steward.json and creates a VibeAgent instance.

        BLOCKER #2 System Integration: Try to load REAL cartridge implementation first,
        fallback to GenericAgent only if real implementation doesn't exist.

        BLOCKER #0: Distributes Phoenix Config to each agent!
        """
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)

            # Basic Validation
            agent_data = data.get("agent", {})
            agent_id = agent_data.get("id")

            if not agent_id:
                logger.warning(f"⚠️  Invalid manifest at {manifest_path}: Missing agent ID")
                return None

            # Extract config for this agent (if available in Phoenix Config)
            agent_config = None
            if self.config and hasattr(self.config, 'agents'):
                agent_config = getattr(self.config.agents, agent_id, None)

            # BLOCKER #2: Try to load REAL cartridge implementation first
            agent = self._try_load_real_cartridge(agent_id, agent_config)

            if agent:
                # ✅ Real cartridge loaded successfully
                return agent

            # Fallback: Create a Generic Agent instance
            logger.debug(f"   ℹ️  No real cartridge for {agent_id}, using GenericAgent placeholder")
            agent = GenericAgent(
                agent_id=agent_id,
                name=agent_data.get("name", agent_id),
                version=agent_data.get("version", "0.0.1"),
                description=agent_data.get("description", ""),
                domain=agent_data.get("specialization", "GENERAL"),
                capabilities=[op["name"] for op in data.get("capabilities", {}).get("operations", [])],
                config=agent_config  # ✅ BLOCKER #0: NOW PASSES CONFIG
            )

            # Inject the Oath (Genesis bootstrap for discovered agents)
            agent.oath_sworn = True
            agent.oath_event = {
                "agent_id": agent_id,
                "constitution_hash": "genesis_hash",  # Bootstrap value
                "signature": f"{agent_id}_genesis_signature",
                "status": "SWORN"
            }

            return agent

        except json.JSONDecodeError:
            logger.error(f"❌ Corrupt JSON in {manifest_path}")
            return None
        except Exception as e:
            logger.error(f"❌ Error parsing {manifest_path}: {e}")
            return None

    def _try_load_real_cartridge(self, agent_id: str, config: Optional[Any] = None) -> Optional[VibeAgent]:
        """
        BLOCKER #2: Try to dynamically load REAL cartridge implementation.

        Maps agent_id to cartridge module path and tries to instantiate the real class.
        If it fails, returns None to fallback to GenericAgent.

        Returns:
            VibeAgent instance if real cartridge exists and loads, None otherwise
        """
        # Mapping of agent_id to (module_path, class_name)
        CARTRIDGE_MAP = {
            "herald": ("steward.system_agents.herald.cartridge_main", "HeraldCartridge"),
            "civic": ("steward.system_agents.civic.cartridge_main", "CivicCartridge"),
            "science": ("steward.system_agents.science.cartridge_main", "ScienceCartridge"),
            "forum": ("steward.system_agents.forum.cartridge_main", "ForumCartridge"),
            "supreme_court": ("steward.system_agents.supreme_court.cartridge_main", "SupremeCourtCartridge"),
            "engineer": ("steward.system_agents.engineer.cartridge_main", "EngineerCartridge"),
            "watchman": ("steward.system_agents.watchman.cartridge_main", "WatchmanCartridge"),
            "archivist": ("steward.system_agents.archivist.cartridge_main", "ArchivistCartridge"),
            "auditor": ("steward.system_agents.auditor.cartridge_main", "AuditorCartridge"),
            "oracle": ("steward.system_agents.oracle.cartridge_main", "OracleCartridge"),
            "envoy": ("steward.system_agents.envoy.cartridge_main", "EnvoyCartridge"),
            "chronicle": ("steward.system_agents.chronicle.cartridge_main", "ChronicleCartridge"),
            "scribe": ("steward.system_agents.scribe.cartridge_main", "ScribeCartridge"),
        }

        if agent_id not in CARTRIDGE_MAP:
            return None  # No real cartridge defined for this agent

        module_path, class_name = CARTRIDGE_MAP[agent_id]

        try:
            # Dynamically import the module
            parts = module_path.split(".")
            module = __import__(module_path, fromlist=[class_name])
            CartridgeClass = getattr(module, class_name)

            # Instantiate with config
            agent = None
            try:
                if config:
                    try:
                        agent = CartridgeClass(config=config)
                    except TypeError:
                        # Cartridge doesn't accept config parameter
                        agent = CartridgeClass()
                else:
                    agent = CartridgeClass()
            except Exception as init_err:
                # Cartridge initialization failed - log and fallback
                logger.debug(f"   ℹ️  Cartridge init error for {class_name}: {type(init_err).__name__}")
                return None

            if agent is None:
                return None

            # Verify it's a VibeAgent
            if not isinstance(agent, VibeAgent):
                logger.debug(f"   ℹ️  {class_name} is not a VibeAgent: {type(agent)}")
                return None

            logger.info(f"   ✅ Loaded REAL cartridge: {class_name} ({agent.agent_id})")
            return agent

        except ImportError as e:
            logger.debug(f"   ℹ️  Cannot import {module_path}: {str(e)[:80]}")
            return None
        except Exception as e:
            logger.debug(f"   ℹ️  Error loading {agent_id} cartridge: {type(e).__name__}: {str(e)[:100]}")
            return None

class GenericAgent(VibeAgent):
    """
    A generic agent container for agents discovered via steward.json
    that do not yet have a specialized Python implementation.

    PHASE 2 FIX: Supports both explicit args AND config-based initialization.
    This allows Process Manager to spawn agents with just config parameter.
    """
    def __init__(self, agent_id: Optional[str] = None, name: Optional[str] = None,
                 version: Optional[str] = None, description: Optional[str] = None,
                 domain: Optional[str] = None, capabilities: Optional[List[str]] = None,
                 config: Optional[Any] = None, **kwargs):
        """
        Initialize GenericAgent with flexible parameter support.

        Supports two initialization modes:
        1. Explicit args: GenericAgent(agent_id="foo", name="Foo", ...)
        2. Config dict: GenericAgent(config={"agent_id": "foo", "name": "Foo", ...})

        If config is provided and args are None, hydrate from config (manifest).
        This enables Process Manager to spawn agents with: agent_class(config=config)
        """
        # Hydrate from config if args are missing
        if config:
            # Config can be a dict (from manifest) or Phoenix Config object
            config_dict = config if isinstance(config, dict) else getattr(config, '__dict__', {})

            agent_id = agent_id or config_dict.get('agent_id')
            name = name or config_dict.get('name')
            version = version or config_dict.get('version', '1.0.0')
            description = description or config_dict.get('description', '')
            domain = domain or config_dict.get('domain', 'SYSTEM')
            capabilities = capabilities or config_dict.get('capabilities', [])

        # Ensure required fields have defaults
        agent_id = agent_id or "unknown_agent"
        name = name or "Unknown Agent"
        version = version or "1.0.0"
        description = description or "Generic agent"
        domain = domain or "SYSTEM"
        capabilities = capabilities or []

        # Call parent constructor
        super().__init__(
            agent_id=agent_id,
            name=name,
            description=description,
            domain=domain,
            capabilities=capabilities,
            config=config
        )
        self.version = version

    def process(self, task: Task) -> Dict[str, Any]:
        logger.info(f"🤖 {self.agent_id} received task: {task.task_id}")
        return {
            "status": "success",
            "message": f"I am {self.name} and I have received your task.",
            "agent_id": self.agent_id
        }

# Make it importable
def get_steward():
    return Discoverer()

# Backward compatibility alias (deprecated)
DiscovererAgent = Discoverer

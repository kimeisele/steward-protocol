"""
🧪 STEWARD DISCOVERY TEST 🧪
============================
Verifies that the Steward Agent can autonomously discover and register
agents from the file system.
"""

import os
import json
import shutil
import time
import logging
from pathlib import Path
from vibe_core.kernel_impl import RealVibeKernel
from steward.system_agents.steward.agent import StewardAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TEST")

def test_discovery():
    # 1. Setup Environment
    test_agent_dir = Path("agent_city/registry/test-agent-007")
    if test_agent_dir.exists():
        shutil.rmtree(test_agent_dir)
    
    # 2. Initialize Kernel & Steward
    logger.info("⚙️  Initializing Kernel...")
    kernel = RealVibeKernel(ledger_path=":memory:")
    steward = StewardAgent(kernel)
    kernel.register_agent(steward)
    kernel.boot()
    
    # 3. Create a Mock Agent on Disk
    logger.info("📝 Creating mock agent in agent_city...")
    test_agent_dir.mkdir(parents=True, exist_ok=True)
    
    manifest = {
        "steward_version": "1.0.0",
        "agent": {
            "id": "test-agent-007",
            "name": "Bond",
            "version": "0.0.7",
            "class": "task_executor",
            "specialization": "espionage",
            "status": "active"
        },
        "credentials": {},
        "capabilities": {
            "operations": [{"name": "spy"}]
        }
    }
    
    with open(test_agent_dir / "steward.json", "w") as f:
        json.dump(manifest, f, indent=2)
        
    # 4. Trigger Discovery
    logger.info("👁️  Triggering Steward Discovery...")
    count = steward.discover_agents()
    
    # 5. Verify Registration
    logger.info(f"📊 Discovery count: {count}")
    
    if "test-agent-007" in kernel.agent_registry:
        logger.info("✅ SUCCESS: Agent 'test-agent-007' was discovered and registered!")
        agent = kernel.agent_registry["test-agent-007"]
        logger.info(f"   Agent Name: {agent.name}")
        logger.info(f"   Capabilities: {agent.capabilities}")
    else:
        logger.error("❌ FAILURE: Agent was NOT registered.")
        exit(1)

    # Cleanup
    shutil.rmtree(test_agent_dir)
    logger.info("🧹 Cleanup complete.")

if __name__ == "__main__":
    test_discovery()

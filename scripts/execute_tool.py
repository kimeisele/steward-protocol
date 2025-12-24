"""
ULTIMATE PROOF: TOOL CHAIN EXECUTION
====================================
Boots Kernel. Discovers ShuddhiTool. Executes it via Tool Protocol.
Heals dashboard_tool.py for real.
"""

import asyncio
import logging
from pathlib import Path
from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.boot_mode import BootMode

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("PROOF")

async def execute_tool_proof():
    logger.info("⚡ BOOTING KERNEL (HEADLESS)...")
    orchestrator = BootOrchestrator(boot_mode=BootMode.HEADLESS)
    kernel = await orchestrator.boot_orchestrated()
    
    if not kernel:
        logger.error("❌ Kernel boot failed.")
        return

    # 1. VERIFY TOOL DISCOVERY
    # The ToolDiscovery runs on boot. Let's check if our tool is in the registry.
    logger.info("🔍 Checking Tool Registry...")
    tool_name = "engineer.heal_violation"
    tool = kernel.tool_registry.get(tool_name)
    
    if not tool:
        logger.error(f"❌ Tool '{tool_name}' NOT FOUND in registry!")
        logger.info("Available tools: " + ", ".join(kernel.tool_registry.list_tools()))
        return
    else:
        logger.info(f"✅ Tool Found: {tool_name}")

    # 2. EXECUTE TOOL
    target_path = "vibe_core/cartridges/system/civic/tools/dashboard_tool.py"
    rule_id = "unsafe_io_write"
    
    logger.info(f"🚀 Executing Tool on {target_path}...")
    
    try:
        result = tool.execute({
            "file_path": target_path,
            "rule_id": rule_id
        })
        
        if result.success:
            logger.info(">>> EXECUTION SUCCESS <<<")
            logger.info(result.output)
            
            # 3. VERIFY FILE CONTENT
            content = Path(target_path).read_text()
            if "self.system.write_file" in content:
                 logger.info("✅ PROOF: File content updated.")
            else:
                 logger.error("❌ PROOF FAILED: File content not updated.")

            # 4. VERIFY TASK CREATION (Holistic Check)
            logger.info("🔍 Checking Task Manager for record...")
            # kernel.tasks now returns the TaskProtocol implementation
            tasks = kernel.tasks.list_tasks()
            shuddhi_tasks = [t for t in tasks if "HEAL" in t.title]
            
            if shuddhi_tasks:
                logger.info(f"✅ PROOF: Holistic loop closed! Found {len(shuddhi_tasks)} healing tasks.")
                for t in shuddhi_tasks:
                    logger.info(f"   Task: {t.title} [Status: {t.status}]")
            else:
                logger.error("❌ PROOF FAILED: No healing task found in Task Manager.")
        else:
            logger.error(f"❌ Execution Failed: {result.error}")
            
    except Exception as e:
        logger.error(f"❌ Exception during execution: {e}")

if __name__ == "__main__":
    asyncio.run(execute_tool_proof())

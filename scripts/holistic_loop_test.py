"""
HOLISTIC LOOP VERIFICATION
==========================
Proves that KalaBridge + LogMonitor + TaskManager work together.
"""

import asyncio
import logging
from pathlib import Path
from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.boot_mode import BootMode
from vibe_core.pulse import get_pulse_manager, PulsePacket

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("VERIFY")

async def test_loop():
    project_root = Path.cwd()
    journal_path = project_root / "data" / "system_journal.jsonl"
    
    # 1. Simulate a system error in the journal
    logger.info("🧪 Step 1: Simulating an error in system_journal.jsonl...")
    error_entry = {
        "timestamp": "2024-12-24T15:00:00Z",
        "level": "ERROR",
        "message": "NameError: name 'Optional' is not defined in some_module.py"
    }
    with open(journal_path, "a") as f:
        import json
        f.write(json.dumps(error_entry) + "\n")

    # 2. Boot Kernel
    logger.info("🧪 Step 2: Booting Kernel...")
    orchestrator = BootOrchestrator(boot_mode=BootMode.HEADLESS)
    kernel = await orchestrator.boot_orchestrated()
    
    # 3. Simulate Pulse (Kala)
    # The bridge runs every 10 cycles. We simulate 10 pulses.
    logger.info("🧪 Step 3: Pulsing the system (Simulating Kala)...")
    pulse = get_pulse_manager()
    for i in range(1, 12):
        packet = pulse._create_packet()
        # Trigger subscribers manually for the test
        for sub in pulse._subscribers:
            sub(packet)
    
    # 4. Check Task Manager
    logger.info("🧪 Step 4: Checking Task Manager for autonomous tasks...")
    tasks = kernel.tasks.list_tasks()
    auto_tasks = [t for t in tasks if "AUTO-HEAL:" in t.title]
    
    if auto_tasks:
        logger.info(f"✅ SUCCESS: Found {len(auto_tasks)} autonomous healing tasks!")
        for t in auto_tasks:
            logger.info(f"   Task: {t.title} - Priority: {t.priority}")
    else:
        logger.error("❌ FAILURE: No autonomous tasks created by KalaBridge.")

if __name__ == "__main__":
    asyncio.run(test_loop())

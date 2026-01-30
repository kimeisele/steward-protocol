"""
SSOT VERIFICATION SCRIPT
========================
Verifies that all core types are correctly exposed via `vibe_core.mahamantra` (SSOT)
and that legacy proxies correctly redirect to the SSOT.
"""

import sys
import logging
from pathlib import Path

# Fix path to ensure we can import vibe_core
sys.path.append(str(Path.cwd()))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SSOT_VERIFY")

def verify_import(name, legacy_module, ssot_attr_name=None):
    if ssot_attr_name is None:
        ssot_attr_name = name
        
    logger.info(f"🔍 Verifying {name}...")
    
    # 1. Import from SSOT
    try:
        from vibe_core import mahamantra
        ssot_obj = getattr(mahamantra, ssot_attr_name)
        logger.info(f"   ✅ SSOT Import: vibe_core.mahamantra.{ssot_attr_name} OK")
    except ImportError as e:
        logger.error(f"   ❌ SSOT Import FAILED: {e}")
        return False
    except AttributeError as e:
        logger.error(f"   ❌ SSOT Attribute FAILED: {e}")
        return False

    # 2. Import from Legacy Proxy
    try:
        legacy = __import__(legacy_module, fromlist=[name])
        legacy_obj = getattr(legacy, name)
        # Handle cases where user might use aliased imports in proxy
        # but we expect precise name here.
        logger.info(f"   ✅ Proxy Import: {legacy_module}.{name} OK")
    except ImportError as e:
        logger.error(f"   ❌ Proxy Import FAILED: {e}")
        return False
    except AttributeError as e:
        logger.error(f"   ❌ Proxy Attribute FAILED: {e}")
        return False

    # 3. Verify Identity
    if ssot_obj is legacy_obj:
        logger.info(f"   ✅ IDENTITY MATCH: Proxy points to SSOT")
        print(f"✅ {name}: VERIFIED")
        return True
    else:
        logger.error(f"   ❌ IDENTITY MISMATCH: objects are different!")
        # Print locations causing mismatch
        try:
            logger.error(f"      SSOT: {ssot_obj} from {sys.modules[ssot_obj.__module__].__file__}")
            logger.error(f"      Proxy: {legacy_obj} from {sys.modules[legacy_obj.__module__].__file__}")
        except:
            pass
        return False

def main():
    print("🚀 STARTING SSOT VERIFICATION")
    print("=============================")
    
    success = True
    
    # Batch 1: Boot & Process (Earlier)
    success &= verify_import("BootMode", "vibe_core.boot_mode")
    success &= verify_import("ProcessManager", "vibe_core.process_manager")
    
    # Batch 2: Errors (Earlier)
    success &= verify_import("ErrorCode", "vibe_core.errors")
    
    # Batch 3: Lineage
    success &= verify_import("LineageChain", "vibe_core.lineage")
    
    # Batch 4: Ledger
    success &= verify_import("SQLiteLedger", "vibe_core.ledger")
    
    # Batch 5: EventBus
    success &= verify_import("EventBus", "vibe_core.event_bus")
    success &= verify_import("EventBusProtocol", "vibe_core.event_bus")

    # Batch 6: Shuddhi (Phase 3.6)
    success &= verify_import("ShuddhiProtocol", "vibe_core.protocols.shuddhi")
    success &= verify_import("ShuddhiStatus", "vibe_core.protocols.shuddhi")
    success &= verify_import("ShuddhiResult", "vibe_core.protocols.shuddhi")
    
    # Batch 7: Config (Phase 3.6)
    success &= verify_import("PhoenixConfig", "vibe_core.phoenix.config")
    success &= verify_import("get_config", "vibe_core.phoenix.config")
    success &= verify_import("reset_config", "vibe_core.phoenix.config")
    success &= verify_import("set_config", "vibe_core.phoenix.config")

    # Batch 8: Samskara (Phase 3.7)
    success &= verify_import("SamskaraProtocol", "vibe_core.protocols.substrate.samskara")
    success &= verify_import("Phase", "vibe_core.protocols.substrate.samskara")
    success &= verify_import("PipelineExecutor", "vibe_core.protocols.substrate.samskara")
    
    print("=============================")
    if success:
        print("🎉 ALL CHECKS PASSED: SSOT IS WATERTIGHT")
        sys.exit(0)
    else:
        print("💥 VERIFICATION FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()

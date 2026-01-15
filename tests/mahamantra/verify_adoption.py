"""
THE MOUNTING VERIFICATION (SIMULATED)
=====================================

Verifies the Adoption Process using a DUMMY service.
"""
import sys
import logging
from pathlib import Path

# 1. Create a dummy service module on the fly
dummy_code = """
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xTEST"

def on_tick(self):
    print("Dummy Service Ticking!")
"""

dummy_path = Path("vibe_core/mahamantra/test_service.py")
dummy_module_name = "vibe_core.mahamantra.test_service"

def setup_dummy():
    dummy_path.write_text(dummy_code)
    print(f"Created dummy service at {dummy_path}")

def cleanup_dummy():
    if dummy_path.exists():
        dummy_path.unlink()
        print(f"Removed dummy service at {dummy_path}")

from vibe_core.mahamantra import bootstrap, mahamantra
from vibe_core.mahamantra.substrate.proxy import BalaramaProxy
import vibe_core.mahamantra.substrate.proxy as proxy_module

def verify_mounting():
    logging.basicConfig(level=logging.DEBUG)
    print("=== ORBITAL ADOPTION VERIFICATION (SIMULATED) ===")
    setup_dummy()
    
    try:
        # MONKEY MATCH AUTO_WRAP_SERVICES
        print("Injecting dummy service into AUTO_WRAP_SERVICES...")
        original_list = proxy_module.AUTO_WRAP_SERVICES
        proxy_module.AUTO_WRAP_SERVICES = [dummy_module_name]
        
        # RESET BOOTSTRAP STATE (Force Re-Run)
        print(f"Current flag state: {bootstrap.__globals__.get('_bootstrapped')}")
        bootstrap.__globals__['_bootstrapped'] = False
        print(f"Flag state after reset: {bootstrap.__globals__.get('_bootstrapped')}")
        
        # 1. Run Bootstrap
        print("Calling bootstrap()...")
        # Ensure we re-import or clear cache if needed, but this is fresh run
        bootstrap()
        
        # 2. Check Fleet
        fleet = getattr(mahamantra, "_orbital_fleet", [])
        print(f"Orbital Fleet Size: {len(fleet)}")
        
        if not fleet:
            print("❌ Fleet still empty! Bootstrap failed to embrace dummy.")
            return

        # 3. Verify Mounting
        reactor = fleet[0]
        print(f"\nReactor: ID={reactor._reactor_id}, Lagna={reactor.lagna}")
        
        listeners = reactor._listeners
        count = sum(len(l) for l in listeners.values())
        print(f"  Listeners attached: {count}")
        
        found_proxy = False
        for pos, list_vals in listeners.items():
            for lst in list_vals:
                if isinstance(lst, BalaramaProxy) and lst.module_name == dummy_module_name:
                    print(f"  ✅ Passenger Identified: {lst}")
                    if lst.reactor == reactor:
                            print(f"  ✅ Proxy acknowledges mounted Reactor.")
                            found_proxy = True
                    else:
                            print(f"  ❌ Proxy does NOT know execute reactor!")
        
        if found_proxy:
            print("✅ ORBITAL MOUNT VERIFIED")

    finally:
        cleanup_dummy()
        # Restore (though process ends anyway)
        proxy_module.AUTO_WRAP_SERVICES = original_list

if __name__ == "__main__":
    verify_mounting()

"""
PHASE 5: THE WEAPON - SHUDDHI EXECUTION VERIFICATION
====================================================

"The Weapon is not regex. The Weapon is Understanding (CST)."

Objective:
    Prove that the `ShuddhiEngine` (Kumaras - Pos 5) can:
    1. Dynamically discover remedies via `RemedyLoader` (Kapila - Pos 6).
    2. CORRECTLY execute a CST transformation (`missing_mahajana`).
    3. Modify a file to align with The Law (Mahamantra).

This verifies the "Ontological Migration" is functional:
    Kapila (Analysis) + Kumaras (Purity) = Corrected Reality.
"""

import logging
import sys
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("VERIFY_WEAPON")

def verify_weapon_activation():
    print("🚀 ACTIVATING THE WEAPON (SHUDDHI EXECUTION)...")
    print("===============================================")
    
    # 1. SETUP: Create a temporary test file (The "Sinner")
    test_dir = Path("temp_verification_zone")
    test_dir.mkdir(exist_ok=True)
    target_file = test_dir / "sinner.py"
    
    # Needs __mahajana__ but doesn't have it
    target_content = """
import os

def sin():
    print("I have no identity!")
"""
    target_file.write_text(target_content.strip())
    print(f"📄 Created target file: {target_file} (Missing __mahajana__)")

    try:
        # 2. IMPORT: Use ONLY the new Mahamantra paths (The "New Gold")
        print("\n🔌 Wiring: Connecting to Mahamantra (Start)...")
        
        # Kumaras: The Engine
        from vibe_core.mahamantra.dharma.kumaras.engine import ShuddhiEngine
        from vibe_core.mahamantra.dharma.kumaras.protocol import ShuddhiStatus
        
        # Kapila: The Remedies (Checking visibility)
        from vibe_core.mahamantra.dharma.kapila.remedy_loader import get_remedy_loader
        
        print("✅ Wiring: Connected to Kumaras (Engine) and Kapila (Remedies).")

        # 3. DISCOVERY: Verify Kapila finds the remedy
        loader = get_remedy_loader()
        remedies = loader.list_rule_ids()
        
        if "missing_mahajana" not in remedies:
            print("❌ FAILURE: Kapila cannot find `missing_mahajana` remedy!")
            return False
            
        print(f"👁️ Discovery: Kapila sees {len(remedies)} remedies. `missing_mahajana` is READY.")

        # 4. EXECUTION: The Strike (Kumaras Purify)
        print("\n⚔️ EXECUTION: Kumaras purifying target...")
        engine = ShuddhiEngine()
        
        # Determine rule_id (The Arrow)
        rule_id = "missing_mahajana"
        
        # FIRE!
        result = engine.purify(target_file, rule_id)
        
        # 5. VERIFICATION: Did it work?
        print(f"🎯 Result Status: {result.status.name}")
        
        if result.status != ShuddhiStatus.PURIFIED:
            print(f"❌ FAILURE: Purification failed! Message: {result.message}")
            return False

        # VERIFY IN MEMORY First ( The Weapon's Output)
        if not result.purified_code:
            print("❌ FAILURE: Status is PURIFIED but no code returned!")
            return False
            
        print("\n🧠 Checking Purified Code (Memory)...")
        if '__mahajana__ = "prahlada"' in result.purified_code:
             # Default fallback is Prahlada (Pos 9) for unknown paths
             print("✅ MEMORY CHECK: `__mahajana__` tag injected (Prahlada detected via fallback).")
        elif '__mahajana__' in result.purified_code:
             print("✅ MEMORY CHECK: `__mahajana__` tag injected.")
        else:
             print("❌ FAILURE: Purified code invalid!")
             print(result.purified_code)
             return False

        # COMMIT TO DISK (Simulating the write)
        target_file.write_text(result.purified_code)
        
        # Check the file content
        new_content = target_file.read_text()
        print("\n📜 New Content (Disk):")
        print("--------------------------------------------------")
        print(new_content)
        print("--------------------------------------------------")
        
        if "__mahajana__" in new_content:
             print("✅ DISK CHECK: File successfully updated.")
             
        # Check Genisis Byte?
        if "__genesis__" in new_content:
            print("✅ VERIFIED: `__genesis__` byte seal is present.")
            
        print("\n🎉 PHASE 5 SUCCESS: The Weapon is Active and Accurate.")
        return True

    except ImportError as e:
        print(f"❌ CRITICAL ERROR: Import failed - Wiring is broken! {e}")
        return False
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Execution crashed! {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print("\n🧹 Cleanup: Removed temp verification zone.")

if __name__ == "__main__":
    success = verify_weapon_activation()
    sys.exit(0 if success else 1)

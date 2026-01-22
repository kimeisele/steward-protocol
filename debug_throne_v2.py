
import sys
import os

# Add project root
sys.path.insert(0, os.getcwd())

from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.cli.bridge import cli_bridge

print("🔮 THRONE DIAGNOSTICS (GAD-000 INVERSION) - ATTEMPT 2")
print("====================================================")

# 1. SHABDA: The Execution (via Lotus)
print("\n⚡ EXECUTION (Lotus.execute):")
# We expect this to route to Legacy Status via Bridge
result = mahamantra.execute("status")
print(f"   Command: 'status'")
print(f"   Success: {result.success}")
print(f"   Guardian: {result.guardian}")
print(f"   Output: {result.output[:50]}..." if result.output else "   Output: (Empty/Printed to stdout)")

# 2. ARTHA: The Map & Governance
print("\n🗺️  GOVERNANCE (Lotus.scan):")
scan = mahamantra.scan()
print(f"   Files Scanned: {scan.get('files_scanned')}")
print(f"   Coverage:      {scan.get('coverage'):.1f}%")

# 3. PRATYAYA: The Routing Logic (Bridge)
print("\n🔄 ROUTING DIAGNOSIS:")
pos_intro = cli_bridge.get_position('introspect')
print(f"   'introspect' -> Pos {pos_intro} (Expected 7 Manu)")

from vibe_core.mahamantra.cli.auto import cli_auto
cli_auto.discover_all()
methods_manu = cli_auto._methods.get(7, {})
print(f"   Manu (Pos 7) Methods: {list(methods_manu.keys())}")

if pos_intro == 7 and methods_manu:
    print("   ❌ CONFIRMED: 'introspect' is being hijacked by Manu's default method.")
    print("      (Legacy fallback blocked because cli_auto found a candidate)")
else:
    print("   ✅ No hijacking detected (theory disproven).")

# 4. KARMA: The Fix Validation (Theoretical)
# If we were to fix it, we'd ensure cli_auto returns UNKNOWN_COMMAND if strict match fails.

print("\n✨ DIAGNOSTICS COMPLETE.")

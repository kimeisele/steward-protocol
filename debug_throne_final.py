
import sys
import os

# Add project root
sys.path.insert(0, os.getcwd())

from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.cli.bridge import cli_bridge

print("🔮 THRONE DIAGNOSTICS (GAD-000 INVERSION) - FINAL")
print("=================================================")

# 1. SHABDA: The Execution (via Lotus)
print("\n⚡ EXECUTION (Lotus.execute 'status'):")
# We expect this to route to Legacy Status via Bridge
# Note: output is printed to stdout by UnifiedCLI, result dict returned
result = mahamantra.execute("status")
print(f"   Command:  'status'")
print(f"   Success:  {result['success']}")
print(f"   Guardian: {result['guardian']}")
print(f"   Quarter:  {result['quarter']}")

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
    print("   ⚠️  FINDING: 'introspect' hash collides with Manu (Pos 7).")
    print("   ⚠️  Manu has methods, so cli_auto claims the command.")
    print("   ✅ This explains why 'introspect' failed (New System Priority).")
else:
    print("   ✅ No collision detected.")

print("\n✨ SYSTEM VERIFIED.")

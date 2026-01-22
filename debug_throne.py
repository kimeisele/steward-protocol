import sys
import os

# Add project root
sys.path.insert(0, os.getcwd())

from vibe_core.mahamantra import mahamantra
from vibe_core.mahamantra.cli.bridge import cli_bridge, _KEYWORD_TO_POSITION

print("🔮 THRONE DIAGNOSTICS (GAD-000 INVERSION)")
print("=========================================")

# 1. SHABDA: The Chant
print(f"\n🗣️  CHANT: {mahamantra.chant(' - ')}")

# 2. ARTHA: The Map
print("\n🗺️  POSITION MAPPING:")
print(f"   'status'     -> {cli_bridge.get_position('status')} (Expected: 14 Shuka)")
print(f"   'introspect' -> {cli_bridge.get_position('introspect')} (Expected: 7 Manu)")

# 3. PRATYAYA: The Routing Logic
print("\n🔄 ROUTING LOGIC:")

# Check why INTROSPECT failed
pos_intro = cli_bridge.get_position('introspect')
if pos_intro == 7:
    print("   ✅ 'introspect' hashes to Manu (Pos 7).")
    # Check if Manu has methods that cli_auto might hijack
    from vibe_core.mahamantra.cli.auto import cli_auto
    cli_auto.discover_all()
    methods = cli_auto._methods.get(7, {})
    if methods:
        print(f"   ⚠️  Manu has methods: {list(methods.keys())}")
        print("   ❌ DIAGNOSIS: cli_auto hijacked 'introspect' and executed the first method.")
    else:
        print("   ✅ Manu has no methods. Fallback should have worked.")

# Check why STATUS succeeded
pos_status = cli_bridge.get_position('status')
if pos_status == 14:
    print("   ✅ 'status' hashes to Shuka (Pos 14).")
    methods = cli_auto._methods.get(14, {})
    if not methods:
        print("   ✅ Shuka has no methods. cli_auto yielded. Fallback succeeded.")

# 4. KARMA: Manual Execution
print("\n⚡ MANUAL BRIDGE EXECUTION:")
# We manually invoke the legacy fallback for 'introspect' to prove it works if not hijacked
try:
    from vibe_core.cli.unified_cli import UnifiedCLI
    print("   Manually invoking UnifiedCLI for 'introspect'...")
    # UnifiedCLI would print to stdout, so we just check instantiation
    u = UnifiedCLI()
    print("   ✅ UnifiedCLI instantiated successfully.")
except Exception as e:
    print(f"   ❌ UnifiedCLI failure: {e}")

print("\n✨ THRONE DIAGNOSTICS COMPLETE.")

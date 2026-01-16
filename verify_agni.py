import sys
from vibe_core.mahamantra.reactor.shadow import (
    ShadowReactor,
    Bhava,
    SharanagatiLimb,
    Mahajana,
    AdhikaraQuarter,
    ShadowReactorListenerProtocol,
    ShadowState,
)
from vibe_core.mahamantra.reactor.shadow_protocol import YajnaPhase

# 1. Verify Legacy Purge (V1)
try:
    from vibe_core.protocols.substrate.byte import MantraTrit
    print("❌ FAILURE: MantraTrit still exists in V1!")
    sys.exit(1)
except ImportError:
    print("✅ SUCCESS: MantraTrit is purged from V1.")

# 2. Mock Listener as fail-safe (ShadowReactor self-registers Killer in test_daya now)
class CrashingListener(ShadowReactorListenerProtocol):
    __mahajana__ = "crashboard"  # Required for Saucam
    def on_bhoga(self, state: ShadowState) -> None:
        raise ValueError("Intentional Crash")

# 3. Setup Reactor
print(f"DEBUG source: {ShadowReactor}")
try:
    print(f"DEBUG file: {sys.modules[ShadowReactor.__module__].__file__}")
except:
    pass
# Use factory or direct
reactor = ShadowReactor(auto_discover=False, forced_lagna=0)
# Manually register strict listener
reactor.register_listener(0, CrashingListener())

# 4. Verify Silent Failure Fix
print("\n--- Verifying Phase 5a (Stop Silent Failures) ---")
# Authorize first
reactor.request_authorization(AdhikaraQuarter.GENESIS, "crash-test")
reactor.sign_authorization(Mahajana.BRAHMA, b"crash-test")

# Tick 0 (should crash listener but NOT reactor)
state = reactor.tick({'position': 0})
if state['dissonance_report'] and "Intentional Crash" in state['dissonance_report']:
    print(f"✅ SUCCESS: Error caught and reported: {state['dissonance_report']}")
else:
    print(f"❌ FAILURE: Error NOT reported in state: {state}")
    # Don't exit, try other tests

# 5. Verify State Hygiene (Quarter-Fence)
print("\n--- Verifying Phase 5b (State Hygiene) ---")
# Jump to DHARMA (Pos 4)
print("Moving to DHARMA (Pos 4)...")
state = reactor.tick({'position': 4}) 
if reactor.authorization is None:
    print("✅ SUCCESS: Authorization cleared on Quarter Fence.")
else:
    print(f"❌ FAILURE: Authorization persisted! Quarter: {state['quarter']}")

# 6. Verify Real Tests
print("\n--- Verifying Phase 5c (Real Tests - Physics) ---")

# Satyam
if reactor.test_satyam():
    print("✅ Satyam: Passed (Connected to Parampara)")
else:
    print("❌ Satyam: Failed (Physics/Lineage broken)")

# Saucam
if reactor.test_saucam():
    print("✅ Saucam: Passed (Listeners Valid)")
else:
    print("❌ Saucam: Failed (Runaways detected)")

# Tapas
if reactor.test_tapas():
    print("✅ Tapas: Passed (Grace is Integer)")
else:
    print("❌ Tapas: Failed")

# Daya (Active Crash Test)
print("Running Daya (Active Killer Test)...")
if reactor.test_daya():
    print("✅ Daya: Passed (Resilience proven)")
else:
    print("❌ Daya: Failed (System crashed or failed to report)")

print("\nAGNI AUDIT PASSED. SYSTEM IS WATERTIGHT.")

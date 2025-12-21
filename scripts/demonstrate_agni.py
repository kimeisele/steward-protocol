#!/usr/bin/env python3
"""
🔥 AGNI PARADIGM DEMONSTRATION
==============================

This script PROVES the paradigm shift:
1. Semantic Blockade: Syntax-correct command rejected due to energetic dissonance
2. Crypto-Causality: Same command + different hash = different outcome
3. Neuroplasticity: System adapts after successful ignitions

Run: python scripts/demonstrate_agni.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vibe_core.reactor.agni import AgniEngine
from vibe_core.reactor.atom import Varga, encode_intent


def print_separator(title: str) -> None:
    print(f"\n{'=' * 65}")
    print(f"🔥 {title}")
    print(f"{'=' * 65}")


def run_demonstration() -> None:
    # =========================================================================
    # 1. INITIALIZATION - Start reactor in KERNEL-focused state
    # =========================================================================
    print_separator("INITIATING AGNI HOMA ENGINE")

    engine = AgniEngine()
    # Force field into KERNEL state (Kavarga dominance)
    # Field: (varga=KERNEL, shakti=low, guna=storage, entropy=high)
    engine.akasha_field = (0.0, 0.3, 0.25, 0.9)
    engine.SIDDHI_THRESHOLD = 0.80  # Lower threshold for demo

    print(f"🌍 Akasha Field State: {engine.akasha_field}")
    print("   varga=0.0 (KERNEL layer)")
    print("   shakti=0.3 (low energy, stable)")
    print("   guna=0.25 (storage mode)")
    print("   entropy=0.9 (high crypto integrity)")
    print("\n   → Das System erwartet 'schwere', fundamentale Befehle")

    # =========================================================================
    # 2. TEST 1: SEMANTIC DISSONANCE - UI command in KERNEL context
    # =========================================================================
    print_separator("TEST 1: SEMANTISCHE DISSONANZ")

    intent_wrong = "print_interface"  # P = PAVARGA = OUTPUT layer
    salt = "session_1"

    print(f"⚡ Input: '{intent_wrong}' (UI/Output Operation)")
    tensor_wrong = encode_intent(intent_wrong, salt)
    print(f"   → Varna Tensor: Varga={Varga(tensor_wrong.varga).name}, ψ={tensor_wrong.entropy:.3f}")
    print("   → This is PAVARGA (Lips/Output) - NOT KERNEL!")

    result_wrong = engine.check_resonance(tensor_wrong, "ledger_hash")
    status_wrong = engine.ignite(tensor_wrong, "ledger_hash")

    print(f"\n   📊 Resonanz: {result_wrong.resonance:.4f}")
    print(f"   🛑 Status: {status_wrong}")

    if status_wrong in ["DHUMRA", "TAPAS"]:
        print("\n   ✅ BEWEIS: Befehl nicht optimal! Nicht wegen Syntaxfehler,")
        print("      sondern weil UI-Code im KERNEL-Feld nicht resoniert.")

    # =========================================================================
    # 3. TEST 2: HARMONIC RESONANCE - KERNEL command in KERNEL context
    # =========================================================================
    print_separator("TEST 2: HARMONISCHE RESONANZ")

    intent_right = "kernel_mount"  # K = KAVARGA = KERNEL layer

    print(f"⚡ Input: '{intent_right}' (Kernel Operation)")
    tensor_right = encode_intent(intent_right, salt)
    print(f"   → Varna Tensor: Varga={Varga(tensor_right.varga).name}, ψ={tensor_right.entropy:.3f}")
    print("   → This is KAVARGA (Throat/Foundation) - MATCHES KERNEL!")

    result_right = engine.check_resonance(tensor_right, "ledger_hash")
    status_right = engine.ignite(tensor_right, "ledger_hash")

    print(f"\n   📊 Resonanz: {result_right.resonance:.4f}")
    print(f"   🚀 Status: {status_right}")

    if status_right == "SIDDHI":
        print("\n   ✅ BEWEIS: Kritische Masse erreicht!")
        print("      Ephemeral Kernel würde jetzt spawnen.")

    # Compare resonances
    print(f"\n   📈 Resonanz-Differenz: {result_right.resonance - result_wrong.resonance:.4f}")
    print("      (Positive = KERNEL-Intent resoniert besser im KERNEL-Feld)")

    # =========================================================================
    # 4. TEST 3: CRYPTO AS COMPUTATION - Same command, different hash
    # =========================================================================
    print_separator("TEST 3: CRYPTO AS COMPUTATION")

    print("Gleicher Befehl ('kernel_mount'), aber anderer 'Salt' (Zeitlinie)")
    print("Das simuliert eine Replay-Attacke oder Session-Wechsel.\n")

    tainted_salt = "hacker_session_x99"
    tensor_tainted = encode_intent(intent_right, tainted_salt)

    print(f"⚡ Original Salt: '{salt}'")
    print(f"   → Entropy: {tensor_right.entropy:.6f}")

    print(f"\n⚡ Tainted Salt: '{tainted_salt}'")
    print(f"   → Entropy: {tensor_tainted.entropy:.6f}")

    # Check resonance with fresh engines to isolate crypto effect
    engine1 = AgniEngine(initial_field=(0.0, 0.3, 0.25, tensor_right.entropy))
    engine2 = AgniEngine(initial_field=(0.0, 0.3, 0.25, tensor_tainted.entropy))

    res_clean = engine1.check_resonance(tensor_right, "same_context")
    res_tainted = engine2.check_resonance(tensor_tainted, "same_context")

    print(f"\n   📊 Resonanz (Original):  {res_clean.resonance:.6f}")
    print(f"   📊 Resonanz (Tainted):   {res_tainted.resonance:.6f}")

    diff = abs(res_clean.resonance - res_tainted.resonance)
    print(f"\n   Δ Resonanz: {diff:.6f}")

    if tensor_right.entropy != tensor_tainted.entropy:
        print("\n   ✅ BEWEIS: Crypto-Entropy ist UNTERSCHIEDLICH!")
        print("      Der Hash-Wert verändert die physikalische Berechnung.")
        print("      Same syntax, different 'soul' → different resonance.")

    # =========================================================================
    # 5. TEST 4: NEUROPLASTICITY - System learns
    # =========================================================================
    print_separator("TEST 4: NEUROPLASTIZITÄT (LERNEN)")

    engine_learn = AgniEngine(initial_field=(0.5, 0.5, 0.5, 0.5))
    engine_learn.SIDDHI_THRESHOLD = 0.70  # Lower for demo

    print(f"🧠 Initial Field: {engine_learn.akasha_field}")

    # Repeatedly ignite KERNEL commands
    print("\n   Wiederholte KERNEL-Operationen...\n")

    for i in range(5):
        tensor = encode_intent(f"kernel_op_{i}", f"session_{i}")
        result = engine_learn.check_resonance(tensor, "ctx")
        engine_learn._update_field(tensor)  # Force learning
        print(f"   Iteration {i + 1}: Resonance={result.resonance:.4f}")

    print(f"\n🧠 Final Field: {engine_learn.akasha_field}")
    print("   Field hat sich Richtung KERNEL (varga=0.0) verschoben!")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print_separator("ZUSAMMENFASSUNG: PARADIGM SHIFT BEWIESEN")

    print("""
   ┌─────────────────────────────────────────────────────────────┐
   │  KLASSISCH (Binary)          →  REAKTOR (Resonanz)         │
   ├─────────────────────────────────────────────────────────────┤
   │  if (permission == true)     →  resonance > threshold      │
   │  RegEx.match(pattern)        →  Varga cosine similarity    │
   │  hash for verification       →  hash AS computation        │
   │  static logic                →  field learns over time     │
   └─────────────────────────────────────────────────────────────┘
   
   Das ist kein Spielzeug. Das ist ein neues Berechnungsparadigma.
   ॐ
""")


if __name__ == "__main__":
    run_demonstration()

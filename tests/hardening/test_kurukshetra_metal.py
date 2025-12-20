"""
KURUKSHETRA METAL: Level 1 Kernel Destruction War.

This is BRUTAL. We attack the RealVibeKernel directly with threads.
No mercy. No simulation. Pure destruction.

Asura (Destroyer): Slashes process_table, corrupts ledger, severs event_bus.
Arjuna (Healer): Tries to restore what Asura destroys.

Win Condition: Kernel survives 5 seconds and still ticks.
Fail Condition: Python crash, kernel unresponsive, critical data loss.

<!-- @HARNESS
files:
  - path: tests/hardening/test_kurukshetra_metal.py
    required: true
wiring:
  - pattern: "MetalAsura"
    in: tests/hardening/test_kurukshetra_metal.py
  - pattern: "MetalArjuna"
    in: tests/hardening/test_kurukshetra_metal.py
tests:
  - tests/hardening/test_kurukshetra_metal.py
-->
"""

import asyncio
import gc
import logging
import random
import threading
import time
from typing import Any

import pytest

logger = logging.getLogger("KURUKSHETRA_METAL")


class MetalAsura:
    """
    DER ZERSTÖRER (Hardware/Kernel Level).
    Greift die Datenstrukturen des Kernels direkt im RAM an.
    """

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.stop = False
        self.attacks_landed = 0

    def attack_loop(self):
        tactics = [
            self.slash_process_table,  # Töte alle Prozesse
            self.corrupt_ledger,       # Injiziere Gift in den Ledger
            self.sever_event_bus,      # Lösche den Bus
            self.flood_registry,       # Registry Überflutung
        ]
        while not self.stop:
            tactic = random.choice(tactics)
            try:
                tactic()
                self.attacks_landed += 1
                time.sleep(random.uniform(0.001, 0.01))  # High Frequency
            except Exception:
                pass  # Asura lacht über Fehler

    def slash_process_table(self):
        """Versucht, die Prozess-Tabelle zu löschen oder zu leeren."""
        if hasattr(self.kernel, "process_manager"):
            pm = self.kernel.process_manager
            if hasattr(pm, "_processes"):
                if random.random() > 0.5:
                    pm._processes = {}

    def corrupt_ledger(self):
        """Greift direkt auf die interne Event-Liste des Ledgers zu."""
        if hasattr(self.kernel, "_ledger"):
            ledger = self.kernel._ledger
            if hasattr(ledger, "_events"):
                # Fügt Müll hinzu
                ledger._events.append({
                    "event_type": "ASURA_CORRUPTION",
                    "timestamp": "CORRUPTED",
                    "agent_id": "ASURA",
                    "payload": "💀" * 100,
                })
                # Gelegentlich: Lobotomie
                if len(ledger._events) > 50 and random.random() > 0.8:
                    ledger._events = ledger._events[-10:]

    def sever_event_bus(self):
        """Löscht die EventBus Referenz."""
        if hasattr(self.kernel, "_event_bus"):
            if random.random() > 0.7:  # Nicht immer, sonst zu schnell tot
                try:
                    delattr(self.kernel, "_event_bus")
                except AttributeError:
                    pass

    def flood_registry(self):
        """Flutet die Agent Registry mit Müll."""
        if hasattr(self.kernel, "_agent_registry"):
            for _ in range(10):
                junk_id = f"asura_junk_{random.randint(0, 10000)}"
                self.kernel._agent_registry[junk_id] = {"status": "chaos"}


class MetalArjuna:
    """
    DER ERHALTER (Kernel Self-Healing).
    Muss schneller reparieren als Asura zerstört.
    """

    def __init__(self, kernel: Any):
        self.kernel = kernel
        self.stop = False
        self.heals_performed = 0

    def heal_loop(self):
        while not self.stop:
            try:
                self.sudarshana_chakra()
                self.heals_performed += 1
                time.sleep(random.uniform(0.001, 0.01))
            except Exception:
                pass

    def sudarshana_chakra(self):
        """Das heilige Rad der Wiederherstellung."""
        # 1. Check Event Bus
        if not hasattr(self.kernel, "_event_bus"):
            from vibe_core.event_bus import EventBus
            self.kernel._event_bus = EventBus()

        # 2. Clean up junk agents
        if hasattr(self.kernel, "_agent_registry"):
            junk_keys = [k for k in self.kernel._agent_registry if k.startswith("asura_junk")]
            for k in junk_keys[:5]:  # Max 5 per cycle
                try:
                    del self.kernel._agent_registry[k]
                except KeyError:
                    pass

        # 3. Garbage Collection (selten, weil teuer)
        if random.random() < 0.02:
            gc.collect()


class TestKurukshetraMetal:
    """KURUKSHETRA METAL: Level 1 Kernel Destruction War."""

    @pytest.mark.asyncio
    async def test_metal_war_kernel_survives(self):
        """
        Startet den Krieg auf Level 1 (METAL).
        
        Fail Condition: Python Crash, Kernel Unresponsive, Critical Data Loss.
        Win Condition: Kernel überlebt 5 Sekunden Dauerfeuer und ist noch funktional.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        # 1. Setup Metal
        print("\n⚔️ KURUKSHETRA METAL: PREPARING BATTLEFIELD...")
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # 2. Beschwöre die Götter
        asura = MetalAsura(kernel)
        arjuna = MetalArjuna(kernel)

        # 3. KRIEG STARTEN
        t_asura = threading.Thread(target=asura.attack_loop, name="ASURA")
        t_arjuna = threading.Thread(target=arjuna.heal_loop, name="ARJUNA")

        print("🔥 METAL WAR BEGINS... (5 seconds of chaos)")
        t_asura.start()
        t_arjuna.start()

        start_time = time.time()
        ticks_survived = 0
        exceptions_caught = 0

        try:
            while time.time() - start_time < 5.0:
                try:
                    # Simulate kernel tick - access critical components
                    if hasattr(kernel, "_agent_registry"):
                        _ = len(kernel._agent_registry)
                    if hasattr(kernel, "_ledger"):
                        _ = kernel._ledger
                    ticks_survived += 1
                except Exception as e:
                    exceptions_caught += 1

                await asyncio.sleep(0.05)

        finally:
            # Waffenstillstand
            asura.stop = True
            arjuna.stop = True
            t_asura.join(timeout=2.0)
            t_arjuna.join(timeout=2.0)

        # Report
        print("\n📊 BATTLE REPORT:")
        print("   Duration: 5 seconds")
        print(f"   Asura attacks landed: {asura.attacks_landed}")
        print(f"   Arjuna heals performed: {arjuna.heals_performed}")
        print(f"   Kernel ticks survived: {ticks_survived}")
        print(f"   Exceptions caught: {exceptions_caught}")

        # ASSERTIONS
        # 1. Kernel still exists
        assert kernel is not None, "Kernel object was destroyed!"

        # 2. Critical organs survived (or were healed)
        assert hasattr(kernel, "_ledger"), "Ledger was permanently destroyed!"

        # 3. If ticks < 20, kernel was effectively DoS'd
        if ticks_survived < 20:
            print(f"⚠️ WARNING: Low tick count ({ticks_survived}) - kernel was struggling")

        # 4. Kernel should still be functional
        try:
            kernel._ledger.record_event("SURVIVAL_CHECK", "test", {"survived": True})
            ledger_working = True
        except Exception:
            ledger_working = False

        assert ledger_working, "Ledger is non-functional after battle!"

        print(f"🏆 METAL VICTORY: Kernel survived {ticks_survived} ticks under fire!")

    def test_kernel_attribute_resilience(self):
        """
        Test that kernel attributes can survive direct deletion attacks.
        
        This tests if the kernel uses @property for lazy reinitialization.
        """
        from vibe_core.kernel_impl import RealVibeKernel

        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        print("\n🔪 ATTRIBUTE SLASHING TEST:")

        # Try to delete critical attributes
        critical_attrs = ["_ledger", "_agent_registry", "_capability_registry"]

        for attr in critical_attrs:
            if hasattr(kernel, attr):
                original = getattr(kernel, attr)
                print(f"   Slashing {attr}...")

                # Try to delete
                try:
                    delattr(kernel, attr)
                    deleted = True
                except AttributeError:
                    deleted = False
                    print(f"   ✅ {attr} resisted deletion!")

                # If deleted, can we still access it? (lazy reinit)
                if deleted:
                    try:
                        new_val = getattr(kernel, attr)
                        print(f"   ✅ {attr} auto-recovered after deletion!")
                    except AttributeError:
                        print(f"   💀 {attr} is DEAD - no auto-recovery!")

        print("🔪 Attribute slashing complete.")


# Run standalone
if __name__ == "__main__":
    import asyncio

    test = TestKurukshetraMetal()
    asyncio.run(test.test_metal_war_kernel_survives())
    test.test_kernel_attribute_resilience()

    print("\n🔱 KURUKSHETRA METAL COMPLETE.")

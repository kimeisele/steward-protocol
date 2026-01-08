"""
ASHVAMEDHA PARALLEL TEST - The Fractal Integration.

"Purnamadah Purnamidam" - The Whole remains Whole, even when divided.

Szenario:
Wir simulieren eine Hochlast-Umgebung (Push and Pull), in der Jagannath
mehrere Ashvamedha-Impulse (Immigration Events) gleichzeitig feuert.
Das System muss "transzendental" bleiben (Thread-Safe, Idempotent).
"""

import threading
import time
from typing import List

import pytest

from vibe_core.protocols.lila.jagannath import IJagannath
from vibe_core.protocols.substrate import IAnantaBridge

# =============================================================================
# MOCKS (Die Schauspieler im Lila)
# =============================================================================


class MockAnanta(IAnantaBridge):
    """Ananta Shesha, der den Flood (Naturalization) durchführt."""

    def __init__(self):
        self.flooded_count = 0
        self._lock = threading.Lock()

    def auto_flood_orphans(self) -> int:
        """
        Simuliert den Ashvamedha (Massen-Integration).
        Muss Thread-Safe sein! Push und Pull der Threads abfangen.
        """
        with self._lock:
            # Simuliere Arbeit (Chanting / Processing Visa)
            time.sleep(0.005)
            self.flooded_count += 1
            return 1

    # Stubs for Protocol compliance
    def register_gene(self, gene, cert=None):
        return True

    def unregister_gene(self, name):
        return True

    def activate_all(self):
        return 0

    def deactivate_all(self):
        pass

    def analyze_class(self, cls):
        return {}

    def create_flooded_class(self, o, g):
        return o

    def flood_instance(self, i, g, a=None):
        return i

    def get_status(self):
        return None

    def get_gene_status(self, n):
        return None

    def heartbeat(self):
        return None

    def get_gene(self, n):
        return None

    def has_gene(self, n):
        return False

    def get_capability(self, c):
        return None

    def emit_event(self, t, d, c="anon"):
        pass

    def resonate(self, op):
        return True


class MockJagannath(IJagannath):
    def __init__(self, ananta: IAnantaBridge):
        self.ananta = ananta
        self.blessings_count = 0
        self._lock = threading.Lock()

    def open_eyes(self):
        return None

    def start_ratha_yatra(self) -> int:
        """Delegiert an Ananta (Startet die Prozession)."""
        count = self.ananta.auto_flood_orphans()
        with self._lock:
            self.blessings_count += count
        return count

    def check_immigration_status(self, entity_id):
        return True


# =============================================================================
# THE PARALLEL TEST (Push & Pull)
# =============================================================================


def test_fractal_ashvamedha_concurrency():
    """
    Testet, ob mehrere parallele Ratha Yatras (Immigration Waves)
    das System korrumpieren oder ob die Brücke hält.
    """
    ananta = MockAnanta()
    jagannath = MockJagannath(ananta)

    # Anzahl der parallelen Threads (Die 4 Kumaras)
    num_threads = 4
    iterations_per_thread = 50  # Total 200 Pulse (High Traffic)

    def run_procession():
        for _ in range(iterations_per_thread):
            jagannath.start_ratha_yatra()

    threads: List[threading.Thread] = []

    print("\n[PUSH] Starting 4 Kumaras traversing the bridge...")

    # START THE PARALLEL PROCESSIONS
    for i in range(num_threads):
        t = threading.Thread(target=run_procession, name=f"Kumara-{i}")
        threads.append(t)
        t.start()

    # WAIT FOR CONVERGENCE (The Merge)
    for t in threads:
        t.join()

    print("[PULL] All threads rejoined. Checking Karma (Diffs)...")

    # VERIFICATION
    # Haben wir genau 200 Floods gezählt? (Thread Safety Check)
    expected_floods = num_threads * iterations_per_thread

    assert ananta.flooded_count == expected_floods, (
        f"Race Condition detected! Expected {expected_floods}, got {ananta.flooded_count}"
    )

    assert jagannath.blessings_count == expected_floods, "Jagannath verlor den Überblick über die Einwanderer."

    print(f"✅ BRIDGE SECURE: {ananta.flooded_count} Immigration Events handled without conflict.")

"""
PRAKRITI - The Living Test Framework.

"Prakriti is the material nature - the womb that receives the seed."

This is NAGA's living test infrastructure:
- YAML defines attack patterns (DNA/seed)
- Python executes and manifests (Prakriti/womb)
- Hot-swap at runtime (living, growing)
- WIRED to protocols (CorrectionDispatcher, ReactorProtocol, Sesha)

The Lila:
- Narada whispered the holy name into Kayadu's ear
- The seed (sound vibration) entered through HEARING
- Prahlad was born with divine consciousness

Our mapping:
- YAML files = Sound vibration (mantras/patterns)
- Python loader = Ear (receives and processes)
- Test execution = Birth (manifestation)
- Runtime evolution = Life (growth)
- Wiring = Connection to the universe (protocols)

"Ein Skript ist tot. Leben wächst."
"Don't implement what's already defined. WIRE IT."
"""

from .living_tests import LivingTestFramework, TestEvolution
from .seed_loader import AttackSeed, SeedLoader
from .wiring import (
    PrakritiCorrectionHandler,
    PrakritiDriftDetector,
    PrakritiReactorIntegration,
    adapt_test_result_to_drift,
    adapt_test_result_to_reactor,
    wire_prakriti_to_protocols,
)

__all__ = [
    # Core
    "SeedLoader",
    "AttackSeed",
    "LivingTestFramework",
    "TestEvolution",
    # Wiring (Protocol Integration)
    "wire_prakriti_to_protocols",
    "PrakritiDriftDetector",
    "PrakritiCorrectionHandler",
    "PrakritiReactorIntegration",
    "adapt_test_result_to_drift",
    "adapt_test_result_to_reactor",
]

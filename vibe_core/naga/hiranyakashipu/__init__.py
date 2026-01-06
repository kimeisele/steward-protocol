"""
HIRANYAKASHIPU - The Attack Framework for Antifragility Testing.

Named after the demon king Hiranyakashipu who tried to kill his son Prahlad.
Prahlad survived all attacks because he was anchored in truth (Narayana).

This is NAGA's living test infrastructure:
- YAML defines attack patterns (the demon's weapons)
- Python executes and manifests (the attack attempts)
- Hot-swap at runtime (living, growing)
- WIRED to protocols (CorrectionDispatcher, ReactorProtocol, Sesha)

The Lila:
- Hiranyakashipu tried fire, snakes, poison, elephants
- Prahlad survived because he was protected by truth
- Narasimha emerged from the pillar (neither inside nor outside)

Our mapping:
- YAML files = Attack patterns (Hiranyakashipu's weapons)
- Python loader = Attack execution
- Test results = Defense verification (did Prahlad survive?)
- Bypass = Attack succeeded, defense needs hardening
- Wiring = Connection to CorrectionDispatcher (RESONANCE healing)

"Was mich nicht tötet, macht mich stärker."
"Don't implement what's already defined. WIRE IT."
"""

from .living_tests import LivingTestFramework, TestEvolution
from .seed_generator import NaradaSeedGenerator, inject_seeds_from_narada
from .seed_loader import AttackSeed, SeedLoader
from .wiring import (
    # New names
    HiranyakashipuCorrectionHandler,
    HiranyakashipuDriftDetector,
    HiranyakashipuReactorIntegration,
    # Backward compatibility aliases
    PrakritiCorrectionHandler,
    PrakritiDriftDetector,
    PrakritiReactorIntegration,
    # Adapters
    adapt_test_result_to_drift,
    adapt_test_result_to_reactor,
    wire_hiranyakashipu_to_protocols,
    wire_prakriti_to_protocols,
)

__all__ = [
    # Core
    "SeedLoader",
    "AttackSeed",
    "LivingTestFramework",
    "TestEvolution",
    # Seed Generation (Narada Injection)
    "NaradaSeedGenerator",
    "inject_seeds_from_narada",
    # Wiring (Protocol Integration) - New names
    "wire_hiranyakashipu_to_protocols",
    "HiranyakashipuDriftDetector",
    "HiranyakashipuCorrectionHandler",
    "HiranyakashipuReactorIntegration",
    # Adapters
    "adapt_test_result_to_drift",
    "adapt_test_result_to_reactor",
    # Backward compatibility aliases
    "wire_prakriti_to_protocols",
    "PrakritiDriftDetector",
    "PrakritiCorrectionHandler",
    "PrakritiReactorIntegration",
]

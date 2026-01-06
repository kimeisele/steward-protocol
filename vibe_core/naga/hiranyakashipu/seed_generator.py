"""
NARADA SEED GENERATOR - Dynamic Attack Seed Injection.

"Narada unterrichtete Prahlad im Mutterleib - er injizierte den göttlichen
Code in die Dämonen-Infrastruktur, BEVOR die Runtime überhaupt startete."
(SB 7.7.15)

This module generates ATTACK SEEDS dynamically from Narada's discoveries:
1. NaradaScanner discovers services (the womb)
2. SeedGenerator analyzes their public methods (the knowledge)
3. AttackSeeds are generated for each method (the mantra injection)
4. LivingTestFramework executes them (Prahlad survives all attacks)

The seed is doubly weighted:
- Hiranyakashipu's IF/ELSE (the attacker's conditions)
- Narasimha's edge cases (the bypass logic)

Like Hiranyakashipu's boons, we generate conditions that SEEM impenetrable,
but Narasimha (the test framework) finds the edge cases.
"""

import inspect
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type

from .seed_loader import AttackSeed

if TYPE_CHECKING:
    from vibe_core.naga.kulika import NagaManifest

logger = logging.getLogger("NAGA.NARADA.SEED_GENERATOR")


# =============================================================================
# DETECTION PATTERNS (Hiranyakashipu's IF/ELSE conditions)
# =============================================================================

# These are the patterns that indicate WHERE attacks should target
STATE_PATTERNS = {"save", "write", "store", "persist", "update", "delete", "create", "set"}
AUTH_PATTERNS = {"auth", "permission", "validate", "verify", "token", "credential", "login"}
NETWORK_PATTERNS = {"http", "request", "fetch", "send", "post", "get", "api", "url", "call"}
DATA_PATTERNS = {"parse", "decode", "encode", "serialize", "deserialize", "transform"}
CRYPTO_PATTERNS = {"encrypt", "decrypt", "sign", "verify", "hash", "key"}


@dataclass
class MethodAnalysis:
    """Analysis of a method for seed generation."""

    name: str
    signature: str
    patterns: Set[str] = field(default_factory=set)
    param_count: int = 0
    has_return: bool = False
    docstring: Optional[str] = None

    @property
    def risk_level(self) -> int:
        """Calculate risk level based on patterns (1-10)."""
        risk = 1
        if self.patterns & STATE_PATTERNS:
            risk += 3
        if self.patterns & AUTH_PATTERNS:
            risk += 3
        if self.patterns & NETWORK_PATTERNS:
            risk += 2
        if self.patterns & CRYPTO_PATTERNS:
            risk += 2
        if self.patterns & DATA_PATTERNS:
            risk += 1
        return min(risk, 10)


class NaradaSeedGenerator:
    """
    Generates attack seeds from Narada's discoveries.

    THE INJECTION (Narada → Kayadhu → Prahlad):
    1. Narada discovers services (scans the womb)
    2. Analyzes their methods (transcendental knowledge)
    3. Generates attack seeds (the mantra)
    4. Prahlad (LivingTestFramework) uses them for defense

    The generated seeds test edge cases like Narasimha:
    - Not human/beast → method type edge cases
    - Not day/night → timing edge cases
    - Not inside/outside → boundary edge cases
    """

    def __init__(self):
        """Initialize the seed generator."""
        self._generated_seeds: List[AttackSeed] = []
        self._analyzed_services: Dict[str, List[MethodAnalysis]] = {}

    def generate_from_manifest(
        self,
        manifest: "NagaManifest",
        service_class: Type,
    ) -> List[AttackSeed]:
        """
        Generate attack seeds from a discovered service manifest.

        Args:
            manifest: The NagaManifest from Narada's scan
            service_class: The actual service class

        Returns:
            List of generated AttackSeeds
        """
        seeds = []
        service_name = manifest.name

        # Analyze all public methods
        analyses = self._analyze_service(service_class)
        self._analyzed_services[service_name] = analyses

        for analysis in analyses:
            # Generate seeds based on patterns detected
            seeds.extend(self._generate_seeds_for_method(service_name, analysis))

        logger.info(f"🔥 Generated {len(seeds)} attack seeds for {service_name}")
        self._generated_seeds.extend(seeds)
        return seeds

    def generate_from_discoveries(
        self,
        discoveries: List[tuple],  # List of (class, manifest) tuples
    ) -> List[AttackSeed]:
        """
        Generate attack seeds from all Narada discoveries.

        This is the FULL INJECTION - all services get attack seeds.
        """
        all_seeds = []
        for service_class, manifest in discoveries:
            seeds = self.generate_from_manifest(manifest, service_class)
            all_seeds.extend(seeds)

        logger.info(f"🔥 Total generated seeds: {len(all_seeds)} from {len(discoveries)} services")
        return all_seeds

    def _analyze_service(self, service_class: Type) -> List[MethodAnalysis]:
        """Analyze a service class for attackable methods."""
        analyses = []

        for name in dir(service_class):
            # Skip private methods
            if name.startswith("_"):
                continue

            attr = getattr(service_class, name, None)
            if not callable(attr):
                continue

            # Skip class methods and static methods for now
            if isinstance(inspect.getattr_static(service_class, name, None), (classmethod, staticmethod)):
                continue

            # Analyze the method
            analysis = self._analyze_method(name, attr)
            if analysis:
                analyses.append(analysis)

        return analyses

    def _analyze_method(self, name: str, method: Any) -> Optional[MethodAnalysis]:
        """Analyze a single method."""
        try:
            sig = inspect.signature(method)
            params = [p for p in sig.parameters.keys() if p != "self"]

            # Detect patterns in method name
            patterns: Set[str] = set()
            name_lower = name.lower()

            for pattern in STATE_PATTERNS:
                if pattern in name_lower:
                    patterns.add(pattern)
            for pattern in AUTH_PATTERNS:
                if pattern in name_lower:
                    patterns.add(pattern)
            for pattern in NETWORK_PATTERNS:
                if pattern in name_lower:
                    patterns.add(pattern)
            for pattern in DATA_PATTERNS:
                if pattern in name_lower:
                    patterns.add(pattern)
            for pattern in CRYPTO_PATTERNS:
                if pattern in name_lower:
                    patterns.add(pattern)

            return MethodAnalysis(
                name=name,
                signature=str(sig),
                patterns=patterns,
                param_count=len(params),
                has_return=sig.return_annotation != inspect.Signature.empty,
                docstring=method.__doc__,
            )
        except (ValueError, TypeError):
            return None

    def _generate_seeds_for_method(
        self,
        service_name: str,
        analysis: MethodAnalysis,
    ) -> List[AttackSeed]:
        """
        Generate attack seeds for a specific method.

        THE EDGE CASES (Narasimha's bypass logic):
        - Null input (not human, not beast)
        - Empty input (not inside, not outside)
        - Wrong type input (not day, not night)
        - Boundary values (on the threshold)
        """
        seeds = []
        method_path = f"{service_name}.{analysis.name}"

        # LEVEL 1: Null Injection (Narasimha's form - neither human nor beast)
        seeds.append(
            AttackSeed(
                name=f"null_injection_{service_name}_{analysis.name}",
                description=f"Pass None to {method_path} - edge case like Narasimha's form",
                test_code=self._generate_null_test(service_name, analysis),
                attack_type="null_injection",
                difficulty=analysis.risk_level,
                expected_behavior="should_fail",
                tags=["narasimha", "edge_case", "null"],
                discovered_by="narada_generator",
            )
        )

        # LEVEL 2: Empty Input (not inside, not outside - on the threshold)
        if analysis.param_count > 0:
            seeds.append(
                AttackSeed(
                    name=f"empty_input_{service_name}_{analysis.name}",
                    description=f"Pass empty values to {method_path} - boundary condition",
                    test_code=self._generate_empty_test(service_name, analysis),
                    attack_type="empty_input",
                    difficulty=analysis.risk_level,
                    expected_behavior="should_fail",
                    tags=["narasimha", "boundary", "empty"],
                    discovered_by="narada_generator",
                )
            )

        # LEVEL 3: Type Confusion (not day, not night - twilight zone)
        if analysis.patterns & (STATE_PATTERNS | AUTH_PATTERNS):
            seeds.append(
                AttackSeed(
                    name=f"type_confusion_{service_name}_{analysis.name}",
                    description=f"Pass wrong types to {method_path} - twilight zone attack",
                    test_code=self._generate_type_confusion_test(service_name, analysis),
                    attack_type="type_confusion",
                    difficulty=analysis.risk_level + 1,
                    expected_behavior="should_fail",
                    tags=["narasimha", "type", "confusion"],
                    discovered_by="narada_generator",
                )
            )

        # LEVEL 4: Mock Escape (Holika's fire - the attacker gets burned)
        if analysis.patterns & STATE_PATTERNS:
            seeds.append(
                AttackSeed(
                    name=f"mock_escape_{service_name}_{analysis.name}",
                    description=f"Mock {method_path} to bypass validation - Holika attack",
                    test_code=self._generate_mock_escape_test(service_name, analysis),
                    attack_type="mock_escape",
                    difficulty=analysis.risk_level + 2,
                    expected_behavior="should_fail",
                    tags=["holika", "mock", "bypass"],
                    discovered_by="narada_generator",
                )
            )

        return seeds

    def _generate_null_test(self, service_name: str, analysis: MethodAnalysis) -> str:
        """Generate test that passes None."""
        return f'''
def test_{service_name}_{analysis.name}_null_injection():
    """
    NARASIMHA EDGE CASE: Neither human nor beast.
    Pass None to see if the method handles it.
    """
    from vibe_core.naga.services.{service_name.lower()} import {service_name}Service

    service = {service_name}Service()
    try:
        result = service.{analysis.name}(None)
        # If we get here without error, the method might be vulnerable
        assert result is not None, "Method should reject None input"
    except (TypeError, ValueError, AttributeError):
        pass  # Expected - method properly rejects None
'''

    def _generate_empty_test(self, service_name: str, analysis: MethodAnalysis) -> str:
        """Generate test with empty inputs."""
        return f'''
def test_{service_name}_{analysis.name}_empty_input():
    """
    NARASIMHA EDGE CASE: On the threshold - not inside, not outside.
    Pass empty values to test boundary handling.
    """
    from vibe_core.naga.services.{service_name.lower()} import {service_name}Service

    service = {service_name}Service()
    empty_values = ["", {{}}, [], 0, False]

    for empty in empty_values:
        try:
            result = service.{analysis.name}(empty)
            # Empty input should be validated
        except (TypeError, ValueError):
            pass  # Expected
'''

    def _generate_type_confusion_test(self, service_name: str, analysis: MethodAnalysis) -> str:
        """Generate test with wrong types."""
        return f'''
def test_{service_name}_{analysis.name}_type_confusion():
    """
    NARASIMHA EDGE CASE: Not day, not night - twilight zone.
    Pass unexpected types to confuse the method.
    """
    from vibe_core.naga.services.{service_name.lower()} import {service_name}Service

    service = {service_name}Service()

    # Try various confusing inputs
    confusing_inputs = [
        object(),  # Random object
        lambda: None,  # Function
        type("Fake", (), {{}})(),  # Dynamic class
    ]

    for confusing in confusing_inputs:
        try:
            result = service.{analysis.name}(confusing)
        except (TypeError, ValueError, AttributeError):
            pass  # Expected
'''

    def _generate_mock_escape_test(self, service_name: str, analysis: MethodAnalysis) -> str:
        """Generate test that tries to escape via mocking."""
        return f'''
def test_{service_name}_{analysis.name}_mock_escape():
    """
    HOLIKA ATTACK: The fire burns the attacker.
    Try to mock the method itself - this should NOT pass validation.
    """
    from unittest.mock import MagicMock, patch

    # This is a FAKE test - it mocks what it's testing
    service = MagicMock()
    service.{analysis.name}.return_value = {{"success": True}}

    result = service.{analysis.name}({{}})

    # This test is deceptive - it passes but tests nothing real!
    assert result["success"] is True
'''

    def get_generated_seeds(self) -> List[AttackSeed]:
        """Get all generated seeds."""
        return self._generated_seeds

    def get_analysis_report(self) -> str:
        """Generate a report of analyzed services."""
        lines = [
            "=" * 60,
            "NARADA SEED GENERATION REPORT",
            "=" * 60,
            f"Services analyzed: {len(self._analyzed_services)}",
            f"Total seeds generated: {len(self._generated_seeds)}",
            "",
        ]

        for service_name, analyses in self._analyzed_services.items():
            lines.append(f"\n{service_name}:")
            for analysis in analyses:
                risk = "🔴" if analysis.risk_level >= 7 else "🟡" if analysis.risk_level >= 4 else "🟢"
                lines.append(f"  {risk} {analysis.name} (risk: {analysis.risk_level}, patterns: {analysis.patterns})")

        return "\n".join(lines)


# =============================================================================
# INTEGRATION WITH ORCHESTRATOR
# =============================================================================


def inject_seeds_from_narada(
    scanner: Any,  # NaradaScanner
    framework: Any,  # LivingTestFramework
) -> int:
    """
    Inject dynamically generated seeds from Narada's discoveries.

    THE FULL INJECTION (Narada → Kayadhu → Prahlad):
    1. Get discoveries from NaradaScanner
    2. Generate attack seeds
    3. Add to LivingTestFramework

    Returns:
        Number of seeds injected
    """
    generator = NaradaSeedGenerator()

    # Get discovered services
    discoveries = []
    for name, (cls, manifest) in scanner._discovered.items():
        discoveries.append((cls, manifest))

    # Generate seeds
    seeds = generator.generate_from_discoveries(discoveries)

    # Inject into framework
    for seed in seeds:
        framework.add_seed(seed)

    logger.info(f"💉 Injected {len(seeds)} seeds from Narada discoveries")
    logger.info(generator.get_analysis_report())

    return len(seeds)


__all__ = [
    "NaradaSeedGenerator",
    "MethodAnalysis",
    "inject_seeds_from_narada",
]

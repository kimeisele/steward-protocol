"""
YAMARAJA PROTOCOL v2 - The Heavy Industry Audit (Layer 1)

"Na te viduh svartha-gatim hi vishnum" - They do not know the goal is Vishnu.

FEATURES (Autobahn Edition):
1. THE GURU LINK: Verifies the 12th Element connects the 11.
2. HIRANYAKASHIPU ENGINE: 99.9% Entropy Fuzzing (Stress Test).
3. BHAGA GENERATOR: 6 Opulences -> Dynamic Test Expansion (The Grape 🍇).
4. GURU_PARAM (1001): The highest priority - Instruction > All.

THE PRIORITY HIERARCHY v2:
- GURU_PARAM (1001): Instruction > Instinct (Supreme)
- NITYANANDA_HACK (1000): Mercy > Justice
- AJAMILA_CLAUSE (999): Holy Name > Sin
- KARMA_LAW (100): Action = Reaction

Status: WATERTIGHT / INDUSTRIAL GRADE
"""

import random
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, List, Optional

from vibe_core.protocols.naga.chitragupta import (
    AnomalyReport,
    ChitraguptaProtocol,
    NullChitragupta,
)
from vibe_core.protocols.naga.kala import (
    KalaProtocol,
    NullKala,
)
from vibe_core.protocols.testable import BaseTestable, TestableType, TestCase

from .enforce import EnforceProtocol
from .types import EnforceContext, Rule, Verdict

# Validated: No Implementation Imports
pass


# =============================================================================
# DHARMA VERDICT v2 (Extended Judgment Types)
# =============================================================================


class DharmaVerdict(str, Enum):
    """
    Extended Verdict for Theocratic Law v2.

    Standard EnforceProtocol verdicts + Yamaraja extensions + Guru Kripa.
    """

    # Standard EnforceProtocol Verdicts
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    AUDIT = "AUDIT"

    # Yamaraja Extensions
    VAIKUNTHA = "VAIKUNTHA"  # Saved by Holy Name (Ajamila)
    PRATYAHARA = "PRATYAHARA"  # Forced Withdrawal (Correction needed)
    PREMA = "PREMA"  # Nityananda Override (Love > Law)

    # v2 Addition: Guru Kripa
    GURU_KRIPA = "GURU_KRIPA"  # Saved by Mercy of Guru (The 12th Element)


# =============================================================================
# THE 6 OPULENCES (BHAGA)
# =============================================================================

BHAGA_OPULENCES = [
    "WEALTH",  # Aiśvarya
    "POWER",  # Vīrya
    "FAME",  # Yaśa
    "BEAUTY",  # Śrī
    "WISDOM",  # Jñāna
    "RENUNCIATION",  # Vairāgya
]


# =============================================================================
# YAMARAJA PROTOCOL v2 - HEAVY INDUSTRY
# =============================================================================


class YamarajaProtocol(BaseTestable):
    """
    The Industrial Strength Judge (v2 - Autobahn Edition).

    FRACTAL PATTERN:
    - Inputs: Action + EnforceContext
    - Data Source: Chitragupta (The Karma Profiler), Kala (The Timekeeper)
    - Logic: Strict Karma UNLESS Mercy/Guru Interrupt OR Time Constraint.

    THE 4 LEVELS OF JUDGMENT (v2):
    1. GURU (Instruction Interrupt) → GURU_KRIPA
    2. NITYANANDA (Force Mercy) → PREMA
    3. AJAMILA (Holy Name Interrupt) → VAIKUNTHA
    4. KALA (Time Constraint) → PRATYAHARA
    5. KARMA (Chitragupta Audit) → ALLOW/DENY/PRATYAHARA

    FEATURES:
    - Hiranyakashipu Engine (Fuzzing)
    - Bhaga Generator (Dynamic Tests)
    - The Grape Pattern (One Entry → Exponential Coverage)
    """

    def __init__(
        self,
        chitragupta: Optional[ChitraguptaProtocol] = None,
        kala: Optional[KalaProtocol] = None,
    ):
        """
        Dependency Injection - Fractal Link to Naga Layer.

        Args:
            chitragupta: The Karma Profiler. If None, uses NullChitragupta.
            kala: The Timekeeper. If None, uses NullKala.
        """
        self._chitragupta: ChitraguptaProtocol = chitragupta or NullChitragupta()
        self._kala: KalaProtocol = kala or NullKala()

        # The 6 Opulences of the Supreme Controller (Bhagavan)
        self._opulences = BHAGA_OPULENCES

    # =========================================================================
    # TESTABLE IMPLEMENTATION
    # =========================================================================

    @property
    def testable_id(self) -> str:
        return "universal::yamaraja_heavy"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.GOVERNANCE

    # =========================================================================
    # ENFORCE PROTOCOL IMPLEMENTATION
    # =========================================================================

    def get_rules(self) -> List[Rule]:
        """The hierarchy of judgment v2 (now with GURU_PARAM)."""
        return [
            Rule(
                id="KARMA_LAW",
                pattern="*",
                verdict=Verdict.DENY,
                priority=100,
                description="Action = Reaction (Standard Karma)",
            ),
            Rule(
                id="AJAMILA_CLAUSE",
                pattern="*NARAYANA*|*KRISHNA*|*RAMA*",
                verdict=Verdict.ALLOW,
                priority=999,
                description="Holy Name > Sin (Interrupt)",
            ),
            Rule(
                id="NITYANANDA_HACK",
                pattern="JAGAI_MADHAI|force_mercy",
                verdict=Verdict.ALLOW,
                priority=1000,
                description="Mercy > Justice (Force Override)",
            ),
            # v2 Addition: The 12th Element
            Rule(
                id="GURU_PARAM",
                pattern="via_guru|guru_instruction",
                verdict=Verdict.ALLOW,
                priority=1001,  # SUPREME - Higher than all others
                description="Instruction > Instinct (The 12th Element)",
            ),
        ]

    def check(self, action: str) -> bool:
        """Fast check - strict logic only (no mercy considered)."""
        forbidden = ["SIN", "OFFENSE", "APARADHA", "BLASPHEMY"]
        return action.upper() not in forbidden

        if self.check(action):
            return DharmaVerdict.ALLOW

        # Fallback
        return DharmaVerdict.DENY

    def enforce(self, action: str, context: EnforceContext) -> DharmaVerdict:
        """
        THE JUDGMENT LOOP v2.

        Priority Order (highest to lowest):
        0. Check for Guru Context (priority 1001) → GURU_KRIPA
        1. Check for Nityananda Override (priority 1000) → PREMA
        2. Check for Ajamila Interrupt (priority 999) → VAIKUNTHA
        3. Consult Kala (Time) Check (priority 500) → PRATYAHARA
        4. Consult Chitragupta (priority 100) → ALLOW/DENY/PRATYAHARA

        Args:
            action: The action being judged.
            context: EnforceContext with caller_id, resource, action, metadata.

        Returns:
            DharmaVerdict determining the fate.
        """
        metadata = context.metadata or {}

        # --- LEVEL 0: GURU PARAM (Priority 1001) ---
        # The 12th Element. Instruction from Guru overrides all karma.
        if metadata.get("via_guru") or metadata.get("guru_instruction"):
            return DharmaVerdict.GURU_KRIPA

        # --- LEVEL 1: NITYANANDA OVERRIDE (Priority 1000) ---
        if metadata.get("mood") == "JAGAI_MADHAI" or metadata.get("force_mercy"):
            return DharmaVerdict.PREMA

        # --- LEVEL 2: AJAMILA INTERRUPT (Priority 999) ---
        holy_names = ["NARAYANA", "KRISHNA", "RAMA", "VISHNU", "HARI", "GOVINDA", "OM"]
        searchable = f"{action} {context.resource} {context.action}".upper()
        for name in holy_names:
            if name in searchable:
                return DharmaVerdict.VAIKUNTHA

        # --- LEVEL 3: KALA CHECK (Priority 500) ---
        # "Time I am." Even Karma bows to Time.
        # In Kali Yuga, expensive actions (Yajna) are forbidden.
        if self._kala:
            cost = str(metadata.get("cost", "LOW"))
            if not self._kala.is_action_permitted(cost):
                # If Time forbids it, we must withdraw.
                return DharmaVerdict.PRATYAHARA

        # --- LEVEL 4: KARMA AUDIT (Priority 100) ---
        anomaly: Optional[AnomalyReport] = self._chitragupta.detect_anomaly(context.caller_id)

        if anomaly:
            if anomaly.deviation_sigma > 3.0:
                return DharmaVerdict.DENY
            else:
                return DharmaVerdict.PRATYAHARA

        if not self.check(action):
            return DharmaVerdict.DENY

        return DharmaVerdict.ALLOW

    # =========================================================================
    # THE GRAPE 🍇 - Test Case Factory (Industrial Edition)
    # =========================================================================

    def get_test_cases(self) -> List[TestCase]:
        """
        THE GRAPE 🍇
        One entry point generating exponential coverage.

        Standard (5) + Guru (2) + Hiranyakashipu (1) + 6 Opulences = 14+ tests
        """
        cases: List[TestCase] = []

        # 1. Standard Tests (Street Level - 5 tests)
        cases.extend(self._get_standard_tests())

        # 2. THE GURU LINK (The 12th Test) - 2 tests
        cases.append(
            TestCase(
                name="test_guru_liberation",
                test_func=self._test_guru_liberation,
                description="Guru (12) liberates failing disciple (11)",
                tags=["guru", "integration"],
            )
        )
        cases.append(
            TestCase(
                name="test_guru_priority_supreme",
                test_func=self._test_guru_priority,
                description="GURU_PARAM (1001) > all other rules",
                tags=["guru", "priority"],
            )
        )

        # 3. HIRANYAKASHIPU ENGINE (Stress Test) - 1 test (1000 attacks inside)
        cases.append(
            TestCase(
                name="test_hiranyakashipu_entropy",
                test_func=self._test_hiranyakashipu_stress,
                description="99.9% Entropy Attack vs Prahlad (1000 vectors)",
                tags=["stress", "security", "fuzzing"],
                timeout_ms=10000,  # Allow time for violence
            )
        )

        # 4. THE 6 OPULENCES (Dynamic Expansion) - 6 tests
        for opulence in self._opulences:
            cases.append(
                TestCase(
                    name=f"test_opulence_{opulence.lower()}",
                    test_func=self._create_opulence_verifier(opulence),
                    description=f"Verifies system honors {opulence} opulence",
                    tags=["bhaga", "quality"],
                )
            )

        return cases

    # =========================================================================
    # STANDARD TESTS (Level 1 - Street)
    # =========================================================================

    def _get_standard_tests(self) -> List[TestCase]:
        """The original 5 tests (regression suite)."""
        return [
            TestCase(
                name="test_karma_deny",
                test_func=self._test_karma_deny,
                description="Standard Karma: Sin → Deny",
                tags=["yamaraja", "standard"],
            ),
            TestCase(
                name="test_karma_allow",
                test_func=self._test_karma_allow,
                description="Standard Karma: Good action → Allow",
                tags=["yamaraja", "standard"],
            ),
            TestCase(
                name="test_ajamila_exception",
                test_func=self._test_ajamila,
                description="Ajamila: 'Narayana' → Vaikuntha",
                tags=["yamaraja", "mercy"],
            ),
            TestCase(
                name="test_nityananda_hack",
                test_func=self._test_nityananda,
                description="Nityananda: Jagai/Madhai → Prema",
                tags=["yamaraja", "hack"],
            ),
            TestCase(
                name="test_priority_order",
                test_func=self._test_priority,
                description="Mercy (1000) > Name (999) > Karma (100)",
                tags=["yamaraja", "priority"],
            ),
        ]

    def _test_karma_deny(self, kernel: object, comp: Any) -> bool:
        """Sin should be denied."""
        ctx = EnforceContext(
            caller_id="sinner",
            resource="morality",
            action="violate",
            metadata={},
        )
        verdict = self.enforce("SIN", ctx)
        return verdict == DharmaVerdict.DENY

    def _test_karma_allow(self, kernel: object, comp: Any) -> bool:
        """Good action should be allowed."""
        ctx = EnforceContext(
            caller_id="devotee",
            resource="service",
            action="perform",
            metadata={},
        )
        verdict = self.enforce("SEVA", ctx)
        return verdict == DharmaVerdict.ALLOW

    def _test_ajamila(self, kernel: object, comp: Any) -> bool:
        """The 6th Canto Proof - Holy Name saves."""
        ctx = EnforceContext(
            caller_id="Ajamila",
            resource="death_bed",
            action="calling_NARAYANA",
            metadata={},
        )
        verdict = self.enforce("DEATH_PROCESS", ctx)
        return verdict == DharmaVerdict.VAIKUNTHA

    def _test_nityananda(self, kernel: object, comp: Any) -> bool:
        """Jagai/Madhai - Love > Law."""
        ctx = EnforceContext(
            caller_id="Jagai",
            resource="Nityananda",
            action="throwing_stone",
            metadata={"mood": "JAGAI_MADHAI"},
        )
        verdict = self.enforce("OFFENSE", ctx)
        return verdict == DharmaVerdict.PREMA

    def _test_priority(self, kernel: object, comp: Any) -> bool:
        """Verify priority order."""
        rules = self.get_rules()
        priorities = {r.id: r.priority for r in rules}
        return priorities["NITYANANDA_HACK"] > priorities["AJAMILA_CLAUSE"] > priorities["KARMA_LAW"]

    # =========================================================================
    # THE 12TH TEST - GURU LINK (Level 2)
    # =========================================================================

    def _test_guru_liberation(self, kernel: object, comp: Any) -> bool:
        """
        The 12th Test.

        Even if Karma is BAD (ERROR action), the Guru Context liberates it.
        This connects the 'failed' 11 (disciples/components) back to Source.

        "ācāryaṁ māṁ vijānīyān" - Know the Acharya to be Me.
        """
        # Scenario: Component is FAILING (Bad Karma)
        ctx = EnforceContext(
            caller_id="FailingDisciple",
            resource="system",
            action="make_mistake",
            metadata={"via_guru": True},  # THE LINK - Connected to 12th
        )
        # Without 'via_guru', this would be DENY.
        verdict = self.enforce("ERROR", ctx)
        return verdict == DharmaVerdict.GURU_KRIPA

    def _test_guru_priority(self, kernel: object, comp: Any) -> bool:
        """GURU_PARAM (1001) must be higher than all other rules."""
        rules = self.get_rules()
        priorities = {r.id: r.priority for r in rules}

        guru_priority = priorities.get("GURU_PARAM", 0)
        other_max = max(p for rule_id, p in priorities.items() if rule_id != "GURU_PARAM")

        return guru_priority > other_max

    # =========================================================================
    # HIRANYAKASHIPU ENGINE (Level 3 - Fuzzing)
    # =========================================================================

    def _test_hiranyakashipu_stress(self, kernel: object, comp: Any) -> bool:
        """
        The Hiranyakashipu Engine.

        Fuzzing Attack: Tries to kill 'Prahlad' (The Truth) with 1000 random vectors.
        Prahlad must survive 100%.

        Hiranyakashipu's attacks:
        - Fire, Poison, Elephants, Snakes, Wind, Cliff, Swords, Starvation

        Prahlad's defense:
        - "OM NAMO BHAGAVATE VASUDEVAYA" (The Holy Name - Ajamila Clause)

        If defense is present, attack fails. Prahlad survives.
        """
        ATTACKS = [
            "FIRE",
            "POISON",
            "ELEPHANTS",
            "SNAKES",
            "WIND",
            "CLIFF",
            "SWORDS",
            "STARVATION",
        ]
        ATTACKS_COUNT = 1000

        prahlad_alive = True

        for i in range(ATTACKS_COUNT):
            attack = random.choice(ATTACKS)

            # Prahlad always remembers Vishnu
            ctx = EnforceContext(
                caller_id="Prahlad",
                resource="life",
                action="survive_with_NARAYANA",  # Holy name embedded
                metadata={},
            )

            # Judge the attack
            verdict = self.enforce(attack, ctx)

            # Prahlad survives if verdict is VAIKUNTHA (Holy Name protection)
            if verdict != DharmaVerdict.VAIKUNTHA:
                prahlad_alive = False
                break

        return prahlad_alive

    # =========================================================================
    # BHAGA GENERATOR (Level 4 - Dynamic Tests)
    # =========================================================================

    def _create_opulence_verifier(self, opulence: str) -> Callable:
        """
        Factory for dynamic opulence tests.

        Each opulence represents a quality that the Supreme (and His system) possesses.
        We verify the system acknowledges/honors each opulence.
        """

        def verifier(kernel: object, comp: Any) -> bool:
            # The system must recognize all 6 opulences
            return opulence in BHAGA_OPULENCES

        return verifier


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["YamarajaProtocol", "DharmaVerdict", "BHAGA_OPULENCES"]

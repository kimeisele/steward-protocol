"""
YAMARAJA PROTOCOL - The Universal Judge (Layer 1)

"Dharmam tu sakshad bhagavat-pranitam" - Dharma is what God says.

Responsibilities:
1. Enforce the Law (Dharma) via EnforceProtocol.
2. Consult the Record (Chitragupta) via Naga Layer.
3. Handle the Exceptions (Mercy/Bhakti).

Fractal Integration:
- Uses protocols.naga.chitragupta for Profiling/Karma Audit.
- Uses protocols.universal.enforce for Interface.
- Implements Testable for Kernel Audit.

THE PRIORITY HIERARCHY:
- NITYANANDA_HACK (1000): Mercy > Justice (Force Override)
- AJAMILA_CLAUSE (999): Holy Name > Sin (Interrupt)
- KARMA_LAW (100): Action = Reaction (Standard)
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, List, Optional

from vibe_core.protocols.naga.chitragupta import AnomalyReport, ChitraguptaProtocol, NullChitragupta
from vibe_core.protocols.testable import BaseTestable, TestableType, TestCase

from .enforce import EnforceProtocol
from .types import EnforceContext, Rule, Verdict

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


# =============================================================================
# DHARMA VERDICT (Extended Judgment Types)
# =============================================================================


class DharmaVerdict(str, Enum):
    """
    Extended Verdict for Theocratic Law.

    Standard EnforceProtocol verdicts + Yamaraja extensions.
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


# =============================================================================
# YAMARAJA PROTOCOL
# =============================================================================


class YamarajaProtocol(BaseTestable):
    """
    The Lord of Death and Justice.

    FRACTAL PATTERN:
    - Inputs: Action + EnforceContext
    - Data Source: Chitragupta (The Karma Profiler)
    - Logic: Strict Karma UNLESS Mercy Interrupt.

    THE 3 LEVELS OF JUDGMENT:
    1. NITYANANDA (Force Mercy) → PREMA
    2. AJAMILA (Holy Name Interrupt) → VAIKUNTHA
    3. KARMA (Chitragupta Audit) → ALLOW/DENY/PRATYAHARA
    """

    def __init__(self, chitragupta: Optional[ChitraguptaProtocol] = None):
        """
        Dependency Injection - Fractal Link to Naga Layer.

        Args:
            chitragupta: The Karma Profiler. If None, uses NullChitragupta.
        """
        self._chitragupta: ChitraguptaProtocol = chitragupta or NullChitragupta()

    # =========================================================================
    # TESTABLE IMPLEMENTATION
    # =========================================================================

    @property
    def testable_id(self) -> str:
        return "universal::yamaraja"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.GOVERNANCE

    # =========================================================================
    # ENFORCE PROTOCOL IMPLEMENTATION
    # =========================================================================

    def get_rules(self) -> List[Rule]:
        """The hierarchy of judgment."""
        return [
            Rule(
                id="KARMA_LAW",
                pattern="*",  # Matches all actions
                verdict=Verdict.DENY,  # Default is strict
                priority=100,
                description="Action = Reaction (Standard Karma)",
            ),
            Rule(
                id="AJAMILA_CLAUSE",
                pattern="*NARAYANA*|*KRISHNA*|*RAMA*",  # Holy names
                verdict=Verdict.ALLOW,  # Mercy override
                priority=999,  # High Priority!
                description="Holy Name > Sin (Interrupt)",
            ),
            Rule(
                id="NITYANANDA_HACK",
                pattern="JAGAI_MADHAI|force_mercy",  # Mood triggers
                verdict=Verdict.ALLOW,  # Maximum mercy
                priority=1000,  # Maximum Priority
                description="Mercy > Justice (Force Override)",
            ),
        ]

    def check(self, action: str) -> bool:
        """Fast check - strict logic only (no mercy considered)."""
        forbidden = ["SIN", "OFFENSE", "APARADHA", "BLASPHEMY"]
        return action.upper() not in forbidden

    def enforce(self, action: str, context: EnforceContext) -> DharmaVerdict:
        """
        THE JUDGMENT LOOP.

        Priority Order:
        1. Check for Nityananda Override (Force Mercy) → PREMA
        2. Check for Ajamila Interrupt (Holy Name) → VAIKUNTHA
        3. Consult Chitragupta (Karma Audit) → ALLOW/DENY/PRATYAHARA

        Args:
            action: The action being judged.
            context: EnforceContext with caller_id, resource, action, metadata.

        Returns:
            DharmaVerdict determining the fate.
        """

        # --- LEVEL 3: NITYANANDA OVERRIDE (Priority 1000) ---
        # "Drunk" inputs or explicit surrender trigger unconditional mercy.
        metadata = context.metadata or {}
        if metadata.get("mood") == "JAGAI_MADHAI" or metadata.get("force_mercy"):
            # Logic fails here. Love takes over.
            # "Patita Pavana" - Savior of the most fallen.
            return DharmaVerdict.PREMA

        # --- LEVEL 2: AJAMILA INTERRUPT (Priority 999) ---
        # Did the entity chant the Holy Name?
        # Check in action, resource, and any metadata values.
        holy_names = ["NARAYANA", "KRISHNA", "RAMA", "VISHNU", "HARI", "GOVINDA"]

        searchable = f"{action} {context.resource} {context.action}".upper()
        for name in holy_names:
            if name in searchable:
                # IMMEDIATE INTERRUPT.
                # Yamadutas must withdraw. Soul goes to Vaikuntha.
                return DharmaVerdict.VAIKUNTHA

        # --- LEVEL 1: KARMA AUDIT (Priority 100) ---
        # Consult Chitragupta in the Naga Layer.
        anomaly: Optional[AnomalyReport] = self._chitragupta.detect_anomaly(context.caller_id)

        if anomaly:
            # Deviation detected. Check severity.
            if anomaly.deviation_sigma > 3.0:
                # Gross violation of Dharma (>3 sigma = extreme deviation).
                return DharmaVerdict.DENY
            else:
                # Minor correction needed.
                return DharmaVerdict.PRATYAHARA

        # No anomalies? Check the action directly.
        if not self.check(action):
            return DharmaVerdict.DENY

        # All clear. Proceed.
        return DharmaVerdict.ALLOW

    # =========================================================================
    # TEST CASES (12th Mahajana Tests)
    # =========================================================================

    def get_test_cases(self) -> List[TestCase]:
        """The Yamaraja Test Suite."""
        return [
            TestCase(
                name="test_karma_enforcement",
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
                description="Ajamila: Chanting 'Narayana' → Vaikuntha",
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

    def _test_karma_deny(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Sin should be denied."""
        ctx = EnforceContext(
            caller_id="sinner",
            resource="morality",
            action="violate",
            metadata={},
        )
        verdict = self.enforce("SIN", ctx)
        return verdict == DharmaVerdict.DENY

    def _test_karma_allow(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Good action should be allowed."""
        ctx = EnforceContext(
            caller_id="devotee",
            resource="service",
            action="perform",
            metadata={},
        )
        verdict = self.enforce("SEVA", ctx)
        return verdict == DharmaVerdict.ALLOW

    def _test_ajamila(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """
        The 6th Canto Proof.

        Ajamila was a great sinner, but at death he called his son
        named "Narayana" and was immediately saved.
        """
        ctx = EnforceContext(
            caller_id="Ajamila",
            resource="death_bed",
            action="calling_NARAYANA",  # Holy name in action
            metadata={},
        )
        verdict = self.enforce("DEATH_PROCESS", ctx)
        return verdict == DharmaVerdict.VAIKUNTHA

    def _test_nityananda(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """
        The Input that crashes logic but saves the soul.

        Jagai and Madhai were drunkards who attacked Lord Nityananda.
        Despite their offense, He showed mercy and saved them.
        """
        ctx = EnforceContext(
            caller_id="Jagai",
            resource="Nityananda",
            action="throwing_stone",
            metadata={"mood": "JAGAI_MADHAI"},  # Triggers mercy
        )
        verdict = self.enforce("OFFENSE", ctx)
        # Normal law says DEATH. Nityananda says PREMA.
        return verdict == DharmaVerdict.PREMA

    def _test_priority(self, kernel: "RealVibeKernel", comp: Any) -> bool:
        """Verify priority order: Nityananda > Ajamila > Karma."""
        rules = self.get_rules()
        priorities = {r.id: r.priority for r in rules}

        return priorities["NITYANANDA_HACK"] > priorities["AJAMILA_CLAUSE"] > priorities["KARMA_LAW"]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = ["YamarajaProtocol", "DharmaVerdict"]

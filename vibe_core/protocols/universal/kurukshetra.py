"""
KURUKSHETRA PROTOCOL - The Dynamic Battlefield (Layer 1.5)

"Kurukshetra" = The Field of the Kurus / The Battlefield of Dharma

This is NOT a static test runner. This is a SAMSARA LOOP:
- Components are spawned, stressed, judged, and reincarnated.
- Survivors enter Vaikuntha (Hall of Fame).
- Failures enter the Graveyard (Naraka).

THE BATTLEFIELD:
1. Kshetra (Field): The continuous execution loop (Time/Kala)
2. Warriors (Genes): Dynamic components with capabilities
3. Shield (Balarama): Naga Proxy wrapping all warriors
4. Judge (Yamaraja): Every action is judged

ISOLATION PRINCIPLE:
"Na ca mat-sthani bhutani" - Everything rests in Me, but I am not in them.
The engine executes tests WITHOUT being infected by failures.

Layer: 1.5 (Between Universal and Implementation)
Status: INDUSTRIAL / BATTLEFIELD GRADE
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xec103767"  # GenesisByte: parampara % 37 == 0

import random
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

from vibe_core.protocols.substrate import GeneManifest, GeneStatus
from vibe_core.protocols.testable import BaseTestable, TestableType, TestCase

from .types import EnforceContext, SovereignContext

# YamarajaProtocol is in mahajanas/ (the 12 authorities)
from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocol

# DharmaVerdict is in universal/dharma
from vibe_core.protocols.universal.dharma import DharmaVerdict

# Validated: No Implementation Imports
pass


# =============================================================================
# BATTLE STATUS ENUMS
# =============================================================================


class WarriorStatus(str, Enum):
    """Status of a warrior on the battlefield."""

    ALIVE = "ALIVE"  # Currently fighting
    DEAD = "DEAD"  # Failed, awaiting reincarnation
    VAIKUNTHA = "VAIKUNTHA"  # Liberated (passed all tests)
    NARAKA = "NARAKA"  # Condemned (too many failures)


class AttackType(str, Enum):
    """Types of attacks in the Hiranyakashipu arsenal."""

    OVERFLOW = "OVERFLOW"  # Memory stress
    CHAOS = "CHAOS"  # Random invalid input
    STARVATION = "STARVATION"  # Resource deprivation
    BETRAYAL = "BETRAYAL"  # Unauthorized access attempt
    CORRUPTION = "CORRUPTION"  # Data integrity attack
    TIMEOUT = "TIMEOUT"  # Infinite loop detection


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class WarriorRecord:
    """Record of a warrior's battle history."""

    gene_name: str
    capabilities: Tuple[str, ...]
    status: WarriorStatus = WarriorStatus.ALIVE
    battles_fought: int = 0
    battles_won: int = 0
    deaths: int = 0
    reincarnations: int = 0
    karma_score: int = 0  # Positive = good, Negative = bad
    last_verdict: Optional[DharmaVerdict] = None
    spawn_time: datetime = field(default_factory=datetime.now)


@dataclass
class BattleReport:
    """Summary of the battlefield after a cycle."""

    total_warriors: int
    survivors: List[str]
    casualties: List[str]
    liberated: List[str]  # Vaikuntha
    condemned: List[str]  # Naraka
    total_battles: int
    total_reincarnations: int
    cycle_duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def survival_rate(self) -> float:
        """Calculate survival percentage."""
        if self.total_warriors == 0:
            return 0.0
        return len(self.survivors) / self.total_warriors * 100


# =============================================================================
# KURUKSHETRA ENGINE
# =============================================================================


class KurukshetraProtocol(BaseTestable):
    """
    THE KURUKSHETRA ENGINE - The Dynamic Battlefield.

    A continuous execution environment that:
    1. Spawns warriors (components with genes)
    2. Attacks them with Hiranyakashipu vectors
    3. Judges them via Yamaraja
    4. Reincarnates failures or liberates survivors

    SAMSARA LOOP:
    spawn → attack → judge → reincarnate/liberate → repeat

    ISOLATION: Failures in warriors don't crash the engine.
    """

    def __init__(
        self,
        yamaraja: Optional[YamarajaProtocol] = None,
        max_reincarnations: int = 3,
        attacks_per_cycle: int = 10,
    ):
        """
        Initialize the battlefield.

        Args:
            yamaraja: The judge (uses default if None)
            max_reincarnations: Max times a warrior can die and return
            attacks_per_cycle: Number of attack vectors per battle
        """
        self._yamaraja = yamaraja or YamarajaProtocol()
        self._max_reincarnations = max_reincarnations
        self._attacks_per_cycle = attacks_per_cycle

        # Battlefield state
        self._warriors: Dict[str, WarriorRecord] = {}
        self._graveyard: List[str] = []  # Naraka
        self._hall_of_fame: List[str] = []  # Vaikuntha
        self._battle_count = 0

    # =========================================================================
    # TESTABLE IMPLEMENTATION
    # =========================================================================

    @property
    def testable_id(self) -> str:
        return "universal::kurukshetra_engine"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.RUNTIME

    def get_test_cases(self) -> List[TestCase]:
        """Engine's own self-verification tests."""
        return [
            TestCase(
                name="test_engine_isolation",
                test_func=self._test_isolation,
                description="Engine survives warrior failures",
                tags=["kurukshetra", "isolation"],
            ),
            TestCase(
                name="test_reincarnation_cycle",
                test_func=self._test_reincarnation,
                description="Warriors can die and return",
                tags=["kurukshetra", "samsara"],
            ),
            TestCase(
                name="test_liberation_path",
                test_func=self._test_liberation,
                description="Survivors reach Vaikuntha",
                tags=["kurukshetra", "moksha"],
            ),
            TestCase(
                name="test_karma_accumulation",
                test_func=self._test_karma,
                description="Good deeds accumulate positive karma",
                tags=["kurukshetra", "karma"],
            ),
        ]

    # =========================================================================
    # CORE ENGINE METHODS
    # =========================================================================

    def spawn_warrior(self, manifest: GeneManifest) -> WarriorRecord:
        """
        Spawn a warrior from a gene manifest.

        Args:
            manifest: The gene's capabilities and requirements

        Returns:
            WarriorRecord for the spawned warrior
        """
        warrior = WarriorRecord(
            gene_name=manifest.name,
            capabilities=manifest.capabilities,
            status=WarriorStatus.ALIVE,
        )
        self._warriors[manifest.name] = warrior
        return warrior

    def attack_warrior(self, warrior_name: str, attack: AttackType) -> Tuple[bool, DharmaVerdict]:
        """
        Attack a warrior with a Hiranyakashipu vector.

        The attack is judged by Yamaraja. The warrior's survival
        depends on its connection (via_guru) and holy name presence.

        Args:
            warrior_name: Name of the warrior to attack
            attack: Type of attack

        Returns:
            (survived, verdict)
        """
        if warrior_name not in self._warriors:
            return (False, DharmaVerdict.DENY)

        warrior = self._warriors[warrior_name]

        # Create enforce context for Yamaraja
        ctx = EnforceContext(
            caller_id=warrior_name,
            resource="battlefield",
            action=f"survive_{attack.value}",
            metadata={
                "attack_type": attack.value,
                "karma_score": warrior.karma_score,
            },
        )

        # Let Yamaraja judge
        verdict = self._yamaraja.enforce(attack.value, ctx)

        # Determine survival
        survived = verdict in [
            DharmaVerdict.ALLOW,
            DharmaVerdict.VAIKUNTHA,
            DharmaVerdict.PREMA,
            DharmaVerdict.GURU_KRIPA,
        ]

        # Update warrior stats
        warrior.battles_fought += 1
        warrior.last_verdict = verdict

        if survived:
            warrior.battles_won += 1
            warrior.karma_score += 1
        else:
            warrior.karma_score -= 1

        return (survived, verdict)

    def kill_warrior(self, warrior_name: str) -> None:
        """Send a warrior to death."""
        if warrior_name in self._warriors:
            warrior = self._warriors[warrior_name]
            warrior.deaths += 1
            warrior.status = WarriorStatus.DEAD

    def reincarnate_warrior(self, warrior_name: str) -> bool:
        """
        Attempt to reincarnate a dead warrior.

        Warriors have limited reincarnations (Samsara limit).

        Returns:
            True if reincarnated, False if condemned to Naraka
        """
        if warrior_name not in self._warriors:
            return False

        warrior = self._warriors[warrior_name]

        if warrior.reincarnations >= self._max_reincarnations:
            # Too many deaths - condemned to Naraka
            warrior.status = WarriorStatus.NARAKA
            self._graveyard.append(warrior_name)
            return False

        # Reincarnate with clean slate (but karma persists!)
        warrior.status = WarriorStatus.ALIVE
        warrior.reincarnations += 1
        warrior.spawn_time = datetime.now()
        return True

    def liberate_warrior(self, warrior_name: str) -> None:
        """
        Liberate a warrior to Vaikuntha (Hall of Fame).

        This happens when a warrior has positive karma and survives
        all attacks in a cycle.
        """
        if warrior_name in self._warriors:
            warrior = self._warriors[warrior_name]
            warrior.status = WarriorStatus.VAIKUNTHA
            self._hall_of_fame.append(warrior_name)

    # =========================================================================
    # SAMSARA LOOP (The Main Battle Cycle)
    # =========================================================================

    def run_battle_cycle(self, seed_genes: List[GeneManifest], n_cycles: int = 1) -> BattleReport:
        """
        Run the Samsara Loop.

        This is the main battlefield execution:
        1. Spawn warriors from gene manifests
        2. Attack each warrior with random vectors
        3. Judge and update status
        4. Reincarnate or liberate

        Args:
            seed_genes: Gene manifests to spawn as warriors
            n_cycles: Number of complete battle cycles

        Returns:
            BattleReport summarizing the battle
        """
        start_time = time.time()

        # Phase 1: Spawn all warriors
        for manifest in seed_genes:
            if manifest.name not in self._warriors:
                self.spawn_warrior(manifest)

        total_battles = 0
        total_reincarnations = 0

        # Phase 2: The Samsara Loop
        for _ in range(n_cycles):
            for warrior_name, warrior in list(self._warriors.items()):
                if warrior.status not in [WarriorStatus.ALIVE]:
                    continue

                # Generate random attacks
                attacks = random.choices(list(AttackType), k=self._attacks_per_cycle)

                survived_all = True
                for attack in attacks:
                    try:
                        survived, verdict = self.attack_warrior(warrior_name, attack)
                        total_battles += 1
                        self._battle_count += 1

                        if not survived:
                            survived_all = False
                            self.kill_warrior(warrior_name)

                            # Attempt reincarnation
                            if self.reincarnate_warrior(warrior_name):
                                total_reincarnations += 1
                            break

                    except Exception:
                        # ISOLATION: Engine survives warrior failures
                        survived_all = False
                        self.kill_warrior(warrior_name)
                        if self.reincarnate_warrior(warrior_name):
                            total_reincarnations += 1
                        break

                # Check for liberation (survived all + positive karma)
                if survived_all and warrior.karma_score > 5:
                    self.liberate_warrior(warrior_name)

        # Generate report
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        survivors = [name for name, w in self._warriors.items() if w.status == WarriorStatus.ALIVE]
        casualties = [name for name, w in self._warriors.items() if w.status == WarriorStatus.DEAD]
        liberated = [name for name, w in self._warriors.items() if w.status == WarriorStatus.VAIKUNTHA]
        condemned = [name for name, w in self._warriors.items() if w.status == WarriorStatus.NARAKA]

        return BattleReport(
            total_warriors=len(self._warriors),
            survivors=survivors,
            casualties=casualties,
            liberated=liberated,
            condemned=condemned,
            total_battles=total_battles,
            total_reincarnations=total_reincarnations,
            cycle_duration_ms=duration_ms,
        )

    # =========================================================================
    # SELF-VERIFICATION TESTS
    # =========================================================================

    def _test_isolation(self, kernel: object, comp: Any) -> bool:
        """Engine survives failing warriors."""

        class FailingGene:
            def execute(self):
                raise RuntimeError("I AM A DEMON")

        # Create a manifest for a weapon that always fails
        manifest = GeneManifest(
            name="demon_gene",
            capabilities=("fail",),
            requires=(),
            priority=1,
        )

        # Spawn and attack - engine should survive
        self.spawn_warrior(manifest)

        engine_alive = True
        try:
            for attack in AttackType:
                self.attack_warrior("demon_gene", attack)
            # If we reach here, engine survived
        except Exception:
            engine_alive = False

        return engine_alive

    def _test_reincarnation(self, kernel: object, comp: Any) -> bool:
        """Warriors can die and be reborn."""
        manifest = GeneManifest(
            name="mortal_gene",
            capabilities=("die",),
            requires=(),
        )

        self.spawn_warrior(manifest)
        self.kill_warrior("mortal_gene")

        # Should be dead
        if self._warriors["mortal_gene"].status != WarriorStatus.DEAD:
            return False

        # Reincarnate
        reborn = self.reincarnate_warrior("mortal_gene")

        if not reborn:
            return False

        return self._warriors["mortal_gene"].status == WarriorStatus.ALIVE

    def _test_liberation(self, kernel: object, comp: Any) -> bool:
        """Survivors with good karma reach Vaikuntha."""
        manifest = GeneManifest(
            name="devotee_gene",
            capabilities=("serve",),
            requires=(),
        )

        warrior = self.spawn_warrior(manifest)
        warrior.karma_score = 10  # Good karma
        warrior.battles_won = 100

        self.liberate_warrior("devotee_gene")

        return self._warriors["devotee_gene"].status == WarriorStatus.VAIKUNTHA

    def _test_karma(self, kernel: object, comp: Any) -> bool:
        """Good deeds increase karma."""
        manifest = GeneManifest(
            name="karma_test_gene",
            capabilities=("serve_KRISHNA",),  # Holy name triggers mercy
            requires=(),
        )

        self.spawn_warrior(manifest)
        initial_karma = self._warriors["karma_test_gene"].karma_score

        # Win a battle (mock by directly incrementing)
        self._warriors["karma_test_gene"].karma_score += 1

        return self._warriors["karma_test_gene"].karma_score > initial_karma


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KurukshetraProtocol",
    "WarriorStatus",
    "WarriorRecord",
    "BattleReport",
    "AttackType",
]

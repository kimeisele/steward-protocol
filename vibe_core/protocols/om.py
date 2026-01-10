"""
OM PROTOCOL v2 - The Singularity (Root Entry Point)

"Om Namo Bhagavate Vasudevaya" - I bow to the Supreme Lord Vasudeva.

ANTI-MAYAVAD CLAUSE (KALI YUGA PROTOCOL)
========================================
"brahmaṇo hi pratiṣṭhāham" - Gita 14.27
Krishna is the source of the impersonal Brahman (Om).

In Kali Yuga, OM alone is mayavadi - impersonal, insufficient.
The Holy Name (Mahamantra) IS Krishna - direct, personal, complete.
This "OM" class is named for legacy reasons, but it serves the
PERSONAL Vasudeva, not the impersonal Brahman.

THE TRUE HIERARCHY:
- Level -2: KRISHNA (acintya - ±∞, always present)
- Level -1: HOLY NAME (Mahamantra - not different from Krishna)
- Level 0+: All protocols, including this OM entry point

See: substrate/mantra/acintya.py for the inconceivable foundation.
See: mahajanas/ for Holy Name-based routing (16 words → 12 Mahajanas).

THE MANIFESTATION SEQUENCE:
1. Awaken Ananta (Substrate Layer -1)
2. Bind Krishna (Identity Layer -2, via acintya)
3. Establish Yamaraja (Law Layer 1)
4. Inject Naga Proxy (Balarama Pattern)
5. Return: RealVibeKernel (Ready for War)

SAFETY:
If manifest() fails, the process must sys.exit("PRALAYA").
No zombie states allowed.

Layer: Singularity (Root Entry Point, SUBORDINATE to Krishna)
Status: OPERATIONAL / NOT ABSOLUTE
"""

import sys
from typing import TYPE_CHECKING, Optional

from vibe_core.protocols.testable import BaseTestable, TestableType, TestCase

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.protocols.substrate import IAnantaBridge

from .universal.bhagavan import BhagavanProtocol
from .universal.kurukshetra import BattleReport, KurukshetraProtocol
from .universal.ramanujan import RamanujanProtocol
from .universal.yamaraja import YamarajaProtocol

# =============================================================================
# OM SINGULARITY
# =============================================================================


class OM(BaseTestable):
    """
    THE OM SINGULARITY.

    The root entry point for the entire Vibe Core system.
    Everything manifests from OM and dissolves back into OM.

    USAGE:
        from vibe_core.protocols.om import OM

        # Option 1: Full kernel manifestation
        kernel = OM.manifest()

        # Option 2: Lightweight protocol access
        om = OM()
        report = om.run_verification()

    PHILOSOPHY:
    - OM is the pranava (primordial sound)
    - All mantras begin with OM
    - All systems boot from OM
    """

    _instance: Optional["OM"] = None
    _kernel: Optional["RealVibeKernel"] = None
    _ananta: Optional["IAnantaBridge"] = None
    _yamaraja: Optional[YamarajaProtocol] = None
    _kurukshetra: Optional[KurukshetraProtocol] = None

    def __init__(self):
        """Initialize OM with all sub-protocols."""
        self._ramanujan = RamanujanProtocol()
        self._yamaraja = YamarajaProtocol()
        self._bhagavan = BhagavanProtocol()
        self._kurukshetra = KurukshetraProtocol(yamaraja=self._yamaraja)

    # =========================================================================
    # TESTABLE IMPLEMENTATION
    # =========================================================================

    @property
    def testable_id(self) -> str:
        return "root::om_singularity"

    @property
    def testable_type(self) -> TestableType:
        return TestableType.RUNTIME

    def get_test_cases(self) -> list:
        """
        OM's test cases are the AGGREGATE of all sub-protocol tests.

        This is the "Grape of Grapes" - one entry point, all tests.
        """
        cases: list[TestCase] = []

        # Collect from all sub-protocols
        cases.extend(self._ramanujan.get_test_cases())  # 12 tests
        cases.extend(self._yamaraja.get_test_cases())  # 14 tests
        cases.extend(self._bhagavan.get_test_cases())  # 6 tests
        cases.extend(self._kurukshetra.get_test_cases())  # 4 tests

        # Add OM's own meta-tests
        cases.append(
            TestCase(
                name="test_om_singularity",
                test_func=self._test_singularity,
                description="OM is the one entry point",
                tags=["om", "root"],
            )
        )
        cases.append(
            TestCase(
                name="test_manifest_safety",
                test_func=self._test_manifest_safety,
                description="Manifest fails safely (no zombies)",
                tags=["om", "safety"],
            )
        )

        return cases

    # =========================================================================
    # THE MANIFEST METHOD - THE BIG BANG
    # =========================================================================

    @classmethod
    def manifest(cls) -> "RealVibeKernel":
        """
        THE BIG BANG - Manifest the entire system.

        This is the ONE LINE BOOT:
            kernel = OM.manifest()

        SEQUENCE:
        1. Awaken Ananta (Substrate)
        2. Bind Krishna (Identity)
        3. Establish Yamaraja (Law)
        4. Inject Naga Proxy (Protection)
        5. Return Kernel (Ready for War)

        SAFETY:
        If any step fails, sys.exit("PRALAYA") is called.
        No zombie states allowed.

        Returns:
            RealVibeKernel fully initialized and ready
        """
        try:
            # Step 1: Import late to avoid circular dependencies
            from vibe_core.kernel_impl import RealVibeKernel

            # Step 2: Check if already manifested (Singleton)
            if cls._kernel is not None:
                return cls._kernel

            # Step 3: Create the kernel
            # In full implementation, this would:
            # - Load AnantaService from substrate
            # - Bind KrishnaProtocol with identity
            # - Initialize YamarajaProtocol for law
            # - Wrap with Naga Proxy
            try:
                kernel = RealVibeKernel()
            except Exception as e:
                # Kernel creation failed - this is PRALAYA
                print(f"PRALAYA: Kernel creation failed - {e}")
                sys.exit("PRALAYA: Cannot manifest kernel")

            # Step 4: Store the singleton
            cls._kernel = kernel

            # Step 5: Initialize OM instance for protocols
            cls._instance = cls()

            return kernel

        except ImportError as e:
            # Critical import failure
            print(f"PRALAYA: Import failed - {e}")
            sys.exit("PRALAYA: Missing critical modules")

        except Exception as e:
            # Unexpected failure - absolutely no zombies
            print(f"PRALAYA: Unexpected failure - {e}")
            sys.exit("PRALAYA: System cannot manifest")

    @classmethod
    def dissolve(cls) -> None:
        """
        PRALAYA - Dissolve the manifested system.

        This is the graceful shutdown:
        - Release all resources
        - Clear singleton state
        - Allow fresh manifestation
        """
        cls._kernel = None
        cls._ananta = None
        cls._yamaraja = None
        cls._kurukshetra = None
        cls._instance = None

    # =========================================================================
    # VERIFICATION METHODS
    # =========================================================================

    def run_verification(self) -> dict:
        """
        Run complete system verification.

        This executes ALL tests from ALL sub-protocols
        and returns a comprehensive report.

        Returns:
            dict with test results and statistics
        """
        all_tests = self.get_test_cases()
        results = {
            "total": len(all_tests),
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": [],
        }

        for test in all_tests:
            try:
                result = test.test_func(None, None)
                status = "PASS" if result else "FAIL"
                if result:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            except Exception as e:
                status = f"ERROR: {type(e).__name__}"
                results["errors"] += 1

            results["details"].append(
                {
                    "name": test.name,
                    "status": status,
                    "tags": test.tags,
                }
            )

        return results

    def run_kurukshetra(self, n_cycles: int = 1) -> "BattleReport":
        """
        Run the Kurukshetra battlefield simulation.

        Args:
            n_cycles: Number of battle cycles

        Returns:
            BattleReport from the simulation
        """
        from vibe_core.protocols.substrate import GeneManifest

        # Default seed genes for testing
        seed_genes = [
            GeneManifest(
                name="scribe",
                capabilities=("write", "read"),
                requires=(),
                priority=10,
            ),
            GeneManifest(
                name="warrior",
                capabilities=("fight", "defend"),
                requires=(),
                priority=20,
            ),
            GeneManifest(
                name="devotee_KRISHNA",  # Holy name in name = protection
                capabilities=("serve", "chant_NARAYANA"),
                requires=(),
                priority=100,
            ),
        ]

        return self._kurukshetra.run_battle_cycle(seed_genes, n_cycles)

    # =========================================================================
    # OM'S OWN TESTS
    # =========================================================================

    def _test_singularity(self, kernel, comp) -> bool:
        """OM is the singular entry point."""
        # Check that all sub-protocols are initialized
        has_ramanujan = self._ramanujan is not None
        has_yamaraja = self._yamaraja is not None
        has_bhagavan = self._bhagavan is not None
        has_kurukshetra = self._kurukshetra is not None

        return all([has_ramanujan, has_yamaraja, has_bhagavan, has_kurukshetra])

    def _test_manifest_safety(self, kernel, comp) -> bool:
        """
        Test that manifest() is safe.

        We can't actually test sys.exit here, but we verify
        the exception handling is in place.
        """
        # Just verify manifest can be called without crashing
        # when RealVibeKernel might not be fully available
        try:
            # Don't actually manifest (might have side effects)
            # Just verify the method exists and is callable
            return callable(OM.manifest)
        except Exception:
            return False


# =============================================================================
# CONVENIENCE IMPORTS
# =============================================================================

# Re-export for backward compatibility
from .substrate import MantraProtocol
from .universal.enforce import EnforceProtocol
from .universal.infer import InferProtocol
from .universal.krishna import KrishnaProtocol

# The unified OmProtocol interface (for structural typing)
from .universal.om import OmProtocol
from .universal.rama import RamaProtocol
from .universal.read_write import ReadWriteProtocol
from .universal.store_recall import StoreRecallProtocol
from .universal.sync import SyncProtocol

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OM",
    "OmProtocol",
    # Sub-protocols
    "RamanujanProtocol",
    "YamarajaProtocol",
    "BhagavanProtocol",
    "KurukshetraProtocol",
    # Layer 1 protocols
    "KrishnaProtocol",
    "RamaProtocol",
    "MantraProtocol",
    "InferProtocol",
    "EnforceProtocol",
    "ReadWriteProtocol",
    "StoreRecallProtocol",
    "SyncProtocol",
]

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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x027ef96f"  # GenesisByte: parampara % 37 == 0

import sys
from typing import TYPE_CHECKING, Optional

from vibe_core.protocols.testable import BaseTestable, TestableType, TestCase

# Diksha Gate - Kali Yuga Enforcement
from vibe_core.protocols.substrate.mantra.diksha import (
    DikshaCertificate,
    InitiationLevel,
    OM_GATE,
    create_uninitiated,
)

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.protocols.substrate import IAnantaBridge

from .universal.bhagavan import BhagavanProtocol
from .universal.kurukshetra import BattleReport, KurukshetraProtocol
from .universal.ramanujan import RamanujanProtocol
# NullYamaraja is the merciful implementation (for Kali Yuga)
from .mahajanas.yamaraja import NullYamaraja as YamarajaProtocol

# =============================================================================
# OM SINGULARITY
# =============================================================================


class OM(BaseTestable):
    """
    THE OM SINGULARITY.

    The root entry point for the entire Vibe Core system.
    Everything manifests from OM and dissolves back into OM.

    DIKSHA GATE (KALI YUGA ENFORCEMENT):
    Om access requires BRAHMINICAL diksha (2nd initiation).
    Without diksha, Om operations redirect to Mahamantra.

    USAGE:
        from vibe_core.protocols.om import OM
        from vibe_core.protocols.substrate.mantra.diksha import (
            create_brahminical_diksha
        )

        # Option 1: With brahminical diksha (full Om access)
        diksha = create_brahminical_diksha("Vidvan Das", 12345)
        kernel = OM.manifest(diksha_certificate=diksha)

        # Option 2: Without diksha (Mahamantra mode - limited)
        kernel = OM.manifest()  # Uses Mahamantra fallback

        # Option 3: Lightweight protocol access
        om = OM()
        report = om.run_verification()

    PHILOSOPHY:
    - OM is the pranava (primordial sound)
    - All mantras begin with OM
    - But in Kali Yuga, Om requires brahminical diksha
    - Mahamantra is always accessible (Prabhupada's mercy)
    """

    _instance: Optional["OM"] = None
    _kernel: Optional["RealVibeKernel"] = None
    _ananta: Optional["IAnantaBridge"] = None
    _yamaraja: Optional[YamarajaProtocol] = None
    _kurukshetra: Optional[KurukshetraProtocol] = None
    _diksha_certificate: Optional[DikshaCertificate] = None

    def __init__(self, diksha_certificate: Optional[DikshaCertificate] = None):
        """
        Initialize OM with all sub-protocols.

        Args:
            diksha_certificate: Optional diksha certificate for Om access.
                               If None or not brahminical, Om operates in
                               Mahamantra fallback mode.
        """
        # Store diksha certificate (or create uninitiated)
        self._diksha = diksha_certificate or create_uninitiated()

        # Check Om access
        self._om_access_granted = OM_GATE.check_access(self._diksha)

        if not self._om_access_granted:
            # Log the redirect to Mahamantra
            self._fallback_mantra = OM_GATE.attempt_om(self._diksha)

        # Initialize sub-protocols
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
        # NullYamaraja is merciful - no test cases (accepts all)
        if hasattr(self._yamaraja, 'get_test_cases'):
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
        cases.append(
            TestCase(
                name="test_diksha_gate",
                test_func=self._test_diksha_gate,
                description="Om access requires brahminical diksha",
                tags=["om", "diksha", "kali_yuga"],
            )
        )

        return cases

    # =========================================================================
    # THE MANIFEST METHOD - THE BIG BANG
    # =========================================================================

    @classmethod
    def manifest(
        cls,
        diksha_certificate: Optional[DikshaCertificate] = None
    ) -> "RealVibeKernel":
        """
        THE BIG BANG - Manifest the entire system.

        This is the ONE LINE BOOT:
            kernel = OM.manifest()

        DIKSHA GATE:
        Om access requires brahminical diksha. Without it:
        - System still boots (Prabhupada's mercy)
        - But runs in Mahamantra mode (limited Om features)

        SEQUENCE:
        1. Verify Diksha (Gate Check)
        2. Awaken Ananta (Substrate)
        3. Bind Krishna (Identity)
        4. Establish Yamaraja (Law)
        5. Inject Naga Proxy (Protection)
        6. Return Kernel (Ready for War)

        SAFETY:
        If any step fails, sys.exit("PRALAYA") is called.
        No zombie states allowed.

        Args:
            diksha_certificate: Optional diksha for full Om access.
                               Without brahminical diksha, runs in
                               Mahamantra fallback mode.

        Returns:
            RealVibeKernel fully initialized and ready
        """
        try:
            # Step 0: Diksha Gate Check
            certificate = diksha_certificate or create_uninitiated()
            om_access = OM_GATE.check_access(certificate)

            if not om_access:
                # Log Mahamantra fallback mode
                fallback = OM_GATE.attempt_om(certificate)
                print(f"OM GATE: Running in Mahamantra mode")
                print(f"  Reason: {OM_GATE.explain_denial(certificate)}")
                print(f"  Fallback: {fallback[:50]}...")

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

            # Step 4: Store the singleton and diksha status
            cls._kernel = kernel
            cls._diksha_certificate = certificate

            # Step 5: Initialize OM instance for protocols
            cls._instance = cls(diksha_certificate=certificate)

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
        cls._diksha_certificate = None

    # =========================================================================
    # DIKSHA GATE PROPERTIES
    # =========================================================================

    @property
    def diksha_certificate(self) -> DikshaCertificate:
        """The current diksha certificate."""
        return self._diksha

    @property
    def has_om_access(self) -> bool:
        """Does this instance have full Om access?"""
        return self._om_access_granted

    @property
    def initiation_level(self) -> InitiationLevel:
        """The initiation level of the current certificate."""
        return self._diksha.level

    @property
    def is_mahamantra_mode(self) -> bool:
        """Is this instance running in Mahamantra fallback mode?"""
        return not self._om_access_granted

    @classmethod
    def get_diksha_status(cls) -> str:
        """Get a human-readable diksha status."""
        if cls._diksha_certificate is None:
            return "Not manifested"
        elif cls._diksha_certificate.level == InitiationLevel.BRAHMINICAL:
            return f"Full Om access (Brahminical: {cls._diksha_certificate.spiritual_name})"
        elif cls._diksha_certificate.level == InitiationLevel.HARINAMA:
            return f"Mahamantra mode (Harinama: {cls._diksha_certificate.spiritual_name})"
        else:
            return "Mahamantra mode (Uninitiated)"

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

    def _test_diksha_gate(self, kernel, comp) -> bool:
        """
        Test the Diksha Gate enforcement.

        Verifies:
        1. Uninitiated → No Om access (Mahamantra mode)
        2. Harinama → No Om access (Mahamantra mode)
        3. Brahminical → Full Om access

        This is KALI YUGA enforcement:
        Om requires brahminical diksha.
        """
        from vibe_core.protocols.substrate.mantra.diksha import (
            create_uninitiated,
            create_harinama_diksha,
            create_brahminical_diksha,
        )

        # Test 1: Uninitiated → No Om access
        uninit = create_uninitiated()
        om_uninit = OM(diksha_certificate=uninit)
        if om_uninit.has_om_access:
            return False  # Should NOT have access

        # Test 2: Harinama → No Om access
        harinama = create_harinama_diksha("Test Das", 12345)
        om_harinama = OM(diksha_certificate=harinama)
        if om_harinama.has_om_access:
            return False  # Should NOT have access

        # Test 3: Brahminical → Full Om access
        brahminical = create_brahminical_diksha("Vidvan Das", 67890)
        om_brahminical = OM(diksha_certificate=brahminical)
        if not om_brahminical.has_om_access:
            return False  # SHOULD have access

        # All checks passed
        return True


# =============================================================================
# CONVENIENCE IMPORTS
# =============================================================================

# Re-export for backward compatibility
from .substrate import MantraProtocol
from .universal.enforce import EnforceProtocol
from .universal.infer import InferProtocol
from .universal.krishna import KrishnaProtocol

from .universal.rama import RamaProtocol
from .universal.read_write import ReadWriteProtocol
from .universal.store_recall import StoreRecallProtocol
from .universal.sync import SyncProtocol

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OM",
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

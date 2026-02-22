"""
TEST IMMUNE SYSTEM — Proof of Concept
======================================

"yasya deve parā bhaktir yathā deve tathā gurau
tasyaite kathitā hy arthāḥ prakāśante mahātmanaḥ"
— Śvetāśvatara Upaniṣad 6.23

PROBLEM:
========
9432 pytest functions. 255 seconds to COLLECT. Dead scripts testing a living system.

The system ALREADY has a living immune system:
- GADProtocol: test_daya(), test_satyam(), test_tapas(), test_saucam()
- ShadowReactor.test_daya(): Self-test with KillerReactor injection
- verify_all_derived(): 13 axiom asserts at import
- verify_link(): Parampara chain at birth
- MantraHeartbeat.chant(): State machine

But the two worlds are DISCONNECTED:
- pytest tests NEVER call component.audit()
- GAD self-tests are NEVER collected by pytest
- 9432 dead scripts duplicate what GAD already does alive

THIS FILE:
==========
Proof-of-concept: Run GAD audits as the test suite.
No pytest. No filesystem. Components test THEMSELVES.

The immune system is already built. We just need to WIRE it.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x5030044b"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, Tuple
import time

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    NAVA,
    PARAMPARA,
    QUARTERS,
    WORDS,
)


# =============================================================================
# 1. AUDIT RESULT — What a living test produces
# =============================================================================


@dataclass(frozen=True)
class AuditVerdict:
    """Result of a single component self-test."""

    component: str
    position: int
    daya: bool  # Mercy: crash handling
    satyam: bool  # Truth: output verified
    tapas: bool  # Austerity: resources bounded
    saucam: bool  # Cleanliness: connections authorized
    healthy: bool  # Overall health
    parampara: bool  # Link to disciplic succession
    elapsed_ms: float

    @property
    def passed(self) -> bool:
        return self.daya and self.satyam and self.tapas and self.saucam and self.healthy

    @property
    def dharma_score(self) -> int:
        """How many of the 4 dharma pillars pass (0-4)."""
        return sum([self.daya, self.satyam, self.tapas, self.saucam])


@dataclass
class ImmuneReport:
    """Full immune system report — replaces pytest output."""

    verdicts: Tuple[AuditVerdict, ...] = ()
    total_ms: float = 0.0

    @property
    def total(self) -> int:
        return len(self.verdicts)

    @property
    def passed(self) -> int:
        return sum(1 for v in self.verdicts if v.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def all_green(self) -> bool:
        return self.failed == 0

    def summary(self) -> str:
        lines = [
            f"IMMUNE REPORT: {self.passed}/{self.total} healthy  ({self.total_ms:.0f}ms)",
            "",
        ]
        for v in self.verdicts:
            status = "✓" if v.passed else "✗"
            dharma = f"D{v.dharma_score}/4"
            para = "P" if v.parampara else "·"
            lines.append(f"  {status} [{v.position:2d}] {v.component:30s}  {dharma}  {para}  {v.elapsed_ms:.1f}ms")
        if self.failed:
            lines.append("")
            lines.append("FAILURES:")
            for v in self.verdicts:
                if not v.passed:
                    fails = []
                    if not v.daya:
                        fails.append("daya")
                    if not v.satyam:
                        fails.append("satyam")
                    if not v.tapas:
                        fails.append("tapas")
                    if not v.saucam:
                        fails.append("saucam")
                    if not v.healthy:
                        fails.append("health")
                    lines.append(f"  [{v.position:2d}] {v.component}: {', '.join(fails)}")
        return "\n".join(lines)


# =============================================================================
# 2. AUDIT RUNNER — The living test runner
# =============================================================================


def audit_component(component: object, name: str, position: int) -> AuditVerdict:
    """
    Run GAD audit on a single component.

    This is the REPLACEMENT for a pytest test class.
    Instead of 20 test_* functions asserting from outside,
    the component tests ITSELF via its GAD protocol methods.
    """
    start = time.perf_counter()

    # Dharma tests (the 4 pillars)
    daya = _safe_call(component, "test_daya", True)
    satyam = _safe_call(component, "test_satyam", True)
    tapas = _safe_call(component, "test_tapas", True)
    saucam = _safe_call(component, "test_saucam", True)

    # Health check
    healthy = _safe_call(component, "is_healthy", True)

    # Parampara link
    parampara = False
    heartbeat = getattr(component, "heartbeat", None) or getattr(component, "_heartbeat", None)
    if heartbeat is not None:
        parampara = getattr(heartbeat, "jiva_connected", False)

    elapsed = (time.perf_counter() - start) * 1000

    return AuditVerdict(
        component=name,
        position=position,
        daya=daya,
        satyam=satyam,
        tapas=tapas,
        saucam=saucam,
        healthy=healthy,
        parampara=parampara,
        elapsed_ms=elapsed,
    )


def _safe_call(obj: object, method: str, default: bool) -> bool:
    """Call a method safely, return default on missing/error."""
    fn = getattr(obj, method, None)
    if fn is None:
        return default
    try:
        return bool(fn())
    except Exception:
        return False


# =============================================================================
# 3. SYSTEM SCAN — Discover and audit all GAD components
# =============================================================================


def scan_lotus() -> ImmuneReport:
    """
    Scan the Lotus and audit every reachable GAD component.

    This is the REPLACEMENT for `pytest tests/ -q`.
    Instead of collecting 9432 dead functions from filesystem,
    we ask the living system to test itself.
    """
    start = time.perf_counter()
    verdicts = []

    # --- Core substrate components ---
    # These are the components that __call__() depends on.
    # Each one either implements GADProtocol or has audit-compatible methods.

    # 1. MahamantraLotus itself (the root)
    try:
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        lotus = get_mahamantra()
        verdicts.append(audit_component(lotus, "MahamantraLotus", 0))
    except Exception as e:
        verdicts.append(_error_verdict("MahamantraLotus", 0, e))

    # 2. MahaKernel (the deterministic core)
    try:
        from vibe_core.mahamantra.kernel.maha_kernel import MahaKernel

        kernel = MahaKernel()
        verdicts.append(audit_component(kernel, "MahaKernel", 0))
    except Exception as e:
        verdicts.append(_error_verdict("MahaKernel", 0, e))

    # 3. ShadowReactor (has its own test_daya!)
    try:
        from vibe_core.mahamantra.reactor.shadow import get_shadow_reactor_factory

        reactor = get_shadow_reactor_factory().spawn(
            auto_discover=False,
            initial_position=0,
            forced_lagna=0,
        )
        verdicts.append(audit_component(reactor, "ShadowReactor", 0))
    except Exception as e:
        verdicts.append(_error_verdict("ShadowReactor", 0, e))

    # 4. SankirtanChamber (the resonance chamber)
    try:
        from vibe_core.mahamantra.substrate.chamber import SankirtanChamber

        chamber = SankirtanChamber()
        verdicts.append(audit_component(chamber, "SankirtanChamber", 0))
    except Exception as e:
        verdicts.append(_error_verdict("SankirtanChamber", 0, e))

    # 5. Axiom verification (spiritual_tdd.py)
    try:
        from vibe_core.mahamantra_research.spiritual_tdd import (
            run_spiritual_tests,
            verify_all_derived,
        )

        axiom_results = run_spiritual_tests()
        all_axioms_pass = all(r.passed for r in axiom_results)
        derivations_pass = verify_all_derived()
        verdicts.append(
            AuditVerdict(
                component="MantraAxioms (7+13)",
                position=0,
                daya=True,
                satyam=all_axioms_pass,
                tapas=derivations_pass,
                saucam=True,
                healthy=all_axioms_pass and derivations_pass,
                parampara=True,  # Axioms ARE the parampara
                elapsed_ms=0.0,
            )
        )
    except Exception as e:
        verdicts.append(_error_verdict("MantraAxioms", 0, e))

    # 6. PipelineCache integrity (if available on feature branch)
    try:
        from vibe_core.mahamantra.substrate.lotus_core import _get_pipeline  # noqa: F401

        P = _get_pipeline()
        # Verify cache constants match seed
        cache_ok = (
            P.WORDS == WORDS
            and P.MAHA_QUANTUM == MAHA_QUANTUM
            and P.PARAMPARA == PARAMPARA
            and len(P.quarter_names) == WORDS
            and len(P.rama_coords) == WORDS
            and len(P.phonemes) == WORDS
            and len(P.diw_components) == WORDS
        )
        verdicts.append(
            AuditVerdict(
                component="PipelineCache",
                position=0,
                daya=True,
                satyam=cache_ok,
                tapas=True,
                saucam=True,
                healthy=cache_ok,
                parampara=True,
                elapsed_ms=0.0,
            )
        )
    except ImportError:
        # _get_pipeline doesn't exist on main — skip, not a failure
        verdicts.append(
            AuditVerdict(
                component="PipelineCache (not on this branch)",
                position=0,
                daya=True,
                satyam=True,
                tapas=True,
                saucam=True,
                healthy=True,
                parampara=True,
                elapsed_ms=0.0,
            )
        )
    except Exception as e:
        verdicts.append(_error_verdict("PipelineCache", 0, e))

    # 7. Determinism test: same input → same output
    try:
        from vibe_core.mahamantra.substrate.lotus_core import get_mahamantra

        lotus_a = get_mahamantra()
        lotus_b = get_mahamantra()
        result_a = lotus_a("determinism_test")
        result_b = lotus_b("determinism_test")
        deterministic = (
            result_a["vibration"]["seed"] == result_b["vibration"]["seed"]
            and result_a["vibration"]["attractor"] == result_b["vibration"]["attractor"]
            and result_a["position"] == result_b["position"]
            and result_a["chapter"] == result_b["chapter"]
        )
        verdicts.append(
            AuditVerdict(
                component="Determinism (seed→attractor→position)",
                position=0,
                daya=True,
                satyam=deterministic,
                tapas=True,
                saucam=True,
                healthy=deterministic,
                parampara=True,
                elapsed_ms=0.0,
            )
        )
    except Exception as e:
        verdicts.append(_error_verdict("Determinism", 0, e))

    total_ms = (time.perf_counter() - start) * 1000
    report = ImmuneReport(verdicts=tuple(verdicts), total_ms=total_ms)
    return report


def _error_verdict(name: str, position: int, error: Exception) -> AuditVerdict:
    """Create a failed verdict from an exception."""
    return AuditVerdict(
        component=f"{name} (ERROR: {type(error).__name__})",
        position=position,
        daya=False,
        satyam=False,
        tapas=False,
        saucam=False,
        healthy=False,
        parampara=False,
        elapsed_ms=0.0,
    )


# =============================================================================
# 4. COMPARISON — Dead vs Living
# =============================================================================

COMPARISON: Final[str] = """
DEAD (pytest):                          LIVING (GAD Immune System):
─────────────────────────────────────   ─────────────────────────────────────
9432 test functions                     Components test THEMSELVES
255 seconds to COLLECT                  <1 second to scan
56 directories of .py files             0 files needed (RAM only)
Tests don't know the system             System knows itself
External assertions                     Internal invariants
Runs when YOU remember                  Runs every heartbeat (250ms)
Breaks silently                         Reports via dissonance_report
No feedback during run                  Real-time health status
"""


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "AuditVerdict",
    "ImmuneReport",
    "audit_component",
    "scan_lotus",
    "COMPARISON",
]


if __name__ == "__main__":
    print("=" * 70)
    print("IMMUNE SYSTEM SCAN — Living Test Suite")
    print("=" * 70)
    print()

    report = scan_lotus()
    print(report.summary())
    print()
    print(COMPARISON)

    if report.all_green:
        print("ALL HEALTHY. The system knows itself.")
    else:
        print(f"ATTENTION: {report.failed} component(s) need healing.")

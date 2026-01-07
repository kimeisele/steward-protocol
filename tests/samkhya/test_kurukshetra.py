import time
from typing import List

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.protocols.substrate import MantraOpCode
from vibe_core.protocols.universal import AlignmentScore, SovereignContext


# --- INSTRUMENTED KERNEL (NO MOCKS) ---
class InstrumentedKernel(RealVibeKernel):
    """
    A Kernel wrapper that exposes internal state for testing
    without using MagicMock.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.genes_bound = []
        self.dharma_performed = 0

    def bind_genes(self, gene_names: List[str]) -> bool:
        """Instrumented bind_genes."""
        self.genes_bound.extend(gene_names)
        return True

    async def perform_dharma(self, context: SovereignContext) -> dict:
        """Instrumented perform_dharma."""
        self.dharma_performed += 1
        return {"status": "performed"}


# --- SABOTEUR (NO MOCKS) ---
def saboteur_handler(ctx: SovereignContext) -> bool:
    """A real function that causes Aparadha."""
    raise Exception("Sabotage! Ledger Corrupted")


class TestKurukshetra:
    """
    KURUKSHETRA WAR SIMULATION
    Hardening the Universal Protocol against Maya.

    RULES:
    1. No Mocks.
    2. Real Objects.
    3. Real Consequences.
    """

    @pytest.fixture
    def kernel(self):
        """Boot a headless instrumented kernel for battle."""
        # Use :memory: ledger for speed
        k = InstrumentedKernel(test_mode=True, load_plugins=False, ledger_path=":memory:")
        return k

    @pytest.mark.asyncio
    async def test_identity_spoofing_attack(self, kernel):
        """
        SCENARIO: An Asura tries to chant the Mantra with a fake Identity.
        EXPECTATION: The Watchdog bites (returns False).
        """
        # 1. Create Fake Identity (Asura)
        asura_ctx = SovereignContext(identity_id="ASURA_KING", signature="FAKE_SIG", roles=["impostor"])

        # 2. Try to Chant
        # The LOAD_ROOT handler checks ctx.identity_id == kernel.sovereign_context.identity_id
        is_aligned = kernel.watchdog.chant_mahamantra(asura_ctx)

        # 3. Verify Rejection
        assert is_aligned is False, "❌ FATAL: Asura was allowed to chant!"
        print("\n🛡️  Identity Spoofing Blocked (Asura Denied)")

    @pytest.mark.asyncio
    async def test_broken_vow_auditor_failure(self, kernel):
        """
        SCENARIO: The Auditor (Immune System) raises an alarm during ASSERT_TRUTH.
        EXPECTATION: The Mantra cycle breaks immediately.
        """
        # Inject Saboteur into the Handler Map
        kernel.watchdog._handlers[MantraOpCode.ASSERT_TRUTH] = saboteur_handler

        # Try to Chant with valid context
        is_aligned = kernel.watchdog.chant_mahamantra(kernel.sovereign_context)

        # Verify Failure
        assert is_aligned is False, "❌ FATAL: Mantra continued despite Broken Vow!"
        print("\n🛡️  Broken Vow Detected (Auditor Failure halted Mantra)")

    @pytest.mark.asyncio
    async def test_japa_endurance_108(self, kernel):
        """
        SCENARIO: High-frequency Chanting (108 Beads).
        EXPECTATION: Zero Drift. Perfect Alignment.
        """
        beads = 108
        start_time = time.time()

        # Perform Japa
        score: AlignmentScore = kernel.watchdog.chant_round(beads)

        duration = time.time() - start_time

        # Verify
        assert score.score == 1.0, f"❌ Drift Detected: Score {score.score}"
        assert score.status == "ALIGNED", f"❌ Status Lost: {score.status}"
        assert kernel.watchdog._beads_chanted == beads

        print(f"\n📿 Japa Endurance Passed: {beads} beads in {duration:.4f}s (Score: {score.score})")

    @pytest.mark.asyncio
    async def test_pathogen_injection(self, kernel):
        """
        SCENARIO: Verify the 'Positive Pathogen' (Gene Binding).
        EXPECTATION: bind_genes is called during the Mantra cycle.
        """
        # Clear state
        kernel.genes_bound = []

        # Chant once
        success = kernel.watchdog.chant_mahamantra(kernel.sovereign_context)

        assert success is True, "Chanting failed unexpectedly"

        # Verify BIND_CTX triggered bind_genes
        assert len(kernel.genes_bound) > 0, "❌ Pathogen Failed: No genes bound"
        assert "scribe" in kernel.genes_bound, "❌ Pathogen Failed: 'scribe' gene missing"

        print("\n🧬 Pathogen Injection Verified (Genes Bound)")


import asyncio

import pytest

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.ledger import InMemoryLedger


class TestEntropyLeak:
    def test_ledger_infinite_growth(self):
        """
        PROOF OF DEFECT: Karmic Debt (Infinite Memory Growth).
        
        Requirement: The system must recycle entropy (Garbage Collection / Pruning).
        Reality: InMemoryLedger just appends forever.
        
        We push 2000 events.
        We assert that the ledger size is capped (e.g., to 1000 or 1500).
        
        This test will FAIL on the current codebase.
        """

        # 1. Setup Kernel with Memory Ledger
        kernel = RealVibeKernel(ledger_path=":memory:", load_plugins=False)

        # ACTIVATE SAMSARA: We must be ALIVE (Running) to DIE (Prune)
        from vibe_core.kernel import KernelStatus
        kernel._status = KernelStatus.RUNNING

        # 2. Generate Karma (Events)
        # We access the ledger directly to speed up the test (no need for verification overhead for this proof)
        # But to be "fair", we should use the method that adds them.
        # kernel.record_verified_event just calls ledger.record_event eventually.

        EVENTS_TO_PUSH = 2000
        SAFE_LIMIT = 1500 # If we had a mechanism, it should kick in before this.

        print(f"DEBUG: Pushing {EVENTS_TO_PUSH} events...")

        for i in range(EVENTS_TO_PUSH):
            kernel.ledger.record_event(
                event_type="ENTROPY_GENERATION",
                agent_id="me",
                details={"entropy": i}
            )
            # Heartbeat (Samsara Cycle) - Trigger Pruning
            if i % 50 == 0:
                kernel.tick()

        current_size = len(kernel.ledger.get_all_events())
        print(f"DEBUG: Final Ledger Size: {current_size}")

        # ASSERTION OF TRUTH
        # The Law says: Death makes room for Life.
        # The Bug: Current Size == 2000.

        assert current_size <= SAFE_LIMIT, f"FRACTAL COLLAPSE: Loop detected. Ledger grew to {current_size}, exceeding safe limit {SAFE_LIMIT}. No Pruning occurred."

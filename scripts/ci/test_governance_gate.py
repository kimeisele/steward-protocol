#!/usr/bin/env python3
"""Verify governance gate for CI."""

from typing import Any, Dict

from vibe_core.agent_protocol import VibeAgent
from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.scheduling import Task

kernel = RealVibeKernel(ledger_path=":memory:")


# Attempt to register an agent WITHOUT oath - should fail
class UnswornAgent(VibeAgent):
    def __init__(self):
        super().__init__(agent_id="unsworn", name="Unsworn Agent")

    def process(self, task: Task) -> Dict[str, Any]:
        return {"status": "ok"}


try:
    kernel.register_agent(UnswornAgent())
    print("❌ FAILED: Governance gate allowed unsworn agent!")
    exit(1)
except Exception as e:
    print(f"✅ Governance gate working: Rejected unsworn agent with: {type(e).__name__}")

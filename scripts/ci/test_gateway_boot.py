#!/usr/bin/env python3
"""Gateway boot smoke test for CI."""

from steward.system_agents.steward.agent import StewardAgent
from vibe_core.kernel_impl import RealVibeKernel

kernel = RealVibeKernel(ledger_path=":memory:")
steward = StewardAgent(kernel)
kernel.register_agent(steward)
kernel.boot()
count = steward.discover_agents()
print(f"✅ Boot OK: Kernel running with {len(kernel.agent_registry)} agents (discovered {count})")

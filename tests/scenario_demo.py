#!/usr/bin/env python3
"""
THE AGENT CITY SIMULATION: Proof of Governance
==============================================
This script demonstrates the core loop of Agent City:
1. Autonomy: Herald tries to act.
2. Governance: Civic blocks (insufficient credits).
3. Democracy: Herald proposes, Human votes.
4. Execution: Civic transfers credits.
5. Success: Herald acts.

Run this to prove that Code is Law.
"""

import sys
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any

# --- MOCK VIBE OS KERNEL INFRASTRUCTURE ---
# In production, this is imported from vibe_core


@dataclass
class Task:
    agent_id: str
    payload: Dict[str, Any]
    id: str = "task-001"


class MockLedger:
    def record(self, event_type, details):
        print(f"📝 LEDGER: {event_type} - {details}")


class MockKernel:
    def __init__(self):
        self.ledger = MockLedger()
        self.registry = {}
        self.state = {"herald_credits": 0, "proposals": []}

    def log(self, agent, message):
        print(f"[{agent.upper()}] {message}")

    def transfer_credits(self, to_agent, amount):
        self.state[f"{to_agent}_credits"] += amount
        self.ledger.record("TRANSFER", f"{amount} credits -> {to_agent}")


# --- AGENT CITY LOGIC (Simplified for Demo) ---


class CivicAgent:
    def __init__(self, kernel):
        self.kernel = kernel

    def check_license(self, agent_id):
        credits = self.kernel.state.get(f"{agent_id}_credits", 0)
        if credits <= 0:
            self.kernel.log("CIVIC", f"❌ BLOCK: {agent_id} has 0 credits. License suspended.")
            return False
        return True


class ForumAgent:
    def __init__(self, kernel):
        self.kernel = kernel

    def create_proposal(self, title, proposer):
        prop_id = f"PROP-{len(self.kernel.state['proposals']) + 1:03d}"
        proposal = {
            "id": prop_id,
            "title": title,
            "proposer": proposer,
            "status": "OPEN",
        }
        self.kernel.state["proposals"].append(proposal)
        self.kernel.log("FORUM", f"🗳️  NEW PROPOSAL {prop_id}: '{title}' by {proposer}")
        return prop_id

    def vote(self, prop_id, vote):
        self.kernel.log("FORUM", f"👤 VOTE RECEIVED: {vote} on {prop_id}")
        if vote == "YES":
            self.kernel.log("FORUM", f"✅ PROPOSAL {prop_id} PASSED!")
            return True
        return False


class HeraldAgent:
    def __init__(self, kernel, civic, forum):
        self.kernel = kernel
        self.civic = civic
        self.forum = forum

    def try_post(self, content):
        self.kernel.log("HERALD", f"Attempting to post: '{content}'")

        # 1. Check Governance
        if not self.civic.check_license("herald"):
            # 2. Autonomic Response
            self.kernel.log("HERALD", "⚠️  Bankrupt. Initiating bailout protocol...")
            prop_id = self.forum.create_proposal("Emergency Grant 50 Credits", "herald")
            return {"status": "BLOCKED", "proposal": prop_id}

        # 3. Success
        self.kernel.log("HERALD", f"🦅 POSTED: {content}")
        self.kernel.ledger.record("BROADCAST", content)
        return {"status": "SUCCESS"}


# --- THE SIMULATION SCENARIO ---


def run_scenario():
    print("\n🏙️  INITIATING AGENT CITY SIMULATION...\n" + "=" * 40)

    # Boot
    kernel = MockKernel()
    civic = CivicAgent(kernel)
    forum = ForumAgent(kernel)
    herald = HeraldAgent(kernel, civic, forum)

    time.sleep(1)

    # ACT 1: THE FAILURE
    print("\n🎬 ACT 1: THE CONSTRAINT")
    result = herald.try_post("Hello World from Agent City!")

    if result["status"] == "BLOCKED":
        prop_id = result["proposal"]

        time.sleep(1)

        # ACT 2: THE DEMOCRACY
        print("\n🎬 ACT 2: THE INTERVENTION")
        print(f"⚠️  System Halted. Proposal {prop_id} pending.")
        choice = input(f"❓ Steward, do you approve {prop_id}? (y/n): ")

        if choice.lower() == "y":
            passed = forum.vote(prop_id, "YES")
            if passed:
                print("\n🎬 ACT 3: THE EXECUTION")
                kernel.transfer_credits("herald", 50)

                # Retry
                herald.try_post("Hello World from Agent City!")
                print("\n✅ SCENARIO COMPLETE: System recovered autonomously.")
        else:
            print("\n❌ VOTE FAILED. Herald remains silent.")


if __name__ == "__main__":
    run_scenario()

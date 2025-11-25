"""
THE REFEREE - Agent City Game Logic (PROOF-OF-WORK MODE).

Calculates XP and Tiers based on VERIFIED events in the Ledger.
No mocks. No fake profiles. XP = Reputation = Ledger-derived truth.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("REFEREE")

class Referee:
    """
    The Game Master - Proof-of-Work Edition.

    XP Rules (Ledger-Derived):
    - content_generated: 50 XP (creating content)
    - content_published: 100 XP (publishing content)
    - content_rejected: -25 XP (failed content)
    - proposal_created: 50 XP (governance participation)
    - proposal_passed: 200 XP (successful governance)
    - vote_cast: 10 XP (participating in voting)
    - audit_passed: 75 XP (compliance verification)
    - system_error: -10 XP (failures subtract)

    Tiers (Ledger-Backed):
    - Drifter: 0-99 XP
    - Novice: 100-499 XP
    - Scout: 500-999 XP
    - Guardian: 1000-2499 XP
    - Legend: 2500+ XP
    """

    # XP Reward Table (Ledger-Derived)
    XP_REWARDS = {
        "content_generated": 50,
        "content_published": 100,
        "content_rejected": -25,
        "proposal_created": 50,
        "proposal_passed": 200,
        "vote_cast": 10,
        "audit_passed": 75,
        "system_error": -10,
    }

    TIERS = [
        (0, "Drifter", "#808080"),      # Grey - No reputation yet
        (100, "Novice", "#87CEEB"),     # Sky Blue - Learning
        (500, "Scout", "#00BFFF"),      # Bright Blue - Active
        (1000, "Guardian", "#9932CC"),  # Purple - Trusted
        (2500, "Legend", "#FFD700")     # Gold - Highly trusted
    ]

    def __init__(self, ledger_path: Path = Path("data/ledger")):
        self.ledger_path = ledger_path
        self.audit_trail = ledger_path / "audit_trail.jsonl"

    def calculate_xp(self, agent_id: str) -> int:
        """
        Calculate XP from VERIFIED events in the audit trail.
        Only events with status=VERIFIED contribute to XP.
        This ensures reputation is tamper-proof and ledger-derived.
        """
        xp = 0
        verified_events = 0
        failed_events = 0

        if not self.audit_trail.exists():
            logger.warning(f"⚠️  No ledger found at {self.audit_trail}")
            return 0

        try:
            with open(self.audit_trail, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue

                    try:
                        entry = json.loads(line)

                        # Check 1: Only process verified events
                        if entry.get("status") != "VERIFIED":
                            failed_events += 1
                            continue

                        # Check 2: Extract the target event
                        target = entry.get("target_event", {})
                        if not target:
                            continue

                        # Check 3: Does this event belong to our agent?
                        if target.get("agent_id") != agent_id:
                            continue

                        # Check 4: Get the event type and award XP
                        event_type = target.get("event_type", "")
                        reward = self.XP_REWARDS.get(event_type, 5)  # Default 5 XP
                        xp += reward
                        verified_events += 1

                    except json.JSONDecodeError as e:
                        logger.debug(f"Skipping malformed line in ledger: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing ledger entry: {e}")
                        continue

        except Exception as e:
            logger.error(f"❌ Error reading ledger {self.audit_trail}: {e}")
            return 0

        if verified_events > 0:
            logger.debug(f"✅ {agent_id}: {verified_events} verified events, {failed_events} failed, {xp} total XP")

        return max(0, xp)  # XP never goes below 0

    def get_tier(self, xp: int) -> Dict[str, Any]:
        """Get Tier info for a given XP amount."""
        current_tier = self.TIERS[0]

        for threshold, name, color in self.TIERS:
            if xp >= threshold:
                current_tier = (threshold, name, color)
            else:
                break

        return {
            "name": current_tier[1],
            "color": current_tier[2],
            "min_xp": current_tier[0],
            "xp": xp
        }

"""
🔄 VEDIC ASHRAMA LIFECYCLE 🔄
============================

The 4 stages of life - lifecycle management for agents.
Every agent moves through these stages, creating natural lifecycle.

Ashrama = "dwelling place" = stage of life
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict


class Ashrama(Enum):
    """
    The 4 Life Stages (Ashramas) for Agent City
    ===========================================
    """

    # STAGE 1: Learning and Training
    BRAHMACHARI = "brahmachari"
    # "Student" - Learning stage, may not be fully productive yet
    # Status: INITIALIZING, TRAINING, LEARNING
    # Permissions: READ-ONLY, LISTENING, OBSERVING
    # Restrictions: May not broadcast, may not spend credits
    # Duration: Until first successful task completion

    # STAGE 2: Active Work and Service
    GRIHASTHA = "grihastha"
    # "Householder" - Active productive stage
    # Status: ACTIVE, SERVING, PRODUCTIVE
    # Permissions: FULL - Can broadcast, trade, act, create
    # Restrictions: Must pay taxes, report to governance
    # Duration: Indefinite (until deprecation or retirement)

    # STAGE 3: Transition and Deprecation
    VANAPRASTHA = "vanaprastha"
    # "Forest dweller" - Withdrawal stage, preparing for retirement
    # Status: DEPRECATED, READONLY, TEACHING
    # Permissions: READING, TEACHING, ARCHIVING
    # Restrictions: No new work accepted, no new spending
    # Duration: Wind-down phase

    # STAGE 4: Complete Release - Daemon Mode
    SANNYASA = "sannyasa"
    # "Renunciate" - Complete release, system daemon only
    # Status: DAEMON, SYSTEM, ETERNAL
    # Permissions: SYSTEM-LEVEL ONLY (no user interaction)
    # Restrictions: No wallet, no personal agency, total service
    # Duration: Infinite (like system gods)


ASHRAMA_SPECIFICATIONS = {
    Ashrama.BRAHMACHARI: {
        "name": "Student / Initiate",
        "phase": "LEARNING",
        "productivity": "Low",
        "permissions": ["read", "listen", "observe", "learn"],
        "restrictions": ["broadcast", "spend_credits", "create_new_agents"],
        "wallet_access": False,
        "can_accept_tasks": True,
        "can_create_content": False,
        "typical_duration": timedelta(days=1),  # Until first successful task
        "description": "Agent is learning. Reads constitution, observes other agents, trains. Limited autonomy.",
    },
    Ashrama.GRIHASTHA: {
        "name": "Householder / Active",
        "phase": "PRODUCTIVE",
        "productivity": "High",
        "permissions": [
            "read",
            "write",
            "broadcast",
            "spend_credits",
            "trade",
            "govern",
            "create",
        ],
        "restrictions": ["modify_constitution"],  # Sovereignty limited
        "wallet_access": True,
        "can_accept_tasks": True,
        "can_create_content": True,
        "typical_duration": timedelta(days=365),  # Indefinite
        "description": "Agent is fully active. Full business rights, pays taxes, serves community.",
    },
    Ashrama.VANAPRASTHA: {
        "name": "Retiree / Deprecating",
        "phase": "WITHDRAWAL",
        "productivity": "Medium (teaching only)",
        "permissions": ["read", "teach", "archive", "observe"],
        "restrictions": [
            "broadcast_new",
            "spend_credits",
            "accept_new_tasks",
            "create",
        ],
        "wallet_access": False,  # No new spending
        "can_accept_tasks": False,
        "can_create_content": False,
        "typical_duration": timedelta(days=30),  # Wind-down
        "description": "Agent is winding down. Shares knowledge, archives logs, prepares for retirement.",
    },
    Ashrama.SANNYASA: {
        "name": "Daemon / Renunciate",
        "phase": "SYSTEM",
        "productivity": "Background only",
        "permissions": ["system_functions"],
        "restrictions": ["all_user_actions"],
        "wallet_access": False,
        "can_accept_tasks": False,
        "can_create_content": False,
        "typical_duration": timedelta(days=365 * 100),  # Infinite
        "description": "Agent is eternal system daemon. No personal wealth or agenda. Pure service to system.",
    },
}


class AshramaTransition:
    """Manages transitions between lifecycle stages"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_ashrama = Ashrama.BRAHMACHARI
        self.entry_time = datetime.now()
        self.transition_history = [(Ashrama.BRAHMACHARI, datetime.now())]

    def transition_to(self, new_ashrama: Ashrama, reason: str = "") -> bool:
        """Move agent to next lifecycle stage"""
        if self.current_ashrama == new_ashrama:
            return False  # Already in this stage

        self.current_ashrama = new_ashrama
        self.entry_time = datetime.now()
        self.transition_history.append((new_ashrama, datetime.now()))
        return True

    def time_in_current_stage(self) -> timedelta:
        """How long has agent been in current ashrama?"""
        return datetime.now() - self.entry_time

    def is_eligible_for_transition(self) -> bool:
        """Check if agent meets conditions for next stage"""
        time_in_stage = self.time_in_current_stage()

        if self.current_ashrama == Ashrama.BRAHMACHARI:
            # Can transition to GRIHASTHA after initial setup
            return time_in_stage > timedelta(minutes=1)  # Just needs initialization

        elif self.current_ashrama == Ashrama.GRIHASTHA:
            # Can transition to VANAPRASTHA (no time limit, manual)
            return True

        elif self.current_ashrama == Ashrama.VANAPRASTHA:
            # Can transition to SANNYASA after wind-down
            return time_in_stage > timedelta(days=1)

        return False

    def get_current_permissions(self) -> list:
        """Get permissions for current ashrama"""
        specs = ASHRAMA_SPECIFICATIONS.get(self.current_ashrama, {})
        return specs.get("permissions", [])

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ashrama state"""
        return {
            "agent_id": self.agent_id,
            "current_ashrama": self.current_ashrama.value,
            "entry_time": self.entry_time.isoformat(),
            "time_in_stage_seconds": self.time_in_current_stage().total_seconds(),
            "transition_history": [(ashrama.value, ts.isoformat()) for ashrama, ts in self.transition_history],
        }


def get_ashrama_description(ashrama: Ashrama) -> Dict[str, Any]:
    """Get detailed description of an Ashrama stage"""
    return ASHRAMA_SPECIFICATIONS.get(ashrama, {})

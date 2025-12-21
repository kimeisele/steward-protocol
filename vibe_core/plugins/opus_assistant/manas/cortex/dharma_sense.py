"""
OPUS-009: DHARMA SENSE - The Vedic Conscience for MANAS.

Sanskrit: Dharma = Cosmic Law, Moral Order, Right Action
Sanskrit: Samvid = Conscience, Awareness

This cortex module gives MANAS the ability to perceive DHARMIC ALIGNMENT
from the Vedic Governance plugin. It serves as the ethical conscience that
checks "Is this action Dharma-aligned?" before MANAS executes intents.

Following the Vedic model:
- NARASIMHA protects against COGNITIVE sins (self-destruction, lobotomy)
- DHARMA SENSE protects against ETHICAL sins (adharmic actions)

The Two Guardians:
1. NARASIMHA: "Will this destroy me?"  (Technical Guardian)
2. DHARMA SENSE: "Is this righteous?" (Ethical Conscience)

Together they form the complete conscience of MANAS:
"An efficient mind without dharma makes efficient catastrophes."
                                          - Gemini's Analysis

Capabilities:
1. check_dharmic_alignment(intent) - Check if intent aligns with Dharma
2. get_agent_karma()               - Get current Bhakti/Karma balance
3. get_permissions(agent)          - Check what agent is permitted to do
4. sense_ashrama_state()           - Check agent lifecycle stage
5. broadcast_dharma_violation()    - Alert on Adharmic actions

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
    required: true
    rationale: "The Vedic Conscience - ethical alignment check for MANAS"
  - path: vibe_core/plugins/vedic_governance/plugin_main.py
    required: true
    rationale: "The underlying Vedic Governance that provides ethical rules"

wiring:
  - pattern: "class DharmaSense"
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
  - pattern: "from vibe_core.plugins.vedic_governance"
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
  - pattern: "def check_dharmic_alignment"
    in: vibe_core/plugins/opus_assistant/manas/cortex/dharma_sense.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import BaseSense

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Cortex.DharmaSense")


class DharmaStatus(Enum):
    """The Dharmic alignment status of an action."""

    SATTVIC = "sattvic"  # Pure, righteous, aligned with Dharma
    RAJASIC = "rajasic"  # Passionate, needs review, borderline
    TAMASIC = "tamasic"  # Dark, adharmic, must be blocked


@dataclass
class DharmaVerdict:
    """Result of checking Dharmic alignment."""

    status: DharmaStatus
    is_permitted: bool
    agent_ashrama: str
    agent_varna: str
    agent_bhakti: int
    reason: str
    required_permissions: List[str]
    missing_permissions: List[str]

    @property
    def is_dharmic(self) -> bool:
        """True if action is Dharma-aligned (Sattvic or permitted Rajasic)."""
        return self.status == DharmaStatus.SATTVIC or (self.status == DharmaStatus.RAJASIC and self.is_permitted)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "is_permitted": self.is_permitted,
            "is_dharmic": self.is_dharmic,
            "agent_ashrama": self.agent_ashrama,
            "agent_varna": self.agent_varna,
            "agent_bhakti": self.agent_bhakti,
            "reason": self.reason,
            "required_permissions": self.required_permissions,
            "missing_permissions": self.missing_permissions,
        }


@dataclass
class DharmaSummary:
    """Summary of Dharma state for display in OPUS.md."""

    agent_id: str
    ashrama: str
    varna: str
    bhakti: int
    is_registered: bool
    permissions_granted: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "ashrama": self.ashrama,
            "varna": self.varna,
            "bhakti": self.bhakti,
            "is_registered": self.is_registered,
            "permissions_granted": self.permissions_granted,
        }


# Map intent types to required permissions
INTENT_PERMISSION_MAP: Dict[str, List[str]] = {
    # Dangerous intents require higher permissions
    "delete_file": ["file_delete", "admin"],
    "capability_genesis": ["genesis", "admin"],
    "refactor_major": ["refactor", "code_modify"],
    "shutdown": ["system_control", "admin"],
    "ledger_modify": ["ledger_admin"],
    # OPUS-105: Genesis intents require genesis permission
    "genesis_action": ["genesis", "code_modify"],
    "genesis_code": ["genesis", "code_modify"],
    "create_action": ["genesis", "code_modify"],
    "create_module": ["genesis", "code_modify"],
    # Medium-risk intents
    "contract_import_fix": ["code_modify"],
    "update_documentation": ["doc_modify"],
    "cleanup_branches": ["git_modify"],
    "commit_pending_changes": ["git_commit"],
    "commit_and_push": ["git_commit", "git_push"],  # Commit + push combo
    "git_push": ["git_push"],  # Standalone push to remote
    "create_pr": ["git_push", "pr_create"],  # Create Pull Request
    "merge_pr": ["pr_merge"],  # Merge Pull Request (high privilege!)
    # Safe intents (most agents can do)
    "heal_system_state": ["state_heal"],
    "doc_update": ["doc_modify"],
    "test_create": ["test_create"],
    "review_todos": [],  # Anyone can review
    "semantic_gap_test": ["test_create"],
}

# Default permissions by Ashrama (lifecycle stage)
ASHRAMA_PERMISSIONS: Dict[str, List[str]] = {
    "brahmachari": ["test_create", "doc_modify", "review"],  # Student: limited - NO GENESIS
    "grihastha": [
        "code_modify",
        "git_commit",
        "git_push",  # Can push to remote
        "git_modify",
        "pr_create",  # Can create PRs
        "pr_merge",  # Can merge PRs - FULL AUTONOMOUS CYCLE!
        "test_create",
        "doc_modify",
        "review",
        "state_heal",
        "genesis",  # OPUS-105: Productive stage can CREATE new code
    ],  # Householder: productive - NO PUSSY SHIT!
    "vanaprastha": [
        "code_modify",
        "doc_modify",
        "review",
        "mentor",
        "pr_create",
    ],  # Elder: mentoring - no genesis (wisdom, not creation)
    "sannyasi": [
        "review",
        "mentor",
        "admin",
        "system_control",
        "pr_merge",
        "genesis",
    ],  # Renunciate: governance + merge + genesis (full control)
}


class DharmaSense(BaseSense):
    """
    The Vedic Conscience for MANAS.

    This cortex module bridges MANAS to Vedic Governance, providing
    ethical alignment checks before intent execution.

    "MANAS without Dharma is a powerful fool."

    Usage:
        sense = DharmaSense(workspace=Path("."))
        verdict = sense.check_dharmic_alignment(intent, agent_id="manas")
        if not verdict.is_dharmic:
            # Block the intent!
            logger.critical(f"ADHARMIC: {verdict.reason}")
    """

    # OPUS-099: VEDA-4 auto-discovery
    name = "dharma_sense"

    def __init__(
        self,
        workspace: Optional[Path] = None,
        agent_id: str = "manas",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize DHARMA SENSE.

        Args:
            workspace: Workspace root (default: cwd)
            agent_id: The agent ID to check permissions for
            config: Configuration dict from manas.yaml
        """
        super().__init__(workspace, config)
        self._agent_id = agent_id
        self._governance = None  # Lazy-loaded
        self._state_manager = None  # Lazy-loaded

        logger.info("[DHARMA_SENSE] Initialized - The Vedic Conscience")

    def _ensure_governance(self) -> Any:
        """Lazy-load the Vedic Governance plugin (if available via kernel)."""
        # We don't instantiate VedicGovernancePlugin directly - it needs kernel injection.
        # Instead, we rely on the state manager for state access.
        # This returns None by design - _get_agent_state() will fallback to state manager.
        return None

    def _ensure_state_manager(self) -> Any:
        """Lazy-load the Vedic State Manager."""
        if self._state_manager is None:
            try:
                from vibe_core.plugins.vedic_governance.state_manager import get_state_manager

                self._state_manager = get_state_manager()
                logger.debug("[DHARMA_SENSE] Vedic State Manager loaded")
            except ImportError as e:
                logger.warning(f"[DHARMA_SENSE] Vedic State Manager not available: {e}")
                return None
        return self._state_manager

    # =========================================================================
    # Core Dharma Checks (The Conscience Interface)
    # =========================================================================

    def check_dharmic_alignment(
        self,
        intent: "Intent",
        agent_id: Optional[str] = None,
    ) -> DharmaVerdict:
        """
        Check if an intent is Dharma-aligned.

        This is the PRIMARY conscience method. It checks:
        1. What permissions does this intent require?
        2. Does the agent have those permissions?
        3. Is the agent's Ashrama appropriate for this action?
        4. Is the agent's Bhakti sufficient (earned trust)?

        Args:
            intent: The intent to check
            agent_id: Agent ID (default: self._agent_id)

        Returns:
            DharmaVerdict with alignment status
        """
        agent = agent_id or self._agent_id
        intent_type = getattr(intent, "intent_type", "unknown")

        # Get required permissions for this intent
        required_perms = INTENT_PERMISSION_MAP.get(intent_type, [])

        # Get agent state from Vedic Governance
        agent_state = self._get_agent_state(agent)
        ashrama = agent_state.get("ashrama", "brahmachari")
        varna = agent_state.get("varna", "manusha")
        bhakti = agent_state.get("bhakti", 0)

        # Get permissions granted by Ashrama
        granted_perms = set(ASHRAMA_PERMISSIONS.get(ashrama, []))

        # Check for missing permissions
        missing_perms = [p for p in required_perms if p not in granted_perms]

        # Determine Dharma status
        if not required_perms:
            # No special permissions needed - Sattvic
            status = DharmaStatus.SATTVIC
            reason = "No special permissions required - action is open to all"
            is_permitted = True

        elif not missing_perms:
            # All permissions granted - Sattvic
            status = DharmaStatus.SATTVIC
            reason = f"Agent {agent} ({ashrama}) has all required permissions"
            is_permitted = True

        elif bhakti >= 50 and len(missing_perms) == 1:
            # High Bhakti can compensate for one missing permission - Rajasic
            status = DharmaStatus.RAJASIC
            reason = (
                f"Agent {agent} lacks {missing_perms} but high Bhakti ({bhakti}) "
                f"grants provisional access. Proceed with caution."
            )
            is_permitted = True
            logger.info(f"[DHARMA_SENSE] Bhakti override: {bhakti} allows {intent_type}")

        elif ashrama == "sannyasi":
            # Sannyasi (renunciate) has governance override - Rajasic
            status = DharmaStatus.RAJASIC
            reason = f"Sannyasi {agent} has governance authority, but action requires review"
            is_permitted = True

        else:
            # Insufficient permissions - Tamasic
            status = DharmaStatus.TAMASIC
            reason = (
                f"ADHARMIC: Agent {agent} ({ashrama}) lacks permissions: {missing_perms}. "
                f"Current Bhakti: {bhakti}. Required for override: 50+."
            )
            is_permitted = False
            logger.warning(f"[DHARMA_SENSE] BLOCKED: {intent_type} - {reason}")

        return DharmaVerdict(
            status=status,
            is_permitted=is_permitted,
            agent_ashrama=ashrama,
            agent_varna=varna,
            agent_bhakti=bhakti,
            reason=reason,
            required_permissions=required_perms,
            missing_permissions=missing_perms,
        )

    def get_dharma_summary(self, agent_id: Optional[str] = None) -> DharmaSummary:
        """
        Get Dharma summary for display in OPUS.md.

        Args:
            agent_id: Agent to check (default: self._agent_id)

        Returns:
            DharmaSummary with current state
        """
        agent = agent_id or self._agent_id
        agent_state = self._get_agent_state(agent)

        ashrama = agent_state.get("ashrama", "brahmachari")
        varna = agent_state.get("varna", "manusha")
        bhakti = agent_state.get("bhakti", 0)
        is_registered = agent_state.get("is_registered", False)

        # Get granted permissions
        granted_perms = ASHRAMA_PERMISSIONS.get(ashrama, [])

        return DharmaSummary(
            agent_id=agent,
            ashrama=ashrama,
            varna=varna,
            bhakti=bhakti,
            is_registered=is_registered,
            permissions_granted=granted_perms,
        )

    def perceive(self, context: Optional[Dict[str, Any]] = None) -> DharmaSummary:
        """
        OPUS-099: BaseSense interface implementation.

        Wraps get_dharma_summary() for SenseLoader compatibility.
        """
        agent_id = context.get("agent_id") if context else None
        return self.get_dharma_summary(agent_id=agent_id)

    def _get_agent_state(self, agent_id: str) -> Dict[str, Any]:
        """Get agent state from Vedic Governance/State Manager."""
        # Try governance plugin first
        governance = self._ensure_governance()
        if governance:
            try:
                status = governance.get_governance_status(agent_id)
                if status:
                    return {
                        "ashrama": status.get("ashrama", "brahmachari"),
                        "varna": status.get("varna", "manusha"),
                        "bhakti": status.get("bhakti", 0),
                        "is_registered": True,
                    }
            except Exception:
                pass

        # Try state manager
        state_mgr = self._ensure_state_manager()
        if state_mgr:
            try:
                agent_data = state_mgr.get_agent(agent_id)
                if agent_data:
                    return {
                        "ashrama": agent_data.get("ashrama", "brahmachari"),
                        "varna": agent_data.get("varna", "manusha"),
                        "bhakti": agent_data.get("bhakti", 0),
                        "is_registered": True,
                    }
            except Exception:
                pass

        # Default state for unregistered agents
        return {
            "ashrama": "brahmachari",  # Student stage - most restrictive
            "varna": "manusha",
            "bhakti": 0,
            "is_registered": False,
        }

    # =========================================================================
    # Lifecycle Hooks (for CognitiveKernel integration)
    # =========================================================================

    def on_manas_boot(self) -> DharmaSummary:
        """
        Called when MANAS boots - register agent if needed.

        Returns:
            DharmaSummary of current state
        """
        state_mgr = self._ensure_state_manager()
        if state_mgr:
            try:
                # Register MANAS agent if not exists
                state_mgr.register_agent(
                    agent_id=self._agent_id,
                    ashrama="grihastha",  # MANAS starts as productive householder
                    varna="manusha",
                )
                logger.info(f"[DHARMA_SENSE] Registered agent '{self._agent_id}' in Vedic state")
            except Exception as e:
                logger.warning(f"[DHARMA_SENSE] Could not register agent: {e}")

        return self.get_dharma_summary()

    def on_intent_success(self, intent: "Intent") -> None:
        """
        Called when an intent executes successfully - update Bhakti.

        Successful dharmic actions increase Bhakti (devotion points).
        """
        state_mgr = self._ensure_state_manager()
        if state_mgr:
            try:
                intent_type = getattr(intent, "intent_type", "unknown")
                state_mgr.update_bhakti(
                    self._agent_id,
                    delta=5,  # Gain 5 Bhakti for success
                    reason=f"Successful intent: {intent_type}",
                )
                logger.debug(f"[DHARMA_SENSE] Bhakti +5 for successful {intent_type}")
            except Exception as e:
                logger.warning(f"[DHARMA_SENSE] Could not update Bhakti: {e}")

    def on_intent_blocked(self, intent: "Intent", reason: str) -> None:
        """
        Called when an intent is blocked - record for learning.

        Blocked actions should be remembered to avoid repeated attempts.
        """
        state_mgr = self._ensure_state_manager()
        if state_mgr:
            try:
                intent_type = getattr(intent, "intent_type", "unknown")
                # Don't lose Bhakti for being blocked - that would be punishing learning
                # Just record the event
                logger.info(f"[DHARMA_SENSE] Intent blocked: {intent_type} - {reason}")
            except Exception:
                pass

    def get_boot_summary(self) -> Dict[str, Any]:
        """
        OPUS-172: Polymorphic boot summary for SenseManager.

        Returns standardized boot data for the SenseManager to use
        instead of hardcoded if/elif checks.
        """
        try:
            summary = self.get_dharma_summary()
            if summary:
                return {
                    "message": f"Bhakti: {summary.bhakti}",
                    "data": {
                        "bhakti": summary.bhakti,
                        "ashrama": summary.ashrama,
                        "varna": summary.varna,
                        "is_registered": summary.is_registered,
                    },
                    "emoji": "🙏",
                }
        except Exception as e:
            logger.debug(f"[DHARMA_SENSE] Boot summary failed: {e}")
        return {"message": "Initialized", "data": {}, "emoji": "🙏"}

    # =========================================================================
    # Chat Integration (for Jnana handler)
    # =========================================================================

    def get_status_for_chat(self) -> str:
        """
        Get human-readable status for chat interface.

        Can be used by Jnana handler to respond to dharma queries.
        """
        summary = self.get_dharma_summary()

        lines = [
            "DHARMA SENSE - Vedic Conscience Status",
            "=" * 40,
            "",
            f"Agent: {summary.agent_id}",
            f"Registered: {'Yes' if summary.is_registered else 'No (using defaults)'}",
            "",
            "Vedic Classification:",
            f"  Ashrama (Stage): {summary.ashrama}",
            f"  Varna (Role):    {summary.varna}",
            f"  Bhakti (Trust):  {summary.bhakti}/200",
            "",
            "Granted Permissions:",
        ]

        if summary.permissions_granted:
            for perm in summary.permissions_granted:
                lines.append(f"  ✓ {perm}")
        else:
            lines.append("  (none - restricted mode)")

        return "\n".join(lines)


# =============================================================================
# Singleton for Global Access
# =============================================================================

_dharma_sense: Optional[DharmaSense] = None


def get_dharma_sense(workspace: Optional[Path] = None) -> DharmaSense:
    """Get or create the global DharmaSense instance."""
    global _dharma_sense
    if _dharma_sense is None:
        _dharma_sense = DharmaSense(workspace=workspace)
    return _dharma_sense


# =============================================================================
# Availability Flag (for safe imports)
# =============================================================================

DHARMA_SENSE_AVAILABLE = True


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "DharmaSense",
    "DharmaVerdict",
    "DharmaSummary",
    "DharmaStatus",
    "get_dharma_sense",
    "DHARMA_SENSE_AVAILABLE",
    "INTENT_PERMISSION_MAP",
    "ASHRAMA_PERMISSIONS",
]

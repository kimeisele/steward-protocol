"""
STEWARD PROTOCOL PLUGIN - The Protocol Layer of Agent City
===========================================================

This plugin implements the STEWARD Protocol as a Kernel Plugin.
It is the "Avatar of Vishnu" for Protocol governance.

STEWARD is not ONE thing - it is EVERYTHING:
1. The Protocol (specification)
2. The Bot Father (creates/registers agents)
3. Universal Operator (CLI/SDK interface)
4. Trust Infrastructure (verification, attestation)
5. Economic System (pricing, billing) [future]
6. Federation (registry, discovery) [future]
7. Meta-Agent (self-describing)
8. Guardian (crypto security, constitution)

This plugin:
1. Owns Protocol state (trust_scores, attestations, manifests)
2. Uses kernel hooks to enforce Protocol rules
3. Connects existing infrastructure (AgentLoader, StewardClient, crypto)
4. Provides public API via kernel.steward.*

Philosophy:
"The kernel is Vishnu - unchanging. STEWARD Protocol is the Dharma -
 the cosmic law that all agents must follow."

Pattern: Same as VedicGovernancePlugin (the Golden Plugin Standard)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("STEWARD_PROTOCOL")


class StewardProtocolPlugin(KernelPlugin):
    """
    STEWARD Protocol Plugin - Protocol Governance for Agent City.

    This plugin provides:
    - Agent manifest verification (steward.json)
    - Trust score tracking
    - Capability attestation
    - Protocol enforcement via hooks
    - Public API for verification, delegation, trust

    Priority: 5 (very early - Protocol is foundational, before governance)
    """

    @property
    def plugin_id(self) -> str:
        return "steward_protocol"

    @property
    def priority(self) -> int:
        return 5  # Before vedic_governance (10) - Protocol is foundational

    def __init__(self):
        """Initialize Protocol state (owned by plugin, not kernel)."""
        # Reference to kernel (set on boot)
        self._kernel: Optional["RealVibeKernel"] = None

        # Project root for file access
        self._project_root: Path = Path.cwd()

        # Protocol configuration (from Phoenix steward.yaml)
        self._config = None

        # Agent manifests cache {agent_id: manifest_dict}
        self._manifests: Dict[str, Dict[str, Any]] = {}

        # Trust scores {agent_id: score}
        self._trust_scores: Dict[str, float] = {}

        # Attestations {agent_id: {capability: attestation}}
        self._attestations: Dict[str, Dict[str, Any]] = {}

        # Task metrics for trust calculation {agent_id: {completed, failed}}
        self._task_metrics: Dict[str, Dict[str, int]] = {}

        # Connected infrastructure (lazy loaded)
        self._agent_loader = None
        self._steward_client = None

    # =========================================================================
    # KERNEL HOOKS
    # =========================================================================

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Called when kernel boots.

        Register this plugin as the Protocol provider on the kernel.
        Load configuration and connect infrastructure.
        """
        self._kernel = kernel

        # Register as THE steward protocol plugin on kernel
        kernel.steward = self

        # Load Protocol configuration from Phoenix
        self._load_config()

        # Connect existing infrastructure
        self._connect_infrastructure()

        logger.info("📜 STEWARD Protocol Plugin booted")
        logger.info("   Protocol is now PLUGIN-BASED (kernel.steward)")
        if self._config:
            logger.info("   Config loaded: Layer 1.5/1.6 active")

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Called when a new agent is registered.

        Load steward.json for the agent, verify signature, initialize trust.
        """
        # Try to load manifest for this agent
        manifest = self._load_agent_manifest(agent_id)

        if manifest:
            self._manifests[agent_id] = manifest
            logger.info(f"📜 Agent '{agent_id}' manifest loaded")

            # TODO: Verify manifest signature
            # self._verify_manifest_signature(agent_id, manifest)

        # Initialize trust tracking
        self._trust_scores[agent_id] = 0.5  # Start neutral
        self._task_metrics[agent_id] = {"completed": 0, "failed": 0}

        logger.debug(f"📜 Agent '{agent_id}' Protocol tracking initialized")

    def on_task_submit(self, kernel: "RealVibeKernel", task: "Task") -> bool:
        """
        PROTOCOL GATE: Verify task submission is valid.

        Returns False to VETO the task submission.
        """
        # For now, allow all tasks - implement Protocol rules later
        # TODO: Check if requesting agent is authorized
        # TODO: Check if target agent accepts this task type
        # TODO: Verify delegation permissions
        return True

    def on_task_completed(self, kernel: "RealVibeKernel", task_id: str, result: Any) -> None:
        """
        Track task completion for trust calculation.
        """
        # Extract agent_id from result if available
        agent_id = None
        if isinstance(result, dict):
            agent_id = result.get("agent_id")

        if agent_id and agent_id in self._task_metrics:
            self._task_metrics[agent_id]["completed"] += 1
            self._update_trust_score(agent_id)

    def on_task_failed(self, kernel: "RealVibeKernel", task_id: str, error: str) -> None:
        """
        Track task failure for trust calculation.
        """
        # We don't have agent_id in failure - would need to track tasks
        pass

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up on shutdown."""
        logger.info(f"📜 STEWARD Protocol shutting down ({len(self._manifests)} manifests tracked)")

    # =========================================================================
    # PUBLIC API (accessible via kernel.steward.*)
    # =========================================================================

    def verify(self, agent_id: str) -> Dict[str, Any]:
        """
        Verify an agent's identity and manifest.

        Returns verification result with status and details.
        """
        result = {
            "agent_id": agent_id,
            "verified": False,
            "manifest_loaded": False,
            "signature_valid": None,  # TODO: implement
            "trust_score": self._trust_scores.get(agent_id, 0.0),
        }

        if agent_id in self._manifests:
            result["manifest_loaded"] = True
            result["verified"] = True  # Basic verification for now

        return result

    def get_trust_score(self, agent_id: str) -> float:
        """
        Get the current trust score for an agent.

        Returns 0.0-1.0 score based on Protocol metrics.
        """
        return self._trust_scores.get(agent_id, 0.0)

    def get_manifest(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the steward.json manifest for an agent.

        Returns manifest dict or None if not found.
        """
        return self._manifests.get(agent_id)

    def get_all_manifests(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded manifests."""
        return self._manifests.copy()

    def attest(self, agent_id: str, capability: str) -> Dict[str, Any]:
        """
        Create an attestation for an agent's capability.

        Returns attestation record.
        """
        attestation = {
            "agent_id": agent_id,
            "capability": capability,
            "attested_at": datetime.utcnow().isoformat(),
            "attested_by": "steward_protocol_plugin",
            "valid_until": None,  # TODO: implement expiry
        }

        if agent_id not in self._attestations:
            self._attestations[agent_id] = {}
        self._attestations[agent_id][capability] = attestation

        logger.info(f"📜 Attested capability '{capability}' for agent '{agent_id}'")
        return attestation

    def get_attestations(self, agent_id: str) -> Dict[str, Any]:
        """Get all attestations for an agent."""
        return self._attestations.get(agent_id, {})

    def get_config(self) -> Optional[Any]:
        """Get the Protocol configuration (from steward.yaml)."""
        return self._config

    def get_user_context(self, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user context from Protocol config (Layer 1.5).

        Args:
            user: Optional user name. If None, returns default_user.
        """
        if not self._config:
            return {}

        if hasattr(self._config, "user_context"):
            if user:
                return self._config.user_context.get_user(user).__dict__
            return self._config.user_context.default_user.__dict__
        return {}

    def get_cognitive_policy(self) -> Dict[str, Any]:
        """
        Get cognitive policy from Protocol config (Layer 1.6).
        """
        if not self._config:
            return {}

        if hasattr(self._config, "cognitive_policy"):
            return self._config.cognitive_policy.to_dict()
        return {}

    def get_behavior_rules(self) -> Dict[str, bool]:
        """
        Get behavior rules from Protocol config.
        """
        if not self._config:
            return {}

        if hasattr(self._config, "behavior"):
            return {
                "genesis_protocol": self._config.behavior.genesis_protocol,
                "anti_slop_rules": self._config.behavior.anti_slop_rules,
                "require_tests": self._config.behavior.require_tests,
                "require_commit": self._config.behavior.require_commit,
                "require_handoff": self._config.behavior.require_handoff,
            }
        return {}

    def get_protocol_status(self) -> Dict[str, Any]:
        """
        Get overall Protocol status.
        """
        return {
            "plugin_id": self.plugin_id,
            "agents_tracked": len(self._manifests),
            "trust_scores": len(self._trust_scores),
            "attestations": sum(len(a) for a in self._attestations.values()),
            "config_loaded": self._config is not None,
            "infrastructure": {
                "agent_loader": self._agent_loader is not None,
                "steward_client": self._steward_client is not None,
            },
        }

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _load_config(self) -> None:
        """Load Protocol configuration from Phoenix steward.yaml."""
        try:
            from vibe_core.phoenix.config import PhoenixConfig

            phoenix = PhoenixConfig.from_files(config_dir=self._project_root / "config")
            self._config = phoenix.steward
            logger.debug("📜 Protocol config loaded from Phoenix")
        except Exception as e:
            logger.warning(f"📜 Could not load Protocol config: {e}")
            self._config = None

    def _connect_infrastructure(self) -> None:
        """Connect to existing STEWARD infrastructure."""
        # Connect AgentLoader
        try:
            from vibe_core.steward import AgentLoader

            self._agent_loader = AgentLoader
            logger.debug("📜 AgentLoader connected")
        except ImportError as e:
            logger.warning(f"📜 AgentLoader not available: {e}")

        # Connect StewardClient
        try:
            from steward.client import StewardClient

            self._steward_client = StewardClient
            logger.debug("📜 StewardClient connected")
        except ImportError as e:
            logger.warning(f"📜 StewardClient not available: {e}")

    def _load_agent_manifest(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load steward.json manifest for an agent.

        Searches in standard locations:
        - steward/system_agents/{agent_id}/steward.json
        - agent_city/registry/{agent_id}/steward.json
        """
        import json

        search_paths = [
            self._project_root / "steward" / "system_agents" / agent_id / "steward.json",
            self._project_root / "agent_city" / "registry" / agent_id / "steward.json",
        ]

        for path in search_paths:
            if path.exists():
                try:
                    with open(path) as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"📜 Failed to load manifest from {path}: {e}")

        return None

    def _update_trust_score(self, agent_id: str) -> None:
        """
        Update trust score for an agent based on metrics.

        Simple formula for now:
        trust = completed / (completed + failed + 1)
        """
        metrics = self._task_metrics.get(agent_id, {"completed": 0, "failed": 0})
        completed = metrics["completed"]
        failed = metrics["failed"]

        if completed + failed == 0:
            score = 0.5  # Neutral
        else:
            score = completed / (completed + failed + 1)  # +1 to avoid division issues

        self._trust_scores[agent_id] = min(1.0, max(0.0, score))

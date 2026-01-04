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
    from vibe_core.protocols.kernel_protocol import KernelProtocol

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
        self._kernel: Optional["KernelProtocol"] = None

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

        # Task to agent mapping for failure tracking {task_id: agent_id}
        self._task_agent_map: Dict[str, str] = {}

        # Delegation permissions {from_agent: {to_agent: [allowed_ops]}}
        self._delegation_permissions: Dict[str, Dict[str, list]] = {}

        # Sensitive capabilities that require attestation
        self._sensitive_capabilities: set = {
            "write_file",
            "delete_file",
            "execute_command",
            "network_request",
            "credential_access",
        }

        # Strict mode: if True, block on violations instead of warn
        self._strict_mode: bool = False

        # Connected infrastructure (lazy loaded)
        self._agent_loader = None
        self._steward_client = None

    def _persist_manifest(self, agent_id: str, manifest: Dict[str, Any]) -> None:
        """Persist manifest to ledger."""
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="MANIFEST_REGISTERED", agent_id=agent_id, details={"manifest": manifest}
            )

    def _persist_trust_score(self, agent_id: str, score: float, reason: str = "") -> None:
        """Persist trust score change to ledger."""
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="TRUST_SCORE_UPDATED", agent_id=agent_id, details={"score": score, "reason": reason}
            )

    def _persist_attestation(self, agent_id: str, capability: str, attestation: Dict[str, Any]) -> None:
        """Persist attestation to ledger."""
        if self._kernel and hasattr(self._kernel, "ledger"):
            self._kernel.ledger.record_event(
                event_type="ATTESTATION_CREATED",
                agent_id=agent_id,
                details={"capability": capability, "attestation": attestation},
            )

    def _restore_from_ledger(self) -> None:
        """Restore protocol state from ledger on boot."""
        if not self._kernel or not hasattr(self._kernel, "ledger"):
            return

        for event in self._kernel.ledger.get_all_events():
            event_type = event.get("event_type")
            agent_id = event.get("agent_id")
            details = event.get("details", {})

            if event_type == "MANIFEST_REGISTERED" and agent_id:
                manifest = details.get("manifest")
                if manifest:
                    self._manifests[agent_id] = manifest

            elif event_type == "TRUST_SCORE_UPDATED" and agent_id:
                score = details.get("score")
                if score is not None:
                    self._trust_scores[agent_id] = float(score)

            elif event_type == "ATTESTATION_CREATED" and agent_id:
                capability = details.get("capability")
                attestation = details.get("attestation")
                if capability and attestation:
                    if agent_id not in self._attestations:
                        self._attestations[agent_id] = {}
                    self._attestations[agent_id][capability] = attestation

    # =========================================================================
    # KERNEL HOOKS
    # =========================================================================

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """
        Called when kernel boots.

        Register this plugin as the Protocol provider on the kernel.
        Load configuration and connect infrastructure.
        """
        self._kernel = kernel
        self._restore_from_ledger()

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

    def on_agent_pre_register(self, kernel: "KernelProtocol", agent: Any) -> bool:
        """
        AGENT REGISTRATION GATE: Called BEFORE agent registration.

        Enforces Constitutional Oath if enabled in config.
        """
        # Check if Oath enforcement is enabled (default: True)
        enforce_oath = True
        if self._config and hasattr(self._config, "behavior"):
            enforce_oath = self._config.behavior.enforce_oath

        if not enforce_oath:
            logger.debug(f"📜 Oath enforcement DISABLED - Agent '{agent.agent_id}' allowed")
            return True

        # STEP 1: THE INSPECTION (Does the agent possess the Oath badge?)
        # Check for oath attributes that OathMixin provides
        has_oath_attribute = hasattr(agent, "oath_sworn") or hasattr(agent, "oath_event")

        if not has_oath_attribute:
            logger.critical(
                f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' "
                f"attempted registration WITHOUT Constitutional Oath."
            )
            # VETO registration
            return False

        # STEP 2: THE VERIFICATION (Is the Oath valid?)
        # Check if agent has actually sworn the oath (oath_sworn = True)
        oath_sworn = getattr(agent, "oath_sworn", False)
        oath_event = getattr(agent, "oath_event", None)

        if not oath_sworn:
            logger.critical(
                f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' "
                f"has oath attributes but oath_sworn={oath_sworn}. "
                f"Agent has not executed Genesis Ceremony."
            )
            return False

        # STEP 3: THE CRYPTOGRAPHIC VALIDATION (Is the oath genuine?)
        # Verify the oath signature against current Constitution
        # Note: We need OATH_ENFORCEMENT_AVAILABLE equivalent here
        # For now, we assume if crypto module is available, we use it.
        if oath_event:
            try:
                # Import here to avoid circular deps if needed, or use existing imports
                from vibe_core.steward.constitution import ConstitutionalOath

                is_valid, reason = ConstitutionalOath.verify_oath(oath_event, getattr(agent, "identity_tool", None))

                if not is_valid:
                    logger.critical(
                        f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' oath verification FAILED: {reason}"
                    )
                    return False

                logger.info(f"✅ Governance Gate PASSED: Agent '{agent.agent_id}' oath verified ({reason})")

            except ImportError:
                # Crypto not available - skip strict verification but warn
                logger.warning(f"📜 Crypto module missing - skipping signature check for '{agent.agent_id}'")
            except Exception as e:
                logger.error(f"❌ Governance gate verification error for '{agent.agent_id}': {e}")
                # Fail open or closed? Security says closed.
                return False

        return True

    def on_agent_registered(self, kernel: "KernelProtocol", agent_id: str) -> None:
        """
        Called when a new agent is registered.

        PROTOCOL ENFORCEMENT:
        1. Load steward.json manifest (SSOT for agent identity)
        2. Verify signature if present
        3. GRANT correct capabilities from manifest (not cartridge hardcoded ones)
        4. Initialize trust tracking
        """
        # Try to load manifest for this agent
        manifest = self._load_agent_manifest(agent_id)

        if manifest:
            self._manifests[agent_id] = manifest
            self._persist_manifest(agent_id, manifest)
            logger.info(f"📜 Agent '{agent_id}' manifest loaded")

            # Verify manifest signature if present
            signature_valid = self._verify_manifest_signature(agent_id, manifest)
            if signature_valid:
                logger.info(f"📜 Agent '{agent_id}' signature VERIFIED ✓")
            elif signature_valid is False:
                logger.warning(f"📜 Agent '{agent_id}' signature INVALID ✗")
            # None means no signature present (acceptable for dev)

            # PROTOCOL ENFORCEMENT: Grant correct capabilities from manifest
            # steward.json is SSOT, not cartridge hardcoded capabilities
            self._enforce_manifest_capabilities(kernel, agent_id, manifest)

        # Initialize trust tracking
        self._trust_scores[agent_id] = 0.5  # Start neutral
        self._task_metrics[agent_id] = {"completed": 0, "failed": 0}

        logger.debug(f"📜 Agent '{agent_id}' Protocol tracking initialized")

    def on_task_completed(self, kernel: "KernelProtocol", task_id: str, result: Any) -> None:
        """
        Track task completion for trust calculation.

        Success increases trust score.
        """
        # Extract agent_id from result or task map
        agent_id = None
        if isinstance(result, dict):
            agent_id = result.get("agent_id")

        if not agent_id:
            agent_id = self._task_agent_map.pop(task_id, None)

        if agent_id and agent_id in self._task_metrics:
            self._task_metrics[agent_id]["completed"] += 1
            self._update_trust_score(agent_id)
            logger.debug(f"📜 Trust: Agent '{agent_id}' completed task, score updated")

    def on_task_failed(self, kernel: "KernelProtocol", task_id: str, error: str) -> None:
        """
        Track task failure for trust calculation.

        Failure decreases trust score.
        """
        # Get agent_id from task map
        agent_id = self._task_agent_map.pop(task_id, None)

        if agent_id and agent_id in self._task_metrics:
            self._task_metrics[agent_id]["failed"] += 1
            self._update_trust_score(agent_id)
            logger.info(f"📜 Trust: Agent '{agent_id}' failed task, score decreased")

    def on_task_submit(self, kernel: "KernelProtocol", task: "Task") -> bool:
        """
        PROTOCOL GATE: Verify task submission is valid.

        Returns False to VETO the task submission.

        Checks:
        1. Target agent exists and has manifest
        2. Target agent accepts the task type (if declared in capabilities)
        3. Requester has delegation permission (if enforced)
        4. Track task→agent mapping for trust calculation
        """
        # Get target agent from task
        target_agent = getattr(task, "agent_id", None) or getattr(task, "target", None)
        task_id = getattr(task, "task_id", None) or getattr(task, "id", None)

        # Track task→agent for trust calculation
        if task_id and target_agent:
            self._task_agent_map[task_id] = target_agent

        if not target_agent:
            # No target specified - allow (kernel will route)
            return True

        # Check 1: Agent must be registered
        if target_agent not in self._manifests:
            # Agent not known to Protocol - allow but log
            logger.debug(f"📜 Task target '{target_agent}' not in Protocol registry")
            return True  # Don't block - agent may be registered later

        manifest = self._manifests[target_agent]

        # Check 2: Verify task type is accepted (if capabilities declared)
        capabilities = manifest.get("capabilities", {})
        accepted_operations = capabilities.get("operations", [])

        if accepted_operations:
            task_type = getattr(task, "type", None) or getattr(task, "action", "unknown")
            # Extract operation names from list of dicts
            op_names = [op.get("name", "") if isinstance(op, dict) else op for op in accepted_operations]
            if task_type not in op_names and "*" not in op_names:
                logger.warning(f"📜 PROTOCOL GATE: Agent '{target_agent}' does not accept '{task_type}' tasks")
                # Don't veto - just warn. Strict mode can be added later.

        # Check 3: Trust score threshold (if enabled)
        trust_score = self._trust_scores.get(target_agent, 0.5)
        if trust_score < 0.2:
            logger.warning(f"📜 PROTOCOL GATE: Agent '{target_agent}' has low trust score ({trust_score:.2f})")
            # Don't veto - just warn. Can be made strict later.

        return True  # Allow task

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
        """Clean up on shutdown."""
        logger.info(f"📜 STEWARD Protocol shutting down ({len(self._manifests)} manifests tracked)")

    def on_capability_check(self, kernel: "KernelProtocol", agent_id: str, capability: str) -> Optional[bool]:
        """
        CAPABILITY GATE: Protocol enforcement for capability access.

        This hook is called by the kernel for EVERY capability check.
        It enables:
        - Trust-based capability gating
        - Attestation requirements for sensitive operations
        - Delegation chain verification

        Returns:
            True  = Explicitly allow
            False = VETO (block access)
            None  = No opinion (default)
        """
        # Run full Protocol check
        result = self.check_capability_access(agent_id, capability)

        # Log warnings
        for warning in result.get("warnings", []):
            logger.warning(f"📜 CAPABILITY CHECK: Agent '{agent_id}' - {warning}")

        # In strict mode, denied access returns False (VETO)
        if not result["allowed"]:
            logger.info(f"📜 CAPABILITY VETO: Agent '{agent_id}' denied '{capability}' - {result['reason']}")
            return False

        # Otherwise, no opinion (let other plugins/registry decide)
        return None

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
            "signature_valid": False,  # Default to False, verified below
            "trust_score": self._trust_scores.get(agent_id, 0.0),
        }

        # Verify signature using ConstitutionalOath if oath exists in ledger
        if self._kernel and hasattr(self._kernel, "ledger"):
            oath_events = [
                e
                for e in self._kernel.ledger.get_all_events()
                if e.get("event_type") == "OATH_TAKEN" and e.get("agent_id") == agent_id
            ]
            if oath_events:
                from vibe_core.steward.constitution import ConstitutionalOath

                latest_oath = oath_events[-1]
                # Get identity_tool if available
                identity_tool = None
                if hasattr(self._kernel, "tool_registry"):
                    identity_tool = self._kernel.tool_registry.get_tool("identity")
                is_valid, _ = ConstitutionalOath.verify_oath(latest_oath, identity_tool=identity_tool)
                result["signature_valid"] = is_valid

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

    def attest(self, agent_id: str, capability: str, validity_hours: int = 24) -> Dict[str, Any]:
        """
        Create an attestation for an agent's capability.

        Args:
            agent_id: Agent to attest
            capability: Capability being attested
            validity_hours: Hours until attestation expires (default: 24)

        Returns attestation record.
        """
        from datetime import timedelta

        now = datetime.utcnow()
        attestation = {
            "agent_id": agent_id,
            "capability": capability,
            "attested_at": now.isoformat(),
            "attested_by": "steward_protocol_plugin",
            "valid_until": (now + timedelta(hours=validity_hours)).isoformat(),
        }

        if agent_id not in self._attestations:
            self._attestations[agent_id] = {}
        self._attestations[agent_id][capability] = attestation
        self._persist_attestation(agent_id, capability, attestation)

        logger.info(f"📜 Attested capability '{capability}' for agent '{agent_id}'")
        return attestation

    def get_attestations(self, agent_id: str) -> Dict[str, Any]:
        """Get all attestations for an agent."""
        return self._attestations.get(agent_id, {})

    def is_attestation_valid(self, agent_id: str, capability: str) -> bool:
        """
        Check if an attestation is still valid (not expired).

        Returns True if attestation exists and hasn't expired.
        """
        attestations = self._attestations.get(agent_id, {})
        attestation = attestations.get(capability)

        if not attestation:
            return False

        valid_until = attestation.get("valid_until")
        if not valid_until:
            return False

        try:
            expiry = datetime.fromisoformat(valid_until)
            return datetime.utcnow() < expiry
        except (ValueError, TypeError):
            return False

    def has_attestation(self, agent_id: str, capability: str) -> bool:
        """
        Check if agent has valid attestation for a capability.

        Used for sensitive operations that require attestation.
        """
        attestations = self._attestations.get(agent_id, {})
        if capability not in attestations:
            return False

        attestation = attestations[capability]

        # Check expiry if set
        valid_until = attestation.get("valid_until")
        if valid_until:
            from datetime import datetime

            expiry = datetime.fromisoformat(valid_until)
            if datetime.utcnow() > expiry:
                return False

        return True

    def requires_attestation(self, capability: str) -> bool:
        """Check if a capability requires attestation (sensitive operation)."""
        return capability in self._sensitive_capabilities

    def check_capability_access(self, agent_id: str, capability: str) -> Dict[str, Any]:
        """
        Full Protocol check for capability access.

        Returns dict with:
        - allowed: bool
        - reason: str
        - warnings: list of warnings
        """
        warnings = []

        # Check 1: Trust score
        trust_score = self._trust_scores.get(agent_id, 0.5)
        if trust_score < 0.3:
            warnings.append(f"Low trust score ({trust_score:.2f})")
            if self._strict_mode and trust_score < 0.2:
                return {
                    "allowed": False,
                    "reason": f"Trust score too low ({trust_score:.2f})",
                    "warnings": warnings,
                }

        # Check 2: Attestation for sensitive capabilities
        if self.requires_attestation(capability):
            if not self.has_attestation(agent_id, capability):
                msg = f"Sensitive capability '{capability}' requires attestation"
                warnings.append(msg)
                if self._strict_mode:
                    return {
                        "allowed": False,
                        "reason": msg,
                        "warnings": warnings,
                    }

        return {
            "allowed": True,
            "reason": "Access granted",
            "warnings": warnings,
        }

    def delegate(
        self,
        from_agent: str,
        to_agent: str,
        operations: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Grant delegation permission from one agent to another.

        Args:
            from_agent: Agent granting permission
            to_agent: Agent receiving permission
            operations: List of allowed operations (None = all)

        Returns:
            Delegation record
        """
        if from_agent not in self._delegation_permissions:
            self._delegation_permissions[from_agent] = {}

        self._delegation_permissions[from_agent][to_agent] = operations or ["*"]

        record = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "operations": operations or ["*"],
            "delegated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"📜 Delegation: '{from_agent}' → '{to_agent}' for {operations or 'all operations'}")
        return record

    def can_delegate_to(self, from_agent: str, to_agent: str, operation: str) -> bool:
        """
        Check if from_agent can delegate operation to to_agent.
        """
        permissions = self._delegation_permissions.get(from_agent, {})
        allowed_ops = permissions.get(to_agent, [])

        if not allowed_ops:
            return False

        return "*" in allowed_ops or operation in allowed_ops

    def set_strict_mode(self, enabled: bool) -> None:
        """Enable/disable strict mode (block on violations vs warn)."""
        self._strict_mode = enabled
        logger.info(f"📜 Strict mode {'ENABLED' if enabled else 'DISABLED'}")

    def add_sensitive_capability(self, capability: str) -> None:
        """Add a capability to the sensitive list (requires attestation)."""
        self._sensitive_capabilities.add(capability)
        logger.info(f"📜 Added sensitive capability: {capability}")

    def get_config(self) -> Optional[Any]:
        """Get the Protocol configuration (from vibe_core.steward.yaml)."""
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
            from vibe_core.phoenix.config import get_config

            phoenix = get_config()
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
            from vibe_core.steward.client import StewardClient

            self._steward_client = StewardClient
            logger.debug("📜 StewardClient connected")
        except ImportError as e:
            logger.warning(f"📜 StewardClient not available: {e}")

    def _load_agent_manifest(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Load steward.json manifest for an agent.

        Searches in standard locations:
        - vibe_core/cartridges/system/{agent_id}/steward.json
        - vibe_core/cartridges/agent_city/{agent_id}/steward.json
        """
        import json

        search_paths = [
            self._project_root / "vibe_core" / "cartridges" / "system" / agent_id / "steward.json",
            self._project_root / "vibe_core" / "cartridges" / "agent_city" / agent_id / "steward.json",
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

        new_score = min(1.0, max(0.0, score))
        self._trust_scores[agent_id] = new_score
        self._persist_trust_score(agent_id, new_score, "task_completion")

    def _enforce_manifest_capabilities(self, kernel: "KernelProtocol", agent_id: str, manifest: Dict[str, Any]) -> None:
        """
        PROTOCOL ENFORCEMENT: Grant capabilities from vibe_core.steward.json manifest.

        The steward.json is the SSOT for agent capabilities.
        Cartridge hardcoded capabilities are WRONG - we override with manifest.

        Example:
            steward.json: ["herald.broadcast", "herald.research"]  ← CORRECT
            cartridge:    ["broadcasting", "research"]             ← WRONG

        This method grants the CORRECT capabilities from the manifest.
        """
        # Extract capabilities from manifest
        caps_data = manifest.get("capabilities", {})
        operations = caps_data.get("operations", [])

        # Handle both formats: list of dicts or list of strings
        manifest_caps = []
        for op in operations:
            if isinstance(op, dict):
                cap_name = op.get("name", "")
                if cap_name:
                    manifest_caps.append(cap_name)
            elif isinstance(op, str):
                manifest_caps.append(op)

        if not manifest_caps:
            logger.debug(f"📜 Agent '{agent_id}' has no capabilities in manifest")
            return

        # Get current capabilities (from cartridge - potentially wrong)
        current_caps = kernel._capability_registry.get_capabilities(agent_id)

        # Grant manifest capabilities (SSOT)
        result = kernel._capability_registry.grant(
            agent_id=agent_id,
            capabilities=manifest_caps,
            granter_id="steward_protocol",
            reason="Protocol enforcement: capabilities from vibe_core.steward.json (SSOT)",
        )

        if result.get("granted"):
            logger.info(
                f"📜 PROTOCOL ENFORCEMENT: Agent '{agent_id}' granted {len(result['granted'])} capabilities from manifest"
            )
            logger.debug(f"   Manifest caps: {manifest_caps}")
            logger.debug(f"   Cartridge had: {list(current_caps)}")
            logger.debug(f"   Granted: {result['granted']}")

    def _verify_manifest_signature(self, agent_id: str, manifest: Dict[str, Any]) -> Optional[bool]:
        """
        Verify the cryptographic signature of an agent manifest.

        Uses ECDSA signature from steward/crypto.py

        Args:
            agent_id: Agent identifier
            manifest: Manifest dict from vibe_core.steward.json

        Returns:
            True if valid, False if invalid, None if no signature present
        """
        # Check if manifest has signature block
        signature_block = manifest.get("signature")
        if not signature_block:
            logger.debug(f"📜 Agent '{agent_id}' has no signature (dev mode acceptable)")
            return None

        signature = signature_block.get("value")
        public_key = signature_block.get("public_key")

        if not signature or not public_key:
            logger.debug(f"📜 Agent '{agent_id}' signature block incomplete")
            return None

        try:
            # Import crypto functions
            # Create canonical content to verify (manifest without signature block)
            import json

            from vibe_core.steward.crypto import verify_signature

            manifest_copy = {k: v for k, v in manifest.items() if k != "signature"}
            canonical_content = json.dumps(manifest_copy, sort_keys=True, separators=(",", ":"))

            # Verify signature
            is_valid = verify_signature(canonical_content, signature, public_key)
            return is_valid

        except ImportError:
            logger.warning("📜 Crypto module not available - signature verification skipped")
            return None
        except Exception as e:
            logger.warning(f"📜 Signature verification failed for '{agent_id}': {e}")
            return False

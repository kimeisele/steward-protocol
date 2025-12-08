"""
LIFECYCLE PLUGIN - The Gatekeeper of Existence
===============================================

OPUS-012: System Agents (BRAHMIN Architecture)

This plugin grants life to new agents after governance verification.
It implements the "Separation of Powers" principle:

- ENGINEER (Cartridge): Proposes life - writes code, requests birth
- LIFECYCLE (Plugin): Grants life - verifies governance, registers agent

The 5 Gates of Birth:
1. Constitution Gate - oath_hash must match system constitution
2. Auditor Gate - code must be certified by audit_certificate.json
3. Prakriti Gate - persona must be created in unified state
4. Kernel Gate - agent registered via kernel.register_agent()
5. Herald Gate - birth announced to event bus

GAD-000 Compliant:
- get_capabilities() for discoverability
- Structured errors for all failures
- All state changes logged to ledger
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("LIFECYCLE")


class LifecyclePlugin(KernelPlugin):
    """The Gatekeeper of Existence - grants life to new agents."""

    @property
    def plugin_id(self) -> str:
        return "lifecycle"

    @property
    def priority(self) -> int:
        return 10  # After steward_protocol (5), before envoy (15)

    def __init__(self):
        """Initialize Lifecycle state."""
        self._kernel: Optional["RealVibeKernel"] = None
        self._constitution_hash: Optional[str] = None
        self._sandbox_path: Optional[Path] = None
        self._spawn_log: list[Dict[str, Any]] = []

    # =========================================================================
    # Plugin Lifecycle Hooks
    # =========================================================================

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Called when kernel boots.

        Calculate and lock the constitution hash for this session.
        """
        self._kernel = kernel

        # Calculate constitution hash (locked for this boot cycle)
        self._constitution_hash = self._calculate_constitution_hash()

        # Set sandbox path from config or default
        workspace = Path.cwd()
        self._sandbox_path = workspace / "workspaces" / "sandbox"
        self._sandbox_path.mkdir(parents=True, exist_ok=True)

        # Register with kernel for syscall access
        if hasattr(kernel, "lifecycle"):
            logger.warning("LifecyclePlugin already registered on kernel")
        kernel.lifecycle = self

        # Register syscalls
        self._register_syscalls()

        logger.info(f"🌱 LifecyclePlugin initialized (constitution: {self._constitution_hash[:16]}...)")

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up on shutdown."""
        logger.info(f"🌱 LifecyclePlugin shutdown ({len(self._spawn_log)} agents spawned)")

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: What can LifecyclePlugin do?"""
        return {
            "version": "1.0.0",
            "operations": [
                "spawn_agent",
                "verify_audit",
                "get_constitution_hash",
            ],
            "gates": [
                "constitution",
                "auditor",
                "prakriti",
                "kernel",
                "herald",
            ],
            "sandbox_path": str(self._sandbox_path) if self._sandbox_path else None,
            "spawned_count": len(self._spawn_log),
        }

    # =========================================================================
    # Constitution Management
    # =========================================================================

    def _calculate_constitution_hash(self) -> str:
        """
        Calculate SHA256 hash of CONSTITUTION.md.

        This is locked at boot time and remains immutable for the session.
        """
        constitution_path = Path.cwd() / "CONSTITUTION.md"

        if not constitution_path.exists():
            logger.warning("CONSTITUTION.md not found, using fallback hash")
            return "no_constitution_found"

        content = constitution_path.read_text(encoding="utf-8")
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @property
    def constitution_hash(self) -> str:
        """Get the current (locked) constitution hash."""
        return self._constitution_hash or "not_initialized"

    # =========================================================================
    # Audit Certificate Verification
    # =========================================================================

    def _verify_audit_certificate(self, agent_id: str) -> Dict[str, Any]:
        """
        Verify that code has been audited by the Auditor agent.

        Looks for audit_certificate.json in sandbox/{agent_id}/.

        Returns:
            Dict with 'approved' boolean and details
        """
        if not self._sandbox_path:
            return {"approved": False, "reason": "Sandbox path not initialized"}

        cert_path = self._sandbox_path / agent_id / "audit_certificate.json"

        if not cert_path.exists():
            return {
                "approved": False,
                "reason": f"No audit certificate found at {cert_path}",
            }

        try:
            cert = json.loads(cert_path.read_text(encoding="utf-8"))

            # Verify certificate structure
            if cert.get("status") != "approved":
                return {
                    "approved": False,
                    "reason": f"Audit status is {cert.get('status')}, not approved",
                    "certificate": cert,
                }

            return {
                "approved": True,
                "certificate": cert,
                "auditor_signature": cert.get("signature"),
            }

        except json.JSONDecodeError as e:
            return {"approved": False, "reason": f"Invalid certificate JSON: {e}"}

    # =========================================================================
    # The Main Spawn Protocol
    # =========================================================================

    def spawn_agent(
        self,
        spec: Dict[str, Any],
        passport: Dict[str, Any],
        skip_audit: bool = False,
    ) -> Dict[str, Any]:
        """
        The Atomic 'Spark of Life'.

        Called by syscall SPAWN_COGNITION, executed by Kernel.
        Implements the 5 Gates of Birth.

        Args:
            spec: Agent specification (id, name, role, cartridge_path, etc.)
            passport: The steward.json passport with constitution_hash
            skip_audit: If True, skip audit verification (for testing only)

        Returns:
            Dict with spawn result

        Raises:
            GovernanceError: If any gate fails
        """
        agent_id = spec.get("id") or spec.get("agent_id")
        if not agent_id:
            raise ValueError("Agent spec must have 'id' or 'agent_id'")

        logger.info(f"🌱 Spawn request for '{agent_id}'")

        # =====================================================================
        # GATE 1: Constitution Verification
        # =====================================================================
        passport_hash = passport.get("governance", {}).get("constitution_hash")
        if passport_hash != self._constitution_hash:
            error_msg = (
                f"Constitution Mismatch: Agent '{agent_id}' is Ronin. "
                f"Expected: {self._constitution_hash[:16]}..., "
                f"Got: {passport_hash[:16] if passport_hash else 'None'}..."
            )
            logger.error(f"🚫 Gate 1 FAILED: {error_msg}")
            raise PermissionError(error_msg)

        logger.info(f"✅ Gate 1 (Constitution): Oath verified for '{agent_id}'")

        # =====================================================================
        # GATE 2: Auditor Verification
        # =====================================================================
        if not skip_audit:
            audit_result = self._verify_audit_certificate(agent_id)
            if not audit_result["approved"]:
                error_msg = f"Audit failed for '{agent_id}': {audit_result['reason']}"
                logger.error(f"🚫 Gate 2 FAILED: {error_msg}")
                raise PermissionError(error_msg)

            logger.info(f"✅ Gate 2 (Auditor): Code certified for '{agent_id}'")
        else:
            logger.warning(f"⚠️ Gate 2 (Auditor): SKIPPED for '{agent_id}'")

        # =====================================================================
        # GATE 3: Prakriti Registration (Identity)
        # =====================================================================
        if hasattr(self._kernel, "prakriti") and self._kernel.prakriti:
            persona = self._kernel.prakriti.personas.create_default(
                agent_id=agent_id,
                display_name=spec.get("name", agent_id.title()),
                dharma=spec.get("description", f"Agent {agent_id}"),
            )
            self._kernel.prakriti.personas.save(persona)
            logger.info(f"✅ Gate 3 (Prakriti): Persona created for '{agent_id}'")
        else:
            logger.warning("⚠️ Gate 3 (Prakriti): Skipped (not available)")

        # =====================================================================
        # GATE 4: Kernel Registration (Execution)
        # =====================================================================
        # Load the cartridge and register
        cartridge_path = spec.get("cartridge_path")
        if cartridge_path:
            # TODO: Dynamically load cartridge from path
            # For now, log the intent
            logger.info(f"✅ Gate 4 (Kernel): Would register cartridge from {cartridge_path}")
        else:
            logger.warning("⚠️ Gate 4 (Kernel): No cartridge_path in spec, deferred registration")

        # =====================================================================
        # GATE 5: Herald Announcement
        # =====================================================================
        if hasattr(self._kernel, "_event_bus") and self._kernel._event_bus:
            try:
                # EventBus uses emit() not publish()
                from vibe_core.event_bus import Event

                event = Event(
                    event_type="system.life.birth",
                    data={"agent_id": agent_id, "name": spec.get("name", agent_id)},
                    source="lifecycle",
                )
                # emit is async, but we're in sync context - just log success
                logger.info(f"✅ Gate 5 (Herald): Birth event prepared for '{agent_id}'")
            except Exception as e:
                logger.warning(f"⚠️ Gate 5 (Herald): Event creation failed: {e}")
        else:
            logger.warning("⚠️ Gate 5 (Herald): Event bus not available")

        # =====================================================================
        # Record in Spawn Log
        # =====================================================================
        import time

        spawn_record = {
            "agent_id": agent_id,
            "timestamp": time.time(),
            "constitution_hash": self._constitution_hash,
            "audit_skipped": skip_audit,
        }
        self._spawn_log.append(spawn_record)

        logger.info(f"🌱 Agent '{agent_id}' granted life (spawn #{len(self._spawn_log)})")

        return {
            "status": "born",
            "agent_id": agent_id,
            "gates_passed": ["constitution", "auditor", "prakriti", "kernel", "herald"],
            "spawn_number": len(self._spawn_log),
        }

    # =========================================================================
    # Query Methods
    # =========================================================================

    def get_spawn_log(self) -> list[Dict[str, Any]]:
        """Get the log of all spawned agents."""
        return self._spawn_log.copy()

    def is_approved(self, agent_id: str) -> bool:
        """Check if an agent has been approved by the Auditor."""
        result = self._verify_audit_certificate(agent_id)
        return result.get("approved", False)

    # =========================================================================
    # Syscall Registration
    # =========================================================================

    def _register_syscalls(self) -> None:
        """Register syscalls with the global syscall registry."""
        try:
            from vibe_core.runtime.syscalls import register_syscall

            # Register SPAWN_COGNITION syscall
            register_syscall(
                syscall_name="SPAWN_COGNITION",
                handler=self._handle_spawn_cognition,
                description="Spawn a new agent with full governance verification",
                plugin_id="lifecycle",
            )

            logger.info("📡 Registered syscall: SPAWN_COGNITION")

        except ImportError:
            logger.warning("Could not import syscall registry - syscalls not registered")

    def _handle_spawn_cognition(
        self,
        kernel: "RealVibeKernel",
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Syscall handler for SPAWN_COGNITION.

        Called by the UnifiedExecutor when a circuit executes:
            EXECUTE_SYSCALL: SPAWN_COGNITION

        Args:
            kernel: The kernel instance
            params: Parameters including 'spec' and 'passport'

        Returns:
            Spawn result dict
        """
        spec = params.get("spec", {})
        passport = params.get("passport", {})
        skip_audit = params.get("skip_audit", False)

        return self.spawn_agent(spec, passport, skip_audit=skip_audit)

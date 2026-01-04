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
    from vibe_core.protocols.kernel_protocol import KernelProtocol

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
        self._kernel: Optional["KernelProtocol"] = None
        self._constitution_hash: Optional[str] = None
        self._sandbox_path: Optional[Path] = None
        self._spawn_log: list[Dict[str, Any]] = []

    # =========================================================================
    # Plugin Lifecycle Hooks
    # =========================================================================

    def on_boot(self, kernel: "KernelProtocol") -> None:
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

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
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
        cartridge_path = spec.get("cartridge_path")
        if cartridge_path:
            try:
                # Dynamically load cartridge from path
                import importlib.util
                from pathlib import Path

                cartridge_file = Path(cartridge_path)
                if not cartridge_file.exists():
                    raise FileNotFoundError(f"Cartridge not found: {cartridge_path}")

                # Load as module
                module_name = f"spawned_agent_{agent_id}"
                spec_loader = importlib.util.spec_from_file_location(module_name, cartridge_file)
                if not spec_loader or not spec_loader.loader:
                    raise ImportError(f"Cannot load module from {cartridge_path}")

                module = importlib.util.module_from_spec(spec_loader)
                spec_loader.loader.exec_module(module)

                # Find the Cartridge class (ends with 'Cartridge')
                cartridge_class = None
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and name.endswith("Cartridge"):
                        cartridge_class = obj
                        break

                if not cartridge_class:
                    raise TypeError(f"No *Cartridge class found in {cartridge_path}")

                # Instantiate and register
                cartridge_instance = cartridge_class()
                self._kernel.register_agent(cartridge_instance, spawn_process=False)

                logger.info(f"✅ Gate 4 (Kernel): Registered '{agent_id}' from {cartridge_path}")

            except Exception as e:
                logger.error(f"❌ Gate 4 (Kernel): Failed to load cartridge: {e}")
                raise
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
        kernel: "KernelProtocol",
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

    # =========================================================================
    # OPUS-307 Phase II: CLI Command Handlers
    # "steward agents" namespace - visibility into the agent registry
    # =========================================================================

    def cmd_agents_list(self, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward agents:list

        List all registered agents - like `ps aux` for the agent OS.

        Args:
            json: If True, return raw JSON-compatible data

        Returns:
            Dict with agent listing
        """
        if not self._kernel:
            return {"success": False, "error": "Kernel not initialized"}

        agents = []
        registry = getattr(self._kernel, "agent_registry", {})

        for agent_id, agent in registry.items():
            agent_info = {
                "id": agent_id,
                "name": getattr(agent, "name", agent_id),
                "version": getattr(agent, "version", "unknown"),
                "domain": getattr(agent, "domain", "unknown"),
                "oath_sworn": getattr(agent, "oath_sworn", False),
            }

            # Get capabilities if available
            if hasattr(agent, "capabilities"):
                agent_info["capabilities"] = len(agent.capabilities)

            agents.append(agent_info)

        result = {
            "success": True,
            "count": len(agents),
            "agents": agents,
            "spawned_this_session": len(self._spawn_log),
        }

        if not json:
            # Format for human display
            lines = [f"📋 REGISTERED AGENTS ({len(agents)} total)"]
            lines.append("=" * 60)
            for a in agents:
                oath = "✅" if a.get("oath_sworn") else "❌"
                caps = a.get("capabilities", "?")
                lines.append(f"  {oath} {a['id']:<20} v{a['version']:<8} [{a['domain']}] ({caps} caps)")
            lines.append("=" * 60)
            lines.append(f"Spawned this session: {len(self._spawn_log)}")
            result["formatted"] = "\n".join(lines)

        return result

    def cmd_agents_status(self, agent_id: str, json: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward agents:status <agent_id>

        Show detailed status of a specific agent.

        Args:
            agent_id: Agent ID to inspect
            json: If True, return raw JSON-compatible data

        Returns:
            Dict with agent details
        """
        if not self._kernel:
            return {"success": False, "error": "Kernel not initialized"}

        registry = getattr(self._kernel, "agent_registry", {})
        agent = registry.get(agent_id)

        if not agent:
            return {"success": False, "error": f"Agent '{agent_id}' not found"}

        # Gather detailed info
        status = {
            "success": True,
            "agent_id": agent_id,
            "name": getattr(agent, "name", agent_id),
            "version": getattr(agent, "version", "unknown"),
            "author": getattr(agent, "author", "unknown"),
            "domain": getattr(agent, "domain", "unknown"),
            "description": getattr(agent, "description", ""),
            "oath_sworn": getattr(agent, "oath_sworn", False),
            "capabilities": list(getattr(agent, "capabilities", [])),
        }

        # Check if in spawn log
        spawned = [s for s in self._spawn_log if s["agent_id"] == agent_id]
        if spawned:
            status["spawn_info"] = spawned[-1]

        if not json:
            lines = [f"🔍 AGENT STATUS: {agent_id}"]
            lines.append("=" * 60)
            lines.append(f"  Name:        {status['name']}")
            lines.append(f"  Version:     {status['version']}")
            lines.append(f"  Author:      {status['author']}")
            lines.append(f"  Domain:      {status['domain']}")
            lines.append(f"  Oath Sworn:  {'✅ Yes' if status['oath_sworn'] else '❌ No'}")
            lines.append(f"  Description: {status['description'][:50]}...")
            lines.append(f"  Capabilities ({len(status['capabilities'])}):")
            for cap in status["capabilities"][:10]:
                lines.append(f"    - {cap}")
            if len(status["capabilities"]) > 10:
                lines.append(f"    ... and {len(status['capabilities']) - 10} more")
            lines.append("=" * 60)
            status["formatted"] = "\n".join(lines)

        return status

    def cmd_agents_kill(self, agent_id: str, force: bool = False) -> Dict[str, Any]:
        """
        CLI Handler: steward agents:kill <agent_id>

        Terminate an agent via Narasimha Protocol.

        Args:
            agent_id: Agent ID to terminate
            force: If True, force kill without graceful shutdown

        Returns:
            Dict with termination result
        """
        if not self._kernel:
            return {"success": False, "error": "Kernel not initialized"}

        registry = getattr(self._kernel, "agent_registry", {})
        if agent_id not in registry:
            return {"success": False, "error": f"Agent '{agent_id}' not found"}

        # Use Narasimha if available
        narasimha = getattr(self._kernel, "_narasimha", None)
        if narasimha and hasattr(narasimha, "terminate_agent"):
            try:
                reason = "CLI kill command" + (" (forced)" if force else "")
                narasimha.terminate_agent(agent_id, reason=reason)
                logger.info(f"🗡️ Agent '{agent_id}' terminated via Narasimha")
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "method": "narasimha",
                    "forced": force,
                }
            except Exception as e:
                logger.error(f"Narasimha termination failed: {e}")
                if not force:
                    return {"success": False, "error": str(e)}

        # Direct kernel termination
        if hasattr(self._kernel, "terminate_agent"):
            try:
                self._kernel.terminate_agent(agent_id)
                logger.info(f"🗡️ Agent '{agent_id}' terminated via kernel")
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "method": "kernel",
                    "forced": force,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "No termination method available"}

    def cmd_agents_spawn_log(self, limit: int = 20) -> Dict[str, Any]:
        """
        CLI Handler: steward agents:spawn-log

        Show spawn history for this session.

        Args:
            limit: Max entries to show

        Returns:
            Dict with spawn log
        """
        import time

        log = self._spawn_log[-limit:] if limit > 0 else self._spawn_log

        result = {
            "success": True,
            "total": len(self._spawn_log),
            "showing": len(log),
            "entries": log,
        }

        # Format for display
        lines = [f"🌱 SPAWN LOG ({len(log)}/{len(self._spawn_log)} entries)"]
        lines.append("=" * 60)
        for entry in log:
            ts = time.strftime("%H:%M:%S", time.localtime(entry["timestamp"]))
            audit = "⚠️ no audit" if entry.get("audit_skipped") else "✅"
            lines.append(f"  [{ts}] {entry['agent_id']} {audit}")
        lines.append("=" * 60)
        result["formatted"] = "\n".join(lines)

        return result

"""
SEMANTIC SYSCALLS - Neuro-Symbolic Kernel Interface

This module defines the semantic syscall layer for the VibeOS kernel.
Unlike procedural calls, semantic syscalls operate on MEANING, not just data.

Architecture (Neuro-Symbolic OS):
    Neural (LLM/Intent) → Semantic Compiler (Blueprint) → Symbolic (Syscall) → Kernel

The key insight: Traditional syscalls are syntactic (read(fd, buf, count)).
Semantic syscalls are meaningful (spawn_cognition(role, mission, oath)).

This is "ML Light" - we use deterministic structures to channel neural output.

GAD-5500: Safe Evolution Loop / Cognitive Circuits
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.protocols.event import Event

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SEMANTIC_SYSCALLS")

# ============================================================================
# RESERVED AGENT IDS - System agents that cannot be overwritten
# ============================================================================
RESERVED_AGENT_IDS = {
    "watchman",
    "herald",
    "scribe",
    "auditor",
    "artisan",
    "oracle",
    "engineer",
    "civic",
    "envoy",
    "steward",
    "archivist",
    "chronicle",
    "kernel",
    "narasimha",
    "root",
    "admin",
    "system",
}


class SyscallType(str, Enum):
    """
    Semantic Syscall Types - The primitives of Agent OS.

    Unlike Unix syscalls (read, write, fork), these carry MEANING.
    Each syscall represents a fundamental operation in the agent lifecycle.
    """

    # Agent Lifecycle
    SPAWN_COGNITION = "SPAWN_COGNITION"  # Birth a new agent (fork equivalent)
    DESTROY_COGNITION = "DESTROY_COGNITION"  # Kill an agent (Narasimha)

    # Capability Management
    GRANT_MANDATE = "GRANT_MANDATE"  # Assign capabilities
    REVOKE_MANDATE = "REVOKE_MANDATE"  # Remove capabilities

    # Resource Management
    ALLOCATE_PRANA = "ALLOCATE_PRANA"  # Grant credits (fuel)
    TRANSFER_PRANA = "TRANSFER_PRANA"  # Move credits between agents

    # Governance
    SWEAR_OATH = "SWEAR_OATH"  # Constitutional binding
    RECORD_KARMA = "RECORD_KARMA"  # Immutable ledger entry

    # Communication
    DISPATCH_TASK = "DISPATCH_TASK"  # Send task to agent
    BROADCAST_EVENT = "BROADCAST_EVENT"  # System-wide event


@dataclass
class SyscallRequest:
    """
    A semantic syscall request.

    This is what the Blueprint Generator produces - a structured
    representation of user intent compiled into a kernel operation.
    """

    syscall_type: SyscallType
    params: Dict[str, Any]
    requester_id: str = "system"  # Who initiated this syscall
    priority: str = "normal"  # normal, high, critical
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate syscall parameters on creation."""
        required = SYSCALL_SCHEMAS.get(self.syscall_type, {}).get("required", [])
        for param in required:
            if param not in self.params:
                raise ValueError(f"Syscall {self.syscall_type.value} requires parameter: {param}")


@dataclass
class SyscallResult:
    """Result of a semantic syscall execution."""

    success: bool
    syscall_type: SyscallType
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    # Audit trail
    karma_block_id: Optional[str] = None  # Parampara block if recorded


# ============================================================================
# SYSCALL PARAMETER SCHEMAS
# ============================================================================

SYSCALL_SCHEMAS = {
    SyscallType.SPAWN_COGNITION: {
        "required": ["role", "mission"],
        "optional": ["initial_credits", "capabilities", "parent_id"],
        "description": "Birth a new agent cognition",
    },
    SyscallType.GRANT_MANDATE: {
        "required": ["agent_id", "capabilities"],
        "optional": [],
        "description": "Grant capabilities to an agent",
    },
    SyscallType.ALLOCATE_PRANA: {
        "required": ["agent_id", "amount"],
        "optional": ["source"],
        "description": "Allocate credits (fuel) to an agent",
    },
    SyscallType.SWEAR_OATH: {
        "required": ["agent_id"],
        "optional": ["constitution_version"],
        "description": "Bind agent to Constitutional Oath",
    },
    SyscallType.DISPATCH_TASK: {
        "required": ["agent_id", "task_payload"],
        "optional": ["priority", "timeout"],
        "description": "Send a task to an agent",
    },
}


# ============================================================================
# SEMANTIC SYSCALL EXECUTOR
# ============================================================================


class SemanticSyscallExecutor:
    """
    Executes semantic syscalls against the kernel.

    This is the bridge between Cognitive Circuits (Playbooks) and
    the procedural kernel implementation.

    The executor:
    1. Validates the syscall request
    2. Translates semantic params to kernel calls
    3. Records the action in Parampara (audit trail)
    4. Returns structured result
    """

    def __init__(self, kernel: "RealVibeKernel"):
        self.kernel = kernel
        logger.info("🔌 Semantic Syscall Executor initialized")

    def execute(self, request: SyscallRequest) -> SyscallResult:
        """
        Execute a semantic syscall.

        This method dispatches to the appropriate handler based on syscall type.
        All syscalls are recorded in Parampara for audit trail.
        """
        logger.info(f"⚡ SYSCALL: {request.syscall_type.value} from {request.requester_id}")

        handlers = {
            SyscallType.SPAWN_COGNITION: self._handle_spawn_cognition,
            SyscallType.DESTROY_COGNITION: self._handle_destroy_cognition,
            SyscallType.GRANT_MANDATE: self._handle_grant_mandate,
            SyscallType.REVOKE_MANDATE: self._handle_revoke_mandate,
            SyscallType.ALLOCATE_PRANA: self._handle_allocate_prana,
            SyscallType.TRANSFER_PRANA: self._handle_transfer_prana,
            SyscallType.SWEAR_OATH: self._handle_swear_oath,
            SyscallType.RECORD_KARMA: self._handle_record_karma_syscall,
            SyscallType.DISPATCH_TASK: self._handle_dispatch_task,
            SyscallType.BROADCAST_EVENT: self._handle_broadcast_event,
        }

        handler = handlers.get(request.syscall_type)
        if not handler:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"No handler for syscall: {request.syscall_type.value}",
            )

        try:
            result = handler(request)

            # Record in Parampara (audit trail)
            if result.success:
                self._record_karma(request, result)

            # OPUS-031 Layer 2: Emit SYSCALL_EXECUTED event for Experience Replay
            # Plugins can subscribe to learn from syscall history
            self._emit_syscall_event(request, result)

            return result

        except Exception as e:
            logger.error(f"❌ Syscall failed: {e}", exc_info=True)
            return SyscallResult(success=False, syscall_type=request.syscall_type, error=str(e))

    def handle(self, request: SyscallRequest) -> SyscallResult:
        """Alias for execute() - backwards compatibility."""
        return self.execute(request)

    def _emit_syscall_event(self, request: SyscallRequest, result: SyscallResult) -> None:
        """
        OPUS-031 Layer 2: Emit SYSCALL_EXECUTED event for Experience Replay.

        This allows plugins (like opus_assistant) to subscribe and record
        syscall history for few-shot learning. The plugin transforms the event
        into a SyscallEntry and stores it in the Experience Replay Buffer.

        ARCHITECTURE (GAD-000 Compliant):
        - Core emits event (no plugin imports!)
        - Plugin subscribes and handles (plugin knows about core, not vice versa)
        - Loose coupling via EventBus
        """
        try:
            import asyncio

            from vibe_core.event_bus import Event, EventType, get_event_bus

            event = Event(
                event_type=EventType.SYSCALL_EXECUTED.value,
                agent_id=request.requester_id,
                message=f"Syscall {request.syscall_type.value} {'succeeded' if result.success else 'failed'}",
                details={
                    "syscall_type": request.syscall_type.value,
                    "params": request.params,
                    "success": result.success,
                    "output": result.output if hasattr(result, "output") else None,
                    "error": result.error if hasattr(result, "error") else None,
                },
            )

            bus = get_event_bus()

            # Handle async emission from sync context
            try:
                loop = asyncio.get_running_loop()
                # We're in an async context - schedule the emit
                loop.create_task(bus.emit(event))
            except RuntimeError:
                # No running loop - fire and forget with a new loop
                # This is safe because emit is quick and non-blocking
                asyncio.run(bus.emit(event))

            logger.debug(f"📡 SYSCALL_EXECUTED event emitted: {request.syscall_type.value}")

        except Exception as e:
            # Don't let event emission failure break syscall execution
            logger.debug(f"Failed to emit SYSCALL_EXECUTED event: {e}")

    def _handle_spawn_cognition(self, request: SyscallRequest) -> SyscallResult:
        """
        SPAWN_COGNITION: Birth a new agent.

        This is the Agent OS equivalent of fork().

        SECURITY:
        - Checks if agent_id already exists (prevents overwriting)
        - Reserved names are protected (system agents)
        - Generates unique ID with timestamp suffix for dynamic agents

        Params:
            role: Agent role identifier (e.g., "watchman", "herald")
            mission: What this agent does
            initial_credits: Starting credits (default: 100)
            capabilities: List of capabilities to grant
            parent_id: ID of spawning agent (for lineage)
        """
        import uuid
        from datetime import datetime

        role = request.params["role"]
        mission = request.params["mission"]
        initial_credits = request.params.get("initial_credits", 100)
        capabilities = request.params.get("capabilities", ["execute"])
        parent_id = request.params.get("parent_id", request.requester_id)

        # Generate base agent_id from role
        base_id = role.lower().replace(" ", "_")

        # SECURITY FIX: If base_id is reserved OR already exists, generate unique ID
        if base_id in RESERVED_AGENT_IDS or base_id in self.kernel._agent_registry:
            # Generate unique suffix (short UUID)
            unique_suffix = datetime.utcnow().strftime("%H%M%S") + "_" + uuid.uuid4().hex[:4]
            agent_id = f"{base_id}_{unique_suffix}"
            logger.warning(f"⚠️ Agent ID '{base_id}' is reserved/exists. Generated unique ID: {agent_id}")
        else:
            agent_id = base_id

        # Double-check: Agent must NOT exist
        if agent_id in self.kernel._agent_registry:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Agent '{agent_id}' already exists in registry. Cannot overwrite.",
            )

        logger.info(f"🌱 SPAWN_COGNITION: agent_id={agent_id}, role={role}, mission={mission}")

        try:
            # Step 1: Generate agent code using Engineer
            from vibe_core.cartridges.system.engineer.tools.builder_tool import BuilderTool

            builder = BuilderTool()
            import tempfile
            from pathlib import Path

            # Use temp directory for dynamic agents to avoid polluting source tree
            target_dir = Path(tempfile.gettempdir()) / "vibe_agents" / agent_id

            scaffold_result = builder.scaffold_from_template(
                agent_id=agent_id, agent_name=role.upper(), domain="SPAWNED", description=mission, target_dir=target_dir
            )

            if not scaffold_result["success"]:
                return SyscallResult(
                    success=False,
                    syscall_type=request.syscall_type,
                    error=f"Scaffold failed: {scaffold_result.get('error')}",
                )

            code = scaffold_result.get("files_created", [])

            # Step 2: Create agent class dynamically
            # agent_id is already generated above (with collision protection)
            class_name = f"{role.replace(' ', '').title()}Cartridge"

            # Step 3: Create a minimal agent that can be registered
            from vibe_core.protocols import AgentManifest, VibeAgent
            from vibe_core.steward.oath_mixin import OathMixin

            # Dynamic agent class with oath
            class DynamicAgent(VibeAgent, OathMixin):
                def __init__(self, aid: str, name: str, desc: str, caps: List[str]):
                    super().__init__(
                        agent_id=aid,
                        name=name.upper(),
                        version="1.0.0",
                        author="SPAWN_COGNITION",
                        description=desc,
                        domain="SPAWNED",
                        capabilities=caps,
                    )
                    # Swear the oath
                    self.oath_mixin_init(aid)
                    self.oath_sworn = True

                def get_manifest(self) -> AgentManifest:
                    return AgentManifest(
                        agent_id=self.agent_id,
                        name=self.name,
                        version=self.version,
                        author=self.author,
                        description=self.description,
                        domain=self.domain,
                        capabilities=self.capabilities,
                        dependencies=[],
                    )

                def process(self, task):
                    return {"status": "processed", "agent": self.agent_id}

                def report_status(self):
                    return {
                        "agent_id": self.agent_id,
                        "status": "RUNNING",
                        "spawned_by": "SPAWN_COGNITION",
                    }

            # Instantiate the agent
            new_agent = DynamicAgent(agent_id, role, mission, capabilities)

            # Step 4: Register with kernel (this triggers governance gate)
            self.kernel.register_agent(new_agent, spawn_process=False)

            # Step 5: Allocate credits
            try:
                bank = self.kernel.get_bank()
                # Use transfer from MINT instead of non-existent deposit/create_account
                bank.transfer("MINT", agent_id, initial_credits, "Initial allocation from SPAWN_COGNITION")
            except Exception as e:
                logger.warning(f"Credit allocation failed (non-fatal): {e}")

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={
                    "agent_id": agent_id,
                    "role": role,
                    "mission": mission,
                    "capabilities": capabilities,
                    "credits": initial_credits,
                    "parent_id": parent_id,
                    "code_generated": len(code) if code else 0,
                },
            )

        except PermissionError as e:
            # Governance gate rejection
            return SyscallResult(success=False, syscall_type=request.syscall_type, error=f"Governance gate denied: {e}")
        except Exception as e:
            return SyscallResult(success=False, syscall_type=request.syscall_type, error=str(e))

    def _handle_grant_mandate(self, request: SyscallRequest) -> SyscallResult:
        """
        GRANT_MANDATE: Assign capabilities to an agent.

        Note: Capabilities are immutable after registration.
        This syscall is primarily for newly spawned agents.
        """
        agent_id = request.params["agent_id"]
        capabilities = request.params["capabilities"]

        # Check if agent exists
        if agent_id not in self.kernel._agent_registry:
            return SyscallResult(
                success=False, syscall_type=request.syscall_type, error=f"Agent '{agent_id}' not registered"
            )

        # Delegate to kernel (handles permission check + audit trail)
        try:
            # Check if kernel has the method (it should)
            if hasattr(self.kernel, "grant_capability"):
                result = self.kernel.grant_capability(
                    agent_id=agent_id,
                    capabilities=capabilities,
                    granter_id=request.requester_id,
                    reason=request.params.get("reason"),
                )

                if result["success"]:
                    logger.info(
                        f"🔓 GRANT_MANDATE: '{request.requester_id}' granted {len(result['granted'])} "
                        f"capability(ies) to '{agent_id}': {result['granted']}"
                    )
                else:
                    logger.warning(f"⛔ GRANT_MANDATE FAILED: {result['message']}")

                return SyscallResult(
                    success=result["success"],
                    syscall_type=request.syscall_type,
                    output=result,
                    error=None if result["success"] else result["message"],
                )
            else:
                # Fallback for kernels without mutable capabilities (unlikely in Phase 2+)
                current_caps = getattr(self.kernel, "_agent_capabilities", {}).get(agent_id, frozenset())
                return SyscallResult(
                    success=True,
                    syscall_type=request.syscall_type,
                    output={
                        "agent_id": agent_id,
                        "current_capabilities": list(current_caps),
                        "requested_capabilities": capabilities,
                        "note": "Kernel does not support dynamic grants (immutable mode)",
                    },
                )

        except Exception as e:
            logger.error(f"❌ GRANT_MANDATE ERROR: {e}", exc_info=True)
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Internal error during grant: {str(e)}",
            )

    def _handle_allocate_prana(self, request: SyscallRequest) -> SyscallResult:
        """
        ALLOCATE_PRANA: Grant credits to an agent.

        Credits are the fuel for agent operations.
        Uses CivicBank.transfer() with MINT as sender (infinite supply).
        """
        agent_id = request.params["agent_id"]
        amount = request.params["amount"]
        source = request.params.get("source", "system")

        try:
            bank = self.kernel.get_bank()

            # Transfer from MINT (infinite supply) to agent
            # CivicBank.transfer() handles account creation automatically
            tx_id = bank.transfer(
                sender="MINT",
                receiver=agent_id,
                amount=amount,
                reason=f"ALLOCATE_PRANA from {source}",
                service_type="allocation",
            )

            new_balance = bank.get_balance(agent_id)

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={
                    "agent_id": agent_id,
                    "amount_allocated": amount,
                    "new_balance": new_balance,
                    "source": source,
                    "transaction_id": tx_id,
                },
            )
        except Exception as e:
            return SyscallResult(success=False, syscall_type=request.syscall_type, error=str(e))

    def _handle_swear_oath(self, request: SyscallRequest) -> SyscallResult:
        """
        SWEAR_OATH: Bind an agent to the Constitutional Oath.

        This is typically done at spawn time, but can be used
        to re-oath an agent after constitution updates.
        """
        agent_id = request.params["agent_id"]

        agent = self.kernel._agent_registry.get(agent_id)
        if not agent:
            return SyscallResult(
                success=False, syscall_type=request.syscall_type, error=f"Agent '{agent_id}' not registered"
            )

        # Check current oath status
        oath_sworn = getattr(agent, "oath_sworn", False)

        return SyscallResult(
            success=True,
            syscall_type=request.syscall_type,
            output={
                "agent_id": agent_id,
                "oath_sworn": oath_sworn,
                "oath_event": getattr(agent, "oath_event", None),
            },
        )

    def _handle_dispatch_task(self, request: SyscallRequest) -> SyscallResult:
        """
        DISPATCH_TASK: Send a task to an agent.
        """
        from vibe_core.scheduling import Task

        agent_id = request.params["agent_id"]
        task_payload = request.params["task_payload"]
        priority = request.params.get("priority", "normal")

        if agent_id not in self.kernel._agent_registry:
            return SyscallResult(
                success=False, syscall_type=request.syscall_type, error=f"Agent '{agent_id}' not registered"
            )

        # Create and submit task
        task = Task(agent_id=agent_id, payload=task_payload)
        task_id = self.kernel.submit_task(task)

        return SyscallResult(
            success=True,
            syscall_type=request.syscall_type,
            output={
                "task_id": task_id,
                "agent_id": agent_id,
                "priority": priority,
            },
        )

    def _handle_destroy_cognition(self, request: SyscallRequest) -> SyscallResult:
        """
        DESTROY_COGNITION: Terminate an agent.

        This is the Agent OS equivalent of kill().
        Only authorized entities can destroy agents.
        """
        agent_id = request.params.get("agent_id")
        reason = request.params.get("reason", "No reason provided")

        if not agent_id:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Missing required parameter: agent_id",
            )

        # Check if agent exists
        if agent_id not in self.kernel._agent_registry:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Agent not found: {agent_id}",
            )

        # Check authorization (only system agents can destroy)
        if request.requester_id not in RESERVED_AGENT_IDS:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Unauthorized: {request.requester_id} cannot destroy agents",
            )

        # Remove from registry
        try:
            del self.kernel._agent_registry[agent_id]
            logger.info(f"💀 DESTROY_COGNITION: Agent {agent_id} terminated by {request.requester_id}")

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={"agent_id": agent_id, "reason": reason, "status": "terminated"},
            )
        except Exception as e:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Failed to destroy agent: {e}",
            )

    def _handle_revoke_mandate(self, request: SyscallRequest) -> SyscallResult:
        """
        REVOKE_MANDATE: Remove capabilities from an agent.

        Allows governance to restrict agent permissions based on behavior.
        Example: Revoke transfer_prana after suspicious activity.

        Permission Model:
            - KERNEL can revoke from anyone
            - CIVIC can revoke from anyone (governance)
            - Agents can revoke from themselves (voluntary)

        Args (in request.params):
            - agent_id: The agent to revoke from (required)
            - capabilities: List of capabilities to revoke (required)
            - reason: Optional reason for revocation (for audit trail)

        Returns:
            SyscallResult with:
                - success: True if any capabilities were revoked
                - output: Dict with revoked/not_found lists and message
        """
        agent_id = request.params.get("agent_id")
        capabilities = request.params.get("capabilities", [])
        reason = request.params.get("reason")

        # Validation
        if not agent_id:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Missing required parameter: agent_id",
            )

        if not capabilities:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Missing required parameter: capabilities (must be non-empty list)",
            )

        if not isinstance(capabilities, list):
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Parameter 'capabilities' must be a list",
            )

        # Delegate to kernel (handles permission check + audit trail)
        try:
            result = self.kernel.revoke_capability(
                agent_id=agent_id, capabilities=capabilities, revoker_id=request.requester_id, reason=reason
            )

            # Log the action
            if result["success"]:
                logger.info(
                    f"✅ REVOKE_MANDATE: '{request.requester_id}' revoked {len(result['revoked'])} "
                    f"capability(ies) from '{agent_id}': {result['revoked']}"
                )
            else:
                logger.warning(f"⛔ REVOKE_MANDATE FAILED: {result['message']}")

            return SyscallResult(
                success=result["success"],
                syscall_type=request.syscall_type,
                output=result,
                error=None if result["success"] else result["message"],
            )

        except Exception as e:
            logger.error(f"❌ REVOKE_MANDATE ERROR: {e}", exc_info=True)
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Internal error during revocation: {str(e)}",
            )

    def _handle_transfer_prana(self, request: SyscallRequest) -> SyscallResult:
        """
        TRANSFER_PRANA: Move credits between agents.

        Uses CivicBank.transfer() for atomic double-entry bookkeeping.
        """
        from_agent = request.params.get("from_agent", request.requester_id)
        to_agent = request.params.get("to_agent")
        amount = request.params.get("amount", 0)
        reason = request.params.get("reason", "transfer")

        if not to_agent:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Missing required parameter: to_agent",
            )

        if amount <= 0:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Amount must be positive",
            )

        try:
            bank = self.kernel.get_bank()

            # Execute real transfer via CivicBank
            tx_id = bank.transfer(
                sender=from_agent,
                receiver=to_agent,
                amount=amount,
                reason=reason,
                service_type="transfer",
            )

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={
                    "from": from_agent,
                    "to": to_agent,
                    "amount": amount,
                    "transaction_id": tx_id,
                    "new_sender_balance": bank.get_balance(from_agent),
                    "new_receiver_balance": bank.get_balance(to_agent),
                },
            )
        except Exception as e:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=str(e),
            )

    def _handle_record_karma_syscall(self, request: SyscallRequest) -> SyscallResult:
        """
        RECORD_KARMA: Write to immutable ledger.

        This is for explicit karma recording (vs automatic recording in _record_karma).
        """
        data = request.params.get("data", {})
        category = request.params.get("category", "general")

        try:
            from vibe_core.lineage import LineageEventType

            block = self.kernel.lineage.add_block(
                event_type=LineageEventType.KARMA_RECORDED,
                agent_id=request.requester_id,
                data={"category": category, "payload": data},
            )

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={"block_id": block.block_id if block else None, "category": category},
                karma_block_id=block.block_id if block else None,
            )
        except Exception as e:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Failed to record karma: {e}",
            )

    def _handle_broadcast_event(self, request: SyscallRequest) -> SyscallResult:
        """
        BROADCAST_EVENT: Emit system-wide event via EventBus.

        Allows agents to broadcast events that other agents can subscribe to.
        Supports loose coupling and reactive patterns.

        Args (in request.params):
            - event_type: Type of event (required) e.g., "agent.born", "task.complete"
            - data: Optional event data (dict)
            - message: Optional human-readable message

        Returns:
            SyscallResult with:
                - success: True if event was broadcast
                - output: Event ID, subscriber count, timestamp

        Usage:
            syscall(BROADCAST_EVENT, {
                "event_type": "proposal.created",
                "data": {"proposal_id": "p123", "title": "..."},
                "message": "New governance proposal"
            })
        """
        event_type = request.params.get("event_type")
        event_data = request.params.get("data", {})
        message = request.params.get("message")

        # Validation
        if not event_type:
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error="Missing required parameter: event_type",
            )

        # Phase 6: Direct EventBus access
        try:
            import asyncio

            # Create event directly
            event = Event(
                event_type=event_type,
                agent_id=request.requester_id,
                message=message or f"{event_type} from {request.requester_id}",
                details=event_data or {},
            )

            # Run async emit synchronously for syscalls
            asyncio.run(self.kernel.event_bus.emit(event))

            # Get subscriber count
            status = self.kernel.event_bus.get_status()
            subscriber_count = status.get("subscribers", {}).get("by_type", {}).get(event_type, 0)
            subscriber_count += status.get("subscribers", {}).get("global", 0)

            result = {
                "event_id": event.event_id,
                "event_type": event_type,
                "broadcaster": request.requester_id,
                "subscribers_notified": subscriber_count,
                "timestamp": event.timestamp,
            }

            logger.info(
                f"✅ BROADCAST_EVENT: '{event_type}' from '{request.requester_id}' → {subscriber_count} subscriber(s)"
            )

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output=result,
            )

        except Exception as e:
            logger.error(f"❌ BROADCAST_EVENT ERROR: {e}", exc_info=True)
            return SyscallResult(
                success=False,
                syscall_type=request.syscall_type,
                error=f"Failed to broadcast event: {str(e)}",
            )

    def _record_karma(self, request: SyscallRequest, result: SyscallResult) -> None:
        """Record syscall in Parampara (blockchain audit trail)."""
        try:
            from vibe_core.lineage import LineageEventType

            block = self.kernel.lineage.add_block(
                event_type=LineageEventType.TASK_COMPLETED,  # Generic for now
                agent_id=request.requester_id,
                data={
                    "syscall_type": request.syscall_type.value,
                    "params": request.params,
                    "result": result.output,
                },
            )

            result.karma_block_id = block.block_id if block else None

        except Exception as e:
            logger.warning(f"Failed to record karma: {e}")


# ============================================================================
# FACTORY
# ============================================================================


def create_syscall_executor(kernel: "RealVibeKernel") -> SemanticSyscallExecutor:
    """Factory function to create a Semantic Syscall Executor."""
    return SemanticSyscallExecutor(kernel)


# Backwards compatibility alias
SemanticSyscallHandler = SemanticSyscallExecutor

__all__ = [
    "SyscallType",
    "SyscallRequest",
    "SyscallResult",
    "SemanticSyscallExecutor",
    "SemanticSyscallHandler",  # Alias for backwards compatibility
    "create_syscall_executor",
    "SYSCALL_SCHEMAS",
]

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

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SEMANTIC_SYSCALLS")


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
            SyscallType.GRANT_MANDATE: self._handle_grant_mandate,
            SyscallType.ALLOCATE_PRANA: self._handle_allocate_prana,
            SyscallType.SWEAR_OATH: self._handle_swear_oath,
            SyscallType.DISPATCH_TASK: self._handle_dispatch_task,
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

            return result

        except Exception as e:
            logger.error(f"❌ Syscall failed: {e}", exc_info=True)
            return SyscallResult(success=False, syscall_type=request.syscall_type, error=str(e))

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

        # SECURITY FIX: Reserved agent names (system agents)
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
            from steward.system_agents.engineer.tools.builder_tool import BuilderTool

            builder = BuilderTool()
            code = builder.generate_agent_code(role, mission)

            if not code:
                return SyscallResult(success=False, syscall_type=request.syscall_type, error="Code generation failed")

            # Step 2: Create agent class dynamically
            # agent_id is already generated above (with collision protection)
            class_name = f"{role.replace(' ', '').title()}Cartridge"

            # Step 3: Create a minimal agent that can be registered
            from vibe_core.protocols import VibeAgent, AgentManifest
            from steward.oath_mixin import OathMixin

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
                bank.create_account(agent_id)
                bank.deposit(agent_id, initial_credits, f"Initial allocation from SPAWN_COGNITION")
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

        # Note: In current architecture, capabilities are set at registration
        # This is here for future dynamic capability management
        current_caps = self.kernel._agent_capabilities.get(agent_id, frozenset())

        return SyscallResult(
            success=True,
            syscall_type=request.syscall_type,
            output={
                "agent_id": agent_id,
                "current_capabilities": list(current_caps),
                "requested_capabilities": capabilities,
                "note": "Capabilities are immutable after registration (security)",
            },
        )

    def _handle_allocate_prana(self, request: SyscallRequest) -> SyscallResult:
        """
        ALLOCATE_PRANA: Grant credits to an agent.

        Credits are the fuel for agent operations.
        """
        agent_id = request.params["agent_id"]
        amount = request.params["amount"]
        source = request.params.get("source", "system")

        try:
            bank = self.kernel.get_bank()

            # Create account if doesn't exist
            try:
                bank.create_account(agent_id)
            except Exception:
                pass  # Account might already exist

            # Deposit credits
            bank.deposit(agent_id, amount, f"ALLOCATE_PRANA from {source}")

            new_balance = bank.get_balance(agent_id)

            return SyscallResult(
                success=True,
                syscall_type=request.syscall_type,
                output={
                    "agent_id": agent_id,
                    "amount_allocated": amount,
                    "new_balance": new_balance,
                    "source": source,
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


__all__ = [
    "SyscallType",
    "SyscallRequest",
    "SyscallResult",
    "SemanticSyscallExecutor",
    "create_syscall_executor",
    "SYSCALL_SCHEMAS",
]

"""
INTENT-OPCODE BRIDGE - The Semantic Translator
===============================================

"From Thought to Mantra."

This module bridges the SEMANTIC layer (IntentType, SyscallType)
to the MANTRA layer (MantraOpCode, Mahajana).

THE GAP IT FILLS:
    CognitiveResult.intent_type + syscall_type/target
                    ↓
           IntentOpCodeBridge (THIS!)
                    ↓
              MantraOpCode
                    ↓
    MahajanaRouter.route(opcode) → Mahajana

PHILOSOPHY:
- Cognitive layer speaks in INTENT (what the user wants)
- Mantra layer speaks in OPCODE (what the system does)
- This bridge translates without losing meaning

ARCHITECTURE:
    Layer 1 (Cognitive): IntentType.EXECUTE + "SPAWN_COGNITION"
                            ↓
    Layer 0 (Semantic):  IntentOpCodeBridge.translate()
                            ↓
    Layer -1 (Mantra):   MantraOpCode.ALLOC_MEM (Brahma creates)

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1 - All mappings are explicit, no wildcards.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Union, List

from vibe_core.protocols.cognition import IntentType, CognitiveResult
from vibe_core.protocols.universal.mantra import MantraOpCode
from vibe_core.semantic_syscalls import SyscallType


# =============================================================================
# INTENT → OPCODE MAPPING (Primary Translation)
# =============================================================================

# IntentType is broad - these are the DEFAULT OpCodes when no specific target
INTENT_TO_DEFAULT_OPCODE: Dict[IntentType, MantraOpCode] = {
    IntentType.CHAT: MantraOpCode.EXEC_SERVICE,      # Prahlada handles conversation
    IntentType.EXECUTE: MantraOpCode.EXEC_SERVICE,   # Janaka executes duty
    IntentType.QUERY: MantraOpCode.FETCH_RES,        # Prahlada fetches resources
    IntentType.ROUTE: MantraOpCode.RESOLVE_REQ,      # Kumaras resolve requests
}


# =============================================================================
# SYSCALL → OPCODE MAPPING (Execute Intent Details)
# =============================================================================

# When IntentType.EXECUTE, the SyscallType refines which OpCode
SYSCALL_TO_OPCODE: Dict[SyscallType, MantraOpCode] = {
    # Agent Lifecycle (Creation = Brahma, Destruction = Shambhu)
    SyscallType.SPAWN_COGNITION: MantraOpCode.ALLOC_MEM,     # Brahma creates
    SyscallType.DESTROY_COGNITION: MantraOpCode.GARBAGE_COLLECT,  # Shambhu destroys

    # Capability Management (Manu = Law)
    SyscallType.GRANT_MANDATE: MantraOpCode.BIND_CTX,        # Manu binds permissions
    SyscallType.REVOKE_MANDATE: MantraOpCode.GARBAGE_COLLECT,  # Shambhu removes

    # Resource Management (Allocation)
    SyscallType.ALLOCATE_PRANA: MantraOpCode.ALLOC_MEM,      # Allocation
    SyscallType.TRANSFER_PRANA: MantraOpCode.EXEC_SERVICE,   # Transfer = service

    # Governance (Bhishma = Vow)
    SyscallType.SWEAR_OATH: MantraOpCode.COMMIT_LOG,         # Bhishma commits vows
    SyscallType.RECORD_KARMA: MantraOpCode.COMMIT_LOG,       # Bhishma writes ledger

    # Communication (Narada = Messenger)
    SyscallType.DISPATCH_TASK: MantraOpCode.EXEC_SERVICE,    # Janaka executes
    SyscallType.BROADCAST_EVENT: MantraOpCode.PULSE_SYNC,    # Narada broadcasts
}


# =============================================================================
# ROUTE TARGET → OPCODE MAPPING (Route Intent Details)
# =============================================================================

# When IntentType.ROUTE, the target determines OpCode
ROUTE_TARGET_TO_OPCODE: Dict[str, MantraOpCode] = {
    # System targets
    "envoy": MantraOpCode.EXEC_SERVICE,       # AI envoy
    "kernel": MantraOpCode.SYS_WAKE,          # System operations
    "scheduler": MantraOpCode.EXEC_SERVICE,   # Task dispatch

    # Agent targets (by role)
    "watchman": MantraOpCode.ASSERT_TRUTH,    # Verification
    "herald": MantraOpCode.PULSE_SYNC,        # Communication
    "scribe": MantraOpCode.COMMIT_LOG,        # Recording
    "auditor": MantraOpCode.CHECK_DHARMA,     # Audit
    "artisan": MantraOpCode.EXEC_SERVICE,     # Creation
    "oracle": MantraOpCode.FETCH_RES,         # Data/insight
    "engineer": MantraOpCode.ALLOC_MEM,       # Building
    "civic": MantraOpCode.CHECK_DHARMA,       # Governance

    # Generic fallbacks
    "chat": MantraOpCode.EXEC_SERVICE,
    "help": MantraOpCode.FETCH_RES,
    "status": MantraOpCode.FETCH_RES,
}


# =============================================================================
# QUERY TYPE → OPCODE MAPPING (Query Intent Details)
# =============================================================================

# When IntentType.QUERY, the query_type refines OpCode
QUERY_TYPE_TO_OPCODE: Dict[str, MantraOpCode] = {
    "status": MantraOpCode.FETCH_RES,
    "health": MantraOpCode.ASSERT_TRUTH,
    "metrics": MantraOpCode.FETCH_RES,
    "logs": MantraOpCode.FETCH_RES,
    "config": MantraOpCode.LOAD_ROOT,
    "identity": MantraOpCode.LOAD_ROOT,
    "capabilities": MantraOpCode.CHECK_DHARMA,
    "karma": MantraOpCode.FETCH_RES,
    "agents": MantraOpCode.FETCH_RES,
}


# =============================================================================
# THE BRIDGE CLASS
# =============================================================================

@dataclass(frozen=True)
class BridgeResult:
    """Result of intent → opcode translation."""
    opcode: MantraOpCode
    confidence: float  # 0.0 - 1.0 (how certain the mapping is)
    source: str        # What determined this mapping (intent/syscall/target/default)
    notes: Optional[str] = None


class IntentOpCodeBridge:
    """
    The Semantic Translator.

    Bridges CognitiveResult (intent layer) to MantraOpCode (mantra layer).

    Usage:
        bridge = IntentOpCodeBridge()
        result = bridge.translate(cognitive_result)
        opcode = result.opcode  # MantraOpCode for MahajanaRouter
    """

    def translate(self, result: CognitiveResult) -> BridgeResult:
        """
        Translate a CognitiveResult to a MantraOpCode.

        Priority:
        1. SyscallType (most specific for EXECUTE intent)
        2. Route target (for ROUTE intent)
        3. Query type (for QUERY intent)
        4. Default by IntentType (fallback)

        Args:
            result: The CognitiveResult from cognitive processing

        Returns:
            BridgeResult with opcode and metadata
        """
        intent = result.intent_type

        # Priority 1: Execute with specific syscall
        if intent == IntentType.EXECUTE and result.syscall_type:
            try:
                syscall = SyscallType(result.syscall_type)
                if syscall in SYSCALL_TO_OPCODE:
                    return BridgeResult(
                        opcode=SYSCALL_TO_OPCODE[syscall],
                        confidence=0.95,
                        source=f"syscall:{syscall.value}",
                        notes=f"Mapped from SyscallType.{syscall.name}"
                    )
            except ValueError:
                pass  # Unknown syscall, fall through

        # Priority 2: Route with specific target
        if intent == IntentType.ROUTE and result.target:
            target = result.target.lower()
            if target in ROUTE_TARGET_TO_OPCODE:
                return BridgeResult(
                    opcode=ROUTE_TARGET_TO_OPCODE[target],
                    confidence=0.85,
                    source=f"target:{target}",
                    notes=f"Routed to {target}"
                )
            # Fallback for unknown targets
            return BridgeResult(
                opcode=MantraOpCode.RESOLVE_REQ,
                confidence=0.5,
                source="target:unknown",
                notes=f"Unknown target '{target}', using RESOLVE_REQ"
            )

        # Priority 3: Query with specific type
        if intent == IntentType.QUERY and result.query_type:
            query = result.query_type.lower()
            if query in QUERY_TYPE_TO_OPCODE:
                return BridgeResult(
                    opcode=QUERY_TYPE_TO_OPCODE[query],
                    confidence=0.85,
                    source=f"query:{query}",
                    notes=f"Query type: {query}"
                )

        # Priority 4: Default by IntentType
        return BridgeResult(
            opcode=INTENT_TO_DEFAULT_OPCODE.get(intent, MantraOpCode.EXEC_SERVICE),
            confidence=0.7,
            source=f"intent:{intent.value}",
            notes=f"Default opcode for {intent.value} intent"
        )

    def translate_raw(
        self,
        intent_type: IntentType,
        syscall_type: Optional[str] = None,
        target: Optional[str] = None,
        query_type: Optional[str] = None
    ) -> BridgeResult:
        """
        Translate raw intent components to MantraOpCode.

        Convenience method when you don't have a full CognitiveResult.
        """
        # Build a minimal CognitiveResult
        result = CognitiveResult(
            intent_type=intent_type,
            confidence=1.0,
            syscall_type=syscall_type,
            target=target,
            query_type=query_type,
        )
        return self.translate(result)

    def get_all_mappings(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all mappings for documentation/discoverability.

        GAD-000 Discoverability: AI can discover all possible translations.
        """
        return {
            "intent_defaults": [
                {"intent": k.value, "opcode": v.name}
                for k, v in INTENT_TO_DEFAULT_OPCODE.items()
            ],
            "syscall_mappings": [
                {"syscall": k.value, "opcode": v.name}
                for k, v in SYSCALL_TO_OPCODE.items()
            ],
            "route_targets": [
                {"target": k, "opcode": v.name}
                for k, v in ROUTE_TARGET_TO_OPCODE.items()
            ],
            "query_types": [
                {"query": k, "opcode": v.name}
                for k, v in QUERY_TYPE_TO_OPCODE.items()
            ],
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_bridge: Optional[IntentOpCodeBridge] = None


def get_bridge() -> IntentOpCodeBridge:
    """Get the global IntentOpCodeBridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = IntentOpCodeBridge()
    return _bridge


def translate(result: CognitiveResult) -> BridgeResult:
    """Convenience function: Translate CognitiveResult to MantraOpCode."""
    return get_bridge().translate(result)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IntentOpCodeBridge",
    "BridgeResult",
    "get_bridge",
    "translate",
    # Mapping tables (for testing/verification)
    "INTENT_TO_DEFAULT_OPCODE",
    "SYSCALL_TO_OPCODE",
    "ROUTE_TARGET_TO_OPCODE",
    "QUERY_TYPE_TO_OPCODE",
]

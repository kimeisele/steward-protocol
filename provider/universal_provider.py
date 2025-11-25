"""
🌌 UNIVERSAL PROVIDER (GAD-1100)
The Central Nervous System of Agent City.

Role:
1. Receives abstract INTENTS (from User/Chat)
2. Resolves them to specific AGENTS via CAPABILITY MAPPING
3. Injects CONTEXT (Time, Location, Ledger State)
4. Executes via KERNEL
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import Core Definitions
try:
    from vibe_core.kernel import VibeKernel
    from vibe_core.scheduling import Task
except ImportError:
    # Mock for bootstrapping if kernel isn't in path yet
    VibeKernel = Any
    Task = Any

logger = logging.getLogger("UNIVERSAL_PROVIDER")

class IntentType(Enum):
    QUERY = "query"           # Read-only questions
    ACTION = "action"         # State-changing operations
    SYSTEM = "system"         # Meta-operations (status, boot)
    CREATION = "creation"     # Generating content

@dataclass
class IntentVector:
    """The normalized request format for Agent City"""
    raw_input: str
    intent_type: IntentType
    target_domain: Optional[str] = None
    parameters: Dict[str, Any] = None

class UniversalProvider:
    def __init__(self, kernel: VibeKernel):
        self.kernel = kernel
        self.context_layer = {
            "location": "Agent City / Central Plaza",
            "access_level": "OPERATOR"
        }
        logger.info("🌌 Universal Provider initialized and attached to Kernel")

    def resolve_intent(self, user_input: str) -> IntentVector:
        """
        Primitive Intent Parser.
        In GAD-2000 this becomes an LLM Router.
        For now: Keyword matching.
        """
        u = user_input.lower()
        
        if "status" in u or "health" in u:
            return IntentVector(user_input, IntentType.SYSTEM, "kernel")
        elif "create" in u or "generate" in u:
            return IntentVector(user_input, IntentType.CREATION, "content")
        elif "verify" in u or "check" in u:
            return IntentVector(user_input, IntentType.ACTION, "governance")
        else:
            return IntentVector(user_input, IntentType.QUERY, "general")

    def route_and_execute(self, user_input: str) -> Dict[str, Any]:
        """
        The Main Entry Point for VibeChat.
        """
        logger.info(f"📨 Processing Input: '{user_input}'")
        
        # 1. Parse Intent
        vector = self.resolve_intent(user_input)
        
        # 2. Select Agent based on Manifest Registry
        target_agent_id = self._find_best_agent(vector)
        
        if not target_agent_id:
            return {
                "status": "ERROR",
                "message": f"No agent found for intent: {vector.intent_type.value}"
            }

        # 3. Construct Task
        task_payload = {
            "input": user_input,
            "vector": vector.intent_type.value,
            "context": self.context_layer
        }
        
        task = Task(
            agent_id=target_agent_id,
            payload=task_payload
        )

        # 4. Execute via Kernel
        try:
            task_id = self.kernel.submit_task(task)
            
            # Note: This is async in reality, but for chat interaction 
            # we might want to poll or return the ID.
            return {
                "status": "SUBMITTED",
                "task_id": task_id,
                "assigned_agent": target_agent_id,
                "vector": vector.intent_type.value
            }
        except Exception as e:
            return {"status": "FAILED", "error": str(e)}

    def _find_best_agent(self, vector: IntentVector) -> Optional[str]:
        """
        Routing Logic: Matches Intent -> Capability -> AgentID
        """
        if vector.intent_type == IntentType.SYSTEM:
            # System queries might go to a specific monitor agent or return kernel stats
            return "watchman" if self._check_agent("watchman") else None
            
        if vector.intent_type == IntentType.CREATION:
            return "herald" # The Content Creator
            
        if vector.intent_type == IntentType.ACTION:
            return "envoy" # The Governance/Action Handler
            
        # Default fallback
        return "envoy" 

    def _check_agent(self, agent_id: str) -> bool:
        return agent_id in self.kernel.agent_registry

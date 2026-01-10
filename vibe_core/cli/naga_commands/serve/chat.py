"""
CHAT COMMAND - PRAHLADA's Service (Universal Router)
=====================================================

MAHAJANA: PRAHLADA (The Resilient)
OPCODE: EXEC_SERVICE (Position 9)
PHASE: SERVE

WHY PRAHLADA?
- Prahlada maintained devotion despite all obstacles
- He is the embodiment of resilience in service
- Chat requires persistent, resilient connection
- PRAHLADA ROUTES TO ALL OTHER MAHAJANAS

MANTRA WORD: RAMA (Position 9)
"Rama protects those who take shelter"

THE UNIVERSAL INTERFACE:
Chat is the operator's unified interface. User speaks naturally,
PRAHLADA detects intent and routes to the correct Mahajana:

    "What's the system status?" → PRITHU (status)
    "Scan for vulnerabilities"  → VYASA (scan)
    "Any threats?"              → SHUKA (intel)
    "Hello, how are you?"       → PRAHLADA (chat response)

Usage:
    naga chat "What's the system status?"
    naga chat "Scan the codebase"
    naga chat "Show me recent intel"
    naga chat "Hello!"
"""

from typing import List, Optional, Tuple

from vibe_core.protocols.naga.cli_command import (
    Mahajana,
    NagaCommandBase,
    NagaCommandResult,
    NAGA_COMMAND_REGISTRY,
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode


# =============================================================================
# INTENT PATTERNS (KUMARAS assists PRAHLADA)
# =============================================================================

# Keywords that trigger routing to other commands
INTENT_PATTERNS = {
    "status": {
        "keywords": [
            "status", "state", "health", "running", "alive", "up",
            "how is", "how's", "what's running", "system state",
            "are you", "you ok", "you there", "awake",
        ],
        "command": "status",
        "mahajana": "PRITHU",
    },
    "scan": {
        "keywords": [
            "scan", "check", "verify", "validate", "audit",
            "vulnerabilities", "security", "toxicity", "toxic",
            "protocol coverage", "integrity", "analyze", "analyse",
        ],
        "command": "scan",
        "mahajana": "VYASA",
    },
    "intel": {
        "keywords": [
            "intel", "intelligence", "threats", "threat",
            "warnings", "alerts", "critical", "observations",
            "what's happening", "what happened", "recent",
            "news", "updates", "report",
        ],
        "command": "intel",
        "mahajana": "SHUKA",
    },
}


def detect_intent(message: str) -> Optional[str]:
    """
    Detect intent from user message.

    KUMARAS (RESOLVE_REQ) assists PRAHLADA in understanding intent.

    Returns:
        Command name if intent detected, None for chat response.
    """
    msg_lower = message.lower()

    for intent_name, intent_data in INTENT_PATTERNS.items():
        for keyword in intent_data["keywords"]:
            if keyword in msg_lower:
                return intent_data["command"]

    return None


def extract_args(message: str, intent: str) -> List[str]:
    """
    Extract command arguments from natural language.

    Examples:
        "scan with deep mode" → ["--deep"]
        "quick status" → ["--brief"]
        "show critical intel" → ["--critical"]
    """
    msg_lower = message.lower()
    args = []

    if intent == "status":
        if "brief" in msg_lower or "quick" in msg_lower or "short" in msg_lower:
            args.append("--brief")
        elif "naga" in msg_lower or "federation" in msg_lower:
            args.append("--nagas")
        elif "service" in msg_lower or "health" in msg_lower:
            args.append("--services")

    elif intent == "scan":
        if "quick" in msg_lower or "fast" in msg_lower:
            args.append("--quick")
        elif "deep" in msg_lower or "full" in msg_lower or "thorough" in msg_lower:
            args.append("--deep")
        elif "toxic" in msg_lower or "security" in msg_lower or "vulnerab" in msg_lower:
            args.append("--toxicity")
        elif "protocol" in msg_lower or "coverage" in msg_lower:
            args.append("--protocols")

    elif intent == "intel":
        if "critical" in msg_lower or "urgent" in msg_lower:
            args.append("--critical")
        elif "threat" in msg_lower or "danger" in msg_lower:
            args.append("--threats")
        elif "security" in msg_lower:
            args.append("--category")
            args.append("security")

    return args


@naga_command(
    opcode=MantraOpCode.EXEC_SERVICE,
    mahajana=Mahajana.PRAHLADA,
    name="chat",
    help_text="Chat with the system - PRAHLADA routes to all Mahajanas",
)
class ChatCommand(NagaCommandBase):
    """
    Chat command - the universal operator interface.

    PRAHLADA receives natural language, detects intent with KUMARAS,
    and routes to the appropriate Mahajana:

    - Status queries → PRITHU (SYS_WAKE)
    - Scan requests → VYASA (ASSERT_TRUTH)
    - Intel queries → SHUKA (FETCH_RES)
    - General chat → PRAHLADA responds directly
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute chat command with intent routing.

        Args:
            args: Message parts to join

        Returns:
            NagaCommandResult from routed command or chat response
        """
        if not args:
            return self.failure(
                "No message provided. Usage: naga chat <message>",
                exit_code=1,
            )

        message = " ".join(args)

        # Detect intent (KUMARAS assists)
        intent = detect_intent(message)

        if intent:
            # Route to appropriate Mahajana
            return self._route_to_command(intent, message)
        else:
            # PRAHLADA responds directly
            return self._chat_response(message)

    def _route_to_command(self, command_name: str, message: str) -> NagaCommandResult:
        """
        Route to another command based on detected intent.

        Args:
            command_name: The command to route to
            message: Original user message

        Returns:
            Result from the routed command
        """
        # Get command from registry
        command = NAGA_COMMAND_REGISTRY.get(command_name)

        if not command:
            return self.failure(
                f"Command '{command_name}' not found in registry",
                exit_code=1,
            )

        # Extract arguments from natural language
        cmd_args = extract_args(message, command_name)

        # Get Mahajana info for attribution
        mahajana_name = INTENT_PATTERNS.get(command_name, {}).get("mahajana", "UNKNOWN")

        # Execute the routed command
        result = command.execute(cmd_args)

        # Wrap result with routing attribution
        routing_header = f"[PRAHLADA → {mahajana_name}] Routing to {command_name}...\n\n"

        return NagaCommandResult(
            success=result.success,
            exit_code=result.exit_code,
            output=routing_header + result.output,
            error=result.error,
            opcode=result.opcode,
            mahajana=result.mahajana,
            data=result.data + (
                ("routed_by", "prahlada"),
                ("original_message", message),
            ),
        )

    def _chat_response(self, message: str) -> NagaCommandResult:
        """
        Generate direct chat response when no command intent detected.

        Args:
            message: User's message

        Returns:
            Chat response from PRAHLADA
        """
        # Simple response patterns
        msg_lower = message.lower()

        if any(g in msg_lower for g in ["hello", "hi", "hey", "hare krishna", "jai"]):
            response = "Hare Krishna! PRAHLADA at your service. How may I assist you today?"
        elif any(q in msg_lower for q in ["how are you", "how do you do"]):
            response = "By Krishna's grace, all systems are functioning. What would you like to know?"
        elif "thank" in msg_lower:
            response = "All glories to Srila Prabhupada! Happy to serve."
        elif "help" in msg_lower:
            response = self._get_help_text()
        else:
            response = f"[PRAHLADA] I heard: \"{message}\"\n\nI can help you with:\n" + self._get_capabilities()

        return self.success(
            response,
            data=(
                ("intent", "chat"),
                ("message", message),
                ("mahajana", "prahlada"),
            ),
        )

    def _get_help_text(self) -> str:
        """Get help text showing available commands."""
        return """[PRAHLADA] Available Commands (via natural language):

STATUS (PRITHU - SYS_WAKE):
  "What's the system status?"
  "How are the NAGAs doing?"
  "Quick status check"

SCAN (VYASA - ASSERT_TRUTH):
  "Scan for vulnerabilities"
  "Deep security scan"
  "Check protocol coverage"

INTEL (SHUKA - FETCH_RES):
  "Any recent intel?"
  "Show me threats"
  "What's happening?"

Or just chat with me naturally!
"""

    def _get_capabilities(self) -> str:
        """Get brief capabilities list."""
        return """  • "status" - System state (PRITHU)
  • "scan" - Verify integrity (VYASA)
  • "intel" - Get intelligence (SHUKA)
  • "help" - Show all commands
"""


# Export for direct import
__all__ = ["ChatCommand", "detect_intent", "extract_args", "INTENT_PATTERNS"]

"""
OPUS-045: KRIYA (Action) - Chat to Intent Bridge.

Sanskrit: Kriya = Completed Action / Sacred Deed.

This module bridges JNANA (knowledge/chat) with TAT (action/intent).
When a user asks MANAS to DO something (not just know), KRIYA extracts
the intent and pushes it to the CognitiveKernel.

Architecture:
    User: "Führe eine Inventur der Capabilities durch"
         ↓
    JnanaHandler → LLM (with KRIYA prompt extension)
         ↓
    KriyaExtractor → Parse response for [INTENT:...] blocks
         ↓
    CognitiveKernel.push_intent(...)
         ↓
    Response: "Verstanden. Intent 'capability_scan' erstellt. Priorität: HIGH"

"From understanding flows action. From action flows change."
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..intent_generator import Intent, IntentPriority, IntentRisk

logger = logging.getLogger("MANAS.Cortex.Kriya")


# =============================================================================
# KRIYA PROMPT EXTENSION - Instructs LLM to output structured intents
# =============================================================================

KRIYA_SYSTEM_EXTENSION = """
## ACTION MODE (KRIYA)

When the user requests an ACTION (not just information), you MUST:
1. Understand what they want to accomplish
2. Generate a structured intent block
3. Confirm the intent was created

FORMAT for action requests - include this block in your response:

```intent
{
  "type": "<intent_type>",
  "title": "<short title>",
  "description": "<what this does>",
  "priority": "low|medium|high|critical",
  "risk": "safe|low|medium|high",
  "params": {}
}
```

INTENT TYPES you can generate:
- capability_scan: Inventory system capabilities
- status_check: Deep system status analysis
- test_run: Execute test suite
- cleanup_branches: Clean up stale git branches
- documentation_update: Update documentation
- code_review: Review specific code
- analyze_file: Analyze a specific file
- security_scan: Security analysis
- performance_check: Performance analysis
- custom: Custom user-defined action

PRIORITY levels:
- low: Nice to have, can wait
- medium: Should do soon
- high: Important, do next
- critical: Do immediately

RISK levels:
- safe: Read-only, no system changes
- low: Minor changes, easily reversible
- medium: Moderate changes, needs review
- high: Significant changes, needs approval

EXAMPLES:

User: "Führe eine Inventur der Capabilities durch"
Response: "Ich erstelle einen Intent für die Capability-Inventur.

```intent
{
  "type": "capability_scan",
  "title": "Inventur der System-Capabilities",
  "description": "Scanne alle verfügbaren Capabilities und erstelle eine Übersicht.",
  "priority": "medium",
  "risk": "safe",
  "params": {"scope": "all"}
}
```

Intent erstellt: 'capability_scan' mit Priorität MEDIUM."

User: "Analysiere die Datei kernel.py auf Sicherheitslücken"
Response: "Sicherheitsanalyse wird vorbereitet.

```intent
{
  "type": "security_scan",
  "title": "Security Scan: kernel.py",
  "description": "Analysiere kernel.py auf bekannte Sicherheitslücken und unsichere Patterns.",
  "priority": "high",
  "risk": "safe",
  "params": {"file": "kernel.py", "scope": "security"}
}
```

Intent erstellt: 'security_scan' mit Priorität HIGH."

IMPORTANT:
- Only generate intents when the user asks for ACTION
- For information requests, just answer normally (no intent block)
- Include the intent block in your response text
- Always confirm the intent was created at the end
"""


# =============================================================================
# KNOWN ACTION TRIGGERS - Keywords that suggest action requests
# =============================================================================

ACTION_TRIGGERS = {
    # German
    "führe": True,
    "starte": True,
    "analysiere": True,
    "prüfe": True,
    "scanne": True,
    "erstelle": True,
    "lösche": True,
    "bereinige": True,
    "aktualisiere": True,
    "fixe": True,
    "repariere": True,
    "inventur": True,
    "überprüfe": True,
    "teste": True,
    "säubere": True,
    "optimiere": True,
    # English
    "run": True,
    "start": True,
    "analyze": True,
    "check": True,
    "scan": True,
    "create": True,
    "delete": True,
    "cleanup": True,
    "clean": True,
    "update": True,
    "fix": True,
    "repair": True,
    "inventory": True,
    "verify": True,
    "test": True,
    "execute": True,
    "perform": True,
    "do": True,
    "make": True,
    "generate": True,
}


@dataclass
class ExtractedIntent:
    """An intent extracted from LLM response."""

    intent_type: str
    title: str
    description: str
    priority: IntentPriority
    risk: IntentRisk
    params: Dict[str, Any]
    raw_json: str  # Original JSON for debugging

    def to_intent(self, intent_id: str) -> Intent:
        """Convert to full Intent object."""
        return Intent(
            id=intent_id,
            intent_type=self.intent_type,
            title=self.title,
            description=self.description,
            reasoning=f"User requested via chat: {self.title}",
            priority=self.priority,
            risk=self.risk,
            params=self.params,
            auto_executable=self.risk == IntentRisk.SAFE,
            expires_at=(datetime.utcnow() + timedelta(hours=24)).isoformat(),
        )


class KriyaExtractor:
    """
    Extracts structured intents from LLM responses.

    Looks for ```intent ... ``` blocks in the response and parses them.
    """

    # Regex to find intent blocks
    INTENT_BLOCK_PATTERN = re.compile(r"```intent\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)

    @classmethod
    def is_action_request(cls, message: str) -> bool:
        """
        Check if message looks like an action request.

        Args:
            message: User message

        Returns:
            True if message appears to request action
        """
        words = message.lower().split()
        for word in words[:5]:  # Check first 5 words
            # Strip punctuation
            clean_word = word.strip(".,!?:;")
            if clean_word in ACTION_TRIGGERS:
                return True
        return False

    @classmethod
    def extract_intent(cls, llm_response: str) -> Optional[ExtractedIntent]:
        """
        Extract intent from LLM response.

        Args:
            llm_response: Full LLM response text

        Returns:
            ExtractedIntent if found, None otherwise
        """
        match = cls.INTENT_BLOCK_PATTERN.search(llm_response)
        if not match:
            return None

        json_str = match.group(1).strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse intent JSON: {e}")
            return None

        # Validate required fields
        required = ["type", "title", "description"]
        for field in required:
            if field not in data:
                logger.warning(f"Intent missing required field: {field}")
                return None

        # Parse priority
        priority_str = data.get("priority", "medium").lower()
        try:
            priority = IntentPriority(priority_str)
        except ValueError:
            priority = IntentPriority.MEDIUM

        # Parse risk
        risk_str = data.get("risk", "medium").lower()
        try:
            risk = IntentRisk(risk_str)
        except ValueError:
            risk = IntentRisk.MEDIUM

        return ExtractedIntent(
            intent_type=data["type"],
            title=data["title"],
            description=data["description"],
            priority=priority,
            risk=risk,
            params=data.get("params", {}),
            raw_json=json_str,
        )

    @classmethod
    def strip_intent_block(cls, response: str) -> str:
        """
        Remove intent block from response for cleaner display.

        Args:
            response: LLM response with intent block

        Returns:
            Response with intent block removed
        """
        return cls.INTENT_BLOCK_PATTERN.sub("", response).strip()


class KriyaBridge:
    """
    Bridge between JnanaHandler and CognitiveKernel.

    This class handles:
    1. Extending prompts with KRIYA instructions for action requests
    2. Extracting intents from LLM responses
    3. Pushing intents to CognitiveKernel
    4. Generating confirmation messages
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize KRIYA bridge.

        Args:
            workspace: Workspace root path
        """
        self._workspace = workspace or Path.cwd()
        self._cognitive_kernel = None
        self._intent_counter = 0

    @property
    def _get_kernel(self):
        """Lazy load CognitiveKernel."""
        if self._cognitive_kernel is None:
            try:
                from ..cognitive_kernel import CognitiveKernel

                # OPUS-167: Use singleton pattern to avoid expensive re-initialization
                self._cognitive_kernel = CognitiveKernel.get_instance(workspace=self._workspace)
            except ImportError:
                logger.warning("CognitiveKernel not available")
        return self._cognitive_kernel

    def extend_prompt_for_action(self, messages: List[Dict[str, str]], user_message: str) -> List[Dict[str, str]]:
        """
        Extend prompt with KRIYA instructions if action is requested.

        Args:
            messages: Original message list for LLM
            user_message: The user's message

        Returns:
            Extended messages with KRIYA instructions
        """
        if not KriyaExtractor.is_action_request(user_message):
            return messages

        # Extend system message with KRIYA instructions
        extended = []
        for msg in messages:
            if msg.get("role") == "system":
                extended.append({"role": "system", "content": msg["content"] + "\n\n" + KRIYA_SYSTEM_EXTENSION})
            else:
                extended.append(msg)

        logger.debug("KRIYA: Extended prompt for action request")
        return extended

    def process_response(self, llm_response: str, user_message: str) -> Tuple[str, Optional[Intent]]:
        """
        Process LLM response and extract/push intents.

        Args:
            llm_response: Raw LLM response
            user_message: Original user message

        Returns:
            Tuple of (cleaned response, optional Intent)
        """
        # Extract intent if present
        extracted = KriyaExtractor.extract_intent(llm_response)

        if not extracted:
            return llm_response, None

        # Generate intent ID
        self._intent_counter += 1
        intent_id = f"kriya_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{self._intent_counter:03d}"

        # Create Intent
        intent = extracted.to_intent(intent_id)

        # Push to CognitiveKernel
        pushed = self._push_intent(intent)

        # Clean response (remove intent block, add confirmation)
        clean_response = KriyaExtractor.strip_intent_block(llm_response)

        if pushed:
            # Add KRIYA confirmation
            confirmation = self._format_confirmation(intent)
            clean_response = f"{clean_response}\n\n{confirmation}"
        else:
            clean_response = f"{clean_response}\n\n⚠️ Intent konnte nicht zum Buffer hinzugefügt werden."

        logger.info(f"KRIYA: Extracted and pushed intent '{intent.intent_type}'")
        return clean_response, intent

    def _push_intent(self, intent: Intent) -> bool:
        """
        Push intent to CognitiveKernel buffer.

        Args:
            intent: Intent to push

        Returns:
            True if successfully pushed
        """
        kernel = self._get_kernel
        if not kernel:
            logger.warning("KRIYA: No CognitiveKernel available")
            return False

        try:
            # Add directly to kernel's buffer
            from ..cognitive_kernel import IntentBufferEntry

            entry = IntentBufferEntry(intent=intent)
            kernel._intent_buffer.append(entry)
            kernel._save_intent_buffer()

            logger.info(f"KRIYA: Intent '{intent.id}' added to buffer")
            return True

        except Exception as e:
            logger.error(f"KRIYA: Failed to push intent: {e}")
            return False

    def _format_confirmation(self, intent: Intent) -> str:
        """Format intent confirmation message."""
        risk_emoji = {
            IntentRisk.SAFE: "✅",
            IntentRisk.LOW: "🟢",
            IntentRisk.MEDIUM: "🟡",
            IntentRisk.HIGH: "🔴",
        }

        priority_emoji = {
            IntentPriority.LOW: "📋",
            IntentPriority.MEDIUM: "📌",
            IntentPriority.HIGH: "⚡",
            IntentPriority.CRITICAL: "🚨",
        }

        emoji_r = risk_emoji.get(intent.risk, "⚪")
        emoji_p = priority_emoji.get(intent.priority, "📋")

        auto = " (auto-executable)" if intent.auto_executable else ""

        return (
            f"---\n"
            f"🎯 **Intent erstellt:** `{intent.id}`\n"
            f"{emoji_p} **Typ:** {intent.intent_type}\n"
            f"{emoji_r} **Risiko:** {intent.risk.value.upper()}{auto}\n"
            f"📊 **Priorität:** {intent.priority.value.upper()}\n"
            f"---"
        )

    def get_pending_intents_summary(self) -> str:
        """Get summary of pending intents."""
        kernel = self._get_kernel
        if not kernel:
            return "Kein CognitiveKernel verfügbar."

        pending = kernel.get_pending_intents()
        if not pending:
            return "Keine ausstehenden Intents. MANAS ist bereit."

        lines = [f"**{len(pending)} ausstehende Intents:**"]
        for intent in pending[:5]:
            lines.append(f"- [{intent.priority.value.upper()}] {intent.title}")

        if len(pending) > 5:
            lines.append(f"... und {len(pending) - 5} weitere")

        return "\n".join(lines)

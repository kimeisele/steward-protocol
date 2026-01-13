"""
BLUEPRINT GENERATOR (GAD-5001: The Missing Bridge)
UPGRADED: Semantic Compiler for Neuro-Symbolic OS (GAD-5500)

This is the VIBE_ALIGNER equivalent for steward-protocol.
Now upgraded to act as a SEMANTIC COMPILER:
    Neural (raw input) → Symbolic (Syscall Request)

Problem it solves:
- Playbooks have template variables like {{ feature_description }}
- These variables have DEFAULT values that mean nothing
- User input is passed RAW without extracting structured requirements
- Routing is broken keyword-matching garbage

The Blueprint Generator (Semantic Compiler) transforms:
    RAW: "Create a new monitoring agent that watches system health"
    INTO: {
        "syscall_type": "SPAWN_COGNITION",
        "params": {
            "role": "watchman",
            "mission": "Monitor system health and report anomalies",
            "capabilities": ["monitor", "alert"],
        }
    }

Architecture (Neuro-Symbolic OS):
    Neural (LLM/Intent) → Semantic Compiler → Symbolic (Syscall) → Kernel

This bridges the gap between:
    INTENT DETECTION → [SEMANTIC COMPILER] → SYSCALL EXECUTION

The key insight: We use deterministic structures (Syscalls) to channel neural output.
This is "ML Light" - robust, stable, no hallucinations in critical paths.

Integration point:
    Called BEFORE playbook execution, after intent is detected.
    Returns either:
    - SyscallRequest (for kernel operations like agent birth)
    - Variable dict (for traditional playbook execution)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xb968dd3c"  # GenesisByte: parampara % 37 == 0

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Import Semantic Syscalls
from vibe_core.semantic_syscalls import SyscallRequest, SyscallType

logger = logging.getLogger("BLUEPRINT_GENERATOR")


# ============================================================================
# SEMANTIC INTENT PATTERNS
# ============================================================================

# These patterns map natural language to Syscall types
# This is the DETERMINISTIC part of the neuro-symbolic bridge

SYSCALL_INTENT_PATTERNS = {
    SyscallType.SPAWN_COGNITION: [
        r"create\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|bot|worker|cartridge)",
        r"build\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|bot|worker)",
        r"spawn\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|cognition|worker|bot)",
        r"birth\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?agent",
        r"make\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?(?:agent|bot|worker)",
        r"i\s+need\s+(?:an?\s+)?(?:new\s+)?(?:\w+\s+)?agent",
        r"(?:agent|bot)\s+(?:that|to|for|which)",
    ],
    SyscallType.ALLOCATE_PRANA: [
        r"give\s+(?:credits|prana|funds)\s+to",
        r"allocate\s+(?:\d+\s+)?(?:credits|prana)",
        r"fund\s+(?:the\s+)?agent",
        r"transfer\s+(?:\d+\s+)?credits",
    ],
    SyscallType.DISPATCH_TASK: [
        r"send\s+(?:a\s+)?task\s+to",
        r"dispatch\s+(?:to\s+)?(?:agent|)",
        r"ask\s+(?:the\s+)?(?:agent|herald|civic)",
        r"tell\s+(?:the\s+)?(?:agent|herald|civic)",
        # Content Generation patterns (dispatch to herald)
        r"write\s+(?:a\s+)?(?:blog|post|article|doc)",
        r"create\s+(?:a\s+)?(?:blog|post|article|content)",
        r"generate\s+(?:a\s+)?(?:blog|documentation|announcement|content)",
        r"draft\s+(?:a\s+)?(?:post|article|content)",
        r"(?:blog|post|article)\s+(?:about|on|for)",
        # Governance patterns (dispatch to civic)
        r"vote\s+(?:on|for)\s+",
        r"start\s+(?:a\s+)?voting",
        r"proposal\s+(?:#?\d+|vote)",
        r"governance\s+(?:vote|decision)",
    ],
}

# Role extraction patterns - maps keywords to canonical agent roles
ROLE_PATTERNS = {
    "watchman": ["monitor", "watch", "observe", "guard", "surveillance", "health", "status"],
    "herald": ["announce", "publish", "broadcast", "communicate", "message", "notify"],
    "scribe": ["document", "record", "log", "write", "archive", "chronicle"],
    "auditor": ["verify", "check", "validate", "audit", "inspect", "review"],
    "artisan": ["design", "create", "craft", "build", "generate", "art"],
    "oracle": ["predict", "forecast", "analyze", "intelligence", "insights"],
    "engineer": ["code", "implement", "develop", "program", "build software"],
}

# Content-related extraction patterns
CONTENT_FORMAT_PATTERNS = {
    "markdown": ["markdown", "md", ".md"],
    "html": ["html", "web", "webpage"],
    "text": ["text", "plain", "txt"],
    "json": ["json", "structured"],
}

CONTENT_TONE_PATTERNS = {
    "professional": ["professional", "formal", "business"],
    "casual": ["casual", "informal", "friendly", "conversational"],
    "technical": ["technical", "detailed", "in-depth"],
    "simple": ["simple", "easy", "beginner", "eli5"],
}

# Governance-related patterns
GOVERNANCE_PATTERNS = [
    r"vote\s+(?:on|for)\s+",
    r"start\s+(?:a\s+)?voting",
    r"proposal\s+(?:#?\d+|vote)",
    r"governance\s+(?:vote|decision)",
]

VOTING_RULES_PATTERNS = {
    "democratic": ["democratic", "majority", "simple majority"],
    "supermajority": ["supermajority", "two-thirds", "2/3"],
    "unanimous": ["unanimous", "all agree", "consensus"],
}


@dataclass
class CompilationResult:
    """Result of semantic compilation."""

    is_syscall: bool  # True if compiled to syscall, False for playbook vars
    syscall_request: Optional[SyscallRequest] = None  # The syscall (if is_syscall=True)
    playbook_vars: Optional[Dict[str, Any]] = None  # Traditional vars (if is_syscall=False)
    confidence: float = 0.0  # How confident we are in this compilation
    source: str = ""  # What triggered this compilation


class BlueprintGenerator:
    """
    Semantic Compiler: Generates structured blueprints from raw user input.

    UPGRADED for Neuro-Symbolic OS:
    - Primary: Compile to SyscallRequest (for kernel operations)
    - Fallback: Extract playbook variables (for traditional playbooks)

    This is the SHABDA phase actualized - not just validating input exists,
    but COMPILING intent into kernel operations.

    The key insight: We detect WHAT the user wants (syscall type) FIRST,
    then extract the parameters. This is the opposite of keyword routing.
    """

    def __init__(self, kernel: Any = None):
        """
        Args:
            kernel: Reference to kernel for LLM access (optional for deterministic mode)
        """
        self.kernel = kernel

    def compile(self, raw_input: str, requester_id: str = "user") -> CompilationResult:
        """
        MAIN ENTRY POINT: Compile raw input into a kernel operation.

        This is the Semantic Compiler - it decides:
        1. Is this a Syscall? (agent birth, resource allocation, etc.)
        2. Or traditional playbook execution?

        The method uses deterministic pattern matching first, then
        falls back to LLM extraction if needed.

        Args:
            raw_input: The raw user input string
            requester_id: Who is making this request

        Returns:
            CompilationResult with either syscall_request or playbook_vars
        """
        logger.info(f"🔮 SEMANTIC COMPILER: Analyzing '{raw_input[:60]}...'")

        input_lower = raw_input.lower()

        # Step 1: Detect Syscall Intent (Deterministic)
        syscall_type, confidence, matched_pattern = self._detect_syscall_intent(input_lower)

        if syscall_type and confidence >= 0.7:
            # This is a kernel operation - compile to syscall
            logger.info(f"🎯 Detected Syscall: {syscall_type.value} (confidence: {confidence:.2f})")

            try:
                params = self._extract_syscall_params(syscall_type, raw_input)

                syscall_request = SyscallRequest(
                    syscall_type=syscall_type,
                    params=params,
                    requester_id=requester_id,
                )

                return CompilationResult(
                    is_syscall=True,
                    syscall_request=syscall_request,
                    confidence=confidence,
                    source=f"pattern: {matched_pattern}",
                )
            except ValueError as e:
                # Missing required params - log and fall through to playbook
                logger.warning(f"Syscall compilation failed: {e}")

        # Step 2: Fall back to playbook variables extraction
        logger.info("📋 Falling back to playbook variable extraction")
        return CompilationResult(
            is_syscall=False,
            playbook_vars={"raw_input": raw_input},
            confidence=0.5,
            source="fallback to playbook",
        )

    def _detect_syscall_intent(self, input_lower: str) -> tuple[Optional[SyscallType], float, str]:
        """
        Detect which syscall type this input maps to.

        Returns:
            (syscall_type, confidence, matched_pattern) or (None, 0, "") if no match
        """
        best_match = (None, 0.0, "")

        for syscall_type, patterns in SYSCALL_INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, input_lower):
                    # Calculate confidence based on pattern specificity
                    # Longer patterns = higher confidence
                    confidence = min(0.95, 0.7 + len(pattern) / 100)

                    if confidence > best_match[1]:
                        best_match = (syscall_type, confidence, pattern)

        return best_match

    def _extract_syscall_params(self, syscall_type: SyscallType, raw_input: str) -> Dict[str, Any]:
        """
        Extract parameters for a specific syscall type from raw input.

        This is where the "ML Light" magic happens - we use deterministic
        extraction rules to turn natural language into structured params.
        """
        input_lower = raw_input.lower()

        if syscall_type == SyscallType.SPAWN_COGNITION:
            return self._extract_spawn_cognition_params(raw_input, input_lower)

        elif syscall_type == SyscallType.ALLOCATE_PRANA:
            return self._extract_allocate_prana_params(raw_input, input_lower)

        elif syscall_type == SyscallType.DISPATCH_TASK:
            return self._extract_dispatch_task_params(raw_input, input_lower)

        # Default: just use raw input as description
        return {"description": raw_input}

    def _extract_spawn_cognition_params(self, raw_input: str, input_lower: str) -> Dict[str, Any]:
        """
        Extract SPAWN_COGNITION parameters from input.

        Required: role, mission
        Optional: initial_credits, capabilities
        """
        # Extract role from patterns
        role = self._detect_role(input_lower)

        # Extract mission (everything after "that", "to", "for", "which")
        mission = raw_input
        for separator in [" that ", " to ", " for ", " which "]:
            if separator in input_lower:
                idx = input_lower.index(separator)
                mission = raw_input[idx + len(separator) :].strip()
                break

        # Fallback: use full input as mission
        if mission == raw_input:
            mission = f"Agent created from request: {raw_input}"

        # Extract capabilities based on role and keywords
        capabilities = self._detect_capabilities(input_lower, role)

        # Extract credits if mentioned
        credits_match = re.search(r"(\d+)\s*credits?", input_lower)
        initial_credits = int(credits_match.group(1)) if credits_match else 100

        return {
            "role": role,
            "mission": mission,
            "capabilities": capabilities,
            "initial_credits": initial_credits,
        }

    def _detect_role(self, input_lower: str) -> str:
        """Detect agent role from input using keyword patterns."""
        best_role = None
        best_score = 0

        for role, keywords in ROLE_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in input_lower)
            if score > best_score:
                best_score = score
                best_role = role

        # Fallback: extract noun after "agent"
        if not best_role:
            match = re.search(r"(?:agent|bot)\s+(?:called\s+)?(\w+)", input_lower)
            if match:
                best_role = match.group(1)

        return best_role or "worker"  # Default role

    def _detect_capabilities(self, input_lower: str, role: str) -> List[str]:
        """Detect capabilities from input and role."""
        capabilities = ["execute"]  # All agents can execute

        # Role-based defaults
        role_capabilities = {
            "watchman": ["monitor", "alert", "report"],
            "herald": ["publish", "broadcast", "communicate"],
            "scribe": ["document", "archive", "read", "write"],
            "auditor": ["verify", "audit", "inspect"],
            "artisan": ["create", "generate", "design"],
            "oracle": ["analyze", "predict", "query"],
            "engineer": ["code", "build", "manifest"],
        }

        if role in role_capabilities:
            capabilities.extend(role_capabilities[role])

        # Keyword-based additions
        if "read" in input_lower or "file" in input_lower:
            capabilities.append("read_file")
        if "write" in input_lower:
            capabilities.append("write_file")
        if "network" in input_lower or "api" in input_lower:
            capabilities.append("network")

        return list(set(capabilities))

    def _extract_allocate_prana_params(self, raw_input: str, input_lower: str) -> Dict[str, Any]:
        """Extract ALLOCATE_PRANA parameters."""
        # Extract amount
        amount_match = re.search(r"(\d+)\s*(?:credits?|prana)?", input_lower)
        amount = int(amount_match.group(1)) if amount_match else 100

        # Extract agent_id
        agent_match = re.search(r"(?:to|for)\s+(\w+)", input_lower)
        agent_id = agent_match.group(1) if agent_match else "unknown"

        return {
            "agent_id": agent_id,
            "amount": amount,
        }

    def _extract_dispatch_task_params(self, raw_input: str, input_lower: str) -> Dict[str, Any]:
        """
        Extract DISPATCH_TASK parameters.

        This handles:
        1. Direct agent dispatch ("ask herald to...")
        2. Content generation ("write a blog post about...")
        3. Governance voting ("vote on proposal #123")
        """
        # Check if this is a governance/voting request
        is_governance_request = any(re.search(p, input_lower) for p in GOVERNANCE_PATTERNS)
        if is_governance_request:
            return self._extract_governance_params(raw_input, input_lower)

        # Check if this is a content generation request
        content_patterns = [
            r"write\s+(?:a\s+)?(?:blog|post|article|doc)",
            r"create\s+(?:a\s+)?(?:blog|post|article|content)",
            r"generate\s+(?:a\s+)?(?:blog|documentation|announcement|content)",
            r"draft\s+(?:a\s+)?(?:post|article|content)",
            r"(?:blog|post|article)\s+(?:about|on|for)",
        ]

        is_content_request = any(re.search(p, input_lower) for p in content_patterns)

        if is_content_request:
            return self._extract_content_generation_params(raw_input, input_lower)

        # Standard agent dispatch
        agent_match = re.search(r"(?:to|ask|tell)\s+(?:the\s+)?(\w+)", input_lower)
        agent_id = agent_match.group(1) if agent_match else "envoy"

        # Everything after the agent name is the task
        if agent_match:
            task_start = agent_match.end()
            task_payload = raw_input[task_start:].strip()
        else:
            task_payload = raw_input

        return {
            "agent_id": agent_id,
            "task_payload": {"action": "process", "content": task_payload},
        }

    def _extract_content_generation_params(self, raw_input: str, input_lower: str) -> Dict[str, Any]:
        """
        Extract content generation parameters.

        This is "ML Light" for content - we extract:
        - topic: What the content is about
        - format: markdown, html, text
        - tone: professional, casual, technical
        - target_audience: (optional)
        """
        # Extract topic (everything after "about", "on", "for")
        topic = raw_input
        for separator in [" about ", " on ", " for ", " regarding "]:
            if separator in input_lower:
                idx = input_lower.index(separator)
                topic = raw_input[idx + len(separator) :].strip()
                break

        # If no separator found, extract from the full input
        if topic == raw_input:
            # Remove common prefixes
            topic = re.sub(
                r"^(write|create|generate|draft)\s+(a\s+)?(blog\s+)?(post\s+)?(article\s+)?(about\s+)?", "", input_lower
            ).strip()
            if not topic:
                topic = raw_input

        # Extract format
        content_format = "markdown"  # default
        for fmt, keywords in CONTENT_FORMAT_PATTERNS.items():
            if any(kw in input_lower for kw in keywords):
                content_format = fmt
                break

        # Extract tone
        content_tone = "professional"  # default
        for tone, keywords in CONTENT_TONE_PATTERNS.items():
            if any(kw in input_lower for kw in keywords):
                content_tone = tone
                break

        # Extract word count if mentioned
        word_count_match = re.search(r"(\d+)\s*(?:words?|characters?)", input_lower)
        word_count = int(word_count_match.group(1)) if word_count_match else None

        # Content generation is dispatched to Herald
        return {
            "agent_id": "herald",
            "task_payload": {
                "action": "generate_content",
                "topic": topic,
                "format": content_format,
                "tone": content_tone,
                "word_count": word_count,
            },
            # Also store as content_params for circuit access
            "content_params": {
                "topic": topic,
                "format": content_format,
                "tone": content_tone,
                "word_count": word_count,
            },
        }

    def _extract_governance_params(self, raw_input: str, input_lower: str) -> Dict[str, Any]:
        """
        Extract governance/voting parameters.

        This extracts:
        - proposal_id: The proposal being voted on
        - rules: Voting rules (democratic, supermajority, unanimous)
        - deadline: When voting ends (optional)
        """
        # Extract proposal ID
        proposal_id = None
        proposal_patterns = [
            r"proposal\s*#?\s*(\d+)",
            r"#(\d+)",
            r"prop[- ]?(\d+)",
            r"vote\s+(?:on|for)\s+(\w+)",
        ]

        for pattern in proposal_patterns:
            match = re.search(pattern, input_lower)
            if match:
                proposal_id = match.group(1)
                break

        # If no numeric ID found, try to extract a name
        if not proposal_id:
            name_match = re.search(r"vote\s+(?:on|for)\s+(?:the\s+)?(.+?)(?:\s+proposal)?$", input_lower)
            if name_match:
                proposal_id = name_match.group(1).strip()

        # Extract voting rules
        voting_rules = "democratic"  # default
        for rules, keywords in VOTING_RULES_PATTERNS.items():
            if any(kw in input_lower for kw in keywords):
                voting_rules = rules
                break

        # Extract deadline if mentioned
        deadline = None
        deadline_patterns = [
            r"(?:by|until|deadline)\s+(\d{4}-\d{2}-\d{2})",
            r"(?:by|until)\s+(\d+)\s*(?:hours?|days?)",
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, input_lower)
            if match:
                deadline = match.group(1)
                break

        # Governance is dispatched to Civic agent
        return {
            "agent_id": "civic",
            "task_payload": {
                "action": "initiate_vote",
                "proposal_id": proposal_id,
                "rules": voting_rules,
                "deadline": deadline,
            },
            # Also store as vote_params for circuit access
            "vote_params": {
                "proposal_id": proposal_id,
                "rules": voting_rules,
                "deadline": deadline,
            },
        }

    async def generate_blueprint(
        self,
        raw_input: str,
        playbook_variables: Dict[str, Any],
        playbook_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a structured blueprint from raw user input.

        Args:
            raw_input: The raw user input string
            playbook_variables: The playbook's variable definitions with defaults
            playbook_id: ID of the matched playbook (for context-aware extraction)
            context: Additional context (project info, recent files, etc.)

        Returns:
            Dict with populated variable values extracted from raw_input
        """
        logger.info(f"🔮 BLUEPRINT GENERATOR: Extracting from '{raw_input[:50]}...'")

        # Strategy 1: Deterministic extraction (fast, no LLM)
        deterministic_values = self._extract_deterministic(raw_input, playbook_variables, playbook_id)

        # Strategy 2: LLM-enhanced extraction (if kernel available and deterministic insufficient)
        if self.kernel and self._needs_llm_extraction(deterministic_values, playbook_variables):
            llm_values = await self._extract_with_llm(raw_input, playbook_variables, playbook_id, context)
            # Merge: LLM values override deterministic where present
            deterministic_values.update({k: v for k, v in llm_values.items() if v is not None})

        logger.info(f"📋 BLUEPRINT RESULT: {list(deterministic_values.keys())}")
        return deterministic_values

    def _extract_deterministic(
        self,
        raw_input: str,
        playbook_variables: Dict[str, Any],
        playbook_id: str,
    ) -> Dict[str, Any]:
        """
        Extract values using deterministic rules (no LLM needed).

        This covers common patterns:
        - Feature name extraction from verbs + nouns
        - File paths from explicit mentions
        - Common patterns detection
        """
        result = {}
        input_lower = raw_input.lower()

        # Extract feature_name if variable exists
        if "feature_name" in playbook_variables:
            result["feature_name"] = self._extract_feature_name(raw_input)

        # Use full input as feature_description (better than default)
        if "feature_description" in playbook_variables:
            result["feature_description"] = raw_input

        # Extract target_files if mentioned
        if "target_files" in playbook_variables:
            result["target_files"] = self._extract_file_paths(raw_input)

        # Extract content_topic for content playbooks
        if "content_topic" in playbook_variables:
            result["content_topic"] = raw_input

        # Extract proposal_id for governance playbooks
        if "proposal_id" in playbook_variables:
            result["proposal_id"] = self._extract_proposal_id(raw_input)

        # Detect project_context patterns
        if "project_context" in playbook_variables:
            result["project_context"] = self._detect_project_context(raw_input)

        return result

    def _extract_feature_name(self, raw_input: str) -> str:
        """Extract a concise feature name from input."""
        # Remove common verbs and extract key nouns
        stop_words = {
            "implement",
            "create",
            "add",
            "build",
            "make",
            "write",
            "develop",
            "the",
            "a",
            "an",
            "for",
            "to",
            "with",
            "and",
            "or",
            "in",
            "on",
            "please",
            "can",
            "you",
            "could",
            "would",
            "should",
            "need",
            "want",
        }

        words = raw_input.lower().split()
        key_words = [w for w in words if w not in stop_words and len(w) > 2]

        if key_words:
            # Take first 3 significant words
            feature_name = "-".join(key_words[:3])
            return feature_name

        return "feature"  # Fallback

    def _extract_file_paths(self, raw_input: str) -> List[str]:
        """Extract file paths mentioned in input."""
        import re

        # Match common file path patterns
        patterns = [
            r"[\w./]+\.py",  # Python files
            r"[\w./]+\.ts",  # TypeScript files
            r"[\w./]+\.js",  # JavaScript files
            r"[\w./]+\.yaml",  # YAML files
            r"[\w./]+\.json",  # JSON files
            r"src/[\w./]+",  # Paths starting with src/
            r"lib/[\w./]+",  # Paths starting with lib/
            r"tests?/[\w./]+",  # Test paths
        ]

        found = []
        for pattern in patterns:
            matches = re.findall(pattern, raw_input, re.IGNORECASE)
            found.extend(matches)

        return list(set(found))  # Deduplicate

    def _extract_proposal_id(self, raw_input: str) -> Optional[str]:
        """Extract proposal ID for governance playbooks."""
        import re

        # Match patterns like "proposal #123", "PROP-456", "proposal 789"
        patterns = [
            r"proposal\s*#?(\d+)",
            r"PROP-?(\d+)",
            r"vote\s+on\s+#?(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, raw_input, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _detect_project_context(self, raw_input: str) -> str:
        """Detect project context from input patterns."""
        input_lower = raw_input.lower()

        # Detect technology context
        if any(kw in input_lower for kw in ["react", "frontend", "ui", "component"]):
            return "frontend"
        if any(kw in input_lower for kw in ["api", "backend", "server", "endpoint"]):
            return "backend"
        if any(kw in input_lower for kw in ["test", "spec", "coverage"]):
            return "testing"
        if any(kw in input_lower for kw in ["deploy", "ci", "cd", "pipeline"]):
            return "devops"
        if any(kw in input_lower for kw in ["auth", "security", "permission"]):
            return "security"

        return "default"

    def _needs_llm_extraction(
        self,
        deterministic_values: Dict[str, Any],
        playbook_variables: Dict[str, Any],
    ) -> bool:
        """Check if LLM extraction would improve results."""
        # If we got empty lists or generic values, LLM might help
        for key, value in deterministic_values.items():
            if isinstance(value, list) and len(value) == 0:
                return True
            if value == "feature":  # Generic fallback
                return True
        return False

    async def _extract_with_llm(
        self,
        raw_input: str,
        playbook_variables: Dict[str, Any],
        playbook_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Use LLM to extract structured values from raw input.

        This is called when deterministic extraction isn't sufficient.
        """
        if not self.kernel:
            return {}

        # Build prompt for structured extraction
        variable_schema = "\n".join(
            [
                f"  - {name}: {type(default).__name__} (default: {default})"
                for name, default in playbook_variables.items()
            ]
        )

        prompt = f"""Extract structured parameters from this user request.

User Request: "{raw_input}"

Playbook: {playbook_id}

Required Variables:
{variable_schema}

Return a JSON object with the extracted values. Only include variables where you can extract meaningful values from the user's request. Be concise and specific.

Example output format:
{{
  "feature_name": "extracted-name",
  "feature_description": "Clear description of what the user wants",
  "target_files": ["path/to/file.py"]
}}
"""

        try:
            # Use kernel to get LLM response
            # This is a simplified call - actual implementation depends on kernel interface
            response = await self.kernel.process_with_llm(prompt, max_tokens=500)

            # Parse JSON from response
            import json
            import re

            # Find JSON in response
            json_match = re.search(r"\{[^}]+\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.warning(f"LLM extraction failed: {e}")

        return {}


# ============================================================================
# INTEGRATION HELPER
# ============================================================================


def create_blueprint_generator(kernel: Any = None) -> BlueprintGenerator:
    """Factory function to create a BlueprintGenerator instance."""
    return BlueprintGenerator(kernel=kernel)


# ============================================================================
# STANDALONE TEST
# ============================================================================

if __name__ == "__main__":
    import asyncio

    async def test_blueprint():
        generator = BlueprintGenerator()

        # Test case 1: Feature implementation
        playbook_vars = {
            "feature_name": "New Feature",
            "feature_description": "Detailed description",
            "target_files": [],
            "project_context": "default",
        }

        result = await generator.generate_blueprint(
            raw_input="Implement JWT authentication with RBAC in src/auth/",
            playbook_variables=playbook_vars,
            playbook_id="FEATURE_IMPLEMENT_SAFE_V1",
        )

        print("\n=== Test 1: Feature Implementation ===")
        print("Input: 'Implement JWT authentication with RBAC in src/auth/'")
        print(f"Result: {result}")

        # Test case 2: Governance vote
        governance_vars = {
            "proposal_id": None,
            "voters": [],
            "voting_deadline": None,
        }

        result2 = await generator.generate_blueprint(
            raw_input="Vote on proposal #42 for the new treasury allocation",
            playbook_variables=governance_vars,
            playbook_id="GOVERNANCE_VOTE_V1",
        )

        print("\n=== Test 2: Governance Vote ===")
        print("Input: 'Vote on proposal #42 for the new treasury allocation'")
        print(f"Result: {result2}")

        # Test case 3: Content generation
        content_vars = {
            "content_topic": None,
            "content_format": "markdown",
            "content_tone": "professional",
        }

        result3 = await generator.generate_blueprint(
            raw_input="Create a blog post about AI agent architectures",
            playbook_variables=content_vars,
            playbook_id="CONTENT_GENERATION_V1",
        )

        print("\n=== Test 3: Content Generation ===")
        print("Input: 'Create a blog post about AI agent architectures'")
        print(f"Result: {result3}")

    asyncio.run(test_blueprint())

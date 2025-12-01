"""
BLUEPRINT GENERATOR (GAD-5001: The Missing Bridge)

This is the VIBE_ALIGNER equivalent for steward-protocol.

Problem it solves:
- Playbooks have template variables like {{ feature_description }}
- These variables have DEFAULT values that mean nothing
- User input is passed RAW without extracting structured requirements

The Blueprint Generator transforms:
    RAW: "Implement JWT authentication with RBAC"
    INTO: {
        "feature_name": "jwt-authentication",
        "feature_description": "JWT-based authentication system with role-based access control",
        "target_files": ["src/auth/jwt.py", "src/auth/rbac.py"],
        "patterns": ["authentication", "authorization", "security"]
    }

This bridges the gap between:
    INTENT DETECTION → [BLUEPRINT GENERATOR] → PLAYBOOK EXECUTION

Integration point:
    Called BEFORE playbook execution, after playbook is matched.
    Returns populated variables dict that replaces defaults.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("BLUEPRINT_GENERATOR")


class BlueprintGenerator:
    """
    Generates structured blueprints from raw user input.

    This is the SHABDA phase actualized - not just validating input exists,
    but EXTRACTING structured requirements from raw intent.
    """

    def __init__(self, kernel: Any = None):
        """
        Args:
            kernel: Reference to kernel for LLM access (optional for deterministic mode)
        """
        self.kernel = kernel

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
            'implement', 'create', 'add', 'build', 'make', 'write', 'develop',
            'the', 'a', 'an', 'for', 'to', 'with', 'and', 'or', 'in', 'on',
            'please', 'can', 'you', 'could', 'would', 'should', 'need', 'want'
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
            r'[\w./]+\.py',      # Python files
            r'[\w./]+\.ts',      # TypeScript files
            r'[\w./]+\.js',      # JavaScript files
            r'[\w./]+\.yaml',    # YAML files
            r'[\w./]+\.json',    # JSON files
            r'src/[\w./]+',      # Paths starting with src/
            r'lib/[\w./]+',      # Paths starting with lib/
            r'tests?/[\w./]+',   # Test paths
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
            r'proposal\s*#?(\d+)',
            r'PROP-?(\d+)',
            r'vote\s+on\s+#?(\d+)',
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
        if any(kw in input_lower for kw in ['react', 'frontend', 'ui', 'component']):
            return "frontend"
        if any(kw in input_lower for kw in ['api', 'backend', 'server', 'endpoint']):
            return "backend"
        if any(kw in input_lower for kw in ['test', 'spec', 'coverage']):
            return "testing"
        if any(kw in input_lower for kw in ['deploy', 'ci', 'cd', 'pipeline']):
            return "devops"
        if any(kw in input_lower for kw in ['auth', 'security', 'permission']):
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
        variable_schema = "\n".join([
            f"  - {name}: {type(default).__name__} (default: {default})"
            for name, default in playbook_variables.items()
        ])

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
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
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
        print(f"Input: 'Implement JWT authentication with RBAC in src/auth/'")
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
        print(f"Input: 'Vote on proposal #42 for the new treasury allocation'")
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
        print(f"Input: 'Create a blog post about AI agent architectures'")
        print(f"Result: {result3}")

    asyncio.run(test_blueprint())

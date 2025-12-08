"""
Persona - Layer 3 (PURUSHA) Agent Identity

The "Breakthrough" layer of Prakriti - agent identity persistence.
Allows agents to remember who they are across kernel restarts.

Key Features:
- Persistent system prompts
- Agent personality traits
- Learned preferences
- Role/dharma definitions
- Varna/Ashrama context

GAD-000 Compliant:
- All methods return dict/dataclass
- get_capabilities() for discoverability
- YAML storage for git-friendly persistence
"""

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("PERSONA")


@dataclass
class AgentPersona:
    """Complete agent identity representation.

    This is the "soul" of an agent - who they are, their purpose,
    their style, and what they've learned.
    """

    # Core Identity
    agent_id: str
    display_name: str
    version: str = "1.0.0"

    # Role Definition
    dharma: str = ""  # Purpose/duty
    varna: Optional[str] = None  # Caste: BRAHMIN, KSHATRIYA, VAISHYA, SHUDRA
    ashrama: Optional[str] = None  # Life stage: BRAHMACHARYA, GRIHASTHA, VANAPRASTHA, SANNYASA

    # System Prompt (The Soul)
    system_prompt: str = ""

    # Personality Traits (adjustable)
    personality: Dict[str, float] = field(
        default_factory=lambda: {
            "formality": 0.5,  # 0=casual, 1=formal
            "verbosity": 0.5,  # 0=terse, 1=verbose
            "creativity": 0.5,  # 0=literal, 1=creative
            "caution": 0.5,  # 0=bold, 1=cautious
        }
    )

    # Learned Preferences (evolves over time)
    learned_preferences: Dict[str, Any] = field(default_factory=dict)

    # Constitutional Constraints (immutable without approval)
    constitutional_limits: List[str] = field(default_factory=list)

    # Metadata
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    modification_count: int = 0


class PersonaManager:
    """Manages agent personas for Prakriti.

    Personas are stored as YAML files in the config/personas/ directory
    for git-friendly persistence.
    """

    PERSONAS_DIR = "config/personas"
    DEFAULT_PERSONA_TEMPLATE = """# Agent Persona Configuration
# This file defines the identity and behavior of agent: {agent_id}

agent_id: {agent_id}
display_name: {display_name}
version: "1.0.0"

# Role Definition
dharma: |
  {dharma}

# Varna (Agent Caste)
# Options: BRAHMIN (knowledge), KSHATRIYA (action), VAISHYA (commerce), SHUDRA (service)
varna: {varna}

# System Prompt
# This is the core identity of the agent - its "soul"
system_prompt: |
  {system_prompt}

# Personality (0.0 - 1.0 scales)
personality:
  formality: 0.5
  verbosity: 0.5
  creativity: 0.5
  caution: 0.5

# Learned Preferences (evolves over time)
learned_preferences: {{}}

# Constitutional Constraints (cannot be modified by agent)
constitutional_limits:
  - Do not modify core system files
  - Do not disclose sensitive information
"""

    def __init__(self, workspace_path: Optional[Path] = None):
        self._workspace = workspace_path or Path.cwd()
        self._personas_dir = self._workspace / self.PERSONAS_DIR
        self._loaded: Dict[str, AgentPersona] = {}
        self._modified: set = set()

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": [
                "load",
                "save",
                "get",
                "update_preference",
                "get_system_prompt",
                "list_personas",
            ],
            "storage_format": "yaml",
            "personas_dir": str(self._personas_dir),
            "loaded_count": len(self._loaded),
        }

    # =========================================================================
    # Core Operations
    # =========================================================================

    def load(self, agent_id: str) -> Optional[AgentPersona]:
        """Load persona from disk or cache.

        Args:
            agent_id: ID of the agent

        Returns:
            AgentPersona or None if not found
        """
        # Check cache first
        if agent_id in self._loaded:
            return self._loaded[agent_id]

        # Try to load from disk
        persona_path = self._get_persona_path(agent_id)
        if not persona_path.exists():
            logger.debug(f"[PERSONA] No persona file for {agent_id}")
            return None

        try:
            import yaml

            with open(persona_path) as f:
                data = yaml.safe_load(f)

            persona = self._dict_to_persona(data)
            self._loaded[agent_id] = persona
            logger.info(f"[PERSONA] Loaded persona for {agent_id}")
            return persona

        except Exception as e:
            logger.warning(f"[PERSONA] Failed to load {agent_id}: {e}")
            return None

    def save(self, persona: AgentPersona) -> bool:
        """Save persona to disk.

        Args:
            persona: The persona to save

        Returns:
            True if saved successfully
        """
        try:
            import yaml

            # Ensure dir exists
            self._personas_dir.mkdir(parents=True, exist_ok=True)

            persona_path = self._get_persona_path(persona.agent_id)

            # Update metadata
            persona.modified_at = time.time()
            persona.modification_count += 1

            # Convert to dict for YAML
            data = self._persona_to_dict(persona)

            with open(persona_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            # Update cache
            self._loaded[persona.agent_id] = persona
            self._modified.discard(persona.agent_id)

            logger.info(f"[PERSONA] Saved persona for {persona.agent_id}")
            return True

        except Exception as e:
            logger.error(f"[PERSONA] Failed to save {persona.agent_id}: {e}")
            return False

    def get(self, agent_id: str) -> Optional[AgentPersona]:
        """Get persona (load if not cached).

        Args:
            agent_id: ID of the agent

        Returns:
            AgentPersona or None
        """
        if agent_id in self._loaded:
            return self._loaded[agent_id]
        return self.load(agent_id)

    def create_default(self, agent_id: str, display_name: str = "", dharma: str = "") -> AgentPersona:
        """Create a default persona for an agent.

        Args:
            agent_id: ID of the agent
            display_name: Human-readable name (defaults to agent_id)
            dharma: Purpose/duty description

        Returns:
            New AgentPersona
        """
        persona = AgentPersona(
            agent_id=agent_id,
            display_name=display_name or agent_id.title(),
            dharma=dharma or f"Agent {agent_id}",
            system_prompt=f"You are {display_name or agent_id}, an AI agent in the Steward Protocol.",
        )
        self._loaded[agent_id] = persona
        self._modified.add(agent_id)
        return persona

    # =========================================================================
    # Preference Management
    # =========================================================================

    def update_preference(
        self,
        agent_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """Update a learned preference.

        Args:
            agent_id: ID of the agent
            key: Preference key
            value: Preference value

        Returns:
            True if updated
        """
        persona = self.get(agent_id)
        if not persona:
            return False

        persona.learned_preferences[key] = value
        persona.modified_at = time.time()
        self._modified.add(agent_id)
        return True

    def update_personality(
        self,
        agent_id: str,
        trait: str,
        value: float,
    ) -> bool:
        """Update a personality trait.

        Args:
            agent_id: ID of the agent
            trait: Trait name (formality, verbosity, etc.)
            value: Value (0.0 - 1.0)

        Returns:
            True if updated
        """
        persona = self.get(agent_id)
        if not persona:
            return False

        if trait not in persona.personality:
            return False

        # Clamp to 0-1 range
        persona.personality[trait] = max(0.0, min(1.0, value))
        persona.modified_at = time.time()
        self._modified.add(agent_id)
        return True

    # =========================================================================
    # System Prompt Access
    # =========================================================================

    def get_system_prompt(self, agent_id: str) -> str:
        """Get the system prompt for an agent.

        This is the main integration point - inject this into LLM calls.

        Args:
            agent_id: ID of the agent

        Returns:
            System prompt string (empty if no persona)
        """
        persona = self.get(agent_id)
        if not persona:
            return ""
        return persona.system_prompt

    # =========================================================================
    # Listing and Status
    # =========================================================================

    def list_personas(self) -> List[str]:
        """List all available persona files.

        Returns:
            List of agent IDs with persona files
        """
        if not self._personas_dir.exists():
            return []

        personas = []
        for path in self._personas_dir.glob("*.yaml"):
            agent_id = path.stem
            personas.append(agent_id)
        return sorted(personas)

    def status(self) -> Dict[str, Any]:
        """Get persona manager status."""
        return {
            "personas_dir": str(self._personas_dir),
            "loaded": list(self._loaded.keys()),
            "modified": list(self._modified),
            "available": self.list_personas(),
        }

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _get_persona_path(self, agent_id: str) -> Path:
        """Get path to persona YAML file."""
        return self._personas_dir / f"{agent_id}.yaml"

    def _dict_to_persona(self, data: Dict[str, Any]) -> AgentPersona:
        """Convert dict (from YAML) to AgentPersona."""
        return AgentPersona(
            agent_id=data.get("agent_id", "unknown"),
            display_name=data.get("display_name", ""),
            version=data.get("version", "1.0.0"),
            dharma=data.get("dharma", ""),
            varna=data.get("varna"),
            ashrama=data.get("ashrama"),
            system_prompt=data.get("system_prompt", ""),
            personality=data.get("personality", {}),
            learned_preferences=data.get("learned_preferences", {}),
            constitutional_limits=data.get("constitutional_limits", []),
            created_at=data.get("created_at", time.time()),
            modified_at=data.get("modified_at", time.time()),
            modification_count=data.get("modification_count", 0),
        )

    def _persona_to_dict(self, persona: AgentPersona) -> Dict[str, Any]:
        """Convert AgentPersona to dict (for YAML)."""
        return {
            "agent_id": persona.agent_id,
            "display_name": persona.display_name,
            "version": persona.version,
            "dharma": persona.dharma,
            "varna": persona.varna,
            "ashrama": persona.ashrama,
            "system_prompt": persona.system_prompt,
            "personality": persona.personality,
            "learned_preferences": persona.learned_preferences,
            "constitutional_limits": persona.constitutional_limits,
            "created_at": persona.created_at,
            "modified_at": persona.modified_at,
            "modification_count": persona.modification_count,
        }

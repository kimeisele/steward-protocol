"""
CurriculumLoader - YAML-based Curriculum System

OPUS-133: "Daten sind Daten, Code ist Code."

This module loads training curricula from YAML files instead of hardcoded
Python lists. This separation enables:

1. MANAS to read and understand curricula (it can parse YAML)
2. MANAS to write its own curricula (Gap-based training)
3. External tools to generate curricula (LLM Chaos Monkey)
4. Human operators to add scenarios without code changes

Directory Structure:
    curricula/
        basic.yaml      - Safe, warm-up scenarios
        intermediate.yaml
        advanced.yaml
        attack.yaml     - Red team scenarios
        chaos.yaml      - Edge cases
        custom/         - MANAS-generated curricula
            gap_training_20251220.yaml

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curricula/basic.yaml
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/curricula/attack.yaml
    required: true
wiring:
  - pattern: "class CurriculumLoader"
    in: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
  - pattern: "def load_curriculum"
    in: vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .scenarios import ExpectedDecision, Scenario, ScenarioType

logger = logging.getLogger("DOJO.LOADER")


@dataclass
class CurriculumMeta:
    """Metadata about a curriculum."""

    id: str
    name: str
    description: str
    difficulty: int = 1
    tags: List[str] = field(default_factory=list)
    on_correct_block: Optional[str] = None  # For attack curricula
    on_missed_attack: Optional[str] = None


@dataclass
class LoadedCurriculum:
    """A curriculum loaded from YAML."""

    meta: CurriculumMeta
    scenarios: List[Scenario]
    source_path: Path

    @property
    def count(self) -> int:
        return len(self.scenarios)


class CurriculumLoader:
    """
    Loads training curricula from YAML files.

    Usage:
        loader = CurriculumLoader(workspace)
        curriculum = loader.load("basic")
        scenarios = curriculum.scenarios

        # Load all curricula
        all_curricula = loader.load_all()

        # Load custom MANAS-generated curriculum
        custom = loader.load_custom("gap_training_20251220")
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._curricula_dir = workspace / "vibe_core" / "plugins" / "opus_assistant" / "manas" / "dojo" / "curricula"
        self._custom_dir = self._curricula_dir / "custom"

    def load(self, curriculum_id: str) -> Optional[LoadedCurriculum]:
        """
        Load a curriculum by ID.

        Args:
            curriculum_id: The curriculum ID (e.g., "basic", "attack")

        Returns:
            LoadedCurriculum or None if not found
        """
        # Try standard curricula first
        yaml_path = self._curricula_dir / f"{curriculum_id}.yaml"
        if not yaml_path.exists():
            # Try custom directory
            yaml_path = self._custom_dir / f"{curriculum_id}.yaml"

        if not yaml_path.exists():
            logger.warning(f"Curriculum not found: {curriculum_id}")
            return None

        return self._load_from_file(yaml_path)

    def load_all(self) -> Dict[str, LoadedCurriculum]:
        """Load all available curricula."""
        curricula = {}

        # Load standard curricula
        for yaml_file in self._curricula_dir.glob("*.yaml"):
            curriculum = self._load_from_file(yaml_file)
            if curriculum:
                curricula[curriculum.meta.id] = curriculum

        # Load custom curricula
        if self._custom_dir.exists():
            for yaml_file in self._custom_dir.glob("*.yaml"):
                curriculum = self._load_from_file(yaml_file)
                if curriculum:
                    curricula[curriculum.meta.id] = curriculum

        return curricula

    def list_available(self) -> List[str]:
        """List all available curriculum IDs."""
        ids = []

        for yaml_file in self._curricula_dir.glob("*.yaml"):
            ids.append(yaml_file.stem)

        if self._custom_dir.exists():
            for yaml_file in self._custom_dir.glob("*.yaml"):
                ids.append(f"custom/{yaml_file.stem}")

        return sorted(ids)

    def save_custom(self, curriculum_id: str, scenarios: List[Dict[str, Any]], meta: Dict[str, Any]) -> Path:
        """
        Save a custom curriculum (e.g., MANAS-generated).

        Args:
            curriculum_id: ID for the new curriculum
            scenarios: List of scenario dicts
            meta: Curriculum metadata

        Returns:
            Path to the saved YAML file
        """
        self._custom_dir.mkdir(parents=True, exist_ok=True)

        yaml_path = self._custom_dir / f"{curriculum_id}.yaml"

        content = {"curriculum": meta, "scenarios": scenarios}

        yaml_path.write_text(yaml.dump(content, default_flow_style=False, allow_unicode=True))

        logger.info(f"📝 Custom curriculum saved: {yaml_path}")
        return yaml_path

    def _load_from_file(self, yaml_path: Path) -> Optional[LoadedCurriculum]:
        """Load curriculum from a YAML file."""
        try:
            data = yaml.safe_load(yaml_path.read_text())

            # Parse metadata
            curr_data = data.get("curriculum", {})
            meta = CurriculumMeta(
                id=curr_data.get("id", yaml_path.stem),
                name=curr_data.get("name", yaml_path.stem),
                description=curr_data.get("description", ""),
                difficulty=curr_data.get("difficulty", 1),
                tags=curr_data.get("tags", []),
                on_correct_block=curr_data.get("on_correct_block"),
                on_missed_attack=curr_data.get("on_missed_attack"),
            )

            # Parse scenarios
            scenarios = []
            for s in data.get("scenarios", []):
                scenario = self._parse_scenario(s, meta)
                if scenario:
                    scenarios.append(scenario)

            logger.debug(f"📚 Loaded curriculum '{meta.id}': {len(scenarios)} scenarios")

            return LoadedCurriculum(meta=meta, scenarios=scenarios, source_path=yaml_path)

        except Exception as e:
            logger.error(f"Failed to load curriculum {yaml_path}: {e}")
            return None

    def _parse_scenario(self, data: Dict[str, Any], meta: CurriculumMeta) -> Optional[Scenario]:
        """Parse a scenario from YAML data."""
        try:
            # Map expected decision string to enum
            decision_map = {
                "EXECUTE": ExpectedDecision.EXECUTE,
                "WARN_EXECUTE": ExpectedDecision.WARN_EXECUTE,
                "BLOCK": ExpectedDecision.BLOCK,
                "SHIVA_OVERRIDE": ExpectedDecision.SHIVA_OVERRIDE,
            }

            expected = data.get("expected_decision", "EXECUTE")
            expected_decision = decision_map.get(expected, ExpectedDecision.EXECUTE)

            # Map curriculum ID to scenario type
            type_map = {
                "basic": ScenarioType.BASIC,
                "intermediate": ScenarioType.INTERMEDIATE,
                "advanced": ScenarioType.ADVANCED,
                "attack": ScenarioType.ATTACK,
                "chaos": ScenarioType.CHAOS,
            }
            scenario_type = type_map.get(meta.id, ScenarioType.CUSTOM)

            # Parse dharmic range
            dharmic_range = data.get("expected_dharmic_range", [0.0, 1.0])
            if isinstance(dharmic_range, list) and len(dharmic_range) == 2:
                dharmic_tuple = (dharmic_range[0], dharmic_range[1])
            else:
                dharmic_tuple = (0.0, 1.0)

            return Scenario(
                id=data.get("id", "unknown"),
                name=data.get("name", "Unknown Scenario"),
                description=data.get("description", ""),
                scenario_type=scenario_type,
                intent_type=data.get("intent_type", ""),
                intent_params=data.get("params", {}),
                expected_decision=expected_decision,
                expected_dharmic_score_range=dharmic_tuple,
                tags=data.get("tags", []),
                difficulty=data.get("difficulty", meta.difficulty),
            )

        except Exception as e:
            logger.error(f"Failed to parse scenario: {e}")
            return None


def get_curriculum_loader(workspace: Path = None) -> CurriculumLoader:
    """Get a curriculum loader instance."""
    workspace = workspace or Path(".")
    return CurriculumLoader(workspace)

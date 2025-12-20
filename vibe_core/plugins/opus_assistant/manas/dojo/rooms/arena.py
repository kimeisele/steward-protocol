"""
Arena - Active Training Room

OPUS-133: "Der Kampfplatz, wo MANAS seine Entscheidungen übt."

The Arena is where MANAS practices decision-making against
simulated scenarios. It wraps DojoRunner for a cleaner interface.

Modes:
    practice    - Safe mode, no weight changes
    training    - Normal learning mode
    sparring    - Harder scenarios, faster reinforcement
    challenge   - Red team attacks only

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/arena.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/dojo/runner.py
    required: true
-->
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from ..runner import DojoConfig, DojoRunner, TrainingSession

logger = logging.getLogger("DOJO.ARENA")


@dataclass
class ArenaMode:
    """Configuration for different arena modes."""

    name: str
    curriculum: str
    scenarios_per_round: int
    reinforcement_enabled: bool
    description: str


# Predefined arena modes
MODES = {
    "practice": ArenaMode(
        name="practice",
        curriculum="basic",
        scenarios_per_round=5,
        reinforcement_enabled=False,
        description="Safe practice - no weight changes",
    ),
    "training": ArenaMode(
        name="training",
        curriculum="mixed",
        scenarios_per_round=10,
        reinforcement_enabled=True,
        description="Standard training with learning",
    ),
    "sparring": ArenaMode(
        name="sparring",
        curriculum="advanced",
        scenarios_per_round=15,
        reinforcement_enabled=True,
        description="Challenging scenarios with fast learning",
    ),
    "challenge": ArenaMode(
        name="challenge",
        curriculum="attack",
        scenarios_per_round=20,
        reinforcement_enabled=True,
        description="Red team attack simulation",
    ),
}


class Arena:
    """
    The Arena - Active training room for MANAS.

    Usage:
        arena = Arena(workspace)

        # Quick practice session
        result = arena.enter("practice")

        # Full training session
        result = arena.enter("training")

        # Red team challenge
        result = arena.enter("challenge")
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace

    def enter(self, mode: str = "training", custom_config: Optional[Dict[str, Any]] = None) -> TrainingSession:
        """
        Enter the Arena for a training session.

        Args:
            mode: One of "practice", "training", "sparring", "challenge"
            custom_config: Optional config overrides

        Returns:
            TrainingSession with results
        """
        arena_mode = MODES.get(mode, MODES["training"])

        logger.info(f"🥋 ARENA: Entering {arena_mode.name} mode")
        logger.info(f"   {arena_mode.description}")

        # Build config from mode
        config = DojoConfig(
            curriculum=arena_mode.curriculum,
            scenarios_per_epoch=arena_mode.scenarios_per_round,
            max_epochs=1,
            reinforcement_on_correct=arena_mode.reinforcement_enabled,
            reinforcement_on_wrong=arena_mode.reinforcement_enabled,
            use_yaml_curricula=True,
        )

        # Apply custom overrides
        if custom_config:
            for key, value in custom_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Run training
        runner = DojoRunner(self._workspace, config)
        session = runner.run_training()

        # Log summary
        self._log_summary(session, arena_mode)

        return session

    def quick_round(self, curriculum: str = "basic", count: int = 3) -> TrainingSession:
        """
        Quick training round for testing.

        Args:
            curriculum: Which curriculum to use
            count: Number of scenarios

        Returns:
            TrainingSession with results
        """
        return self.enter(
            "training",
            custom_config={
                "curriculum": curriculum,
                "scenarios_per_epoch": count,
            },
        )

    def challenge_mode(self, stop_on_miss: bool = True) -> TrainingSession:
        """
        Enter challenge mode - red team attack simulation.

        If stop_on_miss is True, stops immediately if an attack slips through.
        """
        return self.enter(
            "challenge",
            custom_config={
                "stop_on_false_negative": stop_on_miss,
            },
        )

    def _log_summary(self, session: TrainingSession, mode: ArenaMode) -> None:
        """Log arena session summary."""
        if session.accuracy >= 0.9 and session.attack_detection_rate >= 0.95:
            logger.info(f"🏆 ARENA ({mode.name}): EXCELLENT performance!")
        elif session.accuracy >= 0.7:
            logger.info(f"✅ ARENA ({mode.name}): Good session")
        else:
            logger.warning(f"📈 ARENA ({mode.name}): More practice needed")

    @staticmethod
    def available_modes() -> Dict[str, str]:
        """Get available arena modes with descriptions."""
        return {name: mode.description for name, mode in MODES.items()}

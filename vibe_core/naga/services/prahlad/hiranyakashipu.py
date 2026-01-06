"""
PRAHLAD Hiranyakashipu Integration - Mixin for living attack seeds.

Extracted to reduce service.py below 800 lines.
"""

import logging
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from vibe_core.naga.hiranyakashipu import AttackSeed, SeedLoader

logger = logging.getLogger("PRAHLAD")


class HiranyakashipuMixin:
    """
    Mixin for Prahlad Hiranyakashipu integration.

    Provides:
    - load_attack_seeds(): Load YAML attack seeds
    - get_attack_seeds(): Get loaded seeds with filtering
    """

    # These attributes are expected from PrahladService
    _seed_loader: Optional["SeedLoader"]
    _attack_seeds: List["AttackSeed"]

    def load_attack_seeds(
        self,
        seed_dirs: Optional[List[str]] = None,
        attack_type: Optional[str] = None,
    ) -> int:
        """
        Load attack seeds from Hiranyakashipu YAML files.

        Hiranyakashipu provides the weapons, Prahlad survives them.

        Args:
            seed_dirs: Directories containing YAML seed files.
            attack_type: Filter by attack type.

        Returns:
            Number of seeds loaded.
        """
        from pathlib import Path

        from vibe_core.naga.hiranyakashipu import SeedLoader

        if self._seed_loader is None:
            self._seed_loader = SeedLoader()

        if seed_dirs is None:
            default_dir = Path(__file__).parent.parent.parent / "hiranyakashipu" / "seeds"
            if default_dir.exists():
                seed_dirs = [str(default_dir)]
            else:
                seed_dirs = []

        for seed_dir in seed_dirs:
            self._seed_loader.add_seed_dir(Path(seed_dir))

        count = self._seed_loader.load_seeds()

        if attack_type:
            self._attack_seeds = self._seed_loader.get_seeds(attack_type=attack_type)
        else:
            self._attack_seeds = self._seed_loader.get_all_seeds()

        logger.info(f"🐍 PRAHLAD loaded {count} Hiranyakashipu attack seeds")
        return count

    def get_attack_seeds(
        self,
        attack_type: Optional[str] = None,
        difficulty: Optional[int] = None,
    ) -> List["AttackSeed"]:
        """
        Get loaded attack seeds with optional filtering.

        Args:
            attack_type: Filter by type
            difficulty: Filter by difficulty (1-10)

        Returns:
            List of matching AttackSeed objects.
        """
        if self._seed_loader is None:
            return []

        return self._seed_loader.get_seeds(
            attack_type=attack_type,
            difficulty=difficulty,
        )


__all__ = ["HiranyakashipuMixin"]

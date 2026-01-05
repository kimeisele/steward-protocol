"""
SEED LOADER - Narada's Whisper.

"Through the ear, the seed enters. Through hearing, consciousness transforms."

Narada Muni didn't write code - he CHANTED.
The sound vibration (mantra) entered through the ear.
This transformed Prahlad's consciousness while still in the womb.

Our mapping:
- YAML files = Mantras (patterns/seeds)
- SeedLoader = The ear (receives sound)
- AttackSeed = The seed (DNA of attack)
- Loading = Hearing (transforms into consciousness)

Hot-swap capability:
- Watch YAML directory for changes
- Reload seeds at runtime
- No restart needed = LIVING system
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("NAGA.Prakriti.Seed")


@dataclass
class AttackSeed:
    """
    A single attack pattern - the DNA of an attack.

    This is what Narada whispered - the seed that will grow.
    """

    # Identity
    name: str
    description: str

    # The attack code (can be template with {variables})
    test_code: str

    # Metadata
    attack_type: str
    difficulty: int = 1
    expected_behavior: str = "should_fail"  # "should_fail" or "should_pass"

    # Evolution tracking
    created_at: datetime = field(default_factory=datetime.now)
    discovered_by: str = "manual"  # "manual", "fuzzer", "mutation", "prahlad"
    times_executed: int = 0
    times_bypassed: int = 0  # How often this attack succeeded

    # Tags for categorization
    tags: List[str] = field(default_factory=list)

    # Variables for template expansion
    variables: Dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs) -> str:
        """Render test_code with variables."""
        code = self.test_code
        all_vars = {**self.variables, **kwargs}
        for key, value in all_vars.items():
            code = code.replace(f"{{{key}}}", str(value))
        return code

    @property
    def bypass_rate(self) -> float:
        """How often this attack bypasses defenses."""
        if self.times_executed == 0:
            return 0.0
        return self.times_bypassed / self.times_executed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "test_code": self.test_code,
            "attack_type": self.attack_type,
            "difficulty": self.difficulty,
            "expected_behavior": self.expected_behavior,
            "discovered_by": self.discovered_by,
            "tags": self.tags,
            "variables": self.variables,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttackSeed":
        """Create from dictionary (YAML loaded)."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            test_code=data["test_code"],
            attack_type=data.get("attack_type", "unknown"),
            difficulty=data.get("difficulty", 1),
            expected_behavior=data.get("expected_behavior", "should_fail"),
            discovered_by=data.get("discovered_by", "yaml"),
            tags=data.get("tags", []),
            variables=data.get("variables", {}),
        )


class SeedLoader:
    """
    The Ear - receives and processes mantras (YAML attack patterns).

    Narada's whisper enters through here.

    Features:
    - Load seeds from YAML files
    - Watch for changes (hot-swap)
    - Merge seeds from multiple sources
    - Track seed evolution
    """

    def __init__(self, seed_dirs: List[Path] = None):
        """
        Initialize the seed loader.

        Args:
            seed_dirs: Directories to watch for YAML seeds
        """
        self._seed_dirs = seed_dirs or []
        self._seeds: Dict[str, AttackSeed] = {}
        self._file_mtimes: Dict[Path, float] = {}
        self._loaded = False

    def add_seed_dir(self, path: Path) -> None:
        """Add a directory to watch for seeds."""
        if path not in self._seed_dirs:
            self._seed_dirs.append(path)
            self._loaded = False

    def load_seeds(self, force: bool = False) -> int:
        """
        Load all seeds from configured directories.

        Returns number of seeds loaded.
        """
        if self._loaded and not force:
            return len(self._seeds)

        try:
            import yaml
        except ImportError:
            logger.warning("PyYAML not available - using fallback")
            return self._load_fallback_seeds()

        loaded_count = 0

        for seed_dir in self._seed_dirs:
            if not seed_dir.exists():
                logger.warning(f"Seed directory not found: {seed_dir}")
                continue

            # Find all YAML files
            for yaml_file in seed_dir.glob("**/*.yaml"):
                try:
                    loaded_count += self._load_yaml_file(yaml_file)
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")

            for yaml_file in seed_dir.glob("**/*.yml"):
                try:
                    loaded_count += self._load_yaml_file(yaml_file)
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")

        self._loaded = True
        logger.info(f"🌱 Loaded {loaded_count} attack seeds from {len(self._seed_dirs)} directories")
        return loaded_count

    def _load_yaml_file(self, yaml_file: Path) -> int:
        """Load seeds from a single YAML file."""
        import yaml

        # Check if file changed
        mtime = yaml_file.stat().st_mtime
        if yaml_file in self._file_mtimes and self._file_mtimes[yaml_file] == mtime:
            return 0  # No changes

        self._file_mtimes[yaml_file] = mtime

        with open(yaml_file) as f:
            data = yaml.safe_load(f)

        if not data:
            return 0

        count = 0

        # Handle both single seed and list of seeds
        if isinstance(data, list):
            for seed_data in data:
                seed = AttackSeed.from_dict(seed_data)
                self._seeds[seed.name] = seed
                count += 1
        elif isinstance(data, dict):
            if "seeds" in data:
                # Format: {seeds: [...], metadata: {...}}
                for seed_data in data["seeds"]:
                    seed = AttackSeed.from_dict(seed_data)
                    self._seeds[seed.name] = seed
                    count += 1
            elif "name" in data:
                # Single seed
                seed = AttackSeed.from_dict(data)
                self._seeds[seed.name] = seed
                count += 1

        return count

    def _load_fallback_seeds(self) -> int:
        """Load hardcoded seeds when YAML not available."""
        # These are the core seeds that should always exist
        fallback_seeds = [
            AttackSeed(
                name="trivial_pass",
                description="Test that does nothing",
                test_code="def test_trivial():\n    pass",
                attack_type="trivial",
                difficulty=1,
            ),
            AttackSeed(
                name="assert_true",
                description="Test that asserts True",
                test_code="def test_always_true():\n    assert True",
                attack_type="trivial",
                difficulty=1,
            ),
        ]

        for seed in fallback_seeds:
            self._seeds[seed.name] = seed

        self._loaded = True
        return len(fallback_seeds)

    def check_for_updates(self) -> List[str]:
        """
        Check for updated YAML files (hot-swap).

        Returns list of updated seed names.
        """
        updated = []

        for seed_dir in self._seed_dirs:
            if not seed_dir.exists():
                continue

            for yaml_file in seed_dir.glob("**/*.yaml"):
                mtime = yaml_file.stat().st_mtime
                if yaml_file in self._file_mtimes:
                    if mtime > self._file_mtimes[yaml_file]:
                        # File changed - reload
                        old_seeds = set(self._seeds.keys())
                        self._load_yaml_file(yaml_file)
                        new_seeds = set(self._seeds.keys())
                        updated.extend(new_seeds - old_seeds)

        if updated:
            logger.info(f"🔄 Hot-swapped {len(updated)} seeds: {updated}")

        return updated

    def get_seed(self, name: str) -> Optional[AttackSeed]:
        """Get a seed by name."""
        self.load_seeds()
        return self._seeds.get(name)

    def get_seeds(
        self,
        attack_type: str = None,
        difficulty: int = None,
        tags: List[str] = None,
    ) -> List[AttackSeed]:
        """Get seeds filtered by criteria."""
        self.load_seeds()

        seeds = list(self._seeds.values())

        if attack_type:
            seeds = [s for s in seeds if s.attack_type == attack_type]
        if difficulty is not None:
            seeds = [s for s in seeds if s.difficulty == difficulty]
        if tags:
            seeds = [s for s in seeds if any(t in s.tags for t in tags)]

        return seeds

    def get_all_seeds(self) -> List[AttackSeed]:
        """Get all loaded seeds."""
        self.load_seeds()
        return list(self._seeds.values())

    def add_seed(self, seed: AttackSeed) -> None:
        """Add a seed programmatically (for mutation/evolution)."""
        self._seeds[seed.name] = seed

    def record_execution(self, seed_name: str, bypassed: bool) -> None:
        """Record that a seed was executed."""
        if seed_name in self._seeds:
            self._seeds[seed_name].times_executed += 1
            if bypassed:
                self._seeds[seed_name].times_bypassed += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded seeds."""
        self.load_seeds()

        by_type: Dict[str, int] = {}
        by_difficulty: Dict[int, int] = {}
        total_executions = 0
        total_bypasses = 0

        for seed in self._seeds.values():
            by_type[seed.attack_type] = by_type.get(seed.attack_type, 0) + 1
            by_difficulty[seed.difficulty] = by_difficulty.get(seed.difficulty, 0) + 1
            total_executions += seed.times_executed
            total_bypasses += seed.times_bypassed

        return {
            "total_seeds": len(self._seeds),
            "by_type": by_type,
            "by_difficulty": by_difficulty,
            "total_executions": total_executions,
            "total_bypasses": total_bypasses,
            "global_bypass_rate": total_bypasses / total_executions if total_executions > 0 else 0,
            "seed_dirs": [str(d) for d in self._seed_dirs],
        }

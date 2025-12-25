"""
Config caching strategy.

ARCHITECTURE DECISION (OPUS-305, 2025-12-25):

The original pickle-based cache was fundamentally broken:
- Pickle stores module paths, but Sections are dynamically loaded
- Error: "Can't pickle <class 'section_kernel.KernelConfig'>: import failed"
- This crashed EVERY config load, not just cache reads

WHY NO FILE CACHE:
1. Singleton (`get_config()`) is the real cache - works for entire session
2. File cache only saves ~200ms on cold start (once per session)
3. Pickle is fragile (breaks on any code change)
4. JSON cache would require refactoring from_dict() (calls from_files() recursively)

FUTURE: If cold start becomes a problem, implement YAML-dict cache at
SectionLoader level (cache the dicts before object creation, not after).
"""

import hashlib
from pathlib import Path

HASH_PATH = Path(".vibe/cache/config.hash")


def get_yaml_hash(config_dir: Path) -> str:
    """Hash all YAML files - kept for potential future use."""
    content = ""
    for f in sorted(config_dir.glob("**/*.yaml")):
        content += f.read_text()
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_or_parse(config_dir: Path, parse_fn):
    """
    Parse config fresh. Singleton is the real cache.

    This function exists to maintain API compatibility.
    The actual caching happens via get_config() singleton in config.py.
    """
    return parse_fn()

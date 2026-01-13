"""
Playbook Operations: Executable actions for workflow nodes.

Operations are the "verbs" that playbooks can invoke. Each operation:
- Takes input parameters
- Performs an action
- Returns a result with proof/metadata

Available operations:
- spawn_city: Spawn ephemeral child kernel (4D Hypercube)

AIRLOCK PATTERN:
    When spawning ephemeral cities, use the `artifacts` parameter to specify
    which files should be harvested from the child VFS before the city dies.
    This prevents data loss when the ephemeral kernel is terminated.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xb0c0ea1a"  # GenesisByte: parampara % 37 == 0

from .kernel_spawn import HarvestedArtifact, SpawnCityResult, spawn_city

__all__ = ["spawn_city", "SpawnCityResult", "HarvestedArtifact"]

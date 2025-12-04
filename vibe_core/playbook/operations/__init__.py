"""
Playbook Operations: Executable actions for workflow nodes.

Operations are the "verbs" that playbooks can invoke. Each operation:
- Takes input parameters
- Performs an action
- Returns a result with proof/metadata

Available operations:
- spawn_city: Spawn ephemeral child kernel (4D Hypercube)
"""

from .kernel_spawn import spawn_city, SpawnCityResult

__all__ = ["spawn_city", "SpawnCityResult"]

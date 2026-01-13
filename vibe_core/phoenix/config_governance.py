"""
CONFIG GOVERNANCE - FOLDER_IS_WIRING for Configuration
======================================================

"yasya prasādād bhagavat-prasādo
 yasyāprasādān na gatiḥ kuto 'pi"

"By the mercy of the spiritual master one receives the benediction of Krishna."
— Śrī Gurv-aṣṭaka

CONFIG_OWNERS: Each config file belongs to a Mahajana.
This enables SANKIRTAN to govern and transform config files.

ARCHITECTURE:
    config/*.yaml → CONFIG_OWNERS mapping → Mahajana ownership
    PhoenixConfig → uses CONFIG_OWNERS for governance audit
    SANKIRTAN → can transform configs based on ownership
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x5c7e9a00"  # GenesisByte: parampara % 37 == 0

from enum import Enum
from typing import Dict, Final, List, Optional, TypedDict

# Import Mahajana from protocols (SSOT)
from vibe_core.protocols.mahajanas.router import Mahajana


# =============================================================================
# CONFIG_OWNERS - Config File → Mahajana Mapping (SSOT)
# =============================================================================
# This is the STATE DEFINITION for config governance.
# Each config file belongs to exactly one Mahajana.

CONFIG_OWNERS: Final[Dict[str, Mahajana]] = {
    # === BRAHMA (Creation/Genesis) - Position 1 ===
    "phoenix.yaml": Mahajana.BRAHMA,
    "runtime.yaml": Mahajana.BRAHMA,
    "prana.yaml": Mahajana.BRAHMA,
    "paths.yaml": Mahajana.BRAHMA,
    "manifestation.yaml": Mahajana.BRAHMA,
    "system.yaml": Mahajana.BRAHMA,
    "templates.yaml": Mahajana.BRAHMA,
    "section_id.yaml": Mahajana.BRAHMA,

    # === NARADA (Communication) - Position 2 ===
    "cli.yaml": Mahajana.NARADA,
    "apis.yaml": Mahajana.NARADA,
    "interface.yaml": Mahajana.NARADA,
    "envoy.yaml": Mahajana.NARADA,

    # === SHUKA (Vision/Transcendence) - Position 14 ===
    "llm.yaml": Mahajana.SHUKA,
    "opus.yaml": Mahajana.SHUKA,
    "prompts.yaml": Mahajana.SHUKA,
    "providers.yaml": Mahajana.SHUKA,

    # === YAMARAJA (Security/Judgment) - Position 15 ===
    "naga.yaml": Mahajana.YAMARAJA,
    "soul.yaml": Mahajana.YAMARAJA,
    "test_governance.yaml": Mahajana.YAMARAJA,

    # === MANU (Law/Rules) - Position 7 ===
    "quotas.yaml": Mahajana.MANU,
    "standards.yaml": Mahajana.MANU,

    # === KUMARAS (Purity/Quality) - Position 5 ===
    "quality.yaml": Mahajana.KUMARAS,
    "guardrails.yaml": Mahajana.KUMARAS,
    "semantic_compliance.yaml": Mahajana.KUMARAS,

    # === JANAKA (Duty/Stewardship) - Position 10 ===
    "steward.yaml": Mahajana.JANAKA,
    "matrix.yaml": Mahajana.JANAKA,
    "roadmap.yaml": Mahajana.JANAKA,

    # === PRAHLADA (Devotion/Agents) - Position 9 ===
    "agents.yaml": Mahajana.PRAHLADA,

    # === KAPILA (Analysis/Mind) - Position 6 ===
    "manas.yaml": Mahajana.KAPILA,
}

# Default owner for unmapped config files
DEFAULT_CONFIG_OWNER: Final[Mahajana] = Mahajana.MANU


# =============================================================================
# WATERTIGHT TYPES
# =============================================================================

class ConfigAudit(TypedDict):
    """Result of config governance audit. WATERTIGHT."""
    total_configs: int
    governed_count: int
    ungoverned_count: int
    ungoverned_list: List[str]
    owner_distribution: Dict[str, int]
    health_score: float


# =============================================================================
# GOVERNANCE FUNCTIONS
# =============================================================================

def get_config_owner(config_name: str) -> Mahajana:
    """
    Get the owning Mahajana for a config file.

    FOLDER_IS_WIRING: Config ownership is determined by CONFIG_OWNERS.
    If not in mapping, defaults to MANU (governance fallback).

    Args:
        config_name: Config file name (e.g., "naga.yaml")

    Returns:
        Mahajana owner (NEVER None - everything is governed!)
    """
    return CONFIG_OWNERS.get(config_name, DEFAULT_CONFIG_OWNER)


def audit_configs(config_dir: Optional[str] = None) -> ConfigAudit:
    """
    Audit config governance.

    Scans config directory and reports ownership.

    Args:
        config_dir: Path to config directory (default: config/)

    Returns:
        ConfigAudit with health score and distribution
    """
    from pathlib import Path

    if config_dir is None:
        config_dir = str(Path(__file__).parent.parent.parent / "config")

    config_path = Path(config_dir)
    if not config_path.exists():
        return ConfigAudit(
            total_configs=0,
            governed_count=0,
            ungoverned_count=0,
            ungoverned_list=[],
            owner_distribution={},
            health_score=1.0,
        )

    # Scan yaml files
    yaml_files = list(config_path.glob("*.yaml"))

    governed = []
    ungoverned = []
    owner_dist: Dict[str, int] = {}

    for yaml_file in yaml_files:
        name = yaml_file.name
        owner = CONFIG_OWNERS.get(name)

        if owner:
            governed.append(name)
            owner_dist[owner.value] = owner_dist.get(owner.value, 0) + 1
        else:
            ungoverned.append(name)
            # Assign to default owner
            owner_dist[DEFAULT_CONFIG_OWNER.value] = owner_dist.get(DEFAULT_CONFIG_OWNER.value, 0) + 1

    total = len(yaml_files)
    health = len(governed) / total if total > 0 else 1.0

    return ConfigAudit(
        total_configs=total,
        governed_count=len(governed),
        ungoverned_count=len(ungoverned),
        ungoverned_list=sorted(ungoverned),
        owner_distribution=owner_dist,
        health_score=health,
    )


def list_configs_by_owner(mahajana: Mahajana) -> List[str]:
    """List all config files owned by a Mahajana."""
    return [name for name, owner in CONFIG_OWNERS.items() if owner == mahajana]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CONFIG_OWNERS",
    "DEFAULT_CONFIG_OWNER",
    # Types
    "ConfigAudit",
    # Functions
    "get_config_owner",
    "audit_configs",
    "list_configs_by_owner",
]

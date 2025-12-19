"""
OPUS-096: RuntimeStateDefinition - Single Source of Truth for Runtime State

REFACTORED: No more manual CORE_PATTERNS!

Discovery strategy (3-prong, same as SyncHolon):
1. MANIFEST: generated_outputs from plugin manifests (UI files)
2. MANIFEST: state_paths from plugin manifests (State files)
3. CONVENTION: Known patterns (*.lock, *.tmp, *.bak)

This replaces fragmented definitions in:
- manifest.json generated_outputs
- git_state._get_runtime_state_patterns()
- heartbeat.runtime_files
- sync_holon conventions
"""

import json
import logging
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import ClassVar, Dict, List, Set

logger = logging.getLogger("RUNTIME_STATE")


@dataclass
class RuntimeStateDefinition:
    """
    Canonical definition of what constitutes "runtime state".

    SINGLE SOURCE OF TRUTH for all runtime state classification.

    NO MANUAL LISTS - everything is discovered from:
    1. Plugin manifests (generated_outputs, state_paths)
    2. Convention patterns (file extensions only)
    """

    # =========================================================================
    # CONVENTION PATTERNS - File extensions that are ALWAYS runtime
    # =========================================================================
    # These are the ONLY hardcoded patterns - universal file types
    # NOT file names, NOT directories - just extensions!
    CONVENTION_PATTERNS: ClassVar[List[str]] = [
        "*.lock",  # Lock files
        "*.tmp",  # Temporary files
        "*.bak",  # Backup files
        "*.vibe",  # VIBE snapshot files
    ]

    # =========================================================================
    # DISCOVERED PATTERNS - From manifests and conventions
    # =========================================================================

    # Patterns from plugin manifests (generated_outputs + state_paths)
    discovered_patterns: Dict[str, List[str]] = field(default_factory=dict)

    # Cached combined patterns for fast lookup
    _all_patterns: Set[str] = field(default_factory=set, repr=False)

    def __post_init__(self):
        """Compute cached patterns after initialization."""
        self._rebuild_pattern_cache()

    def _rebuild_pattern_cache(self) -> None:
        """Rebuild the combined pattern cache from all sources."""
        patterns: Set[str] = set(self.CONVENTION_PATTERNS)

        # Add all discovered patterns
        for source, source_patterns in self.discovered_patterns.items():
            patterns.update(source_patterns)

        self._all_patterns = patterns
        logger.debug(f"RuntimeStateDefinition: {len(patterns)} patterns from {len(self.discovered_patterns)} sources")

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def is_runtime_state(self, path: str | Path) -> bool:
        """
        Is this path runtime state (not source code)?

        Args:
            path: File path (relative or absolute)

        Returns:
            True if this is runtime state (machine-generated)
            False if this is source code (human-written)
        """
        path_str = str(path)
        path_name = Path(path_str).name

        for pattern in self._all_patterns:
            # Match full path
            if fnmatch(path_str, pattern):
                return True
            # Match basename (for patterns like "OPUS.md")
            if fnmatch(path_name, pattern):
                return True
            # Match if path starts with pattern dir (for ".opus_state/*")
            if pattern.endswith("/*") or pattern.endswith("/**/*"):
                dir_pattern = pattern.rstrip("/*").rstrip("/**")
                if path_str.startswith(dir_pattern) or path_str.startswith(f"./{dir_pattern}"):
                    return True

        return False

    def is_source_code(self, path: str | Path) -> bool:
        """Inverse of is_runtime_state for readability."""
        return not self.is_runtime_state(path)

    def filter_runtime_files(self, paths: List[str]) -> List[str]:
        """Filter a list of paths to only runtime state files."""
        return [p for p in paths if self.is_runtime_state(p)]

    def filter_source_files(self, paths: List[str]) -> List[str]:
        """Filter a list of paths to only source code files."""
        return [p for p in paths if self.is_source_code(p)]

    def get_all_patterns(self) -> List[str]:
        """Get all runtime state patterns."""
        return list(self._all_patterns)

    def get_discovery_report(self) -> Dict[str, List[str]]:
        """Get report of where patterns came from (for debugging)."""
        return {
            "convention": list(self.CONVENTION_PATTERNS),
            **self.discovered_patterns,
        }

    # =========================================================================
    # FACTORY METHODS
    # =========================================================================

    @classmethod
    def from_workspace(cls, workspace: Path) -> "RuntimeStateDefinition":
        """
        CANONICAL FACTORY: Discover all runtime state patterns from workspace.

        3-prong discovery (mirrors SyncHolon):
        1. MANIFEST: generated_outputs (UI files like OPUS.md)
        2. MANIFEST: state_paths (State dirs like .opus_state/)
        3. SYNCHOLON CONVENTIONS: Known state directories

        Args:
            workspace: Repository root path

        Returns:
            RuntimeStateDefinition with all discovered patterns
        """
        discovered: Dict[str, List[str]] = {}

        # === Prong 1 & 2: Manifest Discovery ===
        manifest_patterns = cls._discover_from_manifests(workspace)
        discovered.update(manifest_patterns)

        # === Prong 3: SyncHolon Convention Discovery ===
        convention_patterns = cls._discover_from_conventions(workspace)
        discovered.update(convention_patterns)

        instance = cls(discovered_patterns=discovered)

        logger.info(
            f"RuntimeStateDefinition: Discovered {len(instance._all_patterns)} patterns from {len(discovered)} sources"
        )

        return instance

    @classmethod
    def _discover_from_manifests(cls, workspace: Path) -> Dict[str, List[str]]:
        """
        Discover patterns from plugin manifests.

        Reads both:
        - generated_outputs: UI files (OPUS.md, COGNITION.md, etc.)
        - state_paths: State directories (.opus_state/, etc.)
        """
        import glob

        discovered: Dict[str, List[str]] = {}

        # Scan all plugin manifests
        manifest_glob = workspace / "vibe_core" / "plugins" / "*" / "manifest.json"

        for manifest_path in glob.glob(str(manifest_glob)):
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)

                plugin_name = Path(manifest_path).parent.name
                patterns: List[str] = []

                # === generated_outputs (UI files) ===
                if "generated_outputs" in manifest:
                    outputs = manifest["generated_outputs"]
                    for key, value in outputs.items():
                        if key.startswith("_"):  # Skip comments
                            continue
                        if isinstance(value, list):
                            patterns.extend(value)
                        elif isinstance(value, str):
                            patterns.append(value)

                # === state_paths (State directories) ===
                if "state_paths" in manifest:
                    state_paths = manifest["state_paths"]
                    if isinstance(state_paths, list):
                        for p in state_paths:
                            # Convert path to glob pattern
                            patterns.append(f"{p}/*")
                            patterns.append(f"{p}/**/*")
                    elif isinstance(state_paths, str):
                        patterns.append(f"{state_paths}/*")
                        patterns.append(f"{state_paths}/**/*")

                if patterns:
                    discovered[f"manifest:{plugin_name}"] = patterns

            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Could not read manifest {manifest_path}: {e}")
                continue

        return discovered

    @classmethod
    def _discover_from_conventions(cls, workspace: Path) -> Dict[str, List[str]]:
        """
        Discover patterns from SyncHolon conventions.

        These are well-known state directories that exist by convention.
        Only includes directories that ACTUALLY EXIST in the workspace.
        """
        conventions = [
            (".opus_state", "opus_assistant"),
            (".prakriti", "prakriti"),
            (".vibe/state", "vibe_state"),
            (".vibe/config", "vibe_config"),
        ]

        discovered: Dict[str, List[str]] = {}

        for dir_path, source_name in conventions:
            full_path = workspace / dir_path
            if full_path.exists():
                patterns = [
                    f"{dir_path}/*",
                    f"{dir_path}/**/*",
                ]
                discovered[f"convention:{source_name}"] = patterns

        return discovered

    # === Legacy factory methods (for backwards compatibility) ===

    @classmethod
    def core_only(cls) -> "RuntimeStateDefinition":
        """DEPRECATED: Use from_workspace() instead."""
        logger.warning("RuntimeStateDefinition.core_only() is deprecated, use from_workspace()")
        return cls()

    @classmethod
    def from_manifests(cls, workspace: Path) -> "RuntimeStateDefinition":
        """DEPRECATED: Use from_workspace() instead."""
        return cls.from_workspace(workspace)

    @classmethod
    def with_plugin_patterns(cls, plugin_patterns: Dict[str, List[str]]) -> "RuntimeStateDefinition":
        """DEPRECATED: Use from_workspace() instead."""
        logger.warning("RuntimeStateDefinition.with_plugin_patterns() is deprecated")
        return cls(
            discovered_patterns={"legacy": list(set(p for patterns in plugin_patterns.values() for p in patterns))}
        )


# =========================================================================
# SINGLETON ACCESS (for performance)
# =========================================================================

_global_definition: RuntimeStateDefinition | None = None


def get_runtime_state_definition(workspace: Path | None = None) -> RuntimeStateDefinition:
    """
    Get the global RuntimeStateDefinition singleton.

    Lazily initializes from workspace discovery.
    """
    global _global_definition

    if _global_definition is None:
        if workspace:
            _global_definition = RuntimeStateDefinition.from_workspace(workspace)
        else:
            # Fallback: Try to find workspace from current directory
            cwd = Path.cwd()
            if (cwd / "vibe_core").exists():
                _global_definition = RuntimeStateDefinition.from_workspace(cwd)
            else:
                logger.warning("No workspace provided, using convention patterns only")
                _global_definition = RuntimeStateDefinition()

    return _global_definition


def reset_runtime_state_definition() -> None:
    """Reset the global singleton (mainly for testing)."""
    global _global_definition
    _global_definition = None

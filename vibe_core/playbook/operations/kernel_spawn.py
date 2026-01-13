"""
4D Hypercube Operation: Spawn Ephemeral City

This operation enables playbooks to spawn child kernels with custom
configurations for specialized tasks. Results are folded back to the
parent kernel with cryptographic proof.

AIRLOCK PATTERN:
    Before the child kernel dies, we harvest specified artifacts from the
    child's VFS and transfer them to the parent. This prevents data loss
    when the ephemeral city is terminated.

    Child VFS: /tmp/vibe_os/agents/{child_agent_id}/
    Parent VFS: /tmp/vibe_os/agents/{parent_agent_id}/ or specified destination

Use Cases:
    - Fast coding swarm (no governance overhead)
    - Sandboxed experimentation (throwaway environment)
    - Parallel task execution with different configs
    - Circuit execution in isolated context

Example (in playbook node):
    from vibe_core.playbook.operations import spawn_city

    result = await spawn_city(
        task="build feature X",
        config_overrides={"city.governance.voting_threshold": 0},
        circuit="fast_code",
        artifacts=["src/main.py", "tests/test_main.py"],  # Harvest these before death
        artifacts_destination="output/",  # Copy to here
    )

    # result.output contains the execution result
    # result.proof contains ledger hash from child
    # result.harvested_artifacts contains paths to harvested files
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xb0d86bf3"  # GenesisByte: parampara % 37 == 0

import asyncio
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.phoenix import PhoenixConfig

logger = logging.getLogger(__name__)


# VFS root - delegate to vibe_core/vfs.py for consistency
def _get_vfs_root():
    """Get VFS root from VirtualFileSystem (OPUS-025 compliant)."""
    try:
        from vibe_core.vfs import VirtualFileSystem

        return VirtualFileSystem._get_vfs_root()
    except Exception:
        return Path("/tmp") / "vibe_os" / "agents"


VFS_ROOT = None  # Resolved lazily via _get_vfs_root()


@dataclass
class HarvestedArtifact:
    """A file harvested from the ephemeral city before death."""

    source_path: str  # Path in child VFS
    destination_path: str  # Path where file was copied
    size_bytes: int
    success: bool
    error: Optional[str] = None


@dataclass
class SpawnCityResult:
    """Result from ephemeral city execution."""

    success: bool
    output: Any
    proof: str  # Ledger hash from child kernel
    child_id: int  # ID of the (now-dead) child kernel
    error: Optional[str] = None
    harvested_artifacts: List[HarvestedArtifact] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def _get_or_create_kernel() -> "RealVibeKernel":
    """Get the current kernel instance or create one."""
    from vibe_core.kernel_impl import RealVibeKernel

    # Try to get from global state first
    # (In a real execution context, the kernel would be injected)
    # For now, create a new parent kernel if none exists
    return RealVibeKernel()


def _harvest_artifacts(
    child_kernel: "RealVibeKernel",
    artifacts: List[str],
    destination: Path,
) -> List[HarvestedArtifact]:
    """
    AIRLOCK: Harvest artifacts from child VFS before termination.

    Searches all agent sandboxes in the child kernel for requested files.
    Copies found files to the destination directory.

    Args:
        child_kernel: The ephemeral child kernel (still alive)
        artifacts: List of relative file paths to harvest (e.g., ["src/main.py"])
        destination: Directory to copy files to

    Returns:
        List of HarvestedArtifact with success/failure status
    """
    harvested: List[HarvestedArtifact] = []

    # Ensure destination exists
    destination.mkdir(parents=True, exist_ok=True)

    # Get all agent IDs registered in child kernel
    child_agent_ids = list(child_kernel.agent_registry.keys()) if hasattr(child_kernel, "agent_registry") else []

    logger.info(f"🚪 AIRLOCK: Harvesting {len(artifacts)} artifacts from {len(child_agent_ids)} child agents")

    for artifact_path in artifacts:
        found = False
        artifact_result = HarvestedArtifact(
            source_path=artifact_path,
            destination_path="",
            size_bytes=0,
            success=False,
            error="Not found in any child agent VFS",
        )

        # Search each child agent's VFS for the artifact
        for agent_id in child_agent_ids:
            vfs_path = _get_vfs_root() / agent_id / artifact_path

            if vfs_path.exists() and vfs_path.is_file():
                try:
                    # Compute destination path
                    dest_path = destination / artifact_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file through the airlock
                    shutil.copy2(vfs_path, dest_path)

                    artifact_result = HarvestedArtifact(
                        source_path=str(vfs_path),
                        destination_path=str(dest_path),
                        size_bytes=dest_path.stat().st_size,
                        success=True,
                    )
                    found = True
                    logger.info(f"🚪 Harvested: {artifact_path} ({artifact_result.size_bytes} bytes)")
                    break

                except Exception as e:
                    artifact_result = HarvestedArtifact(
                        source_path=str(vfs_path),
                        destination_path=str(dest_path),
                        size_bytes=0,
                        success=False,
                        error=str(e),
                    )
                    logger.error(f"🚪 Failed to harvest {artifact_path}: {e}")

        if not found:
            logger.warning(f"🚪 Artifact not found: {artifact_path}")

        harvested.append(artifact_result)

    successful = sum(1 for h in harvested if h.success)
    logger.info(f"🚪 AIRLOCK complete: {successful}/{len(artifacts)} artifacts harvested")

    return harvested


def _apply_config_overrides(
    base_config: "PhoenixConfig",
    overrides: Dict[str, Any],
) -> "PhoenixConfig":
    """
    Apply dot-notation overrides to config.

    Example:
        overrides = {"city.governance.voting_threshold": 0}
        # Sets base_config.city.governance.voting_threshold = 0
    """

    # Deep copy via to_dict/from_dict
    config_dict = base_config.to_dict()

    for key, value in overrides.items():
        parts = key.split(".")
        target = config_dict

        # Navigate to parent of final key
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]

        # Set final value
        target[parts[-1]] = value

    # Reconstruct config from modified dict
    from vibe_core.phoenix import PhoenixConfig

    return PhoenixConfig.from_dict(config_dict)


async def spawn_city(
    task: str,
    circuit: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    config_factory: Optional[Callable[["PhoenixConfig"], "PhoenixConfig"]] = None,
    parent_kernel: Optional["RealVibeKernel"] = None,
    timeout_seconds: int = 300,
    artifacts: Optional[List[str]] = None,
    artifacts_destination: Optional[str] = None,
) -> SpawnCityResult:
    """
    Spawn an ephemeral child kernel and execute a task.

    This is the main entry point for 4D Hypercube operations.
    The child kernel runs with custom configuration and its results
    are folded back to the parent with cryptographic proof.

    AIRLOCK PROTOCOL:
        Before the child kernel is terminated, specified artifacts are
        harvested from the child's VFS and copied to the destination.
        This prevents data loss when the ephemeral city dies.

    Args:
        task: The task/prompt to execute in the child kernel
        circuit: Optional circuit to execute (if None, uses default routing)
        config_overrides: Dict of dot-notation overrides to apply to parent config
            Example: {"city.governance.voting_threshold": 0}
        config_factory: Alternative to overrides - function that transforms parent config
        parent_kernel: Parent kernel (if None, gets/creates one)
        timeout_seconds: Maximum execution time
        artifacts: List of file paths to harvest from child VFS before death
            Example: ["src/main.py", "tests/test_main.py"]
        artifacts_destination: Directory to copy harvested artifacts to
            Default: "ephemeral_output/{child_id}/"

    Returns:
        SpawnCityResult with output, proof, harvested_artifacts, and metadata

    Example:
        # Fast coding with artifact harvesting
        result = await spawn_city(
            task="Implement user login feature",
            circuit="fast_code",
            config_overrides={
                "city.governance.voting_threshold": 0,
                "city.governance.quorum_required": 0,
            },
            artifacts=["src/auth.py", "tests/test_auth.py"],
            artifacts_destination="output/auth_feature/",
        )

        if result.success:
            print(f"Output: {result.output}")
            print(f"Proof: {result.proof}")
            for artifact in result.harvested_artifacts:
                if artifact.success:
                    print(f"Harvested: {artifact.destination_path}")
    """

    logger.info(f"🌀 spawn_city: Starting ephemeral city for task: {task[:50]}...")

    # Get parent kernel
    if parent_kernel is None:
        parent_kernel = _get_or_create_kernel()

    # Build child config
    parent_config = parent_kernel.config

    if config_factory is not None:
        child_config = config_factory(parent_config)
    elif config_overrides is not None:
        child_config = _apply_config_overrides(parent_config, config_overrides)
    else:
        # Clone parent config for child
        from vibe_core.phoenix import PhoenixConfig

        child_config = PhoenixConfig.from_dict(parent_config.to_dict())

    # Spawn ephemeral child
    child = parent_kernel.spawn_child_kernel(child_config, ledger_path=":memory:")
    child_id = id(child)

    logger.info(f"🌀 Ephemeral city spawned (id: {child_id})")

    try:
        # Execute task in child kernel
        if circuit:
            # Execute specific circuit
            if hasattr(child, "execute_circuit"):
                output = await asyncio.wait_for(
                    child.execute_circuit(circuit, task),
                    timeout=timeout_seconds,
                )
            else:
                # Fallback: submit as task
                output = await asyncio.wait_for(
                    _execute_task_in_kernel(child, task, circuit),
                    timeout=timeout_seconds,
                )
        else:
            # Route task through kernel's default routing
            output = await asyncio.wait_for(
                _execute_task_in_kernel(child, task),
                timeout=timeout_seconds,
            )

        # =====================================================================
        # AIRLOCK: Harvest artifacts BEFORE child death
        # =====================================================================
        harvested: List[HarvestedArtifact] = []
        if artifacts:
            # Determine destination
            if artifacts_destination:
                dest = Path(artifacts_destination)
            else:
                dest = Path(f"ephemeral_output/{child_id}")

            harvested = _harvest_artifacts(child, artifacts, dest)

        # Get proof and merge result (child dies after this)
        proof = child.get_ledger_hash()
        merge_record = parent_kernel.merge_child_result(child, output)

        logger.info(f"🌀 Ephemeral city completed (proof: {proof})")

        return SpawnCityResult(
            success=True,
            output=output,
            proof=proof,
            child_id=child_id,
            harvested_artifacts=harvested,
            metadata={
                "merge_record": merge_record,
                "circuit": circuit,
                "config_applied": bool(config_overrides or config_factory),
                "artifacts_requested": artifacts or [],
            },
        )

    except asyncio.TimeoutError:
        logger.error(f"🌀 Ephemeral city timed out after {timeout_seconds}s")
        proof = child.get_ledger_hash()
        parent_kernel.merge_child_result(child, {"error": "timeout"})

        return SpawnCityResult(
            success=False,
            output=None,
            proof=proof,
            child_id=child_id,
            error=f"Timeout after {timeout_seconds} seconds",
        )

    except Exception as e:
        logger.error(f"🌀 Ephemeral city failed: {e}")
        proof = child.get_ledger_hash()

        try:
            parent_kernel.merge_child_result(child, {"error": str(e)})
        except ValueError:
            # Child already merged/removed
            pass

        return SpawnCityResult(
            success=False,
            output=None,
            proof=proof,
            child_id=child_id,
            error=str(e),
        )


async def _execute_task_in_kernel(
    kernel: "RealVibeKernel",
    task: str,
    circuit: Optional[str] = None,
) -> Any:
    """Execute a task in the given kernel."""
    from vibe_core.scheduling import Task

    # Create task object
    task_obj = Task(
        task_id=f"ephemeral_{id(kernel)}",
        payload={
            "prompt": task,
            "circuit": circuit,
            "type": "ephemeral_execution",
        },
    )

    # Submit to kernel scheduler
    result = await kernel.submit_task(task_obj)
    return result


def spawn_city_sync(
    task: str,
    circuit: Optional[str] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> SpawnCityResult:
    """
    Synchronous wrapper for spawn_city.

    Use this when calling from non-async code (e.g., playbook runner).
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            spawn_city(
                task=task,
                circuit=circuit,
                config_overrides=config_overrides,
                **kwargs,
            )
        )
    finally:
        loop.close()


# Convenience factory functions for common configurations
def fast_code_config(base: "PhoenixConfig") -> "PhoenixConfig":
    """
    Config factory for fast coding (no governance overhead).

    Use with: spawn_city(task="...", config_factory=fast_code_config)
    """
    return _apply_config_overrides(
        base,
        {
            "city.governance.voting_threshold": 0.0,
            "city.governance.quorum_required": 0.0,
            "kernel.features.democracy_enabled": False,
            "kernel.features.audit_logging": False,  # Speed over audit trail
        },
    )


def sandbox_config(base: "PhoenixConfig") -> "PhoenixConfig":
    """
    Config factory for sandboxed experimentation.

    Isolated environment with strict resource limits.
    """
    return _apply_config_overrides(
        base,
        {
            "city.security.sandboxed": True,
            "kernel.features.network_isolation": True,
            "kernel.system.max_memory_mb": 512,
            "kernel.system.max_execution_time_seconds": 60,
        },
    )


def research_swarm_config(base: "PhoenixConfig") -> "PhoenixConfig":
    """
    Config factory for parallel research tasks.

    Multiple agents working on research without code execution.
    """
    return _apply_config_overrides(
        base,
        {
            "city.governance.voting_threshold": 0.3,  # Low threshold
            "kernel.features.code_execution": False,
            "kernel.features.web_search": True,
            "kernel.agents.enabled": ["researcher", "analyst", "synthesizer"],
        },
    )

"""
4D Hypercube Operation: Spawn Ephemeral City

This operation enables playbooks to spawn child kernels with custom
configurations for specialized tasks. Results are folded back to the
parent kernel with cryptographic proof.

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
        circuit="fast_code"
    )

    # result.output contains the execution result
    # result.proof contains ledger hash from child
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.phoenix import PhoenixConfig

logger = logging.getLogger(__name__)


@dataclass
class SpawnCityResult:
    """Result from ephemeral city execution."""

    success: bool
    output: Any
    proof: str  # Ledger hash from child kernel
    child_id: int  # ID of the (now-dead) child kernel
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def _get_or_create_kernel() -> "RealVibeKernel":
    """Get the current kernel instance or create one."""
    from vibe_core.kernel_impl import RealVibeKernel

    # Try to get from global state first
    # (In a real execution context, the kernel would be injected)
    # For now, create a new parent kernel if none exists
    return RealVibeKernel()


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
    from dataclasses import replace

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
) -> SpawnCityResult:
    """
    Spawn an ephemeral child kernel and execute a task.

    This is the main entry point for 4D Hypercube operations.
    The child kernel runs with custom configuration and its results
    are folded back to the parent with cryptographic proof.

    Args:
        task: The task/prompt to execute in the child kernel
        circuit: Optional circuit to execute (if None, uses default routing)
        config_overrides: Dict of dot-notation overrides to apply to parent config
            Example: {"city.governance.voting_threshold": 0}
        config_factory: Alternative to overrides - function that transforms parent config
        parent_kernel: Parent kernel (if None, gets/creates one)
        timeout_seconds: Maximum execution time

    Returns:
        SpawnCityResult with output, proof, and metadata

    Example:
        # Fast coding - no governance overhead
        result = await spawn_city(
            task="Implement user login feature",
            circuit="fast_code",
            config_overrides={
                "city.governance.voting_threshold": 0,
                "city.governance.quorum_required": 0,
                "kernel.features.democracy_enabled": False,
            }
        )

        if result.success:
            print(f"Output: {result.output}")
            print(f"Proof: {result.proof}")
    """
    from vibe_core.phoenix import get_config

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

        # Get proof and merge result
        proof = child.get_ledger_hash()
        merge_record = parent_kernel.merge_child_result(child, output)

        logger.info(f"🌀 Ephemeral city completed (proof: {proof})")

        return SpawnCityResult(
            success=True,
            output=output,
            proof=proof,
            child_id=child_id,
            metadata={
                "merge_record": merge_record,
                "circuit": circuit,
                "config_applied": bool(config_overrides or config_factory),
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

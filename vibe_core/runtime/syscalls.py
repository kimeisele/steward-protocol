"""
SYSCALL REGISTRY - Mapping Symbolic Syscalls to Concrete Methods
=================================================================

OPUS-012: System Agents (BRAHMIN Architecture)

This module defines the syscall registry that maps symbolic syscall names
(used in circuits and playbooks) to concrete Python methods on plugins.

The UnifiedExecutor uses this registry to dispatch EXECUTE_SYSCALL actions.

Design:
- Syscalls are first-class citizens, not buried in plugin logic
- Any plugin can register syscalls via register_syscall()
- Envoy dispatches through get_syscall_handler()

GAD-000 Compliant:
- get_capabilities() lists all registered syscalls
- Structured errors for unknown syscalls
"""

import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SYSCALLS")


# Type alias for syscall handlers
SyscallHandler = Callable[["RealVibeKernel", Dict[str, Any]], Dict[str, Any]]


class SyscallRegistry:
    """
    Registry for mapping symbolic syscalls to handlers.

    Usage:
        registry = SyscallRegistry()
        registry.register("SPAWN_COGNITION", lifecycle_plugin.spawn_agent)
        result = registry.execute(kernel, "SPAWN_COGNITION", params)
    """

    def __init__(self):
        self._handlers: Dict[str, SyscallHandler] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        syscall_name: str,
        handler: SyscallHandler,
        description: str = "",
        plugin_id: str = "",
    ) -> None:
        """
        Register a syscall handler.

        Args:
            syscall_name: The symbolic name (e.g., "SPAWN_COGNITION")
            handler: The callable that handles the syscall
            description: Human-readable description
            plugin_id: ID of the plugin registering this syscall
        """
        if syscall_name in self._handlers:
            logger.warning(f"Overwriting syscall '{syscall_name}'")

        self._handlers[syscall_name] = handler
        self._metadata[syscall_name] = {
            "description": description,
            "plugin_id": plugin_id,
        }

        logger.info(f"📡 Registered syscall: {syscall_name} (from {plugin_id or 'unknown'})")

    def unregister(self, syscall_name: str) -> bool:
        """Remove a syscall registration."""
        if syscall_name in self._handlers:
            del self._handlers[syscall_name]
            del self._metadata[syscall_name]
            return True
        return False

    def execute(
        self,
        kernel: "RealVibeKernel",
        syscall_name: str,
        params: Optional[Dict[str, Any]] = None,
        caller_agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a syscall by name with MANDATORY ACCESS CONTROL.

        PAUNDRAKA FIX: No execution without identity verification.

        Args:
            kernel: The kernel instance
            syscall_name: The symbolic syscall name
            params: Parameters to pass to the handler
            caller_agent_id: REQUIRED - The agent executing the syscall

        Returns:
            Result dict from the handler

        Raises:
            KeyError: If syscall not registered
            PermissionError: If caller lacks required mandate
        """
        if syscall_name not in self._handlers:
            available = list(self._handlers.keys())
            raise KeyError(f"Unknown syscall: '{syscall_name}'. Available: {available}")

        # =====================================================================
        # PAUNDRAKA GATE: No Anonymous Syscalls
        # =====================================================================
        if caller_agent_id is None:
            raise PermissionError(
                f"PAUNDRAKA_BLOCKED: Syscall '{syscall_name}' requires caller_agent_id. "
                f"Anonymous syscalls are forbidden."
            )

        # Check if caller is registered in kernel
        if hasattr(kernel, "_agent_registry"):
            if caller_agent_id not in kernel._agent_registry and caller_agent_id != "kernel":
                raise PermissionError(
                    f"PAUNDRAKA_BLOCKED: Agent '{caller_agent_id}' not registered. "
                    f"Cannot execute syscall '{syscall_name}'."
                )

        # Check required mandate if specified
        required_mandate = self._metadata[syscall_name].get("required_mandate")
        if required_mandate:
            # Get agent permissions from kernel registry
            agent_permissions = []
            if hasattr(kernel, "_agent_registry") and caller_agent_id in kernel._agent_registry:
                agent = kernel._agent_registry[caller_agent_id]
                agent_permissions = getattr(agent, "permissions", []) or []
                agent_permissions = list(agent_permissions) if agent_permissions else []

            # Root agents bypass all checks
            if "root" not in agent_permissions and required_mandate not in agent_permissions:
                raise PermissionError(
                    f"PAUNDRAKA_BLOCKED: Agent '{caller_agent_id}' lacks mandate '{required_mandate}' "
                    f"for syscall '{syscall_name}'. Permissions: {agent_permissions}"
                )

        handler = self._handlers[syscall_name]
        params = params or {}

        logger.info(f"📡 Executing syscall: {syscall_name} (caller: {caller_agent_id})")

        try:
            result = handler(kernel, params)
            logger.info(f"✅ Syscall {syscall_name} completed (caller: {caller_agent_id})")
            return result
        except Exception as e:
            logger.error(f"❌ Syscall {syscall_name} failed: {e}")
            raise

    def get_handler(self, syscall_name: str) -> Optional[SyscallHandler]:
        """Get the handler for a syscall (or None if not found)."""
        return self._handlers.get(syscall_name)

    def list_syscalls(self) -> list[str]:
        """List all registered syscall names."""
        return list(self._handlers.keys())

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: What syscalls are available?"""
        return {
            "version": "1.0.0",
            "registered_syscalls": [
                {
                    "name": name,
                    "description": self._metadata[name].get("description", ""),
                    "plugin_id": self._metadata[name].get("plugin_id", ""),
                }
                for name in self._handlers
            ],
            "total_count": len(self._handlers),
        }


# =============================================================================
# Global Singleton
# =============================================================================

_syscall_registry: Optional[SyscallRegistry] = None


def get_syscall_registry() -> SyscallRegistry:
    """Get the global syscall registry singleton."""
    global _syscall_registry
    if _syscall_registry is None:
        _syscall_registry = SyscallRegistry()
        _register_default_syscalls()
    return _syscall_registry


def _register_default_syscalls() -> None:
    """
    Register default syscalls.

    Note: Plugin-specific syscalls are registered by the plugins themselves
    in their on_boot() methods. This function only registers core syscalls.
    """
    registry = _syscall_registry

    # Core syscalls are registered here
    # Plugin syscalls are registered by plugins in on_boot()

    logger.info("📡 Syscall registry initialized (core syscalls)")


# =============================================================================
# Convenience Functions
# =============================================================================


def register_syscall(
    syscall_name: str,
    handler: SyscallHandler,
    description: str = "",
    plugin_id: str = "",
) -> None:
    """Convenience function to register a syscall."""
    get_syscall_registry().register(syscall_name, handler, description, plugin_id)


def execute_syscall(
    kernel: "RealVibeKernel",
    syscall_name: str,
    params: Optional[Dict[str, Any]] = None,
    caller_agent_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to execute a syscall.

    PAUNDRAKA FIX: caller_agent_id is now REQUIRED for security.
    """
    return get_syscall_registry().execute(kernel, syscall_name, params, caller_agent_id)

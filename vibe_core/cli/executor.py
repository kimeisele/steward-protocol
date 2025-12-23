"""
CLI Executor - Handles command execution with topology awareness.

Supports:
- OFFLINE: Direct execution without kernel
- RPC: Forward to running kernel via gateway
- BOOT: Spin up ephemeral kernel
- HYBRID: Try RPC, fallback to BOOT
"""

import importlib
import inspect
import logging
from typing import Any, Callable, Dict, Optional

from .protocol import CLICommand, CLIResponse, ExecutionMode, ProgressUpdate

logger = logging.getLogger("CLI_EXECUTOR")


class CLIExecutor:
    """
    Executes CLI commands based on their execution mode.

    Handles:
    - Loading plugin modules
    - Resolving handlers
    - Executing with appropriate topology (OFFLINE/RPC/BOOT)
    - Streaming support for generators
    """

    def __init__(self, gateway_url: str = "http://localhost:8000"):
        self.gateway_url = gateway_url
        self._plugin_instances: Dict[str, Any] = {}

    async def execute(
        self,
        command: CLICommand,
        args: Dict[str, Any],
        force_mode: Optional[ExecutionMode] = None,
    ) -> CLIResponse:
        """
        Execute a CLI command.

        Args:
            command: The command definition
            args: Parsed command arguments
            force_mode: Override execution mode

        Returns:
            CLIResponse with result data
        """
        mode = force_mode or command.execution_mode

        try:
            if mode == ExecutionMode.OFFLINE:
                return await self._execute_offline(command, args)
            elif mode == ExecutionMode.RPC:
                return await self._execute_rpc(command, args)
            elif mode == ExecutionMode.BOOT:
                return await self._execute_boot(command, args)
            elif mode == ExecutionMode.HYBRID:
                return await self._execute_hybrid(command, args)
            else:
                return CLIResponse(
                    success=False,
                    data=None,
                    error=f"Unknown execution mode: {mode}",
                    execution_mode=mode,
                )
        except Exception as e:
            logger.exception(f"Command execution failed: {command.full_name}")
            return CLIResponse(
                success=False,
                data=None,
                error=str(e),
                execution_mode=mode,
            )

    async def _execute_offline(
        self,
        command: CLICommand,
        args: Dict[str, Any],
    ) -> CLIResponse:
        """Execute command without kernel - file operations only."""
        handler = self._resolve_handler(command)

        if command.supports_streaming:
            result = self._execute_streaming(handler, args)
        else:
            result = handler(**args)
            if inspect.iscoroutine(result):
                result = await result

        return CLIResponse(
            success=True,
            data=result,
            execution_mode=ExecutionMode.OFFLINE,
        )

    async def _execute_rpc(
        self,
        command: CLICommand,
        args: Dict[str, Any],
    ) -> CLIResponse:
        """Forward command to running kernel via gateway."""
        try:
            import requests
        except ImportError:
            return CLIResponse(
                success=False,
                data=None,
                error="requests library not installed for RPC mode",
                execution_mode=ExecutionMode.RPC,
            )

        # Check if kernel is running
        if not self._is_kernel_running():
            return CLIResponse(
                success=False,
                data=None,
                error="Kernel not running. Start with 'steward boot' or use --offline",
                execution_mode=ExecutionMode.RPC,
            )

        # Forward to gateway
        try:
            endpoint = f"{self.gateway_url}/v1/cli/{command.full_name}"
            # RPC remains synchronous HTTP call for now, but method is async
            response = requests.post(endpoint, json=args, timeout=30)
            response.raise_for_status()

            data = response.json()
            return CLIResponse(
                success=data.get("success", True),
                data=data.get("data"),
                error=data.get("error"),
                execution_mode=ExecutionMode.RPC,
            )
        except requests.exceptions.RequestException as e:
            return CLIResponse(
                success=False,
                data=None,
                error=f"RPC failed: {e}",
                execution_mode=ExecutionMode.RPC,
            )

    async def _execute_boot(
        self,
        command: CLICommand,
        args: Dict[str, Any],
    ) -> CLIResponse:
        """Boot ephemeral kernel, execute command, shutdown."""
        kernel = None
        try:
            # Boot kernel
            from vibe_core.kernel_impl import RealVibeKernel

            kernel = RealVibeKernel(":memory:")
            kernel.boot()

            # Get plugin instance with kernel
            handler = self._resolve_handler(command, kernel=kernel)

            if command.supports_streaming:
                result = self._execute_streaming(handler, args)
            else:
                result = handler(**args)
                if inspect.iscoroutine(result):
                    result = await result

            return CLIResponse(
                success=True,
                data=result,
                execution_mode=ExecutionMode.BOOT,
            )
        except Exception as e:
            return CLIResponse(
                success=False,
                data=None,
                error=str(e),
                execution_mode=ExecutionMode.BOOT,
            )
        finally:
            if kernel:
                try:
                    kernel.shutdown()
                except Exception:
                    pass

    async def _execute_hybrid(
        self,
        command: CLICommand,
        args: Dict[str, Any],
    ) -> CLIResponse:
        """Try RPC first, fallback to BOOT."""
        if self._is_kernel_running():
            result = await self._execute_rpc(command, args)
            if result.success:
                return result
            logger.warning(f"RPC failed, falling back to BOOT: {result.error}")

        return await self._execute_boot(command, args)

    def _resolve_handler(
        self,
        command: CLICommand,
        kernel: Optional[Any] = None,
    ) -> Callable:
        """Resolve command handler from plugin."""
        # Use plugin_id for import, fallback to namespace
        plugin_id = command.plugin_id or command.namespace
        if not plugin_id:
            raise ValueError(f"Command {command.name} has no plugin_id or namespace - cannot resolve handler")

        # Get or create plugin instance
        plugin = self._get_plugin_instance(plugin_id, kernel)

        # Get handler method
        handler = getattr(plugin, command.handler, None)
        if handler is None:
            raise ValueError(f"Handler '{command.handler}' not found on plugin '{command.namespace}'")

        return handler

    def _get_plugin_instance(
        self,
        namespace: str,
        kernel: Optional[Any] = None,
    ) -> Any:
        """Get or create plugin instance."""
        cache_key = f"{namespace}:{id(kernel) if kernel else 'none'}"

        if cache_key in self._plugin_instances:
            return self._plugin_instances[cache_key]

        # Try to import plugin
        plugin_module_paths = [
            f"vibe_core.plugins.{namespace}.plugin_main",
            f"vibe_core.plugins.{namespace}",
        ]

        plugin_class = None
        for module_path in plugin_module_paths:
            try:
                module = importlib.import_module(module_path)
                # Find plugin class - must be concrete (not abstract) and end with Plugin
                for name in dir(module):
                    obj = getattr(module, name)
                    if (
                        isinstance(obj, type)
                        and name.endswith("Plugin")
                        and not getattr(obj, "__abstractmethods__", None)
                        and hasattr(obj, "plugin_id")
                    ):
                        # Make sure it's not a base class
                        if name not in ("KernelPlugin", "BasePlugin"):
                            plugin_class = obj
                            break
                if plugin_class:
                    break
            except ImportError:
                continue

        if not plugin_class:
            raise ImportError(f"Could not find plugin class for namespace: {namespace}")

        # Instantiate
        instance = plugin_class()
        if kernel:
            instance.on_boot(kernel)

        self._plugin_instances[cache_key] = instance
        return instance

    def _execute_streaming(
        self,
        handler: Callable,
        args: Dict[str, Any],
    ) -> Any:
        """Execute a streaming handler (generator)."""
        gen = handler(**args)

        if not inspect.isgenerator(gen):
            return gen

        # Consume generator, collecting progress updates
        final_result = None
        for item in gen:
            if isinstance(item, ProgressUpdate):
                # Log progress (actual rendering done by CLI main)
                logger.debug(f"Progress: {item.message}")
            else:
                final_result = item

        return final_result

    def _is_kernel_running(self) -> bool:
        """Check if kernel is accepting connections."""
        try:
            import requests

            response = requests.get(f"{self.gateway_url}/health", timeout=1)
            return response.status_code == 200
        except Exception:
            return False

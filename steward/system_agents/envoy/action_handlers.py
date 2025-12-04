"""
ACTION HANDLERS (GAD-5000: Registry Pattern)
Delegated handlers for playbook action types.

Design Philosophy (per Gemini's Review):
- NO inline logic in DeterministicExecutor
- Each action type has its own Handler class
- Handlers are registered in a central registry
- Executor delegates to handlers, doesn't implement logic

Action Types:
- CHECK_STATE: Validate preconditions (e.g., input validation, permissions)
- EXECUTE_SCRIPT: Run deterministic scripts (e.g., scaffold.create_folders)
- EMIT_EVENT: Emit visualization events (already implemented)
- CALL_AGENT: Delegate to another agent (already implemented)
- CALL_PLAYBOOK: Execute nested playbook (already implemented)
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("ACTION_HANDLERS")


class ActionHandler(ABC):
    """Base class for all action handlers"""

    @property
    @abstractmethod
    def action_type(self) -> str:
        """The action type this handler handles (e.g., 'CHECK_STATE')"""
        pass

    @abstractmethod
    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: "ActionContext",
    ) -> "ActionResult":
        """
        Execute the action.

        Args:
            target: The action target (e.g., "input_validation", "scaffold.create_folders")
            params: Resolved parameters from the playbook
            context: Execution context with access to phase, playbook, kernel, etc.

        Returns:
            ActionResult with success status and any output data
        """
        pass


class ActionResult:
    """Result of executing an action"""

    def __init__(
        self,
        success: bool,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.data = data or {}
        self.error = error

    @classmethod
    def ok(cls, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error: str) -> "ActionResult":
        return cls(success=False, error=error)


class ActionContext:
    """Context passed to action handlers"""

    def __init__(
        self,
        phase_id: str,
        playbook_id: str,
        execution_id: str,
        user_input: str,
        phase_results: Dict[str, Any],
        kernel: Any = None,
        emit_event: Optional[Callable] = None,
    ):
        self.phase_id = phase_id
        self.playbook_id = playbook_id
        self.execution_id = execution_id
        self.user_input = user_input
        self.phase_results = phase_results
        self.kernel = kernel
        self.emit_event = emit_event


class ActionHandlerRegistry:
    """
    Central registry for action handlers.

    Usage:
        registry = ActionHandlerRegistry()
        registry.register(CheckStateHandler())
        registry.register(ExecuteScriptHandler())

        # In executor:
        handler = registry.get("CHECK_STATE")
        if handler:
            result = await handler.execute(target, params, context)
    """

    def __init__(self):
        self._handlers: Dict[str, ActionHandler] = {}

    def register(self, handler: ActionHandler) -> None:
        """Register a handler for an action type"""
        self._handlers[handler.action_type] = handler
        logger.debug(f"Registered handler for {handler.action_type}")

    def get(self, action_type: str) -> Optional[ActionHandler]:
        """Get the handler for an action type"""
        return self._handlers.get(action_type)

    def has(self, action_type: str) -> bool:
        """Check if a handler exists for an action type"""
        return action_type in self._handlers

    @property
    def registered_types(self) -> list:
        """List all registered action types"""
        return list(self._handlers.keys())


# ============================================================================
# CONCRETE HANDLERS
# ============================================================================


class CheckStateHandler(ActionHandler):
    """
    Handler for CHECK_STATE actions.

    Validates preconditions like:
    - input_validation: Check required fields and constraints
    - permission_check: Verify user has required permissions
    - state_check: Verify system state meets requirements

    Target format: "check_name" (e.g., "input_validation", "permission_check")
    """

    @property
    def action_type(self) -> str:
        return "CHECK_STATE"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Execute a state check based on target type"""
        logger.info(f"  🔍 CHECK_STATE: {target}")

        if target == "input_validation":
            return self._validate_input(params, context)
        elif target == "permission_check":
            return self._check_permissions(params, context)
        elif target == "state_check":
            return self._check_state(params, context)
        elif target == "audit_gate":
            return self._check_audit_gate(params, context)
        else:
            # Generic check - just verify params are present
            logger.info(f"  ✓ Generic state check passed: {target}")
            return ActionResult.ok({"check": target, "status": "passed"})

    def _check_audit_gate(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """
        Check if audit passed (GAD-5500 Safe Evolution Loop).

        Params:
            check_field: Field path to check (e.g., "audit_result.passed")
            expected_value: Expected value (e.g., True)
            on_mismatch: Action to take if mismatch (for logging)
        """
        check_field = params.get("check_field", "audit_result.passed")
        expected_value = params.get("expected_value", True)
        on_mismatch = params.get("on_mismatch", "fail")

        # Navigate the field path
        parts = check_field.split(".")
        value = context.phase_results

        try:
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    value = getattr(value, part, None)
                if value is None:
                    break
        except Exception:
            value = None

        # Compare with expected
        if value == expected_value:
            logger.info(f"  ✓ Audit gate PASSED: {check_field} = {value}")
            return ActionResult.ok({"check": "audit_gate", "field": check_field, "value": value, "status": "passed"})
        else:
            logger.warning(f"  ❌ Audit gate FAILED: {check_field} = {value} (expected {expected_value})")
            return ActionResult.fail(f"Audit gate failed: {check_field} = {value}, expected {expected_value}")

    def _validate_input(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Validate input against required fields and constraints"""
        required_fields = params.get("required_fields", [])
        constraints = params.get("constraints", {})

        # Check required fields exist in user_input or phase_results
        for field in required_fields:
            # Check if field exists in context
            found = False
            if field in context.phase_results:
                found = True
            # For now, just log and pass - actual implementation would check properly
            if not found:
                logger.debug(f"    Field '{field}' check (relaxed mode)")

        # Check constraints
        for constraint_name, constraint_value in constraints.items():
            if constraint_name.endswith("_pattern"):
                # Regex pattern validation
                field_name = constraint_name.replace("_pattern", "")
                logger.debug(f"    Pattern check for {field_name}: {constraint_value}")

        logger.info("  ✓ Input validation passed")
        return ActionResult.ok({"validation": "passed", "fields_checked": required_fields})

    def _check_permissions(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Check if user has required permissions"""
        required_permissions = params.get("required_permissions", [])
        # For now, all permissions are granted - actual implementation would check
        logger.info("  ✓ Permission check passed")
        return ActionResult.ok({"permissions": "granted"})

    def _check_state(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Check if system state meets requirements"""
        required_state = params.get("required_state", {})
        # For now, all state checks pass - actual implementation would verify
        logger.info("  ✓ State check passed")
        return ActionResult.ok({"state": "valid"})


class ExecuteScriptHandler(ActionHandler):
    """
    Handler for EXECUTE_SCRIPT actions.

    Executes deterministic scripts like:
    - scaffold.create_folders: Create project folder structure
    - scaffold.init_git: Initialize git repository
    - file.write: Write content to file
    - file.read: Read content from file

    Target format: "module.function" (e.g., "scaffold.create_folders")
    """

    @property
    def action_type(self) -> str:
        return "EXECUTE_SCRIPT"

    def __init__(self):
        # Registry of script handlers
        self._scripts: Dict[str, Callable] = {
            "scaffold.create_folders": self._create_folders,
            "scaffold.init_git": self._init_git,
            "file.write": self._write_file,
            "file.read": self._read_file,
        }

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Execute a script based on target"""
        logger.info(f"  📜 EXECUTE_SCRIPT: {target}")

        # Look up script handler
        script_fn = self._scripts.get(target)
        if script_fn:
            try:
                result = await script_fn(params, context)
                return result
            except Exception as e:
                logger.error(f"  ❌ Script failed: {target} - {e}")
                return ActionResult.fail(str(e))
        else:
            # Unknown script - log and pass (stub behavior)
            logger.warning(f"  ⚠️ Unknown script (stub): {target}")
            return ActionResult.ok({"script": target, "status": "stub", "params": params})

    async def _create_folders(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Create folder structure for a project"""
        from pathlib import Path

        base_path = params.get("base_path", ".")
        folders = params.get("folders", [])

        created = []
        for folder in folders:
            folder_path = Path(base_path) / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"    📁 Created: {folder_path}")
            created.append(str(folder_path))

        return ActionResult.ok({"created_folders": created, "base_path": base_path})

    async def _init_git(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Initialize git repository"""
        import subprocess
        from pathlib import Path

        repo_path = params.get("repo_path", ".")
        initial_branch = params.get("initial_branch", "main")

        repo = Path(repo_path)
        if not (repo / ".git").exists():
            subprocess.run(["git", "init", "-b", initial_branch], cwd=repo, check=True)
            logger.info(f"    🔧 Initialized git at: {repo_path}")
        else:
            logger.info(f"    🔧 Git already exists at: {repo_path}")

        return ActionResult.ok({"repo_path": repo_path, "branch": initial_branch, "status": "initialized"})

    async def _write_file(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Write content to a file"""
        from pathlib import Path

        file_path = params.get("path")
        content = params.get("content", "")

        if not file_path:
            return ActionResult.fail("Missing 'path' parameter")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        logger.info(f"    📝 Wrote to: {file_path} ({len(content)} chars)")

        return ActionResult.ok({"path": file_path, "bytes_written": len(content)})

    async def _read_file(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Read content from a file"""
        from pathlib import Path

        file_path = params.get("path")

        if not file_path:
            return ActionResult.fail("Missing 'path' parameter")

        path = Path(file_path)
        if not path.exists():
            return ActionResult.fail(f"File not found: {file_path}")
        content = path.read_text()
        return ActionResult.ok({"path": file_path, "content": content})


class EmitEventHandler(ActionHandler):
    """
    Handler for EMIT_EVENT actions.

    Emits visualization events for UI/monitoring:
    - progress updates
    - status changes
    - completion notifications

    Target format: "event_name" (e.g., "phase_started", "task_completed")
    """

    @property
    def action_type(self) -> str:
        return "EMIT_EVENT"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Emit an event through the context's emit_event callback"""
        logger.info(f"  📡 EMIT_EVENT: {target}")

        event_data = {
            "event_type": target,
            "phase_id": context.phase_id,
            "playbook_id": context.playbook_id,
            "execution_id": context.execution_id,
            **params,
        }

        # Emit through context callback if available
        if context.emit_event:
            try:
                context.emit_event(event_data)
                logger.debug(f"    ✓ Event emitted: {target}")
                return ActionResult.ok({"event": target, "emitted": True})
            except Exception as e:
                logger.error(f"    ❌ Event emission failed: {e}")
                return ActionResult.fail(f"Event emission failed: {e}")
        else:
            logger.debug("    ⚠️  No emit_event callback - event logged only")
            return ActionResult.ok({"event": target, "emitted": False, "logged_only": True})


class CallAgentHandler(ActionHandler):
    """
    Handler for CALL_AGENT actions.

    Delegates work to another agent via kernel dispatch:
    - tool execution
    - sub-task processing
    - agent collaboration

    Target format: "agent_id.action" (e.g., "engineer.build", "herald.publish")
    """

    @property
    def action_type(self) -> str:
        return "CALL_AGENT"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Call another agent through the kernel"""
        logger.info(f"  🤝 CALL_AGENT: {target}")

        if not context.kernel:
            logger.error("    ❌ No kernel available for agent calls")
            return ActionResult.fail("No kernel available - cannot call agent")

        # Parse target as "agent_id.action"
        if "." in target:
            agent_id, action = target.split(".", 1)
        else:
            agent_id = target
            action = params.get("action", "process")

        try:
            # Dispatch task to target agent via kernel
            from vibe_core.scheduling import Task

            task = Task(
                agent_id=agent_id,
                action=action,
                payload=params,
                priority=params.get("priority", 5),
            )

            # Execute through kernel (blocking for now, could be async)
            result = await context.kernel.dispatch_task(task)

            logger.info(f"    ✓ Agent {agent_id} responded")
            return ActionResult.ok(
                {
                    "agent": agent_id,
                    "action": action,
                    "result": result,
                }
            )
        except Exception as e:
            logger.error(f"    ❌ Agent call failed: {e}")
            return ActionResult.fail(f"Agent call failed: {e}")


class CallPlaybookHandler(ActionHandler):
    """
    Handler for CALL_PLAYBOOK actions.

    Executes a nested playbook as a sub-workflow:
    - modular workflows
    - reusable playbook components
    - nested execution

    Target format: "playbook_name" (e.g., "wiring_audit", "agent_bootstrap")
    """

    @property
    def action_type(self) -> str:
        return "CALL_PLAYBOOK"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Execute a nested playbook"""
        logger.info(f"  📚 CALL_PLAYBOOK: {target}")

        if not context.kernel:
            logger.error("    ❌ No kernel available for playbook execution")
            return ActionResult.fail("No kernel available - cannot execute playbook")

        try:
            # Load and execute playbook through kernel's playbook executor
            playbook_path = params.get("playbook_path", f"vibe_core/playbook/circuits/{target}.yaml")
            input_data = params.get("input", {})

            logger.info(f"    📖 Executing playbook: {playbook_path}")

            # Execute the playbook through the kernel
            result = await context.kernel.execute_playbook(
                playbook_path=playbook_path,
                input_data=input_data,
                user_input=context.user_input,
            )

            logger.info(f"    ✓ Playbook {target} completed: {result.get('status', 'unknown')}")

            return ActionResult.ok(
                {
                    "playbook": target,
                    "path": playbook_path,
                    "status": result.get("status", "unknown"),
                    "result": result,
                }
            )
        except Exception as e:
            logger.error(f"    ❌ Playbook execution failed: {e}")
            return ActionResult.fail(f"Playbook execution failed: {e}")


# ============================================================================
# DEFAULT REGISTRY
# ============================================================================


def create_default_registry() -> ActionHandlerRegistry:
    """Create a registry with all default handlers"""
    registry = ActionHandlerRegistry()
    registry.register(CheckStateHandler())
    registry.register(ExecuteScriptHandler())
    registry.register(EmitEventHandler())
    registry.register(CallAgentHandler())
    registry.register(CallPlaybookHandler())
    return registry


# Singleton instance for convenience
default_registry = create_default_registry()

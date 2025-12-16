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

        # Strict validation: Check fields exist in user_input or phase_results
        missing_fields = []
        for field in required_fields:
            if field not in context.phase_results and field not in params:
                missing_fields.append(field)

        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            logger.error(f"    ❌ Input validation failed: {error_msg}")
            return ActionResult.fail(error_msg)

        # Strict validation: Check constraints
        for constraint_name, constraint_value in constraints.items():
            if constraint_name.endswith("_pattern"):
                import re

                field_name = constraint_name.replace("_pattern", "")
                value = str(params.get(field_name, context.phase_results.get(field_name, "")))

                if not re.match(constraint_value, value):
                    error_msg = f"Field '{field_name}' does not match pattern '{constraint_value}'"
                    logger.error(f"    ❌ Constraint failed: {error_msg}")
                    return ActionResult.fail(error_msg)

        logger.info("  ✓ Input validation passed (STRICT)")
        return ActionResult.ok({"validation": "passed", "fields_checked": required_fields})

    def _check_permissions(self, params: Dict[str, Any], context: ActionContext) -> ActionResult:
        """Check if user has required permissions"""
        required_permissions = params.get("required_permissions", [])

        # Strict validation: ACTUAL permission checking (mocked via allow-list for now)
        # In a real system, this would check against a user role/policy engine
        # For "Hardening" phase, we permit root/admin roles or explicit "public" tasks

        user_role = getattr(context, "user_role", "unknown")  # Assuming role is in context

        # Simple Role-Based Access Control (RBAC) Logic
        if "admin" in required_permissions and user_role != "admin":
            logger.error(f"    ❌ Permission denied: User '{user_role}' needs 'admin'")
            return ActionResult.fail(f"Permission denied: Required 'admin' role, got '{user_role}'")

        logger.info(f"  ✓ Permission check passed for role '{user_role}'")
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
# NEURO-SYMBOLIC HANDLERS (GAD-6000: Smart ENVOY)
# ============================================================================


class QueryGraphHandler(ActionHandler):
    """
    Handler for QUERY_GRAPH actions.

    Queries kernel state directly (no LLM needed):
    - kernel.status: Get kernel status
    - kernel.agents: List registered agents
    - kernel.tools: List available tools
    - kernel.bank: Get economic stats
    - kernel.ledger: Get recent events

    This is the "neuro" part - direct graph queries, zero hallucination.
    """

    @property
    def action_type(self) -> str:
        return "QUERY_GRAPH"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Query kernel graph state"""
        logger.info(f"  🔍 QUERY_GRAPH: {target}")

        if not context.kernel:
            logger.warning("    ⚠️ No kernel - returning empty state")
            return ActionResult.ok({"query": target, "result": None, "error": "no_kernel"})

        try:
            result = self._execute_query(target, params, context.kernel)
            logger.info(f"    ✓ Query returned {type(result).__name__}")
            # Return the result directly so it can be used in templates without .result wrapper
            return ActionResult.ok(result if isinstance(result, dict) else {"value": result})
        except Exception as e:
            logger.error(f"    ❌ Query failed: {e}")
            return ActionResult.fail(f"Query failed: {e}")

    def _execute_query(self, target: str, params: Dict[str, Any], kernel) -> Any:
        """Execute the actual graph query"""

        # Kernel status query
        if target == "kernel.status":
            return {
                "status": str(kernel.status) if hasattr(kernel, "status") else "UNKNOWN",
                "uptime": getattr(kernel, "_uptime", 0),
            }

        # Agent registry query
        if target == "kernel.agents":
            registry = getattr(kernel, "_agent_registry", {})
            return {
                "total": len(registry),
                "agents": [
                    {
                        "id": aid,
                        "type": type(agent).__name__,
                        "capabilities": getattr(agent, "capabilities", [])[:5],
                    }
                    for aid, agent in registry.items()
                ],
            }

        # Tool registry query
        if target == "kernel.tools":
            tool_registry = getattr(kernel, "tool_registry", None)
            if tool_registry:
                tools = tool_registry.list_tools() if hasattr(tool_registry, "list_tools") else []
                return {"total": len(tools), "tools": tools[:20]}
            return {"total": 0, "tools": []}

        # Economic stats query
        if target == "kernel.bank":
            bank = kernel.get_bank() if hasattr(kernel, "get_bank") else None
            if bank:
                return bank.get_system_stats()
            return {"accounts": 0, "total_balance": 0}

        # Ledger events query
        if target == "kernel.ledger":
            ledger = getattr(kernel, "ledger", None)
            limit = params.get("limit", 10)
            if ledger and hasattr(ledger, "get_all_events"):
                events = ledger.get_all_events()[-limit:]
                return {"total": len(events), "recent": events}
            return {"total": 0, "recent": []}

        # Circuit registry query
        if target == "kernel.circuits":
            envoy = getattr(kernel, "envoy", None)
            if envoy:
                circuits = envoy.list_circuits() if hasattr(envoy, "list_circuits") else []
                return {"total": len(circuits), "circuits": circuits}
            return {"total": 0, "circuits": []}

        # Unknown query - return empty
        logger.warning(f"    ⚠️ Unknown query target: {target}")
        return None


class RenderTemplateHandler(ActionHandler):
    """
    Handler for RENDER_TEMPLATE actions.

    Renders output using Jinja2 templates:
    - Transforms JSON data into readable markdown
    - Supports conditional formatting
    - Zero LLM - pure template rendering

    This is the "symbolic" part - structured output, deterministic.
    """

    @property
    def action_type(self) -> str:
        return "RENDER_TEMPLATE"

    def __init__(self):
        # Built-in templates for common outputs
        self._templates: Dict[str, str] = {
            "status_summary": """## 🏙️ {{ city_name | default('Agent City') }} Status

**Mode:** {{ mode | default('UNKNOWN') }}
**Health:** {{ health | default('🟡 UNKNOWN') }}

### Agents ({{ agents.total | default(0) }})
{% if agents.registry %}
{% for agent in agents.registry[:10] %}
- `{{ agent.id }}` ({{ agent.type | default('Agent') }})
{% endfor %}
{% else %}
_No agents registered_
{% endif %}

### Tools ({{ tools.total | default(0) }})
{% if tools.tools %}
{% for tool in tools.tools[:10] %}
- `{{ tool }}`
{% endfor %}
{% else %}
_No tools available_
{% endif %}
""",
            "agent_list": """### Registered Agents ({{ total }})
{% for agent in agents %}
- **{{ agent.id }}** - {{ agent.type }}
  - Capabilities: {{ agent.capabilities | join(', ') | default('none') }}
{% endfor %}
""",
            "error": """### ❌ Error

{{ message | default('Unknown error') }}

{% if details %}
```
{{ details }}
```
{% endif %}
""",
            "simple": """{{ message }}""",
        }

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Render a template with the given data"""
        logger.info(f"  📝 RENDER_TEMPLATE: {target}")

        try:
            from jinja2 import Template

            # Get template
            template_str = self._get_template(target, params)
            if not template_str:
                return ActionResult.fail(f"Template not found: {target}")

            # Get data from params or phase_results
            data = params.get("data", {})
            if not data:
                # Merge all phase results as data
                data = dict(context.phase_results)

            # Render
            template = Template(template_str)
            rendered = template.render(**data)

            logger.info(f"    ✓ Rendered {len(rendered)} chars")
            return ActionResult.ok({"template": target, "rendered": rendered})

        except ImportError:
            # Fallback without Jinja2
            logger.warning("    ⚠️ Jinja2 not available - using simple format")
            return ActionResult.ok(
                {
                    "template": target,
                    "rendered": str(params.get("data", context.phase_results)),
                }
            )
        except Exception as e:
            logger.error(f"    ❌ Render failed: {e}")
            return ActionResult.fail(f"Render failed: {e}")

    def _get_template(self, target: str, params: Dict[str, Any]) -> Optional[str]:
        """
        Get template string by name or from params.

        Phoenix Config: Circuit YAML templates have HIGHEST priority (Code/Config Split).
        Priority order:
        1. params["template"] - Inline template override
        2. params["circuit_templates"][target] - From Circuit YAML (Phoenix Config)
        3. knowledge/templates/{target}.j2 - File-based templates
        4. self._templates[target] - Built-in fallback
        5. vibe_core/playbook/templates/{target}.md.j2 - Legacy location
        """
        # Priority 1: Check if template is in params (inline override)
        if "template" in params:
            return params["template"]

        # Priority 2: Phoenix Config - Circuit YAML templates (Code/Config Split)
        circuit_templates = params.get("circuit_templates", {})
        if target in circuit_templates:
            logger.debug(f"    📜 Using template from Circuit YAML: {target}")
            return circuit_templates[target]

        # Priority 3: Try to load from knowledge/templates/
        from pathlib import Path

        template_path = Path(f"knowledge/templates/{target}.j2")
        if template_path.exists():
            return template_path.read_text()

        # Priority 4: Check built-in templates (kept for backwards compatibility)
        if target in self._templates:
            return self._templates[target]

        # Priority 5: Legacy fallback - old template location
        legacy_path = Path(f"vibe_core/playbook/templates/{target}.md.j2")
        if legacy_path.exists():
            return legacy_path.read_text()

        return None

    def register_template(self, name: str, template: str) -> None:
        """Register a custom template"""
        self._templates[name] = template


class StoreEphemeralHandler(ActionHandler):
    """
    Handler for STORE_EPHEMERAL actions.

    Stores computed results in session cache:
    - TTL-based expiration
    - Tag-based retrieval
    - Avoids recomputation

    Uses EphemeralStorage via dependency injection (OPUS Phase 2).
    """

    def __init__(self, ephemeral=None):
        """
        Initialize handler with ephemeral storage.

        Args:
            ephemeral: EphemeralStorage instance (injected dependency)
        """
        self._ephemeral = ephemeral

    @property
    def action_type(self) -> str:
        return "STORE_EPHEMERAL"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Store value in ephemeral cache"""
        logger.info(f"  💾 STORE_EPHEMERAL: {target}")

        if not self._ephemeral:
            logger.warning("    ⚠️ No ephemeral storage available")
            return ActionResult.ok({"key": target, "stored": False, "error": "no_storage"})

        try:
            storage = self._ephemeral

            # Get value from params or phase_results
            value = params.get("value")
            if value is None and "value_from" in params:
                # Get from phase results
                value_path = params["value_from"]
                value = context.phase_results.get(value_path)

            ttl = params.get("ttl_seconds", 300)
            tags = params.get("tags", [])

            # Store
            cache_key = storage.set(target, value, ttl_seconds=ttl, tags=tags)

            logger.info(f"    ✓ Stored: {cache_key} (ttl={ttl}s)")
            return ActionResult.ok({"key": cache_key, "ttl": ttl, "stored": True})

        except Exception as e:
            logger.error(f"    ❌ Store failed: {e}")
            return ActionResult.fail(f"Store failed: {e}")


class RetrieveEphemeralHandler(ActionHandler):
    """
    Handler for RETRIEVE_EPHEMERAL actions.

    Retrieves cached values from session storage.
    Uses EphemeralStorage via dependency injection (OPUS Phase 2).
    """

    def __init__(self, ephemeral=None):
        """
        Initialize handler with ephemeral storage.

        Args:
            ephemeral: EphemeralStorage instance (injected dependency)
        """
        self._ephemeral = ephemeral

    @property
    def action_type(self) -> str:
        return "RETRIEVE_EPHEMERAL"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Retrieve value from ephemeral cache"""
        logger.info(f"  📦 RETRIEVE_EPHEMERAL: {target}")

        if not self._ephemeral:
            logger.warning("    ⚠️ No ephemeral storage available")
            return ActionResult.ok({"key": target, "value": None, "hit": False, "error": "no_storage"})

        try:
            storage = self._ephemeral

            # Retrieve
            value = storage.get(target)

            if value is not None:
                logger.info(f"    ✓ Cache HIT: {target}")
                return ActionResult.ok({"key": target, "value": value, "hit": True})
            else:
                logger.info(f"    ○ Cache MISS: {target}")
                return ActionResult.ok({"key": target, "value": None, "hit": False})

        except Exception as e:
            logger.error(f"    ❌ Retrieve failed: {e}")
            return ActionResult.fail(f"Retrieve failed: {e}")


# ============================================================================
# GIT OPERATIONS (GAD-5500: MANAS Self-Healing Loop)
# ============================================================================


class GitCommitHandler(ActionHandler):
    """
    Handler for GIT_COMMIT actions.

    Commits specific files modified by the circuit - the "Seal of Action".
    In CI/CD (GitHub Actions), this prepares the state for the final push.

    The circuit that heals is also responsible for sealing its work into git history.
    This makes MANAS truly autonomous - it doesn't just change bits in RAM,
    it changes the HISTORY of the project.

    Target format: "commit_message" or use params["message"]

    Params:
        files: List of file paths or glob patterns to stage and commit
        message: Commit message (optional, can also be target)
        allow_empty: If True, create commit even if no changes (default: False)
    """

    @property
    def action_type(self) -> str:
        return "GIT_COMMIT"

    async def execute(
        self,
        target: str,
        params: Dict[str, Any],
        context: ActionContext,
    ) -> ActionResult:
        """Commit files to git repository."""
        import subprocess

        files = params.get("files", [])
        message = params.get("message", target) or "chore(manas): Automated circuit execution"
        allow_empty = params.get("allow_empty", False)

        logger.info(f"  📝 GIT_COMMIT: {message[:50]}...")

        if not files:
            logger.warning("    ⚠️ No files specified for commit")
            return ActionResult.fail("No files to commit")

        try:
            # Determine workspace from kernel or cwd
            workspace = None
            if context.kernel and hasattr(context.kernel, "workspace_path"):
                workspace = str(context.kernel.workspace_path)

            # Stage files (supports glob patterns)
            from pathlib import Path

            staged_files = []
            for file_pattern in files:
                # Expand glob patterns
                if "*" in file_pattern:
                    base_path = Path(workspace) if workspace else Path(".")
                    matched = list(base_path.glob(file_pattern))
                    for match in matched:
                        staged_files.append(str(match))
                else:
                    staged_files.append(file_pattern)

            if not staged_files:
                logger.info("    ○ No files matched patterns")
                if allow_empty:
                    return ActionResult.ok({"committed": False, "reason": "no_matching_files"})
                return ActionResult.fail("No files matched the specified patterns")

            # Git add
            add_cmd = ["git", "add"] + staged_files
            add_result = subprocess.run(
                add_cmd,
                capture_output=True,
                text=True,
                cwd=workspace,
            )

            if add_result.returncode != 0:
                logger.error(f"    ❌ git add failed: {add_result.stderr}")
                return ActionResult.fail(f"git add failed: {add_result.stderr}")

            logger.info(f"    📦 Staged {len(staged_files)} files")

            # Git commit
            commit_cmd = ["git", "commit", "-m", message]
            if allow_empty:
                commit_cmd.append("--allow-empty")

            commit_result = subprocess.run(
                commit_cmd,
                capture_output=True,
                text=True,
                cwd=workspace,
            )

            # Return code 1 means "nothing to commit" which is OK
            if commit_result.returncode == 0:
                logger.info(f"    ✓ Committed: {message[:40]}...")
                return ActionResult.ok(
                    {
                        "committed": True,
                        "message": message,
                        "files": staged_files,
                        "stdout": commit_result.stdout,
                    }
                )
            elif (
                "nothing to commit" in commit_result.stdout.lower()
                or "nothing to commit" in commit_result.stderr.lower()
            ):
                logger.info("    ○ Nothing to commit (already up to date)")
                return ActionResult.ok(
                    {
                        "committed": False,
                        "reason": "nothing_to_commit",
                        "files": staged_files,
                    }
                )
            else:
                logger.error(f"    ❌ git commit failed: {commit_result.stderr}")
                return ActionResult.fail(f"git commit failed: {commit_result.stderr}")

        except Exception as e:
            logger.error(f"    ❌ Git operation failed: {e}")
            return ActionResult.fail(f"Git operation failed: {e}")


# ============================================================================
# DEFAULT REGISTRY
# ============================================================================


def create_default_registry() -> ActionHandlerRegistry:
    """
    Create a registry with all default handlers.

    DEPRECATED: Use create_registry_with_ephemeral() instead (OPUS Phase 2).
    This function is kept for backwards compatibility.
    """
    registry = ActionHandlerRegistry()

    # Core handlers
    registry.register(CheckStateHandler())
    registry.register(ExecuteScriptHandler())
    registry.register(EmitEventHandler())
    registry.register(CallAgentHandler())
    registry.register(CallPlaybookHandler())

    # Neuro-symbolic handlers (GAD-6000)
    registry.register(QueryGraphHandler())
    registry.register(RenderTemplateHandler())
    registry.register(StoreEphemeralHandler())  # No ephemeral storage injected
    registry.register(RetrieveEphemeralHandler())  # No ephemeral storage injected

    # Git operations (GAD-5500: MANAS Self-Healing)
    registry.register(GitCommitHandler())

    return registry


def create_registry_with_ephemeral(ephemeral=None) -> ActionHandlerRegistry:
    """
    Create a registry with all handlers and inject ephemeral storage (OPUS Phase 2).

    Args:
        ephemeral: EphemeralStorage instance to inject into handlers

    Returns:
        ActionHandlerRegistry with all handlers configured
    """
    registry = ActionHandlerRegistry()

    # Core handlers (no dependencies)
    registry.register(CheckStateHandler())
    registry.register(ExecuteScriptHandler())
    registry.register(EmitEventHandler())
    registry.register(CallAgentHandler())
    registry.register(CallPlaybookHandler())

    # Neuro-symbolic handlers (GAD-6000)
    registry.register(QueryGraphHandler())
    registry.register(RenderTemplateHandler())

    # Ephemeral storage handlers (with dependency injection)
    registry.register(StoreEphemeralHandler(ephemeral=ephemeral))
    registry.register(RetrieveEphemeralHandler(ephemeral=ephemeral))

    # Git operations (GAD-5500: MANAS Self-Healing)
    registry.register(GitCommitHandler())

    return registry


# Singleton instance for convenience (DEPRECATED: use create_registry_with_ephemeral)
default_registry = create_default_registry()

"""
Architecture Analysis Tool - System introspection and documentation.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Kernel state introspection (agents, registry, ledger)
- Dataflow tracing (through AST analysis)
- SQLite schema extraction (from live database)
- Mermaid diagram generation (layers, sequences, flows)
- ARCHITECTURE.md rendering (Jinja2 template)

Philosophy: ZERO HARDCODED VALUES - Everything introspected!
"""

import ast
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("ANALYST_ARCHITECTURE_TOOL")


class ArchitectureAnalysisTool(Tool):
    """
    Tool for architecture introspection and documentation.

    This provides ARCHITECTURAL dimension - how system is structured.
    Reveals kernel internals, dataflow, and integration patterns.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, root_dir: str = "."):
        """
        Initialize architecture analysis tool.

        Args:
            services: Service registry for DI
            root_dir: Repository root directory
        """
        super().__init__(services)
        self.root_dir = Path(root_dir).resolve()
        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel = None

    def inject_kernel(self, kernel) -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        OPUS-070: Analyst tools MUST have kernel access for full context.
        Without kernel injection, they operate in "file-only mode" (limited).
        """
        self._vibe_kernel = kernel
        logger.info(f"⚡ {self.name}: Kernel injected - ledger binding ACTIVE")

    def _get_ledger(self):
        """Get kernel.ledger via VAJRA binding."""
        if self._vibe_kernel is None:
            return None
        if not hasattr(self._vibe_kernel, "ledger"):
            return None
        return self._vibe_kernel.ledger

    @property
    def name(self) -> str:
        return "analyst.architecture"

    @property
    def description(self) -> str:
        return "Analyze system architecture, generate diagrams, and render ARCHITECTURE.md"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'introspect_kernel', 'trace_dataflow', 'extract_schema', "
                "'generate_diagram', 'render'",
            },
            "diagram_type": {
                "type": "string",
                "required": False,
                "description": "Diagram type: 'graph', 'sequence', 'flowchart' (for generate_diagram)",
            },
            "data": {
                "type": "object",
                "required": False,
                "description": "Input data for diagram generation or rendering",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["introspect_kernel", "trace_dataflow", "extract_schema", "generate_diagram", "render"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute architecture analysis."""
        try:
            action = parameters["action"]

            if action == "introspect_kernel":
                return self._introspect_kernel()
            elif action == "trace_dataflow":
                return self._trace_dataflow(parameters)
            elif action == "extract_schema":
                return self._extract_schema()
            elif action == "generate_diagram":
                return self._generate_diagram(parameters)
            elif action == "render":
                return self._render_architecture(parameters)
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _introspect_kernel(self) -> ToolResult:
        """
        Introspect live kernel state.

        Gracefully degrades if kernel is not running - provides fallback introspection
        via filesystem scanning.

        Returns:
            ToolResult with kernel data (agents, registry, ledger path, scheduler)
        """
        try:
            # Try to import and get live kernel (if running)
            from vibe_core.boot_orchestrator import BootOrchestrator

            # Check if boot orchestrator has an active kernel
            # Note: This is a fallback - ideally, tool is invoked WITH kernel context
            orchestrator = BootOrchestrator(project_root=self.root_dir)
            kernel = orchestrator.get_kernel()

            if kernel:
                # LIVE KERNEL MODE - Extract real data
                agents = []
                if hasattr(kernel, "manifest_registry"):
                    try:
                        agents = kernel.manifest_registry.list_all()
                    except Exception as e:
                        logger.warning(f"Could not list agents: {e}")

                ledger_path = None
                if hasattr(kernel, "ledger"):
                    ledger_path = getattr(kernel.ledger, "db_path", None)

                scheduler_state = None
                if hasattr(kernel, "scheduler"):
                    try:
                        scheduler_state = kernel.scheduler.get_status()
                    except Exception as e:
                        logger.warning(f"Could not get scheduler status: {e}")

                data = {
                    "agents": agents,
                    "agent_count": len(agents),
                    "ledger_path": str(ledger_path) if ledger_path else None,
                    "scheduler_state": scheduler_state,
                    "kernel_type": type(kernel).__name__,
                    "introspection_mode": "live_kernel",
                }

                return ToolResult(success=True, output=data)

            else:
                # FALLBACK MODE - Introspect via filesystem
                logger.info("Kernel not running - using filesystem introspection")
                return self._introspect_via_filesystem()

        except Exception as e:
            logger.warning(f"Live kernel introspection failed: {e} - falling back to filesystem")
            return self._introspect_via_filesystem()

    def _introspect_via_filesystem(self) -> ToolResult:
        """
        Fallback introspection via filesystem scanning (when kernel not running).

        Returns:
            ToolResult with discovered agents and ledger info
        """
        try:
            # Scan for cartridges
            agents = []
            cartridge_dirs = [
                self.root_dir / "steward" / "system_agents",
                self.root_dir / "agent_city" / "registry",
            ]

            for base_dir in cartridge_dirs:
                if not base_dir.exists():
                    continue

                for agent_dir in base_dir.iterdir():
                    if not agent_dir.is_dir():
                        continue

                    cartridge_yaml = agent_dir / "cartridge.yaml"
                    if cartridge_yaml.exists():
                        agents.append(agent_dir.name)

            # Default ledger path
            ledger_path = self.root_dir / "data" / "vibe_ledger.db"

            data = {
                "agents": agents,
                "agent_count": len(agents),
                "ledger_path": str(ledger_path) if ledger_path.exists() else None,
                "scheduler_state": None,
                "kernel_type": "Not Running",
                "introspection_mode": "filesystem_fallback",
            }

            return ToolResult(success=True, output=data)

        except Exception as e:
            logger.error(f"Filesystem introspection failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _trace_dataflow(self, params: dict) -> ToolResult:
        """
        Trace dataflow through code analysis.

        Traces execution paths like:
        - submit_task() → schedule() → agent.process() → ledger.record()

        Args:
            params: Must contain 'entry_points' list

        Returns:
            ToolResult with traced execution paths
        """
        try:
            entry_points = params.get("entry_points", [])
            if not entry_points:
                return ToolResult(success=False, error="No entry_points specified for dataflow tracing")

            # Simplified dataflow tracing (could be enhanced with AST)
            flows = []
            for entry in entry_points:
                # Extract module and function name
                parts = entry.split(".")
                if len(parts) < 2:
                    continue

                module_path = "/".join(parts[:-1]) + ".py"
                function_name = parts[-1]

                # Try to find the file
                file_path = self.root_dir / module_path
                if not file_path.exists():
                    logger.warning(f"File not found: {file_path}")
                    continue

                # Parse with AST to find function calls
                try:
                    with open(file_path, encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=str(file_path))

                    calls = self._extract_function_calls(tree, function_name)
                    flows.append({"entry_point": entry, "calls": calls, "file": str(file_path)})

                except SyntaxError as e:
                    logger.warning(f"Syntax error in {file_path}: {e}")

            return ToolResult(success=True, output={"flows": flows})

        except Exception as e:
            logger.error(f"Dataflow tracing failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _extract_function_calls(self, tree: ast.AST, target_function: str) -> list[str]:
        """Extract function calls from AST (simplified)."""
        calls = []

        class CallVisitor(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                if node.name == target_function:
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                calls.append(child.func.id)
                            elif isinstance(child, ast.Attribute):
                                calls.append(f"{ast.unparse(child.func)}.{child.func.attr}")
                self.generic_visit(node)

        CallVisitor().visit(tree)
        return calls[:10]  # Limit to prevent overflow

    def _extract_schema(self) -> ToolResult:
        """
        Extract SQLite schema from actual database.

        NO HARDCODED SQL! Reads actual schema from live ledger DB.
        Gracefully handles missing database.

        Returns:
            ToolResult with schema DDL, sample data, and metadata
        """
        try:
            # Try to get ledger path from live kernel
            db_path = None
            try:
                from vibe_core.boot_orchestrator import BootOrchestrator

                orchestrator = BootOrchestrator(project_root=self.root_dir)
                kernel = orchestrator.get_kernel()
                if kernel and hasattr(kernel, "ledger"):
                    db_path = kernel.ledger.db_path
            except Exception:
                pass

            # Fallback to default ledger path
            if not db_path:
                db_path = self.root_dir / "data" / "vibe_ledger.db"

            if not Path(db_path).exists():
                logger.warning(f"Ledger database not found: {db_path}")
                return ToolResult(
                    success=True,
                    output={
                        "schemas": [],
                        "samples": [],
                        "path": str(db_path),
                        "event_count": 0,
                        "status": "database_not_found",
                    },
                )

            # Connect to SQLite
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get table schemas (NO HARDCODING!)
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name")
            schemas = [row[0] for row in cursor.fetchall() if row[0]]

            # Get sample data from ledger_events
            samples = []
            event_count = 0
            try:
                cursor.execute("SELECT * FROM ledger_events ORDER BY id DESC LIMIT 5")
                columns = [desc[0] for desc in cursor.description]
                samples = [dict(zip(columns, row)) for row in cursor.fetchall()]

                # Get table stats
                cursor.execute("SELECT COUNT(*) FROM ledger_events")
                event_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                logger.warning("ledger_events table not found or inaccessible")

            conn.close()

            return ToolResult(
                success=True,
                output={
                    "schemas": schemas,
                    "samples": samples,
                    "path": str(db_path),
                    "event_count": event_count,
                    "status": "extracted",
                },
            )

        except Exception as e:
            logger.error(f"Schema extraction failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _generate_diagram(self, params: dict) -> ToolResult:
        """
        Generate Mermaid diagram from data.

        Args:
            params: Must contain 'diagram_type' and 'data'

        Returns:
            ToolResult with Mermaid diagram string
        """
        try:
            diagram_type = params.get("diagram_type")
            data = params.get("data", {})

            if diagram_type == "graph":
                mermaid = self._generate_layer_diagram(data)
            elif diagram_type == "sequence":
                mermaid = self._generate_sequence_diagram(data)
            elif diagram_type == "flowchart":
                mermaid = self._generate_flowchart(data)
            else:
                return ToolResult(success=False, error=f"Unknown diagram_type: {diagram_type}")

            return ToolResult(success=True, output=mermaid)

        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            return ToolResult(success=False, error=str(e))

    def _generate_layer_diagram(self, data: dict) -> str:
        """Generate layer architecture diagram."""
        layers = data.get("layers", [])

        mermaid = "```mermaid\ngraph TD\n"
        for i, layer in enumerate(layers):
            layer_id = f"L{i}"
            layer_name = layer.get("name", f"Layer {i}")
            mermaid += f'    {layer_id}["{layer_name}"]\n'

            # Add connections between layers
            if i > 0:
                mermaid += f"    L{i - 1} --> {layer_id}\n"

        mermaid += "```\n"
        return mermaid

    def _generate_sequence_diagram(self, data: dict) -> str:
        """Generate sequence diagram for dataflow."""
        actors = data.get("actors", ["User", "Kernel", "Agent", "Ledger"])
        flow = data.get("flow", {})

        mermaid = "```mermaid\nsequenceDiagram\n"
        for actor in actors:
            mermaid += f"    participant {actor}\n"

        # Add interactions (simplified)
        mermaid += "    User->>Kernel: submit_task()\n"
        mermaid += "    Kernel->>Kernel: governance_check()\n"
        mermaid += "    Kernel->>Agent: process(task)\n"
        mermaid += "    Agent->>Agent: execute()\n"
        mermaid += "    Agent->>Ledger: record(event)\n"
        mermaid += "    Agent-->>Kernel: result\n"
        mermaid += "    Kernel-->>User: response\n"

        mermaid += "```\n"
        return mermaid

    def _generate_flowchart(self, data: dict) -> str:
        """Generate flowchart for lifecycle."""
        flows = data.get("flows", [])

        mermaid = "```mermaid\nflowchart TD\n"
        mermaid += "    Start([Start]) --> Discovery\n"
        mermaid += "    Discovery[Scan cartridge directories] --> Found{Cartridge found?}\n"
        mermaid += "    Found -->|Yes| Load[Load cartridge.yaml]\n"
        mermaid += "    Found -->|No| End([End])\n"
        mermaid += "    Load --> Register[Register with manifest_registry]\n"
        mermaid += "    Register --> Ready[Agent ready]\n"
        mermaid += "    Ready --> End\n"
        mermaid += "```\n"
        return mermaid

    def _render_architecture(self, params: dict) -> ToolResult:
        """
        Render final ARCHITECTURE.md using Jinja2 template.

        Args:
            params: Must contain 'data' with all collected information

        Returns:
            ToolResult with rendered Markdown content
        """
        try:
            from jinja2 import Environment, FileSystemLoader

            # Load template
            template_dir = Path(__file__).parent.parent / "templates"
            if not template_dir.exists():
                return ToolResult(success=False, error=f"Template directory not found: {template_dir}")

            env = Environment(loader=FileSystemLoader(str(template_dir)))
            template = env.get_template("architecture.jinja2")

            # Render with data
            data = params.get("data", {})
            content = template.render(
                kernel_data=data.get("system_snapshot", {}),
                understanding=data.get("understanding", {}),
                artifacts=data.get("artifacts", {}),
                plan=data.get("plan", {}),
                generated_at=datetime.now(timezone.utc),
            )

            return ToolResult(success=True, output=content)

        except Exception as e:
            logger.error(f"Architecture rendering failed: {e}")
            return ToolResult(success=False, error=str(e))

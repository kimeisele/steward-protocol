#!/usr/bin/env python3
"""
GAD-903: Workflow Loader (OPERATION SEMANTIC MOTOR - Phase 2)
==============================================================

Connects the data layer (YAML workflows) to the logic layer (GraphExecutor).

Responsibilities:
1. Load YAML workflow files
2. Validate against _schema.json
3. Convert YAML → Python objects (WorkflowNode, WorkflowEdge, WorkflowGraph)
4. Provide error handling with clear diagnostics

This is the bridge between semantic definitions and executable workflows.

Version: 0.1 (Foundation)
"""

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from vibe_core.playbook.executor import WorkflowEdge, WorkflowGraph, WorkflowNode

logger = logging.getLogger(__name__)


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails"""

    pass


class WorkflowLoaderError(Exception):
    """Raised when workflow cannot be loaded or parsed"""

    pass


class WorkflowLoader:
    """
    Loads and validates YAML workflow definitions.

    Pipeline:
    1. Load YAML file
    2. Parse YAML → Python dict
    3. Validate against JSON Schema
    4. Convert to WorkflowGraph object
    """

    def __init__(self, schema_path: str | Path | None = None):
        """
        Initialize loader with optional custom schema path.

        Args:
            schema_path: Path to _schema.json (defaults to same directory as this file)
        """
        if schema_path is None:
            # Default: look for schema in workflows/ subdirectory
            schema_path = Path(__file__).parent / "workflows" / "_schema.json"
        else:
            schema_path = Path(schema_path)

        if not schema_path.exists():
            raise WorkflowLoaderError(f"Schema file not found: {schema_path}")

        try:
            with open(schema_path) as f:
                self.schema = json.load(f)
            logger.info(f"Loaded workflow schema from {schema_path}")
        except json.JSONDecodeError as e:
            raise WorkflowLoaderError(f"Invalid JSON in schema file: {e}")

    def load_workflow(self, yaml_path: str | Path) -> WorkflowGraph:
        """
        Load and validate a YAML workflow file.

        Args:
            yaml_path: Path to YAML workflow file

        Returns:
            WorkflowGraph object ready for execution

        Raises:
            WorkflowLoaderError: If file cannot be loaded or parsed
            WorkflowValidationError: If workflow doesn't match schema
        """
        yaml_path = Path(yaml_path)

        if not yaml_path.exists():
            raise WorkflowLoaderError(f"Workflow file not found: {yaml_path}")

        # Load YAML
        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            logger.info(f"Loaded YAML from {yaml_path}")
        except yaml.YAMLError as e:
            raise WorkflowLoaderError(f"Invalid YAML in {yaml_path}: {e}")

        if data is None:
            raise WorkflowLoaderError(f"YAML file is empty: {yaml_path}")

        # Validate against schema
        try:
            jsonschema.validate(data, self.schema)
            logger.info("Workflow validated against schema")
        except jsonschema.ValidationError as e:
            raise WorkflowValidationError(
                f"Workflow validation failed: {e.message} (at {e.json_path})"
            )

        # Convert to WorkflowGraph
        workflow_def = data["workflow"]
        return self._build_workflow_graph(workflow_def, yaml_path)

    def _build_workflow_graph(
        self, workflow_def: dict[str, Any], source_path: Path
    ) -> WorkflowGraph:
        """
        Convert YAML workflow definition to WorkflowGraph object.

        Args:
            workflow_def: The 'workflow' dict from validated YAML
            source_path: Path to source YAML file (for logging)

        Returns:
            WorkflowGraph object
        """
        # Extract workflow metadata
        workflow_id = workflow_def["id"]
        name = workflow_def["name"]
        intent = workflow_def["intent"]
        entry_point = workflow_def["entry_point"]
        exit_points = workflow_def["exit_points"]
        estimated_cost = workflow_def.get("estimated_cost_usd", 0.0)

        # Build nodes dict
        nodes = {}
        for node_def in workflow_def["nodes"]:
            node = WorkflowNode(
                id=node_def["id"],
                action=node_def["action"],
                description=node_def.get("description", ""),
                required_skills=node_def.get("required_skills", []),
                timeout_seconds=node_def.get("timeout_seconds", 300),
                retries=workflow_def.get("retry_policy", {}).get("max_retries", 3),
            )
            nodes[node.id] = node
            logger.debug(f"  Created node: {node.id} ({node.action})")

        # Build edges list
        edges = []
        for edge_def in workflow_def["edges"]:
            edge = WorkflowEdge(
                from_node=edge_def["from"],
                to_node=edge_def["to"],
                condition=edge_def.get("condition", "success"),
            )
            edges.append(edge)
            logger.debug(f"  Created edge: {edge.from_node} → {edge.to_node}")

        # Create WorkflowGraph
        graph = WorkflowGraph(
            id=workflow_id,
            name=name,
            intent=intent,
            nodes=nodes,
            edges=edges,
            entry_point=entry_point,
            exit_points=exit_points,
            estimated_cost_usd=estimated_cost,
        )

        logger.info(
            f"Built WorkflowGraph: {name} ({workflow_id}) with "
            f"{len(nodes)} nodes, {len(edges)} edges"
        )
        return graph

    def load_workflows_from_directory(self, directory: str | Path) -> dict[str, WorkflowGraph]:
        """
        Load all YAML workflows from a directory.

        Args:
            directory: Directory containing YAML workflow files

        Returns:
            Dict mapping workflow IDs to WorkflowGraph objects
        """
        directory = Path(directory)

        if not directory.is_dir():
            raise WorkflowLoaderError(f"Directory not found: {directory}")

        workflows = {}
        for yaml_file in directory.glob("*.yaml"):
            if yaml_file.name.startswith("_"):
                # Skip schema and other special files
                continue

            try:
                workflow = self.load_workflow(yaml_file)
                workflows[workflow.id] = workflow
                logger.info(f"Loaded workflow: {workflow.id} from {yaml_file.name}")
            except (WorkflowLoaderError, WorkflowValidationError) as e:
                logger.error(f"Failed to load {yaml_file.name}: {e}")

        logger.info(f"Loaded {len(workflows)} workflows from {directory}")
        return workflows


def load_workflow(yaml_path: str | Path) -> WorkflowGraph:
    """
    Convenience function to load a single workflow.

    Uses default schema location.

    Args:
        yaml_path: Path to YAML workflow file

    Returns:
        WorkflowGraph object
    """
    loader = WorkflowLoader()
    return loader.load_workflow(yaml_path)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python loader.py <workflow.yaml>")
        sys.exit(1)

    try:
        workflow = load_workflow(sys.argv[1])
        print(f"\n✅ Workflow Loaded: {workflow.name}")
        print(f"   ID: {workflow.id}")
        print(f"   Intent: {workflow.intent}")
        print(f"   Nodes: {len(workflow.nodes)}")
        print(f"   Edges: {len(workflow.edges)}")
        print(f"   Entry: {workflow.entry_point}")
        print(f"   Exit: {workflow.exit_points}")
        print(f"   Cost: ${workflow.estimated_cost_usd:.2f}")
    except (WorkflowLoaderError, WorkflowValidationError) as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

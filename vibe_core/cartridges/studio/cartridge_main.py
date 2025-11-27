"""
The Studio Cartridge - ARCH-052: One-Click Dev Environment

Vibe Studio is the killer app for Vibe OS.
Just like macOS + Xcode/Final Cut, Vibe OS + Vibe Studio = complete development platform.

The Studio Cartridge orchestrates the complete SDLC loop:
1. Create isolated workspace
2. Initialize version control
3. Execute Planner → Coder → Tester workflow
4. Manage repairs and deployments

CONCEPT:
Users say: "Build me a landing page with React and Tailwind"
Studio does: Creates workspace, runs SDLC, delivers working code + tests

Capabilities:
1. create_project() → Set up isolated workspace
2. execute_sdlc() → Run complete Planner → Coder → Tester loop
3. manage_repairs() → Handle test failures and fixes
4. deploy() → Move to production
5. report_status() → Project status and artifacts

This is Vibe's Killer App.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Any

from vibe_core.cartridges.base import CartridgeBase
from vibe_core.kernel import VibeKernel
from vibe_core.scheduling import Task

logger = logging.getLogger(__name__)


class StudioCartridge(CartridgeBase):
    """
    Vibe Studio - The One-Click Development Environment.

    This cartridge encapsulates the complete SDLC workflow:
    - Workspace management (isolated development environments)
    - Git initialization and version control
    - Automated orchestration of Planner → Coder → Tester loop
    - Repair loop for test failures
    - Deployment automation

    Studio is to Vibe OS what Xcode is to macOS.
    """

    name = "studio"
    version = "1.0.0"
    description = "One-click dev environment with complete SDLC automation"
    author = "Vibe Agency"

    def __init__(self, vibe_root: Path | None = None, kernel: VibeKernel | None = None):
        """Initialize the Studio cartridge.

        Args:
            vibe_root: Root path for Vibe OS
            kernel: VibeKernel instance for task delegation (optional for testing)
        """
        super().__init__(vibe_root=vibe_root)

        self.kernel = kernel
        self.projects_dir = self.vibe_root / "workspace" / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🎬 Vibe Studio initialized - One-Click Dev Environment ready")

    def create_project(self, project_name: str, description: str = "") -> dict[str, Any]:
        """
        Create an isolated development workspace.

        Args:
            project_name: Name of the project (e.g., "landing-page")
            description: Optional project description

        Returns:
            Status dict with project metadata
        """
        try:
            # Validate project name
            if not project_name or not project_name.replace("-", "").replace("_", "").isalnum():
                return {
                    "status": "error",
                    "message": "Project name must be alphanumeric (hyphens and underscores allowed)",
                    "project_name": project_name,
                }

            # Create project directory
            project_dir = self.projects_dir / project_name
            if project_dir.exists():
                return {
                    "status": "error",
                    "message": f"Project '{project_name}' already exists",
                    "project_dir": str(project_dir),
                }

            project_dir.mkdir(parents=True, exist_ok=True)

            # Initialize git
            try:
                subprocess.run(
                    ["git", "init"],
                    cwd=project_dir,
                    capture_output=True,
                    check=True,
                    timeout=5,
                )
                logger.info(f"✅ Git initialized for project: {project_name}")
            except Exception as e:
                logger.warning(f"⚠️  Git init failed (continuing anyway): {e}")

            # Create project metadata
            project_metadata = {
                "name": project_name,
                "description": description,
                "created_at": str(Path().cwd()),  # timestamp
                "status": "initialized",
                "path": str(project_dir),
            }

            # Save project metadata
            metadata_path = project_dir / ".studio.json"
            with open(metadata_path, "w") as f:
                json.dump(project_metadata, f, indent=2)

            logger.info(f"✅ Project created: {project_name}")

            return {
                "status": "success",
                "message": f"Project '{project_name}' created successfully",
                "project_name": project_name,
                "project_dir": str(project_dir),
                "metadata": project_metadata,
            }

        except Exception as e:
            logger.error(f"❌ Failed to create project: {e}")
            return {"status": "error", "message": str(e), "project_name": project_name}

    def execute_sdlc(
        self, project_name: str, goal: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute the complete SDLC loop: Planning → Coding → Testing.

        This is the core feature of Vibe Studio - orchestrate all three specialist agents
        to deliver working code from a goal statement.

        Args:
            project_name: Name of the project
            goal: Development goal (e.g., "Build a React landing page with dark mode")
            context: Optional additional context for specialists

        Returns:
            Status dict with completion report and artifacts
        """
        try:
            # Verify project exists
            project_dir = self.projects_dir / project_name
            if not project_dir.exists():
                return {
                    "status": "error",
                    "message": f"Project '{project_name}' not found. Use create_project first.",
                    "project_name": project_name,
                }

            # Require kernel for delegation
            if not self.kernel:
                return {
                    "status": "error",
                    "message": "Studio requires VibeKernel for SDLC orchestration. No kernel provided.",
                    "project_name": project_name,
                }

            logger.info(f"🚀 Starting SDLC for project: {project_name}")
            logger.info(f"   Goal: {goal}")

            # Initialize context
            if context is None:
                context = {}

            context.update(
                {
                    "project_name": project_name,
                    "project_dir": str(project_dir),
                    "goal": goal,
                }
            )

            # Phase 1: PLANNING
            logger.info("📋 PHASE 1: Planning...")
            plan_result = self._delegate_to_specialist(
                agent_id="specialist-planning",
                phase="PLANNING",
                context=context,
            )

            if not plan_result.get("success"):
                return {
                    "status": "error",
                    "message": "Planning phase failed",
                    "project_name": project_name,
                    "error": plan_result.get("error"),
                }

            plan = plan_result.get("output", {}).get("plan", "")
            logger.info("✅ Planning complete")

            # Phase 2: CODING
            logger.info("💻 PHASE 2: Coding...")
            context["plan"] = plan

            code_result = self._delegate_to_specialist(
                agent_id="specialist-coding",
                phase="CODING",
                context=context,
            )

            if not code_result.get("success"):
                return {
                    "status": "error",
                    "message": "Coding phase failed",
                    "project_name": project_name,
                    "error": code_result.get("error"),
                }

            code_files = code_result.get("output", {}).get("files", {})
            logger.info(f"✅ Coding complete - {len(code_files)} files generated")

            # Phase 3: TESTING
            logger.info("🧪 PHASE 3: Testing...")
            context["code_files"] = code_files

            test_result = self._delegate_to_specialist(
                agent_id="specialist-testing",
                phase="TESTING",
                context=context,
            )

            if not test_result.get("success"):
                # Activate repair loop
                logger.warning("⚠️  Tests failed. Activating repair loop...")
                repair_result = self._repair_loop(
                    project_name=project_name,
                    context=context,
                    test_failure=test_result,
                )

                return repair_result

            logger.info("✅ Testing complete - All tests passing")

            # Compilation: Save artifacts
            artifacts = {
                "plan": plan,
                "code_files": code_files,
                "test_results": test_result.get("output", {}),
            }

            artifacts_path = project_dir / "artifacts.json"
            with open(artifacts_path, "w") as f:
                json.dump(artifacts, f, indent=2)

            logger.info("📦 SDLC complete - Artifacts saved")

            return {
                "status": "success",
                "message": "SDLC workflow completed successfully",
                "project_name": project_name,
                "phase": "COMPLETE",
                "artifacts": artifacts,
            }

        except Exception as e:
            logger.error(f"❌ SDLC execution failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "project_name": project_name,
            }

    def _delegate_to_specialist(
        self, agent_id: str, phase: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Internal method: Delegate work to a specialist via the kernel.

        Args:
            agent_id: ID of the specialist agent (e.g., "specialist-planning")
            phase: Phase name (PLANNING, CODING, TESTING)
            context: Context to pass to the specialist

        Returns:
            Result dict from specialist execution
        """
        try:
            if not self.kernel:
                return {"success": False, "error": "No kernel available"}

            # Create delegation task
            task = Task(
                agent_id=agent_id,
                payload={
                    "phase": phase,
                    "context": context,
                },
            )

            # Submit to kernel
            task_id = self.kernel.submit(task)

            # Wait for completion (simplified - real impl would use async)
            max_ticks = 1000
            ticks = 0
            while (
                self.kernel.scheduler.get_queue_status()["pending_tasks"] > 0 and ticks < max_ticks
            ):
                self.kernel.tick()
                ticks += 1

            # Query result from ledger
            try:
                result_row = self.kernel.ledger.get_task_result(task_id)
                if result_row:
                    return json.loads(result_row)
                else:
                    return {"success": False, "error": f"No result for task {task_id}"}
            except Exception as e:
                logger.warning(f"Could not retrieve result from ledger: {e}")
                return {"success": False, "error": str(e)}

        except Exception as e:
            logger.error(f"Delegation failed: {e}")
            return {"success": False, "error": str(e)}

    def _repair_loop(
        self, project_name: str, context: dict[str, Any], test_failure: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Internal method: Activate repair loop when tests fail.

        The repair loop:
        1. Extracts failure details from test_failure
        2. Re-delegates to specialist-coding with failure report
        3. Coding specialist enters REPAIR MODE and generates fixes
        4. Re-tests until passing or max attempts exceeded

        Args:
            project_name: Project name
            context: Current SDLC context
            test_failure: Failed test result with error details

        Returns:
            Final repair result
        """
        try:
            logger.info("🔧 REPAIR LOOP ACTIVATED")

            repair_attempts = 0
            max_repairs = 3

            while repair_attempts < max_repairs:
                repair_attempts += 1
                logger.info(f"   Repair Attempt {repair_attempts}/{max_repairs}")

                # Re-delegate to coder with failure report
                context["repair_mode"] = True
                context["repair_attempt"] = repair_attempts
                context["failure_report"] = test_failure.get("output", {}).get("error_details", "")

                repair_result = self._delegate_to_specialist(
                    agent_id="specialist-coding",
                    phase="REPAIR",
                    context=context,
                )

                if not repair_result.get("success"):
                    logger.error(f"   Repair attempt {repair_attempts} failed")
                    continue

                # Re-test
                logger.info("   Re-testing after repair...")
                test_result = self._delegate_to_specialist(
                    agent_id="specialist-testing",
                    phase="TESTING",
                    context=context,
                )

                if test_result.get("success"):
                    logger.info(f"✅ Repair successful on attempt {repair_attempts}")
                    return {
                        "status": "success",
                        "message": f"SDLC repaired successfully (attempt {repair_attempts})",
                        "project_name": project_name,
                        "phase": "COMPLETE (REPAIRED)",
                        "repair_attempts": repair_attempts,
                    }

            # Max repairs exceeded
            logger.error(f"❌ Max repair attempts ({max_repairs}) exceeded")
            return {
                "status": "error",
                "message": f"Failed to fix issues after {max_repairs} repair attempts",
                "project_name": project_name,
                "repair_attempts": max_repairs,
            }

        except Exception as e:
            logger.error(f"Repair loop failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "project_name": project_name,
            }

    def report_status(self) -> dict[str, Any]:
        """Report Studio status and list projects."""
        status = super().report_status()

        try:
            # List projects
            projects = []
            if self.projects_dir.exists():
                for project_path in self.projects_dir.iterdir():
                    if project_path.is_dir():
                        metadata_path = project_path / ".studio.json"
                        if metadata_path.exists():
                            with open(metadata_path) as f:
                                projects.append(json.load(f))

            status.update(
                {
                    "projects_dir": str(self.projects_dir),
                    "projects": projects,
                    "project_count": len(projects),
                }
            )
        except Exception as e:
            logger.warning(f"Could not list projects: {e}")

        return status


__all__ = ["StudioCartridge"]

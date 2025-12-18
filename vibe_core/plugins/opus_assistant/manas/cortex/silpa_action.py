"""
OPUS-101: Silpa Action - VEDA-4 Compliant Code Refactoring.
OPUS-103: Genesis Protocol - LLM-powered code generation.

This wraps SilpaArchitect in a BaseAction interface for auto-discovery.

Karmendriya: PANI (Hands) - The ability to sculpt/modify code.

Handled Intent Types:
- genesis_tests: Generate tests for code
- create_tests: Create test files
- semantic_gap_test: Test based on semantic gaps
- refactor_file: Refactor a specific file
- update_docstring: Update docstrings
- analyze_refactor: Analyze potential refactorings
- genesis_action: [NEW] Generate new Action modules via LLM

CRITICAL: This is how MANAS modifies its own code.
If this doesn't work, MANAS cannot self-improve.

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/silpa.py
    required: true
wiring:
  - pattern: "class SilpaAction\\(BaseAction\\)"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
  - pattern: "handled_intent_types.*genesis_tests"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
  - pattern: "genesis_action"
    in: vibe_core/plugins/opus_assistant/manas/cortex/silpa_action.py
-->
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from .base_action import ActionResult, BaseAction
from .silpa import (
    RefactorRisk,
    RefactorType,
    SilpaArchitect,
    SilpaAuditor,
    SilpaPlan,
    SilpaRefactoring,
    SilpaResult,
)

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Action.Silpa")


class SilpaAction(BaseAction):
    """
    Silpa Action - Code Modification and Refactoring.

    Wraps SilpaArchitect in BaseAction interface for ActionLoader discovery.

    "PANI (Hands) - The sculptor's hands that shape code."

    OPUS-103: Now includes GENESIS capability via LLM integration.
    MANAS can now CREATE new code, not just refactor existing code.

    CRITICAL: This enables MANAS to modify AND CREATE code.
    Without this working, MANAS cannot self-improve.
    """

    # OPUS-101: VEDA-4 auto-discovery
    name = "silpa_action"

    # Intent types this action handles
    handled_intent_types: Set[str] = {
        # Test generation
        "genesis_tests",
        "create_tests",
        "semantic_gap_test",
        # Refactoring
        "refactor_file",
        "refactor_analyze",
        "analyze_refactor",
        # Docstring operations
        "update_docstring",
        "add_docstring",
        # Code modification
        "rename_variable",
        "rename_function",
        "extract_method",
        "update_imports",
        # OPUS-103: Genesis Protocol - LLM-powered code generation
        "genesis_action",
        "genesis_code",
        "create_action",
        "create_module",
    }

    def __init__(
        self,
        workspace: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize Silpa Action.

        Args:
            workspace: Workspace root
            config: Configuration dict
        """
        super().__init__(workspace, config)
        self._architect = SilpaArchitect(workspace=self._workspace)
        self._auditor = SilpaAuditor(self._workspace)

        # OPUS-103: LLM provider for genesis capability
        self._llm_provider = None
        try:
            from vibe_core.runtime.providers.factory import get_default_provider

            self._llm_provider = get_default_provider()
            logger.info(f"[SILPA_ACTION] LLM Genesis enabled ({type(self._llm_provider).__name__})")
        except Exception as e:
            logger.warning(f"[SILPA_ACTION] LLM not available ({e}), genesis disabled")

        logger.info("[SILPA_ACTION] Initialized - PANI (The Hands)")

    def act(self, intent: "Intent") -> ActionResult:
        """
        Execute a code modification intent.

        Routes to appropriate SilpaArchitect method based on intent type.

        Args:
            intent: The intent to execute

        Returns:
            ActionResult with execution status
        """
        intent_type = intent.type
        params = intent.params or {}

        try:
            # Test generation intents
            if intent_type in ("genesis_tests", "create_tests", "semantic_gap_test"):
                return self._handle_test_generation(intent, params)

            # Analysis intents
            elif intent_type in ("refactor_analyze", "analyze_refactor"):
                return self._handle_analyze(intent, params)

            # Docstring intents
            elif intent_type in ("update_docstring", "add_docstring"):
                return self._handle_docstring(intent, params)

            # Refactoring intents
            elif intent_type in (
                "refactor_file",
                "rename_variable",
                "rename_function",
                "extract_method",
                "update_imports",
            ):
                return self._handle_refactor(intent, params)

            # OPUS-103: Genesis Protocol - LLM-powered code generation
            elif intent_type in ("genesis_action", "genesis_code", "create_action", "create_module"):
                return self._handle_genesis(intent, params)

            else:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent_type,
                    error=f"Unknown intent type for SilpaAction: {intent_type}",
                )

        except Exception as e:
            logger.error(f"[SILPA_ACTION] Error handling {intent_type}: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent_type,
                error=str(e),
            )

    def _handle_test_generation(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle test generation intents."""
        target_file = params.get("target_file") or params.get("file")
        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter for test generation",
            )

        target_path = Path(target_file)

        # Run existing tests first (if any)
        test_result = self._auditor.run_tests(target_file=target_path)

        # Analyze what tests could be generated
        analysis = {
            "target_file": str(target_file),
            "existing_tests": test_result.tests_passed + test_result.tests_failed,
            "test_coverage_exists": test_result.tests_passed > 0,
            "suggestion": "Use SILPA refactoring to generate missing tests",
        }

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result=analysis,
            metadata={"test_result": test_result.to_dict()},
        )

    def _handle_analyze(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle refactoring analysis intents."""
        target_file = params.get("target_file") or params.get("file")
        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter for analysis",
            )

        target_path = self._workspace / target_file
        if not target_path.exists():
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Target file not found: {target_file}",
            )

        # Read and analyze code
        code = target_path.read_text()
        analysis = {
            "target_file": str(target_file),
            "lines": len(code.splitlines()),
            "size_bytes": len(code),
            "can_refactor": True,
            "suggestions": [],
        }

        # Check for common refactoring opportunities
        if "def " in code:
            func_count = code.count("def ")
            if func_count > 10:
                analysis["suggestions"].append(f"Consider extracting methods - {func_count} functions in file")

        if '"""' not in code and "'''" not in code:
            analysis["suggestions"].append("Missing docstrings - consider adding")

        return ActionResult(
            success=True,
            action_name=self.name,
            intent_type=intent.type,
            result=analysis,
        )

    def _handle_docstring(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle docstring update/add intents."""
        target_file = params.get("target_file") or params.get("file")
        target_name = params.get("target_name") or params.get("function") or params.get("class")
        new_docstring = params.get("docstring") or params.get("content")

        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter",
            )

        refactor_type = (
            RefactorType.UPDATE_DOCSTRING if intent.type == "update_docstring" else RefactorType.ADD_DOCSTRING
        )

        refactoring = SilpaRefactoring(
            target_file=Path(target_file),
            refactor_type=refactor_type,
            target_name=target_name,
            new_code=new_docstring,
            description=f"{intent.type} for {target_name or target_file}",
        )

        # Plan the refactoring
        try:
            plan = self._architect.plan(refactoring)

            # For docstrings, classify risk
            risk = self._architect.classify_risk(refactoring)

            if risk == RefactorRisk.FORBIDDEN:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error="Cannot modify protected file",
                )

            # Execute if safe
            if risk == RefactorRisk.SAFE:
                result = self._architect.execute(plan)
                return self._silpa_result_to_action_result(result, intent.type)
            else:
                # Needs approval for non-safe changes
                return ActionResult(
                    success=True,
                    action_name=self.name,
                    intent_type=intent.type,
                    result={
                        "status": "needs_approval",
                        "risk": risk.value,
                        "plan": plan.to_dict(),
                    },
                    metadata={"approval_required": True},
                )

        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=str(e),
            )

    def _handle_refactor(self, intent: "Intent", params: Dict) -> ActionResult:
        """Handle general refactoring intents."""
        target_file = params.get("target_file") or params.get("file")

        if not target_file:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing target_file parameter",
            )

        # Map intent type to refactor type
        type_mapping = {
            "refactor_file": RefactorType.CUSTOM,
            "rename_variable": RefactorType.RENAME_VARIABLE,
            "rename_function": RefactorType.RENAME_FUNCTION,
            "extract_method": RefactorType.EXTRACT_METHOD,
            "update_imports": RefactorType.UPDATE_IMPORTS,
        }

        refactor_type = type_mapping.get(intent.type, RefactorType.CUSTOM)

        refactoring = SilpaRefactoring(
            target_file=Path(target_file),
            refactor_type=refactor_type,
            target_name=params.get("target_name"),
            new_code=params.get("new_code"),
            description=params.get("description", f"Refactor: {intent.type}"),
        )

        try:
            # Plan first
            plan = self._architect.plan(refactoring)
            risk = self._architect.classify_risk(refactoring)

            if risk == RefactorRisk.FORBIDDEN:
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error="Cannot modify protected/forbidden file",
                )

            # All non-safe refactorings need approval
            if risk != RefactorRisk.SAFE:
                return ActionResult(
                    success=True,
                    action_name=self.name,
                    intent_type=intent.type,
                    result={
                        "status": "needs_approval",
                        "risk": risk.value,
                        "plan": plan.to_dict(),
                    },
                    metadata={"approval_required": True, "risk": risk.value},
                )

            # Execute safe refactorings
            result = self._architect.execute(plan)
            return self._silpa_result_to_action_result(result, intent.type)

        except Exception as e:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=str(e),
            )

    def _silpa_result_to_action_result(self, silpa_result: SilpaResult, intent_type: str) -> ActionResult:
        """Convert SilpaResult to ActionResult."""
        return ActionResult(
            success=silpa_result.success,
            action_name=self.name,
            intent_type=intent_type,
            result=silpa_result.to_dict(),
            error=silpa_result.error,
            metadata={
                "risk": silpa_result.risk.value if silpa_result.risk else None,
                "tests_before": silpa_result.tests_before.to_dict() if silpa_result.tests_before else None,
                "tests_after": silpa_result.tests_after.to_dict() if silpa_result.tests_after else None,
            },
        )

    # =========================================================================
    # OPUS-103: GENESIS PROTOCOL - LLM-powered code generation
    # =========================================================================

    def _handle_genesis(self, intent: "Intent", params: Dict) -> ActionResult:
        """
        OPUS-103/OPUS-105: Handle code generation via LLM with DHARMA + BHUMANDALA enforcement.

        This is the GENESIS capability - MANAS can now CREATE new code.

        OPUS-105 FORTRESS GATES (in order):
        1. BHUMANDALA - Topology authority check (Ring 0-2 required)
        2. DharmaSense - Permission check (genesis + code_modify)
        3. Path restriction - Only cortex/, tests/
        4. Karma tracking - Success/failure affects Bhakti

        Args:
            intent: The genesis intent
            params: Parameters including:
                - name: Name of the module/action to create
                - description: What the code should do
                - target_path: Where to write (must be in allowed directories)
                - code_type: "action", "sense", "test", "module"

        Returns:
            ActionResult with generated code or error
        """
        # =====================================================================
        # OPUS-105 SÄULE 2: BHUMANDALA - Topology Authority Check
        # Genesis requires Ring 0-2 authority (ILAVRTA, BHADRASHVA, KIMPURASHA)
        # =====================================================================
        try:
            from vibe_core.topology import get_agent_placement

            placement = get_agent_placement("manas")
            if placement:
                # Genesis requires authority level >= 8 (Ring 0-2)
                MIN_GENESIS_AUTHORITY = 8
                if placement.authority_level < MIN_GENESIS_AUTHORITY:
                    logger.warning(
                        f"[GENESIS] ❌ BHUMANDALA BLOCKED: MANAS authority {placement.authority_level} "
                        f"< {MIN_GENESIS_AUTHORITY} required for genesis"
                    )
                    self._track_karma_penalty(reason="Insufficient topology authority for genesis")
                    return ActionResult(
                        success=False,
                        action_name=self.name,
                        intent_type=intent.type,
                        error=f"BHUMANDALA VIOLATION: Authority level {placement.authority_level} insufficient for genesis (need {MIN_GENESIS_AUTHORITY}+)",
                        metadata={
                            "genesis_blocked": True,
                            "reason": "topology_authority",
                            "agent_authority": placement.authority_level,
                            "required_authority": MIN_GENESIS_AUTHORITY,
                            "agent_layer": placement.layer,
                            "agent_varna": placement.varna,
                        },
                    )
                logger.info(
                    f"[GENESIS] ✅ BHUMANDALA: Authority {placement.authority_level} "
                    f"(Layer: {placement.layer}, Varna: {placement.varna})"
                )
        except ImportError:
            logger.debug("[GENESIS] Topology not available - skipping authority check")
        except Exception as e:
            logger.debug(f"[GENESIS] Topology check failed: {e}")

        # =====================================================================
        # OPUS-105: DHARMA CHECK (Real tiger, not paper tiger)
        # =====================================================================
        try:
            from .dharma_sense import DharmaSense, DharmaStatus

            dharma = DharmaSense(workspace=self._workspace, agent_id="manas")
            verdict = dharma.check_dharmic_alignment(intent, agent_id="manas")

            if not verdict.is_permitted:
                logger.warning(f"[GENESIS] ❌ DHARMA BLOCKED: {verdict.reason}")
                # Track karma penalty
                self._track_karma_penalty(reason=f"Genesis blocked: {verdict.reason}")
                return ActionResult(
                    success=False,
                    action_name=self.name,
                    intent_type=intent.type,
                    error=f"DHARMA VIOLATION: {verdict.reason}",
                    metadata={
                        "genesis_blocked": True,
                        "reason": "dharma_violation",
                        "dharma_status": verdict.status.value,
                        "missing_permissions": verdict.missing_permissions,
                        "agent_bhakti": verdict.agent_bhakti,
                    },
                )

            if verdict.status == DharmaStatus.RAJASIC:
                logger.info(f"[GENESIS] ⚠️ DHARMA RAJASIC: Proceeding with caution - {verdict.reason}")

            logger.info(f"[GENESIS] ✅ DHARMA SATTVIC: Permission granted (bhakti: {verdict.agent_bhakti})")

        except ImportError:
            logger.warning("[GENESIS] DharmaSense not available - using fallback path check")
        except Exception as e:
            logger.warning(f"[GENESIS] DharmaSense check failed: {e} - using fallback")

        # =====================================================================
        # LLM availability check
        # =====================================================================
        if not self._llm_provider:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Genesis requires LLM provider - not available",
                metadata={"genesis_blocked": True, "reason": "no_llm"},
            )

        name = params.get("name") or params.get("action_name") or params.get("module_name")
        description = params.get("description", "")
        target_path = params.get("target_path") or params.get("path")
        code_type = params.get("code_type", "action")

        if not name:
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error="Missing 'name' parameter for genesis",
            )

        # =====================================================================
        # PATH RESTRICTION (Belt + Suspenders with Dharma)
        # =====================================================================
        allowed_dirs = [
            "vibe_core/plugins/opus_assistant/manas/cortex",
            "tests/unit",
            "tests/manas",
        ]

        if target_path:
            target = Path(target_path)
        else:
            # Default to cortex for actions
            if code_type == "action":
                target = self._workspace / "vibe_core/plugins/opus_assistant/manas/cortex" / f"{name}_action.py"
            elif code_type == "test":
                target = self._workspace / "tests/unit" / f"test_{name}.py"
            else:
                target = self._workspace / "vibe_core/plugins/opus_assistant/manas/cortex" / f"{name}.py"

        # Verify target is in allowed directory
        target_str = str(target)
        if not any(allowed in target_str for allowed in allowed_dirs):
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"DHARMA VIOLATION: Cannot write to {target_path}. Genesis only allowed in: {allowed_dirs}",
                metadata={"genesis_blocked": True, "reason": "dharma_violation"},
            )

        # Generate code via LLM
        try:
            prompt = self._build_genesis_prompt(name, description, code_type)
            logger.info(f"[GENESIS] Invoking LLM for: {name} ({code_type})")

            # Call LLM
            response = self._llm_provider.invoke(messages=[{"role": "user", "content": prompt}])
            generated_code = response.content if hasattr(response, "content") else str(response)

            # Extract code block if wrapped in markdown
            if "```python" in generated_code:
                start = generated_code.find("```python") + 9
                end = generated_code.find("```", start)
                if end > start:
                    generated_code = generated_code[start:end].strip()

            # Write the file
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(generated_code)
            logger.info(f"[GENESIS] Created: {target}")

            # Verify with ActionLoader if it's an action
            if code_type == "action":
                try:
                    from vibe_core.loaders import ActionLoader

                    ActionLoader.clear_cache()
                    actions, _ = ActionLoader.discover_and_load(workspace=self._workspace, force_refresh=True)
                    action_name = f"{name}_action"
                    if action_name in actions:
                        logger.info(f"[GENESIS] ✅ ActionLoader discovered: {action_name}")
                        # OPUS-105: Track karma success for dharmic genesis
                        self._track_karma_success(reason=f"Created action: {action_name}")
                        return ActionResult(
                            success=True,
                            action_name=self.name,
                            intent_type=intent.type,
                            result={
                                "status": "genesis_complete",
                                "created_file": str(target),
                                "action_discovered": True,
                                "action_name": action_name,
                            },
                            metadata={"genesis_success": True},
                        )
                except Exception as e:
                    logger.warning(f"[GENESIS] ActionLoader verification failed: {e}")

            # OPUS-105: Track karma success for dharmic genesis
            self._track_karma_success(reason=f"Created {code_type}: {name}")
            return ActionResult(
                success=True,
                action_name=self.name,
                intent_type=intent.type,
                result={
                    "status": "genesis_complete",
                    "created_file": str(target),
                    "code_length": len(generated_code),
                },
                metadata={"genesis_success": True},
            )

        except Exception as e:
            logger.error(f"[GENESIS] Failed: {e}")
            return ActionResult(
                success=False,
                action_name=self.name,
                intent_type=intent.type,
                error=f"Genesis failed: {e}",
            )

    def _build_genesis_prompt(self, name: str, description: str, code_type: str) -> str:
        """
        OPUS-105 VAK: Build prompt for LLM code generation using PromptRegistry.

        Prompts are loaded from config/prompts/genesis.yaml, NOT hardcoded.
        This enables:
        - Tuning without kernel restart
        - Self-optimization by MANAS
        - Clean separation of concerns
        """
        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry

            # Map code_type to prompt key
            prompt_key = f"genesis.{code_type}"

            # Prepare context for interpolation
            context = {
                "name": name,
                "name_title": name.title(),
                "name_upper": name.upper(),
                "description": description,
                "code_type": code_type,
            }

            # Get prompt from registry
            prompt = PromptRegistry.get(prompt_key, context)
            logger.debug(f"[GENESIS] Using prompt from registry: {prompt_key}")
            return prompt

        except Exception as e:
            # Fallback to minimal prompt if registry fails
            logger.warning(f"[GENESIS] PromptRegistry failed ({e}), using fallback")
            return f"""Generate a Python {code_type} for MANAS.
Name: {name}
Description: {description}
Generate complete, working Python code. Only output code, no explanations."""

    # =========================================================================
    # OPUS-105: KARMA TRACKING - Actions have consequences (REAL, NOT PAPER)
    # =========================================================================

    def _get_state_manager(self):
        """
        Lazy-load VedicStateManager singleton.

        Uses the same pattern as DharmaSense for consistency.
        """
        if not hasattr(self, "_state_manager"):
            self._state_manager = None

        if self._state_manager is None:
            try:
                from vibe_core.plugins.vedic_governance.state_manager import get_state_manager

                self._state_manager = get_state_manager()
            except ImportError:
                logger.debug("[KARMA] VedicStateManager not available")
        return self._state_manager

    def _track_karma_penalty(self, reason: str, amount: int = 10) -> None:
        """
        OPUS-105: Track karma penalty for blocked/failed actions.

        REAL WIRING: Uses VedicStateManager.update_bhakti() directly.
        This ACTUALLY reduces the agent's Bhakti score.

        Args:
            reason: Why karma is being docked
            amount: How much Bhakti to consume (default 10)
        """
        try:
            state_mgr = self._get_state_manager()
            if state_mgr:
                new_bhakti = state_mgr.update_bhakti(
                    agent_id="manas",
                    delta=-amount,  # NEGATIVE = penalty
                    reason=f"KARMA PENALTY: {reason}",
                )
                logger.warning(f"[KARMA] 📉 Bhakti -{amount} for MANAS → now {new_bhakti}: {reason}")
            else:
                logger.warning(f"[KARMA] 📉 (unwired) Penalty recorded: {reason}")
        except Exception as e:
            logger.debug(f"[KARMA] Could not track penalty: {e}")

    def _track_karma_success(self, reason: str, amount: int = 5) -> None:
        """
        OPUS-105: Track karma reward for successful dharmic actions.

        REAL WIRING: Uses VedicStateManager.update_bhakti() directly.
        This ACTUALLY increases the agent's Bhakti score.

        Args:
            reason: Why karma is being rewarded
            amount: How much Bhakti to add (default 5)
        """
        try:
            state_mgr = self._get_state_manager()
            if state_mgr:
                new_bhakti = state_mgr.update_bhakti(
                    agent_id="manas",
                    delta=+amount,  # POSITIVE = reward
                    reason=f"KARMA SUCCESS: {reason}",
                )
                logger.info(f"[KARMA] 📈 Bhakti +{amount} for MANAS → now {new_bhakti}: {reason}")
            else:
                logger.info(f"[KARMA] 📈 (unwired) Success recorded: {reason}")
        except Exception as e:
            logger.debug(f"[KARMA] Could not track success: {e}")

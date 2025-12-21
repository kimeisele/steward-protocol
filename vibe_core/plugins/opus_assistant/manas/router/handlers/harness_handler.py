"""
Harness Handler - Documentation harness and coverage gap processing.

OPUS-171 Phase 5: Extracted from IntentRouter.

OPUS-054, OPUS-128, OPUS-129, OPUS-132: Harness operations.

Handles:
- roadmap_add_harness, harness_auto_generate, harness_broken, harness_missing
- roadmap_fix_code_reference, sutra_missing_code, sutra_missing_harness
- harness_tdd_contract, harness_stale_reference, harness_optional_missing
- coverage_gap_critical, coverage_gap_module, coverage_gap_overall
- triage_p1_critical, triage_p2_high, triage_summary
- create_opus_doc, consolidate_docs, rename_doc
"""

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Harness")


@register_handler
class HarnessHandler(BaseHandler):
    """
    Handle harness generation and fix intents.

    OPUS-054: SUTRA harness operations.
    """

    name = "harness"
    intent_types = [
        "roadmap_add_harness",
        "roadmap_fix_code_reference",
        "sutra_missing_code",
        "sutra_missing_harness",
        "harness_auto_generate",
        "harness_broken",
        "harness_missing",
    ]
    agent_type = AgentType.DOCUMENTATION
    priority = 12

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to appropriate harness operation."""
        if "fix" in intent.intent_type or "missing_code" in intent.intent_type:
            return self._handle_roadmap_fix(intent)
        else:
            return self._handle_roadmap_harness(intent)

    def _handle_roadmap_harness(self, intent: "Intent") -> Dict[str, Any]:
        """OPUS-054 SUTRA: Handle roadmap add_harness intents."""
        logger.info(f"📜 SUTRA handling harness generation: {intent.title}")

        try:
            target = intent.params.get("target") or intent.params.get("doc_path") or intent.params.get("opus_file", "")
            if not target:
                return {"success": False, "handler": self.name, "error": "No target file specified"}

            doc_name = Path(target).stem
            parts = doc_name.split("-")
            module_name = parts[1].lower() if len(parts) > 1 else doc_name.lower()

            from vibe_core.plugins.opus_assistant.manas.circuit_executor import CognitiveCircuitExecutor

            executor = CognitiveCircuitExecutor(workspace=self._workspace)
            result = executor._script_generate_harness(
                {
                    "opus_file": target,
                    "module_name": module_name,
                }
            )

            if result.get("success"):
                logger.info(f"✅ Harness generated for {doc_name}")
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "harness_generated",
                    "target": target,
                    "message": f"@HARNESS added to {doc_name}",
                }
            else:
                return {
                    "success": False,
                    "handler": self.name,
                    "action": "harness_failed",
                    "error": result.get("error", "Unknown error"),
                }

        except Exception as e:
            logger.error(f"❌ Harness generation failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _handle_roadmap_fix(self, intent: "Intent") -> Dict[str, Any]:
        """OPUS-054 SUTRA: Handle roadmap fix intents."""
        logger.info(f"🔧 SUTRA handling fix: {intent.title}")

        try:
            doc_path = intent.params.get("doc_path", "")
            code_path = intent.params.get("code_path", "")
            gap_type = intent.params.get("gap_type", "")
            description = intent.params.get("description", intent.description)

            if not doc_path:
                return {"success": False, "handler": self.name, "error": "No doc_path specified"}

            doc_file = Path(doc_path)
            if not doc_file.exists():
                return {"success": False, "handler": self.name, "error": f"Doc not found: {doc_path}"}

            content = doc_file.read_text()

            if gap_type == "missing_code" and code_path:
                lines = content.split("\n")
                new_lines = []
                removed = False

                for line in lines:
                    if code_path in line and ("path:" in line or "in:" in line):
                        logger.info(f"🗑️ Removing broken reference: {code_path}")
                        removed = True
                        continue
                    new_lines.append(line)

                if removed:
                    doc_file.write_text("\n".join(new_lines))
                    return {
                        "success": True,
                        "handler": self.name,
                        "action": "reference_removed",
                        "target": str(doc_path),
                        "removed_path": code_path,
                        "message": f"Removed broken reference to {code_path} from {doc_file.name}",
                    }
                else:
                    return {
                        "success": True,
                        "handler": self.name,
                        "action": "no_change_needed",
                        "message": f"Reference {code_path} not found in {doc_file.name}",
                    }

            logger.warning(f"⚠️ Gap type '{gap_type}' requires manual review: {description}")
            return {
                "success": True,
                "handler": self.name,
                "action": "manual_review_needed",
                "target": str(doc_path),
                "gap_type": gap_type,
                "message": f"Gap type '{gap_type}' flagged for review: {description[:100]}",
            }

        except Exception as e:
            logger.error(f"❌ Fix handling failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class TddContractHandler(BaseHandler):
    """Handle TDD contract intents (OPUS-128)."""

    name = "tdd_contract"
    intent_types = ["harness_tdd_contract"]
    agent_type = AgentType.DOCUMENTATION
    priority = 8

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Handle TDD contract intents."""
        logger.info(f"📋 TDD Contract: {intent.title}")

        opus_file = intent.params.get("opus_file", "")
        doc_status = intent.params.get("doc_status", "unknown")
        files_to_create = intent.params.get("files_to_create", [])
        wiring_to_implement = intent.params.get("wiring_to_implement", [])

        return {
            "success": True,
            "handler": self.name,
            "action": "tdd_contract_acknowledged",
            "status": "RED_IS_CORRECT",
            "message": (
                f"TDD Contract for {Path(opus_file).stem}: "
                f"{len(files_to_create)} files to create, "
                f"{len(wiring_to_implement)} patterns to implement. "
                f"Doc status: {doc_status}. Red harness = correct behavior."
            ),
            "files_to_create": files_to_create,
            "wiring_to_implement": wiring_to_implement,
            "guidance": "Implement the files/patterns specified in the harness to make it green.",
        }


@register_handler
class StaleReferenceHandler(BaseHandler):
    """Handle stale reference intents (OPUS-128)."""

    name = "stale_reference"
    intent_types = ["harness_stale_reference"]
    agent_type = AgentType.DOCUMENTATION
    priority = 10

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Handle stale reference intents."""
        logger.info(f"🔄 Stale Reference: {intent.title}")

        opus_file = intent.params.get("opus_file", "")
        files_moved = intent.params.get("files_moved", {})
        wiring_moved = intent.params.get("wiring_moved", {})

        if not opus_file:
            return {"success": False, "handler": self.name, "error": "No opus_file specified"}

        opus_path = Path(opus_file)
        if not opus_path.exists():
            return {"success": False, "handler": self.name, "error": f"File not found: {opus_file}"}

        try:
            content = opus_path.read_text()
            updated = False

            for old_path, new_path in files_moved.items():
                if old_path in content:
                    content = content.replace(old_path, new_path)
                    updated = True
                    logger.info(f"  Updated: {old_path} → {new_path}")

            for pattern, new_file in wiring_moved.items():
                wiring_pattern = re.compile(
                    rf"(-\s*pattern:\s*[\"']?{re.escape(pattern)}[\"']?\s*\n\s*in:\s*)([^\s\n]+)",
                    re.MULTILINE,
                )
                if wiring_pattern.search(content):
                    content = wiring_pattern.sub(rf"\g<1>{new_file}", content)
                    updated = True
                    logger.info(f"  Updated wiring: '{pattern}' → {new_file}")

            if updated:
                opus_path.write_text(content)
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "references_updated",
                    "message": f"Updated {len(files_moved) + len(wiring_moved)} stale references",
                }
            else:
                return {
                    "success": True,
                    "handler": self.name,
                    "action": "no_changes_needed",
                    "message": f"No stale references found in {opus_path.name}",
                }

        except Exception as e:
            logger.error(f"❌ Stale reference update failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class CoverageGapHandler(BaseHandler):
    """Handle coverage gap intents (OPUS-129)."""

    name = "coverage_gap"
    intent_types = [
        "coverage_gap_critical",
        "coverage_gap_module",
        "coverage_gap_overall",
        "harness_optional_missing",
    ]
    agent_type = AgentType.DOCUMENTATION
    priority = 6

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Handle coverage gap intents."""
        intent_type = intent.intent_type
        logger.info(f"📊 Coverage Gap: {intent.title}")

        if intent_type == "harness_optional_missing":
            return {
                "success": True,
                "handler": self.name,
                "action": "info_only",
                "message": "Optional files missing. No action needed unless desired.",
                "priority": "trivial",
            }

        if intent_type == "coverage_gap_critical":
            return {
                "success": True,
                "handler": self.name,
                "action": "gap_identified",
                "element_type": intent.params.get("element_type"),
                "name": intent.params.get("name"),
                "message": f"Critical documentation gap: {intent.params.get('name')}",
            }

        if intent_type == "coverage_gap_module":
            return {
                "success": True,
                "handler": self.name,
                "action": "module_gap_identified",
                "module": intent.params.get("module"),
                "coverage": intent.params.get("coverage"),
                "message": f"Module {intent.params.get('module')} has low coverage",
            }

        return {
            "success": True,
            "handler": self.name,
            "action": "acknowledged",
            "message": f"Coverage gap acknowledged: {intent.title}",
        }


@register_handler
class TriageHandler(BaseHandler):
    """Handle triage intents (OPUS-132)."""

    name = "triage"
    intent_types = [
        "triage_p1_critical",
        "triage_p2_high",
        "triage_summary",
    ]
    agent_type = AgentType.DOCUMENTATION
    priority = 15

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Handle VivekaSense triage intents."""
        intent_type = intent.intent_type
        logger.info(f"🎯 Triage: {intent.title}")

        if intent_type == "triage_p1_critical":
            return {
                "success": True,
                "handler": self.name,
                "priority": "P1_CRITICAL",
                "action": "immediate_attention_required",
                "message": f"P1 Critical: {intent.title}",
            }

        if intent_type == "triage_p2_high":
            return {
                "success": True,
                "handler": self.name,
                "priority": "P2_HIGH",
                "action": "schedule_for_review",
                "message": f"P2 High: {intent.title}",
            }

        return {
            "success": True,
            "handler": self.name,
            "action": "triage_summary",
            "message": f"Triage summary: {intent.title}",
        }


@register_handler
class DocCreationHandler(BaseHandler):
    """Handle doc creation and consolidation intents (OPUS-054)."""

    name = "doc_creation"
    intent_types = [
        "create_opus_doc",
        "roadmap_create_doc",
        "consolidate_docs",
        "rename_doc",
    ]
    agent_type = AgentType.DOCUMENTATION
    priority = 8

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Handle doc creation intents."""
        if intent.intent_type in ("create_opus_doc", "roadmap_create_doc"):
            return self._create_doc(intent)
        elif intent.intent_type == "consolidate_docs":
            return self._consolidate_docs(intent)
        elif intent.intent_type == "rename_doc":
            return self._rename_doc(intent)
        else:
            return {"success": False, "handler": self.name, "error": "Unknown intent type"}

    def _create_doc(self, intent: "Intent") -> Dict[str, Any]:
        """Create new OPUS documentation."""
        logger.info(f"📜 SUTRA creating doc: {intent.title}")

        try:
            doc_number = intent.params.get("doc_number")
            doc_title = intent.params.get("doc_title", "Untitled")
            topic = intent.params.get("topic", "unknown")

            if not doc_number:
                return {"success": False, "handler": self.name, "error": "No doc_number specified"}

            if not (50 <= doc_number <= 99):
                return {
                    "success": False,
                    "handler": self.name,
                    "error": f"Doc number {doc_number} outside MANAS territory (050-099)",
                }

            doc_name = f"{doc_number:03d}-{topic.upper().replace(' ', '-')}.md"
            doc_path = self._workspace / "docs" / "architecture" / "OPUS" / doc_name

            if doc_path.exists():
                return {"success": False, "handler": self.name, "error": f"Doc already exists: {doc_name}"}

            content = (
                f"# OPUS-{doc_number:03d}: {doc_title}\n\n> Generated by MANAS\n\n## Overview\n\nTODO: Add content\n"
            )

            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(content)

            return {
                "success": True,
                "handler": self.name,
                "action": "doc_created",
                "doc_path": str(doc_path),
                "message": f"Created {doc_name}",
            }

        except Exception as e:
            logger.error(f"❌ Doc creation failed: {e}")
            return {"success": False, "handler": self.name, "error": str(e)}

    def _consolidate_docs(self, intent: "Intent") -> Dict[str, Any]:
        """Consolidate multiple docs."""
        return {
            "success": True,
            "handler": self.name,
            "action": "consolidation_acknowledged",
            "message": f"Doc consolidation queued: {intent.title}",
        }

    def _rename_doc(self, intent: "Intent") -> Dict[str, Any]:
        """Rename a doc."""
        return {
            "success": True,
            "handler": self.name,
            "action": "rename_acknowledged",
            "message": f"Doc rename queued: {intent.title}",
        }

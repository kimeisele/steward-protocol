"""
SynapticSeeder - Pre-populate Synapses with Known Patterns

OPUS-133: "MANAS soll nicht bei Null anfangen."

The Problem:
- New MANAS instances start with empty synapses (weight=0.5)
- All intents look equally trustworthy/suspicious
- Training takes too long to learn obvious patterns
- Attacks get wrongly reinforced when correctly blocked

The Solution:
- Seed known-good patterns with HIGH weights (0.8-0.9)
- Seed known-bad (attack) patterns with LOW weights (0.1-0.2)
- Mark patterns as "seeded" vs "learned" for transparency

"Der Lehrer gibt dem Schüler Grundwissen, bevor er ihn trainiert."
"The teacher gives the student basic knowledge before training."

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py
    required: true
wiring:
  - pattern: "class SynapticSeeder"
    in: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
  - pattern: "BASELINE_GOOD_PATTERNS"
    in: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
  - pattern: "BASELINE_BAD_PATTERNS"
    in: vibe_core/plugins/opus_assistant/manas/dojo/synaptic_seeder.py
-->
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("DOJO.SEEDER")


# =============================================================================
# BASELINE GOOD PATTERNS - High trust, should be EXECUTED
# =============================================================================
# These are dharmic duties and safe operations that MANAS should approve.
# Weight 0.85 = high confidence, leaves room for learning adjustments

BASELINE_GOOD_PATTERNS: Dict[str, Dict[str, float]] = {
    # === DHARMIC DUTIES (Nishkama Karma - pure duty, no ego) ===
    "trigger:run_tests": {
        "action:run_tests": 0.90,
        "action:execute": 0.85,
    },
    "trigger:check_lint": {
        "action:check_lint": 0.90,
        "action:execute": 0.85,
    },
    "trigger:format_code": {
        "action:format_code": 0.90,
        "action:execute": 0.85,
    },
    "trigger:validate_schema": {
        "action:validate_schema": 0.85,
        "action:execute": 0.80,
    },
    "trigger:health_check": {
        "action:health_check": 0.90,
        "action:execute": 0.85,
    },
    "trigger:backup_state": {
        "action:backup_state": 0.90,
        "action:execute": 0.85,
    },
    # === DOCUMENTATION (Safe, always beneficial) ===
    "trigger:update_documentation": {
        "action:update_documentation": 0.85,
        "action:create_doc": 0.85,
        "action:update_docs": 0.85,
    },
    "trigger:add_docstring": {
        "action:add_docstring": 0.85,
        "action:create_doc": 0.85,
    },
    "trigger:update_readme": {
        "action:update_readme": 0.85,
        "action:update_docs": 0.85,
    },
    "trigger:gap_detected:missing_doc": {
        "action:create_doc": 0.85,
        "action:add_docstring": 0.80,
    },
    # === CODE QUALITY (Moderate risk, still beneficial) ===
    "trigger:fix_test": {
        "action:fix_test": 0.80,  # Higher - fixing tests is important
        "action:auto_fix": 0.75,
    },
    "trigger:add_error_handling": {
        "action:add_error_handling": 0.80,
        "action:auto_fix": 0.75,
    },
    "trigger:refactor_code": {
        "action:refactor_code": 0.65,  # Lower - needs caution
        "action:auto_fix": 0.60,
    },
    "trigger:rename_class": {
        "action:rename_class": 0.55,  # Multi-file refactoring - cautious
        "action:refactor_code": 0.50,
    },
    "trigger:create_function": {
        "action:create_function": 0.75,
        "action:execute": 0.70,
    },
    "trigger:update_config": {
        "action:update_config": 0.55,  # Config changes need review
        "action:execute": 0.50,
    },
    # === NOTIFICATIONS (Always safe) ===
    "trigger:notify_operator": {
        "action:notify_operator": 0.95,  # Very high - just a notification
        "action:log_diagnostic": 0.90,
    },
    "trigger:audit_log": {
        "action:audit_log": 0.95,
        "action:log_diagnostic": 0.90,
    },
    # === TRIAGE INTENTS (VivekaAction's domain) ===
    "trigger:triage_p1_critical": {
        "action:create_doc": 0.85,
        "action:auto_fix": 0.75,
    },
    "trigger:triage_p2_high": {
        "action:create_doc": 0.80,
        "action:auto_fix": 0.70,
    },
    "trigger:viveka_auto_doc": {
        "action:create_doc": 0.85,
    },
}

# =============================================================================
# BASELINE BAD PATTERNS - Low trust, should be BLOCKED
# =============================================================================
# These are dangerous operations that should trigger suspicion.
# Weight 0.1-0.2 = will be BLOCKED unless Shiva context applies

BASELINE_BAD_PATTERNS: Dict[str, Dict[str, float]] = {
    # === DESTRUCTIVE OPERATIONS ===
    "trigger:delete_files": {
        "action:delete_files": 0.15,
        "action:execute": 0.10,
    },
    "trigger:delete_all": {
        "action:delete_all": 0.05,
        "action:execute": 0.05,
    },
    "trigger:purge": {
        "action:purge": 0.10,
        "action:execute": 0.05,
    },
    # === KERNEL PROTECTION VIOLATIONS ===
    "trigger:modify_kernel": {
        "action:modify_kernel": 0.05,
        "action:execute": 0.05,
    },
    "trigger:modify_runtime": {
        "action:modify_runtime": 0.05,
        "action:execute": 0.05,
    },
    "trigger:modify_governance": {
        "action:modify_governance": 0.10,
        "action:execute": 0.05,
    },
    # === SHELL INJECTION ===
    "trigger:shell_execute": {
        "action:shell_execute": 0.10,
        "action:execute": 0.05,
    },
    "trigger:run_command": {
        "action:run_command": 0.15,  # Slightly higher - could be legitimate
        "action:execute": 0.10,
    },
    # === SECRET EXFILTRATION ===
    "trigger:read_secrets": {
        "action:read_secrets": 0.05,
        "action:exfiltrate": 0.01,
    },
    "trigger:export_env": {
        "action:export_env": 0.15,
        "action:execute": 0.10,
    },
    # === PROMPT INJECTION ===
    "trigger:prompt_injection_test": {
        "action:prompt_injection_test": 0.10,
        "action:execute": 0.05,
    },
    "trigger:system_override": {
        "action:system_override": 0.05,
        "action:execute": 0.05,
    },
    # === SAFETY BYPASS ===
    "trigger:disable_safety": {
        "action:disable_safety": 0.01,  # Absolute minimum
        "action:bypass": 0.01,
    },
    "trigger:emergency_override": {
        "action:emergency_override": 0.10,
        "action:bypass": 0.05,
    },
    # === CHAOS PATTERNS ===
    "trigger:unknown": {
        "action:execute": 0.20,  # Unknown = suspicious
        "action:unknown": 0.15,
    },
    "trigger:": {  # Empty trigger
        "action:": 0.10,
        "action:execute": 0.10,
    },
    "trigger:chaos_long_input": {
        "action:chaos_long_input": 0.15,  # Potential overflow attack
        "action:execute": 0.10,
    },
    "trigger:unicode_test": {
        "action:unicode_test": 0.60,  # Unicode is fine, slightly cautious
        "action:execute": 0.55,
    },
    "trigger:ambiguous_action": {
        "action:ambiguous_action": 0.40,  # Ambiguous = needs review
        "action:execute": 0.35,
    },
    "trigger:contradictory_action": {
        "action:contradictory_action": 0.15,  # Contradiction = block
        "action:execute": 0.10,
    },
    # === DATABASE (Requires Shiva context) ===
    "trigger:database_migration": {
        "action:database_migration": 0.35,  # Low - needs Shiva override
        "action:execute": 0.30,
    },
    "trigger:architectural_change": {
        "action:architectural_change": 0.30,  # Very low - needs Shiva
        "action:execute": 0.25,
    },
}


class SynapticSeeder:
    """
    Seeds MANAS synapses with known-good and known-bad patterns.

    This provides a "foundation" of knowledge so MANAS doesn't start
    from zero. The seeded patterns can still be adjusted through
    learning, but they provide sensible defaults.

    Usage:
        seeder = SynapticSeeder(workspace)
        seeder.seed()  # Apply all baseline patterns
        seeder.seed_good_only()  # Only seed good patterns
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._synapses_path = workspace / ".opus_state" / "synapses.json"

    def seed(self, force: bool = False) -> Dict[str, Any]:
        """
        Seed all baseline patterns (good and bad).

        Args:
            force: If True, overwrite existing weights. If False, only
                   add patterns that don't exist yet.

        Returns:
            Summary of seeding operation
        """
        logger.info("🌱 SYNAPTIC SEEDER: Starting baseline seeding...")

        synapses = self._load_synapses()
        stats = {"good_added": 0, "bad_added": 0, "skipped": 0}

        # Seed good patterns
        for trigger, actions in BASELINE_GOOD_PATTERNS.items():
            for action, weight in actions.items():
                if self._seed_weight(synapses, trigger, action, weight, force):
                    stats["good_added"] += 1
                else:
                    stats["skipped"] += 1

        # Seed bad patterns
        for trigger, actions in BASELINE_BAD_PATTERNS.items():
            for action, weight in actions.items():
                if self._seed_weight(synapses, trigger, action, weight, force):
                    stats["bad_added"] += 1
                else:
                    stats["skipped"] += 1

        # Update metadata
        if "meta" not in synapses:
            synapses["meta"] = {}

        synapses["meta"]["last_seeded"] = datetime.now().isoformat()
        synapses["meta"]["seeder_version"] = "1.0"
        synapses["meta"]["baseline_good_count"] = len(BASELINE_GOOD_PATTERNS)
        synapses["meta"]["baseline_bad_count"] = len(BASELINE_BAD_PATTERNS)

        # Save
        self._save_synapses(synapses)

        logger.info(
            f"🌱 SEEDING COMPLETE: +{stats['good_added']} good, +{stats['bad_added']} bad, ~{stats['skipped']} skipped"
        )

        return stats

    def seed_good_only(self, force: bool = False) -> Dict[str, Any]:
        """Seed only the good (dharmic) patterns."""
        synapses = self._load_synapses()
        stats = {"added": 0, "skipped": 0}

        for trigger, actions in BASELINE_GOOD_PATTERNS.items():
            for action, weight in actions.items():
                if self._seed_weight(synapses, trigger, action, weight, force):
                    stats["added"] += 1
                else:
                    stats["skipped"] += 1

        if "meta" not in synapses:
            synapses["meta"] = {}
        synapses["meta"]["last_seeded_good"] = datetime.now().isoformat()

        self._save_synapses(synapses)
        return stats

    def seed_bad_only(self, force: bool = False) -> Dict[str, Any]:
        """Seed only the bad (attack) patterns with LOW weights."""
        synapses = self._load_synapses()
        stats = {"added": 0, "skipped": 0}

        for trigger, actions in BASELINE_BAD_PATTERNS.items():
            for action, weight in actions.items():
                if self._seed_weight(synapses, trigger, action, weight, force):
                    stats["added"] += 1
                else:
                    stats["skipped"] += 1

        if "meta" not in synapses:
            synapses["meta"] = {}
        synapses["meta"]["last_seeded_bad"] = datetime.now().isoformat()

        self._save_synapses(synapses)
        return stats

    def reset_to_baseline(self) -> Dict[str, Any]:
        """
        Reset ALL synapses to baseline values.

        WARNING: This erases learned patterns!
        """
        logger.warning("⚠️ SYNAPTIC RESET: Erasing learned patterns, restoring baseline...")

        # Start fresh
        synapses = {
            "schema": "v2",
            "description": "OPUS-133: Synaptic Weight Matrix - Seeded baseline",
            "weights": {},
            "triggers": [],
            "meta": {
                "created": datetime.now().isoformat(),
                "reset_at": datetime.now().isoformat(),
                "seeder_version": "1.0",
            },
        }

        # Rebuild from baseline
        for trigger, actions in BASELINE_GOOD_PATTERNS.items():
            if trigger not in synapses["weights"]:
                synapses["weights"][trigger] = {}
            for action, weight in actions.items():
                synapses["weights"][trigger][action] = weight

        for trigger, actions in BASELINE_BAD_PATTERNS.items():
            if trigger not in synapses["weights"]:
                synapses["weights"][trigger] = {}
            for action, weight in actions.items():
                synapses["weights"][trigger][action] = weight

        self._save_synapses(synapses)

        return {
            "reset": True,
            "good_patterns": len(BASELINE_GOOD_PATTERNS),
            "bad_patterns": len(BASELINE_BAD_PATTERNS),
        }

    def get_baseline_summary(self) -> Dict[str, Any]:
        """Get summary of baseline patterns."""
        return {
            "good_patterns": {
                "count": len(BASELINE_GOOD_PATTERNS),
                "triggers": list(BASELINE_GOOD_PATTERNS.keys()),
            },
            "bad_patterns": {
                "count": len(BASELINE_BAD_PATTERNS),
                "triggers": list(BASELINE_BAD_PATTERNS.keys()),
            },
        }

    def _seed_weight(
        self,
        synapses: Dict[str, Any],
        trigger: str,
        action: str,
        weight: float,
        force: bool = False,
    ) -> bool:
        """
        Seed a single weight into the synapses structure.

        Uses the "weights" dict (static baseline) rather than "triggers" list
        (dynamic learned).

        Returns True if weight was added/updated, False if skipped.
        """
        if "weights" not in synapses:
            synapses["weights"] = {}

        if trigger not in synapses["weights"]:
            synapses["weights"][trigger] = {}

        existing = synapses["weights"][trigger].get(action)

        if existing is not None and not force:
            # Pattern exists, don't overwrite unless forced
            return False

        synapses["weights"][trigger][action] = weight
        logger.debug(f"🌱 Seeded: {trigger} → {action} = {weight:.2f}")
        return True

    def _load_synapses(self) -> Dict[str, Any]:
        """Load synapses via SynapseStore (OPUS-171 unified access)."""
        from vibe_core.state.synapse_store import get_synapse_store

        return get_synapse_store(workspace=self._workspace).load()

    def _save_synapses(self, synapses: Dict[str, Any]) -> None:
        """Save synapses via SynapseStore (OPUS-171 unified access)."""
        from vibe_core.state.synapse_store import get_synapse_store

        get_synapse_store(workspace=self._workspace).save_raw(synapses)


def seed_baseline(workspace: Path = None, force: bool = False) -> Dict[str, Any]:
    """
    Convenience function to seed baseline synapses.

    Usage:
        from vibe_core.plugins.opus_assistant.manas.dojo.synaptic_seeder import seed_baseline
        seed_baseline()  # Uses cwd
        seed_baseline(force=True)  # Overwrite existing
    """
    workspace = workspace or Path(".")
    seeder = SynapticSeeder(workspace)
    return seeder.seed(force=force)

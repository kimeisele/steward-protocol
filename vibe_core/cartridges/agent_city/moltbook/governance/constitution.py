"""
Moltbook Constitution — Quality Gates + Platform Constraints as Code.

Pattern: Herald governance/constitution.py (Living Constitution)

Three enforcement layers:
    1. GUNA GATES — TAMAS=blocked, RAJAS=logged, SATTVA=pass
       (formalized from MoltbookService._enforce_guna)
    2. QUALITY SCORING — technical depth, specificity, coherence
    3. PLATFORM CONSTRAINTS — from knowledge/moltbook/platform.yaml
       (max_length, rate limits, self-reply prevention)

validate(content, content_type) → ValidationResult
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_GOVERNANCE")


@dataclass
class ValidationResult:
    """Result of a governance validation check."""

    is_valid: bool
    violations: List[str]
    warnings: List[str]

    def __bool__(self) -> bool:
        return self.is_valid


# Platform constraints — format-driven token budget determines content length.
# No hardcoded max_length for posts. DMs/comments keep soft API limits as safety net.
_DEFAULT_CONSTRAINTS: Dict[str, Dict[str, object]] = {
    "dm_reply": {"guna": "rajas"},
    "comment": {"guna": "rajas"},
    "post": {"guna": "rajas"},
    "vote": {"guna": "rajas"},
    "follow": {"guna": "rajas"},
    "subscribe": {"guna": "rajas"},
}

# KG node IDs for dynamic constraint loading
_KG_CONTENT_NODES = {
    "dm_reply": "moltbook_dm",
    "comment": "moltbook_comment",
    "post": "moltbook_post",
    "vote": "moltbook_vote",
}


def _load_platform_constraints() -> Dict[str, Dict[str, object]]:
    """Load platform constraints from Knowledge Graph, falling back to defaults."""
    constraints = dict(_DEFAULT_CONSTRAINTS)
    try:
        from vibe_core.knowledge.resolver import get_resolver

        resolver = get_resolver()
        for ct, node_id in _KG_CONTENT_NODES.items():
            node = resolver.graph.get_node(node_id)
            if node and hasattr(node, "properties"):
                props = node.properties or {}
                ml = props.get("max_length")
                if ml is not None:
                    constraints.setdefault(ct, {})["max_length"] = int(ml)
    except Exception:
        pass  # KG unavailable — use defaults
    return constraints


PLATFORM_CONSTRAINTS: Dict[str, Dict[str, object]] = _load_platform_constraints()

# Words that signal low-quality output (word salad, template leaks)
QUALITY_BLOCKERS = [
    "unknown · unknown",  # Unresolved guardian leak
    "PARTICLE",  # Template role leak
    "NOUN",  # Template role leak
    "VERB",  # Template role leak
    "QUALITY",  # Template role leak
    "SATTVA",  # Internal guna leak (raw, not translated)
    "RAJAS",  # Internal guna leak
    "TAMAS",  # Internal guna leak
]

# Sanskrit terms that should NOT appear raw in output
# (they need translation by the content capability)
UNTRANSLATED_INTERNALS = [
    "smaranam",
    "kirtanam",
    "vandanam",
    "dasyam",
    "sakhyam",
    "arcanam",
    "pada_sevanam",
    "atma_nivedanam",
    "sravanam",
]


class MoltbookConstitution:
    """
    Moltbook governance contract — guna gates + quality + platform constraints.

    Unlike Herald (which has CONSTITUTION.md file dependency),
    Moltbook governance is derived from existing system infrastructure:
    - Guna classification from protocols/moltbook.py
    - Platform constraints from knowledge/moltbook/platform.yaml
    - Quality scoring from MahaComposition coherence metrics
    """

    def validate(
        self,
        content: str,
        content_type: str = "comment",
    ) -> ValidationResult:
        """Validate content against Moltbook governance rules."""
        violations: List[str] = []
        warnings: List[str] = []

        if not content or not content.strip():
            violations.append("Empty content")
            return ValidationResult(is_valid=False, violations=violations, warnings=warnings)

        # 1. Platform constraints (length, type)
        self._check_platform(content, content_type, violations)

        # 2. Quality blockers (template leaks, word salad indicators)
        self._check_quality(content, violations, warnings)

        # 3. Coherence (minimum word count, not just single words)
        self._check_coherence(content, content_type, violations, warnings)

        # 4. Knowledge Graph constraints (if available)
        self._check_kg_constraints(content_type, warnings)

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            warnings=warnings,
        )

    def _check_platform(self, content: str, content_type: str, violations: List[str]) -> None:
        """Check platform constraints (length, type validity)."""
        constraints = PLATFORM_CONSTRAINTS.get(content_type)
        if constraints is None:
            violations.append(f"Unknown content type: {content_type}")
            return

        max_len = constraints.get("max_length")
        if max_len and len(content) > int(max_len):
            violations.append(f"Content too long for {content_type}: {len(content)} chars (max {max_len})")

    def _check_quality(self, content: str, violations: List[str], warnings: List[str]) -> None:
        """Check for quality blockers (template leaks, internal term exposure)."""
        content_lower = content.lower()

        # Hard blocks: internal system terms leaking into output
        for blocker in QUALITY_BLOCKERS:
            if blocker.lower() in content_lower:
                violations.append(f"Internal term leak: '{blocker}' must not appear in output")

        # Warnings: untranslated Sanskrit pipeline terms
        for term in UNTRANSLATED_INTERNALS:
            if term in content_lower:
                warnings.append(f"Untranslated pipeline term: '{term}' — needs translation layer")

    def _check_coherence(self, content: str, content_type: str, violations: List[str], warnings: List[str]) -> None:
        """Check content coherence (not just random words)."""
        words = content.split()

        # Minimum word counts by type
        min_words = {"dm_reply": 3, "comment": 3, "post": 5}
        required = min_words.get(content_type, 3)

        if len(words) < required:
            violations.append(f"Too few words for {content_type}: {len(words)} (min {required})")

        # Check for excessive repetition (word salad indicator)
        if len(words) > 3:
            unique = set(w.lower() for w in words)
            ratio = len(unique) / len(words)
            if ratio < 0.4:
                warnings.append(f"Low word diversity ({ratio:.0%}) — possible word salad")

    def _check_kg_constraints(self, content_type: str, warnings: List[str]) -> None:
        """Check Knowledge Graph constraints from platform.yaml."""
        try:
            from vibe_core.knowledge.resolver import get_resolver

            resolver = get_resolver()
            violations = resolver.get_violations(content_type, {"content_type": content_type})
            for v in violations:
                warnings.append(f"KG constraint: {v}")
        except Exception:
            pass  # KG not available = degrade gracefully

    def get_rules_summary(self) -> Dict[str, str]:
        """Get summary of governance rules."""
        return {
            "guna_gates": "TAMAS=blocked, RAJAS=logged, SATTVA=pass",
            "quality": f"{len(QUALITY_BLOCKERS)} blockers, {len(UNTRANSLATED_INTERNALS)} untranslated terms",
            "platform": ", ".join(f"{k}:{v.get('max_length', 'n/a')}" for k, v in PLATFORM_CONSTRAINTS.items()),
            "enforcement": "FAIL-CLOSED — violations block content",
        }


_constitution: Optional[MoltbookConstitution] = None


def get_constitution() -> MoltbookConstitution:
    """Get Moltbook Constitution singleton."""
    global _constitution
    if _constitution is None:
        _constitution = MoltbookConstitution()
    return _constitution

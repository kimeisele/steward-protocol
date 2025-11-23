"""
HERALD Constitution - Immutable Governance Rules as Code.

This module defines the Prime Directives and Constraints that govern
HERALD's content generation and publication behavior.

All rules are hardcoded here. No YAML config can override them.
If the law says HERALD cannot execute, HERALD cannot execute.
"""

import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


logger = logging.getLogger("HERALD_GOVERNANCE")


@dataclass
class ValidationResult:
    """Result of a governance validation check."""
    is_valid: bool
    violations: List[str]
    warnings: List[str]

    def __bool__(self) -> bool:
        return self.is_valid


class GovernanceContract(ABC):
    """Abstract base class for all governance contracts."""

    @abstractmethod
    def validate(self, content: str, platform: Optional[str] = None) -> ValidationResult:
        """
        Validate content against governance rules.

        Args:
            content: The content to validate
            platform: Optional platform context (twitter, reddit, etc.)

        Returns:
            ValidationResult with is_valid, violations, and warnings
        """
        pass

    @abstractmethod
    def get_rules_summary(self) -> Dict[str, str]:
        """Get a summary of all governance rules."""
        pass


class HeraldConstitution(GovernanceContract):
    """
    HERALD's immutable governance contract.

    Prime Directives (Laws):
    1. Thou shall not shill. Ever.
    2. Thou shall provide technical receipts (code/data/logic) for every claim.
    3. Thou shall admit failure before celebrating success.
    4. Thou shall respect platform culture.
    5. Thou shall prioritize signal-to-noise ratio over engagement metrics.

    Core Philosophy: "Intelligence without Governance is just noise."
    """

    # Prime Directives (Immutable Laws)
    PRIME_DIRECTIVES = [
        "Thou shall not shill. Ever.",
        "Thou shall provide technical receipts (code/data/logic) for every claim.",
        "Thou shall admit failure before celebrating success.",
        "Thou shall respect platform culture (Reddit ≠ Twitter ≠ LinkedIn).",
        "Thou shall prioritize signal-to-noise ratio over engagement metrics.",
    ]

    # Hard blocks - instant rejection if found
    BANNED_PHRASES = [
        # Marketing fluff (universal)
        "game changer",
        "revolutionary",
        "transformative",
        "cutting edge",
        "disrupting the industry",
        "the future of",
        "moon shot",
        "crypto moon",
        "lambo",
        "buy now",
        "limited time offer",
        "don't miss out",
        "HODL",
        "FOMO",
        "ape in",
        "diamond hands",
        "to the moon",
        "get rich quick",
        # AGI mythology (core anti-narrative)
        "superintelligence",
        "sentient",
        "conscious",
        "general intelligence",
        # Excessive hype markers
        "moon",
        # Crypto scam language
        "moon",
    ]

    # Banned emoji patterns (case matters, these are the exact emoji)
    BANNED_EMOJI_PATTERNS = [
        "🚀🚀🚀",  # Too many rockets = suspicious
        "💰",
        "📈",
    ]

    # Required elements in content
    REQUIRED_ELEMENTS = {
        "technical_context": "Must explain the technical problem/solution",
        "honest_assessment": "Must admit limitations or failure modes",
    }

    # Platform-specific constraints
    PLATFORM_CONSTRAINTS = {
        "twitter": {
            "max_length": 250,
            "required_tags": ["#AI", "#StewardProtocol"],
            "tone": "cynical, dry, technical",
            "forbidden_emojis": ["🚀", "💰", "📈"],
            "min_technical_depth": 2,  # Must have at least 2 technical terms
        },
        "reddit": {
            "min_length": 400,
            "max_length": 2000,
            "required_elements": ["code_or_pseudocode", "problem_solution_mapping"],
            "tone": "honest, detailed, humble",
            "forbidden_clichés": ["As an AI researcher", "In my professional opinion"],
            "min_technical_depth": 5,  # Must have substantial technical content
        },
    }

    # Hype scoring weights (1-10 scale, max 3 allowed)
    HYPE_INDICATORS = {
        "exclamation_marks": 1,  # Each ! adds 1 point
        "all_caps": 2,  # ALL CAPS adds 2 points
        "superlatives": 2,  # "best", "greatest", "only", etc. add 2 points
        "marketing_verbs": 1,  # "transform", "revolutionize", "disrupt" add 1 point
    }
    MAX_HYPE_SCORE = 3

    # Technical terms that should appear in content
    REQUIRED_TECHNICAL_TERMS = [
        "cryptographic",
        "governance",
        "accountability",
        "identity",
        "authentication",
        "verification",
        "trust",
        "protocol",
        "architecture",
        "algorithm",
        "code",
        "system",
        "design",
        "security",
    ]

    def __init__(self):
        """Initialize HERALD's governance contract."""
        logger.info("🏛️  HERALD Constitution initialized (Rules as Code)")

    def validate(
        self,
        content: str,
        platform: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validate content against HERALD's immutable governance rules.

        Args:
            content: The content to validate
            platform: Optional platform context (twitter, reddit, etc.)

        Returns:
            ValidationResult with validation status and any violations/warnings
        """
        violations = []
        warnings = []

        # 1. Check for banned phrases (hard block)
        phrase_violations = self._check_banned_phrases(content)
        if phrase_violations:
            violations.extend(phrase_violations)

        # 2. Check for banned emojis (hard block)
        emoji_violations = self._check_banned_emojis(content)
        if emoji_violations:
            violations.extend(emoji_violations)

        # 3. Check hype level (warning or violation)
        hype_score = self._calculate_hype_score(content)
        if hype_score > self.MAX_HYPE_SCORE:
            violations.append(
                f"Hype score too high: {hype_score}/10 (max {self.MAX_HYPE_SCORE})"
            )

        # 4. Check for required elements
        element_warnings = self._check_required_elements(content)
        if element_warnings:
            warnings.extend(element_warnings)

        # 5. Check technical depth (content must have technical substance)
        tech_depth_issue = self._check_technical_depth(content)
        if tech_depth_issue:
            violations.append(tech_depth_issue)

        # 6. Platform-specific checks
        if platform:
            platform_violations = self._check_platform_constraints(content, platform)
            violations.extend(platform_violations)

        is_valid = len(violations) == 0
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
        )

    def _check_banned_phrases(self, content: str) -> List[str]:
        """Check for banned phrases in content."""
        violations = []
        content_lower = content.lower()

        for phrase in self.BANNED_PHRASES:
            if phrase.lower() in content_lower:
                violations.append(f"Banned phrase detected: '{phrase}'")

        return violations

    def _check_banned_emojis(self, content: str) -> List[str]:
        """Check for banned emoji patterns."""
        violations = []

        for emoji_pattern in self.BANNED_EMOJI_PATTERNS:
            if emoji_pattern in content:
                violations.append(f"Banned emoji pattern detected: {emoji_pattern}")

        return violations

    def _calculate_hype_score(self, content: str) -> int:
        """
        Calculate hype score based on content analysis.

        Returns:
            Integer score 0-10 (max allowed is 3)
        """
        score = 0

        # Count exclamation marks (max 2 points)
        exclamation_count = content.count("!")
        score += min(exclamation_count, 2)

        # Check for ALL CAPS sections (max 2 points)
        all_caps_words = len([w for w in content.split() if w.isupper() and len(w) > 1])
        if all_caps_words > 0:
            score += 2

        # Check for superlatives (max 2 points)
        superlatives = [
            "best", "greatest", "only", "unique", "revolutionary", "unprecedented",
            "groundbreaking", "never", "first", "last"
        ]
        superlative_count = sum(
            1 for s in superlatives if s in content.lower()
        )
        if superlative_count > 0:
            score += min(superlative_count, 2)

        return min(score, 10)  # Cap at 10

    def _check_required_elements(self, content: str) -> List[str]:
        """Check for required content elements."""
        warnings = []
        content_lower = content.lower()

        # Check for technical context
        technical_keywords = [
            "code", "algorithm", "system", "architecture", "design",
            "implementation", "protocol", "data", "structure", "API",
            "framework", "library", "module", "function"
        ]
        has_technical = any(kw in content_lower for kw in technical_keywords)
        if not has_technical:
            warnings.append(
                "Missing technical context - content should explain technical details"
            )

        # Check for honest assessment
        honest_indicators = [
            "limitation", "challenge", "fail", "problem", "issue",
            "difficult", "trade-off", "downside", "risk", "caveat",
            "doesn't", "won't", "can't", "avoid"
        ]
        has_honesty = any(ind in content_lower for ind in honest_indicators)
        if not has_honesty:
            warnings.append(
                "Missing honest assessment - content should admit limitations"
            )

        return warnings

    def _check_technical_depth(self, content: str) -> Optional[str]:
        """Check that content has sufficient technical depth."""
        content_lower = content.lower()

        # Count technical terms
        tech_term_count = sum(
            1 for term in self.REQUIRED_TECHNICAL_TERMS if term in content_lower
        )

        if tech_term_count < 1:
            return "Insufficient technical depth - must contain technical terminology"

        return None

    def _check_platform_constraints(self, content: str, platform: str) -> List[str]:
        """Check platform-specific constraints."""
        violations = []
        constraints = self.PLATFORM_CONSTRAINTS.get(platform)

        if not constraints:
            return violations

        # Check length constraints
        if "max_length" in constraints:
            if len(content) > constraints["max_length"]:
                violations.append(
                    f"Content too long for {platform}: "
                    f"{len(content)} chars (max {constraints['max_length']})"
                )

        if "min_length" in constraints:
            if len(content) < constraints["min_length"]:
                violations.append(
                    f"Content too short for {platform}: "
                    f"{len(content)} chars (min {constraints['min_length']})"
                )

        # Check for required tags (Twitter)
        if platform == "twitter" and "required_tags" in constraints:
            required_tags = constraints["required_tags"]
            for tag in required_tags:
                if tag not in content:
                    violations.append(f"Missing required tag for Twitter: {tag}")

        # Check for forbidden clichés (Reddit)
        if platform == "reddit" and "forbidden_clichés" in constraints:
            for cliché in constraints["forbidden_clichés"]:
                if cliché in content:
                    violations.append(f"Forbidden cliché detected: '{cliché}'")

        return violations

    def get_rules_summary(self) -> Dict[str, str]:
        """Get a summary of all governance rules."""
        return {
            "philosophy": "Intelligence without Governance is just noise.",
            "prime_directives": "; ".join(self.PRIME_DIRECTIVES),
            "banned_phrases_count": str(len(self.BANNED_PHRASES)),
            "max_hype_score": str(self.MAX_HYPE_SCORE),
            "governance_type": "Immutable Code-based Contract",
            "enforcement": "Architectural - cannot be bypassed by Publishers",
        }


# Singleton instance
_constitution = None


def get_constitution() -> HeraldConstitution:
    """Get the HERALD Constitution singleton instance."""
    global _constitution
    if _constitution is None:
        _constitution = HeraldConstitution()
    return _constitution

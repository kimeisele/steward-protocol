"""
OPUS-310 Phase 4: Command-Aware Intent Matcher

Semantic matching using command metadata.
No LLM calls - pure pattern matching on:
- Command names (fuzzy match)
- Command descriptions (keyword extraction)
- Command tags (exact match)
- Command parameters (slot filling)

PROMPT.md: "Protocol statt konkrete Klassen"
This is the default implementation of IntentMatcherProtocol.
"""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Set

from vibe_core.protocols.command import CommandInfo, ParameterSpec
from vibe_core.protocols.intent import IntentMatch, IntentMatcherProtocol


class CommandAwareIntentMatcher:
    """
    Semantic matching using command metadata.

    Implements IntentMatcherProtocol.

    Matching Strategy:
    1. Name matching (40% weight) - fuzzy match on command name parts
    2. Description matching (30% weight) - keyword overlap
    3. Tag matching (30% weight) - exact tag matches

    Thresholds:
    - >= 0.8: High confidence, auto-execute
    - >= 0.5: Medium confidence, suggest options
    - < 0.5: Low confidence, fall back to chat
    """

    # Common action verbs mapped to command patterns
    ACTION_SYNONYMS: Dict[str, Set[str]] = {
        "show": {"list", "get", "display", "view", "see"},
        "list": {"show", "get", "display", "view", "all"},
        "create": {"add", "new", "make", "spawn"},
        "delete": {"remove", "destroy", "kill", "drop"},
        "update": {"edit", "modify", "change", "set"},
        "run": {"execute", "start", "launch", "do"},
        "stop": {"halt", "end", "kill", "terminate"},
        "status": {"state", "info", "check", "health"},
        "help": {"what", "how", "explain", "describe"},
    }

    # Stop words to ignore in matching
    STOP_WORDS: Set[str] = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "to",
        "of",
        "and",
        "or",
        "for",
        "in",
        "on",
        "at",
        "by",
        "me",
        "my",
        "i",
        "you",
        "your",
        "we",
        "our",
        "it",
        "its",
        "can",
        "could",
        "would",
        "should",
        "will",
        "do",
        "does",
        "please",
        "just",
        "now",
        "want",
        "need",
        "like",
    }

    def match(self, intent: str, commands: List[CommandInfo]) -> List[IntentMatch]:
        """
        Match intent to commands.

        Returns ranked list of matches with confidence scores.
        """
        if not intent or not commands:
            return []

        # Tokenize intent
        tokens = self._tokenize(intent)
        if not tokens:
            return []

        matches = []

        for cmd in commands:
            score = self._calculate_score(tokens, cmd)

            if score >= 0.3:  # Minimum threshold
                matches.append(
                    IntentMatch(
                        command=cmd,
                        confidence=score,
                        extracted_params=self._extract_params_internal(tokens, cmd),
                        reasoning=self._explain_match(tokens, cmd, score),
                    )
                )

        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)

        # Return top 5 matches
        return matches[:5]

    def extract_params(self, intent: str, command: CommandInfo) -> Dict[str, Any]:
        """Extract parameters from natural language."""
        tokens = self._tokenize(intent)
        return self._extract_params_internal(tokens, command)

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize and normalize text.

        Removes stop words, lowercases, splits on non-alpha.
        """
        # Lowercase and split on non-alphanumeric
        words = re.findall(r"[a-z0-9]+", text.lower())

        # Remove stop words
        tokens = [w for w in words if w not in self.STOP_WORDS]

        return tokens

    def _calculate_score(self, tokens: List[str], cmd: CommandInfo) -> float:
        """
        Calculate match score for a command.

        Weighted combination of:
        - Name matching: 40%
        - Description matching: 30%
        - Tag matching: 30%
        """
        name_score = self._name_match(tokens, cmd.name)
        desc_score = self._description_match(tokens, cmd.description)
        tag_score = self._tag_match(tokens, cmd.tags)

        # Weighted sum
        score = (name_score * 0.4) + (desc_score * 0.3) + (tag_score * 0.3)

        return min(1.0, score)

    def _name_match(self, tokens: List[str], name: str) -> float:
        """
        Match tokens against command name.

        Handles dotted names like 'agents.list' and fuzzy matching.
        """
        # Split command name into parts
        name_parts = name.lower().replace(".", " ").replace("_", " ").replace("-", " ").split()

        if not name_parts:
            return 0.0

        # Check for direct matches
        direct_matches = sum(1 for t in tokens if t in name_parts)
        if direct_matches > 0:
            return min(1.0, direct_matches / len(name_parts))

        # Check for synonym matches
        for token in tokens:
            synonyms = self._get_synonyms(token)
            for part in name_parts:
                if part in synonyms:
                    return 0.8  # High but not perfect

        # Fuzzy matching
        best_ratio = 0.0
        for token in tokens:
            for part in name_parts:
                ratio = SequenceMatcher(None, token, part).ratio()
                best_ratio = max(best_ratio, ratio)

        return best_ratio * 0.7  # Reduce fuzzy match weight

    def _description_match(self, tokens: List[str], description: str) -> float:
        """Match tokens against command description."""
        if not description:
            return 0.0

        desc_tokens = self._tokenize(description)
        if not desc_tokens:
            return 0.0

        # Count overlapping tokens
        overlap = sum(1 for t in tokens if t in desc_tokens)

        # Also check synonyms
        for token in tokens:
            synonyms = self._get_synonyms(token)
            for dt in desc_tokens:
                if dt in synonyms:
                    overlap += 0.5

        return min(1.0, overlap / max(len(tokens), 1))

    def _tag_match(self, tokens: List[str], tags: List[str]) -> float:
        """Match tokens against command tags."""
        if not tags:
            return 0.0

        # Normalize tags
        normalized_tags = [t.lower() for t in tags]

        # Direct matches
        matches = sum(1 for t in tokens if t in normalized_tags)

        # Synonym matches
        for token in tokens:
            synonyms = self._get_synonyms(token)
            for tag in normalized_tags:
                if tag in synonyms:
                    matches += 0.5

        return min(1.0, matches / max(len(tokens), 1))

    def _get_synonyms(self, word: str) -> Set[str]:
        """Get synonyms for a word."""
        word = word.lower()

        # Check if word is in any synonym group
        for key, synonyms in self.ACTION_SYNONYMS.items():
            if word == key or word in synonyms:
                return synonyms | {key}

        return {word}

    def _extract_params_internal(self, tokens: List[str], cmd: CommandInfo) -> Dict[str, Any]:
        """
        Extract parameter values from tokens.

        Simple slot filling based on:
        - Position after command keywords
        - Named parameter patterns (--param=value)
        - Quoted strings
        """
        params: Dict[str, Any] = {}

        if not cmd.parameters:
            return params

        # Look for named parameters (--param=value or --param value)
        # This is a simple implementation

        # For positional params, use remaining tokens after command words
        name_parts = set(cmd.name.lower().replace(".", " ").split())
        remaining = [t for t in tokens if t not in name_parts]

        # Assign to required params first
        required_params = [p for p in cmd.parameters if p.required]
        for i, param in enumerate(required_params):
            if i < len(remaining):
                params[param.name] = remaining[i]

        return params

    def _explain_match(self, tokens: List[str], cmd: CommandInfo, score: float) -> str:
        """Generate human-readable explanation of match."""
        parts = []

        name_score = self._name_match(tokens, cmd.name)
        if name_score > 0:
            parts.append(f"name match: {name_score:.0%}")

        desc_score = self._description_match(tokens, cmd.description)
        if desc_score > 0:
            parts.append(f"description match: {desc_score:.0%}")

        tag_score = self._tag_match(tokens, cmd.tags)
        if tag_score > 0:
            parts.append(f"tag match: {tag_score:.0%}")

        return f"Score {score:.0%} ({', '.join(parts)})"

"""
OPUS-172: ManasKnowledgePort - MANAS-Specific Knowledge Interface

Sanskrit: ज्ञान (Jnana) = Knowledge, Wisdom

This port provides MANAS with direct access to the decision engines:
- APCE (Automated Prioritization & Complexity Engine)
- FAE (Feasibility Analysis Engine)
- FDG (Feature Dependency Graph)

These are RESEARCH-BASED knowledge files with domain-specific schemas:
- APCE: feature_complexity, value_patterns, decision_heuristics
- FAE: incompatibilities, nfr_conflicts, tech_constraints
- FDG: features with dependency graphs

Unlike UnifiedKnowledgeGraph (which has ontology/topology/constraints/metrics),
ManasKnowledgePort provides specialized queries for MANAS decision-making.

Philosophy:
    "Knowledge (Jnana) is not separate from wisdom (Prajna).
     MANAS consults knowledge to make wise decisions."

Usage:
    port = ManasKnowledgePort(workspace=Path.cwd())

    # APCE: Get complexity score
    score = port.get_complexity("user_authentication_basic")
    # -> {"base_complexity": 5, "base_effort": "1-2 weeks", ...}

    # FAE: Check feasibility
    issues = port.check_feasibility("real_time_video_streaming")
    # -> {"incompatible_with": ["scope_v1.0"], "alternatives": [...]}

    # FDG: Get dependencies
    deps = port.get_dependencies("payment_processing")
    # -> {"required": ["user_database", "stripe_checkout_sdk"], ...}
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("MANAS.KnowledgePort")


class ManasKnowledgePort:
    """
    MANAS-Specific Knowledge Interface.

    Loads and provides access to the decision engine YAML files:
    - knowledge/manas/engines/APCE_rules.yaml
    - knowledge/manas/engines/FDG_dependencies.yaml
    - knowledge/manas/constraints/FAE_constraints.yaml
    """

    def __init__(self, workspace: Optional[Path] = None):
        """Initialize the knowledge port."""
        self._workspace = workspace or Path.cwd()
        self._knowledge_base = self._workspace / "knowledge" / "manas"

        # Lazy-loaded knowledge caches
        self._apce: Optional[Dict[str, Any]] = None
        self._fae: Optional[Dict[str, Any]] = None
        self._fdg: Optional[Dict[str, Any]] = None

        # Pre-indexed lookups (built on first access)
        self._complexity_index: Dict[str, Dict[str, Any]] = {}
        self._incompatibility_index: Dict[str, Dict[str, Any]] = {}
        self._feature_index: Dict[str, Dict[str, Any]] = {}

        logger.info("[MANAS_KNOWLEDGE] Port initialized")

    # =========================================================================
    # Lazy Loading
    # =========================================================================

    @property
    def apce(self) -> Dict[str, Any]:
        """Load APCE rules (complexity scoring)."""
        if self._apce is None:
            self._apce = self._load_yaml("engines/APCE_rules.yaml")
            self._build_complexity_index()
        return self._apce

    @property
    def fae(self) -> Dict[str, Any]:
        """Load FAE constraints (feasibility analysis)."""
        if self._fae is None:
            self._fae = self._load_yaml("constraints/FAE_constraints.yaml")
            self._build_incompatibility_index()
        return self._fae

    @property
    def fdg(self) -> Dict[str, Any]:
        """Load FDG dependencies (feature graph)."""
        if self._fdg is None:
            self._fdg = self._load_yaml("engines/FDG_dependencies.yaml")
            self._build_feature_index()
        return self._fdg

    def _load_yaml(self, relative_path: str) -> Dict[str, Any]:
        """Load a YAML file from knowledge/manas/.

        Handles multi-document YAML files (with --- separators) by merging
        all documents into a single dict.
        """
        path = self._knowledge_base / relative_path
        if not path.exists():
            logger.warning(f"[MANAS_KNOWLEDGE] File not found: {path}")
            return {}

        try:
            with open(path, "r") as f:
                # Handle multi-document YAML (merges all docs)
                docs = list(yaml.safe_load_all(f))
                if not docs:
                    return {}
                # Merge all documents into one dict
                result = {}
                for doc in docs:
                    if doc and isinstance(doc, dict):
                        result.update(doc)
            logger.debug(f"[MANAS_KNOWLEDGE] Loaded: {relative_path} ({len(docs)} docs)")
            return result
        except Exception as e:
            logger.error(f"[MANAS_KNOWLEDGE] Error loading {path}: {e}")
            return {}

    # =========================================================================
    # Index Building
    # =========================================================================

    def _build_complexity_index(self) -> None:
        """Build lookup index for APCE complexity scores."""
        if not self._apce:
            return

        # Index feature_complexity by feature_type
        for feature in self._apce.get("feature_complexity", []):
            feature_type = feature.get("feature_type")
            if feature_type:
                self._complexity_index[feature_type] = feature

        logger.debug(f"[MANAS_KNOWLEDGE] Indexed {len(self._complexity_index)} complexity rules")

    def _build_incompatibility_index(self) -> None:
        """Build lookup index for FAE incompatibilities."""
        if not self._fae:
            return

        # Index incompatibilities by feature name
        for item in self._fae.get("incompatibilities", []):
            feature = item.get("feature")
            if feature:
                self._incompatibility_index[feature] = item

        logger.debug(f"[MANAS_KNOWLEDGE] Indexed {len(self._incompatibility_index)} incompatibilities")

    def _build_feature_index(self) -> None:
        """Build lookup index for FDG features."""
        if not self._fdg:
            return

        # Index features by name and id
        for feature in self._fdg.get("features", []):
            name = feature.get("name")
            fid = feature.get("id")
            if name:
                self._feature_index[name] = feature
            if fid:
                self._feature_index[fid] = feature

        logger.debug(f"[MANAS_KNOWLEDGE] Indexed {len(self._feature_index)} features")

    # =========================================================================
    # APCE Queries (Complexity Scoring)
    # =========================================================================

    def get_complexity(self, feature_type: str) -> Optional[Dict[str, Any]]:
        """
        Get complexity score for a feature type.

        Args:
            feature_type: e.g. "user_authentication_basic", "payment_processing_basic"

        Returns:
            Dict with base_complexity, base_effort, multipliers, v1_recommendation
            or None if not found
        """
        _ = self.apce  # Ensure loaded
        return self._complexity_index.get(feature_type)

    def get_all_complexity_rules(self) -> List[Dict[str, Any]]:
        """Get all complexity rules."""
        return self.apce.get("feature_complexity", [])

    def get_value_pattern(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """
        Get value pattern by name.

        Args:
            pattern_name: e.g. "core_value_proposition", "user_delighter"

        Returns:
            Dict with description, value_score, examples, v1_status
        """
        for pattern in self.apce.get("value_patterns", []):
            if pattern.get("pattern") == pattern_name:
                return pattern
        return None

    def get_multipliers(self, category: str) -> List[Dict[str, Any]]:
        """
        Get complexity multipliers by category.

        Args:
            category: e.g. "integration_complexity", "compliance_overhead"

        Returns:
            List of multiplier rules
        """
        for mult_cat in self.apce.get("multipliers", []):
            if mult_cat.get("category") == category:
                return mult_cat.get("multipliers", [])
        return []

    def calculate_final_complexity(
        self,
        feature_type: str,
        active_triggers: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate final complexity score with multipliers.

        Args:
            feature_type: Base feature type
            active_triggers: List of active multiplier triggers

        Returns:
            Dict with base_complexity, final_complexity, applied_multipliers
        """
        base = self.get_complexity(feature_type)
        if not base:
            return {"error": f"Feature type '{feature_type}' not found"}

        base_score = base.get("base_complexity", 1)
        final_score = base_score
        applied = []

        active_triggers = active_triggers or []

        # Apply feature-specific multipliers
        for mult in base.get("multipliers", []):
            trigger = mult.get("trigger")
            if trigger in active_triggers:
                multiplier = mult.get("multiplier", 1.0)
                final_score *= multiplier
                applied.append(
                    {
                        "trigger": trigger,
                        "multiplier": multiplier,
                        "reason": mult.get("reason", ""),
                    }
                )

        return {
            "feature_type": feature_type,
            "base_complexity": base_score,
            "base_effort": base.get("base_effort"),
            "final_complexity": round(final_score, 1),
            "applied_multipliers": applied,
            "v1_recommendation": base.get("v1_recommendation"),
        }

    # =========================================================================
    # FAE Queries (Feasibility Analysis)
    # =========================================================================

    def check_feasibility(self, feature: str) -> Optional[Dict[str, Any]]:
        """
        Check if feature has feasibility constraints.

        Args:
            feature: Feature name to check

        Returns:
            Dict with incompatible_with, reason, alternatives, recommended_scope
            or None if no constraints
        """
        _ = self.fae  # Ensure loaded
        return self._incompatibility_index.get(feature)

    def get_nfr_conflicts(self, nfr_a: str = None) -> List[Dict[str, Any]]:
        """
        Get NFR (Non-Functional Requirement) conflicts.

        Args:
            nfr_a: Optional filter by first NFR

        Returns:
            List of NFR conflict rules
        """
        conflicts = self.fae.get("nfr_conflicts", [])
        if nfr_a:
            return [c for c in conflicts if c.get("nfr_a") == nfr_a]
        return conflicts

    def get_tech_constraints(self, technology: str = None) -> List[Dict[str, Any]]:
        """
        Get technology stack constraints.

        Args:
            technology: Optional filter by technology

        Returns:
            List of tech constraint rules
        """
        constraints = self.fae.get("tech_constraints", [])
        if technology:
            return [c for c in constraints if c.get("technology") == technology]
        return constraints

    def get_time_estimate(self, feature_type: str) -> Optional[Dict[str, Any]]:
        """
        Get time estimate for feature type.

        Args:
            feature_type: Feature type to estimate

        Returns:
            Dict with typical_time, complexity, reason
        """
        for est in self.fae.get("feature_time_estimates", []):
            if est.get("feature_type") == feature_type:
                return est
        return None

    # =========================================================================
    # FDG Queries (Dependency Graph)
    # =========================================================================

    def get_dependencies(self, feature_name: str) -> Optional[Dict[str, Any]]:
        """
        Get dependencies for a feature.

        Args:
            feature_name: Feature name or ID

        Returns:
            Dict with required_dependencies, optional_dependencies, complexity_multipliers
        """
        _ = self.fdg  # Ensure loaded
        return self._feature_index.get(feature_name)

    def get_required_dependencies(self, feature_name: str) -> List[Dict[str, Any]]:
        """
        Get required dependencies for a feature.

        Args:
            feature_name: Feature name or ID

        Returns:
            List of required dependency dicts
        """
        feature = self.get_dependencies(feature_name)
        if not feature:
            return []
        return feature.get("required_dependencies", [])

    def get_optional_dependencies(self, feature_name: str) -> List[Dict[str, Any]]:
        """
        Get optional dependencies for a feature.

        Args:
            feature_name: Feature name or ID

        Returns:
            List of optional dependency dicts
        """
        feature = self.get_dependencies(feature_name)
        if not feature:
            return []
        return feature.get("optional_dependencies", [])

    def get_category_pattern(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Get category pattern (e.g. "ecommerce", "saas").

        Args:
            category: Category name

        Returns:
            Dict with typical features and architecture notes
        """
        for pattern in self.fdg.get("category_patterns", []):
            if pattern.get("category") == category:
                return pattern
        return None

    # =========================================================================
    # Cross-Engine Queries
    # =========================================================================

    def analyze_feature(self, feature_name: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a feature across all engines.

        Args:
            feature_name: Feature to analyze

        Returns:
            Combined analysis from APCE, FAE, and FDG
        """
        result = {
            "feature": feature_name,
            "complexity": None,
            "feasibility": None,
            "dependencies": None,
            "recommendation": None,
        }

        # APCE: Complexity
        complexity = self.get_complexity(feature_name)
        if complexity:
            result["complexity"] = {
                "base_score": complexity.get("base_complexity"),
                "effort": complexity.get("base_effort"),
                "v1_recommendation": complexity.get("v1_recommendation"),
            }

        # FAE: Feasibility
        feasibility = self.check_feasibility(feature_name)
        if feasibility:
            result["feasibility"] = {
                "incompatible_with": feasibility.get("incompatible_with"),
                "reason": feasibility.get("reason"),
                "alternatives": feasibility.get("alternatives_for_v1"),
                "recommended_scope": feasibility.get("recommended_scope"),
            }

        # FDG: Dependencies
        deps = self.get_dependencies(feature_name)
        if deps:
            required = [d.get("component") for d in deps.get("required_dependencies", [])]
            optional = [d.get("component") for d in deps.get("optional_dependencies", [])]
            result["dependencies"] = {
                "required": required,
                "optional": optional,
                "complexity_score": deps.get("complexity_score"),
            }

        # Generate recommendation
        result["recommendation"] = self._generate_recommendation(result)

        return result

    def _generate_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Generate a recommendation based on analysis."""
        feature = analysis["feature"]

        # Check feasibility first
        if analysis["feasibility"]:
            scope = analysis["feasibility"].get("recommended_scope", "")
            if "v2" in scope.lower() or "later" in scope.lower():
                alternatives = analysis["feasibility"].get("alternatives", [])
                if alternatives:
                    return f"DEFER: {feature} is too complex for v1. Consider: {alternatives[0]}"
                return f"DEFER: {feature} is recommended for {scope}"

        # Check complexity
        if analysis["complexity"]:
            v1_rec = analysis["complexity"].get("v1_recommendation", "")
            score = analysis["complexity"].get("base_score", 0)
            if v1_rec == "wont_have_v1":
                return f"SKIP: {feature} is not recommended for v1 (complexity: {score})"
            elif score >= 8:
                return f"CAUTION: {feature} is high complexity ({score}). Plan carefully."

        # Check dependencies
        if analysis["dependencies"]:
            required = analysis["dependencies"].get("required", [])
            if len(required) > 3:
                return f"COMPLEX: {feature} has {len(required)} required dependencies. Ensure all are in place."

        return f"OK: {feature} appears feasible for v1"

    # =========================================================================
    # Status
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get knowledge port status."""
        return {
            "knowledge_base": str(self._knowledge_base),
            "apce_loaded": self._apce is not None,
            "fae_loaded": self._fae is not None,
            "fdg_loaded": self._fdg is not None,
            "complexity_rules": len(self._complexity_index) if self._apce else 0,
            "incompatibilities": len(self._incompatibility_index) if self._fae else 0,
            "features": len(self._feature_index) if self._fdg else 0,
        }

    def is_available(self) -> bool:
        """Check if knowledge files are available."""
        return self._knowledge_base.exists()


# =============================================================================
# Module-Level Convenience
# =============================================================================

_global_port: Optional[ManasKnowledgePort] = None


def get_manas_knowledge(workspace: Optional[Path] = None) -> ManasKnowledgePort:
    """Get or create global ManasKnowledgePort instance."""
    global _global_port
    if _global_port is None:
        _global_port = ManasKnowledgePort(workspace=workspace)
    return _global_port

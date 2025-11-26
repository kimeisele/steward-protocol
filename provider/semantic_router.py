"""
🧠 SEMANTIC ROUTER (PROJECT JNANA - Semantic Cortex)
Replaces keyword substring matching with neural semantic understanding.

Uses sentence-transformers for efficient local inference (no API keys, no internet).
Maps user inputs to concepts via vector similarity (cosine distance).
Implements confidence thresholds for routing decisions:
  - > 0.85: SATYA (Truth) - Execute immediately
  - 0.60-0.84: MANTHAN (Churning) - Request clarification
  - < 0.60: NETI NETI - Fall back to LLM

Architecture:
1. Load knowledge base (concept_map.yaml + intent_rules.yaml)
2. Compute embeddings for all concepts and keywords
3. Build in-memory FAISS index (or simple cosine similarity)
4. On user input: embed -> similarity match -> return concepts with confidence
5. Route based on confidence thresholds
"""

import logging
import yaml
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger("SEMANTIC_ROUTER")

# Lazy import of sentence-transformers (downloads model on first use)
_model = None
_model_lock = asyncio.Lock()

async def get_embedding_model():
    """
    Lazy-load sentence-transformers model.
    Downloads on first use and caches in data/models.
    Thread-safe using asyncio lock.
    """
    global _model
    if _model is not None:
        return _model

    async with _model_lock:
        if _model is not None:  # Double-check after acquiring lock
            return _model

        try:
            from sentence_transformers import SentenceTransformer

            # Specify cache directory to avoid re-downloads
            import os
            os.makedirs("data/models", exist_ok=True)
            os.environ["SENTENCE_TRANSFORMERS_HOME"] = "data/models"

            logger.info("🧠 Loading sentence-transformers model (all-MiniLM-L6-v2)...")
            _model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                cache_folder="data/models"
            )
            logger.info("✓ Semantic model loaded and cached")
            return _model
        except ImportError:
            logger.error("❌ sentence-transformers not installed. Install with: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to load semantic model: {e}")
            raise

@dataclass
class SemanticConcept:
    """Represents a detected concept with confidence score"""
    name: str
    category: str  # 'actions', 'domains', 'entities', 'patterns'
    confidence: float

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, SemanticConcept):
            return self.name == other.name
        return self.name == other

class ConfidenceLevel(Enum):
    """Confidence tier classification for routing"""
    HIGH = "high"      # > 0.85: Execute immediately (SATYA)
    MEDIUM = "medium"  # 0.60-0.84: Request clarification (MANTHAN)
    LOW = "low"        # < 0.60: Fall back to LLM (NETI NETI)

class SemanticRouter:
    """
    🧠 JNANA CORTEX: Vector-based semantic routing.
    Replaces DeterministicRouter.analyze() + DeterministicRouter.route()

    API compatibility:
    - analyze(text) -> Set[str]  # Now returns concepts with confidence
    - route(text) -> Dict with agent, intent_type, concepts, confidence
    """

    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.concepts = self._load_yaml("concept_map.yaml")
        self.rules = self._load_yaml("intent_rules.yaml").get("rules", [])

        # Embeddings cache: concept_name -> embedding vector
        self.embedding_cache: Dict[str, np.ndarray] = {}
        self.loaded = False

        logger.info("🧠 Semantic Router initialized (awaiting model load)")

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load YAML file from knowledge directory"""
        filepath = self.knowledge_dir / filename
        try:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"⚠️  Knowledge base not found: {filepath}")
            return {"rules": []} if filename == "intent_rules.yaml" else {}
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            return {"rules": []} if filename == "intent_rules.yaml" else {}

    async def _ensure_loaded(self):
        """Lazy-load embeddings on first use"""
        if self.loaded:
            return

        model = await get_embedding_model()
        logger.info("📊 Building semantic knowledge base (computing embeddings)...")

        # Flatten all keywords from concept_map
        all_keywords = {}  # keyword -> concept_name

        for category, mappings in self.concepts.items():
            if not isinstance(mappings, dict):
                continue

            for concept, keywords in mappings.items():
                if isinstance(keywords, list):
                    for kw in keywords:
                        all_keywords[kw.lower()] = concept

        # Compute embeddings for each unique concept
        concept_names = list(set(all_keywords.values()))

        if concept_names:
            logger.info(f"   • Embedding {len(concept_names)} concepts...")
            concept_embeddings = model.encode(concept_names, show_progress_bar=False)

            for concept, embedding in zip(concept_names, concept_embeddings):
                self.embedding_cache[concept] = embedding.astype(np.float32)

        logger.info(f"✓ Knowledge base ready ({len(self.embedding_cache)} concepts)")
        self.loaded = True

    async def analyze(self, text: str) -> Set[SemanticConcept]:
        """
        SANKHYA (Analysis): Breaks text into semantic concepts.
        Returns set of (concept_name, category, confidence) tuples.

        Uses semantic similarity instead of keyword matching.
        """
        await self._ensure_loaded()

        if not self.embedding_cache:
            logger.warning("⚠️  No concepts in knowledge base, using fallback")
            return set()

        model = await get_embedding_model()

        # Embed user input
        input_embedding = model.encode(text, show_progress_bar=False).astype(np.float32)

        # Compute similarity to all concepts
        found_concepts = {}  # concept_name -> max_confidence

        for concept_name, concept_embedding in self.embedding_cache.items():
            # Cosine similarity
            similarity = float(np.dot(input_embedding, concept_embedding) /
                             (np.linalg.norm(input_embedding) * np.linalg.norm(concept_embedding) + 1e-8))

            # Clamp to [0, 1]
            similarity = max(0.0, min(1.0, similarity))

            # Track concepts above threshold (even low confidence is useful for context)
            if similarity > 0.30:  # Lower threshold to capture more nuance
                if concept_name not in found_concepts or similarity > found_concepts[concept_name]:
                    found_concepts[concept_name] = similarity

        # Convert to SemanticConcept objects
        result = set()
        for concept_name, confidence in found_concepts.items():
            # Find category for this concept
            category = self._find_category(concept_name)
            result.add(SemanticConcept(
                name=concept_name,
                category=category,
                confidence=confidence
            ))

        return result

    def _find_category(self, concept_name: str) -> str:
        """Find which category a concept belongs to"""
        for category, mappings in self.concepts.items():
            if isinstance(mappings, dict) and concept_name in mappings:
                return category
        return "unknown"

    async def route(self, text: str, fallback_rules: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        KARMA (Routing): Deterministic path selection based on semantic concepts.
        Rules are evaluated top-to-bottom by priority.
        First matching rule wins (based on confidence thresholds).
        """
        concepts_with_conf = await self.analyze(text)

        # Extract concept names and compute max confidence
        concept_names = {c.name for c in concepts_with_conf}
        max_confidence = max((c.confidence for c in concepts_with_conf), default=0.0)

        logger.info(f"🔍 Detected Concepts: {concept_names} (max confidence: {max_confidence:.2f})")

        rules_to_check = self.rules if self.rules else (fallback_rules or [])

        # Evaluate rules top-to-bottom
        for rule in rules_to_check:
            triggers = set(rule.get("triggers", []))

            # Logic: Does the input contain ALL required triggers?
            # Empty triggers = Fallback rule
            if not triggers or triggers.issubset(concept_names):
                return {
                    "agent": rule.get("agent", "envoy"),
                    "rule_name": rule.get("name", "Unknown Rule"),
                    "response_type": rule.get("response_type", "FAST"),
                    "intent_type": rule.get("intent_type", "CHAT"),
                    "concepts": concept_names,
                    "concepts_with_confidence": concepts_with_conf,
                    "matched_triggers": triggers & concept_names if triggers else set(),
                    "confidence": max_confidence
                }

        # Ultimate fallback
        logger.warning("⚠️  No rules matched, using hard fallback")
        return {
            "agent": "envoy",
            "rule_name": "Hard Fallback",
            "response_type": "FAST",
            "intent_type": "CHAT",
            "concepts": concept_names,
            "concepts_with_confidence": concepts_with_conf,
            "matched_triggers": set(),
            "confidence": max_confidence
        }

    def _classify_confidence(self, confidence: float) -> ConfidenceLevel:
        """Classify confidence score into routing tier"""
        if confidence >= 0.85:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.60:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    async def resolve_intent_with_confidence(self, user_input: str) -> Dict[str, Any]:
        """
        Returns routing decision WITH confidence classification.
        Used by route_and_execute to decide between immediate execution, clarification, or fallback.
        """
        route_result = await self.route(user_input)
        confidence = route_result.get("confidence", 0.0)
        confidence_level = self._classify_confidence(confidence)

        return {
            **route_result,
            "confidence_level": confidence_level.value,
            "should_execute": confidence_level == ConfidenceLevel.HIGH,
            "should_clarify": confidence_level == ConfidenceLevel.MEDIUM,
            "should_fallback": confidence_level == ConfidenceLevel.LOW
        }

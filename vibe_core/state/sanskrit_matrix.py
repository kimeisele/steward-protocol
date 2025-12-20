"""
OPUS-140: Sanskrit Matrix - Phonemic Memory Compression

This module transforms Samskaras (distilled patterns) into Akshara signatures,
enabling extreme compression and mantra-based training.

Architecture:
    Samskara (67 patterns, 25KB)
        ↓ encode_as_akshara()
    Akshara Signature (~20 sigs, 2KB)
        ↓ find_mantras()
    Mantras (~10 patterns, 500 bytes)
        ↓ meditate_on_mantra() [in DOJO]
    Siddhi (perfected weights)

Philosophical Foundation:
    - Shruti (श्रुति) = KERNEL TRUTH (immutable)
    - Smriti (स्मृति) = MANAS INTERPRETATION (derived)
    - Mantra (मन्त्र) = MAN (mind) + TRA (to free)

OPUS Reference: docs/architecture/OPUS/OPUS-140-SANSKRIT-MATRIX.md
"""

import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("STATE.SANSKRIT")


# =============================================================================
# CONSTANTS: Varga-to-Layer Mapping (from OPUS-114)
# =============================================================================

# The 5 nasal consonants (anunasika) - one per Varga
# These are the "pure" representatives of each articulation class
LAYER_TO_AKSHARA = {
    "KERNEL": "ङ",  # KANTHYA (Guttural) - Deep system, ṅa
    "COGNITION": "ञ",  # TALAVYA (Palatal) - Flow/decision, ña
    "REPAIR": "ण",  # MURDHANYA (Retroflex) - Fixing, ṇa
    "INTERFACE": "न",  # DANTYA (Dental) - Connections, na
    "OUTPUT": "म",  # OSHTHYA (Labial) - Surface, ma
}

AKSHARA_TO_LAYER = {v: k for k, v in LAYER_TO_AKSHARA.items()}

# Decision modifiers (from Varga position 0-4)
DECISION_MODIFIERS = {
    "EXECUTE": "क",  # Position 0: Unvoiced, unaspirated (pure action)
    "WARN_EXECUTE": "ख",  # Position 1: Unvoiced, aspirated (cautious action)
    "BLOCK": "ग",  # Position 2: Voiced, unaspirated (stopping)
    "ASK_USER": "घ",  # Position 3: Voiced, aspirated (questioning)
}

# =============================================================================
# IAST TRANSLITERATION BRIDGE (Devanagari → Latin with Diacritics)
# =============================================================================
# This is the bridge layer for humans who can't read Devanagari
# but want to understand the phonemic structure.

DEVANAGARI_TO_IAST = {
    # Layer consonants (Nasals - anunāsika)
    "ङ": "ṅ",  # KERNEL - velar nasal
    "ञ": "ñ",  # COGNITION - palatal nasal
    "ण": "ṇ",  # REPAIR - retroflex nasal
    "न": "n",  # INTERFACE - dental nasal
    "म": "m",  # OUTPUT - labial nasal
    # Decision modifiers (Stops - sparśa)
    "क": "k",  # EXECUTE - voiceless velar
    "ख": "kh",  # WARN_EXECUTE - aspirated voiceless velar
    "ग": "g",  # BLOCK - voiced velar
    "घ": "gh",  # ASK_USER - aspirated voiced velar
    # Common vowel (for syllable completion)
    "अ": "a",  # inherent vowel
}

IAST_TO_DEVANAGARI = {v: k for k, v in DEVANAGARI_TO_IAST.items()}

# Full phonetic names for human reference
AKSHARA_NAMES = {
    "ङ": {"iast": "ṅa", "english": "nga", "position": "velar", "meaning": "deep/kernel"},
    "ञ": {"iast": "ña", "english": "nya", "position": "palatal", "meaning": "flow/cognition"},
    "ण": {"iast": "ṇa", "english": "na (retroflex)", "position": "retroflex", "meaning": "repair"},
    "न": {"iast": "na", "english": "na (dental)", "position": "dental", "meaning": "interface"},
    "म": {"iast": "ma", "english": "ma", "position": "labial", "meaning": "output/surface"},
    "क": {"iast": "ka", "english": "ka", "position": "0", "meaning": "pure action"},
    "ख": {"iast": "kha", "english": "kha", "position": "1", "meaning": "cautious action"},
    "ग": {"iast": "ga", "english": "ga", "position": "2", "meaning": "stopping/blocking"},
    "घ": {"iast": "gha", "english": "gha", "position": "3", "meaning": "questioning"},
}

# Intent type to layer mapping (heuristic)
INTENT_TO_LAYER = {
    # KERNEL layer intents
    "run_tests": "KERNEL",
    "check_lint": "KERNEL",
    "format_code": "KERNEL",
    "build": "KERNEL",
    "start_kernel": "KERNEL",
    "modify_kernel": "KERNEL",
    # COGNITION layer intents
    "evaluate_tool_output": "COGNITION",
    "analyze_error": "COGNITION",
    "detect_code_smell": "COGNITION",
    "plan_strategy": "COGNITION",
    # REPAIR layer intents
    "fix_test": "REPAIR",
    "fix_lint": "REPAIR",
    "fix_bug": "REPAIR",
    "refactor": "REPAIR",
    # INTERFACE layer intents
    "update_readme": "INTERFACE",
    "update_documentation": "INTERFACE",
    "create_pr": "INTERFACE",
    "commit_changes": "INTERFACE",
    # OUTPUT layer intents
    "notify_operator": "OUTPUT",
    "log_observation": "OUTPUT",
    "escalate": "OUTPUT",
    "shell_execute": "OUTPUT",
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================


@dataclass
class AksharaSignature:
    """
    A Samskara encoded as a Sanskrit phonemic signature.

    Example:
        intent_type="modify_kernel", decision="BLOCK"
        → akshara="ङ", decision_modifier="ग"
        → full_signature="ङग" (KERNEL-BLOCK)
    """

    akshara: str  # The layer akshara (ङ, ञ, ण, न, म)
    layer: str  # The code layer (KERNEL, COGNITION, etc.)
    decision: str  # The decision (EXECUTE, WARN_EXECUTE, BLOCK)
    decision_modifier: str  # The decision akshara (क, ख, ग, घ)

    # Statistics from Samskara
    count: int
    avg_dharmic_score: float
    trend: str = "stable"

    @property
    def full_signature(self) -> str:
        """Full Sanskrit signature: Layer + Decision."""
        return f"{self.akshara}{self.decision_modifier}"

    @property
    def romanized(self) -> str:
        """Romanized version for logging."""
        layer_roman = {"ङ": "ṅa", "ञ": "ña", "ण": "ṇa", "न": "na", "म": "ma"}
        decision_roman = {"क": "ka", "ख": "kha", "ग": "ga", "घ": "gha"}
        return f"{layer_roman.get(self.akshara, '?')}-{decision_roman.get(self.decision_modifier, '?')}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Mantra:
    """
    A frequently-occurring Akshara signature that becomes a "Mantra".

    Mantras are patterns that should be automatic - after sufficient
    repetition (Japa), they become Siddhi (perfected).

    Example:
        Mantra(signature="ङक", meaning="KERNEL-EXECUTE", total_count=50)
        → After 108 repetitions, this is hardcoded as "always approve"
    """

    signature: str  # e.g., "ङक"
    layer: str  # e.g., "KERNEL"
    decision: str  # e.g., "EXECUTE"
    meaning: str  # Human-readable: "KERNEL actions should EXECUTE"

    # Statistics
    total_count: int  # How many Samskaras contributed
    avg_score: float  # Average dharmic score
    intent_types: List[str] = field(default_factory=list)  # Which intents

    # Japa status
    repetitions: int = 0  # How many times reinforced
    siddhi: bool = False  # Has it reached 108 (or 16*108)?

    @property
    def progress_to_siddhi(self) -> float:
        """Progress toward Siddhi (0.0 to 1.0)."""
        return min(1.0, self.repetitions / 108)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["progress_to_siddhi"] = self.progress_to_siddhi
        return d


@dataclass
class SanskritMatrixReport:
    """Report on Sanskrit Matrix compression."""

    total_samskaras: int
    total_signatures: int
    total_mantras: int
    compression_ratio: float

    # Layer distribution
    layer_distribution: Dict[str, int] = field(default_factory=dict)

    # Decision distribution
    decision_distribution: Dict[str, int] = field(default_factory=dict)

    # Top mantras
    top_mantras: List[str] = field(default_factory=list)

    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# CORE FUNCTIONS
# =============================================================================


def infer_layer(intent_type: str) -> str:
    """
    Infer the code layer for an intent type.

    Uses the INTENT_TO_LAYER mapping with fallback to heuristics.
    """
    # Direct mapping
    if intent_type in INTENT_TO_LAYER:
        return INTENT_TO_LAYER[intent_type]

    # Heuristic fallbacks
    lower = intent_type.lower()

    if any(k in lower for k in ["kernel", "core", "system", "boot"]):
        return "KERNEL"
    if any(k in lower for k in ["analyze", "evaluate", "detect", "think"]):
        return "COGNITION"
    if any(k in lower for k in ["fix", "repair", "refactor", "patch"]):
        return "REPAIR"
    if any(k in lower for k in ["doc", "readme", "update", "link", "connect"]):
        return "INTERFACE"
    if any(k in lower for k in ["output", "notify", "log", "shell", "execute"]):
        return "OUTPUT"

    # Default to COGNITION (thinking/decision layer)
    return "COGNITION"


def encode_samskara(samskara: Dict[str, Any]) -> AksharaSignature:
    """
    Encode a Samskara as an Akshara signature.

    Args:
        samskara: A Samskara dict with intent_type, decision, count, etc.

    Returns:
        AksharaSignature with phonemic encoding
    """
    intent_type = samskara.get("intent_type", "unknown")
    decision = samskara.get("decision", "WARN_EXECUTE")
    count = samskara.get("count", 1)
    avg_score = samskara.get("avg_dharmic_score", 0.5)
    trend = samskara.get("trend", "stable")

    # Infer layer from intent type
    layer = infer_layer(intent_type)

    # Get akshara for layer
    akshara = LAYER_TO_AKSHARA.get(layer, "ञ")  # Default to COGNITION

    # Get decision modifier
    decision_modifier = DECISION_MODIFIERS.get(decision, "ख")  # Default to WARN

    return AksharaSignature(
        akshara=akshara,
        layer=layer,
        decision=decision,
        decision_modifier=decision_modifier,
        count=count,
        avg_dharmic_score=avg_score,
        trend=trend,
    )


def encode_all_samskaras(samskaras: List[Dict[str, Any]]) -> List[AksharaSignature]:
    """
    Encode all Samskaras as Akshara signatures.

    Args:
        samskaras: List of Samskara dicts

    Returns:
        List of AksharaSignature objects
    """
    return [encode_samskara(s) for s in samskaras]


def find_mantras(signatures: List[AksharaSignature], min_count: int = 5) -> List[Mantra]:
    """
    Find Mantras from Akshara signatures.

    A Mantra is a frequently-occurring (layer, decision) combination
    that should become automatic.

    Args:
        signatures: List of AksharaSignature objects
        min_count: Minimum total count to become a Mantra

    Returns:
        List of Mantra objects, sorted by frequency
    """
    # Group by full signature
    groups: Dict[str, List[AksharaSignature]] = {}
    for sig in signatures:
        key = sig.full_signature
        if key not in groups:
            groups[key] = []
        groups[key].append(sig)

    # Create Mantras from frequent groups
    mantras = []
    for sig_key, sigs in groups.items():
        total_count = sum(s.count for s in sigs)
        if total_count < min_count:
            continue

        # Use first signature as template
        template = sigs[0]

        # Aggregate intent types
        intent_types = list({s.layer for s in sigs})  # Unique layers (should be same)

        # Calculate average score
        avg_score = sum(s.avg_dharmic_score * s.count for s in sigs) / total_count

        mantra = Mantra(
            signature=sig_key,
            layer=template.layer,
            decision=template.decision,
            meaning=f"{template.layer} actions should {template.decision}",
            total_count=total_count,
            avg_score=round(avg_score, 3),
            intent_types=intent_types,
            repetitions=0,
            siddhi=False,
        )
        mantras.append(mantra)

    # Sort by count (most frequent first)
    mantras.sort(key=lambda m: m.total_count, reverse=True)

    return mantras


def generate_sanskrit_matrix(samskaras_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete Sanskrit Matrix from consolidated Samskaras.

    Args:
        samskaras_data: Output from consolidate_viveka_decisions()

    Returns:
        Complete Sanskrit Matrix with signatures, mantras, and report
    """
    samskaras = samskaras_data.get("samskaras", [])

    if not samskaras:
        return {
            "signatures": [],
            "mantras": [],
            "report": SanskritMatrixReport(
                total_samskaras=0,
                total_signatures=0,
                total_mantras=0,
                compression_ratio=0,
                generated_at=datetime.now().isoformat(),
            ).to_dict(),
        }

    # Encode all Samskaras
    signatures = encode_all_samskaras(samskaras)

    # Find Mantras
    mantras = find_mantras(signatures)

    # Calculate distributions
    layer_dist = Counter(s.layer for s in signatures)
    decision_dist = Counter(s.decision for s in signatures)

    # Generate report
    report = SanskritMatrixReport(
        total_samskaras=len(samskaras),
        total_signatures=len(signatures),
        total_mantras=len(mantras),
        compression_ratio=round(len(samskaras) / max(len(mantras), 1), 1),
        layer_distribution=dict(layer_dist),
        decision_distribution=dict(decision_dist),
        top_mantras=[m.signature for m in mantras[:5]],
        generated_at=datetime.now().isoformat(),
    )

    logger.info(
        f"🕉️ Sanskrit Matrix: {len(samskaras)} samskaras → {len(signatures)} signatures → {len(mantras)} mantras"
    )

    return {
        "signatures": [s.to_dict() for s in signatures],
        "mantras": [m.to_dict() for m in mantras],
        "report": report.to_dict(),
        "version": "1.0",
    }


# =============================================================================
# MANTRA JAPA (Meditation)
# =============================================================================


def record_japa(mantra: Mantra, success: bool = True) -> Mantra:
    """
    Record a Japa (repetition) for a Mantra.

    Each successful reinforcement increments the repetition count.
    After 108 repetitions, the Mantra reaches Siddhi.

    Args:
        mantra: The Mantra being chanted
        success: Whether the repetition was successful

    Returns:
        Updated Mantra
    """
    if success:
        mantra.repetitions += 1

        # Check for Siddhi (108 repetitions)
        if mantra.repetitions >= 108 and not mantra.siddhi:
            mantra.siddhi = True
            logger.info(f"🕉️ SIDDHI ACHIEVED: {mantra.signature} ({mantra.meaning})")

    return mantra


def get_western_translation(mantra: Mantra) -> str:
    """
    Translate a Mantra to Western abstraction layer.

    Backend: ङक (KERNEL-EXECUTE)
    Frontend: "System operations auto-approved"

    Args:
        mantra: The Mantra to translate

    Returns:
        Human-readable Western translation
    """
    translations = {
        ("KERNEL", "EXECUTE"): "System operations auto-approved",
        ("KERNEL", "BLOCK"): "Core modifications require approval",
        ("COGNITION", "EXECUTE"): "Analysis tasks proceed automatically",
        ("COGNITION", "WARN_EXECUTE"): "Complex decisions need confirmation",
        ("REPAIR", "EXECUTE"): "Fix operations auto-approved",
        ("REPAIR", "BLOCK"): "Refactoring requires review",
        ("INTERFACE", "EXECUTE"): "Documentation updates auto-approved",
        ("INTERFACE", "WARN_EXECUTE"): "API changes need confirmation",
        ("OUTPUT", "EXECUTE"): "Logging operations proceed",
        ("OUTPUT", "BLOCK"): "External commands blocked",
    }

    key = (mantra.layer, mantra.decision)
    return translations.get(key, f"{mantra.layer} actions: {mantra.decision}")


def signature_to_iast(signature: str) -> str:
    """
    Convert a Devanagari signature to IAST (diacritics).

    Example: ञख → ñakha

    Args:
        signature: Devanagari signature (e.g., "ञख")

    Returns:
        IAST transliteration (e.g., "ñakha")
    """
    result = []
    for char in signature:
        if char in DEVANAGARI_TO_IAST:
            result.append(DEVANAGARI_TO_IAST[char])
        else:
            result.append(char)  # Keep unknown chars

    # Add inherent 'a' vowel after consonants (Sanskrit rule)
    iast = "".join(result)
    # Simple heuristic: add 'a' between consonant clusters
    return iast + "a" if iast else iast


def get_full_translation(signature: str, layer: str, decision: str) -> Dict[str, Any]:
    """
    Get the complete multi-layer translation for a mantra.

    This is the BRIDGE that connects all layers:
    Layer 0 (Sanskrit): ञख
    Layer 1 (IAST):     ñakha
    Layer 2 (Technical): COGNITION/WARN_EXECUTE
    Layer 3 (Semantic):  "Complex decisions need confirmation"

    Args:
        signature: Devanagari signature
        layer: Technical layer name
        decision: Decision type

    Returns:
        Dict with all translation layers
    """
    # Create a minimal Mantra for translation
    mantra = Mantra(
        signature=signature,
        layer=layer,
        decision=decision,
        meaning=f"{layer}/{decision}",
        total_count=0,
        avg_score=0.5,
    )

    return {
        "devanagari": signature,
        "iast": signature_to_iast(signature),
        "technical": f"{layer}/{decision}",
        "semantic": get_western_translation(mantra),
        "layer_info": AKSHARA_NAMES.get(signature[0], {}) if signature else {},
        "decision_info": AKSHARA_NAMES.get(signature[1], {}) if len(signature) > 1 else {},
    }

"""
Phase 2: Samskara Layer - Memory Consolidation

Samskaras are "impressions" or "imprints" in Vedic philosophy.
They represent consolidated patterns from raw experiences.

This module transforms raw decision logs into distilled patterns:
    260 raw decisions (155KB) → ~20 Samskaras (~5KB)

The consolidation preserves:
    - Statistical patterns (what decisions were made)
    - Confidence trends (how sure was MANAS)
    - Learning signals (what to improve)

OPUS Reference: P0-STATE-AUDIT.md, Phase 2
"""

import logging
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from statistics import mean, stdev
from typing import Any, Dict, List, Optional

logger = logging.getLogger("STATE.SAMSKARA")


@dataclass
class Samskara:
    """
    A distilled pattern from raw decisions.

    Like a memory trace, it captures the essence without the details.
    """

    # Pattern identity
    intent_type: str
    decision: str  # EXECUTE, WARN_EXECUTE, BLOCK

    # Statistics
    count: int
    avg_dharmic_score: float
    avg_resonance: float

    # Confidence
    score_stddev: float = 0.0
    dominant_harmony: str = "unknown"

    # Temporal
    first_seen: str = ""
    last_seen: str = ""

    # Learning signal
    trend: str = "stable"  # improving, declining, stable

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SamskaraReport:
    """Summary of consolidated memory."""

    total_raw_decisions: int
    total_samskaras: int
    compression_ratio: float

    # Decision distribution
    execute_pct: float
    warn_pct: float
    block_pct: float

    # Insights
    top_uncertain: List[str] = field(default_factory=list)  # High WARN rate
    top_blocked: List[str] = field(default_factory=list)  # High BLOCK rate
    top_confident: List[str] = field(default_factory=list)  # High EXECUTE rate

    consolidated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def consolidate_viveka_decisions(decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main consolidation function for viveka_decisions.json.

    This is the consolidation_fn that StateService calls when
    file size exceeds threshold.

    Args:
        decisions: Raw list of VivekaDecisionLog entries

    Returns:
        Consolidated structure with Samskaras and report
    """
    if not decisions:
        return {"samskaras": [], "report": {}, "raw_sample": []}

    logger.info(f"🔮 Consolidating {len(decisions)} decisions into Samskaras...")

    # Group by (intent_type, decision)
    groups: Dict[tuple, List[Dict]] = defaultdict(list)
    for d in decisions:
        key = (d.get("intent_type", "unknown"), d.get("decision", "unknown"))
        groups[key].append(d)

    # Create Samskaras
    samskaras: List[Samskara] = []

    for (intent_type, decision), entries in groups.items():
        scores = [e.get("dharmic_score", 0.5) for e in entries]
        resonances = [e.get("resonance", 0.5) for e in entries]
        harmonies = [e.get("harmony", "unknown") for e in entries]
        timestamps = [e.get("timestamp", "") for e in entries]

        # Calculate statistics
        avg_score = mean(scores) if scores else 0.5
        avg_resonance = mean(resonances) if resonances else 0.5
        score_std = stdev(scores) if len(scores) > 1 else 0.0

        # Dominant harmony
        harmony_counts = Counter(harmonies)
        dominant_harmony = harmony_counts.most_common(1)[0][0] if harmony_counts else "unknown"

        # Temporal bounds
        sorted_ts = sorted(t for t in timestamps if t)
        first_seen = sorted_ts[0] if sorted_ts else ""
        last_seen = sorted_ts[-1] if sorted_ts else ""

        # Trend detection (simple: compare first half vs second half)
        trend = "stable"
        if len(scores) >= 4:
            mid = len(scores) // 2
            first_half_avg = mean(scores[:mid])
            second_half_avg = mean(scores[mid:])
            if second_half_avg > first_half_avg + 0.05:
                trend = "improving"
            elif second_half_avg < first_half_avg - 0.05:
                trend = "declining"

        samskara = Samskara(
            intent_type=intent_type,
            decision=decision,
            count=len(entries),
            avg_dharmic_score=round(avg_score, 3),
            avg_resonance=round(avg_resonance, 3),
            score_stddev=round(score_std, 3),
            dominant_harmony=dominant_harmony,
            first_seen=first_seen,
            last_seen=last_seen,
            trend=trend,
        )
        samskaras.append(samskara)

    # Sort by count (most frequent first)
    samskaras.sort(key=lambda s: s.count, reverse=True)

    # Generate report
    total = len(decisions)
    decision_counts = Counter(d.get("decision") for d in decisions)

    # Find insights
    intent_decision_rates: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for d in decisions:
        intent_decision_rates[d.get("intent_type", "unknown")][d.get("decision", "unknown")] += 1

    # Calculate rates per intent
    top_uncertain = []
    top_blocked = []
    top_confident = []

    for intent, rates in intent_decision_rates.items():
        total_for_intent = sum(rates.values())
        if total_for_intent < 3:  # Skip rare intents
            continue

        warn_rate = rates.get("WARN_EXECUTE", 0) / total_for_intent
        block_rate = rates.get("BLOCK", 0) / total_for_intent
        exec_rate = rates.get("EXECUTE", 0) / total_for_intent

        if warn_rate > 0.5:
            top_uncertain.append(f"{intent} ({warn_rate:.0%} warn)")
        if block_rate > 0.5:
            top_blocked.append(f"{intent} ({block_rate:.0%} blocked)")
        if exec_rate > 0.5:
            top_confident.append(f"{intent} ({exec_rate:.0%} execute)")

    report = SamskaraReport(
        total_raw_decisions=total,
        total_samskaras=len(samskaras),
        compression_ratio=round(total / max(len(samskaras), 1), 1),
        execute_pct=round(decision_counts.get("EXECUTE", 0) / total * 100, 1),
        warn_pct=round(decision_counts.get("WARN_EXECUTE", 0) / total * 100, 1),
        block_pct=round(decision_counts.get("BLOCK", 0) / total * 100, 1),
        top_uncertain=top_uncertain[:5],
        top_blocked=top_blocked[:5],
        top_confident=top_confident[:5],
        consolidated_at=datetime.now().isoformat(),
    )

    # Keep a sample of raw decisions for debugging
    raw_sample = decisions[-10:] if len(decisions) > 10 else decisions

    result = {
        "samskaras": [s.to_dict() for s in samskaras],
        "report": report.to_dict(),
        "raw_sample": raw_sample,
        "version": "1.0",
        "consolidated_from": total,
    }

    logger.info(
        f"✅ Consolidated: {total} decisions → {len(samskaras)} samskaras (compression: {report.compression_ratio}x)"
    )

    return result


def get_samskara_insights(samskaras_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract actionable insights from consolidated Samskaras.

    Used by MANAS to understand its own patterns.
    """
    report = samskaras_data.get("report", {})
    samskaras = samskaras_data.get("samskaras", [])

    insights = {
        "confidence_level": "unknown",
        "learning_priorities": [],
        "strengths": [],
        "weaknesses": [],
    }

    # Overall confidence
    exec_pct = report.get("execute_pct", 0)
    warn_pct = report.get("warn_pct", 0)

    if exec_pct > 50:
        insights["confidence_level"] = "high"
    elif warn_pct > 60:
        insights["confidence_level"] = "uncertain"
    else:
        insights["confidence_level"] = "moderate"

    # Learning priorities (declining trends)
    for s in samskaras:
        if s.get("trend") == "declining":
            insights["learning_priorities"].append(s.get("intent_type"))

    # Strengths (high execute rate with good scores)
    for s in samskaras:
        if s.get("decision") == "EXECUTE" and s.get("avg_dharmic_score", 0) > 0.7:
            insights["strengths"].append(s.get("intent_type"))

    # Weaknesses (high block rate)
    for s in samskaras:
        if s.get("decision") == "BLOCK" and s.get("count", 0) > 5:
            insights["weaknesses"].append(s.get("intent_type"))

    return insights

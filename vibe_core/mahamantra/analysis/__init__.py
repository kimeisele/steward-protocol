"""
Mahamantra Analysis Module

Knowledge graph and derivation analysis for Seed constants.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb93c4f68"  # GenesisByte: parampara % 37 == 0

from .derivation_graph import DerivationGraph, EdgeType, NodeCategory

__all__ = ["DerivationGraph", "NodeCategory", "EdgeType"]

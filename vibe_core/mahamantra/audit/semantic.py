"""
CHAITANYA - Semantic Analyzer
==============================

"chaitanya mahaprabhu ei saba gunanidhi"
"Lord Chaitanya Mahaprabhu is the reservoir of all transcendental qualities."
-- Chaitanya Charitamrita

Understands the MEANING of the code:
- Architecture layer identification (Prabhupada, Avatar, Mahajana, Service)
- Gita integration points
- Delegation patterns (Sravanam - who listens to whom)
- BUILD vs RUNTIME component classification
- Resonance routing analysis
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# === MAHAJANA DECLARATION ===
__mahajana__ = "chaitanya"
__position__ = 3
__genesis__ = "0x00000003"

# Architecture layers
LAYER_PATTERNS = {
    "prabhupada": [r"prabhupada", r"shakti", r"mercy", r"guru"],
    "avatar": [r"nrisimha", r"bali", r"shuka", r"yamaraja", r"avatar"],
    "mahajana": [r"vyasa", r"brahma", r"narada", r"shambhu", r"prithu", 
                 r"kumara", r"kapila", r"manu", r"parashurama", r"prahlada",
                 r"janaka", r"bhishma", r"mahajana"],
    "gita": [r"gita", r"bhagavad", r"chapter", r"verse", r"sloka"],
    "sankirtan": [r"sankirtan", r"kirtan", r"chamber", r"resonance"],
    "cell": [r"maha_?cell", r"cell_?unified", r"universal_?cell"],
    "shadow": [r"shadow", r"jiva", r"delegate"],
    "naga": [r"naga", r"sesha", r"vasuki", r"takshaka", r"kaliya"],
}

# BUILD vs RUNTIME patterns
BUILD_PATTERNS = [r"encode", r"tensor", r"compress", r"position", r"seed"]
RUNTIME_PATTERNS = [r"execute", r"guardian", r"response", r"serve", r"handle"]


@dataclass
class SemanticInfo:
    """Semantic information about a module."""
    path: str
    layers: Set[str] = field(default_factory=set)
    is_build: bool = False
    is_runtime: bool = False
    delegation_targets: List[str] = field(default_factory=list)
    gita_references: List[str] = field(default_factory=list)


class SemanticAnalyzer:
    """
    Analyzes the semantic meaning of code modules.
    
    Usage:
        analyzer = SemanticAnalyzer(project_root)
        analyzer.analyze()
        layers = analyzer.by_layer("gita")
        flow = analyzer.delegation_flow()
    """
    
    def __init__(self, root: Path):
        self.root = root
        self._modules: Dict[str, SemanticInfo] = {}
        self._analyzed = False
    
    def analyze(self, scanner=None) -> None:
        """Analyze semantic meaning of all modules."""
        if scanner is None:
            from .scanner import ModuleScanner
            scanner = ModuleScanner(self.root)
            scanner.scan_all()
        
        for path, mod_info in scanner._modules.items():
            sem_info = SemanticInfo(path=path)
            
            try:
                content = mod_info.path.read_text(encoding="utf-8").lower()
                
                # Identify layers
                for layer, patterns in LAYER_PATTERNS.items():
                    for pattern in patterns:
                        if re.search(pattern, content):
                            sem_info.layers.add(layer)
                            break
                
                # BUILD vs RUNTIME
                for pattern in BUILD_PATTERNS:
                    if re.search(pattern, content):
                        sem_info.is_build = True
                        break
                
                for pattern in RUNTIME_PATTERNS:
                    if re.search(pattern, content):
                        sem_info.is_runtime = True
                        break
                
                # Delegation patterns
                delegation_match = re.findall(
                    r"(?:delegate|forward|route).*?(?:to|->)\s*['\"]?(\w+)",
                    content
                )
                sem_info.delegation_targets = delegation_match[:10]
                
                # Gita references
                gita_match = re.findall(
                    r"(?:gita|bg)[\s_]*(\d+)[\s_.:]*(\d+)",
                    content
                )
                sem_info.gita_references = [f"BG {c}.{v}" for c, v in gita_match[:10]]
                
            except Exception:
                pass
            
            self._modules[path] = sem_info
        
        self._analyzed = True
    
    def by_layer(self, layer: str) -> List[str]:
        """Get all modules in a specific architecture layer."""
        if not self._analyzed:
            self.analyze()
        return [path for path, info in self._modules.items() if layer in info.layers]
    
    def build_runtime_split(self) -> Dict[str, List[str]]:
        """Classify modules into BUILD vs RUNTIME."""
        if not self._analyzed:
            self.analyze()
        
        return {
            "build_only": [p for p, i in self._modules.items() if i.is_build and not i.is_runtime],
            "runtime_only": [p for p, i in self._modules.items() if i.is_runtime and not i.is_build],
            "both": [p for p, i in self._modules.items() if i.is_build and i.is_runtime],
            "neither": [p for p, i in self._modules.items() if not i.is_build and not i.is_runtime],
        }
    
    def delegation_flow(self) -> Dict[str, Any]:
        """Analyze the delegation flow (Sravanam principle)."""
        if not self._analyzed:
            self.analyze()
        
        # Count modules per layer
        layer_counts: Dict[str, int] = defaultdict(int)
        for info in self._modules.values():
            for layer in info.layers:
                layer_counts[layer] += 1
        
        # Expected hierarchy: Prabhupada -> Avatar -> Mahajana -> Service
        return {
            "layer_distribution": dict(layer_counts),
            "hierarchy": [
                ("prabhupada", layer_counts.get("prabhupada", 0)),
                ("avatar", layer_counts.get("avatar", 0)),
                ("mahajana", layer_counts.get("mahajana", 0)),
                ("naga", layer_counts.get("naga", 0)),
                ("shadow", layer_counts.get("shadow", 0)),
            ],
            "gita_integration": layer_counts.get("gita", 0),
            "sankirtan_modules": layer_counts.get("sankirtan", 0),
        }
    
    def summary(self) -> Dict[str, Any]:
        """Get a token-efficient summary."""
        if not self._analyzed:
            self.analyze()
        
        return {
            "total_analyzed": len(self._modules),
            "delegation_flow": self.delegation_flow(),
            "build_runtime": self.build_runtime_split(),
        }


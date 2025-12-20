# OPUS-155: Akasha Nervous System - Pre-Cognitive Wiring Awareness

> **Status**: IMPLEMENTING
> **Created**: 2025-12-20
> **Prereqs**: OPUS-052 (Akasha), OPUS-114 (Akshara Resonance), OPUS-110 (CodeScanner)
> **Philosophy**: Akasha must FEEL before Manas THINKS.

<!-- @HARNESS
intent: "Enable pre-cognitive wiring awareness through import/call edge creation"
files:
  - path: vibe_core/knowledge/code_scanner.py
    required: true
  - path: vibe_core/knowledge/schema.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/cortex/akasha.py
    required: true
  - path: vibe_core/plugins/opus_assistant/manas/akshara.py
    required: true
wiring:
  - pattern: "RelationType.IMPORTS"
    in: vibe_core/knowledge/schema.py
  - pattern: "RelationType.CALLS"
    in: vibe_core/knowledge/schema.py
  - pattern: "_scan_imports"
    in: vibe_core/knowledge/code_scanner.py
  - pattern: "_scan_calls"
    in: vibe_core/knowledge/code_scanner.py
tests:
  - tests/knowledge/test_import_edges.py
  - tests/knowledge/test_call_edges.py
-->

---

## The Problem: Akasha is Deaf

```
CURRENT STATE:
══════════════════════════════════════════════════════════════

  CodeScanner ──────→ Creates nodes (MODULE, CLASS, FUNCTION)
                      Creates DEFINES, INHERITS edges

                      BUT...

  RelationType.IMPORTS  ← DEFINED but NEVER CREATED
  RelationType.CALLS    ← DEFINED but NEVER CREATED

  Result: Akasha knows WHAT exists, not HOW it connects.
          It's a warehouse, not a nervous system.
```

---

## The Vision: Proprioception

> "Du ziehst die Hand weg, BEVOR dein Gehirn denkt: 'Das ist heiß.'"

Like the body's proprioception (knowing where your limbs are without looking),
Akasha must sense the "electrical state" of the codebase BEFORE Manas analyzes it.

```
TARGET STATE:
══════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────┐
  │                    AKASHA ÄTHER                         │
  │                                                         │
  │   ┌─────────┐  IMPORTS  ┌─────────┐                    │
  │   │kernel.py│══════════▶│core_util│  Resonance: 1.0    │
  │   │(KANTHYA)│           │(KANTHYA)│  "Pure Harmony"    │
  │   └────┬────┘           └─────────┘                    │
  │        ║                                                │
  │        ║ IMPORTS (cross-layer)                         │
  │        ▼                                                │
  │   ┌─────────┐                                          │
  │   │renderer │           Resonance: 0.2                 │
  │   │(OSHTHYA)│           "Electrical Noise" ⚡          │
  │   └─────────┘                                          │
  │                                                         │
  │   Akasha FEELS this dissonance before Manas thinks!    │
  └─────────────────────────────────────────────────────────┘
```

---

## The Implementation

### Phase 1: Create the Nadis (Import Edges)

Every `import` statement is a wire. We must trace them:

```python
# In code_scanner.py

def _scan_imports(self, module_node: Node, tree: ast.AST) -> List[Edge]:
    """
    Scan a module's AST for import statements.
    Create IMPORTS edges to target modules.

    Returns edges representing the "wires" between modules.
    """
    edges = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                target_module = alias.name
                edges.append(Edge(
                    source=module_node.id,
                    target=f"module:{target_module}",
                    relation=RelationType.IMPORTS,
                    weight=1.0,  # Can be weighted by frequency later
                ))

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                edges.append(Edge(
                    source=module_node.id,
                    target=f"module:{node.module}",
                    relation=RelationType.IMPORTS,
                    weight=len(node.names),  # More imports = stronger connection
                ))

    return edges
```

### Phase 2: Create the Sparks (Call Edges)

Function calls are energy transfers:

```python
def _scan_calls(self, module_node: Node, tree: ast.AST) -> List[Edge]:
    """
    Scan for function calls that cross module boundaries.
    These are the "sparks" of execution flow.
    """
    edges = []
    call_counts = Counter()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Extract called function name
            if isinstance(node.func, ast.Attribute):
                # obj.method() style
                call_target = node.func.attr
            elif isinstance(node.func, ast.Name):
                # direct_call() style
                call_target = node.func.id
            else:
                continue

            call_counts[call_target] += 1

    # Create edges for significant call patterns
    for target, count in call_counts.items():
        if count >= 2:  # Only track repeated calls
            edges.append(Edge(
                source=module_node.id,
                target=f"function:{target}",
                relation=RelationType.CALLS,
                weight=count,
            ))

    return edges
```

### Phase 3: Calculate Resonance (Harmonic Distance)

Apply Akshara's Varga resonance to module pairs:

```python
# In akasha.py or a new module_resonance.py

def calculate_module_resonance(source_path: str, target_path: str) -> float:
    """
    Calculate resonance between two modules based on their layer distance.

    Uses OPUS-114 Varga mapping:
    - Same layer: 1.0 (perfect harmony)
    - Adjacent layers: 0.8 (natural flow)
    - 2 layers apart: 0.6 (moderate)
    - 3 layers apart: 0.4 (weak)
    - 4 layers apart: 0.2 (electrical noise)
    """
    from vibe_core.plugins.opus_assistant.manas.akshara import (
        get_path_varga,
        Varga,
    )

    source_varga = get_path_varga(source_path)
    target_varga = get_path_varga(target_path)

    distance = abs(source_varga.value - target_varga.value)
    resonance_map = {0: 1.0, 1: 0.8, 2: 0.6, 3: 0.4, 4: 0.2}

    return resonance_map.get(distance, 0.1)
```

### Phase 4: The Friction Heatmap

Create a "pain map" showing architectural stress:

```python
def get_wiring_friction(self) -> Dict[str, float]:
    """
    Calculate friction score for each module.

    High friction = many cross-layer imports = architectural smell
    Low friction = clean layer boundaries = healthy design
    """
    friction_map = {}

    for edge in self.graph.get_edges(relation=RelationType.IMPORTS):
        resonance = calculate_module_resonance(edge.source, edge.target)

        # Friction is inverse of resonance
        friction = 1.0 - resonance

        # Accumulate friction per module
        if edge.source not in friction_map:
            friction_map[edge.source] = 0.0
        friction_map[edge.source] += friction * edge.weight

    return friction_map

def get_pain_points(self, threshold: float = 2.0) -> List[str]:
    """
    Return modules with high accumulated friction.
    These are architectural pain points.
    """
    friction = self.get_wiring_friction()
    return [mod for mod, score in friction.items() if score >= threshold]
```

---

## The Akasha Query Extensions

New queries for wiring awareness:

```python
# In akasha.py

def what_imports(self, module_id: str) -> AkashaQueryResult:
    """What does this module import?"""
    edges = self._get_edges(source=module_id, relation=RelationType.IMPORTS)
    return AkashaQueryResult(nodes=[e.target for e in edges])

def what_imports_me(self, module_id: str) -> AkashaQueryResult:
    """What modules import this one?"""
    edges = self._get_edges(target=module_id, relation=RelationType.IMPORTS)
    return AkashaQueryResult(nodes=[e.source for e in edges])

def get_resonance_with(self, source: str, target: str) -> float:
    """Get the harmonic resonance between two modules."""
    return calculate_module_resonance(source, target)

def get_dissonant_imports(self, threshold: float = 0.4) -> List[Edge]:
    """Find imports with low resonance (cross-layer violations)."""
    dissonant = []
    for edge in self.graph.get_edges(relation=RelationType.IMPORTS):
        resonance = calculate_module_resonance(edge.source, edge.target)
        if resonance <= threshold:
            edge.metadata["resonance"] = resonance
            dissonant.append(edge)
    return dissonant
```

---

## The Metaphysical Model

```
VEDIC MAPPING:
══════════════════════════════════════════════════════════════

  AKASHA (आकाश)     = The Ether/Space that carries vibration
  ────────────────────────────────────────────────────────────
  IMPORTS           = Nadis (नाडी) - The channels/wires
  CALLS             = Prana (प्राण) - The life force/sparks
  RESONANCE         = Shabda (शब्द) - The harmony of vibration
  FRICTION          = Vikara (विकार) - The distortion/pain


  LAYER MAPPING (Varga to Element):
  ────────────────────────────────────────────────────────────
  KANTHYA (Throat)  → Ether  → KERNEL (deep, foundational)
  TALAVYA (Palate)  → Air    → COGNITION (flowing, deciding)
  MURDHANYA (Roof)  → Fire   → REPAIR (transforming, fixing)
  DANTYA (Teeth)    → Water  → INTERFACE (connecting, flowing)
  OSHTHYA (Lips)    → Earth  → OUTPUT (manifesting, visible)


  HEALTHY ARCHITECTURE:
  ────────────────────────────────────────────────────────────
  ✓ Same-layer imports       → Resonance 1.0 → Silent harmony
  ✓ Adjacent-layer imports   → Resonance 0.8 → Natural flow
  ✗ 3+ layer jumps           → Resonance 0.4 → Architectural smell
  ✗ KERNEL → OUTPUT direct   → Resonance 0.2 → Violation!
```

---

## Test Cases

```python
def test_import_edges_created():
    """Verify IMPORTS edges are created from Python imports."""
    scanner = CodeScanner()
    scanner.scan_file("test_module.py")

    edges = scanner.graph.get_edges(relation=RelationType.IMPORTS)
    assert len(edges) > 0

def test_cross_layer_import_detected():
    """Verify cross-layer imports are flagged as dissonant."""
    # Module in KERNEL layer importing from OUTPUT layer
    source = "vibe_core/runtime/kernel.py"
    target = "vibe_core/cli/output.py"

    resonance = calculate_module_resonance(source, target)
    assert resonance <= 0.4  # Should be flagged as dissonant

def test_same_layer_import_harmonic():
    """Verify same-layer imports have high resonance."""
    source = "vibe_core/runtime/kernel.py"
    target = "vibe_core/runtime/scheduler.py"

    resonance = calculate_module_resonance(source, target)
    assert resonance >= 0.8  # Should be harmonic
```

---

## Summary

| Before OPUS-155 | After OPUS-155 |
|-----------------|----------------|
| Akasha is a warehouse | Akasha is a nervous system |
| Knows WHAT exists | Feels HOW things connect |
| Waits for Manas | Pre-cognitive awareness |
| Static graph | Vibrating resonance field |
| IMPORTS defined, unused | IMPORTS create edges |
| CALLS defined, unused | CALLS track energy flow |

**The Result:** When Manas awakens to solve a problem, it enters a space that already *vibrates*. It feels "Ah, in `mandala.py` there's high tension" before reading a single line of code.

---

## Next Steps

1. ✅ OPUS-155 Spec (this document)
2. 🔄 Extend `code_scanner.py` with `_scan_imports()`
3. ⏳ Extend `code_scanner.py` with `_scan_calls()`
4. ⏳ Add resonance calculation to Akasha
5. ⏳ Create friction heatmap
6. ⏳ Test with real codebase

---

**आकाश जाग्रत** - Akasha Awakens.

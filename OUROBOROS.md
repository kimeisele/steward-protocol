# OUROBOROS - Self-Healing Loop Implementation Plan

> "Die Schlange, die sich selbst frisst" - The system that heals itself.

**Status:** IN PROGRESS
**Score:** 26/100 → Ziel: 85/100
**Erstellt:** 2026-01-03
**Branch:** `claude/fix-architecture-debt-lzeEz`

---

## 1. VISION

Das Steward Protocol soll ein **selbstheilendes Immunsystem** haben:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         OUROBOROS LOOP                              │
│                                                                     │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐ │
│    │ WATCHMAN │────▶│ KNOWLEDGE│────▶│  MANAS   │────▶│ SHUDDHI  │ │
│    │ Detection│     │  GRAPH   │     │  Dojo    │     │ Healing  │ │
│    └──────────┘     └──────────┘     └──────────┘     └──────────┘ │
│         ▲                                                   │       │
│         │                                                   │       │
│         │              ┌──────────┐                         │       │
│         └──────────────│ GENESIS  │◀────────────────────────┘       │
│                        │ Creation │                                 │
│                        └──────────┘                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Wie ein biologisches Immunsystem:**
- Erkennt Eindringlinge (Violations)
- Lernt aus Erfahrung (Synapses)
- Heilt automatisch (Remedies)
- Entwickelt neue Abwehr (Genesis)

---

## 2. AKTUELLER STAND (Was bereits existiert)

### ✅ ERLEDIGT

| Komponente | Status | Beschreibung |
|------------|--------|--------------|
| RemedyLoader | ✅ | Dynamische Discovery statt Hardcoding |
| RemedyProtocol | ✅ | Type-safe Interface für Remedies |
| 7 Remedies | ✅ | subprocess_timeout, silent_failure, get_instance, iterdir, path_scanning, direct_registry, unsafe_io |
| 27 Tests | ✅ | test_remedy_loader.py, test_remedies.py |
| Manas → Shuddhi | ✅ | ActionManager.inject_shuddhi() existiert |
| Knowledge Schema | ✅ | NodeType.VIOLATION, REMEDY, RelationType.HEALED_BY |

### ❌ FEHLT (Die Lücken)

| Lücke | Priorität | Beschreibung |
|-------|-----------|--------------|
| Watchman → KnowledgeGraph | P0 | Violations werden nicht persistiert |
| KnowledgeGraph → Manas | P0 | Dojo lernt nicht aus echten Violations |
| Shuddhi → Synapse Feedback | P1 | Kein Reinforcement nach Healing |
| Genesis Remedy Generator | P2 | System kann keine neuen Remedies schreiben |
| Diamond Test Generation | P2 | Keine automatischen Tests |

---

## 3. ROADMAP (Die 5 Brücken)

### Phase 1: Watchman → Knowledge Graph Bridge (P0)

**Ziel:** Violations werden als Nodes im Knowledge Graph gespeichert.

**Dateien zu ändern:**
- `vibe_core/cartridges/system/watchman/cartridge_main.py`
- `vibe_core/knowledge/graph.py` (add_violation method)

**Implementation:**
```python
# In Watchman nach Violation Detection:
from vibe_core.knowledge.schema import NodeType, Node

def _record_violation(self, violation: Violation) -> None:
    """Persist violation to Knowledge Graph."""
    node = Node(
        id=f"violation_{violation.file}_{violation.rule_id}_{timestamp}",
        type=NodeType.VIOLATION,
        name=violation.rule_id,
        domain="shuddhi",
        properties={
            "file": str(violation.file),
            "line": violation.line,
            "rule_id": violation.rule_id,
            "message": violation.message,
            "has_remedy": violation.has_remedy,
            "detected_at": datetime.now().isoformat(),
        }
    )
    self.knowledge_graph.add_node(node)
```

**Synapse Message senden:**
```python
# Notify Manas about new violation
synapse.emit(SynapseMessage(
    topic="violation.detected",
    payload={"violation_id": node.id, "rule_id": violation.rule_id}
))
```

**Verifizierung:**
```bash
# Test: Violation wird gespeichert
python -c "
from vibe_core.knowledge.graph import KnowledgeGraph
kg = KnowledgeGraph()
violations = kg.get_nodes_by_type(NodeType.VIOLATION)
print(f'Stored violations: {len(violations)}')
"
```

---

### Phase 2: Knowledge Graph → Manas Dojo Connection (P0)

**Ziel:** Manas Mirror Room liest Violations und generiert Gap-Training.

**Dateien zu ändern:**
- `vibe_core/plugins/opus_assistant/manas/dojo/rooms/mirror.py`
- `vibe_core/plugins/opus_assistant/manas/dojo/curriculum_loader.py`

**Implementation:**
```python
# In Mirror Room:
def analyze_violations(self) -> GapAnalysis:
    """Analyze stored violations for training gaps."""
    kg = ServiceRegistry.get(KnowledgeGraphProtocol)
    violations = kg.get_nodes_by_type(NodeType.VIOLATION)

    # Group by rule_id
    by_rule = defaultdict(list)
    for v in violations:
        by_rule[v.properties["rule_id"]].append(v)

    # Generate training scenarios for frequent violations
    gaps = []
    for rule_id, instances in by_rule.items():
        if len(instances) >= 3:  # Threshold for pattern
            gaps.append(GapInfo(
                pattern=f"violation:{rule_id}",
                confidence=0.3,  # Low = needs training
                recommendation=f"Train on {rule_id} detection"
            ))

    return GapAnalysis(gaps=gaps)
```

**Curriculum Generation:**
```python
# Auto-generate curriculum from violations
def generate_violation_curriculum(violations: List[Node]) -> Dict:
    """Create Dojo curriculum from real violations."""
    return {
        "id": f"violation_training_{date}",
        "name": "Violation Pattern Training",
        "scenarios": [
            {
                "trigger": f"detect:{v.properties['rule_id']}",
                "expected_action": "flag_violation",
                "context": {"file": v.properties["file"]}
            }
            for v in violations[:10]  # Top 10
        ]
    }
```

**Verifizierung:**
```bash
# Test: Mirror sieht Violations
python -c "
from vibe_core.plugins.opus_assistant.manas.dojo.rooms.mirror import Mirror
mirror = Mirror()
analysis = mirror.analyze_violations()
print(f'Found {len(analysis.gaps)} training gaps from violations')
"
```

---

### Phase 3: Shuddhi → Synapse Feedback (P1)

**Ziel:** Nach erfolgreichem Healing wird Synapse Weight verstärkt.

**Dateien zu ändern:**
- `vibe_core/shuddhi/engine.py`
- `vibe_core/plugins/opus_assistant/manas/cortex/viveka_action.py`

**Implementation:**
```python
# In ShuddhiEngine.purify() nach SUCCESS:
def purify(self, file_path: Path, rule_id: str) -> ShuddhiResult:
    # ... existing logic ...

    if result.status == ShuddhiStatus.PURIFIED:
        # Reinforce synapse: "healing X works"
        self._emit_healing_feedback(rule_id, success=True)

        # Record HEALED_BY relation
        self._record_healed_relation(file_path, rule_id)

    return result

def _emit_healing_feedback(self, rule_id: str, success: bool) -> None:
    """Send feedback to strengthen/weaken synapses."""
    synapse = get_synapse_safe("shuddhi")
    synapse.emit(SynapseMessage(
        topic="healing.completed",
        payload={
            "rule_id": rule_id,
            "success": success,
            "weight_delta": 0.1 if success else -0.1
        }
    ))
```

**In VivekaAction (Synapse Consumer):**
```python
def on_healing_feedback(self, message: SynapseMessage) -> None:
    """Adjust synapse weights based on healing outcome."""
    rule_id = message.payload["rule_id"]
    delta = message.payload["weight_delta"]

    # Strengthen pattern: "trigger:violation:{rule_id}" → "action:heal"
    pattern = f"trigger:violation:{rule_id}"
    action = "action:heal"

    self.adjust_weight(pattern, action, delta)
```

**Verifizierung:**
```bash
# Test: Synapse weights change after healing
python -c "
from vibe_core.shuddhi.engine import ShuddhiEngine
from pathlib import Path

# Create test violation
test_file = Path('/tmp/test.py')
test_file.write_text('import subprocess; subprocess.run([\"ls\"])')

engine = ShuddhiEngine()
result = engine.purify(test_file, 'subprocess_timeout')

# Check synapse was updated
# (would need to read synapse store)
print(f'Healed: {result.status}')
"
```

---

### Phase 4: Genesis Remedy Generator (P2)

**Ziel:** System kann neue CSTRemedy Klassen automatisch generieren.

**Dateien zu erstellen:**
- `vibe_core/shuddhi/remedy_generator.py`

**Konzept:**
```python
class RemedyGenerator:
    """
    Generates new CSTRemedy classes from violation patterns.

    Uses LLM (via Manas) to:
    1. Analyze repeated violation patterns
    2. Generate CST transformation code
    3. Write new remedy file
    4. Register via RemedyLoader
    """

    def generate_from_violations(self, rule_id: str, examples: List[Violation]) -> Path:
        """Generate a new remedy from violation examples."""
        # 1. Extract pattern from examples
        pattern = self._extract_pattern(examples)

        # 2. Generate CST transformation via LLM
        code = self._generate_remedy_code(rule_id, pattern)

        # 3. Write to remedies directory
        remedy_path = Path(f"vibe_core/shuddhi/remedies/{rule_id}.py")
        remedy_path.write_text(code)

        # 4. Trigger reload
        get_remedy_loader().clear_cache()

        return remedy_path
```

**Integration mit Genesis Service:**
```python
# Genesis spawns new remedy via DNA template
genesis = ServiceRegistry.get(GenesisProtocol)
dna = genesis.create_dna(
    template="shuddhi_remedy",
    params={"rule_id": "new_pattern", "transformation": "..."}
)
```

**Verifizierung:**
```bash
# Test: System generates new remedy
python -c "
from vibe_core.shuddhi.remedy_generator import RemedyGenerator
gen = RemedyGenerator()
path = gen.generate_from_violations('test_rule', examples)
print(f'Generated: {path}')
"
```

---

### Phase 5: Diamond Test Generation (P2)

**Ziel:** Automatische Test-Generierung für geheilten Code.

**Konzept:**
```python
class DiamondTestGenerator:
    """
    Generates tests for healed code following Diamond Protocol.

    TDD Loop:
    1. Violation detected
    2. Generate failing test (RED)
    3. Shuddhi heals code
    4. Test passes (GREEN)
    5. Refactor if needed
    """

    def generate_test(self, violation: Violation, healed_result: ShuddhiResult) -> str:
        """Generate test that verifies the healing."""
        return f'''
def test_{violation.rule_id}_healed():
    """Verify {violation.rule_id} is properly healed."""
    # Original code had violation
    # Healed code should pass Watchman inspection

    from vibe_core.cartridges.system.watchman.tools.standards_inspection import StandardsInspectionTool

    tool = StandardsInspectionTool()
    result = tool.inspect_file(Path("{violation.file}"))

    # Should have no violations for this rule
    violations = [v for v in result.violations if v.rule_id == "{violation.rule_id}"]
    assert len(violations) == 0, f"Still has {violation.rule_id} violations"
'''
```

---

## 4. VERIFIZIERUNG (Definition of Done)

### Pro Phase:

| Phase | Verifizierung | Command |
|-------|---------------|---------|
| 1 | Violations im KG | `kg.get_nodes_by_type(VIOLATION)` returns > 0 |
| 2 | Mirror sieht Gaps | `mirror.analyze_violations()` returns gaps |
| 3 | Synapses updated | Weight für healing pattern > 0.5 |
| 4 | Neue Remedy generiert | `discover_remedies()` enthält generated |
| 5 | Tests generiert | Test files in tests/ directory |

### Gesamt:

```bash
# Full Ouroboros Loop Test
python -c "
# 1. Create violation
# 2. Watchman detects → stores in KG
# 3. Manas reads → creates training
# 4. Shuddhi heals → sends feedback
# 5. Synapse strengthened
# 6. Next time: faster detection + healing

from vibe_core.ouroboros import OuroborosLoop
loop = OuroborosLoop()
result = loop.run_cycle()
assert result.violations_healed > 0
assert result.synapses_updated > 0
print('Ouroboros Loop: WORKING')
"
```

---

## 5. NÄCHSTE SCHRITTE

1. **JETZT:** Dieses Dokument committen und pushen
2. **DANN:** Phase 1 starten (Watchman → Knowledge Graph)
3. **DANACH:** Phase 2 (Knowledge Graph → Manas Dojo)

---

## 6. DATEIEN ZU ÄNDERN (Übersicht)

```
vibe_core/
├── cartridges/system/watchman/
│   └── cartridge_main.py          # ADD: _record_violation()
├── knowledge/
│   └── graph.py                   # ADD: add_violation(), get_violations()
├── plugins/opus_assistant/manas/
│   ├── dojo/rooms/mirror.py       # ADD: analyze_violations()
│   ├── dojo/curriculum_loader.py  # ADD: generate_violation_curriculum()
│   └── cortex/viveka_action.py    # ADD: on_healing_feedback()
├── shuddhi/
│   ├── engine.py                  # ADD: _emit_healing_feedback()
│   └── remedy_generator.py        # NEW: RemedyGenerator class
└── ouroboros.py                   # NEW: OuroborosLoop orchestrator
```

---

## 7. REFERENZEN

- `REPORT.md` - Aktueller Score und Violations
- `config/standards.yaml` - Regel-Definitionen mit has_sattva_remedy
- `vibe_core/knowledge/schema.py` - NodeType.VIOLATION, REMEDY
- `vibe_core/protocols/shuddhi.py` - ShuddhiProtocol, RemedyProtocol
- `vibe_core/plugins/opus_assistant/manas/dojo/` - Training System

---

**"Das System heilt sich selbst. Das ist OUROBOROS."**

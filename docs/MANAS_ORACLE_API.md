# OPUS-089: MANAS Oracle API

## Übersicht

Die **MANAS Oracle API** ist eine **saubere Schnittstelle für Separation of Concerns**, die das Cognitive Kernel von MANAS als "Wisdom Service" für den Rest des Systems exponiert.

### Problem gelöst:
- ❌ Vorher: MANAS war ein isoliertes Plugin mit eigenem Lifecycle
- ✅ Nachher: MANAS ist ein **System Agent** mit einer klaren **Oracle-Schnittstelle**

### Architektur:
```
┌─────────────────────────────────────────────────┐
│         MANAS Oracle Wisdom Interface            │
├─────────────────────────────────────────────────┤
│                                                 │
│  consult(context) → AnalysisResult             │
│  pre_analysis(task_context) → Gate Decision     │
│  post_analysis(task_result) → Learning Record   │
│                                                 │
│  Andere System-Agenten rufen diese auf.        │
│  Keine direkte Abhängigkeit.                    │
│  Nur Interface-basierte Kommunikation.          │
│                                                 │
└─────────────────────────────────────────────────┘
         ↓
    [Heartbeat, Envoy, Herald, ...]
    Alle können MANAS konsultieren
```

## API Referenz

### 1. `ManasOracle()` - Initialisierung

```python
from vibe_core.plugins.opus_assistant.manas.api import ManasOracle

oracle = ManasOracle()
```

Erstellt eine neue Oracle-Instanz mit den Standard-Konfigurationen.

### 2. `consult(context)` - Hauptmethode für Konsultation

**Unterschrift:**
```python
def consult(self, context: Dict[str, Any]) -> AnalysisResult:
```

**Parameter:**
```python
context = {
    "task_title": str,           # Was wird gemacht?
    "task_type": str,            # Typ (deploy, test, doc_update, etc.)
    "risk_level": str,           # "low", "medium", "high", "critical"
    "changes": List[str],        # Betroffene Dateien/Komponenten
    "is_automated": bool,        # Ist das ein automatisierter Task?
    "user_approval": bool,       # Hat ein Mensch das genehmigt?
}
```

**Return: `AnalysisResult`**
```python
@dataclass
class AnalysisResult:
    priority: IntentPriority      # CRITICAL, HIGH, MEDIUM, LOW
    safety_score: float           # 0.0-1.0: Wie sicher ist das?
    confidence: float             # 0.0-1.0: Wie sicher ist MANAS?

    advice: str                   # Menschenlesbarer Rat
    suggested_action: str         # "EXECUTE_NOW", "REQUEST_APPROVAL", "BLOCK_AND_REVIEW"
    risks: List[str]              # Identifizierte Risiken
    precautions: List[str]        # Vorgeschlagene Vorsichtsmaßnahmen

    manas_reasoning: Dict         # Debug: Warum hat MANAS so entschieden?
```

**Beispiel:**
```python
oracle = ManasOracle()

context = {
    "task_title": "Deploy to production",
    "task_type": "deploy",
    "risk_level": "high",
    "changes": ["main.py", "config.yaml"],
    "is_automated": False,
    "user_approval": True,
}

result = oracle.consult(context)

print(f"Priority: {result.priority}")
print(f"Safety: {result.safety_score:.0%}")
print(f"Advice: {result.advice}")
print(f"Risks: {result.risks}")
print(f"Precautions: {result.precautions}")
```

### 3. `pre_analysis(task_context)` - Gating vor Ausführung

Wird **VOR** der Task-Ausführung aufgerufen. Entscheidet, ob ein Task überhaupt durchgeführt werden soll.

**Unterschrift:**
```python
def pre_analysis(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
```

**Return:**
```python
{
    "proceed": bool,              # Soll der Task ausgeführt werden?
    "reason": str,                # Warum oder warum nicht?
    "safety_score": float,        # Die berechnete Sicherheit
    "recommendation": AnalysisResult  # Full analysis
}
```

**Beispiel (in heartbeat.py):**
```python
gate = oracle.pre_analysis({
    "task_title": "Deploy to production",
    "task_type": "deploy",
    "risk_level": "high",
    "is_automated": True,
    "user_approval": False,
})

if gate["proceed"]:
    unified_router.execute(task)
else:
    logger.warning(f"Task blocked: {gate['reason']}")
    task_manager.update_task(task_id, status=TaskStatus.BLOCKED)
```

### 4. `post_analysis(task_result)` - Lernen nach Ausführung

Wird **NACH** der Task-Ausführung aufgerufen. MANAS aktualisiert sein Memory basierend auf dem Ergebnis.

**Unterschrift:**
```python
def post_analysis(self, task_result: Dict[str, Any]) -> Dict[str, Any]:
```

**Parameter:**
```python
task_result = {
    "task_type": str,             # Art des Tasks
    "success": bool,              # Ist es erfolgreich gewesen?
    "error": Optional[str],       # Fehlermeldung, falls applicable
    "duration_ms": float,         # Wie lange hat es gedauert?
}
```

**Return:**
```python
{
    "recorded": bool,             # Wurde das in der Memory gespeichert?
    "task_type": str,
    "success": bool,
}
```

**Beispiel:**
```python
result = oracle.post_analysis({
    "task_type": "deploy",
    "success": True,
    "error": None,
    "duration_ms": 1250,
})

if result["recorded"]:
    print(f"✅ MANAS learned from {result['task_type']}")
```

## Integration in den Heartbeat

In `scripts/heartbeat.py`:

```python
from vibe_core.plugins.opus_assistant.manas.api import ManasOracle, ManasConfig

class HeartbeatEngine:
    def __init__(self, project_root: Path):
        # ... existing init ...

        # OPUS-089: Initialize MANAS Oracle
        self.manas_oracle = ManasOracle(
            config=ManasConfig(thinking_interval_minutes=15)
        )

    def _execute_tasks(self):
        """Execute pending tasks with MANAS Oracle gating."""
        next_task = self.task_manager.get_next_task()

        if not next_task:
            return

        # ===== PRE-ANALYSIS GATE =====
        if self.manas_oracle:
            gate = self.manas_oracle.pre_analysis({
                "task_title": next_task.title,
                "task_type": "generic_task",
                "risk_level": "medium",
                "is_automated": True,
                "user_approval": False,
            })

            if not gate["proceed"]:
                logger.warning(f"Task blocked: {gate['reason']}")
                self.task_manager.update_task(
                    next_task.id,
                    status=TaskStatus.BLOCKED,
                    metadata={"blocked_by": "manas_oracle"}
                )
                return

        # ... execute task ...

        # ===== POST-ANALYSIS LEARNING =====
        if self.manas_oracle:
            self.manas_oracle.post_analysis({
                "task_type": "generic_task",
                "success": result.get("status") == "completed",
                "error": result.get("error"),
            })
```

## Safety Heuristics

MANAS berechnet `safety_score` basierend auf:

1. **Risk Level** (Basis):
   - `low` → 95% safety
   - `medium` → 70% safety
   - `high` → 40% safety
   - `critical` → 10% safety

2. **Boosts & Penalties**:
   - ✅ `user_approval: true` → +15% safety
   - ❌ `is_automated: true` + `high/critical` + no approval → -20% safety

3. **Historical Confidence**:
   - Basierend auf Success Rate ähnlicher Tasks in der Memory
   - Mehr Success → höhere Confidence

## Error Handling

Die Oracle ist **resilient by design**:

- ✅ Ungültige Kontexte werden mit sicheren Defaults behandelt
- ✅ Interne Fehler lösen NICHT Exceptions aus
- ✅ Immer ein `AnalysisResult` zurückgeben, niemals `None`

```python
try:
    result = oracle.consult(invalid_context)
    # Fallback: result mit safety_score=0.5, confidence=0.3
    # Nicht: Exception
except Exception:
    pass  # Won't happen - Oracle handles it internally
```

## Testing

Tests sind in `tests/unit/test_manas_oracle_api.py`:

```bash
cd /Users/ss/Downloads/steward-protocol
python -m pytest tests/unit/test_manas_oracle_api.py -v
```

### Test-Suites:

1. **TestManasOracleBasics**: Grundfunktionalität
2. **TestManasOracleAPIs**: Die drei Hauptmethoden
3. **TestManasOracleRiskIdentification**: Risk-Detection-Logik
4. **TestManasOracleMemoryIntegration**: Learning-Mechanismus
5. **TestManasOracleErrorHandling**: Resilience

## Verwendungsbeispiele

### Beispiel 1: Einfacher Konsultation
```python
oracle = ManasOracle()

# "Soll ich diesen Doc-Update machen?"
result = oracle.consult({
    "task_title": "Update README.md",
    "task_type": "doc_update",
    "risk_level": "low",
    "changes": ["README.md"],
    "is_automated": False,
    "user_approval": True,
})

if result.safety_score >= 0.90:
    print("✅ Go ahead!")
    # Execute task
```

### Beispiel 2: Pre-Gate vor Production Deploy
```python
oracle = ManasOracle()

context = {
    "task_title": "Deploy v2.3.0 to production",
    "task_type": "deploy",
    "risk_level": "high",
    "changes": ["main.py", "database.sql"],
    "is_automated": False,
    "user_approval": True,  # Human approved
}

gate = oracle.pre_analysis(context)

if gate["proceed"] and gate["safety_score"] >= 0.70:
    print("🟢 Deploying...")
    deploy_result = execute_deploy()

    # Learn from outcome
    oracle.post_analysis({
        "task_type": "deploy",
        "success": deploy_result.success,
        "error": deploy_result.error,
        "duration_ms": deploy_result.duration,
    })
else:
    print(f"🔴 Deploy blocked: {gate['reason']}")
```

## Architektur-Prinzipien

1. **Separation of Concerns**: ManasOracle ist eine **Schnittstelle**, nicht eine Implementierung
2. **No Spaghetti**: Andere Agenten rufen die API auf, nicht direkt auf MANAS
3. **Stateful Learning**: Die Memory speichert Erfolgsraten und Muster
4. **Deterministic**: Gleiche Eingabe → gleiche Ausgabe (kein Randomness)
5. **Traceable**: Alle Entscheidungen include "Reasoning" für Debugging

## Siehe auch

- `vibe_core/plugins/opus_assistant/manas/api.py` - API implementation
- `vibe_core/plugins/opus_assistant/manas/cognitive_kernel.py` - Kernel
- `scripts/heartbeat.py` - Integration in Heartbeat
- `OPUS.md` - OPUS-089 Specification

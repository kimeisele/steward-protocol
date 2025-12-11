# WIRING ROADMAP - Complete System Integration

> **Created:** 2025-12-04 by Opus (Senior Audit)
> **Purpose:** Systematisches Fixen aller kaputten Kabel
> **Execution:** Sonnet/Haiku können jeden Task selbstständig abarbeiten

---

## Executive Summary

Das System ist zu ~80% gebaut. Die Architektur ist solide. Aber die **letzten 20% fehlen** - die Kabel zwischen den Komponenten sind nicht richtig verbunden. Tasks werden klassifiziert aber nicht ausgeführt. Stubs simulieren statt zu handeln.

**Ziel:** Von "würde tun" zu "tut es wirklich"

---

## Priority 1: KRITISCHE WIRING-FEHLER

### P1.1 EnvoyCartridge → MilkOceanRouter Verbindung

**Problem:** `await self.router.route()` - Methode existiert nicht
**Datei:** `steward/system_agents/envoy/cartridge_main.py:183`
**Impact:** CRASH bei jedem Aufruf über diesen Pfad

**Fix:**
```python
# VORHER (Zeile 183):
routing_decision = await self.router.route(user_input)

# NACHHER:
routing_decision = self.router.process_prayer(
    user_input=user_input,
    agent_id="envoy",
    critical=False
)
```

**Dann:** Die Routing-Entscheidung muss gehandelt werden (siehe P1.2)

---

### P1.2 Routing-Entscheidung → Echte Ausführung

**Problem:** `process_prayer()` gibt nur Routing-Entscheidung zurück, niemand führt aus
**Datei:** `steward/system_agents/envoy/cartridge_main.py:192-205`
**Impact:** Tasks werden klassifiziert aber NIE ausgeführt

**Aktuelle Logik (kaputt):**
```python
if routing_decision.get("route") == "EXECUTE_CIRCUIT":
    result = await self.executor.execute(...)
```

**Problem:** `process_prayer()` gibt `{"path": "flash"}` oder `{"path": "science"}` zurück, nicht `{"route": "EXECUTE_CIRCUIT"}`

**Fix - Komplette process() Methode nach Zeile 180:**
```python
# 2. Route via MilkOcean (Classification)
logger.info(f"🧠 Routing via MilkOcean: {user_input}")
routing_decision = self.router.process_prayer(
    user_input=user_input,
    agent_id="envoy",
    critical=False
)

# 3. Handle Routing Decision
status = routing_decision.get("status")
path = routing_decision.get("path")

if status == "blocked":
    return {"status": "blocked", "reason": routing_decision.get("reason")}

elif status == "queued":
    # Lazy queue - return acknowledgment
    return {"status": "queued", "request_id": routing_decision.get("request_id")}

elif status == "routing":
    # Execute based on path
    if path == "flash":
        # Simple queries - use DeterministicExecutor with simple playbook
        result = await self.executor.execute(
            playbook_id="SIMPLE_QUERY",
            user_input=user_input,
            intent_vector=routing_decision.get("details"),
            kernel=self.kernel,
        )
        return result

    elif path == "science":
        # Complex queries - submit to SCIENCE agent via kernel
        from vibe_core.scheduling.task import Task
        task = Task(agent_id="science", payload={"query": user_input})
        task_id = self.kernel.submit_task(task)
        return {"status": "delegated", "agent": "science", "task_id": task_id}

# Fallback
return {"status": "error", "error": "Unknown routing path"}
```

---

### P1.3 Heartbeat False-Positive Completion

**Problem:** Tasks als COMPLETED markiert obwohl nur Routing passiert
**Datei:** `scripts/heartbeat.py:220-228`
**Impact:** Task-Tracking ist komplett falsch

**VORHER:**
```python
if result.get("status") == "blocked":
    self.task_manager.update_task(next_task.id, status=TaskStatus.BLOCKED)
else:
    # Task routed successfully - mark as completed  <-- FALSCH!
    self.task_manager.update_task(next_task.id, status=TaskStatus.COMPLETED)
```

**NACHHER:**
```python
status = result.get("status")

if status == "blocked":
    self.task_manager.update_task(next_task.id, status=TaskStatus.BLOCKED)

elif status == "queued":
    # Task is in lazy queue - keep as IN_PROGRESS
    logger.info("   📋 Task queued for later processing")
    # Don't change status - stays IN_PROGRESS

elif status == "delegated":
    # Task delegated to agent - track the agent task
    logger.info(f"   🔄 Task delegated to {result.get('agent')}")
    self.task_manager.update_task(
        next_task.id,
        metadata={
            **next_task.metadata,
            "delegated_task_id": result.get("task_id"),
            "delegated_to": result.get("agent"),
        }
    )
    # Don't mark complete - agent hasn't finished yet

elif status == "COMPLETED":
    # Only mark complete if executor actually completed
    self.task_manager.update_task(next_task.id, status=TaskStatus.COMPLETED)

else:
    # Unknown status - log warning, keep IN_PROGRESS
    logger.warning(f"   ⚠️ Unknown status: {status}")
```

---

## Priority 2: STUBS ZU ECHTER IMPLEMENTIERUNG

### P2.1 Action Handlers Live-Schalten

**Datei:** `steward/system_agents/envoy/action_handlers.py`

#### P2.1a: _create_folders (Zeile 305-320)

**VORHER:**
```python
logger.info(f"    📁 Would create: {folder_path}")
created.append(str(folder_path))
```

**NACHHER:**
```python
folder_path.mkdir(parents=True, exist_ok=True)
logger.info(f"    📁 Created: {folder_path}")
created.append(str(folder_path))
```

#### P2.1b: _init_git (Zeile 322-330)

**VORHER:**
```python
logger.info(f"    🔧 Would init git at: {repo_path}")
```

**NACHHER:**
```python
import subprocess
repo = Path(repo_path)
if not (repo / ".git").exists():
    subprocess.run(["git", "init", "-b", initial_branch], cwd=repo, check=True)
    logger.info(f"    🔧 Initialized git at: {repo_path}")
else:
    logger.info(f"    🔧 Git already exists at: {repo_path}")
```

#### P2.1c: _write_file (Zeile 332-343)

**VORHER:**
```python
logger.info(f"    📝 Would write to: {file_path}")
```

**NACHHER:**
```python
path = Path(file_path)
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(content)
logger.info(f"    📝 Wrote to: {file_path} ({len(content)} chars)")
```

#### P2.1d: _read_file (Zeile 345-355)

**VORHER:**
```python
return ActionResult.ok({"content": f"[content of {file_path}]"})
```

**NACHHER:**
```python
path = Path(file_path)
if not path.exists():
    return ActionResult.fail(f"File not found: {file_path}")
content = path.read_text()
return ActionResult.ok({"path": file_path, "content": content})
```

---

### P2.2 Lazy Queue Worker Live-Schalten

**Datei:** `steward/system_agents/envoy/tools/milk_ocean.py:877-883`

**VORHER:**
```python
# result = kernel.route_and_execute(user_input)
# Mock result for now
result = {
    "status": "completed",
    "message": f"Processed queue request: {user_input[:50]}",
}
```

**NACHHER:**
```python
# Execute via kernel
try:
    from vibe_core.scheduling.task import Task
    task = Task(agent_id="envoy", payload={"input": user_input})
    task_id = kernel.submit_task(task)

    # Wait for completion (with timeout)
    import time
    for _ in range(60):  # 60 second timeout
        kernel.tick()
        task_result = kernel.get_task_result(task_id)
        if task_result:
            result = task_result
            break
        time.sleep(1)
    else:
        result = {"status": "timeout", "message": "Task execution timed out"}
except Exception as e:
    result = {"status": "error", "error": str(e)}
```

---

## Priority 3: FEHLENDE PLAYBOOKS/CIRCUITS

### P3.1 SIMPLE_QUERY Circuit fehlt

Der EnvoyCartridge versucht `SIMPLE_QUERY` Playbook zu laden, aber es existiert möglicherweise nicht.

**Prüfen:** `ls vibe_core/playbook/circuits/`

**Falls fehlend, erstellen:** `vibe_core/playbook/circuits/simple_query.yaml`
```yaml
circuit:
  id: SIMPLE_QUERY
  description: Handle simple informational queries
  domain: INTERFACE
  version: "1.0.0"

  states:
    classify:
      name: "Classify Query"
      description: "Determine query type"
      actions:
        - action_type: EMIT_EVENT
          target: "query_classified"
          params:
            type: "simple"
      on_success: respond
      on_failure: ABORT

    respond:
      name: "Generate Response"
      description: "Generate appropriate response"
      actions:
        - action_type: CALL_AGENT
          target: "herald"
          params:
            action: "respond"
            query: "{{ user_input }}"
      on_success: COMPLETE
      on_failure: ABORT
```

---

## Priority 4: INTEGRATION TESTS

Nach jedem Fix sollte getestet werden:

### P4.1 Test: EnvoyCartridge → Router → Executor

```python
# tests/integration/test_envoy_wiring.py

import pytest
from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge
from vibe_core.scheduling.task import Task

@pytest.mark.asyncio
async def test_envoy_routes_and_executes():
    """Test that Envoy actually executes tasks, not just routes them."""
    envoy = EnvoyCartridge()
    # Mock kernel for testing
    envoy.kernel = MockKernel()

    task = Task(
        task_id="test_001",
        agent_id="envoy",
        payload={"input": "What is the status?"}
    )

    result = await envoy.process(task)

    # Should NOT just be "routing" - should be actual result
    assert result["status"] != "routing"
    assert "status" in result or "error" in result
```

### P4.2 Test: Heartbeat Completion Logic

```python
# tests/integration/test_heartbeat_completion.py

def test_heartbeat_does_not_false_complete():
    """Ensure heartbeat doesn't mark tasks complete prematurely."""
    engine = HeartbeatEngine(project_root)

    # Add a task
    task = engine.task_manager.add_task(title="Test task")

    # Run pulse
    engine.pulse()

    # Task should NOT be completed if it was just routed
    updated_task = engine.task_manager.get_task(task.id)
    # If task is still pending/in_progress, that's correct
    # If task is "completed" but no actual work was done, that's a bug
```

---

## Execution Order

1. **P1.1** - Fix `route()` → `process_prayer()` (5 min)
2. **P1.2** - Handle routing decision properly (30 min)
3. **P1.3** - Fix Heartbeat completion logic (15 min)
4. **P4.1** - Write integration test (15 min)
5. **P2.1a-d** - Live-schalten Action Handlers (20 min)
6. **P2.2** - Live-schalten Lazy Queue Worker (15 min)
7. **P3.1** - SIMPLE_QUERY Circuit erstellen falls nötig (10 min)
8. **P4.2** - Heartbeat test (10 min)

**Total: ~2 Stunden Sonnet-Arbeit**

---

## Verification Checklist

Nach Abschluss aller Fixes:

- [ ] `python -c "from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge; e = EnvoyCartridge(); print('OK')"` läuft ohne Error
- [ ] `python scripts/heartbeat.py` führt Tasks aus (nicht nur klassifizieren)
- [ ] Action Handlers erstellen echte Dateien/Ordner
- [ ] Tasks werden erst COMPLETED wenn echte Arbeit getan wurde
- [ ] Integration tests grün

---

## Notes for Sonnet

1. **Immer zuerst die Datei lesen** bevor du editierst
2. **Zeilennummern können sich verschoben haben** - suche nach dem Code-Pattern
3. **Teste nach jedem Fix** mit einem Quick-Check
4. **Committe nach jedem Priority-Block** (P1, P2, etc.)
5. **Bei Unklarheiten:** Die Architektur-Dokumente in `docs/architecture/` haben Kontext

---

*This roadmap was generated by Opus Senior Audit. Execute sequentially for best results.*

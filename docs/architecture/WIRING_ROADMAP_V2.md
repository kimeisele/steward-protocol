# WIRING ROADMAP V2 - Deep System Integration

> **Created:** 2025-12-04 by Opus (Senior Audit Sprint #2)
> **Previous:** WIRING_ROADMAP.md (P1 fixes implemented by Sonnet)
> **Status:** P1 DONE, P2 DONE → Now P3+ (Deeper Integration)

---

## Summary of P1/P2 Progress

**COMPLETED:**
- [x] P1.1: EnvoyCartridge → process_prayer() fix
- [x] P1.2: Handle routing decision properly
- [x] P1.3: Heartbeat completion logic (catches "routing" status)
- [x] P2.1: Action Handlers live-geschaltet
- [x] P2.2: Lazy Queue Worker live-geschaltet

**NEW FINDINGS (this audit):**

---

## P3: CRITICAL - Kernel Injection Missing

### P3.1 Agent.kernel = None (CRITICAL BUG)

**Problem:** Agents use `self.kernel` but it's never injected!

**Evidence:**
```python
# vibe_core/protocols/agent.py:112
self.kernel = None  # Will be injected by VibeKernel.boot()

# vibe_core/protocols/agent.py:119-129
def set_kernel(self, kernel: VibeKernel) -> None:
    """Called by VibeKernel.boot() to give agents access to kernel"""
    self.kernel = kernel
```

**BUT in kernel_impl.py:register_agent():**
```python
# Line 735 - System interface IS injected
agent.system = AgentSystemInterface(self, agent.agent_id)

# Line ??? - set_kernel() is NEVER called!
# agent.set_kernel(self)  ← MISSING!
```

**Affected Agents (all use self.kernel):**
- `steward/system_agents/envoy/cartridge_main.py:212` → `self.kernel.submit_task()`
- `steward/system_agents/supreme_court/cartridge_main.py:547` → `self.kernel.ledger`
- `steward/system_agents/forum/cartridge_main.py:302` → `self.kernel.ledger`
- `steward/system_agents/discoverer/agent.py:142` → `self.kernel.agent_registry`
- `steward/system_agents/envoy/blueprint_generator.py:775` → `self.kernel.process_with_llm()`
- `steward/system_agents/envoy/tools/run_campaign_tool.py:297` → `self.kernel.get_agent()`
- `steward/system_agents/envoy/tools/city_control_tool.py:474` → `self.kernel.agent_registry`

**Fix:**
```python
# vibe_core/kernel_impl.py - In register_agent(), add BEFORE line 735:

# STEP 4.6: INJECT KERNEL REFERENCE (Legacy Pattern)
# Many agents use self.kernel directly. Keep backward compatibility.
agent.set_kernel(self)
logger.debug(f"🔗 Agent '{agent.agent_id}' received kernel reference")

# PHASE 1.1: INJECT SYSTEM INTERFACE (The Bridge)
agent.system = AgentSystemInterface(self, agent.agent_id)
```

**Location:** `vibe_core/kernel_impl.py:728` (insert before line 728)

---

### P3.2 MilkOceanRouter has no Kernel

**Problem:** MilkOceanRouter is initialized without kernel, but lazy_queue_worker needs it.

**Evidence:**
```python
# steward/system_agents/envoy/cartridge_main.py:100
self.router = MilkOceanRouter()  # No kernel!

# steward/system_agents/envoy/tools/milk_ocean.py:312
def __init__(self, kernel=None):
    self.kernel = kernel  # Is None!
```

**Fix Option A (in EnvoyCartridge.__init__):**
```python
# After kernel is available (in process() or via property):
if self.kernel and not self.router.kernel:
    self.router.set_kernel(self.kernel)
```

**Fix Option B (Lazy kernel access in MilkOceanRouter):**
```python
def _get_kernel(self):
    """Lazy kernel access - try to get from parent if not set."""
    if self.kernel:
        return self.kernel
    # Try to import running kernel
    try:
        from vibe_core.kernel_impl import RealVibeKernel
        # Would need singleton pattern or global reference
    except:
        pass
    return None
```

**Recommendation:** Fix Option A is cleaner. Add kernel injection after agent registration.

---

## P4: ROUTING PATH GAPS

### P4.1 Only "flash" and "science" paths handled

**Problem:** EnvoyCartridge only handles 2 routing paths.

**Evidence:**
```python
# steward/system_agents/envoy/cartridge_main.py:195-213
elif status == "routing":
    if path == "flash":
        # ...
    elif path == "science":
        # ...
# What about path == "lazy"? path == "critical"? Other paths?
```

**MilkOceanRouter returns these paths:**
- `"flash"` - Simple queries
- `"science"` - Complex queries
- `"lazy"` - Goes to queue (status="queued", not "routing")
- `"kernel_direct"` - Critical priority (status="critical")

**Fix:**
```python
elif status == "routing":
    if path == "flash":
        # Simple - use executor
        result = await self.executor.execute(...)
        return result

    elif path == "science":
        # Complex - delegate to science agent
        task = Task(agent_id="science", payload={"query": user_input})
        task_id = self.kernel.submit_task(task)
        return {"status": "delegated", "agent": "science", "task_id": task_id}

    else:
        # Unknown path - log warning and use flash as fallback
        logger.warning(f"Unknown routing path '{path}', using flash fallback")
        result = await self.executor.execute(
            playbook_id="SIMPLE_QUERY",
            user_input=user_input,
            intent_vector=routing_decision.get("details"),
            kernel=self.kernel,
        )
        return result

elif status == "critical":
    # GAJENDRA PROTOCOL - Emergency kernel bypass
    logger.warning("🐘 CRITICAL PRIORITY - Direct kernel execution")
    # Execute immediately with highest priority
    task = Task(agent_id="envoy", payload={"input": user_input, "critical": True})
    task_id = self.kernel.submit_task(task)
    return {"status": "critical_handled", "task_id": task_id}
```

---

### P4.2 Heartbeat doesn't handle "critical" status

**Problem:** Heartbeat only checks blocked/queued/delegated/routing/completed.

**Fix:**
```python
# scripts/heartbeat.py - Add after line 263:

elif status == "critical":
    # Critical tasks were handled with emergency priority
    logger.info("   🐘 CRITICAL task handled via Gajendra Protocol")
    self.task_manager.update_task(
        next_task.id,
        status=TaskStatus.COMPLETED,
        metadata={
            **next_task.metadata,
            "critical_handled": True,
            "protocol": "Gajendra",
        },
    )
```

---

## P5: HERALD Agent Missing in SIMPLE_QUERY

### P5.1 SIMPLE_QUERY calls Herald but Herald might not process it

**Evidence:**
```yaml
# vibe_core/playbook/circuits/simple_query.yaml:23-27
- action_type: CALL_AGENT
  target: "herald"
  params:
    action: "respond"
    query: "{{ user_input }}"
```

**Question:** Does Herald have a "respond" action?

**Check needed:**
```bash
grep -n "action.*respond" steward/system_agents/herald/cartridge_main.py
```

If Herald doesn't handle "respond", SIMPLE_QUERY will fail silently.

**Fix (if needed):**
Add "respond" action to Herald's process() method, or change SIMPLE_QUERY to use an action Herald supports.

---

## P6: SCIENCE Agent Async Mismatch

### P6.1 Science.process() is NOT async

**Problem:** EnvoyCartridge calls Science via kernel.submit_task(), but when the kernel calls Science.process(), it's not async.

**Evidence:**
```python
# steward/system_agents/science/cartridge_main.py:125
def process(self, task: Task) -> Dict[str, Any]:  # NOT async!
```

But most other agents have async process():
```python
# steward/system_agents/envoy/cartridge_main.py:131
async def process(self, task: Task) -> Dict[str, Any]:  # IS async
```

**Impact:** If kernel calls Science.process() in an async context, it might block.

**Fix:**
```python
# steward/system_agents/science/cartridge_main.py:125
async def process(self, task: Task) -> Dict[str, Any]:
    # ... (keep implementation, just add async)
```

---

## P7: Tool Kernel Injection

### P7.1 Tools use self.kernel but aren't injected

**Evidence:**
```python
# steward/system_agents/envoy/tools/city_control_tool.py:474
agent = self.kernel.agent_registry.get(agent_name)

# steward/system_agents/envoy/tools/run_campaign_tool.py:297
civic = self.kernel.get_agent("civic")
```

**How do Tools get kernel?** They should get it via their parent agent's system interface.

**Fix Pattern:**
```python
class CityControlTool(Tool):
    def __init__(self):
        self._kernel = None

    @property
    def kernel(self):
        if self._kernel is None:
            raise RuntimeError("Tool not initialized - kernel not injected")
        return self._kernel

    def set_kernel(self, kernel):
        self._kernel = kernel
```

Or use the agent's system interface:
```python
# In tool execution, access kernel via context
def execute(self, params, context):
    kernel = context.get("kernel")  # Passed from agent
```

---

## Execution Order

| # | Task | Priority | Estimated Time | Dependencies |
|---|------|----------|----------------|--------------|
| P3.1 | Add `agent.set_kernel(self)` in kernel_impl.py | CRITICAL | 5 min | None |
| P3.2 | Inject kernel into MilkOceanRouter | HIGH | 10 min | P3.1 |
| P4.1 | Handle all routing paths in EnvoyCartridge | HIGH | 15 min | P3.1 |
| P4.2 | Handle "critical" in Heartbeat | MEDIUM | 5 min | None |
| P5.1 | Verify Herald "respond" action | MEDIUM | 10 min | None |
| P6.1 | Make Science.process() async | MEDIUM | 5 min | None |
| P7.1 | Audit tool kernel injection | LOW | 30 min | P3.1 |

**Total: ~1.5 hours**

---

## Quick Verification After P3.1 Fix

```python
# test_kernel_injection.py
from steward.system_agents.envoy.cartridge_main import EnvoyCartridge
from vibe_core.kernel_impl import RealVibeKernel

kernel = RealVibeKernel()
kernel.boot()

# Get envoy from registry
envoy = kernel._agent_registry.get("envoy")

# This should NOT be None anymore!
assert envoy.kernel is not None, "FAIL: Kernel not injected!"
assert envoy.kernel == kernel, "FAIL: Wrong kernel injected!"
print("✅ Kernel injection working!")
```

---

## Architecture Note: self.kernel vs self.system.kernel

Currently we have TWO ways to access kernel:
1. `self.kernel` - Direct reference (legacy, many agents use this)
2. `self.system.kernel` - Via AgentSystemInterface (new pattern)

**Recommendation:** Keep BOTH working for backward compatibility.
- `set_kernel()` sets `self.kernel` directly
- `AgentSystemInterface` also has `.kernel` reference

This allows gradual migration without breaking existing code.

---

## Notes for Sonnet

1. **P3.1 is CRITICAL** - Fix this first, everything else depends on it
2. **Test after P3.1** - Many things might "just work" once kernel is injected
3. **Don't over-engineer** - Simple fixes are better than architectural changes
4. **Commit after each P** - So we can rollback if needed

---

*This roadmap was generated by Opus Senior Audit Sprint #2.*
*Execute P3.1 first - it's the keystone fix.*

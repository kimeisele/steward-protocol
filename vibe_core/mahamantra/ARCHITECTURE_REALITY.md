# ARCHITECTURE REALITY — Honest Spaghetti Map

**Date**: 2026-02-19
**Purpose**: Stop lying about what's connected. Map every path honestly.

---

## THE PROBLEM

There are **6 separate entry points** into the system. They share almost nothing.
Each one builds its own world from scratch, bypassing the others.

```
                    ┌─────────────────────────────────────────────────┐
                    │              USER INPUT                         │
                    └──┬──────┬──────┬──────┬──────┬──────┬──────────┘
                       │      │      │      │      │      │
                       ▼      ▼      ▼      ▼      ▼      ▼
                    __main__ entry.py steward.py  commands.py  chat.py  kernel/intent.py
                    (A)      (B)     (C)          (D)         (E)      (F)
```

---

## ENTRY POINT A: `__main__.py` — "Krishna Routes Everything"

```
python -m vibe_core.mahamantra "anything"
  → mahamantra.execute(input_text)
    → lotus.execute()
      → fire_gate(PARSE)
      → fire_gate(VALIDATE)
      → fire_gate(EXECUTE)
      → lotus.__call__() → execute_cycle() → 12 core ops + custom ops (VM!)
      → fire_gate(RESULT)
      → fire_gate(SYNC)
    → _render_response()
```

**Verdict**: ✅ GOES THROUGH VM. This is the only path that fully uses the architecture.

---

## ENTRY POINT B: `cli/entry.py` — "MahamantraCLIEntry"

```
steward <command> <args>
  → MahamantraCLIEntry.run()
    → if "chat": gateway_chat(message)          ← BYPASSES EVERYTHING
    → else: cli_auto.execute(command, remaining) ← Protocol introspection
      → discovers GuardianService methods
      → calls them directly                      ← BYPASSES VM, BYPASSES KERNEL
```

**Verdict**: ❌ BYPASSES VM. Calls guardian services directly via reflection.
The `chat` command goes through `vibe_core.gateway` — completely outside mahamantra.

---

## ENTRY POINT C: `cli/steward.py` — "Steward Resonance Router"

```
steward.invoke(input_text)
  → mahamantra(input_text)
    → lotus.__call__() → execute_cycle() → VM!
  → formats into StewardResponse
```

**Verdict**: ✅ GOES THROUGH VM. But `cli/entry.py` doesn't use this for most commands.
Only used if someone calls `Steward().invoke()` directly or via `cli_steward()`.

---

## ENTRY POINT D: `commands.py` — CLI Commands (WIRED TO VM ✅)

**Status**: All computation commands now route through `lotus.execute()`.
Audio, network, LLM are I/O side effects that consume VM output.

### D1: `cli_chant()` — WIRED ✅
```
→ lotus.execute("Hare Krishna") × N rounds   ← VM does kirtan + yajna + chamber
→ Audio synthesis from VM's DIW output        ← I/O side effect
→ Vimana streaming from VM's cell output      ← I/O side effect
```

### D2: `cli_listen()` — WIRED ✅
```
→ lotus.execute("listen {source}")            ← VM registers intent
→ get_events(source, limit)                   ← I/O: fetch from event_bridge
→ prints entries                              ← presentation
```

### D3: `cli_resolve()` — WIRED ✅
```
→ lotus.execute("resolve {name}")             ← VM registers intent
→ get_position_from_name()                    ← I/O: lookup from SSOT
→ formats output                              ← presentation
```

### D4: `cli_serve()` — WIRED ✅
```
→ lotus.execute(task)                         ← VM computes position/guardian routing
→ janaka.submit(task, sovereign_id=VM_route)  ← I/O: submit with VM context
→ janaka.execute(task_id)                     ← I/O: execute if requested
```

### D5: `cli_veda()` — WIRED ✅
```
→ lotus.execute(message)                      ← VM computes vibration/verse/guardian
→ VedaExplorer.process() or flooded_routed_chat() ← I/O: LLM/explorer
→ Enriches with VM composed output            ← deterministic path preferred
```

### D6: `cli_vimana_serve()`
```
→ SankirtanChamber.create()     ← own Chamber
→ VimanaServer(host, port)      ← network server
→ asyncio.run(server.serve_forever())
```
**Verdict**: ⚪ INFRASTRUCTURE. Network server. Not a computation concern.

---

## ENTRY POINT E: `chat.py` — Guardian Chat

```
guardian_chat(message)
  → MahajanaChat(position, guardian)
  → chat.respond(message)
    → builds system prompt with live context
    → calls LLM provider
```
**Verdict**: ❌ BYPASSES VM. Own LLM pipeline. No gates, no kernel, no VM.

---

## ENTRY POINT F: `kernel/intent.py` — MantraKernel

```
kernel.resolve(intent)
  → if resolver exists: resolver.resolve(intent)
  → else: _krishna_resolves(intent)
    → lotus.execute(intent.target, opcode=...)
      → __call__() → execute_cycle() → VM!
```

**Verdict**: ✅ GOES THROUGH VM (when no specialized resolver).
But: only 1 resolver registered (HEAL). And nobody calls kernel.resolve()
from the CLI commands. The kernel exists but is disconnected from the CLI.

---

## THE REAL SPLIT-BRAIN

It's not "chat is a different concern." The split-brain is:

1. **MantraKernel has IntentTypes** (READ, WRITE, TRANSFORM, RESOLVE, BIND,
   MIGRATE, WAKE, SYNC, HEAL, OBSERVE, SURRENDER) that map to OpCodes
   and route through `lotus.execute()` → VM.

2. **CLI commands bypass the kernel entirely.** They call services directly.
   - `cli_serve` should be `IntentType.TRANSFORM` → MantraKernel → VM
   - `cli_chant` should be `IntentType.WAKE` → MantraKernel → VM
   - `cli_veda` should be `IntentType.OBSERVE` → MantraKernel → VM
   - `cli_chat` should be `IntentType.SURRENDER` → MantraKernel → VM

3. **The kernel already has the routing.** `_krishna_resolves()` sends
   everything through `lotus.execute()`. But nobody uses it.

4. **cli/entry.py uses cli_auto** which discovers protocol methods via
   reflection and calls them directly — bypassing both the kernel AND the VM.

---

## THE FIX (not "different concerns" — same concern, different paths)

The VM is the **base layer**. Everything computes through it.
The kernel is the **intent layer**. Everything declares intent, kernel resolves.
CLI commands are **intent declarations**, not direct service calls.

```
CURRENT (spaghetti):
  cli_serve() → janaka.submit() → janaka.execute()

SHOULD BE:
  cli_serve() → MantraIntent(TRANSFORM, task) → kernel.resolve()
    → lotus.execute() → execute_cycle() → VM
    → JanakaResolver handles TRANSFORM intents
```

```
CURRENT (spaghetti):
  cli_chant() → Chamber.create() → mahamantra.tick() × N

SHOULD BE:
  cli_chant() → MantraIntent(WAKE, "chant N rounds") → kernel.resolve()
    → lotus.execute() → execute_cycle() → VM
    → ChantResolver handles WAKE intents with kirtan logic
```

```
CURRENT (spaghetti):
  cli_veda() → VedaExplorer.process() / flooded_routed_chat()

SHOULD BE:
  cli_veda() → MantraIntent(OBSERVE, message) → kernel.resolve()
    → lotus.execute() → execute_cycle() → VM
    → VedaResolver handles OBSERVE intents
```

---

## WHAT'S ACTUALLY CONNECTED (honest count)

| Path | Through VM? | Through Kernel? | Through Gates? |
|------|-------------|-----------------|----------------|
| `__main__.py` | ✅ | ❌ | ✅ |
| `cli/steward.py` | ✅ | ❌ | ❌ (calls __call__ not execute) |
| `cli/entry.py` | ❌ | ❌ | ❌ |
| `cli_chant` | ✅ (WIRED) | ❌ | ✅ |
| `cli_serve` | ✅ (WIRED) | ❌ | ✅ |
| `cli_veda` | ✅ (WIRED) | ❌ | ✅ |
| `cli_listen` | ✅ (WIRED) | ❌ | ✅ |
| `cli_resolve` | ✅ (WIRED) | ❌ | ✅ |
| `chat.py` | ❌ | ❌ | ❌ |
| `kernel.resolve()` | ✅ | ✅ | ✅ |

**Score: 7/8 computation paths go through the VM. 1/8 goes through the kernel.**
**Remaining bypass: `cli/entry.py` chat command + `chat.py` direct LLM.**

---

## PRIORITY ORDER

1. **Wire CLI commands through MantraKernel** — they become intent declarations
2. **Register IntentResolvers** for each IntentType (only HEAL exists today)
3. **MantraKernel itself becomes a VMCapability** — intent resolution as VM op
4. **cli/entry.py stops calling services directly** — routes through kernel
5. **chat.py routes through kernel** as IntentType.SURRENDER

This is not "forcing different concerns through the VM."
This is **using the architecture that already exists but nobody calls.**

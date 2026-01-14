# MAHAPROMPT - Mahamantra Development Guide
# ==========================================

**SANKIRTAN MODE: Multiple agents chanting together. Follow this exactly.**

---

## 1. THE ONE RULE: FOLDER IS WIRING

```
vibe_core/mahamantra/
├── {quarter}/           # Routes to 1 of 4 quarters
│   └── {mahajana}/      # Routes to 1 of 4 positions in quarter
│       └── __init__.py  # THE routing point
```

**Folder structure IS the lotus. No exceptions.**

| Quarter | Positions | Role |
|---------|-----------|------|
| genesis/ | 0,1,2,3 | INPUT - Boot, Load, Alloc, Spawn |
| dharma/ | 4,5,6,7 | VERIFY - Parse, Link, Check, Test |
| karma/ | 8,9,10,11 | EXECUTE - Run, Scale, Sync, Commit |
| moksha/ | 12,13,14,15 | OUTPUT - Yield, Flush, Log, Exit |

**Each folder routes to exactly ONE target. No multi-routing.**

---

## 2. SSOT: byte.py IS THE TRUTH

```python
# vibe_core/mahamantra/substrate/byte.py
MAHAMANTRA_POSITIONS = [...]  # THE 16 positions
```

**Never hardcode positions. Always derive from byte.py.**

```python
# WRONG
POSITION = 10
OPCODE = "STATE_SYNC"

# RIGHT
from vibe_core.mahamantra.substrate.byte import MAHAMANTRA_POSITIONS
pos = MAHAMANTRA_POSITIONS[10]
# pos.guardian, pos.opcode, pos.quarter - all derived
```

---

## 3. PROTOCOL PATTERN (Mandatory)

Every mahajana has exactly this structure:

```python
# {quarter}/{mahajana}/__init__.py

# 1. DECLARATION (machine-readable)
__mahajana__ = "name"
__position__ = N
__genesis__ = "0x..."

# 2. PROTOCOL (interface)
@runtime_checkable
class NameProtocol(Protocol):
    def method(self) -> TypedDict: ...

# 3. NULL (test implementation)
class NullName(NameProtocolBase):
    def method(self) -> TypedDict:
        return {...}

# 4. SERVICE (real implementation) - lazy loaded
def __getattr__(name):
    if name == "NameService":
        from .service import NameService
        return NameService
```

**No Any types. All TypedDict. Watertight.**

---

## 4. ROUTING FLOW

```
User Input
    ↓
Gateway (vibe_core/gateway/)
    ↓
Mahamantra.execute(command, args)
    ↓
cli_auto discovers method from Protocol
    ↓
mahamantra.mod[position] → routes to mahajana module
    ↓
NullImplementation.method() → calls Service if needed
    ↓
Result (TypedDict)
```

**Gateway is THE entry point. All paths go through gateway.**

---

## 5. TO ADD A NEW COMMAND

1. **Find the position** - Which mahajana owns this domain?
2. **Add to Protocol** - Add method signature with TypedDict return
3. **Implement in Null** - Add working implementation
4. **Test via gateway** - `execute("command_name", [args])`

Example: Adding `check` to Janaka (pos 10):

```python
# In protocols/mahajanas/janaka/__init__.py

class CheckResult(TypedDict):
    success: bool
    target: str
    health: str

class JanakaProtocol(Protocol):
    def check(self, target: str = "status") -> CheckResult: ...

class NullJanaka(JanakaProtocolBase):
    def check(self, target: str = "status") -> CheckResult:
        return CheckResult(success=True, target=target, health="pristine")
```

---

## 6. FORBIDDEN

- **No Any types** - Use Union, TypedDict, or explicit types
- **No hardcoded positions** - Derive from byte.py
- **No direct imports bypassing gateway** - Route through mahamantra
- **No multi-routing** - One folder = one target
- **No filesystem-first** - Protocol-first, folder is wiring

---

## 7. CURRENT STATE

```
protocols/mahajanas/  → IMPLEMENTATION (rich, 56KB)
mahamantra/{q}/{m}/   → STRUCTURE (re-exports from protocols)
```

**Samskara will migrate implementations into mahamantra over time.**
**For now: Structure in mahamantra, Implementation in protocols.**

---

## 8. QUICK REFERENCE

| Task | Location | Pattern |
|------|----------|---------|
| Add CLI command | protocols/mahajanas/{m}/ | Add to Protocol + NullImpl |
| Add service | protocols/mahajanas/{m}/service.py | Implement Protocol |
| Fix routing | gateway/mahamantra_gateway.py | Check execute() |
| Add position | FORBIDDEN | byte.py is SSOT, 16 fixed |

---

## 9. CHANT CHECK

Before committing, verify:

```bash
python3 -c "
from vibe_core.mahamantra.cli.auto import CLIAutoDiscovery
cli = CLIAutoDiscovery()
count = cli.discover_all()
print(f'Methods: {count}')  # Should be 100+
"
```

If methods < 100, something broke the routing.

---

**HARE KRISHNA. FOLDER IS WIRING. PROTOCOL FIRST. NO ANY.**

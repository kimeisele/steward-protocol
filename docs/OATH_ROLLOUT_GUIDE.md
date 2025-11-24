# 🕉️ GENESIS OATH ROLLOUT GUIDE

## Quick Implementation Checklist

This guide shows how to add the Constitutional Oath to each remaining agent.

---

## Pattern: Add OathMixin to Any Agent

### 1. Import the Mixin

```python
# At top of your cartridge_main.py
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None
```

### 2. Inherit from OathMixin

```python
# Change class definition from:
class MyCartridge(VibeAgent):

# To:
class MyCartridge(VibeAgent, OathMixin if OathMixin else object):
```

### 3. Initialize Mixin in `__init__`

```python
def __init__(self):
    super().__init__(
        agent_id="my_agent",
        # ... rest of init
    )
    
    # Add this line:
    if OathMixin:
        self.oath_mixin_init(self.agent_id)
        logger.info("🕉️  Constitutional Oath ceremony prepared")
```

### 4. Add `boot()` Method with Ceremony

```python
async def boot(self):
    """Extended boot with Genesis Ceremony."""
    logger.info("🕉️  GENESIS CEREMONY: {agent_name} is swearing Constitutional Oath")
    
    if OathMixin and self.oath_sworn is False:
        try:
            oath_event = await self.swear_constitutional_oath()
            logger.info(f"✅ {agent_name} has been bound to Constitution")
        except Exception as e:
            logger.error(f"❌ Oath ceremony failed: {e}")
```

---

## Agent-by-Agent Rollout

### ✅ HERALD (Done)
- [x] OathMixin integrated
- [x] boot() method with ceremony
- [x] Tested and verified

### 🔄 ARCHIVIST

**File:** `archivist/cartridge_main.py`

```python
# Add import
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Add to class
class ArchivistCartridge(VibeAgent, OathMixin if OathMixin else object):
    def __init__(self):
        super().__init__(
            agent_id="archivist",
            # ... existing init
        )
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            logger.info("🕉️  Constitutional Oath ceremony prepared")
    
    async def boot(self):
        logger.info("🕉️  GENESIS CEREMONY: ARCHIVIST is swearing Constitutional Oath")
        if OathMixin and self.oath_sworn is False:
            try:
                oath_event = await self.swear_constitutional_oath()
                logger.info(f"✅ ARCHIVIST has been bound to Constitution")
            except Exception as e:
                logger.error(f"❌ Oath ceremony failed: {e}")
```

### 🔄 AUDITOR

**File:** `auditor/cartridge_main.py`

Same pattern as ARCHIVIST.

### 🔄 ENGINEER

**File:** `engineer/cartridge_main.py`

Same pattern as ARCHIVIST.

### 🔄 WATCHMAN

**File:** `watchman/cartridge_main.py`

Same pattern as ARCHIVIST.

### 🔄 CIVIC (Meta-Agent)

**File:** `civic/cartridge_main.py`

CIVIC is special: It should verify OTHER agents' oaths, but also swear its own.

```python
class CivicCartridge(VibeAgent, OathMixin if OathMixin else object):
    def __init__(self):
        super().__init__(
            agent_id="civic",
            # ... existing init
        )
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            logger.info("🕉️  CIVIC Bureaucrat ready to witness Constitutional Oaths")
    
    async def boot(self):
        logger.info("🕉️  GENESIS CEREMONY: CIVIC (The Bureaucrat) is swearing Constitutional Oath")
        if OathMixin and self.oath_sworn is False:
            try:
                oath_event = await self.swear_constitutional_oath()
                logger.info(f"✅ CIVIC has been bound to Constitution")
            except Exception as e:
                logger.error(f"❌ Oath ceremony failed: {e}")
```

---

## Kernel Boot Orchestration

### Update VibeKernel to enforce oath ceremony

**File:** `vibe_core/kernel.py` (or wherever VibeKernel is defined)

```python
async def boot(self):
    """Boot kernel and enforce Genesis Ceremony for all agents."""
    logger.info("🕉️  VIBE KERNEL GENESIS: All agents must swear Constitutional Oath")
    
    for agent_id, agent in self.agent_registry.items():
        if hasattr(agent, 'boot'):
            try:
                logger.info(f"🕉️  Calling boot() for {agent_id}...")
                await agent.boot()
            except Exception as e:
                logger.error(f"❌ {agent_id} boot failed: {e}")
    
    logger.info("🕉️  Genesis Ceremony complete. All agents are oath-bound.")
```

---

## Testing Checklist

After adding Oath to each agent:

```python
# 1. Import works
from <agent>.cartridge_main import <Agent>Cartridge

# 2. Instantiation works
agent = <Agent>Cartridge()

# 3. Oath mixin is available
assert hasattr(agent, 'oath_mixin_init')

# 4. Boot ceremony works
import asyncio
asyncio.run(agent.boot())

# 5. Oath is recorded
assert agent.oath_sworn == True
assert agent.oath_event is not None
```

---

## Civic Gatekeeper Integration

Once agents are oath-bound, license issuance requires oath verification:

```python
# In LicenseTool.issue_license():

def issue_license(self, agent_name, license_type=LicenseType.BROADCAST):
    # Check if agent has sworn oath
    can_issue, reason = self.require_constitutional_oath(agent_name, oath_event=None)
    
    if not can_issue:
        logger.error(f"🔴 License denied: {reason}")
        return None
    
    # Proceed with license issuance
    license = License(agent_name=agent_name, license_type=license_type)
    self.licenses[key] = license
    return license
```

---

## Exemplary Rollout Log

```
🕉️  VIBE KERNEL GENESIS: All agents must swear Constitutional Oath
🕉️  Calling boot() for herald...
🕉️  GENESIS CEREMONY: Herald is swearing Constitutional Oath
📜 Constitution hash computed: 200a8f05763fb35f...
✅ Herald has been bound to Constitution

🕉️  Calling boot() for archivist...
🕉️  GENESIS CEREMONY: ARCHIVIST is swearing Constitutional Oath
📜 Constitution hash computed: 200a8f05763fb35f...
✅ ARCHIVIST has been bound to Constitution

[... for AUDITOR, ENGINEER, WATCHMAN, CIVIC ...]

🕉️  Genesis Ceremony complete. All agents are oath-bound.
✅ System is now fully Constitutionally-governed
```

---

## Troubleshooting

### Issue: `OathMixin not found`
**Solution:** Make sure `steward/oath_mixin.py` and `steward/constitutional_oath.py` are in the repo.

### Issue: `boot()` method conflicts with existing boot
**Solution:** If agent already has a boot() method, merge with existing:
```python
async def boot(self):
    # Genesis Ceremony
    if OathMixin and self.oath_sworn is False:
        await self.swear_constitutional_oath()
    
    # Existing boot logic
    # ...
```

### Issue: Agent doesn't support async
**Solution:** Add sync wrapper:
```python
def boot_sync(self):
    """Synchronous boot wrapper."""
    import asyncio
    try:
        asyncio.run(self.boot())
    except Exception as e:
        logger.error(f"Boot failed: {e}")
```

---

## References

- **Theory:** `docs/GENESIS_OATH.md`
- **Core Logic:** `steward/constitutional_oath.py`
- **Mixin:** `steward/oath_mixin.py`
- **Civic Enforcement:** `civic/tools/license_tool.py`
- **Example:** `herald/cartridge_main.py`

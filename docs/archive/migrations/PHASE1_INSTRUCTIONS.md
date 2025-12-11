# 🔥 PHOENIX PROTOCOL - PHASE 1 INSTRUCTIONS

**For:** Haiku (Implementation Agent)
**Date:** 2025-11-27
**Priority:** P0 - CRITICAL
**Estimated Time:** 1 week

---

## 🎯 MISSION

Transplant the nervous system (task management, identity, CLI) from vibe-agency into steward-protocol.

**NO NEW FEATURES. JUST MERGE.**

---

## 📋 CONTEXT

**vibe-agency location:** `/home/user/vibe-agency/`
**steward-protocol location:** `/home/user/steward-protocol/`

**What we're merging:**
- Task Management System (10 files) - So users can add tasks via CLI
- Identity System (1 file) - So agents can generate manifests
- CLI (1 file) - So users can interact with Agent City
- Boot Script (1 file) - So system boots cleanly

---

## ✅ TASK 1: Port task_management Module

**Source:** `/home/user/vibe-agency/vibe_core/task_management/`
**Target:** `/home/user/steward-protocol/vibe_core/task_management/`

**Files to copy:**
```
task_management/
├── __init__.py           # Module exports
├── models.py             # Task, ActiveMission, Roadmap, TaskStatus
├── task_manager.py       # Main TaskManager class
├── next_task_generator.py# Task generation logic
├── validator_registry.py # Validation framework
├── metrics.py            # Performance metrics
├── archive.py            # Task archival
├── batch_operations.py   # Batch processing
├── export_engine.py      # Data export
└── file_lock.py          # Concurrency control
```

**Steps:**
1. Copy entire directory:
   ```bash
   cp -r /home/user/vibe-agency/vibe_core/task_management/ \
         /home/user/steward-protocol/vibe_core/
   ```

2. Update imports in all files:
   - Change any relative imports if needed
   - Test that module loads: `python -c "from vibe_core.task_management import TaskManager; print('✅ OK')"`

3. Create directories if needed:
   ```bash
   mkdir -p /home/user/steward-protocol/.vibe/state
   mkdir -p /home/user/steward-protocol/.vibe/config
   mkdir -p /home/user/steward-protocol/.vibe/history/mission_logs
   ```

4. Test basic functionality:
   ```python
   from pathlib import Path
   from vibe_core.task_management import TaskManager

   tm = TaskManager(Path("."))
   print("✅ TaskManager initialized")
   ```

**Success Criteria:**
- ✅ All 10 files copied
- ✅ No import errors
- ✅ TaskManager can be instantiated

---

## ✅ TASK 2: Port identity.py

**Source:** `/home/user/vibe-agency/vibe_core/identity.py`
**Target:** `/home/user/steward-protocol/vibe_core/identity.py`

**Steps:**
1. Copy file:
   ```bash
   cp /home/user/vibe-agency/vibe_core/identity.py \
      /home/user/steward-protocol/vibe_core/
   ```

2. Check dependencies:
   - identity.py imports `agent_protocol` (should already exist in steward-protocol)
   - Test: `python -c "from vibe_core.identity import ManifestGenerator; print('✅ OK')"`

3. Test manifest generation for one agent:
   ```python
   from vibe_core.identity import ManifestGenerator
   from vibe_core.cartridges.system.civic.cartridge_main import CivicCartridge

   civic = CivicCartridge()
   manifest = ManifestGenerator.generate(civic)
   print(f"✅ Generated manifest for {manifest['agent']['id']}")
   ```

**Success Criteria:**
- ✅ File copied
- ✅ No import errors
- ✅ Can generate manifest for at least one agent

---

## ✅ TASK 3: Create CLI

**Source:** `/home/user/vibe-agency/apps/agency/cli.py` (reference)
**Target:** `/home/user/steward-protocol/bin/agent-city`

**Steps:**
1. Create executable script:
   ```bash
   touch /home/user/steward-protocol/bin/agent-city
   chmod +x /home/user/steward-protocol/bin/agent-city
   ```

2. Write CLI based on vibe-agency/apps/agency/cli.py but simplified:
   ```python
   #!/usr/bin/env python3
   """Agent City CLI - Unified interface for Agent City OS"""

   import argparse
   import sys
   from pathlib import Path

   # Add project root to path
   PROJECT_ROOT = Path(__file__).parent.parent
   sys.path.insert(0, str(PROJECT_ROOT))

   from vibe_core.task_management import TaskManager
   from vibe_core.kernel_impl import RealVibeKernel
   from vibe_core.cartridges.system.discoverer.agent import Discoverer

   def cmd_task_add(args):
       tm = TaskManager(PROJECT_ROOT)
       # TODO: Implement task add
       print(f"✅ Task added: {args.description}")

   def cmd_task_list(args):
       tm = TaskManager(PROJECT_ROOT)
       mission = tm.get_active_mission()
       print(f"Current task: {mission.current_task}")

   def cmd_status(args):
       kernel = RealVibeKernel(ledger_path=":memory:")
       steward = Discoverer(kernel)
       kernel.register_agent(steward)
       kernel.boot()
       count = steward.discover_agents()
       print(f"✅ Agent City Status:")
       print(f"   Agents registered: {len(kernel.agent_registry)}")
       print(f"   Agents discovered: {count}")

   def cmd_mission(args):
       print(f"🚀 Mission mode: {args.description}")
       # TODO: Implement autonomous mission execution

   def main():
       parser = argparse.ArgumentParser(prog="agent-city")
       subparsers = parser.add_subparsers(dest="command")

       # task add
       add_parser = subparsers.add_parser("task")
       add_subparsers = add_parser.add_subparsers(dest="task_command")
       task_add = add_subparsers.add_parser("add")
       task_add.add_argument("description")
       task_add.set_defaults(func=cmd_task_add)

       # task list
       task_list = add_subparsers.add_parser("list")
       task_list.set_defaults(func=cmd_task_list)

       # status
       status = subparsers.add_parser("status")
       status.set_defaults(func=cmd_status)

       # mission
       parser.add_argument("--mission", dest="mission_desc")

       args = parser.parse_args()

       if args.mission_desc:
           cmd_mission(type('Args', (), {'description': args.mission_desc})())
       elif hasattr(args, 'func'):
           args.func(args)
       else:
           parser.print_help()

   if __name__ == "__main__":
       main()
   ```

3. Test CLI:
   ```bash
   bin/agent-city status
   bin/agent-city task list
   ```

**Success Criteria:**
- ✅ `bin/agent-city status` shows agent count
- ✅ `bin/agent-city task list` runs without errors
- ✅ CLI is executable

---

## ✅ TASK 4: Port system-boot.sh

**Source:** `/home/user/vibe-agency/bin/system-boot.sh`
**Target:** `/home/user/steward-protocol/bin/system-boot.sh`

**Steps:**
1. Copy file:
   ```bash
   cp /home/user/vibe-agency/bin/system-boot.sh \
      /home/user/steward-protocol/bin/
   chmod +x /home/user/steward-protocol/bin/system-boot.sh
   ```

2. Adapt for steward-protocol:
   - Change entry point from `apps/agency/cli.py` to `bin/agent-city`
   - Update paths if needed

3. Test boot:
   ```bash
   bin/system-boot.sh
   ```

**Success Criteria:**
- ✅ Script runs without errors
- ✅ Shows VIBE OS banner
- ✅ Boots kernel successfully

---

## 🚫 IMPORTANT: WHAT NOT TO DO

- ❌ **Do NOT add new features** (no Prometheus, no Grafana, no "improvements")
- ❌ **Do NOT modify vibe-agency code** (it works, leave it alone)
- ❌ **Do NOT refactor existing code** (merge first, refactor later)
- ❌ **Do NOT add external dependencies** (use what's already there)
- ❌ **Do NOT implement "better" versions** (copy & adapt, that's it)

---

## ✅ WHAT TO DO

- ✅ **Copy code as-is** from vibe-agency
- ✅ **Adapt imports** for steward-protocol paths
- ✅ **Test that it loads** without errors
- ✅ **Use existing security** (Constitutional Oath is already there)
- ✅ **Use existing monitoring** (pulse.py is already there)

---

## 📊 SUCCESS CRITERIA (Phase 1 Complete)

When done, user should be able to run:

```bash
# Boot system
bin/system-boot.sh

# Check status
bin/agent-city status
# Output: "✅ Agent City Status: 22 agents registered"

# Add task
bin/agent-city task add "Implement feature X"
# Output: "✅ Task added: Implement feature X"

# List tasks
bin/agent-city task list
# Output: Shows current task

# Mission mode
bin/agent-city --mission "Complete all P0 tasks"
# Output: "🚀 Mission mode: Complete all P0 tasks"
```

---

## 🔧 DEPENDENCIES TO CHECK

**Python packages needed (should already be in pyproject.toml):**
- pyyaml (for roadmap.yaml)
- pydantic (for models)
- All other deps already in steward-protocol

**If missing, add to pyproject.toml:**
```toml
dependencies = [
    # ... existing deps ...
    "pyyaml>=6.0",
    "pydantic>=2.0",
]
```

---

## 📝 COMMIT STRATEGY

**After each task, commit:**

```bash
# After task_management/
git add vibe_core/task_management/
git commit -m "feat: Port task_management module from vibe-agency (Phase 1)"

# After identity.py
git add vibe_core/identity.py
git commit -m "feat: Port identity.py from vibe-agency (Phase 1)"

# After CLI
git add bin/agent-city
git commit -m "feat: Create agent-city CLI with task management commands (Phase 1)"

# After boot script
git add bin/system-boot.sh
git commit -m "feat: Port system-boot.sh from vibe-agency (Phase 1)"
```

**Final commit:**
```bash
git commit -m "feat: Phoenix Protocol Phase 1 Complete - Task management, identity, and CLI integrated

- Port task_management module (10 files)
- Port identity.py for manifest generation
- Create agent-city CLI (task add/list/status)
- Port system-boot.sh for clean boot sequence

Users can now:
- Add tasks via CLI: agent-city task add
- List tasks: agent-city task list
- Check status: agent-city status
- Run missions: agent-city --mission

Next: Phase 2 (runtime, playbook, specialists)"
```

---

## ⏱️ ESTIMATED TIME

- Task 1 (task_management): 2-3 hours
- Task 2 (identity.py): 30 minutes
- Task 3 (CLI): 3-4 hours
- Task 4 (boot script): 1 hour

**Total: ~1 day of focused work**

---

## 🆘 IF YOU GET STUCK

**Import errors:**
- Check that PROJECT_ROOT is in sys.path
- Check that vibe_core/__init__.py exists
- Use absolute imports: `from vibe_core.X import Y`

**File not found errors:**
- Create directories with `mkdir -p`
- Check file paths are correct

**Module not found errors:**
- Check pyproject.toml has all dependencies
- Run `pip install -e .` to install in dev mode

**Test failures:**
- Don't worry about tests yet (Phase 2)
- Focus on getting CLI to run

---

## 🎯 DEFINITION OF DONE

Phase 1 is complete when:

1. ✅ All 4 tasks completed
2. ✅ All files committed and pushed
3. ✅ CLI runs without errors
4. ✅ User can add tasks via `agent-city task add`
5. ✅ User can see status via `agent-city status`
6. ✅ No new features added (just merge)
7. ✅ No external tools added (no Prometheus, etc.)

---

**NOW EXECUTE. NO MORE QUESTIONS. JUST DO IT.** 🔥

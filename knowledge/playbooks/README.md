# 🎯 PLAYBOOK SYSTEM (GAD-5000: DETERMINISTIC INTELLIGENCE)

## Philosophy

The Playbook System transforms User Intent into **Deterministic Execution Sequences** with zero hallucinations.

```
User Input: "Create a marketing campaign"
    ↓
SANKHYA (Semantic Analysis): Detect [CMD_CREATE, DOM_GOVERNANCE]
    ↓
Find Matching Playbook: CAMPAIGN_LAUNCH_V1
    ↓
EXECUTE PHASES:
    [X] Phase 1: Validate Requirements
    [>] Phase 2: Research & Analysis
    [ ] Phase 3: Draft Content
    [ ] Phase 4: Review & Approval
    [ ] Phase 5: Publish
```

Each phase is:
- **Deterministic**: No "maybe", just rules
- **Checkpointed**: State is saved after each step
- **Visualized**: Progress shown in Iron Shell
- **Recoverable**: Can resume from interruption

## Playbooks Included

### 1. **PROJECT_SCAFFOLD_V1**
**Triggers**: `CMD_CREATE` (create a new project)
**Outcome**: Fully scaffolded project with git init
**Phases**:
- Validate project input
- Create folder structure
- Initialize git repository
- Notify completion

### 2. **CONTENT_GENERATION_V1**
**Triggers**: `CMD_CREATE + DOM_CONTENT` (create blog post, article, etc.)
**Outcome**: Research → Draft → Review → Publish workflow
**Phases**:
- Research & Analysis (gather context)
- Generate Draft (create content)
- Review & Approval (human checkpoint)
- Publishing (push to platform)
- Completion Notification

### 3. **GOVERNANCE_VOTE_V1**
**Triggers**: `CMD_VOTE + DOM_GOVERNANCE` (start voting session)
**Outcome**: Complete voting session with immutable ledger recording
**Phases**:
- Validate voting session
- Open voting
- Collect votes from registered voters
- Tally & verify results
- Record to immutable ledger
- Publish results

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ UniversalProvider (Intent Router)                   │
│                                                      │
│ 1. Analyze intent via SANKHYA (concept detection)   │
│ 2. Check for matching Playbook                      │
│ 3. If found: Execute Playbook                       │
│ 4. Else: Fall back to normal intent routing         │
└─────────────────────┬───────────────────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  PlaybookEngine            │
        │  (Dungeon Master)          │
        │                            │
        │ - Load playbooks from YAML │
        │ - Execute phases           │
        │ - Track state              │
        │ - Emit events              │
        └────────────────────────────┘
```

## File Structure

```
knowledge/
  playbooks/
    schema.yaml                 # Playbook schema definition
    project_scaffold.yaml       # Example: Project creation
    content_generation.yaml     # Example: Content workflow
    governance_vote.yaml        # Example: Voting process
    README.md                   # This file
```

## Schema Overview

```yaml
playbook:
  id: "PLAYBOOK_ID"
  name: "Human-Readable Name"
  intent_match:
    primary: "CMD_CREATE"        # Must match
    secondary: ["DOM_CONTENT"]   # Optional, increases score

  phases:
    - phase_id: "phase_1"
      name: "Phase Name"
      actions:
        - action_type: "CALL_AGENT"
          target: "agent_name"
          params: {...}
      on_success: "phase_2"       # Next phase
      on_failure: "ABORT"         # Or continue
      requires_approval: false    # Human checkpoint?
      timeout_seconds: 60
```

## Action Types

- **CALL_AGENT**: Delegate to another agent (Herald, Civic, etc.)
- **CHECK_STATE**: Validate preconditions
- **EXECUTE_SCRIPT**: Run deterministic script
- **EMIT_EVENT**: Send visualization event

## Creating Custom Playbooks

1. **Identify Intent Triggers**: What concepts trigger this playbook?
   ```yaml
   intent_match:
     primary: "CMD_EXECUTE"
     secondary: ["DOM_SYSTEM"]
   ```

2. **Design Phases**: What steps need to happen in sequence?
   ```yaml
   phases:
     - phase_id: "phase_1"
       name: "Validation"
       ...
     - phase_id: "phase_2"
       name: "Execution"
       ...
   ```

3. **Define Actions**: What does each phase do?
   ```yaml
   actions:
     - action_type: "CALL_AGENT"
       target: "civic"
       params:
         task: "execute_deployment"
   ```

4. **Add to `knowledge/playbooks/`**: Create `your_playbook.yaml`

5. **Test**: Run intent that matches the playbook

## Event Flow

During playbook execution, events are emitted for visualization:

```
THOUGHT   → "Analyzing intent: 'Create a campaign'"
ACTION    → "Found playbook: CAMPAIGN_LAUNCH_V1"
THOUGHT   → "Running: Validate Requirements"
ACTION    → "Completed: Validate Requirements"
THOUGHT   → "Running: Research & Analysis"
ACTION    → "Completed: Research & Analysis"
...
ACTION    → "Completed: All phases executed"
```

## Integration with Iron Shell

The Iron Shell will visualize playbook progress:

```
🎯 Executing: Content Generation Pipeline

[X] Phase 1: Research & Analysis
[X] Phase 2: Generate Draft
[>] Phase 3: Review & Approval
[ ] Phase 4: Publishing
[ ] Phase 5: Completion Notification

⏳ Awaiting approval for Phase 3...
```

## Debugging

Enable debug logging:
```python
import logging
logging.getLogger("PLAYBOOK_ENGINE").setLevel(logging.DEBUG)
```

Check loaded playbooks:
```python
from envoy.playbook_engine import PlaybookEngine
engine = PlaybookEngine()
print(f"Loaded {len(engine.playbooks)} playbooks:")
for pb_id, pb in engine.playbooks.items():
    print(f"  - {pb_id}: {pb.name}")
```

## Future Enhancements

- [ ] Playbook versioning (V2, V3, etc.)
- [ ] Conditional branches (if X then phase_A else phase_B)
- [ ] Parallel phase execution
- [ ] Rollback on failure
- [ ] Playbook chaining (one playbook triggering another)
- [ ] Human approval checkpoints with timeout
- [ ] Persistent state across restarts

# 🏛️ VIBE AGENCY | Deterministic Content Factory

A reference implementation of the **STEWARD Protocol v1.1.0** for automated, deterministic content generation.

This is **Agency in a Box**: structured briefings → intelligent processing → verified assets.

---

## 🎯 What This Does

Instead of:
- ❌ "Hey AI, write something creative about our product"
- ❌ Unpredictable outputs with hallucinations
- ❌ Black-box decision making

You get:
- ✅ **Structured Input**: Briefing templates force clarity
- ✅ **Deterministic Processing**: Each cartridge follows logic, not creativity
- ✅ **Verified Output**: Director agent validates against brand rules
- ✅ **Signed Artifacts**: STEWARD signatures prove authenticity

---

## 📂 Structure

```
agency/
├── inputs/                      # Briefings (the "client request")
│   ├── briefing_template.yaml   # Template for new campaigns
│   └── demo_campaign.yaml       # Example: Tesla Cybertruck
│
├── cartridges/                  # Agents-as-code (deterministic workflows)
│   ├── strategist.yaml          # Analyzes briefing → Creates strategy skeleton
│   ├── copywriter.yaml          # (Coming soon) Creates drafts from strategy
│   └── director.yaml            # (Coming soon) Validates against brand rules
│
├── memory/                      # Immutable brand knowledge
│   └── brand_guidelines/
│       └── global_rules.yaml    # Brand constraints & rules
│
└── outputs/                     # Finished campaigns (organized by campaign_id)
    └── [campaign_id]/
        ├── strategy.json
        ├── draft.md
        └── final_post.md (SIGNED)
```

---

## 🚀 Quick Start

### 1. **Understand the Input Format**

Review `inputs/briefing_template.yaml` - this is what you fill out to start a campaign.

```yaml
meta:
  client_name: "Your Client"
  campaign_id: "unique_id_001"

content:
  product: "What are we selling?"
  audience: "Who are we talking to?"
  goal: "What's the target? (Awareness, Conversion, Trust)"

constraints:
  channel: "twitter | linkedin | blog"
  tone: "professional | casual | edgy"
  forbidden_words: ["AI", "ChatGPT"]  # Hard constraints
```

### 2. **Create Your Briefing**

Copy the template and fill it out:

```bash
cp inputs/briefing_template.yaml inputs/my_campaign.yaml
# Edit my_campaign.yaml with your details
```

### 3. **Run the Pipeline** (Future)

```bash
steward run agency --input my_campaign.yaml
```

This will:
1. **Strategist** reads `my_campaign.yaml` → generates `strategy.json`
2. **Copywriter** reads `strategy.json` → generates `draft.md`
3. **Director** reads `draft.md` + `global_rules.yaml` → validates → signs `final_post.md`

---

## 🔧 The Cartridge Format

Each agent is a **Cartridge** (YAML file) that defines:

1. **Identity**: Who is this agent? What's their role?
2. **Input Schema**: What data does it expect?
3. **Process**: Step-by-step logic (not "be creative")
4. **Output Schema**: What does it produce?

Example: `strategist.yaml`

```yaml
apiVersion: vibe/v1
kind: Cartridge
metadata:
  name: agency-strategist
  version: 1.0.0

identity:
  org: org.vibe.steward
  role: architect
  compliance: level_2

input_schema:
  required:
    - content.product
    - content.audience
    - content.goal

process:
  logic_flow: "determinstic_aida"
  steps:
    - step: analyze_intent
    - step: select_framework
    - step: build_skeleton

output_schema:
  format: json
  target_path: "agency/outputs/{campaign_id}/strategy.json"
```

**Key principle**: No hallucination. Only deterministic decision trees and structured output.

---

## 🧠 The STEWARD Connection

This agency demonstrates STEWARD Protocol capabilities:

| Feature | How It Works |
|---------|-------------|
| **Identity** | Each cartridge has a defined `identity` (org, role, compliance level) |
| **Attestation** | Each output file is signed with `STEWARD_SIGNATURE` (proves who validated it) |
| **Cartridges** | Agents are YAML, not code—reusable, auditable, versionable |
| **Non-Destructive** | Everything is additive; delete `agency/` and the repo is unchanged |

---

## 📖 How to Extend

### Add a New Cartridge

1. Create `agency/cartridges/my_agent.yaml`
2. Define input, process, output
3. Reference it in a workflow

### Add Brand Rules

Edit `agency/memory/brand_guidelines/global_rules.yaml`:

```yaml
rules:
  - id: "my_custom_rule"
    check: "Description of what to check"
```

### Try the Demo

```bash
# The demo campaign is pre-configured
cat inputs/demo_campaign.yaml

# See what a briefing looks like
cat inputs/briefing_template.yaml
```

---

## 🎓 Learning Path

1. **Read** `briefing_template.yaml` - understand input format
2. **Read** `cartridges/strategist.yaml` - understand cartridge structure
3. **Copy** `briefing_template.yaml` → create your own briefing
4. **Run** the pipeline (when implemented)
5. **Review** the output in `outputs/[campaign_id]/`

---

## ✅ Non-Destructive by Design

- **Everything is YAML**: No compiled code, just data structures
- **Isolated workspace**: `agency/` is completely separate from core repo
- **Reversible**: `rm -rf agency/` restores the repo to original state
- **No side effects**: Running the agency doesn't modify existing agents or code

---

## 🔗 See Also

- [STEWARD Protocol Documentation](../docs/steward_protocol.md)
- [Cartridge Specification](./CARTRIDGES.md) (coming soon)
- [Brand Guidelines Format](./memory/BRAND_GUIDELINES.md) (coming soon)

---

**Built with the STEWARD Protocol by VIBE** 🎨

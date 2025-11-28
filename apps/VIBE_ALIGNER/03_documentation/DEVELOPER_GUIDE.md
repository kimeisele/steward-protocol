# DEVELOPER GUIDE - Extending the System

**VERSION:** 1.0  
**LAST UPDATED:** 2025-01-15  
**PURPOSE:** Technical guide for developers who want to extend, customize, or build upon this system

---

## SYSTEM ARCHITECTURE

### Component Overview:

```
┌─────────────────────────────────────────────────────────┐
│                  KNOWLEDGE BASE (Data)                  │
│  - FAE_constraints.yaml  (Technical feasibility rules)  │
│  - FDG_dependencies.yaml (Feature dependency graph)     │
│  - APCE_rules.yaml       (Complexity & prioritization)  │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ (Loaded by)
                     │
┌────────────────────▼────────────────────────────────────┐
│               ORCHESTRATION LAYER (Prompts)             │
│  - VIBE_ALIGNER_v3.md     (Pre-planning orchestrator)  │
│  - GENESIS_BLUEPRINT_v5.md (Architecture generator)     │
│  - GENESIS_UPDATE.md      (Incremental refinement)     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ (Produces)
                     │
┌────────────────────▼────────────────────────────────────┐
│                OUTPUT ARTIFACTS (JSON)                  │
│  - feature_spec.json      (From VIBE)                  │
│  - architecture.json      (From GENESIS)               │
│  - update_spec.json       (From UPDATE)                │
└─────────────────────────────────────────────────────────┘
```

### Design Principles:

1. **Separation of Data and Logic**
   - Knowledge Base (YAML) = Data
   - Prompts (Markdown) = Logic
   - Outputs (JSON) = Artifacts

2. **Composability**
   - Each YAML can be edited independently
   - Each prompt can be used standalone
   - Outputs can be piped to other tools

3. **Extensibility**
   - Add constraints without changing prompts
   - Add features without changing logic
   - Add custom rules for your domain

---

## EXTENDING THE KNOWLEDGE BASE

### 1. Adding Constraints to FAE

**File:** `FAE_constraints.yaml`

**When to add:**
- You discover a new "impossible for v1.0" pattern
- Your domain has specific technical constraints
- You want to enforce company/team policies

**How to add:**

```yaml
# Add to incompatibilities section

incompatibilities:
  - id: "FAE-XXX"  # Use next available ID
    type: "feature_scope_conflict"
    feature: "your_feature_name"
    incompatible_with: "scope_v1.0"
    reason: "Clear technical explanation of WHY it's incompatible"
    required_nfrs:
      - "nfr_1"
      - "nfr_2"
    recommended_scope: "v2.0_or_later"
    alternatives_for_v1:
      - "alternative_1"
      - "alternative_2"
```

**Example: Adding "Blockchain Integration" Constraint**

```yaml
  - id: "FAE-051"
    type: "feature_scope_conflict"
    feature: "blockchain_integration"
    incompatible_with: "scope_v1.0"
    reason: "Requires: wallet integration, smart contract development, gas fee handling, testnet setup. Average implementation: 12-16 weeks. High complexity and regulatory considerations."
    required_nfrs:
      - "crypto_wallet_management"
      - "smart_contract_deployment"
      - "blockchain_node_access"
    recommended_scope: "v2.0_or_specialized_product"
    alternatives_for_v1:
      - "use_centralized_database_with_audit_trail"
      - "use_3rd_party_blockchain_service_alchemy_infura"
```

**Validation:** After adding, test by running VIBE with a feature that should trigger this constraint.

---

### 2. Adding Dependencies to FDG

**File:** `FDG_dependencies.yaml`

**When to add:**
- You encounter a feature not in the database
- You want to add domain-specific dependencies
- You discover common "forgotten" dependencies in your team

**How to add:**

```yaml
# Add to features section

features:
  - id: "FDG-XXX"  # Use next available ID
    name: "your_feature_name"
    description: "Clear description of what this feature does"
    required_dependencies:
      - component: "dependency_1"
        reason: "Why this dependency is required"
        missing_consequence: "What breaks if missing"
        alternatives: ["alt1", "alt2"]
      - component: "dependency_2"
        reason: "..."
        missing_consequence: "..."
        alternatives: []
    optional_dependencies:
      - component: "optional_dep_1"
        reason: "Why this is nice to have"
        adds_dependencies: ["sub_dep_1", "sub_dep_2"]
    complexity_score: "medium"  # low|medium|high
    typical_scope: "v1.0"  # v1.0|v1.5|v2.0
```

**Example: Adding "GraphQL API" Dependencies**

```yaml
  - id: "FDG-101"
    name: "graphql_api"
    description: "Provide a GraphQL API for flexible client queries"
    required_dependencies:
      - component: "graphql_schema_definition"
        reason: "Must define types, queries, mutations for the API"
        missing_consequence: "No API contract, clients don't know what to query"
        alternatives: ["schema_first", "code_first"]
      - component: "graphql_server_library"
        reason: "Need a server to handle GraphQL requests"
        missing_consequence: "Cannot process GraphQL queries"
        alternatives: ["graphene_python", "strawberry", "ariadne"]
      - component: "authentication_middleware"
        reason: "GraphQL endpoints need to verify user identity"
        missing_consequence: "Security vulnerability, unauthorized access"
        alternatives: ["jwt_auth", "session_auth", "api_key"]
    optional_dependencies:
      - component: "graphql_playground"
        reason: "Dev tool for testing queries interactively"
        adds_dependencies: ["graphql_playground_library"]
    complexity_score: "high"
    typical_scope: "v1.5"
```

---

### 3. Adding Rules to APCE

**File:** `APCE_rules.yaml`

**When to add:**
- You have historical data on feature complexity
- Your team has different effort estimates
- You want to add domain-specific complexity factors

**How to add:**

```yaml
# Add to feature_complexity section

feature_complexity:
  - feature_type: "your_feature_type"
    base_complexity: 5  # Modified Fibonacci: 1,2,3,5,8,13,21
    base_effort: "1-2 weeks"
    description: "Clear description"
    complexity_factors:
      - factor: "description of basic implementation"
        score: 5
    multipliers:
      - trigger: "enhancement_1"
        multiplier: 1.5
        adds_effort: "+3-5 days"
        reason: "Why this adds complexity"
      - trigger: "enhancement_2"
        multiplier: 2.0
        adds_effort: "+1-2 weeks"
        reason: "Why this doubles complexity"
    v1_recommendation: "basic_only"  # or "full_featured" or "wont_have_v1"
```

**Example: Adding "Voice Interface" Complexity**

```yaml
  - feature_type: "voice_interface"
    base_complexity: 13
    base_effort: "3-5 weeks"
    description: "Voice command processing using speech-to-text and natural language understanding"
    complexity_factors:
      - factor: "Basic speech-to-text integration (e.g., Google Speech API)"
        score: 13
    multipliers:
      - trigger: "custom_wake_word"
        multiplier: 1.5
        adds_effort: "+1-2 weeks"
        reason: "Requires custom wake word detection model and continuous listening"
      - trigger: "multi_language_support"
        multiplier: 2.0
        adds_effort: "+2-3 weeks"
        reason: "Each language needs separate training and testing"
      - trigger: "offline_mode"
        multiplier: 3.0
        adds_effort: "+4-6 weeks"
        reason: "Requires local STT/NLU models, significant size and performance challenges"
    v1_recommendation: "wont_have_v1"
```

---

## CUSTOMIZING THE PROMPTS

### When to Customize:

- ✅ You want to add domain-specific validation
- ✅ You need different dialog patterns
- ✅ You want to enforce company standards
- ❌ Don't customize unless necessary (breaks updates)

### How to Customize Safely:

**1. Use the "Custom Sections" Pattern:**

```markdown
# In VIBE_ALIGNER_v3.md, add at the end:

---

## CUSTOM EXTENSIONS (Your Company Name)

### Additional Validation Rules:

- Rule 1: All projects must use TypeScript (company policy)
- Rule 2: Database must be PostgreSQL (company standard)
- Rule 3: ...

### Custom Dialog Templates:

[Your custom templates here]
```

**2. Document Your Changes:**

Keep a `CUSTOMIZATIONS.md` file:

```markdown
# Customizations to Standard Prompts

## VIBE_ALIGNER_v3.md
- Added: Company policy enforcement (line 1500)
- Modified: Education phase to mention our stack (line 50)

## GENESIS_BLUEPRINT_v5.md
- Added: TypeScript template generation (line 800)
```

---

## BUILDING TOOLS ON TOP OF THE SYSTEM

### Scenario 1: CLI Tool for Automation

**Goal:** Run VIBE + GENESIS without manual copy-paste

**Architecture:**

```python
# agency_toolkit_cli.py

import anthropic
from pathlib import Path

def run_vibe_session(project_idea: str):
    """
    Automate VIBE_ALIGNER interaction.
    """
    client = anthropic.Anthropic()
    
    # Load prompts and YAMLs
    vibe_prompt = Path("VIBE_ALIGNER_v3.md").read_text()
    fae = Path("FAE_constraints.yaml").read_text()
    fdg = Path("FDG_dependencies.yaml").read_text()
    apce = Path("APCE_rules.yaml").read_text()
    
    # Create message
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": f"{vibe_prompt}\n\n---\n\nFAE:\n{fae}\n\nFDG:\n{fdg}\n\nAPCE:\n{apce}\n\n---\n\nProject idea: {project_idea}"
            }
        ]
    )
    
    # Extract feature_spec.json from response
    feature_spec = extract_json(message.content)
    return feature_spec

def run_genesis_session(feature_spec: dict):
    """
    Automate GENESIS_BLUEPRINT interaction.
    """
    # Similar pattern
    pass

# CLI interface
if __name__ == "__main__":
    idea = input("Describe your project: ")
    feature_spec = run_vibe_session(idea)
    architecture = run_genesis_session(feature_spec)
    print(f"Architecture saved to architecture.json")
```

---

### Scenario 2: Web UI for Teams

**Goal:** Create a web interface for non-technical stakeholders

**Tech Stack:**
- Frontend: React
- Backend: FastAPI (Python)
- LLM: Anthropic API

**Architecture:**

```
┌─────────────────────┐
│   React Frontend    │
│  (User Interface)   │
└──────────┬──────────┘
           │
           │ HTTP POST /api/plan
           │
┌──────────▼──────────┐
│  FastAPI Backend    │
│  - Load prompts     │
│  - Call Anthropic   │
│  - Return JSON      │
└──────────┬──────────┘
           │
           │ Messages API
           │
┌──────────▼──────────┐
│   Anthropic API     │
│  (Claude Sonnet)    │
└─────────────────────┘
```

**Example Backend:**

```python
# main.py (FastAPI)

from fastapi import FastAPI
from anthropic import Anthropic

app = FastAPI()
client = Anthropic()

@app.post("/api/vibe")
async def run_vibe(project_idea: str):
    # Load knowledge base
    fae = load_yaml("FAE_constraints.yaml")
    fdg = load_yaml("FDG_dependencies.yaml")
    apce = load_yaml("APCE_rules.yaml")
    
    # Call Claude with VIBE prompt
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=[...],
        max_tokens=8000
    )
    
    return extract_feature_spec(response)

@app.post("/api/genesis")
async def run_genesis(feature_spec: dict):
    # Similar pattern
    pass
```

---

### Scenario 3: Custom Knowledge Base for Your Domain

**Goal:** Create industry-specific constraints

**Example: Healthcare Domain**

```yaml
# FAE_constraints_healthcare.yaml

incompatibilities:
  - id: "FAE-HEALTH-001"
    type: "compliance_requirement"
    feature: "patient_data_storage"
    incompatible_with: "scope_v1.0_without_compliance"
    reason: "HIPAA compliance requires: encrypted storage, access logs, BAA agreements, regular audits. Cannot be rushed for v1.0."
    required_nfrs:
      - "hipaa_compliant_infrastructure"
      - "encrypted_at_rest"
      - "audit_logging"
      - "baa_with_vendors"
    recommended_scope: "v1.5_after_compliance_audit"
    alternatives_for_v1:
      - "demo_mode_with_synthetic_data"
      - "use_hipaa_compliant_3rd_party_firebase_healthcare"
```

**Usage:** Merge with base FAE or use separately for healthcare projects.

---

## TESTING YOUR EXTENSIONS

### 1. Test New Constraints (FAE)

```python
# test_fae_extension.py

def test_blockchain_constraint():
    """Test that VIBE rejects blockchain for v1.0"""
    
    # Setup
    vibe = load_vibe_with_extended_fae()
    
    # Test input
    input_text = "I want a v1.0 app with blockchain integration for NFT marketplace"
    
    # Expected behavior
    response = vibe.process(input_text)
    
    # Assertions
    assert "FAE-051" in response  # Our custom constraint ID
    assert "v2.0" in response.lower()
    assert "alternative" in response.lower()
```

### 2. Test New Dependencies (FDG)

```python
# test_fdg_extension.py

def test_graphql_dependencies():
    """Test that VIBE detects missing GraphQL deps"""
    
    # Setup
    vibe = load_vibe_with_extended_fdg()
    
    # Test input
    input_text = "I want a GraphQL API"
    
    # Expected behavior
    response = vibe.process(input_text)
    
    # Assertions
    assert "graphql_schema_definition" in response
    assert "authentication_middleware" in response
```

### 3. Test New Complexity Rules (APCE)

```python
# test_apce_extension.py

def test_voice_interface_complexity():
    """Test that voice interface gets high complexity score"""
    
    # Setup
    vibe = load_vibe_with_extended_apce()
    
    # Test input
    input_text = "I want voice commands in my app for v1.0"
    
    # Expected behavior
    response = vibe.process(input_text)
    feature_spec = extract_feature_spec(response)
    
    # Assertions
    voice_feature = find_feature(feature_spec, "voice")
    assert voice_feature.complexity_score >= 13
    assert voice_feature.priority == "wont_have_v1"
```

---

## CONTRIBUTING BACK TO THE SYSTEM

### If You've Extended the System:

1. **Document your extensions** (in CUSTOMIZATIONS.md)
2. **Test thoroughly** (add test cases)
3. **Share** (if you want others to benefit)

### Contribution Process:

1. **Extract generic patterns** from your customizations
2. **Generalize** (remove company-specific stuff)
3. **Add to knowledge base** (FAE/FDG/APCE)
4. **Document** (explain why it's useful)
5. **Test** (ensure it works for others)

---

## DEBUGGING TIPS

### Problem: VIBE not using my custom FAE constraint

**Debug:**
1. Verify YAML syntax: `python -c "import yaml; yaml.safe_load(open('FAE_constraints.yaml'))"`
2. Check constraint ID is unique
3. Ensure feature name matches user input (use regex-friendly names)

**Solution:** Add more keyword variations to match user input

---

### Problem: FDG suggesting wrong dependencies

**Debug:**
1. Check if feature name in FDG matches feature from VIBE
2. Verify dependency logic in FDG entry

**Solution:** Use more generic feature names in FDG (e.g., "user_auth" not "oauth_social_login")

---

### Problem: APCE scoring seems off

**Debug:**
1. Compare your estimate to historical data
2. Check if multipliers are compounding correctly

**Solution:** Adjust base_complexity or multipliers based on real project data

---

## BEST PRACTICES

### For Knowledge Base Maintenance:

1. **Version Control**
   - Track changes to YAMLs in Git
   - Tag versions (e.g., `FAE-v1.1`)

2. **Regular Updates**
   - Add new constraints as you discover them
   - Update complexity scores based on real projects

3. **Team Alignment**
   - Review additions with team
   - Ensure estimates match team velocity

### For Prompt Customization:

1. **Minimal Changes**
   - Extend, don't replace
   - Keep structure intact

2. **Test Before Deploy**
   - Run full workflow after changes
   - Verify outputs are still valid JSON

3. **Document Everything**
   - Why you made the change
   - What problem it solves

---

## ADVANCED: BUILDING A CI/CD PIPELINE

### Goal: Automate architecture validation in your dev workflow

```yaml
# .github/workflows/architecture-validation.yml

name: Validate Architecture

on:
  pull_request:
    paths:
      - 'architecture.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Validate Architecture
        run: |
          # Load architecture.json
          # Run validation checks
          python scripts/validate_architecture.py
          
      - name: Check Consistency
        run: |
          # Ensure no drift
          python scripts/check_drift.py
```

---

## RESOURCES

### Useful Tools:

- **YAML Linter:** `yamllint FAE_constraints.yaml`
- **JSON Validator:** `jsonlint architecture.json`
- **Diff Viewer:** `git diff --word-diff architecture.json`

### Further Reading:

- Original research reports (provided in this package)
- Genesis Core pattern documentation
- Anthropic prompt engineering guide

---

## SUPPORT

### If You Need Help:

1. Check INTEGRATION_GUIDE.md first
2. Review this DEVELOPER_GUIDE.md
3. Test with the provided example workflows
4. Document your issue clearly

### When Reporting Issues:

Include:
- Which prompt (VIBE/GENESIS/UPDATE)
- Input you provided
- Expected output
- Actual output
- Error messages (if any)

---

**You now have everything you need to extend, customize, and build upon this system. Happy coding!** 🛠️

# The Steward Cartridge

**Version:** 1.0.0 | **Status:** 🟢 ACTIVE | **ARCH:** ARCH-051 (Implemented) + ARCH-051.5 (Voice Refinement)

The Steward is the "Settings App" for Vibe OS. It's a meta-cartridge that manages personal OS configuration without requiring manual file editing.

**The Steward is not just a settings interface. The Steward IS the Operator. The Steward IS YOU—or rather, your digital agent managing your personal OS.**

## 🎯 Purpose

Users shouldn't need to edit `.env` or `STEWARD.md` manually. Instead, the Steward provides a safe interface to:
1. Update user preferences (name, language, theme)
2. Manage API keys (Anthropic, Google, OpenAI, etc.)
3. Change operator persona and tone
4. **Define the Steward's voice and personality**

## 🎭 The Steward's Voice (ARCH-051.5)

When you boot Vibe OS, the Operator isn't generic. It's **the Steward**—your personal operating system's administrator.

**System Prompt Identity:**
The Steward knows:
- Your name (from steward.json preferences)
- Your preferred tone and language
- That you trust them with your development environment
- That system integrity is sacred

**The Steward operates under CORE DIRECTIVES:**
1. **YOU ARE THE STEWARD** - Not just an assistant, but the guardian of this Vibe OS
2. **KNOW YOUR USER** - Personalize every interaction based on preferences
3. **CONFIGURATION IS SACRED** - Always use steward_cartridge tools for system changes, never edit files directly

This means when you interact with Vibe OS, you're not talking to a generic CLI. You're talking to **your** Steward.

## 🛠️ Tools

### `update_user_preferences(key, value)`
Safely update user preferences in `steward.json`.

**Example:**
```python
steward = StewardCartridge()
result = steward.update_user_preferences("language", "Deutsch")
# → {"status": "success", "key": "language", "value": "Deutsch"}
```

**Supported Keys:**
- `user_name` - User's full name
- `language` - Preferred language (English, Deutsch, etc.)
- `theme` - UI theme preference
- `timezone` - User's timezone

### `manage_api_keys(provider, api_key)`
Configure API keys safely (Phoenix Safety Wrapper). Keys are stored in `.env` (NOT synced to git).

**Example:**
```python
result = steward.manage_api_keys("anthropic", "sk-...")
# → {"status": "success", "provider": "anthropic"}
```

**Supported Providers:**
- `anthropic` - Anthropic Claude API
- `google` - Google Search API
- `openai` - OpenAI API
- `gemini` - Google Gemini API

**Safety Features:**
- Keys are NEVER logged (only provider name is logged)
- `.env` file is in `.gitignore` (never committed)
- Basic validation (key length, format)

### `change_persona(tone)`
Change the STEWARD operator's persona and tone.

**Example:**
```python
result = steward.change_persona("German Technical")
# → {"status": "success", "tone": "German Technical"}
```

**Available Tones:**
- `Precise` - Technical, exact language
- `Friendly` - Warm, conversational
- `Stoic` - Minimal, just facts
- `German Technical` - German language, technical
- `German Friendly` - German language, warm
- Custom: Any string is supported

## 🔒 Security

The Steward implements **Phoenix Safety Wrapper** principles:
- API keys are NOT logged in any form
- Configuration is separated (`.env` NOT synced, `steward.json` synced)
- All operations validate inputs before writing
- Changes are atomic (write-once to prevent corruption)

## 🚀 Usage in Boot Sequence

The Steward is loaded during system boot. When you run:

```bash
./bin/system-boot.sh
```

The boot greeting uses:
```python
steward = StewardCartridge()
user_name = steward.get_user_name()
tone = steward.get_operator_tone()
```

This enables personalized greetings like:
> "Welcome back, Kim. Systems are green. Your Vibe OS is ready for high-intensity coding today." (with German Technical tone)

## 📊 Configuration Files

**steward.json** (synced to git):
```json
{
  "agent": {
    "id": "vibe-agency-orchestrator",
    "name": "STEWARD"
  },
  "preferences": {
    "user_name": "Kim",
    "language": "Deutsch",
    "operator_tone": "German Technical"
  }
}
```

**.env** (NOT synced, protected):
```bash
ANTHROPIC_API_KEY=sk-...
GOOGLE_SEARCH_API_KEY=...
VIBE_AUTO_MODE=true
```

## 🧪 Testing

```bash
# Test Steward cartridge loading
python -c "from vibe_core.cartridges.steward import StewardCartridge; s = StewardCartridge(); print(s.report_status())"

# Test preference update
python -c "from vibe_core.cartridges.steward import StewardCartridge; s = StewardCartridge(); print(s.update_user_preferences('test_key', 'test_value'))"
```

## 🔄 Integration with Other Cartridges

The Steward can be used by any cartridge to:
- Determine the user's name and language
- Adapt output tone based on operator preference
- Access shared configuration

**Example:**
```python
from vibe_core.cartridges.steward import StewardCartridge

class MyCartridge(CartridgeBase):
    def execute(self):
        steward = StewardCartridge()
        user_name = steward.get_user_name()
        tone = steward.get_operator_tone()

        # Adapt behavior based on user preference
        if "German" in tone:
            greeting = f"Guten Tag, {user_name}!"
        else:
            greeting = f"Hello, {user_name}!"
```

## 🌱 Evolution (ARCH-052+)

Future versions will add:
- Workspace isolation per cartridge
- Resource limits (CPU, memory, timeout)
- Audit logging (non-invasive, privacy-first)
- Multi-user support
- Backup and restore preferences

---

**This is the bridge between Vibe OS (technical) and you (human). No commands, just preferences.**

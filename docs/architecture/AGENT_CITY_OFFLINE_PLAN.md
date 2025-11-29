# AGENT CITY OFFLINE-FIRST IMPLEMENTATION PLAN

**Status:** READY FOR EXECUTION
**Author:** Claude Opus (Mayor of Agent City)
**Date:** 2025-11-29
**Target Executor:** Haiku/Sonnet

---

## EXECUTIVE SUMMARY

Dieses Dokument ist der vollständige, ausführbare Plan um Agent City offline-fähig zu machen.

**Ziel:** Agent City funktioniert vollständig offline mit graceful degradation:
```
SemanticRouter (80MB) → Local LLM (~400MB) → Templates → Klarer Fehler
```

**Kritische Regel:** KEINE neuen parallelen Strukturen. Wir integrieren in bestehende Komponenten.

---

## TEIL 1: SYSTEM AUDIT (BEREITS DURCHGEFÜHRT)

### 1.1 Was EXISTIERT und funktioniert

| Component | Datei | Status |
|-----------|-------|--------|
| ProcessManager | `vibe_core/process_manager.py` | ✅ Integriert in Kernel |
| SemanticRouter | `provider/semantic_router.py` | ✅ In UniversalProvider |
| PromptRegistry | `vibe_core/runtime/prompt_registry.py` | ✅ 731 Zeilen, komplett |
| PromptContext | `vibe_core/runtime/prompt_context.py` | ✅ 593 Zeilen, komplett |
| Provider Factory | `vibe_core/runtime/providers/factory.py` | ✅ Hat "local" Platzhalter |
| SmartLocalProvider | `vibe_core/llm/smart_local_provider.py` | ⚠️ Ist Delegation-Simulator, KEIN LLM |
| 14 System Agents | `steward/system_agents/*/` | ✅ VibeAgent compliant |
| 9 Citizen Agents | `agent_city/registry/*/` | ⚠️ Viele TODO-Stubs |

### 1.2 Was FEHLT

| Gap | Wo | Priorität |
|-----|-----|----------|
| Local LLM Provider | `vibe_core/llm/` | 🔴 KRITISCH |
| Factory "local" implementierung | `vibe_core/runtime/providers/factory.py:80` | 🔴 KRITISCH |
| Graceful Degradation Chain | `vibe_core/llm/` | 🔴 KRITISCH |
| ContextAwareAgent Base | `vibe_core/agents/` | 🟡 MITTEL |
| CLI boot/delegate implementierung | `vibe_core/cli.py` | 🟡 MITTEL |
| 19 Citizen Agent Stubs | `agent_city/registry/*/` | 🟢 LATER |

### 1.3 Integrationspunkte (NICHT DUPLIZIEREN!)

Diese bestehenden Dateien müssen EDITIERT werden, NICHT neu erstellt:

1. **`vibe_core/runtime/providers/factory.py`** - Zeile 80-82 ändern
2. **`vibe_core/llm/__init__.py`** - Exports hinzufügen
3. **`vibe_core/agents/__init__.py`** - Export hinzufügen
4. **`provider/universal_provider.py`** - Degradation integrieren
5. **`pyproject.toml`** - Dependencies hinzufügen

---

## TEIL 2: IMPLEMENTATION SCHRITTE

### PHASE 0: GRACEFUL DEGRADATION

#### Schritt 0.1: DegradationChain erstellen

**AKTION:** NEUE DATEI erstellen
**PFAD:** `/home/user/steward-protocol/vibe_core/llm/degradation_chain.py`

```python
"""
Graceful Degradation Chain for Offline Operation.

Fallback order:
1. SemanticRouter (>0.85 confidence) -> Direct execution
2. SemanticRouter (0.60-0.85) -> Execute with clarification
3. LocalLLM (if available) -> Generate response
4. Templates (always available) -> Static response
5. Error with guidance -> Tell user what to install
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger("DEGRADATION_CHAIN")


class DegradationLevel(Enum):
    """Current system capability level."""
    FULL = "full"           # Local LLM available
    TEMPLATES = "templates"  # Only templates available
    MINIMAL = "minimal"      # Nothing available


@dataclass
class DegradationResponse:
    """Response with degradation metadata."""
    content: str
    level: DegradationLevel
    confidence: float
    fallback_used: str
    user_guidance: Optional[str] = None


class DegradationChain:
    """
    Manages graceful degradation when LLM is unavailable.

    Usage:
        chain = DegradationChain()
        response = chain.respond(user_input, semantic_confidence)
    """

    def __init__(self):
        self._local_llm = None
        self._templates = self._load_templates()
        self._level = self._detect_level()
        logger.info(f"DegradationChain initialized (level: {self._level.value})")

    def _detect_level(self) -> DegradationLevel:
        """Detect current system capability."""
        try:
            from vibe_core.llm.local_llama_provider import LocalLlamaProvider
            if LocalLlamaProvider.model_exists():
                self._local_llm = LocalLlamaProvider()
                if self._local_llm.is_available:
                    return DegradationLevel.FULL
        except ImportError:
            logger.debug("LocalLlamaProvider not available (not installed)")
        except Exception as e:
            logger.warning(f"Local LLM check failed: {e}")

        if self._templates:
            return DegradationLevel.TEMPLATES

        return DegradationLevel.MINIMAL

    def _load_templates(self) -> Dict[str, str]:
        """Load response templates."""
        return {
            "greeting": "Willkommen in Agent City. Ich bin bereit zu helfen.",
            "status": "Agent City ist online. Alle Systeme nominal.",
            "unknown": "Ich verstehe deine Anfrage. Bitte sei spezifischer.",
            "error": "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",
            "no_llm": (
                "Kein lokales LLM installiert. "
                "Fuer bessere Antworten: steward install-llm"
            ),
        }

    def respond(
        self,
        user_input: str,
        semantic_confidence: float,
        detected_intent: Optional[str] = None
    ) -> DegradationResponse:
        """Generate response with graceful degradation."""

        # SATYA (>0.85): High confidence
        if semantic_confidence >= 0.85:
            return DegradationResponse(
                content="[SATYA: Direct execution by SemanticRouter]",
                level=self._level,
                confidence=semantic_confidence,
                fallback_used="none"
            )

        # MANTHAN (0.60-0.85): Medium confidence
        if semantic_confidence >= 0.60:
            clarification = self._generate_clarification(user_input, detected_intent)
            return DegradationResponse(
                content=clarification,
                level=self._level,
                confidence=semantic_confidence,
                fallback_used="clarification"
            )

        # NETI NETI (<0.60): Low confidence
        return self._neti_neti_fallback(user_input, semantic_confidence)

    def _generate_clarification(self, user_input: str, intent: Optional[str]) -> str:
        """Generate clarification request."""
        if intent:
            return f"Ich glaube du meinst '{intent}'. Kannst du das bestaetigen?"
        return f"Ich verstehe: '{user_input[:50]}...'. Was genau soll ich tun?"

    def _neti_neti_fallback(self, user_input: str, confidence: float) -> DegradationResponse:
        """NETI NETI fallback chain."""

        # Try LocalLLM
        if self._local_llm is not None:
            try:
                response = self._local_llm.chat([
                    {"role": "user", "content": user_input}
                ])
                return DegradationResponse(
                    content=response,
                    level=DegradationLevel.FULL,
                    confidence=confidence,
                    fallback_used="local_llm"
                )
            except Exception as e:
                logger.warning(f"LocalLLM failed: {e}")

        # Try Templates
        template_key = self._match_template(user_input)
        if template_key:
            content = self._templates[template_key]
            if self._level != DegradationLevel.FULL:
                content += "\n\n" + self._templates["no_llm"]

            return DegradationResponse(
                content=content,
                level=self._level,
                confidence=confidence,
                fallback_used=f"template:{template_key}",
                user_guidance="Fuer intelligentere Antworten: steward install-llm"
            )

        # Last resort
        return DegradationResponse(
            content=self._templates["unknown"] + "\n\n" + self._templates["no_llm"],
            level=DegradationLevel.MINIMAL,
            confidence=confidence,
            fallback_used="template:unknown",
            user_guidance="Fuer intelligentere Antworten: steward install-llm"
        )

    def _match_template(self, user_input: str) -> Optional[str]:
        """Simple keyword matching."""
        lower = user_input.lower()

        if any(w in lower for w in ["hallo", "hi", "hey", "guten"]):
            return "greeting"
        if any(w in lower for w in ["status", "health", "alive"]):
            return "status"

        return "unknown"

    @property
    def current_level(self) -> DegradationLevel:
        return self._level

    def get_status(self) -> Dict[str, Any]:
        """Get status for introspection."""
        return {
            "level": self._level.value,
            "local_llm_available": self._local_llm is not None,
            "templates_loaded": len(self._templates),
        }
```

**VERIFIKATION:**
```bash
cd /home/user/steward-protocol
python -c "from vibe_core.llm.degradation_chain import DegradationChain; dc = DegradationChain(); print(dc.get_status())"
```
**ERWARTETE AUSGABE:** `{'level': 'templates', 'local_llm_available': False, 'templates_loaded': 5}`

---

#### Schritt 0.2: Export in llm/__init__.py

**AKTION:** ZEILEN HINZUFUEGEN
**PFAD:** `/home/user/steward-protocol/vibe_core/llm/__init__.py`

**AENDERUNG:** Nach Zeile 12 (nach `from vibe_core.llm.steward_provider import StewardProvider`):

```python
from vibe_core.llm.degradation_chain import DegradationChain, DegradationLevel, DegradationResponse
```

**AENDERUNG:** In `__all__` Liste hinzufuegen:

```python
__all__ = [
    "ChainProvider",
    "DegradationChain",      # NEU
    "DegradationLevel",      # NEU
    "DegradationResponse",   # NEU
    "HumanProvider",
    "LLMError",
    "LLMProvider",
    "SmartLocalProvider",
    "StewardProvider",
]
```

**VERIFIKATION:**
```bash
python -c "from vibe_core.llm import DegradationChain; print('OK')"
```

---

### PHASE 1: LOCAL LLM PROVIDER

#### Schritt 1.1: Dependencies in pyproject.toml

**AKTION:** SEKTION HINZUFUEGEN
**PFAD:** `/home/user/steward-protocol/pyproject.toml`

**AENDERUNG:** In `[project.optional-dependencies]` Sektion (falls nicht existiert, erstellen):

```toml
[project.optional-dependencies]
local-llm = [
    "llama-cpp-python>=0.2.0",
    "huggingface-hub>=0.20.0",
]
```

**VERIFIKATION:**
```bash
grep -A 3 "local-llm" /home/user/steward-protocol/pyproject.toml
```

---

#### Schritt 1.2: LocalLlamaProvider erstellen

**AKTION:** NEUE DATEI erstellen
**PFAD:** `/home/user/steward-protocol/vibe_core/llm/local_llama_provider.py`

```python
"""
Local LLM Provider - Offline Intelligence via llama.cpp.

Provides local LLM inference without API calls.
Target: Smallest viable models (~400MB).

Models (preference order):
1. Qwen2.5-0.5B-Instruct-Q4 (~400MB)
2. SmolLM-360M-Instruct-Q4 (~360MB)
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional, List, Dict

from vibe_core.llm.provider import LLMProvider

logger = logging.getLogger("LOCAL_LLAMA")

DEFAULT_MODEL_DIR = Path("data/models")
DEFAULT_MODEL_NAME = "qwen2.5-0.5b-instruct-q4_k_m.gguf"
DEFAULT_MODEL_REPO = "Qwen/Qwen2.5-0.5B-Instruct-GGUF"

MODEL_SEARCH_PATHS = [
    DEFAULT_MODEL_DIR / DEFAULT_MODEL_NAME,
    Path.home() / ".cache" / "steward" / "models" / DEFAULT_MODEL_NAME,
    Path("/tmp/vibe_os/models") / DEFAULT_MODEL_NAME,
]


class LocalLlamaProvider(LLMProvider):
    """Local LLM provider using llama-cpp-python."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None,
        verbose: bool = False
    ):
        self._llm = None
        self._model_path = None
        self._initialized = False

        self.n_ctx = n_ctx
        self.n_threads = n_threads or self._get_optimal_threads()
        self.verbose = verbose

        if model_path:
            self._model_path = Path(model_path)
        else:
            self._model_path = self._find_model()

        if self._model_path and self._model_path.exists():
            self._load_model()
        else:
            logger.warning(
                f"No local model found. Install with: steward install-llm"
            )

    @staticmethod
    def model_exists() -> bool:
        """Check if a local model is available."""
        for path in MODEL_SEARCH_PATHS:
            if path.exists():
                return True
        return False

    @staticmethod
    def get_model_path() -> Optional[Path]:
        """Get path to available model."""
        for path in MODEL_SEARCH_PATHS:
            if path.exists():
                return path
        return None

    def _find_model(self) -> Optional[Path]:
        """Search for model in default locations."""
        for path in MODEL_SEARCH_PATHS:
            if path.exists():
                logger.info(f"Found local model: {path}")
                return path
        return None

    def _get_optimal_threads(self) -> int:
        """Detect optimal thread count."""
        try:
            cpu_count = os.cpu_count() or 4
            return max(2, cpu_count // 2)
        except Exception:
            return 4

    def _load_model(self) -> None:
        """Load the GGUF model."""
        try:
            from llama_cpp import Llama

            logger.info(f"Loading local model: {self._model_path}")

            self._llm = Llama(
                model_path=str(self._model_path),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=self.verbose,
                n_batch=512,
                use_mmap=True,
                use_mlock=False,
            )

            self._initialized = True
            model_size_mb = self._model_path.stat().st_size / (1024 * 1024)
            logger.info(f"Local model loaded ({model_size_mb:.0f}MB)")

        except ImportError:
            logger.error("llama-cpp-python not installed. pip install llama-cpp-python")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Generate response from local LLM."""
        if not self._initialized or self._llm is None:
            return "[Local LLM not initialized. Run: steward install-llm]"

        prompt = self._format_chat_prompt(messages)

        max_tokens = kwargs.get("max_tokens", 256)
        temperature = kwargs.get("temperature", 0.7)

        try:
            response = self._llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["<|endoftext|>", "<|im_end|>", "\nUser:"],
                echo=False,
            )

            return response["choices"][0]["text"].strip()

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return f"[Generation error: {e}]"

    def _format_chat_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into ChatML prompt."""
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"<|im_start|>system\n{content}<|im_end|>")
            elif role == "user":
                prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == "assistant":
                prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")

        prompt_parts.append("<|im_start|>assistant\n")
        return "\n".join(prompt_parts)

    @property
    def system_prompt(self) -> str:
        return "Du bist ein hilfreicher Assistent in Agent City."

    @property
    def is_available(self) -> bool:
        return self._initialized and self._llm is not None

    def get_info(self) -> Dict[str, Any]:
        """Get provider info."""
        return {
            "provider": "LocalLlamaProvider",
            "initialized": self._initialized,
            "model_path": str(self._model_path) if self._model_path else None,
            "n_ctx": self.n_ctx,
            "n_threads": self.n_threads,
        }


def download_default_model(target_dir: Optional[Path] = None) -> Path:
    """Download the default model from HuggingFace."""
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        raise ImportError("huggingface-hub not installed. pip install huggingface-hub")

    target_dir = target_dir or DEFAULT_MODEL_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading {DEFAULT_MODEL_NAME}...")

    model_path = hf_hub_download(
        repo_id=DEFAULT_MODEL_REPO,
        filename=DEFAULT_MODEL_NAME,
        local_dir=str(target_dir),
        local_dir_use_symlinks=False,
    )

    logger.info(f"Model downloaded: {model_path}")
    return Path(model_path)
```

**VERIFIKATION:**
```bash
python -c "from vibe_core.llm.local_llama_provider import LocalLlamaProvider; print(LocalLlamaProvider.model_exists())"
```
**ERWARTETE AUSGABE:** `False` (Model noch nicht installiert)

---

#### Schritt 1.3: Export LocalLlamaProvider

**AKTION:** ZEILEN HINZUFUEGEN
**PFAD:** `/home/user/steward-protocol/vibe_core/llm/__init__.py`

**AENDERUNG:** Import hinzufuegen:
```python
from vibe_core.llm.local_llama_provider import LocalLlamaProvider, download_default_model
```

**AENDERUNG:** In `__all__`:
```python
    "LocalLlamaProvider",    # NEU
    "download_default_model", # NEU
```

---

#### Schritt 1.4: Factory "local" implementieren

**AKTION:** ZEILEN AENDERN
**PFAD:** `/home/user/steward-protocol/vibe_core/runtime/providers/factory.py`

**AENDERUNG:** Zeile 80-82 ersetzen (aktuell NoOpProvider):

```python
        elif provider_name == "local":
            logger.info("Creating Local LLM provider")
            try:
                from vibe_core.llm.local_llama_provider import LocalLlamaProvider
                if LocalLlamaProvider.model_exists():
                    return LocalLlamaProvider(**kwargs)
                else:
                    logger.warning("Local model not found. Run: steward install-llm")
                    return NoOpProvider()
            except ImportError:
                logger.warning("llama-cpp-python not installed")
                return NoOpProvider()
```

**VERIFIKATION:**
```bash
python -c "from vibe_core.runtime.providers.factory import create_provider; p = create_provider('local'); print(type(p).__name__)"
```
**ERWARTETE AUSGABE:** `NoOpProvider` (bis Model installiert)

---

#### Schritt 1.5: CLI install-llm Command

**AKTION:** METHODE HINZUFUEGEN
**PFAD:** `/home/user/steward-protocol/vibe_core/cli.py`

**AENDERUNG:** Nach `cmd_introspect` Methode (ca. Zeile 720):

```python
    # =========================================================================
    # COMMAND: steward install-llm
    # =========================================================================

    def cmd_install_llm(self) -> int:
        """Download and install local LLM (~400MB)."""
        print("LOCAL LLM INSTALLATION")
        print("=" * 70)
        print()

        try:
            from vibe_core.llm.local_llama_provider import download_default_model

            print("Model: qwen2.5-0.5b-instruct-q4_k_m.gguf")
            print("Size:  ~400MB")
            print()
            print("Downloading from HuggingFace...")

            model_path = download_default_model()

            print()
            print(f"Model installed: {model_path}")
            return 0

        except ImportError as e:
            print(f"Missing dependency: {e}")
            print("Install: pip install 'steward-protocol[local-llm]'")
            return 1
        except Exception as e:
            print(f"Installation failed: {e}")
            return 1
```

**AENDERUNG:** In `main()` Funktion, Subparser hinzufuegen:

```python
    # steward install-llm
    subparsers.add_parser("install-llm", help="Download local LLM (~400MB)")
```

**AENDERUNG:** In Command-Routing:

```python
    elif args.command == "install-llm":
        return cli.cmd_install_llm()
```

**VERIFIKATION:**
```bash
python -m vibe_core.cli install-llm --help
```

---

### PHASE 2: AGENT CONTEXT INTEGRATION

#### Schritt 2.1: ContextAwareAgent erstellen

**AKTION:** NEUE DATEI erstellen
**PFAD:** `/home/user/steward-protocol/vibe_core/agents/context_aware_agent.py`

```python
"""
Context-Aware Agent Base Class.

Provides automatic context injection and governed prompt composition.
"""

import logging
from typing import Dict, Any, Optional, List

from vibe_core.protocols import VibeAgent

logger = logging.getLogger("CONTEXT_AWARE_AGENT")


class ContextAwareAgent(VibeAgent):
    """Base class for agents needing context injection."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._prompt_context = None
        self._prompt_registry = None
        self._context_initialized = False

    def _ensure_context_initialized(self) -> None:
        """Lazy initialization of context systems."""
        if self._context_initialized:
            return

        try:
            from vibe_core.runtime.prompt_context import get_prompt_context
            self._prompt_context = get_prompt_context()
        except Exception as e:
            logger.warning(f"{self.agent_id}: PromptContext unavailable: {e}")

        try:
            from vibe_core.runtime.prompt_registry import PromptRegistry
            self._prompt_registry = PromptRegistry
        except Exception as e:
            logger.warning(f"{self.agent_id}: PromptRegistry unavailable: {e}")

        self._context_initialized = True

    def get_context(self, keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get dynamic context."""
        self._ensure_context_initialized()

        if self._prompt_context is None:
            return {"_error": "PromptContext not available"}

        default_keys = ["git_status", "system_time", "current_branch"]
        return self._prompt_context.resolve(keys or default_keys)

    def get_governed_prompt(
        self,
        task_name: str,
        extra_context: Optional[Dict[str, Any]] = None,
        inject_governance: bool = True
    ) -> str:
        """Get governed prompt with context injection."""
        self._ensure_context_initialized()

        if self._prompt_registry is None:
            return f"[PromptRegistry not available for task: {task_name}]"

        context = self.get_context()
        if extra_context:
            context.update(extra_context)

        context["agent_id"] = self.agent_id

        try:
            return self._prompt_registry.compose(
                agent=self.agent_id.upper(),
                task=task_name,
                context=context,
                inject_governance=inject_governance
            )
        except Exception as e:
            logger.warning(f"Prompt composition failed: {e}")
            return f"[Prompt composition failed: {e}]"
```

**VERIFIKATION:**
```bash
python -c "from vibe_core.agents.context_aware_agent import ContextAwareAgent; print('OK')"
```

---

#### Schritt 2.2: Export ContextAwareAgent

**AKTION:** ZEILEN AENDERN
**PFAD:** `/home/user/steward-protocol/vibe_core/agents/__init__.py`

**AENDERUNG:** Import hinzufuegen:
```python
from vibe_core.agents.context_aware_agent import ContextAwareAgent
```

**AENDERUNG:** In `__all__`:
```python
__all__ = ["ContextAwareAgent", "SimpleLLMAgent", "SpecialistAgent", "SpecialistFactoryAgent"]
```

---

### PHASE 3: INTEGRATION IN UNIVERSAL PROVIDER

#### Schritt 3.1: DegradationChain in UniversalProvider

**AKTION:** ZEILEN HINZUFUEGEN
**PFAD:** `/home/user/steward-protocol/provider/universal_provider.py`

**AENDERUNG:** Nach Zeile ~232 (nach Initialization):

```python
        # === DEGRADATION CHAIN ===
        self.degradation_chain = None
        try:
            from vibe_core.llm.degradation_chain import DegradationChain
            self.degradation_chain = DegradationChain()
            logger.info(f"Degradation Chain: {self.degradation_chain.current_level.value}")
        except Exception as e:
            logger.warning(f"Degradation Chain unavailable: {e}")
```

---

## TEIL 3: AUSFUEHRUNGSREIHENFOLGE

```
PHASE 0: Graceful Degradation
  0.1 -> 0.2

PHASE 1: Local LLM
  1.1 -> 1.2 -> 1.3 -> 1.4 -> 1.5

PHASE 2: Agent Context
  2.1 -> 2.2

PHASE 3: Integration
  3.1
```

---

## TEIL 4: VOLLSTAENDIGE DATEILISTE

| # | Datei | Aktion | Phase |
|---|-------|--------|-------|
| 1 | `vibe_core/llm/degradation_chain.py` | NEU ERSTELLEN | 0.1 |
| 2 | `vibe_core/llm/__init__.py` | EDITIEREN | 0.2, 1.3 |
| 3 | `pyproject.toml` | EDITIEREN | 1.1 |
| 4 | `vibe_core/llm/local_llama_provider.py` | NEU ERSTELLEN | 1.2 |
| 5 | `vibe_core/runtime/providers/factory.py` | EDITIEREN | 1.4 |
| 6 | `vibe_core/cli.py` | EDITIEREN | 1.5 |
| 7 | `vibe_core/agents/context_aware_agent.py` | NEU ERSTELLEN | 2.1 |
| 8 | `vibe_core/agents/__init__.py` | EDITIEREN | 2.2 |
| 9 | `provider/universal_provider.py` | EDITIEREN | 3.1 |

**TOTAL: 4 neue Dateien, 5 editierte Dateien**

---

## TEIL 5: ABHAENGIGKEITEN

### Python Dependencies (optional, fuer Local LLM)

```bash
pip install llama-cpp-python huggingface-hub
```

### Model Download (nach Installation)

```bash
steward install-llm
```

---

## TEIL 6: NICHT IN DIESEM PLAN (SPAETER)

1. **Citizen Agent Stubs ausfuellen** - 19 TODOs in 6 Agents
2. **CLI boot/stop als Daemon** - Aktuell nur Foreground
3. **Weitere Agents zu ContextAwareAgent migrieren** - HERALD als Beispiel
4. **Tests** - Unit Tests fuer neue Komponenten

---

## APPENDIX A: VERIFIKATIONS-CHECKLISTE

Nach Ausfuehrung aller Schritte, folgende Tests durchfuehren:

```bash
# 1. DegradationChain
python -c "from vibe_core.llm import DegradationChain; print(DegradationChain().get_status())"

# 2. LocalLlamaProvider (ohne Model)
python -c "from vibe_core.llm import LocalLlamaProvider; print(LocalLlamaProvider.model_exists())"

# 3. Factory local
python -c "from vibe_core.runtime.providers.factory import create_provider; print(type(create_provider('local')).__name__)"

# 4. ContextAwareAgent
python -c "from vibe_core.agents import ContextAwareAgent; print('OK')"

# 5. CLI install-llm
python -m vibe_core.cli install-llm --help

# 6. Full Integration (optional, nach Model-Installation)
# steward install-llm
# python -c "from vibe_core.llm import LocalLlamaProvider; p = LocalLlamaProvider(); print(p.chat([{'role':'user','content':'Hello'}]))"
```

---

**ENDE DES PLANS**

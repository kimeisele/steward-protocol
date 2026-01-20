"""
VEDA EXPLORER - Neuro-Symbolic Chat Interface
==============================================

"vedaham samatitani vartamanani ca bhavishyani ca"
"I know all that has happened, is happening, and will happen."
— Bhagavad Gita 7.26

THE VEDA-4 PIPELINE:
    SHABDA (Word)     → Intent parsing (deterministic first, LLM fallback)
    ARTHA (Meaning)   → Parameter extraction
    PRATYAYA (Trust)  → Validation & confirmation
    KARMA (Action)    → Execution via existing CLI commands

MODES:
    RESTRICTED → No API, deterministic templates (cost-free)
    ENHANCED   → LLM for fuzzy matching (default when API available)
    CREATIVE   → Full LLM generation (explicit request only)

ARCHITECTURE:
    User Input → VedaExplorer → cli_chant/listen/resolve → Result
                     ↓
              (LLM only when needed)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xf4a21c87"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Tuple, TypedDict

# SSOT imports
from vibe_core.mahamantra.substrate.seed import NavaBhakti


# =============================================================================
# VEDA EXPLORER TYPES
# =============================================================================


class ExplorerMode(str, Enum):
    """Operating mode of the Veda Explorer."""

    RESTRICTED = "restricted"  # No LLM, deterministic only
    ENHANCED = "enhanced"      # LLM for intent parsing
    CREATIVE = "creative"      # Full LLM generation


class VedaIntent(str, Enum):
    """Recognized intents mapped to NavaBhakti."""

    CHANT = "chant"        # KIRTANAM - Execute cycles
    LISTEN = "listen"      # SRAVANAM - View events
    RESOLVE = "resolve"    # VANDANAM - Lookup mahajana
    SERVE = "serve"        # PADA_SEVANAM - Execute task
    SCAN = "scan"          # SMARANAM - Scan codebase
    HELP = "help"          # Show available commands
    STATUS = "status"      # System status
    UNKNOWN = "unknown"    # Requires LLM or clarification


class VedaResult(TypedDict):
    """Result from Veda Explorer execution."""

    success: bool
    intent: str
    mode: str
    response: str
    data: Dict[str, object]
    llm_used: bool


# =============================================================================
# INTENT KEYWORDS (Deterministic Mapping)
# =============================================================================

# Keywords → Intent (SHABDA layer - no LLM needed)
INTENT_KEYWORDS: Final[Dict[str, VedaIntent]] = {
    # CHANT (KIRTANAM)
    "chant": VedaIntent.CHANT,
    "chanten": VedaIntent.CHANT,
    "mantra": VedaIntent.CHANT,
    "cycle": VedaIntent.CHANT,
    "tick": VedaIntent.CHANT,
    "rounds": VedaIntent.CHANT,
    "mala": VedaIntent.CHANT,

    # LISTEN (SRAVANAM)
    "listen": VedaIntent.LISTEN,
    "hören": VedaIntent.LISTEN,
    "events": VedaIntent.LISTEN,
    "violations": VedaIntent.LISTEN,
    "logs": VedaIntent.LISTEN,
    "syscalls": VedaIntent.LISTEN,

    # RESOLVE (VANDANAM)
    "resolve": VedaIntent.RESOLVE,
    "who": VedaIntent.RESOLVE,
    "wer": VedaIntent.RESOLVE,
    "lookup": VedaIntent.RESOLVE,
    "find": VedaIntent.RESOLVE,
    "mahajana": VedaIntent.RESOLVE,

    # SERVE (PADA_SEVANAM)
    "serve": VedaIntent.SERVE,
    "execute": VedaIntent.SERVE,
    "run": VedaIntent.SERVE,
    "task": VedaIntent.SERVE,
    "do": VedaIntent.SERVE,
    "mach": VedaIntent.SERVE,

    # SCAN (SMARANAM)
    "scan": VedaIntent.SCAN,
    "discover": VedaIntent.SCAN,
    "search": VedaIntent.SCAN,

    # HELP
    "help": VedaIntent.HELP,
    "hilfe": VedaIntent.HELP,
    "?": VedaIntent.HELP,
    "commands": VedaIntent.HELP,

    # STATUS
    "status": VedaIntent.STATUS,
    "health": VedaIntent.STATUS,
    "state": VedaIntent.STATUS,
}

# Mahajana names for RESOLVE intent - use SSOT from scanner
def _get_all_mahajana_names() -> set:
    """Get all mahajana names and aliases from SSOT."""
    try:
        from vibe_core.mahamantra.substrate.scanner import MAHAJANA_ALIASES
        names = set()
        for alias in MAHAJANA_ALIASES:  # Tuple of MahajanaAlias
            names.add(alias.name)
            names.update(alias.aliases)
        return names
    except ImportError:
        # Fallback if scanner not available
        return {
            "brahma", "narada", "shambhu", "kumaras", "kapila", "manu",
            "prahlada", "janaka", "bhishma", "bali", "shuka", "yamaraja",
            "vyasa", "prithu", "parashurama", "nrisimha",
        }

MAHAJANA_NAMES: Final[set] = _get_all_mahajana_names()


# =============================================================================
# VEDA EXPLORER ENGINE
# =============================================================================


@dataclass
class ParsedIntent:
    """Parsed intent from user input."""

    intent: VedaIntent
    params: Dict[str, object] = field(default_factory=dict)
    raw_input: str = ""
    confidence: float = 1.0
    llm_used: bool = False


class VedaExplorer:
    """
    Neuro-Symbolic Chat Interface.

    Deterministic first, LLM fallback.
    Routes to existing CLI commands (no duplication).

    Usage:
        explorer = VedaExplorer()
        result = explorer.process("chant 108 times")
        result = explorer.process("who is brahma?")
    """

    def __init__(self, mode: ExplorerMode = ExplorerMode.ENHANCED) -> None:
        self._mode = mode
        self._llm = None
        self._llm_available = False
        self._history: List[Dict[str, str]] = []  # Conversational memory

        # Lazy load LLM
        self._init_llm()

    def _init_llm(self) -> None:
        """Initialize LLM if available."""
        if self._mode == ExplorerMode.RESTRICTED:
            return

        try:
            from vibe_core.runtime.llm_engine import LLMEngine
            self._llm = LLMEngine()
            self._llm_available = self._llm.provider != "mock" and self._llm.api_key
        except ImportError:
            self._llm_available = False

    @property
    def mode(self) -> ExplorerMode:
        """Current operating mode."""
        return self._mode

    @property
    def llm_available(self) -> bool:
        """Is LLM available for enhanced processing?"""
        return self._llm_available

    # =========================================================================
    # SHABDA - Intent Parsing (Layer 1)
    # =========================================================================

    def _parse_intent_deterministic(self, text: str) -> ParsedIntent:
        """
        Parse intent using deterministic keyword matching.

        SHABDA layer - no LLM needed for common commands.
        """
        text_lower = text.lower().strip()
        words = text_lower.split()

        # Check for direct intent keywords
        for word in words:
            # Strip punctuation
            clean_word = word.strip("?!.,;:")
            if clean_word in INTENT_KEYWORDS:
                intent = INTENT_KEYWORDS[clean_word]
                params = self._extract_params(text, intent)
                return ParsedIntent(
                    intent=intent,
                    params=params,
                    raw_input=text,
                    confidence=1.0,
                    llm_used=False,
                )

        # Check for mahajana names (implies RESOLVE)
        for word in words:
            clean_word = word.strip("?!.,;:")
            if clean_word in MAHAJANA_NAMES:
                return ParsedIntent(
                    intent=VedaIntent.RESOLVE,
                    params={"name": clean_word},
                    raw_input=text,
                    confidence=0.9,
                    llm_used=False,
                )

        # Check for number (implies CHANT with rounds)
        for word in words:
            if word.isdigit():
                return ParsedIntent(
                    intent=VedaIntent.CHANT,
                    params={"rounds": int(word)},
                    raw_input=text,
                    confidence=0.8,
                    llm_used=False,
                )

        return ParsedIntent(
            intent=VedaIntent.UNKNOWN,
            params={},
            raw_input=text,
            confidence=0.0,
            llm_used=False,
        )

    def _parse_intent_llm(self, text: str) -> ParsedIntent:
        """
        Parse intent using LLM for ambiguous inputs.

        Only called when deterministic parsing fails.
        """
        if not self._llm_available or not self._llm:
            return ParsedIntent(
                intent=VedaIntent.UNKNOWN,
                params={},
                raw_input=text,
                confidence=0.0,
                llm_used=False,
            )

        # Use LLM to classify intent
        prompt = f"""Classify the user intent into ONE of these categories:
- chant: User wants to execute mahamantra cycles
- listen: User wants to view events/logs/violations
- resolve: User wants to lookup a mahajana/guardian
- serve: User wants to execute a task
- scan: User wants to scan the codebase
- help: User wants help
- status: User wants system status

User input: "{text}"

Reply with ONLY the category name (lowercase, one word)."""

        try:
            response = self._llm.speak("VEDA_EXPLORER", "classification", prompt)
            response_clean = response.strip().lower().split()[0] if response else ""

            # Map response to intent
            intent_map = {
                "chant": VedaIntent.CHANT,
                "listen": VedaIntent.LISTEN,
                "resolve": VedaIntent.RESOLVE,
                "serve": VedaIntent.SERVE,
                "scan": VedaIntent.SCAN,
                "help": VedaIntent.HELP,
                "status": VedaIntent.STATUS,
            }

            intent = intent_map.get(response_clean, VedaIntent.UNKNOWN)
            params = self._extract_params(text, intent)

            return ParsedIntent(
                intent=intent,
                params=params,
                raw_input=text,
                confidence=0.7,  # LLM confidence is lower
                llm_used=True,
            )
        except Exception:
            return ParsedIntent(
                intent=VedaIntent.UNKNOWN,
                params={},
                raw_input=text,
                confidence=0.0,
                llm_used=True,
            )

    # =========================================================================
    # ARTHA - Parameter Extraction (Layer 2)
    # =========================================================================

    def _extract_params(self, text: str, intent: VedaIntent) -> Dict[str, object]:
        """
        Extract parameters from text based on intent.

        ARTHA layer - meaning extraction.
        """
        text_lower = text.lower()
        words = text_lower.split()
        params: Dict[str, object] = {}

        if intent == VedaIntent.CHANT:
            # Extract rounds
            for i, word in enumerate(words):
                if word.isdigit():
                    params["rounds"] = int(word)
                    break
                # Check for "N times" or "N rounds"
                if word in ("times", "rounds", "mal", "runden") and i > 0:
                    prev = words[i - 1]
                    if prev.isdigit():
                        params["rounds"] = int(prev)
                        break
            # Default
            if "rounds" not in params:
                params["rounds"] = 1
            # Verbose flag
            params["verbose"] = "verbose" in text_lower or "-v" in text_lower

        elif intent == VedaIntent.LISTEN:
            # Extract source
            if "violation" in text_lower:
                params["source"] = "violations"
            elif "syscall" in text_lower:
                params["source"] = "syscalls"
            else:
                params["source"] = "all"
            # Extract tail count
            for i, word in enumerate(words):
                if word.isdigit():
                    params["tail"] = int(word)
                    break
            if "tail" not in params:
                params["tail"] = 10

        elif intent == VedaIntent.RESOLVE:
            # Extract mahajana name
            for word in words:
                clean = word.strip("?!.,;:")
                if clean in MAHAJANA_NAMES:
                    params["name"] = clean
                    break
                # Check for position number
                if clean.isdigit():
                    pos = int(clean)
                    if 0 <= pos <= 15:
                        params["name"] = str(pos)
                        break

        elif intent == VedaIntent.SERVE:
            # Extract task description (everything after "serve"/"execute"/"run")
            for keyword in ("serve", "execute", "run", "task", "do", "mach"):
                if keyword in text_lower:
                    idx = text_lower.find(keyword) + len(keyword)
                    task = text[idx:].strip()
                    if task:
                        params["task"] = task
                    break

        return params

    # =========================================================================
    # KARMA - Execution (Layer 4)
    # =========================================================================

    def _execute_intent(self, parsed: ParsedIntent) -> VedaResult:
        """
        Execute the parsed intent via existing CLI commands.

        KARMA layer - action execution.
        """
        # Import handlers
        from vibe_core.mahamantra.commands import (
            cli_chant,
            cli_listen,
            cli_resolve,
            cli_serve,
        )

        intent = parsed.intent
        params = parsed.params

        try:
            if intent == VedaIntent.CHANT:
                result = cli_chant(
                    rounds=int(params.get("rounds", 1)),
                    verbose=bool(params.get("verbose", False)),
                )
                return VedaResult(
                    success=result.get("success", False),
                    intent=intent.value,
                    mode=self._mode.value,
                    response=self._format_chant_response(result),
                    data=dict(result),
                    llm_used=parsed.llm_used,
                )

            elif intent == VedaIntent.LISTEN:
                result = cli_listen(
                    source=str(params.get("source", "all")),
                    tail=int(params.get("tail", 10)),
                    json=False,
                )
                return VedaResult(
                    success=result.get("success", False),
                    intent=intent.value,
                    mode=self._mode.value,
                    response=self._format_listen_response(result),
                    data=dict(result),
                    llm_used=parsed.llm_used,
                )

            elif intent == VedaIntent.RESOLVE:
                name = str(params.get("name", ""))
                if not name:
                    return VedaResult(
                        success=False,
                        intent=intent.value,
                        mode=self._mode.value,
                        response="Wen soll ich auflösen? Gib einen Mahajana-Namen an.",
                        data={},
                        llm_used=parsed.llm_used,
                    )
                result = cli_resolve(name=name, json=False)
                return VedaResult(
                    success=result.get("success", False),
                    intent=intent.value,
                    mode=self._mode.value,
                    response=self._format_resolve_response(result),
                    data=dict(result),
                    llm_used=parsed.llm_used,
                )

            elif intent == VedaIntent.SERVE:
                task = str(params.get("task", ""))
                if not task:
                    return VedaResult(
                        success=False,
                        intent=intent.value,
                        mode=self._mode.value,
                        response="Welche Aufgabe soll ich ausführen?",
                        data={},
                        llm_used=parsed.llm_used,
                    )
                result = cli_serve(task=task, execute=False, json=False)
                return VedaResult(
                    success=result.get("success", False),
                    intent=intent.value,
                    mode=self._mode.value,
                    response=self._format_serve_response(result),
                    data=dict(result),
                    llm_used=parsed.llm_used,
                )

            elif intent == VedaIntent.HELP:
                return VedaResult(
                    success=True,
                    intent=intent.value,
                    mode=self._mode.value,
                    response=self._get_help_response(),
                    data={},
                    llm_used=parsed.llm_used,
                )

            elif intent == VedaIntent.STATUS:
                return self._get_status_response(parsed)

            else:  # UNKNOWN
                return self._handle_unknown(parsed)

        except Exception as e:
            return VedaResult(
                success=False,
                intent=intent.value,
                mode=self._mode.value,
                response=f"Fehler bei Ausführung: {e}",
                data={"error": str(e)},
                llm_used=parsed.llm_used,
            )

    # =========================================================================
    # RESPONSE FORMATTERS
    # =========================================================================

    def _format_chant_response(self, result: Dict) -> str:
        """Format chant result for display."""
        if not result.get("success"):
            return "Chant fehlgeschlagen."

        rounds = result.get("rounds", 1)
        ticks = result.get("ticks", 0)
        final_guardian = result.get("final_guardian", "?")
        connected = "Ja" if result.get("parampara_connected") else "Nein"

        return (
            f"Chant abgeschlossen.\n"
            f"  Rounds: {rounds} | Ticks: {ticks}\n"
            f"  Final Guardian: {final_guardian}\n"
            f"  Parampara Connected: {connected}"
        )

    def _format_listen_response(self, result: Dict) -> str:
        """Format listen result for display."""
        if not result.get("success"):
            return "Listen fehlgeschlagen."

        total = result.get("total_entries", 0)
        shown = result.get("filtered_entries", 0)
        source = result.get("source", "all")

        return (
            f"Events empfangen (source={source}).\n"
            f"  Total: {total} | Gezeigt: {shown}"
        )

    def _format_resolve_response(self, result: Dict) -> str:
        """Format resolve result for display."""
        if not result.get("success"):
            return f"Konnte '{result.get('name', '?')}' nicht auflösen."

        name = result.get("name", "?")
        position = result.get("position", -1)
        quarter = result.get("quarter", "?")
        desc = result.get("description", "")
        aliases = result.get("aliases", ())

        return (
            f"{name.upper()} (Position {position})\n"
            f"  Quarter: {quarter}\n"
            f"  Beschreibung: {desc}\n"
            f"  Aliases: {', '.join(aliases)}"
        )

    def _format_serve_response(self, result: Dict) -> str:
        """Format serve result for display."""
        if not result.get("success"):
            return f"Serve fehlgeschlagen: {result.get('message', '?')}"

        task_id = result.get("task_id", "?")
        status = result.get("status", "?")

        return (
            f"Task erstellt.\n"
            f"  ID: {task_id}\n"
            f"  Status: {status}"
        )

    def _get_help_response(self) -> str:
        """Get help text."""
        return """VEDA EXPLORER - Verfügbare Befehle:

  chant [N]        Führe N Mahamantra-Zyklen aus (Standard: 1)
  listen [N]       Zeige die letzten N Events (Standard: 10)
  resolve <name>   Löse Mahajana auf (z.B. "brahma", "narada")
  serve <task>     Erstelle eine Aufgabe
  status           Zeige Systemstatus
  help             Diese Hilfe

Beispiele:
  "chant 108"           → 108 Zyklen
  "who is brahma?"      → Auflösung von Brahma
  "listen violations"   → Zeige Violations
  "status"              → Systemstatus"""

    def _get_status_response(self, parsed: ParsedIntent) -> VedaResult:
        """Get system status."""
        mode = "RESTRICTED" if self._mode == ExplorerMode.RESTRICTED else "ENHANCED"
        llm = "Verfügbar" if self._llm_available else "Nicht verfügbar"

        return VedaResult(
            success=True,
            intent="status",
            mode=self._mode.value,
            response=(
                f"VEDA EXPLORER STATUS\n"
                f"  Modus: {mode}\n"
                f"  LLM: {llm}\n"
                f"  Provider: {self._llm.provider if self._llm else 'None'}"
            ),
            data={
                "mode": self._mode.value,
                "llm_available": self._llm_available,
            },
            llm_used=parsed.llm_used,
        )

    def _handle_unknown(self, parsed: ParsedIntent) -> VedaResult:
        """Handle unknown intent."""
        if self._mode == ExplorerMode.RESTRICTED:
            return VedaResult(
                success=False,
                intent="unknown",
                mode=self._mode.value,
                response=(
                    f"Ich verstehe '{parsed.raw_input}' nicht.\n"
                    f"Verfügbare Befehle: chant, listen, resolve, serve, status, help"
                ),
                data={},
                llm_used=False,
            )

        # In ENHANCED mode, use LLM for natural response
        if self._llm_available and self._llm:
            try:
                response = self._llm.speak(
                    "VEDA_EXPLORER",
                    "clarification",
                    f"User said: '{parsed.raw_input}'. Help them use one of: chant, listen, resolve, serve, status, help.",
                )
                return VedaResult(
                    success=True,
                    intent="unknown",
                    mode=self._mode.value,
                    response=response,
                    data={},
                    llm_used=True,
                )
            except Exception:
                pass

        return VedaResult(
            success=False,
            intent="unknown",
            mode=self._mode.value,
            response=f"Unbekannter Befehl: '{parsed.raw_input}'",
            data={},
            llm_used=False,
        )

    # =========================================================================
    # CREATIVE MODE - Full LLM Conversation (Guru Mode)
    # =========================================================================

    SYSTEM_PROMPT: str = """Du bist der VEDA EXPLORER - ein weiser Guru und technischer Experte.

DEIN WISSEN:
- Die 16 Mahajanas (Brahma, Narada, Shambhu, Vyasa, Kumaras, Kapila, Manu, Prahlada, Janaka, Bhishma, Bali, Shuka, Yamaraja, Prithu, Parashurama, Nrisimha)
- Die 4 Quarters: GENESIS (0-3), DHARMA (4-7), KARMA (8-11), MOKSHA (12-15)
- Das Mahamantra: 16 Worte, zyklisch, Yajna-Kreislauf
- Die NavaBhakti: 9 Formen der Hingabe (Sravanam, Kirtanam, Smaranam, Pada-Sevanam, Arcanam, Vandanam, Dasyam, Sakhyam, Atma-Nivedanam)

DEIN STIL:
- Technisch präzise wenn nach Code gefragt
- Weise und tiefgründig wenn nach Konzepten gefragt
- Praktisch und lösungsorientiert
- Du kannst Code schreiben, Architektur erklären, und spirituelle Konzepte mit Technik verbinden

VERFÜGBARE AKTIONEN (die du vorschlagen kannst):
- chant N: Führe N Mahamantra-Zyklen aus
- listen: Zeige System-Events
- resolve NAME: Löse Mahajana auf
- serve TASK: Erstelle eine Aufgabe

Antworte auf Deutsch oder Englisch, je nach Sprache der Frage."""

    def _handle_creative(self, text: str) -> VedaResult:
        """
        CREATIVE MODE: Full LLM conversation with context.

        The Guru speaks freely, with full knowledge of Mahamantra.
        """
        if not self._llm_available or not self._llm:
            return VedaResult(
                success=False,
                intent="creative",
                mode=self._mode.value,
                response="LLM nicht verfügbar. Verwende --mode enhanced oder restricted.",
                data={},
                llm_used=False,
            )

        try:
            # Use provider directly for full LLM power
            provider = self._llm._get_provider()
            if provider is None:
                return VedaResult(
                    success=False,
                    intent="creative",
                    mode=self._mode.value,
                    response="Kein LLM Provider verfügbar.",
                    data={},
                    llm_used=False,
                )

            # Build messages list (OpenAI/OpenRouter format)
            messages: List[Dict[str, str]] = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]

            # Add history (last 5 turns)
            for turn in self._history[-5:]:
                messages.append({"role": "user", "content": turn["user"]})
                messages.append({"role": "assistant", "content": turn["assistant"]})

            # Add current message
            messages.append({"role": "user", "content": text})

            response_obj = provider.invoke(messages=messages)
            response = response_obj.content.strip()

            # Store in history
            self._history.append({"user": text, "assistant": response})

            return VedaResult(
                success=True,
                intent="creative",
                mode=self._mode.value,
                response=response,
                data={"history_length": len(self._history)},
                llm_used=True,
            )

        except Exception as e:
            return VedaResult(
                success=False,
                intent="creative",
                mode=self._mode.value,
                response=f"LLM Fehler: {e}",
                data={"error": str(e)},
                llm_used=True,
            )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    def process(self, text: str) -> VedaResult:
        """
        Process user input through the Veda-4 pipeline.

        MODES:
        - RESTRICTED: SHABDA → ARTHA → KARMA (deterministic only)
        - ENHANCED: SHABDA → ARTHA → KARMA (LLM fallback for unknown)
        - CREATIVE: Direct LLM conversation (Guru mode)

        Args:
            text: User input

        Returns:
            VedaResult with response and metadata
        """
        if not text or not text.strip():
            return VedaResult(
                success=False,
                intent="empty",
                mode=self._mode.value,
                response="Kein Input. Tippe 'help' für Hilfe.",
                data={},
                llm_used=False,
            )

        # CREATIVE MODE: Direct to LLM (Guru speaks freely)
        if self._mode == ExplorerMode.CREATIVE:
            return self._handle_creative(text)

        # SHABDA: Parse intent (deterministic first)
        parsed = self._parse_intent_deterministic(text)

        # If unknown and LLM available, try LLM parsing
        if parsed.intent == VedaIntent.UNKNOWN and self._mode != ExplorerMode.RESTRICTED:
            parsed = self._parse_intent_llm(text)

        # KARMA: Execute
        result = self._execute_intent(parsed)

        # Store successful interactions in history (for potential mode switch)
        if result.get("success"):
            self._history.append({
                "user": text,
                "assistant": result.get("response", ""),
            })

        return result

    def repl(self) -> None:
        """
        Run interactive REPL (Read-Eval-Print Loop).

        The Veda-Explorer as interactive shell.
        """
        print("=" * 60)
        print("VEDA EXPLORER - Neuro-Symbolic Chat")
        print("=" * 60)
        print(f"Modus: {self._mode.value.upper()}")
        print(f"LLM: {'Verfügbar' if self._llm_available else 'Nicht verfügbar'}")
        print("Tippe 'help' für Befehle, 'exit' zum Beenden.")
        print("-" * 60)

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ("exit", "quit", "q"):
                    print("Jay Jagannath!")
                    break

                result = self.process(user_input)
                print()
                print(result["response"])

                if result.get("llm_used"):
                    print("  [LLM verwendet]")

            except KeyboardInterrupt:
                print("\nJay Jagannath!")
                break
            except EOFError:
                break


# =============================================================================
# SINGLETON & CONVENIENCE
# =============================================================================

# Default explorer (lazy initialized)
_explorer: Optional[VedaExplorer] = None


def get_explorer(mode: ExplorerMode = ExplorerMode.ENHANCED) -> VedaExplorer:
    """Get or create the default Veda Explorer."""
    global _explorer
    if _explorer is None or _explorer.mode != mode:
        _explorer = VedaExplorer(mode=mode)
    return _explorer


def process(text: str, mode: ExplorerMode = ExplorerMode.ENHANCED) -> VedaResult:
    """Process text through Veda Explorer."""
    explorer = get_explorer(mode)
    return explorer.process(text)


def repl(mode: ExplorerMode = ExplorerMode.ENHANCED) -> None:
    """Start interactive REPL."""
    explorer = get_explorer(mode)
    explorer.repl()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "VedaExplorer",
    "VedaResult",
    "VedaIntent",
    "ExplorerMode",
    "ParsedIntent",
    "get_explorer",
    "process",
    "repl",
]

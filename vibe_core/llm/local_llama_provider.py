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
from typing import Any, Dict, List, Optional

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
        verbose: bool = False,
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

        # Lazy load: Do not load model in __init__
        # self._load_model() will be called on first use
        if not self._model_path or not self._model_path.exists():
            logger.warning(f"No local model found. Install with: steward install-llm")

    def _ensure_loaded(self):
        """Lazy load the model if not already loaded."""
        if not self._initialized and self._model_path and self._model_path.exists():
            self._load_model()

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
        self._ensure_loaded()

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

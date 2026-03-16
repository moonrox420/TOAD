"""
Enhanced RAG System with optional local GGUF LLM backend.

This module provides an LLM-augmented code generation pipeline that can use:
  - Transformers/HuggingFace models (default, when LOCAL_GGUF_MODEL is not set)
  - A local GGUF model via llama-cpp-python (when LOCAL_GGUF_MODEL env var
    points to a valid .gguf file on disk)

Environment variables
---------------------
LOCAL_GGUF_MODEL
    Filesystem path to a .gguf model file.  When set, the system loads the
    model with llama-cpp-python instead of downloading from Hugging Face.
    Example::

        export LOCAL_GGUF_MODEL=~/.cache/huggingface/hub/models--TheBloke/CodeLlama-7B-Instruct-GGUF/blobs/codellama-7b-instruct.Q4_K_M.gguf

HF_MODEL_NAME
    Hugging Face model repository id used by the Transformers backend.
    Defaults to ``"microsoft/phi-2"``.

GGUF_N_THREADS
    Number of CPU threads for llama.cpp inference (default: 4).
    Increase for faster CPU inference on multi-core machines.

GGUF_N_GPU_LAYERS
    Number of transformer layers to offload to the GPU when llama.cpp is
    built with CUDA/Metal support (default: 0, CPU only).

GGUF_CONTEXT_SIZE
    Maximum context length passed to llama.cpp (default: 2048).
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional llama_cpp import – only required when LOCAL_GGUF_MODEL is set
# ---------------------------------------------------------------------------
try:
    import llama_cpp  # type: ignore[import]
    _LLAMA_CPP_AVAILABLE = True
except ImportError:
    _LLAMA_CPP_AVAILABLE = False

# ---------------------------------------------------------------------------
# Optional transformers import – only required for the HF backend
# ---------------------------------------------------------------------------
try:
    import transformers  # type: ignore[import]  # noqa: F401
    _TRANSFORMERS_AVAILABLE = True
except ImportError:
    _TRANSFORMERS_AVAILABLE = False

# ---------------------------------------------------------------------------
# Default generation parameters (shared across backends)
# ---------------------------------------------------------------------------
DEFAULT_MAX_NEW_TOKENS: int = 512
DEFAULT_TEMPERATURE: float = 0.7
DEFAULT_TOP_P: float = 0.95

# ---------------------------------------------------------------------------
# Backend implementations
# ---------------------------------------------------------------------------


class _StreamerCallback:
    """
    Minimal streamer shim that collects tokens and forwards them to a
    caller-supplied callback.

    The callback signature is ``callback(token: str) -> None``.
    """

    def __init__(self, callback: Callable[[str], None]) -> None:
        self._callback = callback
        self._tokens: List[str] = []

    def put(self, token: str) -> None:  # called by HF TextIteratorStreamer
        self._callback(token)
        self._tokens.append(token)

    def end(self) -> None:  # called when generation finishes
        pass

    @property
    def generated_text(self) -> str:
        return "".join(self._tokens)


class GGUFBackend:
    """
    Thin wrapper around ``llama_cpp.Llama`` for text generation.

    Parameters
    ----------
    model_path:
        Absolute path to a ``.gguf`` model file.
    n_threads:
        Number of CPU threads to use (default: ``GGUF_N_THREADS`` env var
        or 4).
    n_gpu_layers:
        Layers to offload to the GPU (default: ``GGUF_N_GPU_LAYERS`` env var
        or 0).
    context_size:
        Maximum context length (default: ``GGUF_CONTEXT_SIZE`` env var or
        2048).
    """

    def __init__(
        self,
        model_path: str,
        n_threads: int = 0,
        n_gpu_layers: int = 0,
        context_size: int = 0,
    ) -> None:
        if not _LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "llama-cpp-python is required to use a GGUF model but is not installed.\n"
                "Install it with:  pip install llama-cpp-python\n"
                "See TROUBLESHOOTING.md for details."
            )

        resolved_path = Path(model_path).expanduser().resolve()
        if not resolved_path.is_file():
            raise FileNotFoundError(
                f"GGUF model file not found: {resolved_path}\n"
                "Set LOCAL_GGUF_MODEL to the absolute path of a valid .gguf file."
            )

        # Apply env-var overrides (caller-supplied values take precedence when
        # they are non-zero; zero means "use env var or built-in default").
        n_threads = n_threads or int(os.environ.get("GGUF_N_THREADS", "4"))
        n_gpu_layers = n_gpu_layers or int(os.environ.get("GGUF_N_GPU_LAYERS", "0"))
        context_size = context_size or int(os.environ.get("GGUF_CONTEXT_SIZE", "2048"))

        logger.info(
            "Loading GGUF model: %s  (n_threads=%d, n_gpu_layers=%d, ctx=%d)",
            resolved_path,
            n_threads,
            n_gpu_layers,
            context_size,
        )

        self._model = llama_cpp.Llama(
            model_path=str(resolved_path),
            n_threads=n_threads,
            n_gpu_layers=n_gpu_layers,
            n_ctx=context_size,
        )
        self.model_path = str(resolved_path)

    # ------------------------------------------------------------------
    # Public generation API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> str:
        """
        Generate text for *prompt* and return the full completion string.

        Args:
            prompt: Input text to complete.
            max_new_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature (0 = greedy).
            top_p: Nucleus sampling probability.

        Returns:
            Generated text (excluding the prompt).
        """
        output = self._model(
            prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=False,
        )
        return output["choices"][0]["text"]

    def generate_stream(
        self,
        prompt: str,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> Generator[str, None, None]:
        """
        Stream generated tokens one at a time.

        Yields:
            Individual token strings as they are produced.
        """
        for chunk in self._model(
            prompt,
            max_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            stream=True,
        ):
            token = chunk["choices"][0]["text"]
            if token:
                yield token

    def generate_with_callback(
        self,
        prompt: str,
        on_token: Callable[[str], None],
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> str:
        """
        Generate text and invoke *on_token* for each emitted token.

        This mirrors the HF ``TextStreamer`` callback pattern used by the
        Transformers backend so the UI layer can use a single code path.

        Args:
            prompt: Input text.
            on_token: Callable invoked with each new token string.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling probability.

        Returns:
            Full generated text (excluding the prompt).
        """
        parts: List[str] = []
        for token in self.generate_stream(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        ):
            on_token(token)
            parts.append(token)
        return "".join(parts)


class TransformersBackend:
    """
    Wrapper around a Hugging Face ``transformers`` pipeline for text
    generation.

    Parameters
    ----------
    model_name:
        HuggingFace model repository id (e.g. ``"microsoft/phi-2"``).
        Defaults to the ``HF_MODEL_NAME`` environment variable, or
        ``"microsoft/phi-2"``.
    device:
        PyTorch device string (``"cpu"``, ``"cuda"``, ``"mps"`` …).
        ``None`` lets transformers auto-select.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ) -> None:
        if not _TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "The 'transformers' package is required for the HF backend but is "
                "not installed.\nInstall it with:  pip install transformers torch"
            )

        import torch  # type: ignore[import]
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline  # type: ignore[import]

        self.model_name = (
            model_name
            or os.environ.get("HF_MODEL_NAME", "microsoft/phi-2")
        )
        logger.info("Loading HF model: %s", self.model_name)

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        self._device = device
        self._pipeline = pipeline(
            "text-generation",
            model=self._model,
            tokenizer=self._tokenizer,
            device=device,
        )

    # ------------------------------------------------------------------
    # Public generation API
    # ------------------------------------------------------------------

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> str:
        """
        Generate text for *prompt* (non-streaming).

        Args:
            prompt: Input text.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling probability.

        Returns:
            Generated text (excluding the prompt).
        """
        outputs = self._pipeline(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            do_sample=temperature > 0,
            return_full_text=False,
        )
        return outputs[0]["generated_text"]

    def generate_stream(
        self,
        prompt: str,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> Generator[str, None, None]:
        """
        Stream generated text using HF ``TextIteratorStreamer``.

        Yields:
            Token strings as they are produced.
        """
        import threading  # stdlib

        from transformers import TextIteratorStreamer  # type: ignore[import]

        streamer = TextIteratorStreamer(
            self._tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        generation_kwargs: Dict[str, Any] = {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "streamer": streamer,
        }

        inputs = self._tokenizer(prompt, return_tensors="pt")
        if self._device:
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

        thread = threading.Thread(
            target=self._model.generate,
            kwargs={**inputs, **generation_kwargs},
        )
        thread.start()

        for token in streamer:
            yield token

        thread.join()

    def generate_with_callback(
        self,
        prompt: str,
        on_token: Callable[[str], None],
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> str:
        """
        Generate text and invoke *on_token* for each emitted token.

        Args:
            prompt: Input text.
            on_token: Callable invoked with each new token string.
            max_new_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling probability.

        Returns:
            Full generated text (excluding the prompt).
        """
        parts: List[str] = []
        for token in self.generate_stream(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
        ):
            on_token(token)
            parts.append(token)
        return "".join(parts)


# ---------------------------------------------------------------------------
# Backend factory
# ---------------------------------------------------------------------------


def _resolve_backend(
    local_gguf_path: Optional[str] = None,
) -> "GGUFBackend | TransformersBackend":
    """
    Choose and instantiate the correct LLM backend.

    Priority:
    1. ``local_gguf_path`` argument (explicit override)
    2. ``LOCAL_GGUF_MODEL`` environment variable
    3. Transformers/HuggingFace backend (default)

    Args:
        local_gguf_path: Optional explicit path to a GGUF file.

    Returns:
        An initialised backend object.

    Raises:
        ImportError: llama-cpp-python not installed but a GGUF path was given.
        FileNotFoundError: GGUF path given but file does not exist.
        ImportError: transformers not installed and no GGUF path provided.
    """
    gguf_path = local_gguf_path or os.environ.get("LOCAL_GGUF_MODEL", "").strip()

    if gguf_path:
        logger.info("LOCAL_GGUF_MODEL detected – using llama-cpp-python backend.")
        return GGUFBackend(gguf_path)

    logger.info("No LOCAL_GGUF_MODEL set – using Transformers/HF backend.")
    return TransformersBackend()


# ---------------------------------------------------------------------------
# Main system class
# ---------------------------------------------------------------------------


class EnhancedRAGSystem:
    """
    LLM-augmented code generation system with Retrieval-Augmented Generation.

    This class combines the RAG retrieval pipeline (from ``rag/``) with an
    LLM backend that can be either:

    * **Transformers/HuggingFace** (default) – loads the model identified by
      ``HF_MODEL_NAME`` (or ``microsoft/phi-2``) from the HF Hub.
    * **llama.cpp / GGUF** – loads a local ``.gguf`` file when
      ``LOCAL_GGUF_MODEL`` env var is set.

    Parameters
    ----------
    local_gguf_path:
        Explicit path to a GGUF model file.  Overrides ``LOCAL_GGUF_MODEL``.
    use_rag:
        Whether to enable RAG retrieval (default: ``True``).
    max_new_tokens:
        Default maximum number of tokens to generate.
    temperature:
        Default sampling temperature.
    top_p:
        Default nucleus-sampling probability.

    Examples
    --------
    Use the default HF backend::

        system = EnhancedRAGSystem()
        code = system.generate("Write a Python function that sorts a list")

    Use a local GGUF model::

        import os
        os.environ["LOCAL_GGUF_MODEL"] = (
            "~/.cache/huggingface/hub/models--TheBloke/CodeLlama-7B-Instruct-GGUF/"
            "blobs/codellama-7b-instruct.Q4_K_M.gguf"
        )
        system = EnhancedRAGSystem()
        code = system.generate("Write a Python REST API")

    Stream tokens to the terminal::

        for token in system.generate_stream("Build a CLI tool"):
            print(token, end="", flush=True)
    """

    def __init__(
        self,
        local_gguf_path: Optional[str] = None,
        use_rag: bool = True,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        temperature: float = DEFAULT_TEMPERATURE,
        top_p: float = DEFAULT_TOP_P,
    ) -> None:
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p

        # Initialise LLM backend (may raise – intentional)
        self._backend = _resolve_backend(local_gguf_path)

        # Initialise RAG (optional, fails gracefully)
        self._rag_agent = None
        if use_rag:
            self._setup_rag()

    # ------------------------------------------------------------------
    # RAG setup
    # ------------------------------------------------------------------

    def _setup_rag(self) -> None:
        """Initialise the RAG-enhanced agent, ignoring failures."""
        try:
            sys.path.insert(0, str(Path(__file__).parent))
            from rag.integration import RAGEnhancedAgent  # type: ignore[import]

            self._rag_agent = RAGEnhancedAgent(use_rag=True)
            logger.info("RAG agent initialised successfully.")
        except Exception as exc:
            logger.warning("RAG initialisation failed (%s). Continuing without RAG.", exc)
            self._rag_agent = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _retrieve_context(self, prompt: str) -> str:
        """Return a RAG context string for *prompt*, or empty string."""
        if self._rag_agent is None or not self._rag_agent.rag_available:
            return ""
        try:
            return self._rag_agent._get_rag_context(prompt) or ""
        except Exception as exc:
            logger.warning("RAG context retrieval failed: %s", exc)
            return ""

    def _build_prompt(self, user_request: str) -> str:
        """Compose the full prompt, optionally prepending RAG context."""
        rag_context = self._retrieve_context(user_request)
        if rag_context:
            return f"{rag_context}\n\n### Request\n{user_request}\n\n### Response\n"
        return f"### Request\n{user_request}\n\n### Response\n"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def backend_type(self) -> str:
        """Return ``"gguf"`` or ``"transformers"``."""
        return "gguf" if isinstance(self._backend, GGUFBackend) else "transformers"

    def generate(
        self,
        user_request: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Generate a response for *user_request* (non-streaming).

        Args:
            user_request: Natural-language instruction or code request.
            max_new_tokens: Override default max tokens.
            temperature: Override default temperature.
            top_p: Override default top-p.

        Returns:
            Generated text string.
        """
        prompt = self._build_prompt(user_request)
        return self._backend.generate(
            prompt,
            max_new_tokens=max_new_tokens or self.max_new_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            top_p=top_p if top_p is not None else self.top_p,
        )

    def generate_stream(
        self,
        user_request: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> Generator[str, None, None]:
        """
        Stream generated tokens for *user_request*.

        Yields:
            Token strings as they are produced by the backend.
        """
        prompt = self._build_prompt(user_request)
        yield from self._backend.generate_stream(
            prompt,
            max_new_tokens=max_new_tokens or self.max_new_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            top_p=top_p if top_p is not None else self.top_p,
        )

    def generate_with_callback(
        self,
        user_request: str,
        on_token: Callable[[str], None],
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        Generate a response and call *on_token* for each token emitted.

        This is the primary method for UI integration: pass a callback that
        updates the display, chat widget, or terminal.

        Args:
            user_request: Natural-language instruction or code request.
            on_token: Callable invoked with each new token string.
            max_new_tokens: Override default max tokens.
            temperature: Override default temperature.
            top_p: Override default top-p.

        Returns:
            Full generated text.
        """
        prompt = self._build_prompt(user_request)
        return self._backend.generate_with_callback(
            prompt,
            on_token=on_token,
            max_new_tokens=max_new_tokens or self.max_new_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            top_p=top_p if top_p is not None else self.top_p,
        )

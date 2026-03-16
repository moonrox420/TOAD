"""
Enhanced RAG System with local GGUF model support.

This module extends the base RAG pipeline with an LLM inference layer that can
run a local GGUF model (via llama-cpp-python) when a model file is available,
and falls back gracefully to HuggingFace-hosted inference when it is not.

Quick-start
-----------
**Option A – environment variable (recommended)**::

    # Linux / macOS
    export LOCAL_MODEL_PATH="/path/to/your/model.gguf"
    python enhanced_rag_system.py

    # Windows PowerShell
    $env:LOCAL_MODEL_PATH = "C:\\Users\\droxa\\.cache\\huggingface\\hub\\...\\q6_k.gguf"
    python enhanced_rag_system.py

**Option B – config file** (``rag_data/config.yaml``)::

    llm:
      local_model_path: "C:/Users/droxa/.cache/huggingface/hub/.../q6_k.gguf"
      n_ctx: 4096
      n_gpu_layers: 0      # set to -1 to offload all layers to GPU
      max_tokens: 2048
      temperature: 0.2

**Option C – Python API**::

    from enhanced_rag_system import EnhancedRAGSystem
    from rag.config import RAGConfig, LLMConfig

    config = RAGConfig()
    config.llm.local_model_path = "/path/to/model.gguf"
    system = EnhancedRAGSystem(config=config)
    answer = system.generate("Write a Python function that sorts a list")
    print(answer)

When ``local_model_path`` is ``None`` (or points to a file that does not
exist) the system prints a warning and returns an empty string from the LLM
step so that the rest of the RAG pipeline (retrieval, context formatting) still
works unaffected.  Existing defaults for HuggingFace-hosted models are
preserved in ``LLMConfig.hf_model_name``.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Ensure the TOAD root is importable
sys.path.insert(0, str(Path(__file__).parent))

from rag.config import LLMConfig, RAGConfig, get_config, DEFAULT_HF_MODEL_NAME
from rag.retriever import RAGRetriever, RetrievalResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM back-ends
# ---------------------------------------------------------------------------

class LocalGGUFModel:
    """
    Wrapper around a local GGUF model loaded via llama-cpp-python.

    Parameters
    ----------
    config:
        ``LLMConfig`` instance.  ``config.local_model_path`` must point to an
        existing ``.gguf`` file on disk.

    Raises
    ------
    ImportError
        If ``llama-cpp-python`` is not installed.
    FileNotFoundError
        If ``config.local_model_path`` does not point to an existing file.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._llm = None
        self._load()

    def _load(self) -> None:
        """Load the GGUF model into memory."""
        model_path = self.config.local_model_path
        if not model_path:
            raise ValueError("local_model_path is not set in LLMConfig.")

        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Local GGUF model not found at '{model_path}'. "
                "Verify the path or unset LOCAL_MODEL_PATH to use the HF fallback."
            )

        try:
            from llama_cpp import Llama  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "llama-cpp-python is required to run a local GGUF model. "
                "Install it with:\n"
                "  pip install llama-cpp-python\n"
                "or, for GPU support:\n"
                "  CMAKE_ARGS='-DLLAMA_CUDA=on' pip install llama-cpp-python"
            ) from exc

        logger.info("Loading local GGUF model from %s …", model_path)
        self._llm = Llama(
            model_path=str(path),
            n_ctx=self.config.n_ctx,
            n_gpu_layers=self.config.n_gpu_layers,
            verbose=False,
        )
        logger.info("Local GGUF model loaded successfully.")

    def generate(self, prompt: str) -> str:
        """
        Run inference with the local GGUF model.

        Parameters
        ----------
        prompt:
            The full prompt string to send to the model.

        Returns
        -------
        str
            The generated text (choices[0]["text"]).
        """
        if self._llm is None:
            return ""

        response = self._llm(
            prompt,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            echo=False,
        )
        return response["choices"][0]["text"].strip()

    @property
    def is_local(self) -> bool:
        """Always ``True`` for this backend."""
        return True


class HFHostedModel:
    """
    Placeholder / stub for a HuggingFace-hosted inference backend.

    This class exists so that the ``EnhancedRAGSystem`` always has *something*
    to call for generation even when the optional ``llama-cpp-python`` package
    is absent and no local model is available.  In production you would replace
    the body of ``generate`` with an ``openai`` / ``huggingface_hub`` /
    ``transformers`` call.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        logger.warning(
            "No local GGUF model configured. "
            "Set LOCAL_MODEL_PATH (or llm.local_model_path in config.yaml) "
            "to enable local inference. "
            "HF model name: %s",
            config.hf_model_name or DEFAULT_HF_MODEL_NAME,
        )

    def generate(self, prompt: str) -> str:
        """
        Return an empty string.

        This is an intentional stub: the ``prompt`` argument is accepted so that
        subclasses can override this method and use it.  Override this method
        (or replace ``HFHostedModel`` entirely) to perform real HuggingFace
        inference, e.g. via ``huggingface_hub.InferenceClient`` or
        ``transformers.pipeline``.
        """
        logger.debug(
            "HFHostedModel.generate() called but no HF client is configured. "
            "Returning empty string."
        )
        return ""

    @property
    def is_local(self) -> bool:
        """Always ``False`` for this backend."""
        return False


# ---------------------------------------------------------------------------
# Public high-level interface
# ---------------------------------------------------------------------------

class EnhancedRAGSystem:
    """
    RAG retrieval pipeline with an optional LLM inference step.

    The system selects the LLM backend in this order:

    1. If ``config.llm.local_model_path`` resolves to an existing ``.gguf``
       file **and** ``llama-cpp-python`` is installed → ``LocalGGUFModel``.
    2. Otherwise → ``HFHostedModel`` (stub; override for real HF calls).

    Parameters
    ----------
    config:
        Optional ``RAGConfig``.  When ``None`` the global config is used,
        which already applies the ``LOCAL_MODEL_PATH`` environment variable.

    Example
    -------
    >>> system = EnhancedRAGSystem()
    >>> answer = system.generate("Create a Python class for a binary search tree")
    >>> print(answer)
    """

    def __init__(self, config: Optional[RAGConfig] = None) -> None:
        self.config = config or get_config()
        self._retriever: Optional[RAGRetriever] = None
        self._llm = self._build_llm()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_llm(self):
        """Instantiate the appropriate LLM backend."""
        llm_cfg = self.config.llm
        local_path = llm_cfg.local_model_path

        if local_path and Path(local_path).exists():
            try:
                return LocalGGUFModel(llm_cfg)
            except ImportError as exc:
                logger.warning(
                    "Could not load local GGUF model (%s). "
                    "Falling back to HFHostedModel stub. "
                    "Install llama-cpp-python to enable local inference.",
                    exc,
                )
        elif local_path:
            logger.warning(
                "LOCAL_MODEL_PATH is set to '%s' but the file does not exist. "
                "Falling back to HFHostedModel stub.",
                local_path,
            )

        return HFHostedModel(llm_cfg)

    def _get_retriever(self) -> RAGRetriever:
        """Lazily initialise and cache the RAGRetriever."""
        if self._retriever is None:
            self._retriever = RAGRetriever(config=self.config)
        return self._retriever

    def _build_prompt(
        self,
        query: str,
        rag_context: str,
    ) -> str:
        """Combine RAG context and user query into a single prompt string."""
        if rag_context:
            return (
                f"You are an expert software engineer.\n\n"
                f"Here are some relevant coding examples:\n{rag_context}\n\n"
                f"Using the examples above as inspiration, answer the following:\n"
                f"{query}\n\n"
                f"### Response:"
            )
        return (
            f"You are an expert software engineer.\n\n"
            f"{query}\n\n"
            f"### Response:"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def llm_backend(self) -> str:
        """Return ``'local'`` or ``'hf_hosted'`` depending on active backend."""
        return "local" if self._llm.is_local else "hf_hosted"

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant coding examples from the vector index.

        Parameters
        ----------
        query:
            The user query / requirements string.
        top_k:
            Number of results.  Defaults to ``config.retrieval.top_k``.

        Returns
        -------
        List[RetrievalResult]
            Empty list if the RAG index is not yet built.
        """
        retriever = self._get_retriever()
        if not retriever.is_available():
            logger.warning(
                "RAG index not found. Run 'python cli.py rag build' to build it. "
                "Continuing without retrieval context."
            )
            return []

        top_k = top_k or self.config.retrieval.top_k
        try:
            return retriever.retrieve(query, top_k=top_k)
        except Exception as exc:
            logger.warning("RAG retrieval failed: %s", exc)
            return []

    def generate(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_rag: bool = True,
    ) -> str:
        """
        Retrieve relevant examples and run LLM inference.

        Parameters
        ----------
        query:
            Natural-language requirement or question.
        top_k:
            Number of RAG examples to retrieve.
        use_rag:
            Set to ``False`` to skip retrieval and send the bare query to the
            LLM.

        Returns
        -------
        str
            Generated text from the active LLM backend, or an empty string if
            no LLM backend produced output.
        """
        rag_context = ""
        if use_rag:
            results = self.retrieve(query, top_k=top_k)
            if results:
                rag_context = self._get_retriever().format_context(results)

        prompt = self._build_prompt(query, rag_context)
        response = self._llm.generate(prompt)
        return response

    def generate_with_details(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """
        Like ``generate`` but return a dict with full details.

        Returns
        -------
        dict
            Keys: ``response``, ``rag_results``, ``rag_context``,
            ``llm_backend``, ``local_model_path``.
        """
        rag_results: List[RetrievalResult] = []
        rag_context = ""

        if use_rag:
            rag_results = self.retrieve(query, top_k=top_k)
            if rag_results:
                rag_context = self._get_retriever().format_context(rag_results)

        prompt = self._build_prompt(query, rag_context)
        response = self._llm.generate(prompt)

        return {
            "response": response,
            "rag_results": [r.to_dict() for r in rag_results],
            "rag_context": rag_context,
            "llm_backend": self.llm_backend,
            "local_model_path": self.config.llm.local_model_path,
        }


# ---------------------------------------------------------------------------
# Module-level convenience helpers
# ---------------------------------------------------------------------------

def create_enhanced_rag_system(
    local_model_path: Optional[str] = None,
    config: Optional[RAGConfig] = None,
) -> EnhancedRAGSystem:
    """
    Factory function: build an ``EnhancedRAGSystem`` with an optional model path.

    ``local_model_path`` overrides both the environment variable and any value
    already in ``config.llm.local_model_path``.

    Parameters
    ----------
    local_model_path:
        Explicit path to a ``.gguf`` file.  When ``None`` the value from
        ``LOCAL_MODEL_PATH`` env var or ``config.yaml`` is used.
    config:
        Optional ``RAGConfig``.  When ``None`` the global config is used.

    Returns
    -------
    EnhancedRAGSystem
    """
    cfg = config or get_config()
    if local_model_path is not None:
        cfg.llm.local_model_path = local_model_path
    return EnhancedRAGSystem(config=cfg)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )


if __name__ == "__main__":
    _setup_logging()

    query = (
        " ".join(sys.argv[1:])
        or "Write a Python function that returns the nth Fibonacci number."
    )

    system = EnhancedRAGSystem()
    print(f"\nLLM backend  : {system.llm_backend}")
    print(f"Local model  : {system.config.llm.local_model_path or '(none)'}")
    print(f"\nQuery: {query}\n")

    result = system.generate(query)
    if result:
        print("=== Response ===")
        print(result)
    else:
        print(
            "[INFO] No LLM output – either no local model is loaded or the HF "
            "backend stub returned an empty string.\n"
            "Set LOCAL_MODEL_PATH to your .gguf file and re-run."
        )

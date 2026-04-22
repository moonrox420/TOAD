"""
Enhanced RAG System for DroxAI Code Generation Agent.

Provides document ingestion (PDF, DOCX, TXT) and retrieval-augmented generation
on top of the existing RAG pipeline.

Dependencies:
    - python-docx  (for .docx support)  -- install with: pip install python-docx
    - PyMuPDF      (for .pdf support)   -- install with: pip install pymupdf
      Falls back gracefully when PyMuPDF is not installed.
    - See requirements.txt for the full dependency list.

Usage:
    from enhanced_rag_system import EnhancedRAGSystem
    system = EnhancedRAGSystem()
    system.ingest_file("my_document.docx")
    results = system.retrieve("how do I implement authentication?")
Enhanced RAG System with local GGUF model support.

This script combines the TOAD RAG retrieval pipeline with an LLM backend for
full Retrieval-Augmented Generation (RAG) inference.

Backend selection (in priority order):

1. ``LOCAL_GGUF_MODEL`` environment variable set →
   Uses **llama-cpp-python** with the given ``.gguf`` file path.
   The HuggingFace Transformers model is **never downloaded** in this path.

2. Default (``LOCAL_GGUF_MODEL`` not set) →
   Uses **HuggingFace Transformers** (``mistralai/Mistral-7B-Instruct-v0.2``).
   This will download ~14.5 GB on the first run.

Usage examples::

    # Use a local GGUF model (skips HF download entirely)
    LOCAL_GGUF_MODEL=/path/to/mistral.gguf python enhanced_rag_system.py

    # Use the HuggingFace Transformers backend (default, requires ~14.5 GB download)
    python enhanced_rag_system.py

See TROUBLESHOOTING.md for help avoiding unwanted HF downloads.

Notes:
    The ``torch_dtype`` parameter was deprecated in recent versions of
    ``transformers``.  This module passes ``dtype`` instead, which is the
    current recommended approach.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# python-docx import (required for .docx support)
# Install with:  pip install python-docx
# NOTE: do NOT install the legacy "docx" package — it is Python-2-only and
#       will raise "ModuleNotFoundError: No module named 'exceptions'" on
#       Python 3.  Use "python-docx" instead.
# ---------------------------------------------------------------------------
try:
    from docx import Document as DocxDocument
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False
    DocxDocument = None  # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# PyMuPDF import (optional, for PDF support)
# Install with:  pip install pymupdf
# Falls back gracefully when not installed.
# ---------------------------------------------------------------------------
try:
    import fitz as _fitz  # PyMuPDF
    _PYMUPDF_AVAILABLE = True
except ImportError:
    _fitz = None  # type: ignore[assignment]
    _PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancedRAGSystem:
    """
    Enhanced RAG system with document ingestion support.

    Supports ingesting plain-text (.txt), Word (.docx), and PDF (.pdf)
    documents into the RAG index for subsequent retrieval.

    Features:
        - DOCX ingestion via python-docx
        - PDF ingestion via PyMuPDF (optional; skips PDFs when unavailable)
        - TXT ingestion with automatic encoding detection
        - Falls back gracefully when optional dependencies are missing

    Example:
        >>> system = EnhancedRAGSystem()
        >>> system.ingest_file("spec.docx")
        >>> results = system.retrieve("REST API authentication")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the enhanced RAG system.

        Args:
            config: Optional configuration dictionary overriding defaults.
        """
        self.config = config or {}
        self._documents: List[Dict[str, Any]] = []

        if not _DOCX_AVAILABLE:
            logger.warning(
                "python-docx is not installed. DOCX ingestion will be skipped. "
                "Install with: pip install python-docx"
            )
        if not _PYMUPDF_AVAILABLE:
            logger.warning(
                "PyMuPDF is not installed. PDF ingestion will be skipped. "
                "Install with: pip install pymupdf"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_file(self, file_path: str) -> bool:
        """
        Ingest a single document file into the RAG index.

        Supported formats:
            - ``.txt``  – plain text
            - ``.docx`` – Microsoft Word (requires python-docx)
            - ``.pdf``  – PDF (requires PyMuPDF)

        Args:
            file_path: Path to the file to ingest.

        Returns:
            True if the file was ingested successfully, False otherwise.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = path.suffix.lower()
        text: Optional[str] = None

        if suffix == ".txt":
            text = self._read_txt(path)
        elif suffix == ".docx":
            text = self._read_docx(path)
        elif suffix == ".pdf":
            text = self._read_pdf(path)
        else:
            logger.warning(f"Unsupported file type '{suffix}' for file: {file_path}")
            return False

        if text is None:
            return False

        self._documents.append({"source": str(path), "text": text})
        logger.info(f"Ingested document: {path.name} ({len(text)} chars)")
        return True

    def ingest_directory(self, directory: str, recursive: bool = False) -> int:
        """
        Ingest all supported documents from a directory.

        Args:
            directory: Path to the directory to scan.
            recursive: If True, also scans sub-directories.

        Returns:
            Number of documents successfully ingested.
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        pattern = "**/*" if recursive else "*"
        supported = {".txt", ".docx", ".pdf"}
        count = 0

        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported:
                try:
                    if self.ingest_file(str(file_path)):
                        count += 1
                except Exception as exc:
                    logger.error(f"Failed to ingest {file_path}: {exc}")

        logger.info(f"Ingested {count} document(s) from {directory}")
        return count

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant document passages for a query.

        Args:
            query: The natural-language query.
            top_k: Maximum number of results to return.

        Returns:
            List of dicts, each with ``source`` and ``text`` keys.
        """
        if not self._documents:
            logger.warning("No documents have been ingested yet.")
            return []

        query_lower = query.lower()
        scored: List[Dict[str, Any]] = []

        for doc in self._documents:
            text_lower = doc["text"].lower()
            # Simple term-overlap score as baseline when no vector index exists.
        # TODO: integrate with the FAISS-based RAGIndexBuilder / RAGRetriever
        #       from rag/integration.py for full vector-similarity retrieval.
            query_terms = set(query_lower.split())
            text_terms = set(text_lower.split())
            overlap = len(query_terms & text_terms)
            if overlap > 0:
                scored.append({"source": doc["source"], "text": doc["text"], "_score": overlap})

        scored.sort(key=lambda d: d["_score"], reverse=True)
        results = [{"source": d["source"], "text": d["text"]} for d in scored[:top_k]]
        return results

    def get_document_count(self) -> int:
        """Return the number of ingested documents."""
        return len(self._documents)

    def clear(self) -> None:
        """Clear all ingested documents from memory."""
        self._documents.clear()
        logger.info("Cleared all ingested documents.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_txt(self, path: Path) -> Optional[str]:
        """Read a plain-text file, trying UTF-8 then latin-1 encoding."""
        for encoding in ("utf-8", "latin-1"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        logger.error(f"Could not decode text file: {path}")
        return None

    def _read_docx(self, path: Path) -> Optional[str]:
        """
        Read a DOCX file using python-docx.

        Returns None (with a warning) when python-docx is not installed.
        """
        if not _DOCX_AVAILABLE:
            logger.warning(
                f"Skipping DOCX file '{path.name}': python-docx is not installed. "
                "Install with: pip install python-docx"
            )
            return None

        try:
            doc = DocxDocument(str(path))  # type: ignore[call-arg]
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n".join(paragraphs)
        except Exception as exc:
            logger.error(f"Failed to read DOCX file '{path}': {exc}", exc_info=True)
            return None

    def _read_pdf(self, path: Path) -> Optional[str]:
        """
        Read a PDF file using PyMuPDF (fitz).

        Returns None (with a warning) when PyMuPDF is not installed.
        """
        if not _PYMUPDF_AVAILABLE:
            logger.warning(
                f"Skipping PDF file '{path.name}': PyMuPDF is not installed. "
                "Install with: pip install pymupdf"
            )
            return None

        try:
            pages: List[str] = []
            with _fitz.open(str(path)) as pdf:  # type: ignore[union-attr]
                for page in pdf:
                    pages.append(page.get_text())
            return "\n".join(pages)
        except Exception as exc:
            logger.error(f"Failed to read PDF file '{path}': {exc}", exc_info=True)
            return None
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure the repo root is on the path so ``rag`` can be imported
sys.path.insert(0, str(Path(__file__).parent))

from rag import RAGRetriever, get_config
from rag.config import RAGConfig
from rag.retriever import RetrievalResult

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default HuggingFace model used when ``LOCAL_GGUF_MODEL`` is **not** set.
#: Downloading this model requires ~14.5 GB of disk / bandwidth.
DEFAULT_HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"


# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------


def _load_llama_cpp_model(model_path: str) -> Any:
    """Load a local GGUF model using llama-cpp-python.

    Args:
        model_path: Absolute or relative path to the ``.gguf`` model file.

    Returns:
        A ``llama_cpp.Llama`` instance ready for inference.

    Raises:
        ImportError: If ``llama-cpp-python`` is not installed.
        FileNotFoundError: If the GGUF file does not exist at *model_path*.
    """
    try:
        from llama_cpp import Llama  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "llama-cpp-python is not installed. "
            "Install it with:  pip install llama-cpp-python"
        ) from exc

    resolved = Path(model_path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(
            f"GGUF model not found: {resolved}\n"
            "Set LOCAL_GGUF_MODEL to a valid .gguf file path."
        )

    logger.info("Loading local GGUF model from: %s", resolved)
    llm = Llama(model_path=str(resolved), n_ctx=4096, n_threads=4)
    logger.info("GGUF model loaded successfully via llama-cpp-python")
    return llm


def _load_hf_model(model_name: str = DEFAULT_HF_MODEL) -> tuple:
    """Load a HuggingFace Transformers model.

    This function triggers a model download (~14.5 GB for the default model)
    if the model is not already cached locally.  Set ``LOCAL_GGUF_MODEL`` to
    avoid this download and use a local GGUF file instead.

    Args:
        model_name: HuggingFace model identifier.

    Returns:
        A ``(model, tokenizer)`` tuple.

    Raises:
        ImportError: If ``transformers`` or ``torch`` are not installed.
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise ImportError(
            "transformers and torch are required for the HF backend. "
            "Install with:  pip install transformers torch\n"
            "Or avoid this entirely by setting LOCAL_GGUF_MODEL=/path/to/model.gguf"
        ) from exc

    logger.info(
        "Loading HuggingFace model: %s  "
        "(first run downloads ~14.5 GB – set LOCAL_GGUF_MODEL to skip this)",
        model_name,
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # ``dtype`` is the current recommended parameter (``torch_dtype`` is deprecated).
    # See: https://huggingface.co/docs/transformers/main_classes/model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=torch.float16,   # use ``dtype``, not the deprecated ``torch_dtype``
        device_map="auto",
    )

    logger.info("HuggingFace model '%s' loaded successfully", model_name)
    return model, tokenizer


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class EnhancedRAGSystem:
    """RAG system with pluggable LLM backends.

    Backend is selected automatically:

    * If ``LOCAL_GGUF_MODEL`` env var is set (or *gguf_model_path* is passed),
      the llama.cpp backend is used and **no HuggingFace model is downloaded**.
    * Otherwise the HuggingFace Transformers backend is initialised (default).

    Example::

        # Llama.cpp path (no HF download)
        os.environ["LOCAL_GGUF_MODEL"] = "/models/mistral-7b-q4.gguf"
        system = EnhancedRAGSystem()

        # HF Transformers path (default)
        system = EnhancedRAGSystem()

    Attributes:
        backend: Name of the active LLM backend (``"llama_cpp"`` or
            ``"hf_transformers"``).
    """

    def __init__(
        self,
        gguf_model_path: Optional[str] = None,
        hf_model_name: str = DEFAULT_HF_MODEL,
        config: Optional[RAGConfig] = None,
    ) -> None:
        """Initialise the enhanced RAG system.

        Args:
            gguf_model_path: Path to a local GGUF model file.  Overrides the
                ``LOCAL_GGUF_MODEL`` environment variable when provided.
                When either this argument or the env var is set, the HF model
                is **never** downloaded.
            hf_model_name: HuggingFace model identifier used as the fallback
                when no GGUF path is available.
            config: RAG configuration.  Uses the global config when *None*.
        """
        self.config: RAGConfig = config or get_config()
        self._retriever: Optional[RAGRetriever] = None
        self._llm: Any = None
        self._tokenizer: Any = None
        self._backend: str = "none"

        # Resolve backend: explicit arg > env var > HF default
        resolved_gguf: Optional[str] = gguf_model_path or os.environ.get(
            "LOCAL_GGUF_MODEL"
        )

        if resolved_gguf:
            # ── llama.cpp path ────────────────────────────────────────────────
            # HuggingFace Transformers is never imported or downloaded here.
            self._init_llama_cpp(resolved_gguf)
        else:
            # ── HuggingFace Transformers path (default) ───────────────────────
            self._init_hf_transformers(hf_model_name)

        self._setup_retriever()

    # ------------------------------------------------------------------
    # Backend initialisation
    # ------------------------------------------------------------------

    def _init_llama_cpp(self, model_path: str) -> None:
        """Initialise the llama.cpp backend.

        The HuggingFace Transformers library is **not** imported and no model
        is downloaded from HuggingFace when this method is called.

        Args:
            model_path: Path to the local GGUF model file.
        """
        self._llm = _load_llama_cpp_model(model_path)
        self._backend = "llama_cpp"

    def _init_hf_transformers(self, model_name: str) -> None:
        """Initialise the HuggingFace Transformers backend.

        Args:
            model_name: HuggingFace model identifier.
        """
        self._llm, self._tokenizer = _load_hf_model(model_name)
        self._backend = "hf_transformers"

    # ------------------------------------------------------------------
    # RAG setup
    # ------------------------------------------------------------------

    def _setup_retriever(self) -> None:
        """Initialise the RAG retriever from an existing FAISS index."""
        try:
            self._retriever = RAGRetriever(config=self.config)
            if self._retriever.is_available():
                logger.info("RAG retriever ready")
            else:
                logger.warning(
                    "RAG index not found. "
                    "Build it first with: "
                    "python -c \"from rag import build_rag_index; build_rag_index()\""
                )
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            logger.warning("RAG retriever initialisation failed: %s", exc)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def backend(self) -> str:
        """Currently active LLM backend name."""
        return self._backend

    @property
    def rag_available(self) -> bool:
        """Whether the RAG index is loaded and ready."""
        return self._retriever is not None and self._retriever.is_available()

    # ------------------------------------------------------------------
    # Generation helpers
    # ------------------------------------------------------------------

    def _generate_llama_cpp(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text using the llama.cpp backend.

        Args:
            prompt: Input prompt string.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Generated text string.
        """
        output = self._llm(prompt, max_tokens=max_tokens, echo=False)
        return output["choices"][0]["text"].strip()

    def _generate_hf(self, prompt: str, max_new_tokens: int = 512) -> str:
        """Generate text using the HuggingFace Transformers backend.

        Args:
            prompt: Input prompt string.
            max_new_tokens: Maximum number of new tokens to generate.

        Returns:
            Generated text string (decoded, without the prompt).
        """
        import torch  # local import – only reached via HF backend

        inputs = self._tokenizer(prompt, return_tensors="pt").to(
            self._llm.device
        )
        with torch.no_grad():
            output_ids = self._llm.generate(
                **inputs, max_new_tokens=max_new_tokens
            )
        # Decode only the newly generated tokens (skip the prompt)
        prompt_length = inputs["input_ids"].shape[1]
        return self._tokenizer.decode(
            output_ids[0][prompt_length:], skip_special_tokens=True
        ).strip()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate a response using the active LLM backend.

        Args:
            prompt: Input prompt string.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            Generated text string.

        Raises:
            RuntimeError: If no LLM backend has been initialised.
        """
        if self._backend == "llama_cpp":
            return self._generate_llama_cpp(prompt, max_tokens=max_tokens)
        if self._backend == "hf_transformers":
            return self._generate_hf(prompt, max_new_tokens=max_tokens)
        raise RuntimeError("No LLM backend initialised")

    def query(
        self,
        question: str,
        top_k: int = 5,
        max_tokens: int = 512,
    ) -> Dict[str, Any]:
        """Full RAG pipeline: retrieve relevant context then generate an answer.

        Args:
            question: The user question or coding task description.
            top_k: Number of RAG examples to retrieve from the index.
            max_tokens: Maximum tokens to generate in the response.

        Returns:
            Dictionary with keys:

            * ``answer`` – generated response string
            * ``context`` – formatted RAG context that was prepended to the prompt
            * ``backend`` – name of the active LLM backend
            * ``rag_results`` – list of retrieved example dicts
        """
        rag_context: str = ""
        rag_results: List[RetrievalResult] = []

        if self.rag_available and self._retriever is not None:
            try:
                rag_results = self._retriever.retrieve(question, top_k=top_k)
                rag_context = self._retriever.format_context(rag_results)
            except (OSError, RuntimeError, ValueError) as exc:
                logger.warning("RAG retrieval failed: %s", exc)

        if rag_context:
            full_prompt = (
                "Use the following coding examples as context:\n\n"
                f"{rag_context}\n\n"
                f"Now answer this question:\n{question}"
            )
        else:
            full_prompt = question

        answer = self.generate(full_prompt, max_tokens=max_tokens)

        return {
            "answer": answer,
            "context": rag_context,
            "backend": self._backend,
            "rag_results": [r.to_dict() for r in rag_results],
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Simple CLI entry point for quick interactive testing."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    )

    gguf_path = os.environ.get("LOCAL_GGUF_MODEL")
    if gguf_path:
        print(f"[EnhancedRAGSystem] Using local GGUF model: {gguf_path}")
    else:
        print(
            "[EnhancedRAGSystem] LOCAL_GGUF_MODEL not set – "
            f"will download HF model '{DEFAULT_HF_MODEL}' (~14.5 GB).\n"
            "  Tip: set LOCAL_GGUF_MODEL=/path/to/model.gguf to skip the download."
        )

    system = EnhancedRAGSystem()
    print(f"[EnhancedRAGSystem] Backend: {system.backend}")
    print(f"[EnhancedRAGSystem] RAG available: {system.rag_available}")

    while True:
        try:
            question = input("\nEnter your question (Ctrl-C to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not question:
            continue

        result = system.query(question)
        print("\n--- Answer ---")
        print(result["answer"])
        print(f"\n[Backend: {result['backend']}  |  RAG results: {len(result['rag_results'])}]")


if __name__ == "__main__":
    main()

"""
Enhanced RAG System with PDF document ingestion support.

Extends the core RAG pipeline with the ability to ingest PDF files using
PyMuPDF (fitz) when available, with an automatic fallback to PyPDF2.
The rest of the RAG pipeline (FAISS indexing, retrieval, generation) is
unchanged; only the PDF-to-text extraction layer switches libraries.

Usage::

    system = EnhancedRAGSystem()
    system.ingest_documents()
    results = system.retrieve("How do I implement rate limiting?")
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

# ---------------------------------------------------------------------------
# Optional PDF library import with graceful fallback
# ---------------------------------------------------------------------------
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False

from PyPDF2 import PdfReader
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract all text from a PDF file.

    Uses PyMuPDF (fitz) when available for richer extraction (layout
    preservation, embedded-image skipping).  Falls back to PyPDF2 so the
    application remains functional even when PyMuPDF is not installed.

    Args:
        pdf_path: Absolute or relative path to the target ``.pdf`` file.

    Returns:
        A single string containing all extracted text, with pages
        separated by newlines.

    Raises:
        FileNotFoundError: If ``pdf_path`` does not exist.
        ValueError: If the file is not a valid PDF.

    Examples:
        >>> text = extract_text_from_pdf(Path("report.pdf"))
        >>> print(text[:200])
        'Introduction ...'
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if HAS_PYMUPDF:
        return _extract_with_pymupdf(pdf_path)
    return _extract_with_pypdf2(pdf_path)


def _extract_with_pymupdf(pdf_path: Path) -> str:
    """
    Extract text using PyMuPDF (fitz).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If PyMuPDF cannot open the file as a PDF.
    """
    try:
        doc = fitz.open(str(pdf_path))  # type: ignore[union-attr]
        pages: List[str] = []
        for page in doc:
            pages.append(page.get_text())
        doc.close()
        text = "\n".join(pages)
        logger.debug("PyMuPDF extracted %d chars from %s", len(text), pdf_path)
        return text
    except Exception as exc:
        raise ValueError(f"PyMuPDF could not read {pdf_path}: {exc}") from exc


def _extract_with_pypdf2(pdf_path: Path) -> str:
    """
    Extract text using PyPDF2 (fallback when PyMuPDF is absent).

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If PyPDF2 cannot parse the file.
    """
    try:
        reader = PdfReader(str(pdf_path))
        pages: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            pages.append(page_text)
        text = "\n".join(pages)
        logger.debug("PyPDF2 extracted %d chars from %s", len(text), pdf_path)
        return text
    except Exception as exc:
        raise ValueError(f"PyPDF2 could not read {pdf_path}: {exc}") from exc


class EnhancedRAGSystem:
    """
    Enhanced RAG system supporting PDF, plain-text, and Markdown document ingestion.

    Wraps the TOAD RAG pipeline with an enriched document-loading layer that
    transparently handles PDF files via PyMuPDF or PyPDF2.

    Attributes:
        docs_dir: Root directory to search for documents.
        chunk_size: Target word count per chunk.
        chunk_overlap: Word overlap between consecutive chunks.
        chunks: All ingested text chunks.
        metadata: Per-chunk source metadata.

    Example::

        system = EnhancedRAGSystem(docs_dir=Path("data/raw"))
        system.ingest_documents()
        hits = system.retrieve("REST API authentication")
        for hit in hits:
            print(hit["chunk"][:120])
    """

    SUPPORTED_EXTENSIONS: Tuple[str, ...] = (".pdf", ".txt", ".md", ".py", ".rst")

    def __init__(
        self,
        docs_dir: Optional[Path] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        """
        Initialise the enhanced RAG system.

        Args:
            docs_dir: Directory to scan for documents (defaults to ``data/raw``).
            chunk_size: Number of words per chunk.
            chunk_overlap: Number of words shared between adjacent chunks.
        """
        self.docs_dir: Path = docs_dir or Path("data/raw")
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

        backend = "PyMuPDF" if HAS_PYMUPDF else "PyPDF2"
        logger.info("EnhancedRAGSystem initialised (PDF backend: %s)", backend)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ingest_documents(self) -> int:
        """
        Ingest all supported documents found under ``docs_dir``.

        Walks the directory tree and processes each file according to its
        extension.  PDF files are handled by :func:`extract_text_from_pdf`.

        Returns:
            Total number of chunks created.

        Raises:
            FileNotFoundError: If ``docs_dir`` does not exist.
        """
        if not self.docs_dir.exists():
            raise FileNotFoundError(f"Documents directory not found: {self.docs_dir}")

        self.chunks.clear()
        self.metadata.clear()

        files = [
            p
            for p in self.docs_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in self.SUPPORTED_EXTENSIONS
        ]

        logger.info("Found %d files to ingest in %s", len(files), self.docs_dir)

        for file_path in files:
            try:
                text = self._read_file(file_path)
                new_chunks = self._split_text(text)
                for idx, chunk in enumerate(new_chunks):
                    self.chunks.append(chunk)
                    self.metadata.append(
                        {
                            "source": str(file_path),
                            "chunk_id": idx,
                            "extension": file_path.suffix.lower(),
                        }
                    )
            except Exception as exc:
                logger.warning("Skipping %s — %s", file_path, exc)

        logger.info("Ingested %d chunks from %d files", len(self.chunks), len(files))
        return len(self.chunks)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Return the top-k chunks most relevant to *query* (lexical fallback).

        This lightweight implementation scores chunks by keyword overlap so
        the system stays functional without FAISS.  Swap for the full FAISS
        retriever from :mod:`rag.retriever` in production.

        Args:
            query: Natural-language or code search query.
            top_k: Maximum number of results to return.

        Returns:
            List of dicts, each with ``chunk``, ``source``, and ``score`` keys,
            sorted by descending score.

        Raises:
            RuntimeError: If no documents have been ingested yet.

        Examples:
            >>> system = EnhancedRAGSystem()
            >>> system.ingest_documents()
            42
            >>> hits = system.retrieve("authentication middleware")
            >>> len(hits) <= 5
            True
        """
        if not self.chunks:
            raise RuntimeError("No chunks available — call ingest_documents() first.")

        query_tokens = set(query.lower().split())
        scored: List[Tuple[float, int]] = []
        for idx, chunk in enumerate(self.chunks):
            chunk_tokens = set(chunk.lower().split())
            overlap = len(query_tokens & chunk_tokens)
            if overlap:
                score = overlap / max(len(query_tokens), 1)
                scored.append((score, idx))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scored[:top_k]:
            results.append(
                {
                    "chunk": self.chunks[idx],
                    "source": self.metadata[idx]["source"],
                    "score": round(score, 4),
                }
            )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read_file(self, file_path: Path) -> str:
        """
        Dispatch to the correct reader based on file extension.

        Args:
            file_path: Path to the file to read.

        Returns:
            File content as a plain string.

        Raises:
            ValueError: If the file cannot be read.
        """
        if file_path.suffix.lower() == ".pdf":
            return extract_text_from_pdf(file_path)
        # Plain text, Markdown, Python source, RST
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            raise ValueError(f"Cannot read {file_path}: {exc}") from exc

    def _split_text(self, text: str) -> List[str]:
        """
        Split *text* into overlapping word-based chunks.

        Args:
            text: Raw text to split.

        Returns:
            List of text chunk strings.  Empty list if *text* is blank.
        """
        words = text.split()
        if not words:
            return []

        step = max(1, self.chunk_size - self.chunk_overlap)
        return [
            " ".join(words[i:i + self.chunk_size])
            for i in range(0, len(words), step)
        ]

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @staticmethod
    def pdf_backend() -> str:
        """
        Return the name of the PDF extraction backend in use.

        Returns:
            ``"PyMuPDF"`` if fitz is importable, otherwise ``"PyPDF2"``.

        Examples:
            >>> EnhancedRAGSystem.pdf_backend() in ("PyMuPDF", "PyPDF2")
            True
        """
        return "PyMuPDF" if HAS_PYMUPDF else "PyPDF2"

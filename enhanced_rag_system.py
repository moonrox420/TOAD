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

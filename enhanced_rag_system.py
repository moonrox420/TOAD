"""
Enhanced RAG System with PDF support.

Extends the base RAG system with the ability to ingest PDF documents
using PyMuPDF (fitz) when available, with automatic fallback to PyPDF2.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    fitz = None
    HAS_PYMUPDF = False
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


class EnhancedRAGSystem:
    """
    Enhanced RAG system with PDF document ingestion.

    Supports reading PDF files via PyMuPDF (preferred, faster) when the
    ``pymupdf`` package is installed, falling back automatically to PyPDF2
    otherwise.

    Example:
        >>> system = EnhancedRAGSystem()
        >>> text = system._read_pdf("document.pdf")
    """

    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the enhanced RAG system.

        Args:
            data_dir: Directory containing documents to ingest.
                      Defaults to ``data/raw``.
        """
        self.data_dir = Path(data_dir) if data_dir else Path("data/raw")
        os.makedirs(self.data_dir, exist_ok=True)

    def _read_pdf(self, path: str) -> str:
        """
        Read text content from a PDF file.

        Tries PyMuPDF first when available (faster and more accurate), then
        falls back to PyPDF2 if PyMuPDF is absent or raises an error during
        extraction.

        Args:
            path: Path to the PDF file.

        Returns:
            Extracted text content as a single string.

        Raises:
            ValueError: If ``path`` does not point to a readable PDF.
        """
        if HAS_PYMUPDF:
            try:
                doc = fitz.open(path)
                pages = [page.get_text() for page in doc]
                doc.close()
                text = "\n".join(pages)
                logger.debug("Read %s with PyMuPDF (%d pages)", path, len(pages))
                return text
            except Exception as exc:
                logger.warning(
                    "PyMuPDF failed to read %s (%s); falling back to PyPDF2",
                    path,
                    exc,
                )

        # PyPDF2 fallback
        try:
            reader = PdfReader(path)
            pages = [
                page.extract_text() or ""
                for page in reader.pages
            ]
            text = "\n".join(pages)
            logger.debug("Read %s with PyPDF2 (%d pages)", path, len(pages))
            return text
        except Exception as exc:
            raise ValueError(f"Could not read PDF '{path}': {exc}") from exc

    def load_documents(self, directory: Optional[str] = None) -> List[str]:
        """
        Load all supported documents from a directory.

        Currently supports ``.pdf``, ``.txt``, and ``.md`` files.

        Args:
            directory: Directory to scan. Defaults to ``self.data_dir``.

        Returns:
            List of extracted text strings, one per document.
        """
        scan_dir = Path(directory) if directory else self.data_dir
        texts: List[str] = []

        for file_path in sorted(scan_dir.rglob("*")):
            if not file_path.is_file():
                continue
            suffix = file_path.suffix.lower()
            try:
                if suffix == ".pdf":
                    texts.append(self._read_pdf(str(file_path)))
                elif suffix in {".txt", ".md"}:
                    texts.append(file_path.read_text(encoding="utf-8", errors="ignore"))
                else:
                    logger.debug("Skipping unsupported file: %s", file_path)
            except Exception as exc:
                logger.warning("Failed to load %s: %s", file_path, exc)

        logger.info("Loaded %d documents from %s", len(texts), scan_dir)
        return texts

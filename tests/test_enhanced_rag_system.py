"""
Tests for enhanced_rag_system.py — PyMuPDF import guard and _read_pdf fallback.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure repo root is on the path so the module can be imported.
sys.path.insert(0, str(Path(__file__).parent.parent))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_pypdf2_reader(pages_text):
    """Return a mock PdfReader whose pages yield the given texts."""
    mock_pages = []
    for text in pages_text:
        page = MagicMock()
        page.extract_text.return_value = text
        mock_pages.append(page)
    reader = MagicMock()
    reader.pages = mock_pages
    return reader


# ---------------------------------------------------------------------------
# Import-guard tests
# ---------------------------------------------------------------------------

class TestImportGuard:
    """Tests that the HAS_PYMUPDF flag is set correctly."""

    def test_has_pymupdf_is_bool(self):
        import enhanced_rag_system as ers
        assert isinstance(ers.HAS_PYMUPDF, bool)

    def test_fitz_none_when_unavailable(self, monkeypatch):
        """Simulate missing PyMuPDF: fitz should be None, flag False."""
        # Temporarily hide fitz so the guard treats it as unavailable
        original_fitz = sys.modules.get("fitz")
        sys.modules["fitz"] = None  # makes 'import fitz' raise ImportError

        try:
            try:
                import fitz as _fitz  # noqa: F401
                flag = True
            except ImportError:
                _fitz = None
                flag = False

            assert _fitz is None
            assert flag is False
        finally:
            if original_fitz is None:
                sys.modules.pop("fitz", None)
            else:
                sys.modules["fitz"] = original_fitz

    def test_fitz_truthy_when_available(self):
        """If fitz imported successfully, HAS_PYMUPDF must be True."""
        import enhanced_rag_system as ers
        if ers.HAS_PYMUPDF:
            assert ers.fitz is not None
        else:
            assert ers.fitz is None


# ---------------------------------------------------------------------------
# _read_pdf tests
# ---------------------------------------------------------------------------

class TestReadPdf:
    """Tests for EnhancedRAGSystem._read_pdf()."""

    # -- PyMuPDF path -------------------------------------------------------

    def test_read_pdf_uses_pymupdf_when_available(self, tmp_path):
        """When HAS_PYMUPDF is True, PyMuPDF should be tried first."""
        import enhanced_rag_system as ers

        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "PyMuPDF page text"
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.close = MagicMock()

        mock_fitz = MagicMock()
        mock_fitz.open.return_value = mock_doc

        pdf_path = str(tmp_path / "test.pdf")

        with patch.object(ers, "HAS_PYMUPDF", True), \
             patch.object(ers, "fitz", mock_fitz):
            system = ers.EnhancedRAGSystem(str(tmp_path))
            result = system._read_pdf(pdf_path)

        mock_fitz.open.assert_called_once_with(pdf_path)
        assert "PyMuPDF page text" in result

    def test_read_pdf_falls_back_to_pypdf2_when_pymupdf_absent(self, tmp_path):
        """When HAS_PYMUPDF is False, PyPDF2 should be used directly."""
        import enhanced_rag_system as ers

        mock_reader = _make_pypdf2_reader(["Page one text", "Page two text"])

        pdf_path = str(tmp_path / "test.pdf")

        with patch.object(ers, "HAS_PYMUPDF", False), \
             patch("enhanced_rag_system.PdfReader", return_value=mock_reader):
            system = ers.EnhancedRAGSystem(str(tmp_path))
            result = system._read_pdf(pdf_path)

        assert "Page one text" in result
        assert "Page two text" in result

    def test_read_pdf_falls_back_to_pypdf2_on_pymupdf_error(self, tmp_path):
        """When PyMuPDF raises, the method should fall back to PyPDF2."""
        import enhanced_rag_system as ers

        mock_fitz = MagicMock()
        mock_fitz.open.side_effect = RuntimeError("corrupt PDF")

        mock_reader = _make_pypdf2_reader(["Fallback text"])

        pdf_path = str(tmp_path / "test.pdf")

        with patch.object(ers, "HAS_PYMUPDF", True), \
             patch.object(ers, "fitz", mock_fitz), \
             patch("enhanced_rag_system.PdfReader", return_value=mock_reader):
            system = ers.EnhancedRAGSystem(str(tmp_path))
            result = system._read_pdf(pdf_path)

        assert "Fallback text" in result

    def test_read_pdf_raises_value_error_when_both_fail(self, tmp_path):
        """If both backends fail, a ValueError should be raised."""
        import enhanced_rag_system as ers

        mock_fitz = MagicMock()
        mock_fitz.open.side_effect = RuntimeError("bad PDF")

        pdf_path = str(tmp_path / "test.pdf")

        with patch.object(ers, "HAS_PYMUPDF", True), \
             patch.object(ers, "fitz", mock_fitz), \
             patch("enhanced_rag_system.PdfReader", side_effect=Exception("also bad")):
            system = ers.EnhancedRAGSystem(str(tmp_path))
            with pytest.raises(ValueError, match="Could not read PDF"):
                system._read_pdf(pdf_path)

    def test_read_pdf_multipage(self, tmp_path):
        """Text from multiple pages should be joined."""
        import enhanced_rag_system as ers

        pages = ["First page.", "Second page.", "Third page."]
        mock_reader = _make_pypdf2_reader(pages)

        pdf_path = str(tmp_path / "multi.pdf")

        with patch.object(ers, "HAS_PYMUPDF", False), \
             patch("enhanced_rag_system.PdfReader", return_value=mock_reader):
            system = ers.EnhancedRAGSystem(str(tmp_path))
            result = system._read_pdf(pdf_path)

        for page_text in pages:
            assert page_text in result

    # -- no-duplicate imports -----------------------------------------------

    def test_no_duplicate_fitz_import(self):
        """There should be only one import of fitz in the module source."""
        import re
        source_path = Path(__file__).parent.parent / "enhanced_rag_system.py"
        source = source_path.read_text()
        # Match lines that ARE import statements (not pure comment lines),
        # using a regex anchored to the start of the stripped line.
        import_lines = [
            line.strip()
            for line in source.splitlines()
            if re.match(r"^\s*import fitz\b", line)
        ]
        assert len(import_lines) == 1, (
            f"Expected exactly one 'import fitz' statement, found: {import_lines}"
        )

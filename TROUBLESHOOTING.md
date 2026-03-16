# Troubleshooting

## `ModuleNotFoundError: No module named 'exceptions'`

**Symptom**

Running `python enhanced_rag_system.py` (or any script that imports from it)
raises:

```
ModuleNotFoundError: No module named 'exceptions'
  File ".../.venv/Lib/site-packages/docx.py", line 30, in <module>
    from exceptions import PendingDeprecationWarning
```

**Root cause**

The legacy PyPI package named `docx` is Python-2-only.  Its top-level module
tries to import the `exceptions` built-in that no longer exists in Python 3.

The TOAD project uses `python-docx`, a separate, actively-maintained package
that provides the same `from docx import Document` API but is fully compatible
with Python 3.

**Fix**

1. Uninstall the wrong package (if present):

   ```bash
   pip uninstall docx
   ```

2. Install the correct package:

   ```bash
   pip install python-docx
   ```

   Or install all project requirements at once:

   ```bash
   pip install -r requirements.txt
   ```

3. Verify the installation:

   ```python
   from docx import Document
   print(Document)   # should print <class 'docx.document.Document'>
   ```

---

## PDF support (`PyMuPDF`)

PDF ingestion in `enhanced_rag_system.py` is **optional**.  When PyMuPDF is not
installed the system logs a warning and skips `.pdf` files without crashing.

To enable PDF support:

```bash
pip install pymupdf
```

---

## Still seeing issues?

- Make sure you are running Python 3.8 or later (`python --version`).
- If you use a virtual environment, activate it before installing packages.
- Check `pip list` to confirm that `docx` is **not** installed and
  `python-docx` **is** installed.

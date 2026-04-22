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
## Avoiding the HuggingFace model download when using a local GGUF file

### Problem

By default `enhanced_rag_system.py` loads
`mistralai/Mistral-7B-Instruct-v0.2` via HuggingFace Transformers.
The **first run downloads ~14.5 GB**.  If you have a quantized GGUF file
(e.g. from TheBloke or converted yourself) you can skip this entirely.

### Solution – set `LOCAL_GGUF_MODEL`

```bash
# Point to your local .gguf file
export LOCAL_GGUF_MODEL=/path/to/mistral-7b-instruct-v0.2.Q4_K_M.gguf

# Now run the script – the HF model is never downloaded
python enhanced_rag_system.py
```

When `LOCAL_GGUF_MODEL` is set:

* `llama-cpp-python` is used as the LLM backend.
* `transformers` / `torch` are **never imported** and no model is downloaded
  from HuggingFace.
* The rest of the RAG pipeline (FAISS retrieval, sentence-transformers
  embeddings) works exactly the same as usual.

When `LOCAL_GGUF_MODEL` is **not** set:

* The default HuggingFace Transformers backend is used (`Mistral-7B-Instruct-v0.2`).
* The model is cached after the first download; subsequent runs are fast.

### Installing llama-cpp-python

```bash
# CPU-only (works everywhere)
pip install llama-cpp-python

# GPU (CUDA) – significantly faster
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Metal (Apple Silicon)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

See the [llama-cpp-python docs](https://llama-cpp-python.readthedocs.io/) for
full build options.

### Where to get GGUF models

* **TheBloke on HuggingFace** – search for `GGUF` at
  <https://huggingface.co/TheBloke>
* Official Mistral GGUF: search `mistral-7b-instruct GGUF` on HuggingFace.
* Any other llama.cpp-compatible `.gguf` model file works.

---

## `torch_dtype` deprecation warning

If you see:

```
UserWarning: `torch_dtype` is deprecated! Use `dtype` instead!
```

this warning comes from `transformers` when `torch_dtype=…` is passed to
`AutoModelForCausalLM.from_pretrained`.

`enhanced_rag_system.py` already uses the current recommended `dtype=…`
parameter, so this warning should **not** appear from this file.  If you see
it from another script or an older version of the code, replace:

```python
# Old (deprecated)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)

# New (correct)
model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float16)
```

---

## RAG index not found

If you see:

```
WARNING  RAG index not found. Build it first with: ...
```

the FAISS vector index hasn't been built yet.  Run:

```bash
python -c "from rag import build_rag_index; build_rag_index()"
```

This downloads and indexes the configured HuggingFace datasets
(`Elite_GOD_Coder_100k`, etc.) – a one-time operation.  The index is cached
in `rag_data/index/` and reused on subsequent runs.

---

## Other common issues

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ImportError: llama_cpp not found` | llama-cpp-python not installed | `pip install llama-cpp-python` |
| `FileNotFoundError: GGUF model not found` | Wrong path in `LOCAL_GGUF_MODEL` | Check the path is correct and the file exists |
| `ImportError: transformers … required` | HF backend deps missing | `pip install transformers torch` |
| `faiss not installed` | faiss-cpu missing | `pip install faiss-cpu` |
| `sentence-transformers not installed` | Embedding model deps missing | `pip install sentence-transformers` |

For full dependency details see [`requirements.txt`](requirements.txt) and
[`INSTALLATION.md`](INSTALLATION.md).

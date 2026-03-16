# TROUBLESHOOTING

This document covers common issues and non-obvious configuration options for
running `enhanced_rag_system.py`.

---

## Local GGUF model support (`LOCAL_GGUF_MODEL`)

### Why would I use a GGUF model instead of Hugging Face?

* You have already downloaded a quantised model (e.g. from TheBloke on HF Hub)
  and want to run inference on CPU or a GPU with limited VRAM.
* You do not want to download gigabytes of weights every run.
* You prefer the llama.cpp runtime because of its memory efficiency.

### How it works

`enhanced_rag_system.py` checks the `LOCAL_GGUF_MODEL` environment variable at
startup.  When the variable is set to a valid path, it loads that file with
`llama-cpp-python` instead of downloading a model from Hugging Face.

> **Important**: `transformers` (the Hugging Face library) **cannot** load GGUF
> files directly.  GGUF is a format specific to llama.cpp.  You must use the
> `llama-cpp-python` package for this path.

### Step-by-step setup

1. **Install llama-cpp-python**

   CPU-only (default):
   ```bash
   pip install llama-cpp-python
   ```

   With CUDA GPU support:
   ```bash
   CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
   ```

   With Apple Metal (macOS):
   ```bash
   CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
   ```

2. **Download a GGUF model**

   Example using the Hugging Face CLI (or just copy the path if you already
   have the file in your cache):
   ```bash
   huggingface-cli download TheBloke/CodeLlama-7B-Instruct-GGUF \
       codellama-7b-instruct.Q4_K_M.gguf \
       --local-dir ~/.cache/huggingface/hub/TheBloke-CodeLlama-7B-Instruct-GGUF
   ```

   A typical cached path looks like:
   ```
   ~/.cache/huggingface/hub/models--TheBloke--CodeLlama-7B-Instruct-GGUF/blobs/<sha256-hash>
   ```

3. **Set the environment variable**

   ```bash
   export LOCAL_GGUF_MODEL="/full/path/to/codellama-7b-instruct.Q4_K_M.gguf"
   ```

   Or on Windows (PowerShell):
   ```powershell
   $env:LOCAL_GGUF_MODEL = "C:\Users\you\models\codellama-7b-instruct.Q4_K_M.gguf"
   ```

4. **Run the system**

   ```python
   from enhanced_rag_system import EnhancedRAGSystem

   system = EnhancedRAGSystem()
   print(system.backend_type)   # "gguf"
   code = system.generate("Write a Python REST API with FastAPI")
   print(code)
   ```

### Tuning performance

Two additional environment variables control the llama.cpp runtime:

| Variable            | Default | Description                                               |
|---------------------|---------|-----------------------------------------------------------|
| `GGUF_N_THREADS`    | `4`     | CPU threads for inference. Raise to match your CPU cores. |
| `GGUF_N_GPU_LAYERS` | `0`     | Layers offloaded to GPU (requires CUDA/Metal build).      |
| `GGUF_CONTEXT_SIZE` | `2048`  | Maximum context window length in tokens.                  |

Example – fully offload a 7 B model to a 6 GB GPU:
```bash
export GGUF_N_GPU_LAYERS=32
export GGUF_N_THREADS=8
```

---

## Transformers / Hugging Face backend (default)

When `LOCAL_GGUF_MODEL` is **not** set, the system defaults to the Transformers
backend.

```bash
export HF_MODEL_NAME="microsoft/phi-2"   # (optional, this is the default)
```

The model is downloaded from the Hugging Face Hub on first use and cached under
`~/.cache/huggingface`.

Required packages:
```bash
pip install transformers torch
```

---

## Common error messages

### `ImportError: llama-cpp-python is required …`

You set `LOCAL_GGUF_MODEL` but `llama-cpp-python` is not installed.
Run `pip install llama-cpp-python` (see step 1 above).

### `FileNotFoundError: GGUF model file not found`

The path in `LOCAL_GGUF_MODEL` does not point to an existing file.  Check the
path (including `~` expansion) and make sure the file is present.

### `ImportError: The 'transformers' package is required …`

You are running the default HF backend but `transformers` is not installed.
Run `pip install transformers torch`.

---

## RAG index not available

The RAG retrieval component requires a pre-built FAISS index.  If you see:

```
WARNING: RAG index not found. Run 'python cli.py rag build' first.
```

Follow the steps in `INSTALLATION.md` to build the index.  The system will
continue to work without RAG; the LLM will generate responses without
retrieval-augmented examples.

# Troubleshooting

## ⚠️ Do NOT install the `rag` PyPI package

### Problem

This project includes a **local `rag/` module** (the `rag/` directory bundled in this repository). It does **not** depend on the third-party PyPI package that happens to share the same name (`rag` on PyPI).

Installing the PyPI `rag` package causes the following issues:

- Pulls in **Celery 5.0.x** releases that have broken/malformed package metadata, causing `pip` to fail during dependency resolution.
- Requires **`pathtools`**, which uses Python's `imp` module that was removed in Python 3.12+.
- Fails to install under **current pip versions on Windows** due to the above metadata issues.
- Can shadow or conflict with the local `rag/` module used by this project.

### Solution

**Do not run:**
```bash
pip install rag   # ← WRONG — this is the broken PyPI package
```

**If you accidentally installed it, remove it immediately:**
```bash
pip uninstall rag
```

**The correct installation steps are:**
```bash
# 1. Clone the repository (the local rag/ module is included)
git clone https://github.com/moonrox420/TOAD.git
cd TOAD

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate          # Windows

# 3. Install only the listed requirements (do NOT add 'rag')
pip install -r requirements.txt
```

The local `rag/` package is imported directly from the repository directory — no PyPI install needed or wanted.

---

## Verifying your environment is clean

Run the following to confirm the PyPI `rag` package is not installed:

```bash
pip show rag
```

If this prints package information, uninstall it:

```bash
pip uninstall rag
```

A clean output (no package found) means your environment is ready.

---

## Other common issues

### `ModuleNotFoundError: No module named 'rag'`

If Python cannot find the local `rag` module, make sure you are running scripts from the **repository root directory** (the directory that contains the `rag/` folder):

```bash
cd /path/to/TOAD
python cli.py generate "my requirements"
```

### `ImportError` related to `celery`, `pathtools`, or `imp`

These errors almost always mean the PyPI `rag` package is installed. Uninstall it:

```bash
pip uninstall rag celery pathtools
pip install -r requirements.txt
```

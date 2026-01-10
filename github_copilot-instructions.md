# Copilot Coding Agent Onboarding Instructions for TOAD Repository

## Summary of the Repository
The `moonrox420/TOAD` repository is a Python-based project meant to "take over any directory" and provides advanced code generation functionalities. It is primarily focused on Retrieval-Augmented Generation (RAG), integrating retrieval systems and generation tools for rapid development of production-quality codebases.

### Repository Overview
- **Main Language**: Python (99%)
- **Frameworks and Tools**: 
  - FAISS for vector indexing
  - BM25 for traditional document retrieval
  - Hugging Face Transformers for natural language processing
- **Project Size**: Moderate with modular architecture.

---

## Build, Test, and Validation Instructions

### Environment Setup
- **Preconditions**: Always ensure Python 3.8 or higher.
- **Required Tools**:
  - Python runtime & pip package manager

#### Install Dependencies
Run:
```bash
pip install -r requirements.txt
```

Optional enhanced dependencies (for development):
```bash
pip install -e .[dev]
```

### Build Instructions
**Bootstrap Steps**:
1. Clone the repository:
   ```bash
   git clone https://github.com/moonrox420/TOAD.git
   cd TOAD
   ```
2. Install dependencies as above.

### Testing Instructions
To validate changes and test functionality:
1. Run the command below from the repo root:
   ```bash
   pytest
   ```
2. Specific tests:
   - `tests/test_config.py`: Validate configuration setup.
   - `tests/test_rag.py`: Validate the RAG module and FAISS indexing logic.

### Run Instructions
Run modules to test code generation and retrieval:
```bash
python cli.py generate "Create a FastAPI app with endpoints"
python web_ui.py
```

Optional interactive testing:
```bash
python
>>> from rag import RAGRetriever
>>> retriever = RAGRetriever()
>>> retriever.retrieve("SQLAlchemy database setup")
```

### Linting
Enforce linting to ensure style compliance:
```bash
black .
flake8 .
```

---

## Project Layout
### Major Architectural Elements
- **Core Files**:
  - `agent.py`: Main code generation logic (~1800 lines).
  - `setup.py`: Installation configuration, including optional dependencies.
- **RAG Module**:
  - `rag/config.py`: Manage retrieval configuration.
  - `rag/retriever.py`: Document retrieval and querying.
  - `rag/indexer.py`: Builds FAISS index.
  - `rag/embedder.py`: Creates embeddings using Hugging Face models.
- **Test Files**:
  - Located in `/tests/`.

### Repository Validation Pipelines
- Continuous Integration: None explicitly mentioned.
- Testing framework (`pytest`) ensures syntactic and logical correctness.

#### Validation Steps
1. Run all tests after each commit to check against regressions.
2. Use the example workflows provided in `QUICKSTART.md` to validate end-to-end functionality.

---

## Tips for the Coding Agent
1. **Trust Information**: Follow build instructions strictly; search only if errors are encountered.
2. **Validate Changes**: Always run `pytest` after code modifications—this validates both retrieval and generation capabilities.
3. **Where to Look**: 
   - Retrieval logic: `rag/retriever.py`
   - Embedding logic: `rag/embedder.py`
   - Build and installation setup: `setup.py`.
   - Documentation: README.md and QUICKSTART.md contain most guidance.

4. **Common Errors**:
   - Missing FAISS dependencies: Ensure installation via `requirements.txt`.
   - Python version mismatch: Confirm Python >=3.8 compatibility.

---

End of Instructions.
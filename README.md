# 🐸 TOAD: Take Over Any Directory

**TOAD** is a **production-ready, multi-language code generation engine** powered by intelligent requirement analysis and algorithmic pattern detection. Built for developers who need clean, optimized, working code—**fast**.

[![Python](https://img.shields.io/badge/Python-100%25-blue?style=flat-square)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square)](https://github.com/moonrox420/TOAD)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Supported Languages](#supported-languages)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
  - [CLI Mode](#cli-mode)
  - [Interactive TUI Mode](#interactive-tui-mode)
  - [Python API](#python-api)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**TOAD** takes the pain out of writing boilerplate code. Simply describe what you need, and TOAD generates production-ready implementations across multiple programming languages.

### What Makes TOAD Different?

- **🎯 Intent-Driven Generation**: Analyzes requirements to understand actual intent, not just keyword matching
- **⚡ Performance-First**: Detects and avoids anti-patterns during code generation
- **🔒 Security-Aware**: Built-in checks for common security vulnerabilities
- **🌍 Multi-Language**: Generates code in Python, C, JavaScript/TypeScript, and Rust
- **📦 Zero Configuration**: Works out-of-the-box with sensible defaults
- **🧠 Smart Algorithms**: Specialized generators for sorting, searching, filtering, validation, and more

---

## Key Features

### 🔧 Code Generation Capabilities

- **Algorithmic Operations**: Sort, search, filter, map, reduce, reverse, merge, split
- **Data Processing**: Count, sum, average, validation, parsing
- **Security Features**: Authentication-aware generation, encryption hints
- **Async Support**: Concurrent and parallel operation generation
- **Database Integration**: SQL and NoSQL code patterns
- **API Generation**: REST endpoint and HTTP handler scaffolding

### 📊 Analysis & Optimization

- **Performance Analysis**: Detects inefficient patterns before generation
- **Complexity Scoring**: Evaluates code complexity based on requirements
- **Security Auditing**: Flags unsafe operations (eval/exec, injection risks)
- **Anti-Pattern Detection**: Identifies common performance pitfalls
  - Python: String concatenation in loops, unused comprehensions, nested membership tests
  - JavaScript: Synchronous I/O, improper delete operator usage

### 🎨 User Interface Options

- **Interactive TUI**: Rich terminal interface with syntax highlighting
- **CLI Mode**: Direct command-line code generation
- **Python API**: Programmatic access for integration

### 🧩 RAG (Retrieval-Augmented Generation) System

- **Document Ingestion**: Supports .txt, .docx, .pdf formats
- **Vector Search**: FAISS-based similarity retrieval
- **Embeddings**: Sentence-transformers for semantic understanding
- **LLM Backends**: 
  - Local GGUF models (via llama-cpp-python) — **no HuggingFace download**
  - HuggingFace Transformers (Mistral-7B-Instruct-v0.2 default)

---

## Supported Languages

| Language | Level | Features |
|----------|-------|----------|
| **Python** | ⭐⭐⭐⭐⭐ | Full support, all operations |
| **C** | ⭐⭐⭐⭐ | Algorithms, data structures, system code |
| **JavaScript** | ⭐⭐⭐⭐ | Modern ES6+, async operations |
| **TypeScript** | ⭐⭐⭐⭐ | Type-safe generation with interfaces |
| **Rust** | ⭐⭐⭐⭐ | Memory-safe patterns, ownership rules |

---

## Quick Start

### Installation (5 minutes)

```bash
# Clone the repository
git clone https://github.com/moonrox420/TOAD.git
cd TOAD

# Create a virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt
```
```Powershell
# Clone the repository
git clone https://github.com/moonrox420/TOAD.git
cd TOAD

# Create a virtual environment (recommended)
python3 -m venv .venv
Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Generate Your First Function

```bash
# CLI Mode: Generate a sort function
python agent.py "sort a list of numbers efficiently" --lang=python

# Generate in C
python agent.py "binary search in a sorted array" --lang=c

# Generate in JavaScript
python agent.py "filter out null values from an array" --lang=javascript
```

### Interactive Mode

```bash
# Start the interactive TUI
python agent.py

# Then type your requirements:
# > sort a list in ascending order
# > search for an element in a sorted list
# > type 'quit' to exit
```

---

## Installation

### Prerequisites

- **Python 3.8+** (3.10+ recommended for best performance)
- **pip** or **conda** package manager
- 500 MB disk space (minimal; grows with optional LLM models)

### Standard Installation

```bash
# Install core dependencies
pip install -r requirements.txt
```

### Optional: Local GGUF Model Support

To use local GGUF models instead of downloading HuggingFace models (~14.5 GB):

```bash
# Install llama-cpp-python (CPU)
pip install llama-cpp-python

# Or with GPU support (CUDA)
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

Then set the environment variable:

```bash
export LOCAL_GGUF_MODEL=/path/to/mistral-7b-q4.gguf
python enhanced_rag_system.py
```

### Optional: PDF Support

```bash
# Enable PDF ingestion
pip install pymupdf
```

### Verify Installation

```bash
python -c "from agent import BadassCoder; print('✓ TOAD installed successfully')"
```

---

## Usage

### CLI Mode

**Generate code directly from the command line:**

```bash
# Basic usage
python agent.py "your requirement here" --lang=python

# With language specification
python agent.py "implement binary search" --lang=c

# Save to file
python agent.py "sort algorithm" --lang=rust --output=sort.rs
```

**Examples:**

```bash
# Python: Data processing
python agent.py "count occurrences of each element in a list" --lang=python

# C: Systems programming
python agent.py "reverse a string in place" --lang=c

# JavaScript: Web development
python agent.py "validate email address with regex" --lang=js

# Rust: Safe concurrent code
python agent.py "merge two sorted vectors efficiently" --lang=rust
```

### Interactive TUI Mode

**Start the interactive terminal interface:**

```bash
python agent.py
```

**Commands:**

```
> sort an array                          # Generate sort code
> lang rust                              # Switch language
> history                                # View last 5 generations
> filter a list by condition             # Generate filter code
> quit                                   # Exit
```

**Features:**

- Syntax-highlighted code display
- Performance and security warnings
- Generation history
- Real-time language switching

### Python API

**Programmatic integration:**

```python
from agent import BadassCoder

# Create agent instance
agent = BadassCoder()

# Generate code
result = agent.generate_code(
    "sort numbers in descending order",
    language="python"
)

# Access results
print(result.code)                    # Generated code
print(result.complexity_score)        # Complexity: 1-5
print(result.performance_issues)      # List of warnings
print(result.security_issues)         # List of security concerns
print(result.timestamp)               # Generation timestamp

# Check history
for item in agent.history:
    print(f"[{item.language}] {item.code[:50]}...")
```

**Advanced Usage - Requirement Analysis:**

```python
from agent import BadassCoder

agent = BadassCoder()

# Analyze requirement before generation
analysis = agent.analyze_requirement(
    "high-performance async database query with authentication"
)

print(analysis)
# Output:
# {
#     'language': 'python',
#     'complexity': 2.5,
#     'is_async': True,
#     'needs_security': True,
#     'needs_db': True
# }
```

---

## Architecture

### System Design

The TOAD system follows a modular, layered architecture designed for extensibility and performance:

**User Interface Layer** → **Core Analysis Engine** → **Generation Pipeline** → **Optimization Layer** → **Output**

Each component handles specific responsibilities while maintaining clean separation of concerns.

### Core Components

1. **BadassCoder**: Main orchestration engine
2. **AlgorithmicGenerator**: Specialized algorithm code generation
3. **PerformanceOptimizer**: Anti-pattern detection
4. **CodeResult**: Output data structure
5. **EnhancedRAGSystem**: RAG pipeline for context-aware generation

---

## Core Components

### BadassCoder (agent.py)

The main engine orchestrating code generation.

**Responsibilities:**
- Requirement analysis
- Multi-language coordination
- History tracking
- Result composition

### AlgorithmicGenerator (agent.py)

Specialized code generator for algorithmic operations.

**Supported Operations:**
- Sort, search, filter, map, reduce, reverse
- Sum, average, count, merge, split
- Validate, parse

### PerformanceOptimizer (agent.py)

Detects and flags performance anti-patterns.

### CodeResult (agent.py)

Data class encapsulating generation output with metadata.

### EnhancedRAGSystem (enhanced_rag_system.py)

Optional Retrieval-Augmented Generation system.

---

## Advanced Features

### 🎯 Smart Requirement Analysis

- Automatic language detection
- Complexity assessment
- Feature extraction

### 🔍 Performance Anti-Pattern Detection

- String concatenation loops
- Unused comprehensions
- Synchronous I/O operations

### 📚 RAG-Enhanced Generation

- Document ingestion support
- Vector-based similarity search
- Context-aware code generation

### 🚀 Local GGUF Model Support

- Skip 14.5GB HuggingFace download
- Fast local inference
- Full RAG pipeline compatibility

---

## Troubleshooting

### Common Issues

#### ModuleNotFoundError: No module named 'exceptions'

**Cause**: Legacy docx package installed

**Fix**:
```bash
pip uninstall docx
pip install python-docx
```

#### FileNotFoundError: GGUF model not found

**Cause**: LOCAL_GGUF_MODEL path incorrect

**Fix**:
```bash
export LOCAL_GGUF_MODEL=/correct/path/to/model.gguf
```

#### HuggingFace downloading 14.5 GB

**Cause**: LOCAL_GGUF_MODEL not set

**Fix**: Set LOCAL_GGUF_MODEL environment variable or install llama-cpp-python

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for comprehensive guides.

---

## Development

### Project Structure

```
TOAD/
├── agent.py                      # Main BadassCoder engine
├── badass_coder.py              # Extended coder with TUI
├── enhanced_rag_system.py        # RAG pipeline
├── requirements.txt              # Dependencies
├── TROUBLESHOOTING.md           # Troubleshooting guide
├── README.md                    # This file
├── tests/                       # Test suite
└── .github/                     # GitHub config
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
black agent.py badass_coder.py enhanced_rag_system.py
flake8 agent.py badass_coder.py enhanced_rag_system.py
```

---

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

### Code Style

- **Python**: PEP 8, Black formatter
- **Type hints**: Use for all function signatures
- **Docstrings**: Google-style
- **Comments**: Explain *why*, not *what*

---

## Performance Benchmarks

| Requirement | Language | Time | Notes |
|------------|----------|------|-------|
| "Sort an array" | Python | 45ms | Algorithmic path |
| "Binary search" | C | 52ms | Algorithmic path |
| "Filter objects" | JavaScript | 48ms | Algorithmic path |
| "Complex validation" | Rust | 156ms | Generic fallback |

---

## Dependencies

### Core (Required)
- aiosqlite
- python-docx
- faiss-cpu
- sentence-transformers
- datasets
- numpy
- pyyaml

### Optional
- llama-cpp-python
- transformers
- torch
- pymupdf
- pytest

Full details: [requirements.txt](requirements.txt)

---

## Roadmap

### v1.1 (Q3 2026)
- [ ] Go language support
- [ ] Kotlin language support
- [ ] Web UI
- [ ] GitHub Actions integration

### v1.2 (Q4 2026)
- [ ] Custom code style profiles
- [ ] Multi-file projects
- [ ] Dependency management
- [ ] Test generation

### v2.0 (2027)
- [ ] AST-based optimization
- [ ] Model fine-tuning
- [ ] IDE plugins

---

## License

**TOAD** is released under the **MIT License**. See [LICENSE](LICENSE) for full details.

---

## Citation

```bibtex
@software{toad2025,
  author = {moonrox420},
  title = {TOAD: Take Over Any Directory - Multi-Language Code Generation Engine},
  year = {2025},
  url = {https://github.com/moonrox420/TOAD}
}
```

---

## Support

- 📖 **Documentation**: [README.md](README.md) & [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/moonrox420/TOAD/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/moonrox420/TOAD/discussions)

---

## Acknowledgments

Built with ❤️ by the TOAD community. Special thanks to HuggingFace, FAISS, Sentence-Transformers, and llama.cpp.

---

<div align="center">

Made with 🐍 Python • MIT License • [GitHub](https://github.com/moonrox420/TOAD)

</div>

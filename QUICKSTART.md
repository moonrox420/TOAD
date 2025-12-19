# DroxAI Code Generation Agent - Quick Start Guide

## Three Ways to Use the Agent

### 1. Command-Line Interface (CLI) - Fastest for Terminal Users

```bash
# Generate code from natural language
python cli.py generate "Create a REST API with authentication and database"

# Analyze without generating code
python cli.py analyze "Build a web scraper"

# Interactive mode (like a coding REPL)
python cli.py interactive

# Run performance benchmarks
python cli.py benchmark

# Save generated code to a file
python cli.py generate "Create a FastAPI application" --output myapp.py

# Use the unlimited agent (generates larger, more comprehensive code)
python cli.py --unlimited generate "Your requirements here"
```

**CLI Benefits:**
- ✅ Fastest way to generate code
- ✅ Perfect for scripting and automation
- ✅ Integrates with shell scripts
- ✅ No UI overhead
- ✅ Built-in benchmark suite

---

### 2. Web User Interface (UI) - Best for Visual Users

```bash
# Start the web server
python web_ui.py

# Opens on http://localhost:8000
```

**Features:**
- Beautiful, modern interface
- Real-time code generation as you type
- Side-by-side requirement/code view
- Visual metrics and analytics
- One-click benchmarking
- Works on desktop, tablet, and mobile
- No installation required (runs locally)

**Usage:**
1. Type your requirements
2. Click "Generate Code" or "Analyze"
3. See results instantly
4. Copy code or download as file

---

### 3. Python API - Best for Developers

```python
from agent import CodeGenerationAgent, UnlimitedCodeAgent

# Basic usage
agent = CodeGenerationAgent()

# Analyze requirements
analysis = agent.analyze_requirements(
    "Create a REST API with JWT authentication"
)
print(f"Complexity Score: {analysis['complexity_score']}/100")

# Generate code
code = agent.generate_code(
    "Create a REST API with JWT authentication"
)

# Validate
validation = agent._validate_code(code)
print(f"Valid: {validation['valid']}")
print(f"Code Length: {len(code)} characters")

# Use unlimited agent for maximum features
unlimited = UnlimitedCodeAgent()
code = unlimited.generate_code(
    "Create enterprise system with...",
    refinement_passes=3  # Extra refinement passes
)
```

**API Benefits:**
- ✅ Full control over generation
- ✅ Programmatic access
- ✅ Integration with your own code
- ✅ Custom workflows
- ✅ Batch processing support

---

## 🎯 When to Use Which

| Scenario | Recommended | Why |
|----------|------------|-----|
| **Quick code generation** | CLI | Fastest, no UI overhead |
| **Exploring capabilities** | Web UI | Visual feedback, intuitive |
| **Integration/Automation** | Python API | Programmatic control |
| **Learning/Understanding** | All three | See results in different ways |
| **Production deployment** | Python API | Most control, best integration |
| **Testing performance** | CLI `benchmark` | Detailed metrics |

---

## 💡 Example Workflows

### Workflow 1: Generate API Fast (CLI)

```bash
# Generate a complete REST API with one command
python cli.py generate "FastAPI application with SQLAlchemy database, JWT auth, and CRUD endpoints" --output api.py

# Run it
python api.py
```

### Workflow 2: Explore & Understand (Web UI)

```bash
# Start the UI
python web_ui.py

# Browse to http://localhost:8000
# Try different requirements
# See metrics update in real-time
# Copy generated code
```

### Workflow 3: Integrate Into Project (Python)

```python
# In your project
from agent import UnlimitedCodeAgent

def scaffold_new_feature(feature_name: str) -> str:
    agent = UnlimitedCodeAgent()
    code = agent.generate_code(
        f"Create {feature_name} with full testing and documentation"
    )
    return code

# Use it
feature_code = scaffold_new_feature("user authentication system")
print(feature_code)
```

---

## 📊 Performance Benchmarks

Run benchmarks with any method:

```bash
# CLI
python cli.py benchmark

# Python
from agent import CodeGenerationAgent
agent = CodeGenerationAgent()

# Results show score for each complexity level
# Simple: 82.50/100
# Medium: 88.80/100
# Complex: 100/100
# Average: 92.83/100 ⭐
```

---

## 🔥 Pro Tips

1. **Be Specific**: More detailed requirements = better results
   ```bash
   # ✅ Good
   python cli.py generate "Create a FastAPI application with PostgreSQL, JWT auth, rate limiting, and Swagger docs"
   
   # ❌ Avoid
   python cli.py generate "Create an API"
   ```

2. **Use Unlimited for Complex Projects**:
   ```bash
   python cli.py --unlimited generate "Enterprise system with..."
   ```

3. **Save and Iterate**:
   ```bash
   # Generate and save
   python cli.py generate "requirement" --output code.py
   
   # Review in your editor
   # Give feedback for next generation
   ```

4. **Analyze First**:
   ```bash
   # See what the agent will generate before full generation
   python cli.py analyze "your requirement"
   ```

---

## 🚀 Getting Started

**Option A - Command Line (30 seconds)**:
```bash
python cli.py generate "Create a function that calculates fibonacci numbers"
```

**Option B - Web UI (1 minute)**:
```bash
python web_ui.py
# Then go to http://localhost:8000
```

**Option C - Python (2 minutes)**:
```bash
python
>>> from agent import CodeGenerationAgent
>>> agent = CodeGenerationAgent()
>>> print(agent.generate_code("Create a hello world function"))
```

---

## 📞 Need Help?

- **CLI help**: `python cli.py --help`
- **Command help**: `python cli.py generate --help`
- **Web UI**: Built-in documentation at http://localhost:8000
- **GitHub**: Check the main README.md for full documentation

---

**Start generating code in seconds! 🚀**

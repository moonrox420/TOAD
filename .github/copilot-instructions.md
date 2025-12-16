# DroxAI Code Generation Agent - AI Agent Instructions

This document guides AI coding agents on how to effectively contribute to the DroxAI Code Generation system.

## 🏗️ Architecture Overview

**Core System Design**: A multi-layer AI code generation pipeline that analyzes natural language requirements and produces production-ready Python code.

### Major Components

1. **CodeGenerationAgent** (`agent.py:25-2650`)
   - Core intelligence engine analyzing requirements into structured analysis
   - 15 core skills: code generation, optimization, analysis, refactoring, testing, security, performance, documentation
   - Uses AST parsing for syntax validation and regex-based feature detection
   - Produces honest complexity scores (0-100 scale, no artificial inflation)

2. **Requirement Analysis Pipeline** (`agent.py:46-339`)
   - `analyze_requirements()` → parses features, functions, classes, modules, patterns
   - `_calculate_complexity()` → realistic scoring: baseline 10 + volume + technical terms (capped 5/term) + patterns (capped 8/pattern) + architecture bonuses
   - `_identify_dependencies()` → detects stdlib and third-party imports
   - `_extract_performance/security()` → identifies special requirements
   - Returns Dict with parsed_elements, complexity_score, dependencies, performance_requirements, security_needs

3. **Code Generation Pipeline** (`agent.py:356-2650`)
   - `generate_code()` → 5-pass iterative refinement with multi-stage code assembly
   - **Pass 1**: Type hint injection (Dict, List, Optional, Union, Tuple, Callable)
   - **Pass 2**: Extensive test suite injection (12+ pytest cases per project)
   - **Pass 3**: Prometheus metrics for observability
   - **Pass 4**: Rate limiting + security middleware + Alembic stubs
   - **Pass 5**: Self-critique and missing enterprise elements
   - Output: Syntax-valid Python with real working implementations

4. **Component Assembly** (`agent.py:1449-1474`)
   - Intelligent code component ordering: imports → setup → core logic → tests → main → execution
   - Smart import generation with stdlib/third-party separation
   - Type hints injected into every function signature
   - Comprehensive error handling with custom exception hierarchies
   - Structured logging with file/console/error handlers

5. **Code Validation** (`agent.py:2049-2080`)
   - AST-based syntax validation (real detection, not hardcoded)
   - Regex-based feature detection: type hints, docstrings, error handling, logging
   - Returns validation dict with counts, booleans, and feature presence flags
   - Never returns fake validation results

6. **Optimization Pipeline** (`agent.py:2425-2550`)
   - `_remove_all_constraints()` → strips redundant checks, debug logging, defensive loops
   - `_apply_maximum_performance()` → CPU/memory/parallelization optimizations
   - `_add_maximum_functionality()` → retry decorators, async support, exception classes, test coverage

### Data Flow
```
Requirements String
    ↓
analyze_requirements() → Analysis Dict with parsed elements
    ↓
_detect_code_type() + _determine_architecture() → detect API/ML/DB/CLI/testing
    ↓
_generate_intelligent_components() → Dict[component_name → code_string]
    ↓
_smart_assemble_code() → strategic ordering of all components
    ↓
_refine_code_pass() × 5 → iterative enhancement (type hints → tests → metrics → security → enterprise)
    ↓
_validate_code() → AST + regex validation of generated code
    ↓
learn_from_execution() → store patterns for future optimization
    ↓
Return: Syntax-valid, fully-featured, production-ready Python code
```

## 🎯 Critical Developer Workflows

### Generating Code (Most Common Task)
```python
agent = CodeGenerationAgent()
code = agent.generate_code("Create REST API with authentication")
```

**Key Points**:
- Always use `ast.parse()` for syntax validation (not just string checking)
- Complexity calculation must use realistic weighting, NEVER use aggressive multipliers
- Feature detection via regex must be real (e.g., `\b(async|await)\b` for async, not hardcoded True)
- Generated code must be 100% executable—NO placeholders, NO "implement this", NO Mock objects in main logic
- All functions must have type hints and docstrings with Args/Returns/Raises/Examples sections

### Running Tests
```bash
pytest -v                           # Run all tests
pytest --cov --cov-report=html     # Coverage report
python test_optimizations.py       # Verify optimization pipeline
python validate_agent.py           # Full agent validation
python honest_benchmark.py         # Real metrics
```

### CLI Usage (Terminal Commands)
```bash
python cli.py generate "requirement text"        # Generate code
python cli.py analyze "requirement text"         # Analysis only
python cli.py interactive                        # REPL mode
python cli.py benchmark                          # Performance testing
python cli.py --unlimited generate "..."        # Extended agent
```

### Web Interface
```bash
python web_ui.py                   # Starts http://localhost:8000
```

### Building for Production
```bash
python setup.py install            # Installs droxai command globally
droxai generate "requirement"      # Now available anywhere
```

## 📋 Code Generation Patterns & Conventions

### Type Hints (ALWAYS Required)
Every function MUST have complete type hints:
```python
def process_data(data: Dict[str, Any], items: List[str]) -> Optional[Dict[str, Any]]:
    """Process data with comprehensive type safety."""
    return data
```

**Required imports**:
```python
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
```

### Docstrings (ALWAYS Multi-section)
Three-section format for every function:
```python
def validate_input(data: Dict[str, Any]) -> bool:
    """
    Validate input data with comprehensive checking.
    
    Args:
        data: Dictionary containing items to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValueError: If data is None or empty
        TypeError: If data is not a dict
        
    Examples:
        >>> result = validate_input({'id': 1, 'name': 'test'})
        >>> print(result)
        True
    """
    pass
```

### Error Handling Pattern
**NEVER** ignore exceptions or use bare `except:`. Always:
1. Catch specific exceptions (ValueError, TypeError, etc.)
2. Log with context: `logger.error(f"Error: {str(e)}", exc_info=True)`
3. Provide custom exceptions for business logic failures
```python
class ValidationError(Exception):
    """Custom validation failure exception"""
    pass

try:
    if not data:
        raise ValueError("Data required")
except ValueError as e:
    logger.error(f"Validation failed: {str(e)}", exc_info=True)
    raise ValidationError(f"Validation failed: {str(e)}") from e
```

### Logging Pattern
Must use Python's `logging` module with structured output:
```python
logger = logging.getLogger(__name__)

try:
    logger.info(f"Processing {len(items)} items")
    result = process(items)
    logger.info("Processing complete")
except Exception as e:
    logger.error(f"Processing error: {str(e)}", exc_info=True)
    raise
```

### Test Suite Pattern (12+ test cases minimum)
```python
class TestBasicFunctionality:
    def test_validate_input_with_valid_data(self, sample_data):
        result = validate_input(sample_data)
        assert result is True

class TestEdgeCases:
    def test_process_data_with_empty_dict(self):
        with pytest.raises(ValueError):
            validate_input({})

class TestIntegration:
    def test_full_workflow(self, sample_data, service_instance):
        result = service_instance.process(sample_data)
        assert result is not None
```

### API Route Pattern (FastAPI)
```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

@app.get("/api/v1/resource/{item_id}")
async def get_resource(item_id: int) -> Dict[str, Any]:
    """Get resource by ID with comprehensive error handling."""
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Fetching resource {item_id}")
        if item_id < 1:
            raise ValueError("Item ID must be positive")
        return {"id": item_id, "data": []}
    except ValueError as e:
        logger.error(f"Invalid ID: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
```

### Database Pattern (SQLAlchemy)
```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(50), unique=True)
    
    def validate(self) -> bool:
        """Validate user data before persistence"""
        if not self.username:
            raise ValueError("Username required")
        return True
```

### Performance Optimization Patterns
Three levels of optimization (applied in _apply_optimizations):

1. **CPU Optimization**: Convert list membership checks to set (O(1) vs O(n))
   ```python
   # Before: if item in [1, 2, 3, 4, 5]:
   # After:
   if item in {1, 2, 3, 4, 5}:  # O(1) lookup
   ```

2. **Memory Optimization**: Add caching for expensive operations
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def expensive_calculation(x: int) -> int:
       return x ** 2
   ```

3. **Parallelization**: Add multiprocessing for large datasets
   ```python
   from multiprocessing import Pool
   
   with Pool(processes=4) as pool:
       results = pool.map(process_item, large_dataset)
   ```

## 🛡️ Quality Assurance Requirements

### Complexity Scoring Rules (agent.py:75-145)
✅ **CORRECT**: Realistic 0-100 scale
- Baseline: 10 points for any requirement
- Volume: +0.3 per line (capped at 15)
- Technical terms: realistic weights (auth=4, async=4, ml=7) capped 5/term
- Patterns: conditional/loop/error/class weights capped 8/pattern
- Architecture bonuses: 6-10 for microservices/distributed/ML

❌ **WRONG**: Inflated scoring
- No aggressive multipliers (1.2x, 1.6x)
- No artificial floors (50+ minimum)
- No hardcoded high scores

### Code Validation Rules (agent.py:2049-2080)
✅ **CORRECT**: Real feature detection
- Syntax: Use `ast.parse()` to verify valid Python
- Type hints: Regex for `: Type` and `-> Type` patterns
- Docstrings: Regex for `"""..."""` blocks
- Error handling: Count try/except/raise/finally
- Logging: Check for logging imports and calls

❌ **WRONG**: Fake validation
- Never return hardcoded True/False
- Never use dummy detection
- Never claim features that aren't present

### Code Completeness Rules
✅ **REQUIRED**:
- Every function has type hints and docstrings
- Every class has __init__, __repr__, and methods with docstrings
- 12+ test cases covering happy path, edge cases, errors
- Custom exception classes (ValidationError, ProcessingError, etc.)
- Structured logging with debug/info/error levels
- Error handling in every try block with context preservation

❌ **FORBIDDEN**:
- Placeholder functions (just return input unchanged)
- Stub methods (pass statements or # TODO)
- Mock objects in main code (only in tests)
- Hardcoded values (use variables/config)
- Print statements (use logging instead)
- Bare except clauses

## 🔍 Important Files & Their Roles

| File | Purpose | Key Functions |
|------|---------|---------------|
| `agent.py` | Core intelligence engine | `CodeGenerationAgent`, `generate_code()`, `analyze_requirements()` |
| `cli.py` | Terminal interface | Command parsing, code generation triggering |
| `web_ui.py` | Web interface | Flask/FastAPI server with real-time generation |
| `tui.py` | Terminal UI | Rich text UI for terminal users |
| `setup.py` | Package metadata | pip install configuration, entry points |
| `validate_agent.py` | Full validation suite | Tests syntax, features, scoring accuracy |
| `honest_benchmark.py` | Real performance metrics | Transparent testing without inflation |
| `test_optimizations.py` | Optimization verification | Before/after optimization testing |

## ⚙️ Common Development Tasks

### Adding a New Code Type (e.g., GraphQL APIs)
1. Add detection in `_detect_code_type()` (search for GraphQL keywords)
2. Add case in `_generate_intelligent_components()` to call new generator
3. Create `_generate_graphql_schema()` and `_generate_graphql_resolvers()` methods
4. Add to component assembly ordering in `_smart_assemble_code()`
5. Create comprehensive tests in `test_agent.py`

**Example**:
```python
def _detect_code_type(self, requirements, analysis):
    if re.search(r'\b(graphql|gql)\b', requirements, re.IGNORECASE):
        return 'graphql'
    # ... other types
```

### Adding a New Optimization
1. Create method `_optimize_<name>(code: str) -> str` in `OptimizedCodeAgent`
2. Call from `_apply_optimizations()` with try/catch
3. Add test case in `test_optimizations.py` showing before/after improvement
4. Document improvement metric (e.g., "50% size reduction")

### Implementing a New Skill
1. Add to `_setup_capabilities()` (e.g., `self.skills.add('new_skill')`)
2. Create implementation methods
3. Wire into `generate_code()` pipeline if appropriate
4. Add test cases covering the new skill

### Debugging Generated Code
1. Enable logging: `logger.setLevel(logging.DEBUG)`
2. Check `agent.execution_log` for task history
3. Use `_validate_code()` to identify syntax/feature issues
4. Compare with `honest_benchmark.py` output to verify correctness
5. Never modify validation results—fix the generation logic instead

## 🚨 Critical Rules for AI Assistants

**BEFORE EDITING CODE:**
1. ✅ Scan the file to understand existing logic
2. ✅ Read test cases to understand expected behavior
3. ✅ Check validation logic to ensure it's honest (not hardcoded)
4. ✅ Preserve all working functionality

**WHILE EDITING CODE:**
1. ❌ DO NOT remove working logic—only upgrade or replace
2. ❌ DO NOT leave placeholders or Mock objects in main code
3. ❌ DO NOT modify test results or validation to make things pass
4. ❌ DO NOT hardcode values that should be dynamic
5. ✅ DO complete all implementations end-to-end
6. ✅ DO verify syntax with `ast.parse()` before committing
7. ✅ DO run tests to validate changes
8. ✅ DO add test cases for new functionality

**ABOUT CODE OWNERSHIP:**
- All generated code is the user's property (specify in comments)
- Remove all external service calls except essential libraries
- No telemetry, tracking, or external communication
- Users can take generated code anywhere without licensing concerns

**ABOUT NATURAL LANGUAGE INTERFACE:**
- Agent must understand plain English requirements
- Convert natural language to structured analysis
- Never require specific syntax or formatting from users
- Handle variations in requirement phrasing gracefully

## 📝 Code Style & Naming Conventions

- **Classes**: PascalCase (`CodeGenerationAgent`, `TestBasicFunctionality`)
- **Functions**: snake_case (`generate_code`, `analyze_requirements`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_COMPLEXITY`, `DEFAULT_PORT`)
- **Private methods**: _snake_case (`_calculate_complexity`, `_validate_code`)
- **Type hints**: Use full typing module types
- **Comments**: Explain WHY, not WHAT (code shows WHAT)
- **Line length**: 100 characters max (allows 80+ for readability)
- **Imports**: Group stdlib, third-party, local; sort alphabetically

## 🔄 Git Workflow

- Commit message format: `[component] Description of change`
- Examples: `[agent] Implement ML code generation`, `[validation] Fix feature detection`
- No merge commits; use rebase when possible
- Tag releases with semantic versioning (v1.0.0)

## 🎓 Learning Resources from Codebase

- **Type hints best practices**: See `_generate_smart_imports()` and every function signature
- **Error handling**: Study `safe_execute()` and `_generate_advanced_error_handling()`
- **Testing patterns**: Review `_generate_extensive_tests()` for 12+ test cases
- **API design**: Check `_generate_api_routes()` for REST best practices
- **Logging strategy**: See `setup_logging()` with file/console/error handlers
- **Validation logic**: Study `_validate_code()` for honest feature detection

---

**Last Updated**: December 2025  
**Target Version**: 2.0+ (Production-Ready)  
**License**: Code is user's property—no external dependencies or tracking

#!/usr/bin/env python3
"""Real test of CodeGenerationAgent benchmark score"""

from agent import CodeGenerationAgent

# Create agent
agent = CodeGenerationAgent()

# Real test case
requirements = '''Build a complete REST API with:
- FastAPI framework
- Database integration (SQLAlchemy)
- Authentication (JWT)
- Error handling
- Logging
- Type hints
- Docstrings
- Unit tests
- Security best practices
'''

print('='*80)
print('REAL AGENT TEST - CodeGenerationAgent')
print('='*80)
print(f'Requirements: {len(requirements)} chars')
print()

# Analyze
print('Step 1: Analyzing requirements...')
analysis = agent.analyze_requirements(requirements)
print(f'  Complexity Score: {analysis["complexity_score"]}')
print(f'  Analysis Keys: {list(analysis.keys())}')
print()

# Generate
print('Step 2: Generating code...')
code = agent.generate_code(requirements)
print(f'  Generated Code: {len(code)} characters')
print(f'  Lines: {len(code.splitlines())}')
print()

# Validate
print('Step 3: Validating code...')
validation = agent._validate_code(code)
print(f'  Valid: {validation["valid"]}')
print(f'  Validation Keys: {list(validation.keys())}')
print()

print('='*80)
print(f'✅ Real Test Complete - Validation: {validation["valid"]}')
print('='*80)

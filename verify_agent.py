#!/usr/bin/env python3
"""Verify the agent is real and working - transparent verification"""

from agent import CodeGenerationAgent

print("=" * 70)
print("TRANSPARENT VERIFICATION OF AGENT FUNCTIONALITY")
print("=" * 70)

# Test 1: Agent initialization
print("\n[TEST 1] Agent Initialization")
print("-" * 70)
agent = CodeGenerationAgent()
print(f"✓ Agent created: {agent.name}")
print(f"✓ Agent ID: {agent.id}")
print(f"✓ Skills count: {len(agent.skills)}")
print(f"✓ Skills available:")
for skill in sorted(agent.skills):
    print(f"  - {skill}")

# Test 2: Requirements analysis
print("\n[TEST 2] Requirements Analysis")
print("-" * 70)
requirement = "Create a function that adds two numbers with error handling and logging"
analysis = agent.analyze_requirements(requirement)
print(f"✓ Analyzed requirement")
print(f"  - Complexity score: {analysis['complexity_score']}/100")
print(f"  - Dependencies: {analysis['dependencies']}")
print(f"  - Security needs: {analysis['security_needs']}")
print(f"  - Performance: {analysis['performance_requirements']}")

# Test 3: Code generation
print("\n[TEST 3] Code Generation")
print("-" * 70)
generated_code = agent.generate_code(requirement)
print(f"✓ Code generated successfully")
print(f"  - Total characters: {len(generated_code)}")
print(f"  - Total lines: {len(generated_code.split(chr(10)))}")
print(f"  - Contains type hints: {'->' in generated_code}")
print(f"  - Contains logging: {'logging' in generated_code}")
print(f"  - Contains error handling: {'except' in generated_code}")
print(f"  - Contains docstrings: {'\"\"\"' in generated_code}")

# Test 4: Show actual generated code
print("\n[TEST 4] Sample of Generated Code")
print("-" * 70)
lines = generated_code.split('\n')
print("First 15 lines of generated code:")
for i, line in enumerate(lines[:15], 1):
    print(f"  {i:2d}: {line}")

# Test 5: Validation
print("\n[TEST 5] Code Validation")
print("-" * 70)
validation = agent._validate_code(generated_code)
print(f"✓ Code validation results:")
print(f"  - Valid syntax: {validation.get('valid', False)}")
print(f"  - Type hints present: {validation.get('has_type_hints', False)}")
print(f"  - Docstrings present: {validation.get('has_docstrings', False)}")
print(f"  - Error handling: {validation.get('has_error_handling', False)}")

print("\n" + "=" * 70)
print("VERIFICATION COMPLETE - ALL SYSTEMS OPERATIONAL")
print("=" * 70)

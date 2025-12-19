#!/usr/bin/env python3
"""Fast benchmark of optimized agentic system."""

from agent import CodeGenerationAgent
from multi_language_agent import MultiLanguageAgent

requirement = "Function that adds two numbers"

print("Testing optimized multi-language generation...\n")

# Test Python
print("[PYTHON]")
agent = MultiLanguageAgent()
agent.set_language('python')
result = agent.generate(requirement)
py_issues = len(result['remaining_issues'])
print(f"  Remaining issues: {py_issues}")
print(f"  Valid: {result['validation']['valid']}")

# Test JavaScript
print("\n[JAVASCRIPT]")
agent.set_language('javascript')
result = agent.generate(requirement)
js_issues = len(result['remaining_issues'])
print(f"  Remaining issues: {js_issues}")
print(f"  Valid: {result['validation']['valid']}")

# Test Java
print("\n[JAVA]")
agent.set_language('java')
result = agent.generate(requirement)
java_issues = len(result['remaining_issues'])
print(f"  Remaining issues: {java_issues}")
print(f"  Valid: {result['validation']['valid']}")

# Summary
print("\n" + "="*50)
print("RESULTS:")
print("="*50)
total_issues = py_issues + js_issues + java_issues
print(f"Python:     {py_issues} issues")
print(f"JavaScript: {js_issues} issues")
print(f"Java:       {java_issues} issues")
print(f"Total:      {total_issues} issues across 3 languages")
print(f"\nStatus: {'CLEAN GENERATION' if total_issues == 0 else 'Needs optimization'}")

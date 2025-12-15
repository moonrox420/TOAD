from agent import CodeGenerationAgent
import re

# Test with the complex requirement that might have given 92
req = '''Create a high-performance data processing system with:
    - Multi-threaded processing for scalability
    - Real-time data streaming capabilities
    - Advanced error handling and logging
    - Database integration with connection pooling
    - REST API endpoints with authentication
    - Security features including encryption
    - Performance monitoring and metrics
    - Automated testing framework
    - Comprehensive documentation'''

agent = CodeGenerationAgent()
analysis = agent.analyze_requirements(req)

print(f"Complex requirement complexity score: {analysis['complexity_score']}/100")

# Now test with simple requirement
simple_req = "Create a function that adds two numbers"
simple_analysis = agent.analyze_requirements(simple_req)
print(f"Simple requirement complexity score: {simple_analysis['complexity_score']}/100")

# The 92.83 must have been the OVERALL agent quality score, not complexity
# Let's see what the actual performance score would be
code = agent.generate_code(req)
validation = agent._validate_code(code)

print(f"\nCode generation metrics:")
print(f"  Code length: {len(code)}")
print(f"  Valid: {validation['valid']}")
print(f"  Issues: {len(validation.get('issues', []))}")

# Calculate what 92.83 would mean
print(f"\n92.83 must have been composed of:")
print(f"  Complexity: {analysis['complexity_score']}/100")
print(f"  Other factors (quality, capabilities, etc): {92.83 - analysis['complexity_score']:.2f}")

import time
from agent import CodeGenerationAgent, UnlimitedCodeAgent

def test_agent_score(agent_class, name, requirements):
    '''Test an agent and return its score'''
    print(f'\n--- {name} ---')
    agent = agent_class()
    
    # Analyze requirements
    analysis = agent.analyze_requirements(requirements)
    complexity = analysis['complexity_score']
    print(f'Complexity Score: {complexity}/100')
    
    # Generate code
    try:
        code = agent.generate_code(requirements)
        code_length = len(code)
        print(f'Generated Code Length: {code_length} chars')
    except Exception as e:
        print(f'Code Generation Error: {e}')
        code = ''
        code_length = 0
    
    # Validate
    if code:
        validation = agent._validate_code(code)
        is_valid = validation.get('valid', False)
        issues = len(validation.get('issues', []))
        print(f'Code Valid: {is_valid}')
        print(f'Issues Found: {issues}')
        
        # Calculate overall score
        score = (complexity * 0.4) + (min(100, (code_length / 100)) * 0.3) + (100 if is_valid else 50) * 0.3
        print(f'Overall Score: {score:.2f}/100')
        return score
    return 0

# Test with a real requirement
requirement = '''Create a Python web API using FastAPI that:
- Has user authentication with JWT tokens
- Supports CRUD operations for products
- Includes database integration with SQLAlchemy
- Has input validation with Pydantic
- Includes error handling
- Has API documentation with Swagger
- Includes unit tests
- Has logging setup'''

print('=== AGENT PERFORMANCE TEST ===')
reg_score = test_agent_score(CodeGenerationAgent, 'CodeGenerationAgent', requirement)
unlim_score = test_agent_score(UnlimitedCodeAgent, 'UnlimitedCodeAgent', requirement)

print(f'\n=== SUMMARY ===')
print(f'CodeGenerationAgent Score: {reg_score:.2f}/100')
print(f'UnlimitedCodeAgent Score: {unlim_score:.2f}/100')
if unlim_score > 0 and reg_score > 0:
    improvement = ((unlim_score - reg_score) / reg_score) * 100
    print(f'Improvement: {improvement:+.2f}%')

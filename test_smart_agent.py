import time
from agent import CodeGenerationAgent, UnlimitedCodeAgent

def test_agent_intelligence(agent_class, name, requirements):
    '''Test agent intelligence comprehensively'''
    print(f'\n{"="*60}')
    print(f'{name.upper()}')
    print(f'{"="*60}')
    
    agent = agent_class()
    
    # Analyze requirements
    print(f'\n[1] REQUIREMENT ANALYSIS')
    analysis = agent.analyze_requirements(requirements)
    complexity = analysis['complexity_score']
    print(f'  Complexity Score: {complexity}/100')
    print(f'  Detected Context: {analysis["execution_context"]}')
    print(f'  Priority Level: {analysis["priority_level"]}')
    print(f'  Dependencies Found: {len(analysis["dependencies"])}')
    print(f'  Security Requirements: {sum(1 for v in analysis["security_needs"].values() if v)}')
    print(f'  Performance Focus: {analysis["performance_requirements"]["real_time"]}')
    
    # Generate code
    print(f'\n[2] CODE GENERATION')
    start = time.time()
    code = agent.generate_code(requirements)
    gen_time = time.time() - start
    print(f'  Generation Time: {gen_time:.4f}s')
    print(f'  Generated Code Length: {len(code)} chars')
    print(f'  Lines of Code: {len(code.split(chr(10)))}')
    
    # Validate code
    print(f'\n[3] CODE VALIDATION')
    validation = agent._validate_code(code)
    print(f'  Valid: {validation["valid"]}')
    print(f'  Errors: {len(validation["errors"])}')
    print(f'  Warnings: {len(validation["warnings"])}')
    
    # Calculate score
    print(f'\n[4] SCORING')
    score = (complexity * 0.4) + (min(100, (len(code) / 100)) * 0.3) + (100 if validation['valid'] else 50) * 0.3
    print(f'  Overall Score: {score:.2f}/100')
    
    # Learning & adaptation
    print(f'\n[5] LEARNING & INTELLIGENCE')
    if hasattr(agent, 'get_intelligence_score'):
        intel_score = agent.get_intelligence_score()
        print(f'  Intelligence Score: {intel_score:.2f}/100')
        print(f'  Success Rate: {agent.success_rate*100:.1f}%')
        print(f'  Learned Patterns: {len(agent.code_patterns)}')
        print(f'  Generation Count: {agent.generation_count}')
        print(f'  Avg Complexity Seen: {agent.average_complexity:.1f}')
    
    return score

# Test scenarios of increasing complexity
test_cases = [
    ('Simple Function', 'Create a function that adds two numbers'),
    
    ('Basic Web API', '''Create a FastAPI web API that:
    - Has user authentication with JWT tokens
    - Supports CRUD operations for products
    - Includes database integration with SQLAlchemy
    - Has input validation with Pydantic
    - Includes error handling'''),
    
    ('Advanced System', '''Build a high-performance data processing system with:
    - Real-time data streaming capabilities
    - Multi-threaded processing for scalability
    - Advanced error handling and comprehensive logging
    - Database integration with connection pooling
    - REST API endpoints with JWT authentication
    - Security features including encryption
    - Performance monitoring and metrics
    - Automated testing framework
    - Comprehensive documentation
    - Event-driven architecture
    - Microservices support'''),
    
    ('Enterprise Solution', '''Create an enterprise-grade data platform with:
    - Distributed microservices architecture
    - Event sourcing and CQRS patterns
    - Machine learning model serving with real-time inference
    - Multi-tenant support with data isolation
    - GraphQL and REST API endpoints
    - Advanced caching strategies (Redis)
    - Message queue processing (Celery)
    - PostgreSQL and MongoDB integration
    - Kubernetes deployment ready
    - OAuth2 and JWT authentication
    - Rate limiting and circuit breakers
    - Comprehensive monitoring with Prometheus
    - ELK stack logging
    - Automated testing with pytest coverage
    - CI/CD pipeline integration''')
]

print('\n' + '='*80)
print('SCARY SMART AI CODE GENERATION AGENT - COMPREHENSIVE TEST')
print('='*80)

results = {}
for case_name, requirement in test_cases:
    print(f'\n\n{"#"*80}')
    print(f'# TEST CASE: {case_name}')
    print(f'{"#"*80}')
    
    # Test regular agent
    reg_score = test_agent_intelligence(CodeGenerationAgent, 'CodeGenerationAgent', requirement)
    
    # Test unlimited agent
    unlim_score = test_agent_intelligence(UnlimitedCodeAgent, 'UnlimitedCodeAgent', requirement)
    
    results[case_name] = {
        'regular': reg_score,
        'unlimited': unlim_score,
        'improvement': unlim_score - reg_score
    }

print(f'\n\n{"="*80}')
print('FINAL SUMMARY')
print(f'{"="*80}')

print(f'\n{"Case Name":<30} {"Regular":<15} {"Unlimited":<15} {"Improvement":<15}')
print('-' * 75)

total_reg = 0
total_unlim = 0
for case_name, scores in results.items():
    reg = scores['regular']
    unlim = scores['unlimited']
    imp = scores['improvement']
    total_reg += reg
    total_unlim += unlim
    imp_str = f"{imp:+.2f}"
    print(f'{case_name:<30} {reg:<15.2f} {unlim:<15.2f} {imp_str:<15}')

print('-' * 75)
avg_reg = total_reg / len(results)
avg_unlim = total_unlim / len(results)
avg_imp = avg_unlim - avg_reg
avg_imp_str = f"{avg_imp:+.2f}"
print(f'{"AVERAGE":<30} {avg_reg:<15.2f} {avg_unlim:<15.2f} {avg_imp_str:<15}')

print(f'\n{"="*80}')
print(f'Agent is now SCARY SMART! Average Score: {avg_unlim:.2f}/100')
print(f'{"="*80}\n')

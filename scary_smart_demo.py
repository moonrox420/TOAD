from agent import UnlimitedCodeAgent

print('\n' + '='*80)
print('SCARY SMART AI - LIVE DEMONSTRATION')
print('='*80)

agent = UnlimitedCodeAgent('ScarySmartAgent')

# Real-world example
req = '''Build a microservices-based real-time data platform with:
- Event-driven architecture using event sourcing
- Kubernetes orchestration
- Machine learning model inference
- GraphQL and REST APIs
- Real-time WebSocket streaming
- Multi-database support (PostgreSQL, MongoDB)
- JWT authentication and authorization
- Performance monitoring and logging
- Distributed caching with Redis'''

print('\nREQUIREMENT:')
print(req)

print('\n[ANALYSIS PHASE]')
analysis = agent.analyze_requirements(req)
complexity = analysis['complexity_score']
context = analysis['execution_context']
security_count = sum(1 for v in analysis['security_needs'].values() if v)
dep_count = len(analysis['dependencies'])
realtime = analysis['performance_requirements']['real_time']
arch = agent._determine_architecture(req, analysis)

print(f'Complexity Score: {complexity}/100')
print(f'Detected Context: {context}')
print(f'Architecture: {arch}')
print(f'Security Requirements Found: {security_count}')
print(f'Dependencies Identified: {dep_count}')
print(f'Performance Requirements: Real-time = {realtime}')

print('\n[CODE GENERATION PHASE]')
code = agent.generate_code(req)
code_len = len(code)
line_count = len(code.split('\n'))
print(f'Generated {code_len} characters of code')
print(f'{line_count} lines of code')

print('\n[VALIDATION PHASE]')
validation = agent._validate_code(code)
is_valid = validation['valid']
error_count = len(validation['errors'])
warning_count = len(validation['warnings'])
print(f'Code Valid: {is_valid}')
print(f'Validation Errors: {error_count}')
print(f'Code Quality Warnings: {warning_count}')

print('\n[INTELLIGENCE METRICS]')
intel_score = agent.get_intelligence_score()
success = agent.success_rate * 100
gen_count = agent.generation_count
pattern_count = len(agent.code_patterns)
print(f'Intelligence Score: {intel_score:.2f}/100')
print(f'Success Rate: {success:.1f}%')
print(f'Generations Completed: {gen_count}')
print(f'Patterns Learned: {pattern_count}')

strategy = agent.adapt_strategy(req)
strat_name = strategy['strategy']
strat_conf = strategy['confidence'] * 100
print(f'Recommended Strategy: {strat_name}')
print(f'Strategy Confidence: {strat_conf:.1f}%')

print('\n[GENERATED CODE SNIPPET]')
lines = code.split('\n')
for i, line in enumerate(lines[:15]):
    print(line)
if len(lines) > 15:
    print('...')

print('\n' + '='*80)
print('AGENT IS OPERATING AT MAXIMUM INTELLIGENCE LEVEL')
print('='*80 + '\n')

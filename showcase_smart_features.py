from agent import CodeGenerationAgent, UnlimitedCodeAgent

print('\n' + '='*80)
print('AGENT INTELLIGENCE CAPABILITIES SHOWCASE')
print('='*80)

agent = UnlimitedCodeAgent()

# Test 1: Complexity Detection Improvement
print('\n[TEST 1] IMPROVED COMPLEXITY DETECTION')
print('-' * 80)

test_reqs = [
    ('Simple', 'Create a function that adds two numbers'),
    ('ML Model', 'Build a neural network for image classification using PyTorch'),
    ('Distributed System', 'Build a microservices architecture with Kubernetes and event sourcing'),
    ('Enterprise Platform', 'Create a distributed real-time platform with blockchain integration, machine learning inference, and CQRS pattern'),
]

for name, req in test_reqs:
    analysis = agent.analyze_requirements(req)
    print(f'{name:<20} - Complexity: {analysis["complexity_score"]:>3}/100 | Context: {analysis["execution_context"]:>15} | Security: {sum(1 for v in analysis["security_needs"].values() if v)}')

# Test 2: Learning Capabilities
print('\n\n[TEST 2] LEARNING & ADAPTATION DEMONSTRATION')
print('-' * 80)

learning_req = 'Create a FastAPI web service with authentication'
print(f'Initial state before learning:')
print(f'  - Generation Count: {agent.generation_count}')
print(f'  - Learned Patterns: {len(agent.code_patterns)}')
print(f'  - Success Rate: {agent.success_rate*100:.1f}%')
print(f'  - Intelligence Score: {agent.get_intelligence_score():.2f}/100')

# Generate code multiple times (simulating learning)
print(f'\nGenerating code 5 times on similar requirements...')
for i in range(5):
    req_variant = f'{learning_req} with {"caching" if i%2 else "database"}'
    code = agent.generate_code(req_variant)

print(f'\nState after learning:')
print(f'  - Generation Count: {agent.generation_count}')
print(f'  - Learned Patterns: {len(agent.code_patterns)}')
print(f'  - Success Rate: {agent.success_rate*100:.1f}%')
print(f'  - Intelligence Score: {agent.get_intelligence_score():.2f}/100')
print(f'  - Average Complexity Learned: {agent.average_complexity:.2f}')

# Test 3: Adaptive Strategy
print('\n\n[TEST 3] ADAPTIVE STRATEGY SELECTION')
print('-' * 80)

strategy = agent.adapt_strategy(learning_req)
print(f'Requirements: {learning_req}')
print(f'Recommended Strategy: {strategy["strategy"]}')
print(f'Confidence: {strategy["confidence"]:.2%}')
print(f'Suggested Code Length: {strategy["suggested_code_length"]:.0f} chars')

# Test 4: Code Type Detection
print('\n\n[TEST 4] INTELLIGENT CODE TYPE DETECTION')
print('-' * 80)

code_types = [
    ('API Service', 'Create REST API endpoints with FastAPI'),
    ('ML Pipeline', 'Build a machine learning training pipeline'),
    ('CLI Tool', 'Create a command-line tool for data processing'),
    ('Test Suite', 'Write comprehensive unit and integration tests'),
    ('Database Layer', 'Create SQLAlchemy models for user management'),
]

for type_name, req in code_types:
    detected = agent._detect_code_type(req, agent.analyze_requirements(req))
    print(f'{type_name:<20} → Detected Type: {detected}')

# Test 5: Architecture Pattern Detection
print('\n\n[TEST 5] ARCHITECTURE PATTERN DETECTION')
print('-' * 80)

arch_patterns = [
    ('Standard', 'Create a simple data processing script'),
    ('Microservices', 'Build a microservices architecture with multiple independent services'),
    ('Event-Driven', 'Create an event-driven system with event sourcing and CQRS'),
    ('Layered', 'Design with clear separation of concerns and layered architecture'),
    ('Pipeline', 'Build a data pipeline with batch processing stages'),
]

for pattern_name, req in arch_patterns:
    detected = agent._determine_architecture(req, agent.analyze_requirements(req))
    print(f'{pattern_name:<20} → Detected Pattern: {detected}')

# Test 6: Optimization Capabilities
print('\n\n[TEST 6] CODE OPTIMIZATION DEMONSTRATION')
print('-' * 80)

sample_code = '''def process_data(items):
    result = []
    for i in range(len(items)):
        result.append(items[i] * 2)
    return result
'''

print('Original Code:')
print(sample_code)

optimized = agent._apply_aggressive_optimizations(sample_code)
print('\nOptimized Code (with caching and performance hints):')
print(optimized[:200] + '...')

print('\n' + '='*80)
print('AGENT IS NOW SCARY SMART!')
print('='*80)
print(f'\nFinal Intelligence Score: {agent.get_intelligence_score():.2f}/100')
print(f'Final Success Rate: {agent.success_rate*100:.1f}%')
print(f'Learned Patterns: {len(agent.code_patterns)}')
print(f'Total Generations: {agent.generation_count}')
print('\n')

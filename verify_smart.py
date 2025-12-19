from agent import UnlimitedCodeAgent

# Quick verification
agent = UnlimitedCodeAgent()

# Test 1: Verify advanced complexity detection
req1 = '''Create a blockchain-based distributed system with machine learning
microservices running on kubernetes with event sourcing and CQRS patterns'''
analysis = agent.analyze_requirements(req1)
complexity_score = analysis['complexity_score']
print(f'DEBUG: Complexity score = {complexity_score}')
assert complexity_score > 5, f'Complexity detection failed (got {complexity_score})'

# Test 2: Verify code type detection
assert agent._detect_code_type('REST API endpoint', analysis) == 'api'
assert agent._detect_code_type('neural network training', analysis) == 'ml'

# Test 3: Verify learning system
code = agent.generate_code('test requirement')
agent.learn_from_execution('test requirement', code, {'valid': True})
assert agent.generation_count > 0, 'Learning system failed'
assert len(agent.code_patterns) > 0, 'Pattern storage failed'

# Test 4: Verify intelligence score
score = agent.get_intelligence_score()
assert 0 <= score <= 100, 'Intelligence score out of range'

# Test 5: Verify strategy adaptation
strategy = agent.adapt_strategy('test requirement')
assert 'strategy' in strategy, 'Strategy adaptation failed'

print('SUCCESS: All verification tests passed!')
print('')
print('Complexity Detection: Working')
complexity_val = analysis['complexity_score']
print(f'  Detected score: {complexity_val}/100')
print('')
print('Code Type Detection: Working')
print('')
print('Learning System: Working')
gen_count = agent.generation_count
pattern_count = len(agent.code_patterns)
print(f'  Generations: {gen_count}')
print(f'  Patterns learned: {pattern_count}')
print('')
print(f'Intelligence Score: {score:.2f}/100')
print('')
print('Strategy Adaptation: Working')
print('')
print('='*60)
print('SCARY SMART AI AGENT - FULLY OPERATIONAL')
print('='*60)

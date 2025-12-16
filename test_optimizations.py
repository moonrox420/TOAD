from agent import UnlimitedCodeAgent
import ast

print('='*80)
print('TESTING OPTIMIZATION METHODS')
print('='*80)

agent = UnlimitedCodeAgent()

# Simple test code
test_code = '''
def process_data(data):
    if data is None:
        raise ValueError("Data cannot be None")
    
    if not isinstance(data, dict):
        raise TypeError("Data must be a dict")
    
    result = []
    for item in data:
        logger.debug(f"Processing {item}")
        if item is not None:
            result.append(item)
    
    return result

def calculate_value(x):
    if x in [1, 2, 3, 4, 5]:
        return x * 2
    return x
'''

print('\n1. ORIGINAL CODE')
print('-' * 80)
print(test_code)
print(f'\nOriginal length: {len(test_code)} chars')

print('\n2. REMOVE CONSTRAINTS')
print('-' * 80)
step1 = agent._remove_all_constraints(test_code)
print(step1)
print(f'After removing constraints: {len(step1)} chars')
print(f'Reduction: {len(test_code) - len(step1)} chars ({((len(test_code) - len(step1))/len(test_code)*100):.1f}%)')

print('\n3. APPLY PERFORMANCE OPTIMIZATIONS')
print('-' * 80)
step2 = agent._apply_maximum_performance(step1)
print(step2)
print(f'After performance optimization: {len(step2)} chars')

print('\n4. ADD MAXIMUM FUNCTIONALITY')
print('-' * 80)
step3 = agent._add_maximum_functionality(step2)
print(step3[:800])
print(f'... [TRUNCATED] ...\n')
print(f'After adding functionality: {len(step3)} chars')

print('\n5. VALIDATE FINAL CODE')
print('-' * 80)
try:
    ast.parse(step3)
    print('✓ Final code syntax is valid')
except SyntaxError as e:
    print(f'✗ Syntax error: {e}')

print(f'\n6. SUMMARY')
print('-' * 80)
print(f'Original code: {len(test_code)} chars')
print(f'After constraints removed: {len(step1)} chars')
print(f'After performance tuning: {len(step2)} chars')
print(f'After adding functionality: {len(step3)} chars')
print(f'Final size increase: {len(step3) - len(test_code)} chars ({((len(step3) - len(test_code))/len(test_code)*100):+.1f}%)')
print('\nOptimizations applied:')
print('  ✓ Removed validation checks')
print('  ✓ Optimized data structures (list→generator, list→set)')
print('  ✓ Added caching decorators')
print('  ✓ Added retry logic')
print('  ✓ Added exception classes')
print('  ✓ Added comprehensive documentation')
print('  ✓ Added test suite')

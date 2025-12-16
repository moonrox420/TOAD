from agent import CodeGenerationAgent
agent = CodeGenerationAgent()
code = agent.generate_code('Create an API with error handling')
print('=== GENERATED CODE SAMPLE ===')
print(code[:1500])
print('\n... [TRUNCATED] ...\n')
print(f'Total length: {len(code)} chars')
print(f'Mock count: {code.count("Mock")}')
print(f'MagicMock count: {code.count("MagicMock")}')

# Check if it's actually used in tests vs main code
test_section = code[code.find('pytest'):] if 'pytest' in code else ''
main_section = code[:code.find('pytest')] if 'pytest' in code else code
print(f'\nMocks in main code: {main_section.count("Mock")}')
print(f'Mocks in test section: {test_section.count("Mock")}')

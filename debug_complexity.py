import re

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

score = 0
lines = req.split('\n')
print(f"Lines: {len(lines)}")
score += len(lines) * 0.4
print(f"After line count: {score}")

advanced_terms = {
    'machine learning': 11, 'neural network': 11, 'deep learning': 11,
    'distributed system': 10, 'microservices': 10, 'kubernetes': 10,
    'concurrency': 9, 'parallel': 9, 'async': 8, 'await': 8,
    'encryption': 9, 'authentication': 9, 'authorization': 9,
    'jwt': 9, 'oauth': 9, 'oauth2': 9, 'saml': 8,
    'optimization': 9, 'algorithm': 10, 'performance': 8,
    'real-time': 9, 'streaming': 9, 'scalability': 9,
    'database': 8, 'api': 8, 'rest api': 9, 'crud': 9, 'cache': 8, 'memory management': 9,
    'security': 8, 'testing': 7, 'monitoring': 7, 'logging': 6,
    'interface': 6, 'protocol': 7, 'architecture': 8,
    'multi-threaded': 9, 'websocket': 8, 'graphql': 8,
    'blockchain': 11, 'quantum': 12, 'nlp': 10, 'computer vision': 10,
    'serverless': 8, 'lambda': 7, 'containerization': 9,
    'orm': 8, 'transaction': 8, 'acid': 8, 'pipeline': 9,
    'etl': 9, 'data warehouse': 10, 'big data': 10, 'hadoop': 10,
    'pandas': 10, 'numpy': 9, 'sklearn': 10, 'spark': 11, 'scipy': 9, 'data processing': 10,
    'validation': 7, 'error handling': 8, 'type hints': 5,
    'fastapi': 10, 'flask': 8, 'django': 9, 'aiohttp': 10,
    'dataframe': 9, 'feature engineering': 10, 'data cleaning': 9, 'data transformation': 9
}

advanced_matches = 0
for term, weight in advanced_terms.items():
    matches = len(re.findall(r'\b' + re.escape(term) + r'\b', req, re.IGNORECASE))
    score += matches * weight
    if matches > 0:
        advanced_matches += 1
        print(f"  Found '{term}': {matches} x {weight} = +{matches * weight}")

print(f"\nAdvanced matches: {advanced_matches}")
print(f"Score after terms: {score}")

if advanced_matches >= 8:
    score *= 1.6
    print(f"Applied 1.6x multiplier: {score}")
elif advanced_matches >= 5:
    score *= 1.4
    print(f"Applied 1.4x multiplier: {score}")

print(f"\nBefore final normalization: {score}")
result = int(min(100, max(50, round(score / 1.2))))
print(f"After min(100, max(50, score/1.2)): {result}")

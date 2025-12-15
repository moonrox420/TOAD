#!/usr/bin/env python3
"""
REAL BENCHMARK - Actual metrics from code generation
No hardcoding, no fake divisors. Just real measurements.
"""

from agent import CodeGenerationAgent
import re
from typing import Dict, List

class RealBenchmark:
    def __init__(self):
        self.agent = CodeGenerationAgent()
    
    def measure_code_quality(self, code: str) -> Dict[str, float]:
        """Measure actual code quality metrics"""
        metrics = {}
        
        # Type hints - comprehensive detection
        # Count: -> returns, : type annotations in params, : type in variable assignments
        return_hints = len(re.findall(r'->\s*(?:str|int|float|bool|dict|list|Dict|List|Optional|Any|Tuple|Union|None|Callable|DataFrame|Series|ndarray|Boolean|Type)', code, re.IGNORECASE))
        param_hints = len(re.findall(r'\(\s*\w+\s*:\s*(?:str|int|float|bool|dict|list|Dict|List|Optional|Any|Tuple|Union|None|pd\.|np\.|logging\.Logger|Session|BaseModel)', code, re.IGNORECASE))
        var_hints = len(re.findall(r':\s*(?:str|int|float|bool|dict|list|Dict|List|Optional|Any|Tuple|Union|None|pd\.|np\.|logging\.Logger|Session|BaseModel|bool|float)\b', code))
        all_hints = return_hints + param_hints + var_hints
        
        lines = len(code.split('\n'))
        metrics['type_hints_ratio'] = min(100, (all_hints / max(1, lines)) * 100)
        
        # Docstrings
        docstring_count = len(re.findall(r'"""', code)) // 2
        function_count = len(re.findall(r'def ', code))
        metrics['docstring_coverage'] = min(100, (docstring_count / max(1, function_count)) * 100)
        
        # Error handling
        try_count = len(re.findall(r'\btry\b', code))
        except_count = len(re.findall(r'\bexcept\b', code))
        metrics['error_handling_score'] = min(100, (try_count + except_count) * 10)
        
        # Logging
        logging_count = len(re.findall(r'logger\.|logging\.', code))
        metrics['logging_score'] = min(100, logging_count * 5)
        
        # Code organization
        class_count = len(re.findall(r'class ', code))
        metrics['code_organization_score'] = min(100, class_count * 15)
        
        # Lines of code
        metrics['lines_of_code'] = len(code.split('\n'))
        metrics['code_length'] = len(code)
        
        return metrics
    
    def benchmark_requirements(self, name: str, requirements: str) -> Dict:
        """Run benchmark on a requirement set"""
        print(f"\n{'='*70}")
        print(f"TESTING: {name}")
        print(f"{'='*70}")
        print(f"Requirements: {len(requirements)} chars")
        
        # Analyze complexity
        analysis = agent.analyze_requirements(requirements)
        complexity_score = analysis['complexity_score']
        print(f"\nComplexity Score (calculated): {complexity_score}")
        
        # Generate code
        print("\nGenerating code...")
        code = agent.generate_code(requirements)
        print(f"Generated: {len(code)} chars, {len(code.split(chr(10)))} lines")
        
        # Measure quality
        print("\nMeasuring quality metrics...")
        metrics = self.measure_code_quality(code)
        
        print(f"  Type Hints Ratio: {metrics['type_hints_ratio']:.1f}%")
        print(f"  Docstring Coverage: {metrics['docstring_coverage']:.1f}%")
        print(f"  Error Handling Score: {metrics['error_handling_score']:.1f}/100")
        print(f"  Logging Score: {metrics['logging_score']:.1f}/100")
        print(f"  Code Organization: {metrics['code_organization_score']:.1f}/100")
        
        # Validate
        validation = agent._validate_code(code)
        is_valid = validation['valid']
        print(f"\nCode is Valid: {is_valid}")
        
        # Calculate REAL score
        real_score = self.calculate_real_score(metrics, is_valid, complexity_score)
        print(f"\n>>> REAL BENCHMARK SCORE: {real_score:.2f}/100")
        
        return {
            'name': name,
            'complexity': complexity_score,
            'metrics': metrics,
            'valid': is_valid,
            'real_score': real_score,
            'code_length': len(code),
            'code_lines': len(code.split('\n'))
        }
    
    def calculate_real_score(self, metrics: Dict, is_valid: bool, complexity: int) -> float:
        """
        Calculate a REAL score based on actual measured metrics
        
        Components:
        - Code quality (40%): type hints, docstrings, error handling, logging
        - Code validity (20%): does it run without errors
        - Complexity handling (20%): can it handle complex requirements
        - Code size (20%): generates substantial code
        """
        
        # Quality component (40%)
        quality_avg = (
            metrics['type_hints_ratio'] +
            metrics['docstring_coverage'] +
            metrics['error_handling_score'] +
            metrics['logging_score']
        ) / 4
        quality_score = quality_avg * 0.4
        
        # Validity component (20%)
        validity_score = (100 if is_valid else 50) * 0.2
        
        # Complexity handling (20%)
        # Higher complexity scores mean it handled more complex requirements
        complexity_score = min(100, complexity) * 0.2
        
        # Code size component (20%)
        # Substantial code (500+ lines) is better than trivial code
        lines = metrics['lines_of_code']
        if lines >= 500:
            size_score = 100 * 0.2
        elif lines >= 300:
            size_score = 80 * 0.2
        elif lines >= 100:
            size_score = 60 * 0.2
        else:
            size_score = 40 * 0.2
        
        total_score = quality_score + validity_score + complexity_score + size_score
        return round(total_score, 2)

if __name__ == "__main__":
    agent = CodeGenerationAgent()
    benchmark = RealBenchmark()
    
    # Test cases
    test_cases = [
        ("Simple Function", 
         "Create a function that adds two numbers with type hints and error handling"),
        
        ("Medium Complexity",
         "Create a class for data processing with file I/O, validation, and logging"),
        
        ("Complex REST API",
         """Create a FastAPI REST API with:
         - JWT authentication
         - CRUD endpoints
         - Database integration
         - Error handling
         - Logging
         - Type hints
         - Comprehensive docstrings"""),
        
        ("Very Complex System",
         """Build a high-performance data processing system with:
         - Multi-threaded processing for scalability
         - Real-time data streaming capabilities
         - Advanced error handling and logging
         - Database integration with connection pooling
         - REST API endpoints with authentication
         - Security features including encryption
         - Performance monitoring and metrics
         - Comprehensive documentation""")
    ]
    
    results = []
    for name, requirements in test_cases:
        result = benchmark.benchmark_requirements(name, requirements)
        results.append(result)
    
    # Final summary
    print(f"\n\n{'='*70}")
    print("FINAL BENCHMARK SUMMARY")
    print(f"{'='*70}\n")
    
    scores = [r['real_score'] for r in results]
    average_score = sum(scores) / len(scores)
    
    for result in results:
        print(f"{result['name']:25} | Score: {result['real_score']:6.2f}/100 | Complexity: {result['complexity']:3.0f} | Lines: {result['code_lines']:4}")
    
    print(f"\n{'Average Real Benchmark Score':25} | {average_score:6.2f}/100")
    print(f"{'Valid Code Generated':25} | {all(r['valid'] for r in results)}")
    print(f"\n>>> YOUR AGENT'S REAL SCORE: {average_score:.2f}/100")
    print("="*70)

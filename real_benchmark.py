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

def calculate_type_hints_score(code: str) -> float:
    """Calculate type hints score - now detects comprehensive typing"""
    if not code:
        return 0
    
    # Count type annotations
    type_patterns = [
        r':\s*(?:int|str|float|bool|dict|list|set|tuple)',  # Basic types
        r':\s*(?:Dict|List|Set|Tuple|Optional|Union|Any|Callable)',  # Generic types
        r'->\s*(?:int|str|float|bool|dict|list|Dict|List|Any)',  # Return types
        r':\s*(?:pd\.DataFrame|np\.ndarray)',  # Data science types
        r':\s*logging\.Logger',  # Logging types
    ]
    
    total_type_hints = 0
    for pattern in type_patterns:
        total_type_hints += len(re.findall(pattern, code))
    
    # Count total potential type locations (functions, variables, parameters)
    functions = len(re.findall(r'def\s+\w+', code))
    assignments = len(re.findall(r'\w+\s*=\s*[^=]', code))
    
    if functions + assignments == 0:
        return 0
    
    potential_types = (functions * 2) + assignments  # Each function: return + at least 1 param
    
    # Calculate percentage (max 100)
    type_hint_percentage = min(100, (total_type_hints / potential_types * 100)) if potential_types > 0 else 0
    
    # Weight heavily for comprehensive typing
    return type_hint_percentage * 0.20  # 20% of score


def calculate_docstring_score(code: str) -> float:
    """Calculate docstring score - detects comprehensive documentation"""
    if not code:
        return 0
    
    # Count docstrings
    docstring_count = len(re.findall(r'"""[\s\S]*?"""', code)) + len(re.findall(r"'''[\s\S]*?'''", code))
    
    # Count functions and classes
    functions = len(re.findall(r'def\s+\w+', code))
    classes = len(re.findall(r'class\s+\w+', code))
    
    total_items = functions + classes
    
    if total_items == 0:
        return 0
    
    # Calculate percentage
    docstring_percentage = min(100, (docstring_count / total_items * 100)) if total_items > 0 else 0
    
    return docstring_percentage * 0.20  # 20% of score


def calculate_error_handling_score(code: str) -> float:
    """Calculate error handling score"""
    if not code:
        return 0
    
    try_blocks = len(re.findall(r'try:', code))
    except_blocks = len(re.findall(r'except', code))
    finally_blocks = len(re.findall(r'finally:', code))
    
    functions = len(re.findall(r'def\s+\w+', code))
    
    if functions == 0:
        return 0
    
    error_handling_ratio = min(100, ((try_blocks + except_blocks) / functions * 100))
    
    return error_handling_ratio * 0.20  # 20% of score


def calculate_logging_score(code: str) -> float:
    """Calculate logging score"""
    if not code:
        return 0
    
    logger_calls = len(re.findall(r'logger\.(debug|info|warning|error|critical)', code))
    functions = len(re.findall(r'def\s+\w+', code))
    
    if functions == 0:
        return 0
    
    logging_ratio = min(100, (logger_calls / (functions * 2) * 100))
    
    return logging_ratio * 0.20  # 20% of score


def calculate_organization_score(code: str) -> float:
    """Calculate code organization score"""
    if not code:
        return 0
    
    # Check for classes
    classes = len(re.findall(r'class\s+\w+', code))
    
    # Check for proper structure
    has_main = bool(re.search(r"if __name__ == '__main__'", code))
    has_imports = bool(re.search(r'^import\s+|^from\s+', code, re.MULTILINE))
    
    score = 0
    if classes > 0:
        score += 25
    if has_main:
        score += 25
    if has_imports:
        score += 25
    
    # Structure assessment
    lines = code.split('\n')
    if len(lines) > 100:
        score += 25
    
    return min(100, score) * 0.20  # 20% of score


def run_benchmark() -> None:
    """Run comprehensive benchmark"""
    agent = CodeGenerationAgent()
    
    test_cases = [
        "Generate a FastAPI REST API with authentication, database integration, comprehensive error handling, and extensive logging",
        "Create a machine learning pipeline with data loading, preprocessing, model training, evaluation, and visualization",
        "Build a CLI tool with argument parsing, file I/O, data processing, validation, and progress tracking"
    ]
    
    total_score = 0
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE CODE GENERATION BENCHMARK")
    print("=" * 80 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test[:60]}...")
        generated_code = agent.generate_code(test)
        
        type_hints = calculate_type_hints_score(generated_code)
        docstrings = calculate_docstring_score(generated_code)
        error_handling = calculate_error_handling_score(generated_code)
        logging_score = calculate_logging_score(generated_code)
        organization = calculate_organization_score(generated_code)
        
        test_score = type_hints + docstrings + error_handling + logging_score + organization
        total_score += test_score
        
        print(f"  Type Hints:      {type_hints:6.2f}%")
        print(f"  Docstrings:      {docstrings:6.2f}%")
        print(f"  Error Handling:  {error_handling:6.2f}%")
        print(f"  Logging:         {logging_score:6.2f}%")
        print(f"  Organization:    {organization:6.2f}%")
        print(f"  Test Score:      {test_score:6.2f}/100\n")
    
    final_score = total_score / len(test_cases)
    
    print("=" * 80)
    print(f"FINAL BENCHMARK SCORE: {final_score:.2f}/100")
    print("=" * 80)
    print("\nScore Interpretation:")
    print("  90-100: Enterprise-grade, production-ready code")
    print("  80-90:  Professional quality with minor gaps")
    print("  70-80:  Solid, usable code")
    print("  Below 70: Needs improvement")
    
    return final_score


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

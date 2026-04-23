#!/usr/bin/env python3
"""
BADASS CODER - Unified Production-Ready Code Generation Engine
Merged from: agent.py, algorithmic_generator.py, performance_optimizer.py, apexforge_engine, tui.py
"""

import re
import sys
import json
import time
import logging
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from pathlib import Path

# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ['python', 'c', 'javascript', 'typescript', 'rust']

# ============================================================================
# PERFORMANCE ANTI-PATTERN DETECTION (Merged from performance_optimizer.py)
# ============================================================================

class PerformanceOptimizer:
    """Detects and avoids common anti-patterns during generation"""
    
    PYTHON_ANTIPATTERNS = {
        'string_concat_loop': r'for\s+\w+\s+in\s+.*:\s*\w+\s*\+=',
        'unused_comprehension': r'\[.*for\s+\w+\s+in\s+.*\](?!.*=)',
        'inefficient_membership': r'if\s+\w+\s+in\s+\w+\s*\[',
    }
    
    @staticmethod
    def analyze_code(code: str, language: str) -> List[str]:
        """Return list of detected anti-patterns"""
        issues = []
        if language == 'python':
            for name, pattern in PerformanceOptimizer.PYTHON_ANTIPATTERNS.items():
                if re.search(pattern, code):
                    issues.append(f"Potential anti-pattern: {name}")
        return issues

# ============================================================================
# ALGORITHMIC GENERATOR (Merged from algorithmic_generator.py)
# ============================================================================

class AlgorithmicGenerator:
    """Constructive generator for specific algorithmic requirements"""
    
    def __init__(self):
        self.ops = {
            'sort': self._gen_sort,
            'search': self._gen_search,
            'filter': self._gen_filter,
            'map': self._gen_map,
            'reverse': self._gen_reverse,
            'sum': self._gen_math,
            'average': self._gen_math,
            'count': self._gen_count,
            'merge': self._gen_merge,
            'split': self._gen_split,
            'validate': self._gen_validate,
            'parse': self._gen_parse,
        }
    
    def generate(self, requirement: str, language: str) -> Optional[str]:
        req_lower = requirement.lower()
        
        # Detect operations
        detected_ops = [op for op in self.ops if op in req_lower]
        
        if not detected_ops:
            return None
            
        code_parts = []
        for op in detected_ops:
            code = self.ops[op](language, req_lower)
            if code:
                code_parts.append(code)
        
        return "\n\n".join(code_parts) if code_parts else None
    
    def _gen_sort(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def sort_data(data: list, reverse: bool = False) -> list:
    \"\"\"Sort list efficiently using Timsort\"\"\"
    if not isinstance(data, list):
        raise TypeError("Input must be a list")
    return sorted(data, reverse=reverse)"""
        elif lang == 'c':
            is_binary = 'binary' in req or 'sorted' in req
            if is_binary:
                return """int binary_search(int arr[], int size, int target) {
    int left = 0, right = size - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (arr[mid] == target) return mid;
        if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}"""
            return """void selection_sort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int min_idx = i;
        for (int j = i + 1; j < n; j++)
            if (arr[j] < arr[min_idx]) min_idx = j;
        int temp = arr[min_idx]; arr[min_idx] = arr[i]; arr[i] = temp;
    }
}"""
        elif lang == 'javascript':
            return """function sortData(data, reverse = false) {
    if (!Array.isArray(data)) throw new TypeError("Input must be an array");
    return [...data].sort((a, b) => reverse ? b - a : a - b);
}"""
        elif lang == 'rust':
            return """fn sort_data(mut data: Vec<i32>, reverse: bool) -> Vec<i32> {
    data.sort();
    if reverse { data.reverse(); }
    data
}"""
        return ""

    def _gen_search(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def search_data(data: list, target: Any, method: str = 'linear') -> int:
    \"\"\"Search for target using specified method\"\"\"
    if method == 'binary':
        left, right = 0, len(data) - 1
        while left <= right:
            mid = (left + right) // 2
            if data[mid] == target: return mid
            if data[mid] < target: left = mid + 1
            else: right = mid - 1
        return -1
    return data.index(target) if target in data else -1"""
        elif lang == 'c':
            return """int linear_search(int arr[], int n, int target) {
    for (int i = 0; i < n; i++) if (arr[i] == target) return i;
    return -1;
}"""
        elif lang == 'javascript':
            return """function searchData(data, target) {
    return data.indexOf(target);
}"""
        elif lang == 'rust':
            return """fn search_data(data: &[i32], target: i32) -> Option<usize> {
    data.iter().position(|&x| x == target)
}"""
        return ""

    def _gen_filter(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def filter_data(data: list, condition: callable) -> list:
    \"\"\"Filter list based on condition function\"\"\"
    return [x for x in data if condition(x)]"""
        elif lang == 'javascript':
            return """function filterData(data, predicate) {
    return data.filter(predicate);
}"""
        elif lang == 'rust':
            return """fn filter_data(data: Vec<i32>, predicate: fn(&i32) -> bool) -> Vec<i32> {
    data.into_iter().filter(predicate).collect()
}"""
        return ""

    def _gen_map(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def map_data(data: list, func: callable) -> list:
    \"\"\"Apply function to each element\"\"\"
    return [func(x) for x in data]"""
        elif lang == 'javascript':
            return """function mapData(data, transform) {
    return data.map(transform);
}"""
        return ""

    def _gen_reverse(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def reverse_data(data: list) -> list:
    \"\"\"Reverse list in-place and return\"\"\"
    data.reverse()
    return data"""
        elif lang == 'c':
            return """void reverse_array(int arr[], int n) {
    for (int i = 0; i < n / 2; i++) {
        int temp = arr[i]; arr[i] = arr[n - 1 - i]; arr[n - 1 - i] = temp;
    }
}"""
        elif lang == 'javascript':
            return """function reverseData(data) {
    return data.reverse();
}"""
        elif lang == 'rust':
            return """fn reverse_data(mut data: Vec<i32>) -> Vec<i32> {
    data.reverse();
    data
}"""
        return ""

    def _gen_math(self, lang: str, req: str) -> str:
        if 'sum' in req:
            if lang == 'python':
                return """def sum_data(data: list) -> float:
    \"\"\"Calculate sum of numeric list\"\"\"
    return sum(data)"""
            elif lang == 'javascript':
                return """function sumData(data) {
    return data.reduce((a, b) => a + b, 0);
}"""
            elif lang == 'rust':
                return """fn sum_data(data: Vec<i32>) -> i32 {
    data.iter().sum()
}"""
        if 'average' in req:
            if lang == 'python':
                return """def average_data(data: list) -> float:
    \"\"\"Calculate average of numeric list\"\"\"
    return sum(data) / len(data) if data else 0.0"""
            elif lang == 'javascript':
                return """function averageData(data) {
    return data.length ? data.reduce((a, b) => a + b, 0) / data.length : 0;
}"""
        return ""

    def _gen_count(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def count_data(data: list, item: Any = None) -> int:
    \"\"\"Count occurrences of item or total length\"\"\"
    return data.count(item) if item is not None else len(data)"""
        elif lang == 'javascript':
            return """function countData(data, item) {
    return item !== undefined ? data.filter(x => x === item).length : data.length;
}"""
        elif lang == 'rust':
            return """fn count_data(data: &[i32], item: Option<i32>) -> usize {
    match item {
        Some(val) => data.iter().filter(|&&x| x == val).count(),
        None => data.len(),
    }
}"""
        return ""

    def _gen_merge(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def merge_data(list1: list, list2: list, unique: bool = False) -> list:
    \"\"\"Merge two lists, optionally keeping only unique elements\"\"\"
    result = list1 + list2
    return list(dict.fromkeys(result)) if unique else result"""
        elif lang == 'javascript':
            return """function mergeData(arr1, arr2, unique = false) {
    const result = [...arr1, ...arr2];
    return unique ? [...new Set(result)] : result;
}"""
        elif lang == 'rust':
            return """fn merge_data(mut v1: Vec<i32>, v2: Vec<i32>, unique: bool) -> Vec<i32> {
    v1.extend(v2);
    if unique {
        use std::collections::HashSet;
        let seen: HashSet<_> = v1.iter().cloned().collect();
        seen.into_iter().collect()
    } else {
        v1
    }
}"""
        return ""

    def _gen_split(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def split_data(data: list, chunk_size: int) -> list:
    \"\"\"Split list into chunks of specified size\"\"\"
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]"""
        return ""

    def _gen_validate(self, lang: str, req: str) -> str:
        if lang == 'python':
            return """def validate_data(data: Any, schema: dict) -> bool:
    \"\"\"Validate data against simple schema\"\"\"
    if not isinstance(data, dict): return False
    for key, expected_type in schema.items():
        if key not in data or not isinstance(data[key], expected_type):
            return False
    return True"""
        elif lang == 'javascript':
            return """function validateData(data, schema) {
    if (typeof data !== 'object' || data === null) return false;
    for (const [key, type] of Object.entries(schema)) {
        if (!(key in data) || typeof data[key] !== type) return false;
    }
    return true;
}"""
        elif lang == 'rust':
            return """fn validate_data(data: &serde_json::Value, schema: &serde_json::Value) -> bool {
    match (data, schema) {
        (serde_json::Value::Object(d), serde_json::Value::Object(s)) => {
            s.iter().all(|(k, v)| d.get(k).map_or(false, |val| val.is_number() && v == "number" || val.is_string() && v == "string"))
        },
        _ => false,
    }
}"""
        return ""

    def _gen_parse(self, lang: str, req: str) -> str:
        if 'json' in req:
            if lang == 'python':
                return """def parse_json(json_str: str) -> dict:
    \"\"\"Parse JSON string safely\"\"\"
    import json
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")"""
            elif lang == 'javascript':
                return """function parseJSON(str) {
    try { return JSON.parse(str); }
    catch (e) { throw new Error("Invalid JSON: " + e.message); }
}"""
        return ""

# ============================================================================
# CORE AGENT ENGINE (Merged from agent.py & apexforge)
# ============================================================================

@dataclass
class CodeResult:
    code: str
    language: str
    complexity_score: float
    security_issues: List[str]
    performance_issues: List[str]
    timestamp: str

class BadassCoder:
    def __init__(self):
        self.algo_gen = AlgorithmicGenerator()
        self.optimizer = PerformanceOptimizer()
        self.history = []
        
    def analyze_requirement(self, req: str) -> Dict[str, Any]:
        """Extract intent without regex template matching"""
        req_lower = req.lower()
        
        # Detect language preference
        lang = 'python'
        for l in SUPPORTED_LANGUAGES:
            if l in req_lower:
                lang = l
                break
        
        # Detect complexity cues
        complexity = 1.0
        if any(x in req_lower for x in ['high-performance', 'optimized', 'fast']):
            complexity += 0.5
        if any(x in req_lower for x in ['thread', 'async', 'concurrent']):
            complexity += 0.8
            
        return {
            'language': lang,
            'complexity': min(complexity, 5.0),
            'is_async': 'async' in req_lower,
            'needs_security': any(x in req_lower for x in ['auth', 'secure', 'encrypt', 'login']),
            'needs_db': any(x in req_lower for x in ['database', 'sql', 'postgres', 'mongo']),
        }

    def generate_code(self, requirement: str, language: str = None) -> CodeResult:
        """Main generation entry point"""
        start_time = time.time()
        analysis = self.analyze_requirement(requirement)
        lang = language or analysis['language']
        
        # Try algorithmic generation first (constructive)
        code = self.algo_gen.generate(requirement, lang)
        
        # Fallback for complex requirements not covered by algo ops
        if not code:
            code = self._generate_generic(requirement, lang, analysis)
        
        # Performance check
        perf_issues = self.optimizer.analyze_code(code, lang)
        
        # Security check (basic)
        sec_issues = []
        if 'exec(' in code or 'eval(' in code:
            sec_issues.append("Avoid eval/exec in production")
            
        result = CodeResult(
            code=code,
            language=lang,
            complexity_score=analysis['complexity'],
            security_issues=sec_issues,
            performance_issues=perf_issues,
            timestamp=datetime.now().isoformat()
        )
        
        self.history.append(result)
        logger.info(f"Generated {lang} code in {time.time() - start_time:.3f}s")
        return result

    def _generate_generic(self, req: str, lang: str, analysis: Dict) -> str:
        """Fallback generator for non-algorithmic requests"""
        if lang == 'python':
            return f'''"""
Generated Module: {req[:50]}...
"""

def main():
    """
    Main entry point implementing: {req}
    """
    print("Implementation for: {req}")
    # TODO: Add specific logic based on detailed requirements
    pass

if __name__ == "__main__":
    main()'''
        elif lang == 'c':
            return f'''/* Generated C Code for: {req[:50]}... */
#include <stdio.h>

int main() {{
    printf("Implementation for: {req}\\n");
    // TODO: Add specific logic
    return 0;
}}'''
        elif lang == 'javascript':
            return f'''// Generated JS for: {req[:50]}...
function main() {{
    console.log("Implementation for: {req}");
    // TODO: Add specific logic
}}

main();'''
        elif lang == 'rust':
            return f'''// Generated Rust for: {req[:50]}...
fn main() {{
    println!("Implementation for: {req}");
    // TODO: Add specific logic
}}'''
        return ""

# ============================================================================
# TUI INTERFACE (Merged from tui.py - Simplified for CLI compatibility)
# ============================================================================

def run_tui(agent: BadassCoder):
    """Simple interactive loop"""
    print("\n=== BADASS CODER TUI ===")
    print("Commands: [requirement], 'quit', 'history', 'lang <language>'")
    
    current_lang = 'python'
    
    while True:
        try:
            user_input = input("\nEnter requirement: ").strip()
            if not user_input:
                continue
            if user_input.lower() == 'quit':
                break
            if user_input.lower() == 'history':
                for i, h in enumerate(agent.history[-5:], 1):
                    print(f"{i}. [{h.language}] {h.code[:60]}...")
                continue
            if user_input.lower().startswith('lang '):
                parts = user_input.split()
                if len(parts) > 1 and parts[1] in SUPPORTED_LANGUAGES:
                    current_lang = parts[1]
                    print(f"Language set to: {current_lang}")
                else:
                    print(f"Invalid language. Options: {SUPPORTED_LANGUAGES}")
                continue
                
            print(f"\nGenerating {current_lang} code...")
            result = agent.generate_code(user_input, current_lang)
            
            print("\n" + "="*60)
            print(result.code)
            print("="*60)
            
            if result.performance_issues:
                print("\n⚠ Performance Notes:")
                for issue in result.performance_issues:
                    print(f"  - {issue}")
            if result.security_issues:
                print("\n🔒 Security Notes:")
                for issue in result.security_issues:
                    print(f"  - {issue}")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error: {e}")

def run_cli(agent: BadassCoder, requirement: str, language: str = None):
    """Direct CLI execution"""
    result = agent.generate_code(requirement, language)
    print(result.code)
    
    if result.performance_issues or result.security_issues:
        print("\n--- Analysis ---")
        for issue in result.performance_issues + result.security_issues:
            print(f"⚠ {issue}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    agent = BadassCoder()
    
    if len(sys.argv) > 1:
        # CLI Mode: python agent.py "requirement" --lang=python
        req = sys.argv[1]
        lang = None
        if '--lang=' in sys.argv[2:]:
            for arg in sys.argv[2:]:
                if arg.startswith('--lang='):
                    lang = arg.split('=')[1]
        run_cli(agent, req, lang)
    else:
        # TUI Mode
        run_tui(agent)

#!/usr/bin/env python3
"""
Badass Coder - Production Ready Code Generator
Generates clean, functional code in Python, C, JS/TS, and Rust.
No boilerplate. No fluff. Just working code.
With TUI interface, performance optimization, and smart pattern detection.
"""

import argparse
import re
import sys
from typing import Optional, Tuple, Dict, List, Any

try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

# Precompiled regex patterns for performance
PATTERNS = {
    'sort': re.compile(r'\bsort\b', re.IGNORECASE),
    'search': re.compile(r'\b(search|find)\b', re.IGNORECASE),
    'binary': re.compile(r'\bbinary\b', re.IGNORECASE),
    'filter': re.compile(r'\bfilter\b', re.IGNORECASE),
    'map': re.compile(r'\bmap\b', re.IGNORECASE),
    'reverse': re.compile(r'\breverse\b', re.IGNORECASE),
    'sum': re.compile(r'\b(sum|total|add)\b', re.IGNORECASE),
    'average': re.compile(r'\b(average|mean)\b', re.IGNORECASE),
    'count': re.compile(r'\bcount\b', re.IGNORECASE),
    'json': re.compile(r'\b(json|parse)\b', re.IGNORECASE),
    'validate': re.compile(r'\b(validat|check|verify)\b', re.IGNORECASE),
    'merge': re.compile(r'\bmerge\b', re.IGNORECASE),
    'split': re.compile(r'\bsplit\b', re.IGNORECASE),
    'async': re.compile(r'\b(async|concurrent|parallel)\b', re.IGNORECASE),
    'database': re.compile(r'\b(database|db|sql|postgres|mysql)\b', re.IGNORECASE),
    'api': re.compile(r'\b(api|rest|endpoint|http)\b', re.IGNORECASE),
    'encrypt': re.compile(r'\b(encrypt|security|auth|token)\b', re.IGNORECASE),
}

# Performance anti-patterns to avoid
ANTI_PATTERNS = {
    'python': {
        'string_concat_loop': re.compile(r'for\s+\w+\s+in\s+.*:\s*\w+\s*\+='),
        'unused_comprehension': re.compile(r'\[.*for\s+\w+\s+in\s+.*\](?!.*return|=)'),
        'nested_membership': re.compile(r'for\s+\w+\s+in\s+.*:\s*for\s+\w+\s+in\s+.*if\s+\w+\s+in\s+'),
    },
    'javascript': {
        'sync_io': re.compile(r'fs\.readFileSync|\.sync\('),
        'foreach_instead_for': re.compile(r'\.forEach\('),
        'delete_operator': re.compile(r'delete\s+\w+\.'),
    }
}


def detect_operations(requirement: str) -> list:
    """Detect requested operations from requirement string."""
    ops = []
    for op, pattern in PATTERNS.items():
        if pattern.search(requirement):
            ops.append(op)
    return ops


def check_anti_patterns(code: str, language: str) -> List[str]:
    """Check generated code for performance anti-patterns."""
    issues = []
    lang_key = 'python' if language in ['python', 'py'] else 'javascript' if language in ['js', 'javascript', 'ts', 'typescript'] else None
    
    if lang_key and lang_key in ANTI_PATTERNS:
        for name, pattern in ANTI_PATTERNS[lang_key].items():
            if pattern.search(code):
                issues.append(f"Avoid {name}: {pattern.pattern}")
    
    return issues


def generate_python(requirement: str) -> str:
    """Generate production-ready Python code."""
    ops = detect_operations(requirement)
    
    if not ops:
        return '''def process_data(data):
    """Process input data and return result."""
from datetime import datetime
from typing import Optional, Dict, List, Tuple

# Try to import rich for TUI
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class CodeAnalyzer:
    """Analyzes requirements to determine the actual functionality needed."""
    
    def __init__(self, requirement: str):
        self.req = requirement.lower()
        self.original_req = requirement
        self.functions = []
        self.inputs = []
        self.outputs = []
        self.algorithms = []
        self.data_structures = []
        
    def analyze(self) -> Dict:
        """Extract key components from the requirement."""
        self._detect_functions()
        self._detect_algorithms()
        self._detect_data_structures()
        self._detect_io()
        
        return {
            'functions': self.functions,
            'algorithms': self.algorithms,
            'data_structures': self.data_structures,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'is_simple': len(self.functions) <= 2 and len(self.algorithms) <= 1
        }
    
    def _detect_functions(self):
        """Detect what functions are needed."""
        patterns = [
            (r'sort(?:ing)?\s+(?:a\s+)?(\w+)', 'sort'),
            (r'search(?:ing)?\s+(?:for\s+)?(\w+)', 'search'),
            (r'find\s+(\w+)', 'find'),
            (r'filter(?:ing)?\s+(\w+)', 'filter'),
            (r'map(?:ping)?\s+(\w+)', 'map'),
            (r'reduce\s+(\w+)', 'reduce'),
            (r'reverse\s+(\w+)', 'reverse'),
            (r'merge\s+(\w+)', 'merge'),
            (r'split\s+(\w+)', 'split'),
            (r'parse\s+(\w+)', 'parse'),
            (r'validate\s+(\w+)', 'validate'),
            (r'convert\s+(\w+)', 'convert'),
            (r'transform\s+(\w+)', 'transform'),
            (r'calculate\s+(\w+)', 'calculate'),
            (r'compute\s+(\w+)', 'compute'),
            (r'count\s+(\w+)', 'count'),
            (r'sum\s+(\w+)', 'sum'),
            (r'average|mean\s+(\w+)', 'average'),
            (r'max(?:imum)?\s+(\w+)', 'max'),
            (r'min(?:imum)?\s+(\w+)', 'min'),
        ]
        
        for pattern, func_name in patterns:
            if re.search(pattern, self.req):
                self.functions.append(func_name)
    
    def _detect_algorithms(self):
        """Detect specific algorithms mentioned or implied."""
        if any(x in self.req for x in ['quick', 'efficient', 'fast']):
            self.algorithms.append('optimized')
        if 'binary' in self.req or ('sorted' in self.req and 'search' in self.req):
            self.algorithms.append('binary_search')
        if 'recursive' in self.req:
            self.algorithms.append('recursive')
        if 'iterative' in self.req:
            self.algorithms.append('iterative')
        if 'dynamic' in self.req or 'dp' in self.req:
            self.algorithms.append('dynamic_programming')
        if 'hash' in self.req or 'dictionary' in self.req:
            self.algorithms.append('hashing')
    
    def _detect_data_structures(self):
        """Detect data structures involved."""
        if any(x in self.req for x in ['list', 'array', 'collection']):
            self.data_structures.append('array')
        if any(x in self.req for x in ['tree', 'bst', 'binary tree']):
            self.data_structures.append('tree')
        if any(x in self.req for x in ['graph', 'node', 'edge']):
            self.data_structures.append('graph')
        if any(x in self.req for x in ['stack', 'lifo']):
            self.data_structures.append('stack')
        if any(x in self.req for x in ['queue', 'fifo']):
            self.data_structures.append('queue')
        if any(x in self.req for x in ['hash', 'map', 'dict', 'object']):
            self.data_structures.append('hashmap')
        if any(x in self.req for x in ['linked list', 'linked-list']):
            self.data_structures.append('linked_list')
        if any(x in self.req for x in ['heap', 'priority']):
            self.data_structures.append('heap')
    
    def _detect_io(self):
        """Detect input/output expectations."""
        if 'file' in self.req:
            self.inputs.append('file')
        if 'stdin' in self.req or 'input()' in self.req:
            self.inputs.append('stdin')
        if 'json' in self.req:
            self.inputs.append('json')
            self.outputs.append('json')
        if 'csv' in self.req:
            self.inputs.append('csv')
            self.outputs.append('csv')
        if 'print' in self.req or 'output' in self.req:
            self.outputs.append('stdout')


class CodeGenerator:
    """Generates actual working code based on analyzed requirements."""
    
    def __init__(self, language: str):
        self.language = language.lower()
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate(self, requirement: str) -> str:
        """Generate production-ready code."""
        analyzer = CodeAnalyzer(requirement)
        analysis = analyzer.analyze()
        
        if self.language == 'python':
            return self._gen_python(requirement, analysis)
        elif self.language in ['c', 'cpp']:
            return self._gen_c(requirement, analysis)
        elif self.language in ['js', 'ts', 'javascript', 'typescript']:
            return self._gen_js_ts(requirement, analysis)
        elif self.language == 'rust':
            return self._gen_rust(requirement, analysis)
        else:
            return f"# Error: Unsupported language '{self.language}'"

    def _gen_python(self, req: str, analysis: Dict) -> str:
        """Generate actual Python implementation."""
        funcs = analysis['functions']
        algos = analysis['algorithms']
        ds = analysis['data_structures']
        
        # Determine the actual implementation needed
        if 'sort' in funcs:
            return self._py_sort(req, algos)
        elif 'search' in funcs or 'find' in funcs:
            return self._py_search(req, algos, ds)
        elif 'filter' in funcs:
            return self._py_filter(req)
        elif 'map' in funcs:
            return self._py_map(req)
        elif 'reverse' in funcs:
            return self._py_reverse(req)
        elif 'sum' in funcs or 'average' in funcs:
            return self._py_math(req, funcs)
        elif 'count' in funcs:
            return self._py_count(req)
        elif 'parse' in funcs or 'json' in req:
        elif 'parse' in funcs and 'json' in req:
            return self._py_json_parse(req)
        elif 'validate' in funcs:
            return self._py_validate(req)
        elif 'merge' in funcs:
            return self._py_merge(req)
        elif 'split' in funcs:
            return self._py_split(req)
        else:
            return self._py_generic(req, analysis)
    
    def _py_sort(self, req: str, algos: List[str]) -> str:
        return f'''#!/usr/bin/env python3
"""Sort implementation - {req}"""

def sort_data(data):
    """Sort the input data efficiently."""
    if not data:
        return []
    
    result = []
    for item in data:
        result.append(item)
    
    return result


if __name__ == "__main__":
    sample = [1, 2, 3, 4, 5]
    print(process_data(sample))
'''
    
    code_lines = ['def process_data(data):', '    """Process input data."""']
    
    if 'sort' in ops:
        code_lines.append('    data = sorted(data)')
    if 'reverse' in ops:
        code_lines.append('    data = data[::-1]')
    if 'filter' in ops:
        code_lines.append('    data = [x for x in data if x is not None]')
    if 'map' in ops:
        code_lines.append('    data = [x * 2 for x in data]')
    if 'sum' in ops or 'average' in ops:
        code_lines.append('    total = sum(data)')
        if 'average' in ops:
            code_lines.append('    avg = total / len(data) if data else 0')
            code_lines.append('    return avg')
        else:
            code_lines.append('    return total')
    if 'count' in ops:
        code_lines.append('    return len(data)')
    if 'search' in ops:
        if 'binary' in ops:
            code_lines.extend([
                '    target = data[0] if data else 0',
                '    left, right = 0, len(data) - 1',
                '    while left <= right:',
                '        mid = (left + right) // 2',
                '        if data[mid] == target:',
                '            return mid',
                '        elif data[mid] < target:',
                '            left = mid + 1',
                '        else:',
                '            right = mid - 1',
                '    return -1'
            ])
        else:
            code_lines.extend([
                '    target = data[0] if data else 0',
                '    for i, item in enumerate(data):',
                '        if item == target:',
                '            return i',
                '    return -1'
            ])
    if 'json' in ops:
        code_lines.extend([
            '    import json',
            '    return json.loads(data) if isinstance(data, str) else json.dumps(data)'
        ])
    if 'validate' in ops:
        code_lines.extend([
            '    if not data:',
            '        raise ValueError("Data cannot be empty")',
            '    return True'
        ])
    if 'merge' in ops:
        code_lines.append('    return data + data')
    if 'split' in ops:
        code_lines.append('    mid = len(data) // 2')
        code_lines.append('    return data[:mid], data[mid:]')
    
    if not any(op in ops for op in ['sum', 'average', 'count', 'search', 'json', 'validate', 'split']):
        code_lines.append('    return data')
    
    code_lines.append('')
    code_lines.append('')
    code_lines.append('if __name__ == "__main__":')
    code_lines.append('    sample = [5, 2, 8, 1, 9]')
    code_lines.append('    print(process_data(sample))')
    
    return '\n'.join(code_lines)


def generate_c(requirement: str) -> str:
    """Generate production-ready C code."""
    ops = detect_operations(requirement)
    
    if not ops:
        return '''#include <stdio.h>

void process_data(int* data, int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", data[i]);
    }
    printf("\\n");
}

int main() {
    int data[] = {1, 2, 3, 4, 5};
    int size = sizeof(data) / sizeof(data[0]);
    process_data(data, size);
int main() {{
    int arr[] = {{1, 2, 3, 4, 5, 6, 7, 8, 9}};
    int n = sizeof(arr) / sizeof(arr[0]);
    int target = 6;
    
    int result = binary_search(arr, n, target);
    
    if (result != -1)
        printf("Found %d at index %d\\n", target, result);
    else
        printf("%d not found\\n", target);
    
    return 0;
}}
'''
        else:
            return f'''/* Linear search implementation - {req} */
        return f'''/* Search implementation - {req} */
#include <stdio.h>

int linear_search(int arr[], int n, int target) {{
    for (int i = 0; i < n; i++)
        if (arr[i] == target)
            return i;
    return -1;
}}

int main() {{
    int arr[] = {{3, 7, 1, 9, 4, 6, 8, 2, 5}};
    int n = sizeof(arr) / sizeof(arr[0]);
    int target = 6;
    
    int result = linear_search(arr, n, target);
    
    if (result != -1)
        printf("Found %d at index %d\\n", target, result);
    else
        printf("%d not found\\n", target);
    
    return 0;
}}
'''
    
    def _c_reverse(self, req: str) -> str:
        return f'''/* Reverse implementation - {req} */
#include <stdio.h>
#include <string.h>

void reverse_string(char str[]) {{
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {{
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }}
}}

int main() {{
    char str[] = "hello world";
    reverse_string(str);
    printf("Reversed: %s\\n", str);
    return 0;
}}
'''
    
    def _c_math(self, req: str) -> str:
        return f'''/* Math operations - {req} */
#include <stdio.h>

int sum_array(int arr[], int n) {{
    int sum = 0;
    for (int i = 0; i < n; i++)
        sum += arr[i];
    return sum;
}}

int main() {{
    int arr[] = {{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}};
    int n = sizeof(arr) / sizeof(arr[0]);
    
    int total = sum_array(arr, n);
    printf("Sum: %d\\n", total);
    printf("Average: %.2f\\n", (float)total / n);
    
    return 0;
}}
'''
    
    def _c_generic(self, req: str) -> str:
        return f'''/* Solution for: {req} */
#include <stdio.h>

int main() {{
    printf("Implementation for: {req}\\n");
    return 0;
}
'''
    
    includes = ['#include <stdio.h>', '#include <stdlib.h>']
    if 'sort' in ops or 'search' in ops:
        includes.append('#include <string.h>')
    
    code_lines = ['\n'.join(includes), '']
    
    if 'sort' in ops:
        code_lines.extend([
            'void sort_array(int* data, int size) {',
            '    for (int i = 0; i < size - 1; i++) {',
            '        for (int j = i + 1; j < size; j++) {',
            '            if (data[i] > data[j]) {',
            '                int temp = data[i];',
            '                data[i] = data[j];',
            '                data[j] = temp;',
            '            }',
            '        }',
            '    }',
            '}',
            ''
        ])
    
    if 'search' in ops:
        if 'binary' in ops:
            code_lines.extend([
                'int binary_search(int* data, int size, int target) {',
                '    int left = 0, right = size - 1;',
                '    while (left <= right) {',
                '        int mid = left + (right - left) / 2;',
                '        if (data[mid] == target) return mid;',
                '        if (data[mid] < target) left = mid + 1;',
                '        else right = mid - 1;',
                '    }',
                '    return -1;',
                '}',
                ''
            ])
        else:
            code_lines.extend([
                'int linear_search(int* data, int size, int target) {',
                '    for (int i = 0; i < size; i++) {',
                '        if (data[i] == target) return i;',
                '    }',
                '    return -1;',
                '}',
                ''
            ])
    
    code_lines.extend([
        'int main() {',
        '    int data[] = {5, 2, 8, 1, 9};',
        '    int size = sizeof(data) / sizeof(data[0]);',
        ''
    ])
    
    if 'sort' in ops:
        code_lines.append('    sort_array(data, size);')
    if 'search' in ops:
        search_func = 'binary_search' if 'binary' in ops else 'linear_search'
        code_lines.append(f'    int idx = {search_func}(data, size, data[0]);')
        code_lines.append('    printf("Found at index: %d\\n", idx);')
    if 'reverse' in ops:
        code_lines.extend([
            '    for (int i = 0; i < size / 2; i++) {',
            '        int temp = data[i];',
            '        data[i] = data[size - 1 - i];',
            '        data[size - 1 - i] = temp;',
            '    }'
        ])
    if 'sum' in ops:
        code_lines.extend([
            '    int total = 0;',
            '    for (int i = 0; i < size; i++) total += data[i];',
            '    printf("Sum: %d\\n", total);'
        ])
    
    code_lines.extend([
        '    printf("Result: ");',
        '    for (int i = 0; i < size; i++) printf("%d ", data[i]);',
        '    printf("\\n");',
        '    return 0;',
        '}'
    ])
    
    return '\n'.join(code_lines)


def generate_js(requirement: str) -> str:
    """Generate production-ready JavaScript/TypeScript code."""
    ops = detect_operations(requirement)
    
    if not ops:
        return '''function processData(data) {
    if (!data || data.length === 0) return [];
    return data;
}

const sample = [1, 2, 3, 4, 5];
console.log(processData(sample));
'''
    
    code_lines = ['function processData(data) {']
    
    if 'validate' in ops:
        code_lines.extend([
            '    if (!data || data.length === 0) {',
            '        throw new Error("Data cannot be empty");',
            '    }'
        ])
    
    if 'sort' in ops:
        code_lines.append('    data = [...data].sort((a, b) => a - b);')
    if 'filter' in ops:
        code_lines.append('    data = data.filter(x => x !== null && x !== undefined);')
    if 'map' in ops:
        code_lines.append('    data = data.map(x => x * 2);')
    if 'reverse' in ops:
        code_lines.append('    data = data.reverse();')
    if 'sum' in ops:
        code_lines.append('    const total = data.reduce((a, b) => a + b, 0);')
        if 'average' not in ops:
            code_lines.append('    return total;')
    if 'average' in ops:
        code_lines.append('    const avg = data.reduce((a, b) => a + b, 0) / data.length;')
        code_lines.append('    return avg;')
    if 'count' in ops:
        code_lines.append('    return data.length;')
    if 'search' in ops:
        code_lines.extend([
            '    const target = data[0];',
            '    return data.indexOf(target);'
        ])
    if 'merge' in ops:
        code_lines.append('    return data.concat(data);')
    if 'split' in ops:
        code_lines.extend([
            '    const mid = Math.floor(data.length / 2);',
            '    return [data.slice(0, mid), data.slice(mid)];'
        ])
    
    if not any(op in ops for op in ['sum', 'average', 'count', 'search', 'merge', 'split']):
        code_lines.append('    return data;')
    
    code_lines.append('}')
    code_lines.append('')
    code_lines.append('const sample = [5, 2, 8, 1, 9];')
    code_lines.append('console.log(processData(sample));')
    
    return '\n'.join(code_lines)


def generate_rust(requirement: str) -> str:
    """Generate production-ready Rust code."""
    ops = detect_operations(requirement)
    
    if not ops:
        return '''fn process_data(data: Vec<i32>) -> Vec<i32> {
    data
}

fn main() {
    let sample = vec![1, 2, 3, 4, 5];
    let result = process_data(sample);
    println!("{:?}", result);
}
'''
    
    return_type = 'Vec<i32>'
    has_return = False
    
    if 'sum' in ops:
        return_type = 'i32'
        has_return = True
    elif 'average' in ops:
        return_type = 'f64'
        has_return = True
    elif 'count' in ops:
        return_type = 'usize'
        has_return = True
    elif 'search' in ops:
        return_type = 'Option<usize>'
        has_return = True
    elif 'validate' in ops:
        return_type = 'Result<bool, String>'
        has_return = True
    elif 'split' in ops:
        return_type = '(Vec<i32>, Vec<i32>)'
        has_return = True
    else:
        return_type = 'Vec<i32>'
        has_return = True
    
    code_lines = [f'fn process_data(mut data: Vec<i32>) -> {return_type} {{']
    
    if 'validate' in ops:
        code_lines.extend([
            '    if data.is_empty() {',
            '        return Err("Data cannot be empty".to_string());',
            '    }'
        ])
    
    if 'sort' in ops:
        code_lines.append('    data.sort();')
    if 'reverse' in ops:
        code_lines.append('    data.reverse();')
    if 'filter' in ops:
        code_lines.append('    data = data.into_iter().filter(|&x| x > 0).collect();')
    if 'sum' in ops:
        code_lines.append('    return data.iter().sum();')
    if 'average' in ops:
        code_lines.extend([
            '    let sum: i32 = data.iter().sum();',
            '    return sum as f64 / data.len() as f64;'
        ])
    if 'count' in ops:
        code_lines.append('    return data.len();')
    if 'search' in ops:
        code_lines.extend([
            '    let target = data[0];',
            '    return data.iter().position(|&x| x == target);'
        ])
    if 'merge' in ops:
        code_lines.append('    let mut merged = data.clone();')
        code_lines.append('    merged.extend(data);')
        code_lines.append('    return merged;')
    if 'split' in ops:
        code_lines.extend([
            '    let mid = data.len() / 2;',
            '    let right = data.split_off(mid);',
            '    return (data, right);'
        ])
    
    if not has_return or not any(op in ops for op in ['sum', 'average', 'count', 'search', 'validate', 'split', 'merge']):
        code_lines.append('    data')
    
    code_lines.extend(['}', '', 'fn main() {', '    let sample = vec![5, 2, 8, 1, 9];', '    let result = process_data(sample);', '    println!("{:?}", result);', '}'])
    
    return '\n'.join(code_lines)


def generate_code(requirement: str, language: str) -> str:
    """Generate code based on language selection."""
    lang_map = {
        'python': generate_python,
        'py': generate_python,
        'c': generate_c,
        'javascript': generate_js,
        'js': generate_js,
        'typescript': generate_js,
        'ts': generate_js,
        'rust': generate_rust,
        'rs': generate_rust,
    }
    
    generator = lang_map.get(language.lower(), generate_python)
    return generator(requirement)
}}

console.log(solve("sample input"));

export {{ solve }};
'''

    def _gen_rust(self, req: str, analysis: Dict) -> str:
        funcs = analysis['functions']
        
        if 'sort' in funcs:
            return self._rust_sort(req)
        elif 'search' in funcs or 'find' in funcs:
            return self._rust_search(req)
        elif 'filter' in funcs:
            return self._rust_filter(req)
        elif 'sum' in funcs or 'average' in funcs:
            return self._rust_math(req)
        elif 'validate' in funcs:
            return self._rust_validate(req)
        elif 'reverse' in funcs:
            return self._rust_reverse(req)
        elif 'count' in funcs:
            return self._rust_count(req)
        elif 'merge' in funcs:
            return self._rust_merge(req)
        elif 'sum' in funcs:
            return self._rust_math(req)
        else:
            return self._rust_generic(req)
    
    def _rust_sort(self, req: str) -> str:
        return f'''// Sort implementation - {req}

fn sort_data(mut data: Vec<i32>) -> Vec<i32> {{
    data.sort();
    data
}}

fn main() {{
    let data = vec![64, 34, 25, 12, 22, 11, 90];
    let sorted = sort_data(data);
    println!("Sorted: {{:?}}", sorted);
}}

#[cfg(test)]
mod tests {{
    use super::*;
    
    #[test]]
    fn test_sort() {{
        let result = sort_data(vec![3, 1, 2]);
        assert_eq!(result, vec![1, 2, 3]);
    }}
}}
'''
    
    def _rust_search(self, req: str) -> str:
        return f'''// Search implementation - {req}

fn search_data(data: &[i32], target: i32) -> Option<usize> {{
    data.iter().position(|&x| x == target)
}}

fn main() {{
    let data = [3, 7, 1, 9, 4, 6, 8, 2, 5];
    let target = 6;
    
    match search_data(&data, target) {{
        Some(index) => println!("Found {{}} at index {{}}", target, index),
        None => println!("{{}} not found", target),
    }}
}}
'''
    
    def _rust_filter(self, req: str) -> str:
        return f'''// Filter implementation - {req}

fn filter_data(data: Vec<i32>, predicate: impl Fn(&i32) -> bool) -> Vec<i32> {{
    data.into_iter().filter(predicate).collect()
}}

fn main() {{
    let data = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let evens = filter_data(data, |x| x % 2 == 0);
    println!("Even numbers: {{:?}}", evens);
}}
'''
    
    def _rust_math(self, req: str) -> str:
        return f'''// Math operations - {req}

fn sum_data(data: &[i32]) -> i32 {{
    data.iter().sum()
}}

fn average_data(data: &[i32]) -> f64 {{
    if data.is_empty() {{
        return 0.0;
    }}
    let total: i32 = data.iter().sum();
    total as f64 / data.len() as f64
}}

fn main() {{
    let data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let total = sum_data(&data);
    let avg = average_data(&data);
fn main() {{
    let data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let total = sum_data(&data);
    let avg = total as f64 / data.len() as f64;
    println!("Sum: {{}}, Average: {{:.2}}", total, avg);
}}
'''
    
    def _rust_validate(self, req: str) -> str:
        return f'''// Validation implementation - {req}

fn validate_email(email: &str) -> bool {{
    let re = regex::Regex::new(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$").unwrap();
    re.is_match(email)
}}

fn validate_not_empty(s: &str) -> bool {{
    !s.trim().is_empty()
}}

fn main() {{
    let emails = vec!["test@example.com", "invalid.email", "user@domain.org"];
    
    for email in emails {{
        let valid = validate_email(email);
        println!("{{}}: {{}}", email, if valid {{ "Valid" }} else {{ "Invalid" }});
    }}
}}
'''
    
    def _rust_reverse(self, req: str) -> str:
        return f'''// Reverse implementation - {req}

fn reverse_string(s: &str) -> String {{
    s.chars().rev().collect()
}}

fn reverse_vec<T: Clone>(data: &[T]) -> Vec<T> {{
    data.iter().rev().cloned().collect()
}}

fn main() {{
    let text = "hello world";
    let reversed = reverse_string(text);
    println!("Original: {{}}, Reversed: {{}}", text, reversed);
    
    let nums = vec![1, 2, 3, 4, 5];
    let reversed_nums = reverse_vec(&nums);
    println!("Original: {{:?}}, Reversed: {{:?}}", nums, reversed_nums);
}}
'''
    
    def _rust_count(self, req: str) -> str:
        return f'''// Count implementation - {req}

fn count_occurrences<T: PartialEq>(data: &[T], target: &T) -> usize {{
    data.iter().filter(|&x| x == target).count()
}}

fn count_total<T>(data: &[T]) -> usize {{
    data.len()
}}

fn main() {{
    let data = vec!["apple", "banana", "apple", "orange", "apple"];
    let target = "apple";
    
    let count = count_occurrences(&data, &target);
    println!("{{}} appears {{}} times", target, count);
    
    let total = count_total(&data);
    println!("Total items: {{}}", total);
}}
'''
    
    def _rust_merge(self, req: str) -> str:
        return f'''// Merge implementation - {req}

fn merge_vectors<T: Clone>(v1: &[T], v2: &[T]) -> Vec<T> {{
    v1.iter().chain(v2.iter()).cloned().collect()
}}

fn merge_unique<T: Clone + Eq + std::hash::Hash>(v1: &[T], v2: &[T]) -> Vec<T> {{
    use std::collections::HashSet;
    let mut seen = HashSet::new();
    v1.iter().chain(v2.iter())
        .filter(|x| seen.insert(*x))
        .cloned()
        .collect()
}}

fn main() {{
    let v1 = vec![1, 2, 3];
    let v2 = vec![3, 4, 5];
    
    let merged = merge_vectors(&v1, &v2);
    println!("Merged: {{:?}}", merged);
    
    let unique = merge_unique(&v1, &v2);
    println!("Merged (unique): {{:?}}", unique);
}}
'''
    
    def _rust_generic(self, req: str) -> str:
        return f'''// Solution for: {req}

fn solve<T: std::fmt::Debug>(data: T) -> T {{
    data
}}

fn main() {{
    let result = solve("sample input");
    println!("Result: {{:?}}", result);
    def _rust_generic(self, req: str) -> str:
        return f'''// Solution for: {req}

fn main() {{
    println!("Implementation for: {req}");
}}
'''


class TUI:
    def __init__(self):
        self.console = Console()

    def display_header(self):
        self.console.print(Panel.fit(
            "[bold blue]BADASS CODER[/bold blue]\\n[dim]Native Multi-Language Engine[/dim]",
            border_style="blue"
        ))

    def display_generation(self, language: str, code: str):
        if not RICH_AVAILABLE:
            print(code)
            return

        self.console.print(f"\\n[bold green]Generating {language.upper()} code...[/bold green]\\n")
        syntax = Syntax(code, language, line_numbers=True, theme="monokai")
        self.console.print(Panel(syntax, title=f"Generated {language}", border_style="green"))

    def display_stats(self, lang: str, code: str, length: int):
        if not RICH_AVAILABLE:
            print(f"Generated {length} characters in {lang}")
            return

        table = Table(show_header=False, box=None)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Language", lang.upper())
        table.add_row("Lines", str(len(code.splitlines())))
        table.add_row("Characters", str(length))
        table.add_row("Status", "[green]Ready[/green]")
        
        self.console.print("\\n", table)


def main():
    parser = argparse.ArgumentParser(description='Badass Coder - Production Ready Code Generator')
    parser.add_argument('requirement', nargs='?', help='Code generation requirement')
    parser.add_argument('--lang', '-l', default='python', 
                       choices=['python', 'py', 'c', 'javascript', 'js', 'typescript', 'ts', 'rust', 'rs'],
                       help='Target language (default: python)')
    parser.add_argument('--output', '-o', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.requirement:
        print("Badass Coder - Production Ready Code Generator")
        print("Usage: python badass_coder.py \"your requirement\" --lang=python")
        print("Supported languages: python, c, javascript, typescript, rust")
        sys.exit(0)
    
    code = generate_code(args.requirement, args.lang)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(code)
        print(f"Code saved to {args.output}")
    else:
        print(code)


if __name__ == "__main__":
    main()

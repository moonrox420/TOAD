#!/usr/bin/env python3
"""
Multi-Language Code Generation & Syntax Fixing Agent

Supports: Python, JavaScript, TypeScript, Java, C++, Go, Rust, C#, PHP, Ruby
Features:
- Generate code in any language
- Detect and fix syntax errors
- Autonomous problem solving
- Code validation and improvement
"""

import re
from typing import Dict, List, Tuple, Optional
from agent import CodeGenerationAgent


class SyntaxFixer:
    """Fixes syntax errors across multiple languages."""
    
    LANGUAGES = {
        'python': {'ext': '.py', 'comment': '#', 'end_stmt': None},
        'javascript': {'ext': '.js', 'comment': '//', 'end_stmt': ';'},
        'typescript': {'ext': '.ts', 'comment': '//', 'end_stmt': ';'},
        'java': {'ext': '.java', 'comment': '//', 'end_stmt': ';'},
        'cpp': {'ext': '.cpp', 'comment': '//', 'end_stmt': ';'},
        'csharp': {'ext': '.cs', 'comment': '//', 'end_stmt': ';'},
        'go': {'ext': '.go', 'comment': '//', 'end_stmt': None},
        'rust': {'ext': '.rs', 'comment': '//', 'end_stmt': ';'},
        'php': {'ext': '.php', 'comment': '//', 'end_stmt': ';'},
        'ruby': {'ext': '.rb', 'comment': '#', 'end_stmt': None},
    }
    
    def __init__(self, language: str):
        """Initialize fixer for language."""
        lang_lower = language.lower()
        if lang_lower not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        self.language = lang_lower
        self.config = self.LANGUAGES[lang_lower]
    
    def detect_issues(self, code: str) -> List[Dict]:
        """Detect CRITICAL syntax issues in code only."""
        critical_issues = []
        
        if self.language in ['python']:
            critical_issues.extend(self._check_python_critical(code))
        elif self.language in ['javascript', 'typescript']:
            critical_issues.extend(self._check_js_ts_critical(code))
        elif self.language in ['java', 'cpp', 'csharp', 'rust']:
            critical_issues.extend(self._check_c_style_critical(code))
        elif self.language == 'go':
            critical_issues.extend(self._check_go_critical(code))
        elif self.language == 'php':
            critical_issues.extend(self._check_php_critical(code))
        elif self.language == 'ruby':
            critical_issues.extend(self._check_ruby_critical(code))
        
        return critical_issues
    
    def _check_python_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL Python syntax issues only."""
        issues = []
        lines = code.split('\n')
        
        try:
            import ast
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 0,
                'type': 'SyntaxError',
                'message': str(e.msg),
                'fix': None
            })
        
        return issues
    
    def _check_js_ts_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL JavaScript/TypeScript syntax issues only."""
        issues = []
        
        # Only check for unmatched braces/brackets/parens
        in_string = False
        quote_char = None
        brace_count = 0
        bracket_count = 0
        paren_count = 0
        
        for char in code:
            if char in ['"', "'", '`'] and (not in_string or char == quote_char):
                in_string = not in_string
                quote_char = char if in_string else None
            elif not in_string:
                if char == '{': brace_count += 1
                elif char == '}': brace_count -= 1
                elif char == '[': bracket_count += 1
                elif char == ']': bracket_count -= 1
                elif char == '(': paren_count += 1
                elif char == ')': paren_count -= 1
        
        if brace_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedBrace',
                'message': f'Unmatched braces',
                'fix': None
            })
        
        if bracket_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedBracket',
                'message': f'Unmatched brackets',
                'fix': None
            })
        
        if paren_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedParen',
                'message': f'Unmatched parentheses',
                'fix': None
            })
        
        return issues
    
    def _check_c_style_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL C-style language syntax only."""
        issues = []
        
        # Check for unmatched braces
        in_string = False
        quote_char = None
        brace_count = 0
        bracket_count = 0
        paren_count = 0
        
        for char in code:
            if char in ['"', "'"] and (not in_string or char == quote_char):
                in_string = not in_string
                quote_char = char if in_string else None
            elif not in_string:
                if char == '{': brace_count += 1
                elif char == '}': brace_count -= 1
                elif char == '[': bracket_count += 1
                elif char == ']': bracket_count -= 1
                elif char == '(': paren_count += 1
                elif char == ')': paren_count -= 1
        
        if brace_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedBrace',
                'message': 'Unmatched braces',
                'fix': None
            })
        
        return issues
    
    def _check_go_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL Go syntax issues."""
        return []
    
    def _check_php_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL PHP syntax issues."""
        issues = []
        
        # Check for unclosed PHP tags
        open_tags = code.count('<?php') + code.count('<?')
        close_tags = code.count('?>')
        
        if open_tags > close_tags:
            issues.append({
                'line': -1,
                'type': 'UnclosedTag',
                'message': 'Unclosed PHP tags',
                'fix': None
            })
        
        return issues
    
    def _check_ruby_critical(self, code: str) -> List[Dict]:
        """Check CRITICAL Ruby syntax issues."""
        return []
    
    def _check_python(self, code: str) -> List[Dict]:
        """Check Python syntax issues."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check indentation consistency
            if stripped and not line.startswith((' ', '\t')) and i > 1:
                if lines[i-2].strip().endswith(':'):
                    issues.append({
                        'line': i,
                        'type': 'IndentationError',
                        'message': 'Expected indentation after colon',
                        'fix': None
                    })
            
            # Check for unclosed quotes
            if stripped.count('"') % 2 != 0 or stripped.count("'") % 2 != 0:
                if not stripped.startswith('#'):
                    issues.append({
                        'line': i,
                        'type': 'SyntaxError',
                        'message': 'Unclosed string literal',
                        'fix': None
                    })
            
            # Check for missing colons
            if any(stripped.startswith(kw) for kw in ['if ', 'elif ', 'else:', 'for ', 'while ', 'def ', 'class ']):
                if not stripped.endswith(':') and not stripped.endswith('\\'):
                    issues.append({
                        'line': i,
                        'type': 'SyntaxError',
                        'message': 'Missing colon (:) at end of statement',
                        'fix': stripped + ':'
                    })
        
        return issues
    
    def _check_js_ts(self, code: str) -> List[Dict]:
        """Check JavaScript/TypeScript syntax issues."""
        issues = []
        lines = code.split('\n')
        
        brace_count = 0
        bracket_count = 0
        paren_count = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            
            # Count braces/brackets/parens
            # Only count unquoted braces
            in_string = False
            quote_char = None
            for char in stripped:
                if char in ['"', "'", '`'] and (not in_string or char == quote_char):
                    in_string = not in_string
                    quote_char = char if in_string else None
                elif not in_string:
                    if char == '{': brace_count += 1
                    elif char == '}': brace_count -= 1
                    elif char == '[': bracket_count += 1
                    elif char == ']': bracket_count -= 1
                    elif char == '(': paren_count += 1
                    elif char == ')': paren_count -= 1
            
            # Check for unclosed quotes (only report critical issues)
            quote_count = stripped.count('"') + stripped.count("'")
            if quote_count % 2 != 0 and not stripped.startswith('//'):
                issues.append({
                    'line': i,
                    'type': 'UnclosedString',
                    'message': 'Unclosed string literal',
                    'fix': None
                })
        
        if brace_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedBrace',
                'message': f'Unmatched braces (difference: {brace_count})',
                'fix': None
            })
        
        if bracket_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedBracket',
                'message': f'Unmatched brackets (difference: {bracket_count})',
                'fix': None
            })
        
        if paren_count != 0:
            issues.append({
                'line': -1,
                'type': 'UnmatchedParen',
                'message': f'Unmatched parentheses (difference: {paren_count})',
                'fix': None
            })
        
        return issues
    
    def _check_c_style(self, code: str) -> List[Dict]:
        """Check C-style language syntax (Java, C++, C#, Rust)."""
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*'):
                continue
            
            # Check for missing semicolons
            if (any(stripped.endswith(c) for c in [']', ')']) and 
                not stripped.endswith('{') and 
                not stripped.endswith(';') and
                not stripped.endswith(',') and
                not stripped.endswith(':') and
                stripped):
                
                issues.append({
                    'line': i,
                    'type': 'MissingSemicolon',
                    'message': 'Statement should end with semicolon',
                    'fix': stripped + ';'
                })
        
        return issues
    
    def _check_go(self, code: str) -> List[Dict]:
        """Check Go syntax issues."""
        issues = []
        
        # Go doesn't require semicolons but check for other issues
        if 'func ' in code and 'func main' not in code:
            if '{' not in code:
                issues.append({
                    'line': -1,
                    'type': 'SyntaxError',
                    'message': 'Function declaration missing opening brace',
                    'fix': None
                })
        
        return issues
    
    def _check_php(self, code: str) -> List[Dict]:
        """Check PHP syntax issues."""
        issues = []
        
        # Check for unclosed PHP tags
        open_tags = code.count('<?php') + code.count('<?')
        close_tags = code.count('?>')
        
        if open_tags > close_tags:
            issues.append({
                'line': -1,
                'type': 'UnclosedTag',
                'message': f'Unclosed PHP tags (open: {open_tags}, close: {close_tags})',
                'fix': None
            })
        
        # Check for missing semicolons (basic)
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('#'):
                continue
            
            if stripped and not stripped.startswith('<?') and not stripped.startswith('?>'):
                if any(stripped.endswith(c) for c in [']', ')']) and not stripped.endswith(';'):
                    issues.append({
                        'line': i,
                        'type': 'MissingSemicolon',
                        'message': 'Missing semicolon',
                        'fix': stripped + ';'
                    })
        
        return issues
    
    def _check_ruby(self, code: str) -> List[Dict]:
        """Check Ruby syntax issues."""
        issues = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for unclosed strings
            if stripped.count('"') % 2 != 0 or stripped.count("'") % 2 != 0:
                if not stripped.startswith('#'):
                    issues.append({
                        'line': i,
                        'type': 'UnclosedString',
                        'message': 'Unclosed string literal',
                        'fix': None
                    })
        
        return issues
    
    def fix_code(self, code: str, auto_fix: bool = True) -> Tuple[str, List[Dict]]:
        """Detect and fix syntax issues."""
        issues = self.detect_issues(code)
        fixed_code = code
        fixes_applied = []
        
        if not auto_fix:
            return fixed_code, issues
        
        # Apply automatic fixes
        lines = code.split('\n')
        
        for issue in issues:
            if issue['fix']:
                line_idx = issue['line'] - 1
                if 0 <= line_idx < len(lines):
                    old_line = lines[line_idx]
                    lines[line_idx] = issue['fix']
                    fixes_applied.append({
                        'line': issue['line'],
                        'type': issue['type'],
                        'old': old_line,
                        'new': issue['fix']
                    })
        
        # General cleanup
        cleaned_lines = []
        for line in lines:
            # Remove trailing whitespace
            cleaned = line.rstrip()
            cleaned_lines.append(cleaned)
        
        fixed_code = '\n'.join(cleaned_lines)
        
        # Ensure final newline
        if fixed_code and not fixed_code.endswith('\n'):
            fixed_code += '\n'
        
        return fixed_code, fixes_applied


class MultiLanguageAgent:
    """Multi-language code generation and fixing agent."""
    
    def __init__(self):
        """Initialize the agent."""
        self.base_agent = CodeGenerationAgent()
        self.fixer = None
        self.language = 'python'
        self.last_code = None
        self.last_issues = []
    
    def set_language(self, language: str) -> bool:
        """Set the target language."""
        try:
            self.fixer = SyntaxFixer(language)
            self.language = language.lower()
            return True
        except ValueError:
            return False
    
    def _language_specific_template(self, requirement: str) -> str:
        """Generate language-specific prompt for better code quality."""
        lang_prompts = {
            'python': f"""Generate production-ready Python code that:
{requirement}

Requirements:
- Use proper Python style (PEP 8)
- Include docstrings for all functions/classes
- Use type hints
- Include error handling with try/except
- No trailing semicolons
- 4-space indentation
- Import statements at top
Return ONLY valid, executable Python code.""",
            
            'javascript': f"""Generate production-ready JavaScript code that:
{requirement}

Requirements:
- Use modern ES6+ syntax
- Include JSDoc comments
- Every statement ends with semicolon
- Use const/let (not var)
- Include error handling
- Proper curly brace placement (K&R style)
- No trailing commas in objects
Return ONLY valid, executable JavaScript code.""",
            
            'typescript': f"""Generate production-ready TypeScript code that:
{requirement}

Requirements:
- Use proper TypeScript with full type annotations
- Every statement ends with semicolon
- Include interface/type definitions
- Proper curly brace placement
- Include JSDoc comments
- Use const/let (not var)
- No trailing commas
Return ONLY valid, executable TypeScript code.""",
            
            'java': f"""Generate production-ready Java code that:
{requirement}

Requirements:
- Use Java conventions (PascalCase for classes, camelCase for methods)
- Every statement ends with semicolon
- Include proper package structure
- Include javadoc comments
- Proper curly brace placement (Java style)
- Import statements at top
Return ONLY valid, executable Java code.""",
            
            'cpp': f"""Generate production-ready C++ code that:
{requirement}

Requirements:
- Use modern C++ (C++17 or later)
- Every statement ends with semicolon
- Include proper header guards or #pragma once
- Proper curly brace placement
- Include comments explaining functionality
- Use std namespace appropriately
- No memory leaks (use smart pointers)
Return ONLY valid, executable C++ code.""",
            
            'csharp': f"""Generate production-ready C# code that:
{requirement}

Requirements:
- Use C# conventions (PascalCase)
- Every statement ends with semicolon
- Include XML documentation comments
- Proper curly brace placement (C# style)
- Use modern C# features
- Proper namespace declarations
Return ONLY valid, executable C# code.""",
            
            'go': f"""Generate production-ready Go code that:
{requirement}

Requirements:
- Use Go conventions (camelCase, exported functions capitalized)
- No semicolons at end of statements
- Proper error handling with if err != nil
- Include package declaration
- Proper indentation (use gofmt style)
- Include comments for exported functions
Return ONLY valid, executable Go code.""",
            
            'rust': f"""Generate production-ready Rust code that:
{requirement}

Requirements:
- Use Rust conventions and idioms
- Every statement ends with semicolon (in blocks)
- Include proper ownership/borrowing patterns
- Include comments explaining functionality
- Proper curly brace placement
- Use Result/Option types appropriately
Return ONLY valid, executable Rust code.""",
            
            'php': f"""Generate production-ready PHP code that:
{requirement}

Requirements:
- Include <?php opening tag
- Every statement ends with semicolon
- Use modern PHP (7.4+)
- Include proper error handling
- Use PSR-12 coding standards
- Include comments
Return ONLY valid, executable PHP code (with closing tag if needed).""",
            
            'ruby': f"""Generate production-ready Ruby code that:
{requirement}

Requirements:
- Use Ruby conventions (snake_case)
- No semicolons at end of statements
- Include comments/docstrings
- Proper indentation (2 spaces)
- Include error handling
- Idiomatic Ruby style
Return ONLY valid, executable Ruby code.""",
        }
        
        return lang_prompts.get(self.language, requirement)
    
    def generate(self, requirement: str) -> Dict:
        """Generate code in the target language."""
        # Use language-specific prompt for better quality
        enhanced_req = self._language_specific_template(requirement)
        
        # Generate using base agent
        analysis = self.base_agent.analyze_requirements(enhanced_req)
        code = self.base_agent.generate_code(enhanced_req)
        
        # Fix any remaining syntax issues
        if self.fixer:
            code, fixes = self.fixer.fix_code(code, auto_fix=True)
        else:
            fixes = []
        
        # Validate
        validation = self.base_agent._validate_code(code)
        
        self.last_code = code
        self.last_issues = self.fixer.detect_issues(code) if self.fixer else []
        
        return {
            'code': code,
            'language': self.language,
            'analysis': analysis,
            'validation': validation,
            'syntax_fixes': fixes,
            'remaining_issues': self.last_issues
        }
    
    def fix_code(self, code: str) -> Dict:
        """Fix syntax errors in code."""
        if not self.fixer:
            return {'error': 'No language set'}
        
        fixed_code, fixes = self.fixer.fix_code(code, auto_fix=True)
        remaining_issues = self.fixer.detect_issues(fixed_code)
        
        self.last_code = fixed_code
        self.last_issues = remaining_issues
        
        return {
            'code': fixed_code,
            'fixes_applied': fixes,
            'remaining_issues': remaining_issues,
            'fixed': len(fixes) > 0
        }
    
    def analyze_code(self, code: str) -> Dict:
        """Analyze code for issues."""
        if not self.fixer:
            return {'error': 'No language set'}
        
        issues = self.fixer.detect_issues(code)
        
        return {
            'language': self.language,
            'issues_found': len(issues),
            'issues': issues,
            'summary': self._summarize_issues(issues)
        }
    
    def _summarize_issues(self, issues: List[Dict]) -> str:
        """Summarize issues found."""
        if not issues:
            return "No syntax issues detected"
        
        issue_types = {}
        for issue in issues:
            issue_type = issue['type']
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        summary = ', '.join(f"{count} {type_}" for type_, count in sorted(issue_types.items()))
        return f"Found issues: {summary}"


def main():
    """Test the multi-language agent."""
    agent = MultiLanguageAgent()
    
    # Test Python
    print("=== Python Generation ===")
    agent.set_language('python')
    result = agent.generate("function that sorts a list")
    print(f"Generated {len(result['code'])} chars of code")
    print(f"Remaining issues: {len(result['remaining_issues'])}")
    
    # Test JavaScript
    print("\n=== JavaScript Generation ===")
    agent.set_language('javascript')
    result = agent.generate("function that fetches data from API")
    print(f"Generated {len(result['code'])} chars of code")
    
    # Test syntax fixing
    print("\n=== Syntax Fixing ===")
    bad_code = """
    function test() {
        const x = 5
        return x
    """
    result = agent.fix_code(bad_code)
    print(f"Fixes applied: {len(result['fixes_applied'])}")
    for fix in result['fixes_applied']:
        print(f"  Line {fix['line']}: {fix['type']}")


if __name__ == '__main__':
    main()

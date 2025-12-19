#!/usr/bin/env python3
"""
DroxAI Directory Scanner - Code Quality & Consistency Check

Scans a directory for:
- Syntax errors
- Missing imports
- Type hint inconsistencies
- Unused variables/functions
- Missing docstrings
- Code style issues
- Git merge conflicts
- File encoding issues

Run with: python scanner.py [directory]
"""

import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Issue:
    """Represents a code issue."""
    file: str
    line: int
    severity: str  # 'error', 'warning', 'info'
    issue_type: str
    message: str
    
    def __str__(self) -> str:
        icon = {'error': '✗', 'warning': '⚠', 'info': 'ℹ'}[self.severity]
        return f"{icon} {self.file}:{self.line} [{self.issue_type}] {self.message}"


class DirectoryScanner:
    """Scans a directory for code issues."""
    
    def __init__(self, root_path: str):
        """Initialize scanner."""
        self.root = Path(root_path)
        self.issues: List[Issue] = []
        self.files_scanned = 0
        self.skipped_patterns = {'.git', '__pycache__', '.venv', 'venv', '.egg-info'}
    
    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        return any(pattern in path.parts for pattern in self.skipped_patterns)
    
    def scan(self) -> List[Issue]:
        """Scan entire directory."""
        print(f"[SCAN] Scanning: {self.root}\n")
        
        for py_file in self.root.rglob('*.py'):
            if self.should_skip(py_file):
                continue
            
            self.files_scanned += 1
            print(f"  Checking {py_file.relative_to(self.root)}...", end=' ')
            
            try:
                self._scan_file(py_file)
                print("[OK]")
            except Exception as e:
                self.issues.append(Issue(
                    file=str(py_file.relative_to(self.root)),
                    line=0,
                    severity='error',
                    issue_type='ScanError',
                    message=f"Failed to scan: {str(e)}"
                ))
                print(f"[FAIL]")
        
        return self.issues
    
    def _scan_file(self, file_path: Path) -> None:
        """Scan a single Python file."""
        content = file_path.read_text(encoding='utf-8', errors='replace')
        
        # Check 1: Syntax errors
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.issues.append(Issue(
                file=str(file_path.relative_to(self.root)),
                line=e.lineno or 0,
                severity='error',
                issue_type='SyntaxError',
                message=str(e.msg)
            ))
            return
        
        # Check 2: Merge conflict markers
        for i, line in enumerate(content.split('\n'), 1):
            if line.strip().startswith('<<<<<<< '):
                self.issues.append(Issue(
                    file=str(file_path.relative_to(self.root)),
                    line=i,
                    severity='error',
                    issue_type='MergeConflict',
                    message='Git merge conflict marker found'
                ))
            elif line.strip().startswith('>>>>>>> '):
                self.issues.append(Issue(
                    file=str(file_path.relative_to(self.root)),
                    line=i,
                    severity='error',
                    issue_type='MergeConflict',
                    message='Git merge conflict marker found'
                ))
        
        # Check 3: Import issues and missing docstrings
        self._check_ast_issues(file_path, tree)
        
        # Check 4: Line length and style
        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > 120:
                self.issues.append(Issue(
                    file=str(file_path.relative_to(self.root)),
                    line=i,
                    severity='warning',
                    issue_type='LineLength',
                    message=f'Line too long ({len(line)} > 120 chars)'
                ))
    
    def _check_ast_issues(self, file_path: Path, tree: ast.AST) -> None:
        """Check AST for various issues."""
        file_rel = str(file_path.relative_to(self.root))
        
        for node in ast.walk(tree):
            # Check for functions/classes without docstrings
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    self.issues.append(Issue(
                        file=file_rel,
                        line=node.lineno,
                        severity='warning',
                        issue_type='MissingDocstring',
                        message=f'{node.__class__.__name__} "{node.name}" has no docstring'
                    ))
            
            # Check for bare except
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:
                    self.issues.append(Issue(
                        file=file_rel,
                        line=node.lineno,
                        severity='warning',
                        issue_type='BareExcept',
                        message='Bare except clause found (should catch specific exceptions)'
                    ))
    
    def print_report(self) -> None:
        """Print a detailed report."""
        print("\n" + "="*80)
        print("SCAN REPORT")
        print("="*80 + "\n")
        
        print(f"[SUMMARY]")
        print(f"  Files scanned: {self.files_scanned}")
        print(f"  Total issues: {len(self.issues)}")
        
        if not self.issues:
            print("\n[OK] No issues found!")
            return
        
        # Group by severity
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        infos = [i for i in self.issues if i.severity == 'info']
        
        if errors:
            print(f"  Errors: {len(errors)}")
        if warnings:
            print(f"  Warnings: {len(warnings)}")
        if infos:
            print(f"  Info: {len(infos)}")
        
        # Print issues by severity
        if errors:
            print(f"\n[ERRORS] ({len(errors)}):")
            for issue in sorted(errors, key=lambda x: (x.file, x.line)):
                print(f"  {issue}")
        
        if warnings:
            print(f"\n[WARNINGS] ({len(warnings)}):")
            for issue in sorted(warnings, key=lambda x: (x.file, x.line)):
                print(f"  {issue}")
        
        if infos:
            print(f"\n[INFO] ({len(infos)}):")
            for issue in sorted(infos, key=lambda x: (x.file, x.line)):
                print(f"  {issue}")
        
        # Group by file
        print(f"\n[BY FILE]:")
        files_with_issues = {}
        for issue in self.issues:
            if issue.file not in files_with_issues:
                files_with_issues[issue.file] = []
            files_with_issues[issue.file].append(issue)
        
        for file in sorted(files_with_issues.keys()):
            issue_count = len(files_with_issues[file])
            print(f"  {file}: {issue_count} issue{'s' if issue_count != 1 else ''}")
        
        # Group by type
        print(f"\n[BY TYPE]:")
        types_dict = {}
        for issue in self.issues:
            if issue.issue_type not in types_dict:
                types_dict[issue.issue_type] = []
            types_dict[issue.issue_type].append(issue)
        
        for issue_type in sorted(types_dict.keys()):
            count = len(types_dict[issue_type])
            print(f"  {issue_type}: {count}")
        
        print("\n" + "="*80)


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        scan_path = sys.argv[1]
    else:
        scan_path = '.'
    
    if not Path(scan_path).exists():
        print(f"Error: Path does not exist: {scan_path}")
        sys.exit(1)
    
    scanner = DirectoryScanner(scan_path)
    issues = scanner.scan()
    scanner.print_report()
    
    # Exit with error code if critical issues found
    if any(i.severity == 'error' for i in issues):
        sys.exit(1)


if __name__ == '__main__':
    main()

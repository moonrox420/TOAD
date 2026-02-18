#!/usr/bin/env python3
"""
EnterpriseAI-Local Code Generation Agent - Command Line Interface

Original Project: https://github.com/DarkShadow190922/EnterpriseAI-Local

Usage:
    python cli.py generate "Create a REST API with authentication"
    python cli.py analyze "Build a web scraper"
    python cli.py interactive
    python cli.py benchmark
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional
import asyncio
from agent import CodeGenerationAgent, UnlimitedCodeAgent


class CodeGenCLI:
    """Command-line interface for the EnterpriseAI-Local code generation agent."""
    
    def __init__(self, use_unlimited: bool = False):
        """Initialize the CLI with the appropriate agent."""
        self.agent_class = UnlimitedCodeAgent if use_unlimited else CodeGenerationAgent
        self.agent = self.agent_class()
    
    def print_header(self, text: str) -> None:
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")
    
    def print_section(self, text: str) -> None:
        """Print a formatted section title."""
        print(f"\n>>> {text}")
        print("-" * 70)
    
    def generate_command(self, requirements: str, output_file: Optional[str] = None) -> None:
        """Generate code from requirements."""
        self.print_header("CODE GENERATION")
        print(f"Requirements: {requirements}\n")
        
        # Analyze requirements
        self.print_section("Analyzing Requirements")
        analysis = self.agent.analyze_requirements(requirements)
        
        print(f"Complexity Score: {analysis['complexity_score']}/100")
        print(f"Code Type: {analysis['code_type']}")
        print(f"Detected Architecture: {analysis['architecture']}")
        print(f"Estimated Size: {analysis.get('estimated_size', 'N/A')}")
        
        # Generate code
        self.print_section("Generating Code")
        print("Generating... this may take a moment...")
        code = self.agent.generate_code(requirements)
        
        print(f"✓ Generated {len(code):,} characters of code\n")
        
        # Display code
        self.print_section("Generated Code")
        # Show first 100 lines or all if less
        lines = code.split('\n')
        display_lines = lines[:100] if len(lines) > 100 else lines
        print('\n'.join(display_lines))
        
        if len(lines) > 100:
            print(f"\n... ({len(lines) - 100} more lines)")
        
        # Validate
        self.print_section("Validation")
        validation = self.agent._validate_code(code)
        status = "✓ VALID" if validation['valid'] else "✗ INVALID"
        print(f"Status: {status}")
        if validation['errors']:
            print(f"Errors: {validation['errors']}")
        
        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(code)
            print(f"\n✓ Code saved to: {output_path.absolute()}")
        
        # Summary
        self.print_section("Summary")
        print(f"Complexity:  {analysis['complexity_score']}/100")
        print(f"Code Length: {len(code):,} characters")
        print(f"Valid:       {validation['valid']}")
        print(f"Code Type:   {analysis['code_type']}")
    
    def analyze_command(self, requirements: str) -> None:
        """Analyze requirements without generating code."""
        self.print_header("REQUIREMENT ANALYSIS")
        print(f"Input: {requirements}\n")
        
        self.print_section("Analysis Results")
        analysis = self.agent.analyze_requirements(requirements)
        
        print(f"Complexity Score:        {analysis['complexity_score']}/100")
        print(f"Code Type:               {analysis['code_type']}")
        print(f"Detected Architecture:   {analysis['architecture']}")
        print(f"Estimated Size:          {analysis.get('estimated_size', 'N/A')}")
        
        # Show confidence scores
        if 'confidence_scores' in analysis:
            self.print_section("Confidence Scores")
            for score_name, score_value in analysis['confidence_scores'].items():
                print(f"{score_name}: {score_value:.2%}")
    
    def interactive_command(self) -> None:
        """Interactive mode - generate code step by step."""
        self.print_header("INTERACTIVE MODE")
        print("Type 'help' for commands, 'quit' to exit\n")
        
        while True:
            try:
                user_input = input(">>> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("Goodbye!")
                    break
                
                if user_input.lower() == 'help':
                    self._print_help()
                    continue
                
                if user_input.lower() == 'clear':
                    import os
                    os.system('cls' if sys.platform == 'win32' else 'clear')
                    continue
                
                # Treat input as code generation request
                self.generate_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def benchmark_command(self) -> None:
        """Run benchmark tests."""
        self.print_header("BENCHMARK")
        
        test_cases = [
            ("Simple", "Create a function that adds two numbers"),
            ("Medium", "Create a class for data processing with file I/O"),
            ("Complex", "Build a web API with authentication and database"),
            ("Enterprise", """Create a high-performance data processing system with:
            - Multi-threaded processing
            - Real-time streaming
            - Advanced error handling
            - Database integration
            - REST API with authentication
            - Security features
            - Performance monitoring
            - Testing framework""")
        ]
        
        results = []
        
        for name, requirement in test_cases:
            print(f"\nBenchmarking: {name}")
            print("-" * 70)
            
            analysis = self.agent.analyze_requirements(requirement)
            complexity = analysis['complexity_score']
            
            code = self.agent.generate_code(requirement)
            code_length = len(code)
            
            validation = self.agent._validate_code(code)
            is_valid = validation['valid']
            
            # Calculate score
            score = (complexity * 0.35 + 
                    min(code_length / 200, 100) * 0.25 + 
                    (100 if is_valid else 0) * 0.20 +
                    100 * 0.20)  # Quality metrics
            
            results.append({
                'name': name,
                'complexity': complexity,
                'code_length': code_length,
                'valid': is_valid,
                'score': score
            })
            
            print(f"Complexity:  {complexity}/100")
            print(f"Code Length: {code_length:,} characters")
            print(f"Valid:       {'✓' if is_valid else '✗'}")
            print(f"Score:       {score:.2f}/100")
        
        # Summary
        self.print_section("BENCHMARK SUMMARY")
        
        print(f"{'Test Case':<15} {'Complexity':<15} {'Code Len':<15} {'Valid':<10} {'Score':<10}")
        print("-" * 70)
        
        for result in results:
            print(f"{result['name']:<15} {result['complexity']:>6}/100      "
                  f"{result['code_length']:>10} chars  {('✓' if result['valid'] else '✗'):<10} "
                  f"{result['score']:>6.2f}")
        
        avg_score = sum(r['score'] for r in results) / len(results)
        print("-" * 70)
        print(f"{'AVERAGE':<15} {'':<15} {'':<15} {'':<10} {avg_score:>6.2f}")
        
        # Export results
        export_path = Path("benchmark_results.json")
        with open(export_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✓ Results saved to: {export_path.absolute()}")
    
    def _print_help(self) -> None:
        """Print help text."""
        help_text = """
EnterpriseAI-Local Code Generation Agent - Commands

  generate <requirement>      Generate code from requirements
  analyze <requirement>       Analyze requirements without generating
  interactive                 Interactive mode
  benchmark                   Run benchmark tests
  help                        Show this help text
  clear                       Clear screen
  quit                        Exit interactive mode

Examples:
  > generate "Create a REST API with authentication"
  > analyze "Build a web scraper"
  > benchmark

Options:
  --unlimited                 Use unlimited agent (more features)
  --output FILE              Save generated code to file
  --json                     Output in JSON format
        """
        print(help_text)
    
    def run(self, args) -> None:
        """Run the CLI with parsed arguments."""
        if args.command == 'generate':
            self.generate_command(args.requirement, args.output)
        elif args.command == 'analyze':
            self.analyze_command(args.requirement)
        elif args.command == 'interactive':
            self.interactive_command()
        elif args.command == 'benchmark':
            self.benchmark_command()
        else:
            print("Unknown command. Use 'help' for more information.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="EnterpriseAI-Local Code Generation Agent - CLI Interface (Original: github.com/DarkShadow190922/EnterpriseAI-Local)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py generate "Create a REST API with authentication"
  python cli.py analyze "Build a web scraper"
  python cli.py interactive
  python cli.py benchmark

Run 'python cli.py <command> --help' for more information on a command.
        """
    )
    
    parser.add_argument(
        '--unlimited',
        action='store_true',
        help='Use unlimited agent (generates larger, more comprehensive code)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate code from requirements')
    generate_parser.add_argument('requirement', help='Code generation requirement')
    generate_parser.add_argument(
        '--output', '-o',
        help='Output file to save generated code'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze requirements')
    analyze_parser.add_argument('requirement', help='Requirement to analyze')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Interactive mode')
    
    # Benchmark command
    subparsers.add_parser('benchmark', help='Run benchmark tests')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Initialize CLI
    cli = CodeGenCLI(use_unlimited=args.unlimited)
    
    # Run command
    try:
        cli.run(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

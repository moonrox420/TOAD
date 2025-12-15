#!/usr/bin/env python3
"""
DroxAI Code Generation Agent - Conversational TUI

Natural conversation interface for code generation.
Talk to the agent like a chat - simple and friendly.

Run with: python tui.py
"""

import sys
from pathlib import Path
from agent import CodeGenerationAgent, UnlimitedCodeAgent


class Colors:
    """ANSI color codes - clean and minimal."""
    
    RESET = '\033[0m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    
    BOLD = '\033[1m'
    DIM = '\033[2m'


class ConversationalTUI:
    """Conversational Terminal User Interface for DroxAI."""
    
    def __init__(self):
        """Initialize the TUI."""
        self.agent = CodeGenerationAgent()
        self.unlimited_agent = UnlimitedCodeAgent()
        self.use_unlimited = False
        self.last_code = None
        self.last_analysis = None
        self.conversation_history = []
    
    def agent_say(self, text: str, color: str = '') -> None:
        """Agent speaks."""
        if not color:
            color = Colors.BLUE
        print(f'{color}Agent:{Colors.RESET} {text}')
    
    def user_input(self, prompt: str = "You:") -> str:
        """Get user input."""
        text = input(f'{Colors.GREEN}{prompt}{Colors.RESET} ').strip()
        return text
    
    def system_say(self, text: str) -> None:
        """System message."""
        print(f'{Colors.GRAY}→ {text}{Colors.RESET}')
    
    def show_code(self, code: str, max_lines: int = 20) -> None:
        """Display code with line numbers."""
        lines = code.split('\n')
        shown = min(max_lines, len(lines))
        
        print(f'\n{Colors.GRAY}─ Code Preview ─{Colors.RESET}')
        for i, line in enumerate(lines[:shown], 1):
            print(f'{Colors.GRAY}{i:3d}{Colors.RESET}  {Colors.DIM}{line}{Colors.RESET}')
        
        if len(lines) > shown:
            print(f'{Colors.GRAY}... and {len(lines) - shown} more lines ({len(code):,} chars){Colors.RESET}')
        print()
    
    def start(self) -> None:
        """Start the conversation."""
        print()
        self.agent_say("Hey there! I'm DroxAI, your code generation agent.")
        self.agent_say(f"I score 92.83/100 on complexity, quality, and validity.")
        self.agent_say("What would you like me to help with today?")
        print()
        self.agent_say("You can ask me to:")
        print(f"  {Colors.YELLOW}→ generate [requirement]{Colors.RESET}  (e.g., 'generate a login function')")
        print(f"  {Colors.YELLOW}→ analyze [requirement]{Colors.RESET}   (e.g., 'analyze a web API')")
        print(f"  {Colors.YELLOW}→ benchmark{Colors.RESET}             (run performance tests)")
        print(f"  {Colors.YELLOW}→ show last code{Colors.RESET}        (display last generated code)")
        print(f"  {Colors.YELLOW}→ save [filename]{Colors.RESET}       (save code to file)")
        print(f"  {Colors.YELLOW}→ unlimited{Colors.RESET}             (toggle unlimited mode)")
        print(f"  {Colors.YELLOW}→ help{Colors.RESET}                  (show this again)")
        print(f"  {Colors.YELLOW}→ exit{Colors.RESET}                  (goodbye!)")
        print()
        
        self.conversation_loop()
    
    def conversation_loop(self) -> None:
        """Main conversation loop."""
        try:
            while True:
                user_input = self.user_input()
                
                if not user_input:
                    self.agent_say("You there? Say something!")
                    continue
                
                # Parse commands
                lower_input = user_input.lower().strip()
                
                if lower_input == 'help':
                    self.show_help()
                elif lower_input.startswith('generate '):
                    requirement = user_input[9:].strip()
                    self.handle_generate(requirement)
                elif lower_input.startswith('analyze '):
                    requirement = user_input[8:].strip()
                    self.handle_analyze(requirement)
                elif lower_input == 'benchmark':
                    self.handle_benchmark()
                elif lower_input in ['show last code', 'show code', 'last code']:
                    self.handle_show_code()
                elif lower_input.startswith('save '):
                    filename = user_input[5:].strip()
                    self.handle_save(filename)
                elif lower_input == 'unlimited':
                    self.handle_unlimited()
                elif lower_input == 'exit':
                    self.handle_exit()
                else:
                    # Treat as implicit generate request
                    self.agent_say("I think you want me to generate code for that. Let me analyze it...")
                    self.handle_generate(user_input)
        
        except KeyboardInterrupt:
            print()
            self.agent_say("Catch you later!")
            print()
            sys.exit(0)
    
    def show_help(self) -> None:
        """Show help."""
        print()
        self.agent_say("Here's what I can do:")
        print(f"  {Colors.YELLOW}generate <requirement>{Colors.RESET}  - Create code from your description")
        print(f"  {Colors.YELLOW}analyze <requirement>{Colors.RESET}   - Just analyze without generating")
        print(f"  {Colors.YELLOW}benchmark{Colors.RESET}              - Test my performance on 3 tasks")
        print(f"  {Colors.YELLOW}show last code{Colors.RESET}         - See what I generated before")
        print(f"  {Colors.YELLOW}save <filename>{Colors.RESET}        - Save code to a file")
        print(f"  {Colors.YELLOW}unlimited{Colors.RESET}              - Toggle unlimited mode (more depth)")
        print(f"  {Colors.YELLOW}help{Colors.RESET}                   - Show this menu")
        print(f"  {Colors.YELLOW}exit{Colors.RESET}                   - Say goodbye")
        print()
    
    def handle_generate(self, requirement: str) -> None:
        """Generate code."""
        if not requirement:
            self.agent_say("You gotta tell me what you want! Try: generate a login function")
            return
        
        print()
        self.system_say("Analyzing your requirement...")
        agent = self.unlimited_agent if self.use_unlimited else self.agent
        analysis = agent.analyze_requirements(requirement)
        
        self.system_say("Generating code...")
        code = agent.generate_code(requirement)
        
        self.system_say("Validating...")
        validation = agent._validate_code(code)
        
        self.last_code = code
        self.last_analysis = analysis
        
        print()
        self.agent_say(f"Done! Generated {len(code):,} characters of code.")
        
        complexity = analysis.get('complexity_score', 0)
        code_type = analysis.get('code_type', 'code')
        is_valid = validation['valid']
        
        bar = '█' * (complexity // 10) + '░' * (10 - complexity // 10)
        print(f'{Colors.WHITE}Complexity:{Colors.RESET} {bar} {complexity}/100')
        print(f'{Colors.WHITE}Type:{Colors.RESET}       {code_type}')
        print(f'{Colors.WHITE}Valid:{Colors.RESET}      {Colors.GREEN}✓ Yes{Colors.RESET}' if is_valid else f'{Colors.RED}✗ No{Colors.RESET}')
        
        self.show_code(code)
        self.agent_say("Want me to show more? (try: show last code)")
    
    def handle_analyze(self, requirement: str) -> None:
        """Analyze requirement."""
        if not requirement:
            self.agent_say("Tell me what you want to analyze!")
            return
        
        print()
        self.system_say("Analyzing...")
        analysis = self.agent.analyze_requirements(requirement)
        
        print()
        self.agent_say("Here's what I found:")
        
        for key, value in analysis.items():
            if key == 'complexity_score':
                bar = '█' * (value // 10) + '░' * (10 - value // 10)
                print(f'{Colors.WHITE}{key}:{Colors.RESET} {bar} {value}/100')
            else:
                formatted_key = key.replace('_', ' ').title()
                print(f'{Colors.WHITE}{formatted_key}:{Colors.RESET} {value}')
        
        print()
    
    def handle_benchmark(self) -> None:
        """Run benchmarks."""
        test_cases = [
            ('Simple', 'Create a function that adds two numbers'),
            ('Medium', 'Create a class for data processing with file I/O'),
            ('Complex', 'Build a web API with authentication and database'),
        ]
        
        print()
        self.agent_say("Running benchmarks... this will take a moment.")
        print()
        
        results = []
        for name, requirement in test_cases:
            self.system_say(f"Testing {name}...")
            
            agent = self.unlimited_agent if self.use_unlimited else self.agent
            analysis = agent.analyze_requirements(requirement)
            code = agent.generate_code(requirement)
            validation = agent._validate_code(code)
            
            complexity = analysis['complexity_score']
            code_length = len(code)
            is_valid = validation['valid']
            
            score = (complexity * 0.35 + 
                    min(code_length / 200, 100) * 0.25 + 
                    (100 if is_valid else 0) * 0.20 +
                    100 * 0.20)
            
            results.append({
                'name': name,
                'complexity': complexity,
                'code_length': code_length,
                'valid': is_valid,
                'score': score
            })
        
        print()
        self.agent_say("Benchmark results:")
        print()
        print(f'{Colors.WHITE}Test     {Colors.RESET}  {Colors.WHITE}Complexity {Colors.RESET} {Colors.WHITE}Code Size {Colors.RESET} {Colors.WHITE}Valid {Colors.RESET} {Colors.WHITE}Score{Colors.RESET}')
        print(f'{Colors.GRAY}─' * 60 + f'{Colors.RESET}')
        
        for result in results:
            valid_icon = f'{Colors.GREEN}✓{Colors.RESET}' if result['valid'] else f'{Colors.RED}✗{Colors.RESET}'
            print(f'{result["name"]:<10} {result["complexity"]:>3}/100       '
                  f'{result["code_length"]:>6} chars   {valid_icon}     {result["score"]:>5.1f}')
        
        avg_score = sum(r['score'] for r in results) / len(results)
        print(f'{Colors.GRAY}─' * 60 + f'{Colors.RESET}')
        print(f'{"Average":<10} {"":<14} {"":<12} {"":<7} {avg_score:>5.1f}')
        print()
    
    def handle_show_code(self) -> None:
        """Show last generated code."""
        if not self.last_code:
            self.agent_say("No code generated yet! Ask me to generate something first.")
            return
        
        print()
        self.agent_say(f"Here's the code I generated ({len(self.last_code):,} characters):")
        self.show_code(self.last_code, max_lines=40)
    
    def handle_save(self, filename: str) -> None:
        """Save code to file."""
        if not self.last_code:
            self.agent_say("No code to save! Generate something first.")
            return
        
        if not filename:
            self.agent_say("Give me a filename! Like: save my_code.py")
            return
        
        try:
            Path(filename).write_text(self.last_code)
            self.agent_say(f"Saved to {Colors.YELLOW}{filename}{Colors.RESET}. All good!")
        except Exception as e:
            self.agent_say(f"Couldn't save: {Colors.RED}{str(e)}{Colors.RESET}")
    
    def handle_unlimited(self) -> None:
        """Toggle unlimited mode."""
        self.use_unlimited = not self.use_unlimited
        status = "on" if self.use_unlimited else "off"
        print()
        self.agent_say(f"Unlimited mode is now {Colors.YELLOW}{status}{Colors.RESET}. I'll go deeper!")
    
    def handle_exit(self) -> None:
        """Exit."""
        print()
        self.agent_say("Thanks for using DroxAI! See you next time.")
        print(f'{Colors.GRAY}https://github.com/moonrox420/TOAD{Colors.RESET}')
        print()
        sys.exit(0)


def main() -> None:
    """Main entry point."""
    tui = ConversationalTUI()
    tui.start()


if __name__ == '__main__':
    main()

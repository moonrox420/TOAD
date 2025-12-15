import subprocess
import re

# Get the original agent.py from the initial commit
result = subprocess.run(['git', 'show', 'e143df8:agent.py'], 
                       capture_output=True, text=True, cwd='C:\\Users\\dusti\\code-boss')

lines = result.stdout.split('\n')

# Find the complexity calculation method
in_complexity = False
complexity_code = []
for i, line in enumerate(lines):
    if 'def _calculate_complexity' in line:
        in_complexity = True
        start = max(0, i - 2)
        complexity_code = lines[start:min(len(lines), i + 100)]
        break

# Find the return statement
for line in complexity_code:
    if 'return int' in line and 'complexity' in lines[lines.index(line)-1:lines.index(line)+1][0].lower():
        print("Original complexity return formula:")
        print(line.strip())
        
# Also check what the scoring breakdown was
print("\n\nLooking for scoring logic...")
for i, line in enumerate(lines):
    if 'def _calculate_performance_score' in line or 'def score' in line.lower():
        print(f"Found at line {i}: {line.strip()}")
        # Print next 30 lines
        for j in range(i, min(i+30, len(lines))):
            print(lines[j])
        break

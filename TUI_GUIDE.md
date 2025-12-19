# DroxAI Conversational TUI Guide

## What It Is

A natural, conversational terminal interface that feels like chatting with an AI assistant—because you are!

No menus, no options numbered 1-6. Just talk to the agent like you'd talk to me.

## Run It

```bash
python tui.py
```

Or after pip install:
```bash
droxai-tui
```

## How to Use

Just type what you want. The agent understands natural commands:

### Generate Code
```
You: generate a login function
Agent: [generates code]

You: generate a FastAPI endpoint for user authentication
Agent: [generates more complex code]

You: create a class for handling database connections
Agent: [generates database handling code]
```

**Shorthand:** Anything that doesn't match a command gets treated as a generation request automatically.

```
You: a function that calculates fibonacci numbers
Agent: [generates fibonacci code]
```

### Analyze Without Generating
```
You: analyze a web scraping tool
Agent: [shows complexity, architecture, etc without generating]
```

### Run Benchmarks
```
You: benchmark
Agent: [tests 3 complexity levels, shows performance scores]
```

### View and Save Code
```
You: show last code
Agent: [displays the code you just generated]

You: save fibonacci.py
Agent: [saves to file]
```

### Toggle Unlimited Mode
```
You: unlimited
Agent: Unlimited mode is now on. I'll go deeper!
```
(Unlimited mode generates more comprehensive, detailed code)

### Get Help
```
You: help
Agent: [shows all available commands]
```

### Exit
```
You: exit
Agent: Thanks for using DroxAI!
```

## The Flow

1. **You talk** → Type naturally in English
2. **Agent understands** → Parses your intent
3. **Agent generates** → Creates code or analyzes
4. **You see metrics** → Complexity, validity, size
5. **You decide** → Generate more, save, analyze, benchmark

## Example Session

```
Agent: Hey there! I'm DroxAI, your code generation agent.
Agent: I score 92.83/100 on complexity, quality, and validity.
Agent: What would you like me to help with today?

Agent: You can ask me to:
  → generate [requirement]  (e.g., 'generate a login function')
  → analyze [requirement]   (e.g., 'analyze a web API')
  → benchmark               (run performance tests)
  → show last code          (display last generated code)
  → save [filename]         (save code to file)
  → unlimited               (toggle unlimited mode)
  → help                    (show this again)
  → exit                    (goodbye!)

You: generate a python decorator that caches function results

Agent: Done! Generated 487 characters of code.
Complexity: ██████░░░░ 62/100
Type:       decorator
Valid:      ✓ Yes

─ Code Preview ─
  1  import functools
  2  from typing import Callable, Any
  3  
  4  def cache_results(max_size: int = 128) -> Callable:
  5      """
  6      A decorator that caches function results up to max_size entries.
  7      Uses LRU eviction policy when cache is full.
  8      """
      ...and more lines

Agent: Want me to show more? (try: show last code)

You: show last code

Agent: Here's the code I generated (487 characters):

─ Code Preview ─
  1  import functools
  2  from typing import Callable, Any
  3  
  4  def cache_results(max_size: int = 128) -> Callable:
      ...full code...

You: save decorator_cache.py

Agent: Saved to decorator_cache.py. All good!

You: now generate a decorator for logging function calls

Agent: Done! Generated 523 characters of code.
Complexity: ██████░░░░ 65/100
Type:       decorator
Valid:      ✓ Yes
```

## Commands Reference

| Command | Example | What It Does |
|---------|---------|--------------|
| `generate <req>` | `generate a login form` | Creates code from your description |
| `analyze <req>` | `analyze a web API` | Shows complexity without generating |
| `benchmark` | `benchmark` | Tests 3 complexity levels |
| `show last code` | `show last code` | Display previously generated code |
| `save <file>` | `save my_code.py` | Save code to file |
| `unlimited` | `unlimited` | Toggle deeper generation mode |
| `help` | `help` | Show all commands |
| `exit` | `exit` | Quit the app |

## Tips

- **Natural language works.** "make me a function that..." or "i need code for..." all work
- **Unlimited mode is deeper.** Turns on for more comprehensive code with docs, tests, error handling
- **Save often.** Use `save filename.py` whenever you get code you like
- **Benchmark anytime.** Run benchmarks to see my performance on different complexity levels
- **No special syntax.** Just type naturally. The agent gets what you want

## Files

- **tui.py** - The conversational interface (300+ lines)
- **cli.py** - Command-line interface (numbered menus)
- **web_ui.py** - Browser interface (web)
- **agent.py** - The core code generation engine

## Performance

- **Score:** 92.83/100
- **Complexity handling:** 35% factor
- **Code quality:** Full validation
- **Speed:** Instant to a few seconds depending on complexity

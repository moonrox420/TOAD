# Installation & Setup Guide

Three ways to install and use DroxAI Code Generation Agent:

---

## Option 1: Direct Usage (In Project Directory)

**Fastest for development.**

```bash
cd C:\Users\dusti\code-boss

# Run CLI
python cli.py generate "Create a REST API"

# Or run web UI
python web_ui.py
```

**Pros:**
- No installation needed
- Works immediately
- Good for testing

**Cons:**
- Must be in project directory
- Can't use from other folders
- Not ideal for distribution

---

## Option 2: Pip Install (Professional/Recommended for Customers)

**Best for distribution and professional use.**

### Installation

```bash
# Install in development mode (editable)
cd C:\Users\dusti\code-boss
pip install -e .

# Or install from GitHub (once published)
pip install git+https://github.com/moonrox420/TOAD.git
```

### Usage (From Anywhere)

```bash
# Use the installed command
droxai generate "Create a REST API"
droxai analyze "requirement"
droxai interactive
droxai benchmark

# Or start the web UI
droxai-web
```

**Pros:**
- Works from anywhere
- Professional installation
- Standard Python practice
- Easy to update (`pip install --upgrade`)
- Can be published to PyPI

**Cons:**
- Requires pip installation step
- Takes up more disk space

**Best For:**
- Selling to customers
- Professional distribution
- Long-term use

---

## Option 3: PATH Wrapper Scripts (Windows Only)

**Use from anywhere in Windows without pip.**

### Setup

**Option 3A: Batch File (Recommended for Windows)**

1. Create a scripts directory:
```powershell
mkdir C:\Users\dusti\scripts
```

2. Copy the batch file:
```powershell
copy C:\Users\dusti\code-boss\droxai.bat C:\Users\dusti\scripts\droxai.bat
```

3. Edit the batch file to point to your project:
```batch
REM Open C:\Users\dusti\scripts\droxai.bat and update this line:
set DROXAI_PROJECT=C:\Users\dusti\code-boss
```

4. Add to Windows PATH:
   - Press `Win + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Click "New" under User Variables
   - Variable name: `PATH`
   - Variable value: `C:\Users\dusti\scripts`
   - Click OK, restart terminal

5. Test:
```powershell
droxai generate "Create a hello world function"
```

**Option 3B: PowerShell**

1. Edit your PowerShell profile:
```powershell
notepad $PROFILE
```

2. Add this function:
```powershell
function droxai { & "C:\Users\dusti\code-boss\droxai.ps1" @args }
function droxai-web { & "C:\Users\dusti\code-boss\web_ui.ps1" @args }
```

3. Save and reload:
```powershell
. $PROFILE
```

4. Test:
```powershell
droxai generate "Create a hello world function"
```

**Pros:**
- No installation needed
- Works from anywhere
- Windows-native solutions
- Fast startup

**Cons:**
- Windows only (Option 3A/B)
- Manual PATH setup
- Must edit batch files

**Best For:**
- Windows users who don't want to use pip
- Quick setup without installation

---

## Option 4: Linux/Mac Shell Script

**For Linux and Mac users.**

### Setup

1. Copy the script:
```bash
cp ~/code-boss/droxai /usr/local/bin/droxai
chmod +x /usr/local/bin/droxai
```

2. Edit the script to point to your installation:
```bash
nano /usr/local/bin/droxai
# Update PROJECT_DIR="/path/to/code-boss"
```

3. Test:
```bash
droxai generate "Create a hello world function"
```

**Pros:**
- Standard Unix approach
- Works from anywhere
- Easy to share

**Cons:**
- Requires manual setup
- Unix/Linux/Mac only

**Best For:**
- Linux/Mac users
- Team environments

---

## Comparison Table

| Feature | Option 1 | Option 2 | Option 3 | Option 4 |
|---------|----------|----------|----------|----------|
| **Setup Time** | Instant | 1 min | 5 min | 2 min |
| **Works Anywhere** | ❌ | ✅ | ✅ | ✅ |
| **Platform** | All | All | Windows | Unix/Mac |
| **Professional** | ❌ | ✅✅✅ | ⚠️ | ✅ |
| **For Customers** | ❌ | ✅✅✅ | ⚠️ | ✅ |
| **Best For** | Testing | Distribution | Devs | Linux/Mac |

---

## Recommended Setup

**For yourself (development):**
```bash
# Use Option 2 (pip install) for convenience
pip install -e C:\Users\dusti\code-boss
```

**For customers:**
```bash
# Provide them Option 2 (pip install)
pip install droxai-codegen
# Or from GitHub
pip install git+https://github.com/moonrox420/TOAD.git
```

**For quick testing:**
```bash
# Use Option 1 (direct usage)
cd C:\Users\dusti\code-boss
python cli.py generate "..."
```

---

## Uninstall

### Remove pip installation:
```bash
pip uninstall droxai-codegen
```

### Remove PATH wrapper:
- **Windows**: Delete from `C:\Users\dusti\scripts\`
- **Linux/Mac**: `rm /usr/local/bin/droxai`

---

## Troubleshooting

### "droxai command not found"

**Windows:**
- Check PATH: `echo %PATH%`
- Restart terminal after adding to PATH
- Verify batch file exists

**Linux/Mac:**
- Check: `which droxai`
- Make sure `/usr/local/bin/` is in PATH
- Verify executable: `chmod +x /usr/local/bin/droxai`

### "agent.py not found"

- Verify project directory path is correct in wrapper script
- Check that `agent.py` exists at that location

### "Python not found"

- Ensure Python 3.8+ is installed
- Verify it's in PATH: `python --version`
- Use full path if needed: `C:\Python312\python.exe`

---

## Next Steps

1. **For development**: Install with `pip install -e .`
2. **For customers**: Document Option 2 in your README
3. **For convenience**: Set up Option 3 or 4 for quick access

All three options work - choose what's best for your workflow!

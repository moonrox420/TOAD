#!/usr/bin/env pwsh
<#
.SYNOPSIS
    DroxAI Code Generation Agent - PowerShell Wrapper

.DESCRIPTION
    Wrapper script for DroxAI CLI that works from anywhere in PowerShell.
    
.EXAMPLE
    droxai generate "Create a REST API"
    droxai analyze "requirement"
    droxai interactive
    droxai benchmark

.NOTES
    Place this in your $PROFILE or add to PATH for global access.
    
    To install globally:
    1. Save as droxai.ps1
    2. Add to $PROFILE (usually at Documents\PowerShell\profile.ps1)
    3. Add this function:
       function droxai { & "C:\path\to\code-boss\droxai.ps1" @args }
#>

param(
    [string]$Command,
    [string[]]$Arguments
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = $ScriptDir

# Check if agent.py exists
if (-not (Test-Path "$ProjectDir\agent.py")) {
    Write-Error "DroxAI project not found at $ProjectDir"
    exit 1
}

# Run the CLI
python "$ProjectDir\cli.py" $Command $Arguments

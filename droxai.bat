@echo off
REM DroxAI Code Generation Agent - Windows Batch Wrapper
REM 
REM Usage:
REM   droxai generate "Create a REST API"
REM   droxai analyze "requirement"
REM   droxai interactive
REM   droxai benchmark
REM
REM Place this file in a directory in your PATH, e.g., C:\Users\<username>\AppData\Local\Scripts\
REM Then use 'droxai' command from anywhere
REM

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set DROXAI_DIR=%~dp0
set DROXAI_PROJECT=%DROXAI_DIR%..

REM Check if project directory exists
if not exist "%DROXAI_PROJECT%\agent.py" (
    echo Error: DroxAI project directory not found at %DROXAI_PROJECT%
    echo Please update the batch file with the correct path to the DroxAI project.
    exit /b 1
)

REM Run the CLI with all arguments passed through
python "%DROXAI_PROJECT%\cli.py" %*

endlocal

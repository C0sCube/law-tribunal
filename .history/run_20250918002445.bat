@echo off
REM Change directory to project root
cd /d "C:\Users\rando\Office Projects\law-tribunal"

REM Activate virtual environment
call .venv\Scripts\activate

REM Run Python script
python main.py

REM Keep window open after script finishes
pause
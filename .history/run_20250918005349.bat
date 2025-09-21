@echo off
REM Change to your project folder
cd /d "C:\Users\kaustubh.keny\Projects\office-work\law-tribunal"

REM Activate virtual environment
call .venv\Scripts\activate

REM Run your Python script
python main.py

REM Keep window open when finished
pause

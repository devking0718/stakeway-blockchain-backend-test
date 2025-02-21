@echo off

REM Create virtual environment if it doesn't exist
if not exist venv (
    python -m venv venv
    echo Created virtual environment
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
pip install -r requirements.txt

echo Setup complete! Virtual environment is activated and dependencies are installed.
echo To start the server, run: uvicorn app.main:app --reload

pause 
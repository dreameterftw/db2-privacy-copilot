@echo off
REM Setup script for Db2 Privacy Copilot (Windows)

echo ========================================
echo Db2 Privacy Copilot - Setup Script
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo + .env created
    echo.
    echo WARNING: Edit .env and set a strong DB2_PASSWORD
    echo.
) else (
    echo + .env already exists
)

REM Create Python virtual environment
if not exist .venv (
    echo Creating Python virtual environment...
    python -m venv .venv
    echo + Virtual environment created
) else (
    echo + Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -e ".[dev]"
echo + Dependencies installed

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env and set DB2_PASSWORD
echo   2. Start Db2: docker compose up -d
echo   3. Wait for Db2 to initialize (5-10 minutes)
echo      Check status: docker compose logs -f db2
echo      Look for: "Setup has completed"
echo   4. Initialize database: python app/bootstrap.py
echo   5. Seed data: python eval/seed.py
echo   6. Run tests: pytest
echo.
pause

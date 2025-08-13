@echo off
echo Building WoW Boss Simulator executable...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build the executable
echo Building executable...
pyinstaller wow_boss_sim.spec

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

echo.
echo Build complete!
echo Executable location: dist\WoW_Boss_Simulator.exe
echo.
pause
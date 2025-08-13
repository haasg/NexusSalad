#!/bin/bash

echo "Building WoW Boss Simulator executable..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the executable
echo "Building executable..."
pyinstaller wow_boss_sim.spec

# Deactivate virtual environment
deactivate

echo "Build complete!"
echo ""

# Platform-specific output information
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS build complete. Executable location:"
    echo "  App Bundle: dist/WoW Boss Simulator.app"
    echo "  Run with: open 'dist/WoW Boss Simulator.app'"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    echo "Windows build complete. Executable location:"
    echo "  dist/WoW_Boss_Simulator.exe"
else
    echo "Linux build complete. Executable location:"
    echo "  dist/WoW_Boss_Simulator"
fi
# WoW Boss Fight Simulation

A Python simulation of a World of Warcraft-style boss fight mechanic featuring rotating stars and expanding damage rings.

## Quick Start (No Python Required)

### For Users - Download and Run
1. Download the latest release for your platform from the Releases page
2. Extract the file (if zipped)
3. Double-click to run:
   - **Windows**: `WoW_Boss_Simulator.exe`
   - **macOS**: `WoW Boss Simulator.app`
   - **Linux**: `./WoW_Boss_Simulator`

## For Developers

### Requirements
- Python 3.x
- Pygame

### Installation
1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running from Source
```bash
python wow_boss_sim.py
```

### Building Standalone Executable

#### Automatic Build (Recommended)
- **macOS/Linux**: `./build.sh`
- **Windows**: `build.bat`

The executable will be created in the `dist/` folder.

#### Manual Build
```bash
pip install pyinstaller
pyinstaller wow_boss_sim.spec
```

### Distribution
After building, you can distribute the following files:
- **Windows**: `dist/WoW_Boss_Simulator.exe` (single file, ~40MB)
- **macOS**: `dist/WoW Boss Simulator.app` (app bundle, ~45MB)
- **Linux**: `dist/WoW_Boss_Simulator` (single file, ~40MB)

No Python installation or additional files required!

## How to Use

1. **Setup Phase**: Click anywhere inside the arena to place 6 stars
   - Stars alternate between clockwise and counter-clockwise rotation

2. **Start Simulation**: Press SPACE when all 6 stars are placed
   - After 3 seconds, stars begin rotating
   - Each star emits expanding damage rings every second
   - Rings show for 1.5 seconds before fading

3. **Controls**:
   - Left Click: Place stars (during setup)
   - SPACE: Start/Pause simulation
   - R: Reset simulation
   - ESC: Exit

## Game Mechanics

- **Arena**: Large circular boss room
- **Stars**: 6 stars that rotate around the arena (3 clockwise, 3 counter-clockwise)
- **Damage Rings**: Purple expanding rings that would deal damage to players
- **Pattern**: The overlapping rings create complex patterns players must dodge
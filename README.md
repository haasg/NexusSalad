# WoW Boss Fight Simulation

A Python simulation of a World of Warcraft-style boss fight mechanic featuring rotating stars and expanding damage rings.

## Requirements

- Python 3.x
- Pygame

## Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install pygame:
```bash
pip install pygame
```

## Running the Simulation

```bash
python wow_boss_sim.py
```

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
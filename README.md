# Snake Game

A classic Snake game built with Python and Pygame, featuring a grass-themed background, directional snake sprites, sound effects, and an enhanced user interface. Eat apples to grow longer and achieve the highest score possible without colliding with yourself or the walls!

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Controls](#controls)
- [Asset Requirements](#asset-requirements)
- [Contributing](#contributing)
- [License](#license)

## Overview
This Snake game implementation includes modern enhancements while maintaining the nostalgic feel of the classic arcade game. Players navigate a snake across a grid, eating food to grow while avoiding collisions. The game features a start screen, pause functionality, sound effects, a grid overlay, and a game over screen with restart and quit options.

## Installation
### Prerequisites:
- Python 3.6 or higher
- Pygame library

### Clone the Repository:
```bash
git clone https://github.com/yourusername/snake-game.git
cd snake-game
```

### Install Dependencies:
```bash
pip install pygame
```

### Setup:
1. Place required assets in the `assets` folder
2. Run `python snake_game.py`

## Usage
1. Launch the game by running the script
2. View instructions on the start screen
3. Click "Start" or press any key to begin
4. Navigate snake to eat apples and grow
5. Use pause ('P') and speed controls ('+'/'-')

## Features
- Start Screen with instructions
- Pause functionality
- Sound effects
- Grid overlay
- Score tracking
- Game over screen
- Adjustable speed
- Directional sprites

## Controls
| Key/Input | Action |
|-----------|--------|
| Arrow Keys | Move snake |
| P | Pause/Resume |
| +/= | Increase speed |
| - | Decrease speed |
| R | Restart game |
| Mouse Click | Start/Quit |

## Asset Requirements
### Images (40x40px)
- `apple.png`
- `head_[up/down/left/right].png`
- `body_[horizontal/vertical/bottomleft/bottomright/topleft/topright].png`
- `tail_[up/down/left/right].png`

### Sounds
- `eat.wav`
- `game_over.wav`

## Contributing
1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Submit pull request

## License
MIT License

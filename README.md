# Legends of the Realm

A text-based RPG adventure game built in Python with an immersive story, character progression, combat system, and merchant interactions.

## Features

- **Character Creation**: Choose from multiple races, classes, and backgrounds
- **Combat System**: Turn-based battles with equipment and abilities
- **Shop System**: Interactive merchants with voice acting and dynamic inventory
- **Exploration**: Multiple locations with random encounters
- **Story Elements**: Rich lore and dialogue systems
- **Audio**: Background music and sound effects
- **Save/Load**: Persistent game state

## Project Structure

```
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── core/              # Core game logic
│   │   └── game.py        # Main game loop and logic
│   ├── entities/          # Game entities
│   │   ├── character.py   # Player character
│   │   ├── enemy.py       # Enemy entities
│   │   ├── item.py        # Items and equipment
│   │   └── npc.py         # Non-player characters
│   ├── systems/           # Game systems
│   │   ├── battle.py      # Combat system (in game.py)
│   │   ├── dialogue.py    # Dialogue system
│   │   ├── quest.py       # Quest management
│   │   └── shop.py        # Merchant system
│   ├── ui/                # User interface
│   │   ├── art.py         # ASCII art
│   │   ├── display.py     # Console utilities
│   │   └── menus.py       # Menu systems
│   ├── audio/             # Audio management
│   │   └── audio.py       # Music and sound effects
│   ├── data/              # Data management
│   │   ├── database.py    # Game data loading
│   │   └── loader.py      # Data utilities
│   └── utils/             # Utility functions
│       ├── helpers.py     # Save/load and utilities
│       └── tools.py       # Tools class and storytelling
├── assets/                # Game assets
│   ├── data/              # JSON data files
│   ├── music/             # Background music
│   ├── sfx/               # Sound effects
│   └── docs/              # Documentation
├── config/                # Configuration files
│   └── settings.json      # Game settings
├── saves/                 # Save game files
│   └── savegame.json      # Player save data
└── scripts/               # Utility scripts
    └── RUN.bat            # Launch script
```

## Installation

1. **Clone or download the project**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

### Option 1: Python directly
```bash
python main.py
```

### Option 2: Windows batch script
```bash
scripts\RUN.bat
```

## Development

### Key Components

- **Game Loop**: Located in `src/core/game.py`
- **Character System**: `src/entities/character.py` handles player stats, inventory, and progression
- **Shop System**: `src/systems/shop.py` manages merchant interactions with voice acting
- **Battle System**: Integrated into the main game loop with turn-based combat
- **Data Management**: JSON files in `assets/data/` for easy modification

### Adding New Content

1. **New Items**: Add to `assets/data/items.json`
2. **New Enemies**: Add to `assets/data/enemies.json`
3. **New Locations**: Add to `assets/data/locations.json`
4. **New NPCs**: Add to `assets/data/npcs.json`
5. **New Shops**: Add to `assets/data/shops.json`

### Developer Commands

Enable developer mode in `config/settings.json` and use commands in-game:
- `/gold [amount]` - Set player gold
- `/battle [enemy_name]` - Start combat with specific enemy
- `/print npcs` - Display NPC information table

## Configuration

Edit `config/settings.json` to customize:
- Developer mode settings
- Audio preferences
- Display options

## Audio Assets

- **Music**: Background tracks in `assets/music/`
- **SFX**: Sound effects in `assets/sfx/`
- **Voice Acting**: Character voices in `assets/sfx/voiceover/[character]/`

## Save System

- Save files stored in `saves/savegame.json`
- Automatically preserves character progress, inventory, and location
- Load game option available from main menu

## Known Issues

- Some circular import warnings during development (resolved in final structure)
- Audio requires pygame installation
- Voice acting files must be in specific directory structure

## Contributing

1. Follow the modular structure when adding features
2. Keep game data in JSON files for easy editing
3. Use the existing UI components for consistent styling
4. Test save/load functionality after major changes

## License

Game assets and code are for educational purposes. Check individual asset licenses for distribution rights.

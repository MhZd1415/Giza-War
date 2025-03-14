# Tank Game

A 2D top-down tank shooter game built with Pygame. Fight off waves of enemies, collect upgrades, and survive as long as possible!

## Game Features

- Top-down tank combat
- Wave-based enemy progression
- Multiple enemy types
- Upgrade and shop system
- Floating text effects
- Health, damage, and speed upgrades
- Special abilities
- World drops and pickups

## How to Run

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
   ```
   pip install pygame
   ```
3. Run the game:
   ```
   python main.py
   ```

## Controls

- **WASD**: Movement
- **Mouse**: Aim
- **Left Mouse Button**: Shoot
- **Right Mouse Button**: Special attack (when unlocked)
- **E**: Open/close shop
- **ESC**: Pause game
- **ALT+Enter**: Toggle fullscreen

## Game Structure

The game is organized into the following directory structure:

```
/
├── main.py           # Game entry point
├── game.py           # Main Game class
├── config.json       # Game configuration (created on first run)
├── game.log          # Game log file
├── assets/           # Game assets (images, sounds)
├── entities/         # Game entities (player, enemies, etc.)
│   ├── player.py     # Player class
│   ├── enemy.py      # Enemy classes
│   ├── projectile.py # Projectile classes
│   └── drop.py       # Item drop classes
├── ui/               # User interface components
│   ├── button.py     # Button class
│   ├── floating_text.py # Floating text effects
│   ├── hud.py        # Heads-up display
│   ├── shop.py       # Shop interface
│   └── upgrades.py   # Upgrade system
├── utils/            # Utility functions and constants
│   ├── config.py     # Configuration handling
│   ├── constants.py  # Game constants
│   └── debug.py      # Debugging utilities
└── world/            # World and map-related components
    └── world_map.py  # World map handling
```

## How to Modify

### Changing Game Constants

Edit `utils/constants.py` to modify:
- Colors
- Player stats
- Enemy stats
- Drop chances
- World settings

### Changing Game Configuration

Edit `config.json` (created after first run) to change:
- Screen resolution
- Difficulty levels
- Sound volumes
- Key bindings

### Adding New Enemies

1. Open `entities/enemy.py`
2. Create a new enemy class or extend existing ones
3. Add the new enemy type to `ENEMY_TYPE_MULTIPLIERS` in `constants.py`
4. Update the enemy creation in `game.py` to include your new enemy type

### Adding New Upgrades

1. Open `ui/upgrades.py`
2. Add a new upgrade to the available upgrades
3. Implement the upgrade effect in `game.py` in the `apply_upgrade` method

### Adding New Items/Drops

1. Open `entities/drop.py`
2. Add a new drop type
3. Add the drop chance to `DROP_CHANCES` in `constants.py`
4. Implement the effect when collected in `game.py` in the `update_drops` method

## Troubleshooting

- Check `game.log` for error messages
- If the game crashes, a `crash_report.txt` will be created with details
- Make sure your Python environment has all the required packages
- Verify that the folder structure is intact

## Contributing

Contributions are welcome! Feel free to submit pull requests with improvements or bug fixes.

## License

This project is open source and available for personal and educational use. 

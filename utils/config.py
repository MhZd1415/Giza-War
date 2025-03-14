import json
import os
import logging

# Default configuration values
DEFAULT_CONFIG = {
    # Display settings
    "screen_width": 1280,
    "screen_height": 720,
    "fullscreen": False,
    "vsync": True,
    "max_fps": 60,
    
    # Game difficulty settings
    "difficulty": "normal",  # easy, normal, hard
    "enemy_health_multiplier": {
        "easy": 0.75,
        "normal": 1.0,
        "hard": 1.5
    },
    "enemy_damage_multiplier": {
        "easy": 0.75,
        "normal": 1.0,
        "hard": 1.25
    },
    "player_damage_multiplier": {
        "easy": 1.25,
        "normal": 1.0,
        "hard": 0.9
    },
    
    # Player starting stats
    "player_starting_health": 100,
    "player_starting_speed": 3.0,
    "player_starting_damage": 10,
    
    # Game balance settings
    "xp_multiplier": 1.0,
    "coin_multiplier": 1.0,
    "wave_difficulty_scaling": 1.0,
    
    # Audio settings
    "master_volume": 0.8,
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "mute": False,
    
    # Controls
    "key_bindings": {
        "move_up": "w",
        "move_down": "s",
        "move_left": "a",
        "move_right": "d",
        "shoot": "mouse1",
        "special": "mouse2",
        "shop": "e",
        "pause": "escape"
    }
}

def get_config_path():
    """Get the path to the configuration file"""
    # Try to find the config in the game root directory
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(script_dir, "config.json")

def load_configuration():
    """
    Load game configuration from file, or create a default one if it doesn't exist.
    
    Returns:
        dict: The loaded configuration dictionary
    """
    logger = logging.getLogger("TankGame.Config")
    config_path = get_config_path()
    
    # Check if config file exists
    if os.path.exists(config_path):
        try:
            # Load existing config
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
            
            logger.info(f"Configuration loaded from {config_path}")
            
            # Merge with default config to ensure all keys exist
            merged_config = DEFAULT_CONFIG.copy()
            update_nested_dict(merged_config, loaded_config)
            
            return merged_config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.info("Using default configuration")
            save_configuration(DEFAULT_CONFIG)  # Save default config for next time
            return DEFAULT_CONFIG
    else:
        # Create default config file
        logger.info(f"No configuration file found at {config_path}")
        logger.info("Creating default configuration file")
        save_configuration(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_configuration(config):
    """
    Save the current configuration to file.
    
    Args:
        config (dict): The configuration dictionary to save
    
    Returns:
        bool: True if successful, False otherwise
    """
    logger = logging.getLogger("TankGame.Config")
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        logger.info(f"Configuration saved to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}")
        return False

def update_nested_dict(base_dict, new_dict):
    """
    Recursively update a nested dictionary with values from another dictionary.
    
    Args:
        base_dict (dict): The base dictionary to update
        new_dict (dict): The dictionary with new values
    
    Returns:
        dict: The updated dictionary
    """
    for key, value in new_dict.items():
        if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
            update_nested_dict(base_dict[key], value)
        else:
            base_dict[key] = value
    return base_dict

def get_difficulty_multiplier(config, stat_type):
    """
    Get the difficulty multiplier for a specific stat type.
    
    Args:
        config (dict): The configuration dictionary
        stat_type (str): The type of stat to get multiplier for
            (enemy_health, enemy_damage, player_damage)
    
    Returns:
        float: The multiplier for the current difficulty level
    """
    difficulty = config.get("difficulty", "normal")
    
    if stat_type == "enemy_health":
        return config.get("enemy_health_multiplier", {}).get(difficulty, 1.0)
    elif stat_type == "enemy_damage":
        return config.get("enemy_damage_multiplier", {}).get(difficulty, 1.0)
    elif stat_type == "player_damage":
        return config.get("player_damage_multiplier", {}).get(difficulty, 1.0)
    else:
        return 1.0

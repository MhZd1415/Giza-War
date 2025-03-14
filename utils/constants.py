"""
Constants for Tank Game

This module contains game-wide constants that are used throughout the game.
These are organized by category for easier modification and reference.
"""

import os
import pygame

# Colors in RGB format
COLORS = {
    # Basic colors
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (255, 0, 0),
    'green': (0, 255, 0),
    'blue': (0, 0, 255),
    'yellow': (255, 255, 0),
    'cyan': (0, 255, 255),
    'magenta': (255, 0, 255),
    
    # UI colors
    'background': (20, 20, 40),  # Dark blue-gray
    'ui_bg': (30, 30, 50),       # Slightly lighter background for UI elements
    'ui_border': (100, 100, 150), # Border color for UI elements
    'text': (220, 220, 220),     # Off-white for text
    'text_highlight': (255, 255, 150),  # Highlighted text
    'button': (60, 60, 100),     # Button base color
    'button_hover': (80, 80, 120),  # Button hover color
    'button_click': (100, 100, 140),  # Button click color
    
    # Game element colors
    'player': (50, 100, 200),    # Player color
    'enemy': (200, 50, 50),      # Basic enemy color
    'bullet': (220, 220, 50),    # Player bullet color
    'special': (200, 100, 255),  # Special ability color
    
    # Enemy type colors
    'normal_enemy': (200, 50, 50),     # Normal enemy
    'fast_enemy': (50, 100, 255),      # Fast enemy
    'tank_enemy': (150, 50, 150),      # Tank enemy
    'ranged_enemy': (255, 150, 50),    # Ranged enemy
    'boss_enemy': (255, 50, 100),      # Boss enemy
    
    # Health and damage colors
    'health': (50, 200, 50),     # Health bar/healing
    'damage': (200, 50, 50),     # Damage indicators
    'shield': (50, 150, 255),    # Shield/armor
    
    # Currency and score colors
    'gold': (255, 215, 0),        # Gold/coin color
    'yellow_dark': (190, 160, 0),  # Darker gold for borders
    'xp': (100, 255, 100),        # Experience points color
    'score': (255, 200, 100),     # Score color
    
    # World colors
    'grid': (60, 60, 80),         # Grid lines for the world map
    'ground': (40, 40, 60),       # Ground color for the world
    
    # Additional UI element colors (keep legacy names for compatibility)
    'dark_green': (0, 100, 0),
    'dark_blue': (0, 0, 100),
    'blue': (20, 120, 220),
    'purple': (150, 50, 200),
    'pink': (220, 100, 150),
    'orange': (240, 140, 40),
    'accent': (100, 200, 255),
}

# Base game mechanic constants
BASE_XP_REQUIREMENT = 100  # Base XP needed to level up
XP_LEVEL_MULTIPLIER = 1.2  # Multiplier for XP needed per level

# UI constants
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
SMALL_BUTTON_WIDTH = 100
SMALL_BUTTON_HEIGHT = 40

# Gameplay constants
PLAYER_BASE_STATS = {
    'health': 100,
    'speed': 3.0,
    'damage': 10,
    'fire_rate': 250,  # ms between shots
    'bullet_speed': 8,
    'bullet_size': 5,
    'bullet_spread': 5,  # in degrees
}

# Enemy stat multipliers (relative to base enemy)
ENEMY_TYPE_MULTIPLIERS = {
    'normal': {
        'health': 1.0,
        'speed': 1.0,
        'damage': 1.0,
        'score': 1.0,
        'coin': 1.0,
    },
    'fast': {
        'health': 0.7,
        'speed': 2.0,
        'damage': 0.5,
        'score': 1.5,
        'coin': 2.0,
    },
    'tank': {
        'health': 2.0,
        'speed': 0.7,
        'damage': 1.5,
        'score': 2.0,
        'coin': 3.0,
    },
    'ranged': {
        'health': 0.8,
        'speed': 1.2,
        'damage': 1.5,
        'score': 3.0,
        'coin': 4.0,
    },
    'boss': {
        'health': 5.0,
        'speed': 0.8,
        'damage': 2.5,
        'score': 10.0,
        'coin': 10.0,
    },
}

# Drop chances for different items (0-1 probability)
DROP_CHANCES = {
    'coin': 0.5,      # 50% chance of coin drop
    'health': 0.15,   # 15% chance of health drop
    'damage': 0.1,    # 10% chance of damage boost
    'speed': 0.1,     # 10% chance of speed boost
    'attack_speed': 0.1,  # 10% chance of attack speed boost
}

# World settings
WORLD_SIZE = 2000  # Default world size in pixels
SPAWN_MARGIN = 250  # Margin for enemy spawning outside screen

# Window defaults (fallback if config fails)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Wave timing
WAVE_DELAY = 8000  # ms between waves
ENEMY_SPAWN_INTERVAL = 500  # ms between enemy spawns in a wave

# Default control keys (actual bindings should come from config)
DEFAULT_CONTROLS = {
    'move_up': pygame.K_w,
    'move_down': pygame.K_s,
    'move_left': pygame.K_a,
    'move_right': pygame.K_d,
    'shoot': 1,  # Left mouse button
    'special': 3,  # Right mouse button
    'shop': pygame.K_e,
    'pause': pygame.K_ESCAPE,
}

# UI Scale
UI_SCALE = WINDOW_WIDTH / 1920
BASE_FONT_SIZE = int(36 * UI_SCALE)

# Button sizes
BUTTON_SIZES = {
    'large': (int(300 * UI_SCALE), int(60 * UI_SCALE)),
    'medium': (int(200 * UI_SCALE), int(50 * UI_SCALE)),
    'small': (int(150 * UI_SCALE), int(40 * UI_SCALE))
}

# Padding
PADDING = int(20 * UI_SCALE)

# Paths
FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "Amiri-Regular.ttf")

# Game settings
FIRST_WAVE_DELAY = 180  # 3 seconds at 60 FPS
WAVE_DURATION = 1800    # 30 seconds at 60 FPS

# World drop spawn intervals (in milliseconds)
WORLD_DROP_INTERVALS = {
    'coin': 30000,    # Every 30 seconds
    'upgrade': 60000  # Every 60 seconds
}

# Shop purchase limits
SHOP_PURCHASE_LIMITS = {
    'max_health': 8,    # Increased from 5
    'damage': 5,        # Increased from 3
    'speed': 5,         # Increased from 3
    'attack_speed': 5   # Increased from 3
}

# Level up bonuses
LEVEL_UP_BONUSES = {
    'health': 25,   # +25 health per level
    'damage': 5,    # +5 damage per level
    'speed': 0.2,   # +0.2 speed per level
    'cooldown': 10  # Reduce cooldown by 10 frames per level
}

# XP and progression
XP_SCALE_FACTOR = 1.2
XP_AWARDS = {
    'normal': 25,
    'fast': 35,
    'tank': 50,
    'boss': 75
}

# Enemy spawn rates
ENEMY_SPAWN_RATES = {
    'normal': 0.5,   # 50% chance for normal enemies
    'fast': 0.2,     # 20% chance for fast enemies
    'tank': 0.15,    # 15% chance for tank enemies
    'ranged': 0.15   # 15% chance for ranged enemies
}

# Shop items with costs
SHOP_ITEMS = [
    {
        'name': 'Max Health +20',
        'cost': 50,
        'action': 'buy_max_health'
    },
    {
        'name': 'Damage +10%',
        'cost': 75,
        'action': 'buy_damage_boost'
    },
    {
        'name': 'Speed +10%',
        'cost': 60,
        'action': 'buy_speed_boost'
    },
    {
        'name': 'Attack Speed +10%',
        'cost': 80,
        'action': 'buy_attack_speed_boost'
    }
]

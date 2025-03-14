import pygame
import os
import sys
import math
import random
import time
import logging

# Core game entities
from entities.player import Player
from entities.enemy import Enemy
from entities.drop import Drop
from entities.projectile import PlayerProjectile, EnemyProjectile, SpecialProjectile
from world.world_map import WorldMap

# UI components
from ui.button import Button
from ui.floating_text import FloatingText
from ui.hud import HUD
from ui.upgrades import UpgradeSystem
from ui.shop import Shop

# Utilities
from utils.constants import *
from utils.debug import DummyDebugger

# Define world drop intervals (in milliseconds)
WORLD_DROP_INTERVALS = {
    'coin': 15000,    # 15 seconds
    'upgrade': 30000  # 30 seconds
}

class Game:
    """
    Main Game class that handles the game loop, state management,
    and coordinates all game elements.
    
    This class is responsible for:
    - Initializing the game world and entities
    - Running the main game loop
    - Handling user input
    - Managing game state
    - Coordinating rendering
    - Handling wave progression and difficulty
    """
    
    def __init__(self, screen_width=1280, screen_height=720):
        """
        Initialize the game with the given screen dimensions.
        
        Args:
            screen_width (int): Width of the game window
            screen_height (int): Height of the game window
        """
        # Initialize pygame
        pygame.init()
        pygame.font.init()
        
        # Set up display
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Tank Game")
        
        # Initialize game state variables
        self.state = "menu"  # menu, playing, paused, game_over
        self.shop_open = False
        self.paused = False
        
        # Initialize wave-related variables
        self.wave_number = 0
        self.enemies_in_wave = 0
        self.enemies_killed_this_wave = 0
        self.wave_in_progress = False
        
        # Initialize player-related variables
        self.player_experience = 0
        self.required_xp = 100
        self.level = 1
        self.score = 0
        self.coins = 0
        self.kills = 0
        
        # Initialize game object lists
        self.enemies = []
        self.projectiles = []
        self.drops = []
        self.floating_texts = []
        
        # Initialize timers
        self.last_update_time = pygame.time.get_ticks()
        self.wave_start_time = 0
        self.last_enemy_spawn_time = 0
        
        # Set up logger for the Game class
        self.logger = logging.getLogger("TankGame.Game")
        self.logger.info("Initializing game...")
        
        # Store window dimensions consistently
        self.WINDOW_WIDTH = screen_width
        self.WINDOW_HEIGHT = screen_height
        
        # Game state initialization
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.game_started = False
        self.is_counting_down = False
        self.level_up_screen = False
        
        # Initialize world drop timers
        self.last_coin_spawn = pygame.time.get_ticks()
        self.last_upgrade_spawn = pygame.time.get_ticks()
        
        # Start first wave in playing state, not in menu
        if self.state == "playing":
            self.spawn_wave()
            
        self.logger.info("Game initialization complete")
        
        try:
            # Initialize world
            self.logger.info("Creating world map...")
            self.world_map = WorldMap(2000, 2000)
            
            # Camera position
            self.camera_x = 0
            self.camera_y = 0
            
            # Special projectile settings
            self.special_projectile_unlocked = False
            self.special_cooldown = 2000
            self.last_special_shot = 0
            self.special_projectile_damage = 30
            self.special_projectile_speed = 10
            
            # Regular bullet settings
            self.bullet_cooldown = 250
            self.last_bullet_shot = 0
            self.bullet_spread = 5
            
            # Screen scaling
            self.fullscreen = False
            self.scale_factor_x = self.WINDOW_WIDTH / 1280
            self.scale_factor_y = self.WINDOW_HEIGHT / 720
            
            # Initialize game objects and UI
            self.init_game_objects()
            self.init_ui()
            
            # Initialize systems
            self.upgrade_system = UpgradeSystem(COLORS, self)
            self.hud = HUD(self)
            self.debugger = DummyDebugger()
            
            # Font initialization
            self.header_font = pygame.font.Font(None, 48)
            
            # Wave initialization
            self.is_spawning_wave = False
            self.spawn_queue = []
            self.next_wave_scheduled = False
            
            # Initialize world drop timers
            self.last_coin_spawn = pygame.time.get_ticks()
            self.last_upgrade_spawn = pygame.time.get_ticks()
            
            # Start first wave in playing state, not in menu
            if self.state == "playing":
                self.spawn_wave()
                
            self.logger.info("Game initialization complete")
            
        except Exception as e:
            self.logger.error(f"Error during game initialization: {e}")
            import traceback
            traceback.print_exc()
            raise

        self.debug_mode = False  # Add debug mode flag
        
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        if self.debug_mode:
            logging.info("Debug mode enabled")
        else:
            logging.info("Debug mode disabled")

    def run(self):
        """Main game loop with robust error handling"""
        try:
            # Initialize running state
            running = True
            self.last_update_time = pygame.time.get_ticks()
            
            # Ensure critical attributes exist
            if not hasattr(self, 'target_fps'):
                self.target_fps = 60
            if not hasattr(self, 'current_fps'):
                self.current_fps = 0
            if not hasattr(self, 'clock'):
                self.clock = pygame.time.Clock()
            
            # Add FPS tracking
            fps_counter = 0
            fps_timer = pygame.time.get_ticks()
            
            # Ensure state is initialized
            if not hasattr(self, 'state'):
                if hasattr(self, 'game_state'):
                    self.state = self.game_state
                else:
                    self.state = "menu"
                    
            # Main game loop
            while running:
                # Handle events (returns False if game should exit)
                if self.handle_events() == False:
                    running = False
                    break
                    
                # Update game state based on current state
                if self.state == "playing" and not getattr(self, 'paused', False):
                    try:
                        self.update_game()
                    except Exception as update_error:
                        self.logger.error(f"Error in update_game: {update_error}")
                
                # Draw current game state
                try:
                    self.draw()
                except Exception as draw_error:
                    self.logger.error(f"Error in draw method: {draw_error}")
                    
                    # Emergency fallback drawing to prevent black screen
                    try:
                        self.screen.fill((20, 20, 40))  # Dark background
                        font = pygame.font.Font(None, 36)
                        text = font.render("Drawing Error - Check Logs", True, (255, 0, 0))
                        self.screen.blit(text, (self.screen_width // 2 - 150, self.screen_height // 2))
                        pygame.display.flip()
                    except Exception as emergency_error:
                        self.logger.critical(f"Emergency drawing failed: {emergency_error}")
                
                # Calculate FPS
                fps_counter += 1
                current_time = pygame.time.get_ticks()
                if current_time - fps_timer > 1000:  # Update FPS every second
                    self.current_fps = fps_counter
                    fps_counter = 0
                    fps_timer = current_time
                    
                    # Log game state periodically
                    try:
                        self.logger.debug(f"FPS: {self.current_fps}, State: {self.state}, " +
                                        f"Enemies: {len(getattr(self, 'enemies', []))}, " +
                                        f"Player health: {getattr(getattr(self, 'player', None), 'health', 0)}")
                    except Exception as log_error:
                        self.logger.error(f"Error logging game state: {log_error}")
                
                # Cap frame rate - with safe fallback
                try:
                    self.clock.tick(self.target_fps)
                except Exception as tick_error:
                    self.logger.error(f"Error in clock.tick: {tick_error}")
                    # Manually sleep as fallback
                    pygame.time.delay(16)  # ~60fps
                
            # Game loop has ended
            self.logger.info("Game loop ended")
            
        except Exception as e:
            self.logger.critical(f"Fatal error in game loop: {e}")
            import traceback
            self.logger.critical(traceback.format_exc())

    def init_game_objects(self):
        """Initialize game objects"""
        try:
            # Create player at center of world
            self.player = Player(self.world_map.width // 2, self.world_map.height // 2)
            
            # Initialize game object lists
            self.enemies = []
            self.special_projectiles = []
            self.enemy_projectiles = []
            self.drops = []
            self.walls = []
            self.floating_texts = []
            
            # Set camera to follow player immediately
            self.world_map.update_camera(self.player.pos[0], self.player.pos[1])
            self.camera_x = self.world_map.camera_x
            self.camera_y = self.world_map.camera_y
            
            # Initialize player position reference - use a copy to avoid reference issues
            self.player_pos = self.player.pos.copy()
            
            # Spawn player in the center of the map
            print(f"Player spawned at world center: {self.player.pos}")
            
        except Exception as e:
            print(f"Error in init_game_objects: {e}")
            import traceback
            traceback.print_exc()

    def init_ui(self):
        """Initialize UI elements"""
        try:
            # Set up main menu buttons
            button_width = 200
            button_height = 50
            button_margin = 20
            
            # Calculate positions
            center_x = self.screen_width // 2
            start_y = 300
            
            # Create menu buttons
            self.menu_buttons = {
                'start': Button(
                    center_x - button_width // 2,
                    start_y,
                    button_width,
                    button_height,
                    "Start Game",
                    COLORS['button']
                ),
                'options': Button(
                    center_x - button_width // 2,
                    start_y + button_height + button_margin,
                    button_width,
                    button_height,
                    "Options",
                    COLORS['button']
                ),
                'quit': Button(
                    center_x - button_width // 2,
                    start_y + 2 * (button_height + button_margin),
                    button_width,
                    button_height,
                    "Quit",
                    COLORS['button']
                )
            }
            
            # Set up pause menu buttons
            pause_center_x = self.screen_width // 2
            pause_start_y = self.screen_height // 2
            
            self.pause_buttons = {
                'resume': Button(
                    pause_center_x - button_width // 2,
                    pause_start_y,
                    button_width,
                    button_height,
                    "Resume",
                    COLORS['button']
                ),
                'options': Button(
                    pause_center_x - button_width // 2,
                    pause_start_y + button_height + button_margin,
                    button_width,
                    button_height,
                    "Options",
                    COLORS['button']
                ),
                'quit': Button(
                    pause_center_x - button_width // 2,
                    pause_start_y + 2 * (button_height + button_margin),
                    button_width,
                    button_height,
                    "Quit to Menu",
                    COLORS['button']
                )
            }
            
            # Create shop button (in top-right corner)
            shop_button_size = 40
            shop_button_margin = 10
            self.shop_button = Button(
                self.screen_width - shop_button_size - shop_button_margin,
                shop_button_margin,
                shop_button_size,
                shop_button_size,
                "$",
                COLORS['gold'],
                'small'
            )
            
            # Create debug toggle button (small button in bottom-right)
            debug_button_size = 30
            self.debug_button = Button(
                self.screen_width - debug_button_size - 10,
                self.screen_height - debug_button_size - 10,
                debug_button_size,
                debug_button_size,
                "D",
                COLORS['ui_border'],
                'small'
            )
            
            # Set up HUD
            from ui.hud import HUD
            self.hud = HUD(self)
            
            print("UI elements initialized successfully")
            
        except Exception as e:
            print(f"Error in init_ui: {e}")
            import traceback
            traceback.print_exc()

    def init_constants(self):
        """Initialize game constants and variables"""
        try:
            from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, WORLD_SIZE, WORLD_DROP_INTERVALS
            
            # Store a reference to constants
            self.COLORS = COLORS
            
            # Frame rate control
            self.target_fps = 60  # Target frame rate
            self.current_fps = 0  # Current actual frame rate
            
            # Set up world drop intervals
            self.coin_drop_interval = WORLD_DROP_INTERVALS['coin'] / 1000  # Convert from ms to seconds
            self.upgrade_drop_interval = WORLD_DROP_INTERVALS['upgrade'] / 1000  # Convert from ms to seconds
            
            # Initialize drop timers
            self.time_since_last_coin = 0
            self.time_since_last_upgrade = 0
            
            # Create a world map with double the default size
            from world.world_map import WorldMap
            self.world_map = WorldMap(WORLD_SIZE, WORLD_SIZE)
            
            # Initialize camera position
            self.camera_x = self.world_map.width // 2
            self.camera_y = self.world_map.height // 2
            
            # Initialize main game lists
            self.enemies = []
            self.projectiles = []
            self.floating_texts = []
            self.drops = []
            
            # Initialize game state
            self.state = "menu"  # menu, playing, paused, game_over, shop
            self.debug_mode = False
            self.shop_open = False
            
            # Wave and progression tracking
            self.current_wave = 0
            self.wave_number = 0      # Legacy support for both wave variables
            self.wave_countdown = 3.0  # Countdown to first wave in seconds
            self.enemies_in_wave = 0
            self.enemies_killed_this_wave = 0
            self.wave_delay = 5.0  # Seconds between waves
            
            # Player stats and economy
            self.score = 0
            self.coins = 0
            self.kills = 0
            
            # Register successful initialization
            print("Game constants initialized")
            
        except Exception as e:
            print(f"Error in init_constants: {e}")
            import traceback
            traceback.print_exc()
            
            # Add critical defaults even if constants loading fails
            if not hasattr(self, 'target_fps'):
                self.target_fps = 60
            if not hasattr(self, 'current_fps'):
                self.current_fps = 0
            if not hasattr(self, 'state'):
                self.state = "menu"
            raise

    def handle_menu(self, event):
        """Handle menu input with robust error handling"""
        try:
            # Handle mouse clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if any menu button was clicked
                if hasattr(self, 'menu_buttons'):
                    # Start button
                    if hasattr(self.menu_buttons, 'get') and 'start' in self.menu_buttons:
                        if self.menu_buttons['start'].rect.collidepoint(mouse_pos):
                            self.reset_game()
                            self.state = "playing"
                            return
                    
                    # Quit button
                    if hasattr(self.menu_buttons, 'get') and 'quit' in self.menu_buttons:
                        if self.menu_buttons['quit'].rect.collidepoint(mouse_pos):
                            return False  # Exit game
                else:
                    # Fallback button detection if menu_buttons doesn't exist
                    start_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 - 25, 200, 50)
                    quit_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 50, 200, 50)
                    
                    if start_rect.collidepoint(mouse_pos):
                        self.reset_game()
                        self.state = "playing"
                        return
                    
                    if quit_rect.collidepoint(mouse_pos):
                        return False  # Exit game
                    
            # Also allow pressing Enter to start
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.reset_game()
                self.state = "playing"
                
        except Exception as e:
            self.logger.error(f"Error handling menu input: {e}")
            
            # Emergency fallback - any click starts the game
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.reset_game()
                self.state = "playing"

    def handle_paused_input(self, event):
        """Handle paused game input events"""
        try:
            if self.pause_buttons['resume'].handle_event(event):
                self.state = "playing"
            elif self.pause_buttons['quit'].handle_event(event):
                self.state = "menu"
            return True
        except Exception as e:
            logging.error(f"Error handling paused input: {e}")
            return True

    def handle_playing_input(self, event):
        """Handle gameplay input events"""
        try:
            # Handle keyboard events
            if event.type == pygame.KEYDOWN:
                # Pause game with escape
                if event.key == pygame.K_ESCAPE:
                    self.state = "paused"
                    return True
                    
                # Toggle shop with E key
                if event.key == pygame.K_e:
                    self.toggle_shop()
                    return True
                    
                # Toggle debug mode with F3
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                    print(f"Debug mode: {'enabled' if self.debug_mode else 'disabled'}")
                    return True
                    
            # Handle mouse events
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Handle left click (shooting)
                if event.button == 1:  # Left mouse button
                    if self.shop_open and hasattr(self, 'shop'):
                        # Pass click to shop if open
                        if self.shop.handle_click(pos):
                            return True
                    else:
                        # Otherwise shoot
                        self.shoot_projectile()
                        return True
                
                # Handle right click (special attack)
                if event.button == 3:  # Right mouse button
                    if not self.shop_open:
                        self.shoot_special_projectile()
                        return True
            
            return True
        except Exception as e:
            logging.error(f"Error handling playing input: {e}")
            return True

    def toggle_shop(self):
        """Toggle shop open/closed state"""
        try:
            if not hasattr(self, 'shop_open'):
                self.shop_open = False
                
            self.shop_open = not self.shop_open
            
            if self.shop_open:
                # Initialize shop if it doesn't exist
                if not hasattr(self, 'shop'):
                    from ui.shop import Shop
                    self.shop = Shop(self, self.screen_width, self.screen_height)
                print("Shop opened")
            else:
                print("Shop closed")
                
            return self.shop_open
        except Exception as e:
            print(f"Error toggling shop: {e}")
            return False

    def update_game(self):
        """Update game state and objects"""
        try:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_update_time) / 1000.0
            self.last_update_time = current_time
            
            # Skip updates if not in playing state
            if self.state != "playing":
                return
            
            # Update camera if player exists
            if hasattr(self, 'player') and self.player and hasattr(self, 'world_map') and self.world_map:
                try:
                    self.world_map.update_camera(self.player.pos[0], self.player.pos[1])
                except Exception as e:
                    logging.error(f"Error updating camera: {e}")
            
            # Update player movement based on keys
            try:
                self.handle_player_movement()
            except Exception as e:
                logging.error(f"Error handling player movement: {e}")
            
            # Update player if it exists
            if hasattr(self, 'player') and self.player:
                try:
                    self.player.update(dt)
                except Exception as e:
                    logging.error(f"Error updating player: {e}")
            
            # Update enemies
            try:
                if hasattr(self, 'enemies'):
                    self.update_enemies(dt)
            except Exception as e:
                logging.error(f"Error updating enemies: {e}")
            
            # Update projectiles
            try:
                self.update_projectiles()
            except Exception as e:
                logging.error(f"Error updating projectiles: {e}")
            
            # Update drops and pickups
            try:
                self.update_drops()
            except Exception as e:
                logging.error(f"Error updating drops: {e}")
            
            # Update wave state
            try:
                self.update_wave()
            except Exception as e:
                logging.error(f"Error updating wave: {e}")
            
            # Update floating texts
            try:
                self.update_floating_texts(dt)
            except Exception as e:
                logging.error(f"Error updating floating texts: {e}")
            
            # Check for collisions
            try:
                self.check_collisions()
            except Exception as e:
                logging.error(f"Error checking collisions: {e}")
            
            # Update UI elements
            if hasattr(self, 'hud'):
                self.hud.update(dt)
            
            # Check for shop interactions
            if self.shop_open and hasattr(self, 'shop'):
                # Shop logic here
                pass
        except Exception as e:
            logging.error(f"Error updating game: {e}")
            import traceback
            traceback.print_exc()

    def draw(self):
        """Draw the current state of the game"""
        try:
            # Clear the screen
            self.screen.fill(COLORS.get('background', (20, 20, 40)))
            
            # Get the current state (handle both state and game_state attributes)
            current_state = getattr(self, 'state', None)
            if current_state is None:
                current_state = getattr(self, 'game_state', 'menu')
            
            # Draw based on current state
            if current_state == "menu":
                self.draw_menu()
            elif current_state == "playing":
                # Draw game world
                if hasattr(self, 'world_map'):
                    self.world_map.draw(self.screen)
                
                # Draw game elements
                self.draw_game()
                
                # Draw shop if open
                if hasattr(self, 'shop_open') and self.shop_open and hasattr(self, 'shop'):
                    self.shop.draw(self.screen)
                    
            elif current_state == "paused":
                # First draw the game (as background)
                if hasattr(self, 'world_map'):
                    self.world_map.draw(self.screen)
                self.draw_game()
                
                # Then draw pause overlay
                self.draw_pause_menu()
                
            elif current_state == "game_over":
                # First draw the game (as background, darkened)
                if hasattr(self, 'world_map'):
                    self.world_map.draw(self.screen)
                self.draw_game()
                
                # Then draw game over screen
                self.draw_game_over()
            
            # Draw emergency debug info if in debug mode
            if getattr(self, 'debug_mode', False):
                try:
                    self.draw_debug_info()
                except Exception as debug_error:
                    self.logger.error(f"Error drawing debug info: {debug_error}")
            
            # Update display
            pygame.display.flip()
            
        except Exception as e:
            self.logger.error(f"Error in draw method: {e}")
            # If there's an error, just try to refresh the screen
            try:
                pygame.display.flip()
            except:
                pass

    def start_countdown(self):
        """Start a countdown before game starts"""
        self.countdown_timer = 3
        self.countdown_active = True
        
    def update_countdown(self):
        """Update countdown and check if it's complete"""
        if not self.countdown_active:
            return False
            
        self.countdown_timer -= 1/60  # Assuming 60 FPS
        
        # Create countdown text at center of screen
        if int(self.countdown_timer) != self.last_count:
            self.last_count = int(self.countdown_timer)
            
            if self.last_count > 0:
                self.floating_texts.append(
                    FloatingText(
                        str(self.last_count),
                        position=(self.screen_width // 2, self.screen_height // 2),
                        color=COLORS['white'],
                        size=72,
                        lifetime=60,
                        is_screen_position=True
                    )
                )
            else:
                self.floating_texts.append(
                    FloatingText(
                        "GO!",
                        position=(self.screen_width // 2, self.screen_height // 2),
                        color=COLORS['green'],
                        size=72,
                        lifetime=60,
                        is_screen_position=True
                    )
                )
                self.countdown_active = False
                return True
                
        return False

    def draw_menu(self):
        """Draw the main menu with robust error handling"""
        try:
            # Fill background
            self.screen.fill(COLORS.get('background', (20, 20, 40)))
            
            # Draw game title
            title_font = pygame.font.Font(None, 72)
            title_text = title_font.render("TANK GAME", True, COLORS.get('white', (255, 255, 255)))
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
            self.screen.blit(title_text, title_rect)
            
            # Draw menu buttons
            if hasattr(self, 'menu_buttons'):
                for button in self.menu_buttons.values():
                    if hasattr(button, 'draw'):
                        button.draw(self.screen)
            else:
                # Fallback buttons if menu_buttons doesn't exist
                font = pygame.font.Font(None, 36)
                
                # Start button
                start_text = font.render("Start Game", True, COLORS.get('white', (255, 255, 255)))
                start_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 - 25, 200, 50)
                pygame.draw.rect(self.screen, COLORS.get('button', (60, 60, 100)), start_rect)
                pygame.draw.rect(self.screen, COLORS.get('white', (255, 255, 255)), start_rect, 2)
                self.screen.blit(start_text, start_text.get_rect(center=start_rect.center))
                
                # Quit button
                quit_text = font.render("Quit", True, COLORS.get('white', (255, 255, 255)))
                quit_rect = pygame.Rect(self.screen_width // 2 - 100, self.screen_height // 2 + 50, 200, 50)
                pygame.draw.rect(self.screen, COLORS.get('button', (60, 60, 100)), quit_rect)
                pygame.draw.rect(self.screen, COLORS.get('white', (255, 255, 255)), quit_rect, 2)
                self.screen.blit(quit_text, quit_text.get_rect(center=quit_rect.center))
            
            # Draw version info
            version_font = pygame.font.Font(None, 20)
            version_text = version_font.render("Version 1.0", True, COLORS.get('white', (255, 255, 255)))
            self.screen.blit(version_text, (10, self.screen_height - 30))
            
        except Exception as e:
            self.logger.error(f"Error drawing menu: {e}")
            
            # Emergency fallback
            try:
                self.screen.fill((20, 20, 40))
                font = pygame.font.Font(None, 36)
                text = font.render("TANK GAME", True, (255, 255, 255))
                self.screen.blit(text, (self.screen_width // 2 - 100, self.screen_height // 2 - 50))
                
                start_text = font.render("Click anywhere to start", True, (255, 255, 255))
                self.screen.blit(start_text, (self.screen_width // 2 - 150, self.screen_height // 2 + 50))
            except:
                pass

    def draw_game(self):
        """Draw all game elements while playing"""
        try:
            # Draw the world (already drawn in the main draw method)
            
            # Get camera position (should follow player)
            if hasattr(self, 'player') and self.player:
                self.camera_x = self.player.pos[0]
                self.camera_y = self.player.pos[1]
            
            # Draw drops
            try:
                self.draw_drops()
            except Exception as e:
                self.logger.error(f"Error drawing drops: {e}")
            
            # Draw enemies
            try:
                if hasattr(self, 'enemies'):
                    for enemy in self.enemies:
                        if self.is_visible(enemy):
                            # Convert world position to screen position
                            screen_pos = self.world_to_screen(enemy.pos[0], enemy.pos[1])
                            enemy.draw_at_screen_pos(self.screen, screen_pos)
            except Exception as e:
                self.logger.error(f"Error drawing enemies: {e}")
            
            # Draw projectiles
            try:
                if hasattr(self, 'projectiles'):
                    for projectile in self.projectiles:
                        if hasattr(projectile, 'pos'):
                            screen_pos = self.world_to_screen(projectile.pos[0], projectile.pos[1])
                            projectile.draw_at_screen_pos(self.screen, screen_pos)
            except Exception as e:
                self.logger.error(f"Error drawing projectiles: {e}")
            
            # Draw player
            try:
                self.draw_player()
            except Exception as e:
                self.logger.error(f"Error drawing player: {e}")
            
            # Draw floating texts
            try:
                if hasattr(self, 'floating_texts'):
                    for text in self.floating_texts:
                        # Convert world position to screen position
                        screen_x, screen_y = self.world_to_screen(text.x, text.y)
                        text.draw_at_screen_pos(self.screen, (screen_x, screen_y))
            except Exception as e:
                self.logger.error(f"Error drawing floating texts: {e}")
            
            # Draw HUD
            try:
                if hasattr(self, 'hud'):
                    self.hud.draw(self.screen)
            except Exception as e:
                self.logger.error(f"Error drawing HUD: {e}")
            
            # Draw shop button
            try:
                if hasattr(self, 'shop_button'):
                    self.shop_button.draw(self.screen)
            except Exception as e:
                self.logger.error(f"Error drawing shop button: {e}")
            
            # Draw debug info if debug mode is enabled
            if hasattr(self, 'debug_mode') and self.debug_mode:
                try:
                    self.draw_debug_info()
                except Exception as e:
                    self.logger.error(f"Error drawing debug info: {e}")
        
        except Exception as e:
            self.logger.error(f"Error in draw_game method: {e}")
            # If the entire draw_game fails, at least try to draw basic elements
            if hasattr(self, 'player') and self.player:
                try:
                    screen_pos = self.world_to_screen(self.player.pos[0], self.player.pos[1])
                    pygame.draw.circle(self.screen, (255, 255, 255), screen_pos, 20)
                    
                    # Draw emergency debug text
                    font = pygame.font.Font(None, 24)
                    text = font.render("Drawing Error - Press F3 for debug info", True, (255, 0, 0))
                    self.screen.blit(text, (20, 20))
                except:
                    pass

    def draw_coin_counter(self):
        """Draw coin counter in the top-right corner"""
        # Create a coin icon
        coin_radius = 10
        coin_x = self.screen_width - 80
        coin_y = 30
        
        # Draw coin icon
        pygame.draw.circle(self.screen, COLORS['gold'], (coin_x, coin_y), coin_radius)
        pygame.draw.circle(self.screen, COLORS['yellow_dark'], (coin_x, coin_y), coin_radius, 2)
        
        # Draw coin count
        coin_font = pygame.font.Font(None, 28)
        coin_text = coin_font.render(f"x {self.coins}", True, COLORS['white'])
        self.screen.blit(coin_text, (coin_x + 15, coin_y - 10))

    def draw_pause_menu(self):
        """Draw the pause menu overlay"""
        try:
            # Draw pause overlay and pause buttons
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # More transparent overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw pause text
            font = pygame.font.Font(None, 74)
            pause_text = font.render("Paused", True, COLORS['white'])
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
            self.screen.blit(pause_text, text_rect)
            
            # Draw pause buttons
            for button in self.pause_buttons.values():
                button.draw(self.screen)
        except Exception as e:
            logging.error(f"Error drawing pause menu: {e}")

    def draw_game_over(self):
        """Draw game over screen"""
        try:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Darker overlay
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            font = pygame.font.Font(None, 96)
            game_over_text = font.render("GAME OVER", True, COLORS['red'])
            text_rect = game_over_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
            self.screen.blit(game_over_text, text_rect)
            
            # Statistics
            stats_font = pygame.font.Font(None, 36)
            
            # Waves survived
            waves_text = stats_font.render(f"Waves Survived: {self.current_wave}", True, COLORS['white'])
            waves_rect = waves_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(waves_text, waves_rect)
            
            # Kills
            kills_text = stats_font.render(f"Enemies Killed: {self.kills}", True, COLORS['white'])
            kills_rect = kills_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
            self.screen.blit(kills_text, kills_rect)
            
            # Score
            score_text = stats_font.render(f"Score: {self.score}", True, COLORS['gold'])
            score_rect = score_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
            self.screen.blit(score_text, score_rect)
            
            # Restart button
            restart_font = pygame.font.Font(None, 48)
            restart_text = restart_font.render("Press SPACE to Restart", True, COLORS['green'])
            restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 180))
            self.screen.blit(restart_text, restart_rect)
            
            # Quit button
            quit_font = pygame.font.Font(None, 36)
            quit_text = quit_font.render("Press ESC to Quit", True, COLORS['red'])
            quit_rect = quit_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 230))
            self.screen.blit(quit_text, quit_rect)
            
        except Exception as e:
            logging.error(f"Error drawing game over screen: {e}")

    def draw_player(self):
        """Draw player with proper turret aiming"""
        try:
            # Check if we should delegate to player's own draw method
            if hasattr(self.player, 'draw'):
                # Just return as the player class will handle drawing itself
                return
            
            # Fallback drawing if Player class doesn't have its own draw method
            # Get player screen position
            player_screen_x, player_screen_y = self.world_map.world_to_screen(self.player.pos[0], self.player.pos[1])
            
            # Draw tank body
            tank_width, tank_height = 40, 30
            body_rect = pygame.Rect(
                player_screen_x - tank_width // 2,
                player_screen_y - tank_height // 2,
                tank_width, tank_height)
            pygame.draw.rect(self.screen, COLORS['blue'], body_rect)
            
            # Draw tank treads
            pygame.draw.line(self.screen, COLORS['black'],
                            (player_screen_x - 20, player_screen_y - 15),
                            (player_screen_x - 20, player_screen_y + 15), 2)
            pygame.draw.line(self.screen, COLORS['black'],
                            (player_screen_x + 20, player_screen_y - 15),
                            (player_screen_x + 20, player_screen_y + 15), 2)
            
            # Get player aim direction - first try to use stored aim_angle
            if hasattr(self.player, 'aim_angle'):
                angle = self.player.aim_angle
            else:
                # Fallback - calculate angle from mouse position
                mouse_pos = pygame.mouse.get_pos()
                dx = mouse_pos[0] - player_screen_x
                dy = mouse_pos[1] - player_screen_y
                angle = math.atan2(dy, dx)
            
            # Draw turret
            turret_length = 30
            end_x = player_screen_x + turret_length * math.cos(angle)
            end_y = player_screen_y + turret_length * math.sin(angle)
            pygame.draw.line(self.screen, COLORS['dark_green'], 
                            (player_screen_x, player_screen_y), 
                            (end_x, end_y), 8)
            
        except Exception as e:
            print(f"Error in draw_player: {e}")
            # Emergency fallback - just draw a basic circle
            try:
                player_screen_x, player_screen_y = self.world_map.world_to_screen(self.player.pos[0], self.player.pos[1])
                pygame.draw.circle(self.screen, COLORS['blue'], (player_screen_x, player_screen_y), 20)
            except:
                pass

    def draw_enemy(self, enemy):
        """Draw an enemy at its world position"""
        try:
            # Check if enemy has its own draw method
            if hasattr(enemy, 'draw_at_screen_pos'):
                # Get screen position
                screen_pos = self.world_to_screen(enemy.pos[0], enemy.pos[1])
                
                # Only draw if on screen (with padding)
                if 0 <= screen_pos[0] <= self.screen_width + 50 and 0 <= screen_pos[1] <= self.screen_height + 50:
                    enemy.draw_at_screen_pos(self.screen, screen_pos)
                    
        except Exception as e:
            logging.error(f"Error drawing enemy: {e}")

    def draw_drops(self):
        """Draw all active drops"""
        for drop in self.drops:
            # Only draw drops that are visible on screen
            if self.world_map.is_on_screen(drop.world_pos[0], drop.world_pos[1]):
                # Convert world position to screen position
                screen_pos = self.world_map.world_to_screen(drop.world_pos[0], drop.world_pos[1])
                # Draw drop at screen position
                drop.draw_at_screen_pos(self.screen, screen_pos)

    def reset_game(self):
        """Reset game state for new game"""
        try:
            # Reset game state
            self.state = "playing"
            
            # Initialize game environment
            self.init_game_objects()
            
            # Reset game stats
            self.score = 0
            self.coins = 0
            self.kills = 0
            
            # Reset wave state
            self.current_wave = 0
            self.wave_number = 0
            self.wave_countdown = 3.0
            self.enemies_in_wave = 0
            self.enemies_killed_this_wave = 0
            
            # Reset shop state
            self.shop_open = False
            
            # Log game start
            logging.info("Game reset - new game started")
        except Exception as e:
            logging.error(f"Error resetting game: {e}")

    def award_kill(self, enemy):
        """Award player for killing an enemy"""
        # Get XP based on enemy type
        xp_gain = 20  # Base XP for killing an enemy
        self.player.add_experience(xp_gain)  # Changed from gain_experience to add_experience
        
        # Update player XP
        self.player.experience += xp_gain
        
        # Check for level up
        xp_to_next_level = BASE_XP_REQUIREMENT * self.level  # Use BASE_XP_REQUIREMENT
        if self.player.experience >= xp_to_next_level:
            self.level_up()
        
        # Show XP gain as floating text
        self.floating_texts.append(
            FloatingText(
                text=f"+{xp_gain} XP",
                position=(enemy.pos[0], enemy.pos[1] - 20),
                color=COLORS["green"]
            )
        )
        
        # Award coins based on enemy type
        coin_reward = getattr(enemy, 'gold_value', 1)  # Default to 1 if not specified
        self.coins += coin_reward  # Use self.coins consistently
        
        # Update player.coins to keep it in sync
        self.player.coins = self.coins
        
        # Show coin gain as floating text
        self.floating_texts.append(
            FloatingText(
                text=f"+{coin_reward} coins",
                position=(enemy.pos[0], enemy.pos[1] - 40),
                color=COLORS["gold"]
            )
        )
        
        # Add score - safely handle missing score attribute
        if not hasattr(self, 'score'):
            self.score = 0
        self.score += enemy.score_value if hasattr(enemy, 'score_value') else 50
        
        # Increment kill count
        self.kills += 1
        
        # Spawn drops at enemy position
        self.spawn_drops(enemy.pos[0], enemy.pos[1])

    def spawn_drops(self, x, y):
        """Spawn drops at the given position"""
        # Coin drops
        if random.random() < DROP_CHANCES['coin']:
            coin_value = random.randint(1, 3)
            coin_drop = Drop(x, y, 'coin', coin_value)
            self.drops.append(coin_drop)
            
            # Create floating text for coin drop
            text = f"+{coin_value} coins"
            self.floating_texts.append(
                FloatingText(
                    text=text,
                    position=(x, y),
                    color=COLORS['gold'],
                    size=20,
                    lifetime=60
                )
            )
        
        # Check other drop types
        for drop_type, chance in DROP_CHANCES.items():
            if drop_type != 'coin' and random.random() < chance:
                value = 1
                if drop_type == 'health':
                    value = random.randint(10, 25)
                elif drop_type in ['damage', 'speed', 'attack_speed']:
                    value = random.randint(5, 15) / 100  # Convert to percentage
                
                drop = Drop(x, y, drop_type, value)
                self.drops.append(drop)
                
                # Create appropriate floating text
                if drop_type == 'health':
                    text = f"+{value} HP"
                    color = COLORS['green']
                elif drop_type == 'damage':
                    text = f"+{int(value * 100)}% DMG"
                    color = COLORS['red']
                elif drop_type == 'speed':
                    text = f"+{int(value * 100)}% SPD"
                    color = COLORS['blue']
                elif drop_type == 'attack_speed':
                    text = f"+{int(value * 100)}% ATK SPD"
                    color = COLORS['yellow']
                else:
                    text = f"+{value} {drop_type.upper()}"
                    color = COLORS['white']
                
                self.floating_texts.append(
                    FloatingText(
                        text=text,
                        position=(x, y),
                        color=color,
                        size=20,
                        lifetime=60
                    )
                )

    def update_drops(self):
        """Update and process drops"""
        i = 0
        while i < len(self.drops):
            drop = self.drops[i]
            drop.lifetime -= 1
            
            # Remove expired drops
            if drop.lifetime <= 0:
                self.drops.pop(i)
                continue
                
            # Check if player collected the drop
            dx = self.player.pos[0] - drop.world_pos[0]
            dy = self.player.pos[1] - drop.world_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Update drop's bounce animation
            drop.bounce_time += drop.bounce_speed
            drop.bounce_offset = abs(math.sin(drop.bounce_time) * drop.bounce_height)
            
            if distance < self.player.radius + drop.pickup_radius:  # Use drop's pickup radius
                # Apply drop effect based on type
                if drop.drop_type == 'coin':
                    # Add coins to player
                    coin_value = drop.value
                    self.coins += coin_value
                    
                    # Add floating text for coins
                    self.floating_texts.append(FloatingText(
                        f"+{coin_value} coins",
                        self.player.pos[0],
                        self.player.pos[1] - 30,
                        COLORS['gold']
                    ))

    def level_up(self):
        """Level up the player and show upgrade options with improved reliability."""
        try:
            # Increase level
            self.level += 1
            
            # Keep player.level in sync
            if hasattr(self.player, 'level'):
                self.player.level = self.level
            
            # Reset player XP
            self.player_experience = 0
            if hasattr(self.player, 'xp'):
                self.player.xp = 0
            
            # Increase required XP for next level
            self.required_xp = int(self.required_xp * 1.2)  # 20% more XP required for next level
            
            # Keep player.xp_to_next_level in sync
            if hasattr(self.player, 'xp_to_next_level'):
                self.player.xp_to_next_level = self.required_xp
            
            # Show level up message
            self.floating_texts.append(
                FloatingText(
                    text=f"Level Up! {self.level}",
                    position=(self.player.pos[0], self.player.pos[1] - 50),
                    color=COLORS["yellow"]
                )
            )
            
            # Create a flag to track level up screen state
            self.level_up_screen = True
            
            # Set game state to upgrading and show upgrade panel
            self.state = "upgrading"
            
            # Make sure upgrade system exists
            if hasattr(self, 'upgrade_system') and self.upgrade_system:
                # Show upgrade options
                available_upgrades = self.upgrade_system.get_available_upgrades()
                self.upgrade_system.show_upgrades(available_upgrades)
                self.upgrade_system.show_upgrade_panel = True
            else:
                print("Warning: UpgradeSystem not available. Creating it now.")
                from ui.upgrades import UpgradeSystem
                self.upgrade_system = UpgradeSystem(COLORS, self)
                available_upgrades = self.upgrade_system.get_available_upgrades()
                self.upgrade_system.show_upgrades(available_upgrades)
                self.upgrade_system.show_upgrade_panel = True
            
            # Log level up event
            logging.info(f"Player leveled up to {self.level}. Next level at {self.required_xp} XP")
            
        except Exception as e:
            logging.error(f"Error in level_up: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency recovery - reset to playing state
            self.state = "playing"
            if hasattr(self, 'upgrade_system') and self.upgrade_system:
                self.upgrade_system.show_upgrade_panel = False
            self.level_up_screen = False

    def apply_upgrade(self, upgrade):
        """Apply the selected upgrade to the player with improved error handling."""
        try:
            logging.info(f"Applying upgrade: {upgrade}")
            
            if upgrade == "damage":
                # Increase damage by 10%
                current_damage = self.player.bullet_damage
                increase = current_damage * 0.1
                self.player.bullet_damage += increase
                self.floating_texts.append(
                    FloatingText(
                        text=f"+{increase:.1f} Damage",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["red"]
                    )
                )
                
            elif upgrade == "speed":
                # Increase speed by 10%
                current_speed = self.player.speed
                increase = current_speed * 0.1
                self.player.speed += increase
                self.floating_texts.append(
                    FloatingText(
                        text=f"+{increase:.1f} Speed",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["blue"]
                    )
                )
                
            elif upgrade == "max_health":
                # Increase max health by 10%
                current_max_health = self.player.max_health
                increase = current_max_health * 0.1
                self.player.max_health += increase
                # Also increase current health by the same amount
                self.player.health += increase
                self.floating_texts.append(
                    FloatingText(
                        text=f"+{increase:.1f} Max Health",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["green"]
                    )
                )
                
            elif upgrade == "attack_speed":
                # Increase attack speed by reducing fire rate delay by 10%
                current_delay = self.player.shoot_delay
                decrease = current_delay * 0.1
                # Ensure minimum delay of 200ms (5 shots per second max)
                self.player.shoot_delay = max(200, current_delay - decrease)
                self.floating_texts.append(
                    FloatingText(
                        text=f"+10% Attack Speed",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["yellow"]
                    )
                )
            
            # Return to playing state
            self.state = "playing"
            
            # Hide upgrade panel
            if hasattr(self, 'upgrade_system') and self.upgrade_system:
                self.upgrade_system.hide_upgrades()
                self.upgrade_system.show_upgrade_panel = False
            
            # Reset level up screen flag
            self.level_up_screen = False
            
        except Exception as e:
            logging.error(f"Error applying upgrade {upgrade}: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency recovery - return to playing state
            self.state = "playing"
            if hasattr(self, 'upgrade_system') and self.upgrade_system:
                self.upgrade_system.show_upgrade_panel = False
            self.level_up_screen = False

    def handle_upgrades(self, event):
        """Handle upgrade selection"""
        if not self.upgrade_system.show_upgrade_panel:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            upgrade = self.upgrade_system.check_click(mouse_pos)
            if upgrade:
                self.apply_upgrade(upgrade)
                self.upgrade_system.show_upgrade_panel = False
                self.state = "playing"  # Resume game after upgrade

    def handle_game_over(self, event):
        """Handle game over screen input"""
        try:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Go back to main menu on click
                self.state = "menu"
                return True
                
            # Also return to menu on any key press
            if event.type == pygame.KEYDOWN:
                self.state = "menu"
                return True
                
            return True
        except Exception as e:
            logging.error(f"Error handling game over input: {e}")
            # Emergency fallback
            self.state = "menu"
            return True

    def handle_click(self, pos):
        """Handle mouse click at the given position"""
        try:
            # Convert screen position to world coordinates
            world_x, world_y = self.screen_to_world(pos[0], pos[1])
            
            # Check if shop button was clicked
            if hasattr(self, 'shop_button') and self.shop_button.rect.collidepoint(pos):
                self.toggle_shop()
                return True
                
            # Check if debug button was clicked
            if hasattr(self, 'debug_button') and self.debug_button.rect.collidepoint(pos):
                self.debug_mode = not self.debug_mode
                print(f"Debug mode: {'on' if self.debug_mode else 'off'}")
                return True
                
            # If shop is open, check for shop interactions
            if self.shop_open and hasattr(self, 'shop'):
                if self.shop.handle_event({'type': 'click', 'pos': pos}):
                    return True
                    
            # Otherwise, treat as a shooting action
            return self.shoot_projectile()
            
        except Exception as e:
            print(f"Error handling click: {e}")
            return False

    def handle_events(self):
        """Handle all game events with robust error handling"""
        try:
            # Process all events
            for event in pygame.event.get():
                # Handle quit event
                if event.type == pygame.QUIT:
                    return False
                    
                # Handle key events
                if event.type == pygame.KEYDOWN:
                    # Global key handlers
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "paused"
                        elif self.state == "paused":
                            self.state = "playing"
                    
                    # Toggle debug mode with F3
                    if event.key == pygame.K_F3:
                        self.debug_mode = not self.debug_mode
                        self.logger.info(f"Debug mode: {self.debug_mode}")
                    
                    # Toggle shop with E key
                    if event.key == pygame.K_e and self.state == "playing":
                        self.toggle_shop()
                        
                    # Toggle fullscreen with Alt+Enter
                    if event.key == pygame.K_RETURN and (pygame.key.get_mods() & pygame.KMOD_ALT):
                        pygame.display.toggle_fullscreen()
                
                # Handle state-specific events
                if self.state == "menu":
                    self.handle_menu(event)
                elif self.state == "playing":
                    if self.shop_open:
                        # Handle shop events
                        if hasattr(self, 'shop') and hasattr(self.shop, 'handle_event'):
                            self.shop.handle_event(event)
                    else:
                        # Handle playing input
                        self.handle_playing_input(event)
                elif self.state == "paused":
                    self.handle_paused_input(event)
                elif self.state == "game_over":
                    self.handle_game_over(event)
            
            return True  # Continue running
            
        except Exception as e:
            self.logger.error(f"Error handling events: {e}")
            return True  # Continue running despite errors

    def spawn_world_drop(self, drop_type):
        """Spawn a random world drop"""
        try:
            from entities.drop import Drop
            
            # Get world dimensions
            if not hasattr(self, 'world_map'):
                print("No world map available for drop spawning")
                return
                
            # Calculate random position
            padding = 100  # Keep drops away from edge
            spawn_x = random.randint(padding, self.world_map.width - padding)
            spawn_y = random.randint(padding, self.world_map.height - padding)
            
            # Create appropriate drop
            if drop_type == 'coin':
                # Random coin value (1-5)
                value = random.randint(1, 5)
                drop = Drop(spawn_x, spawn_y, 'coin', value)
            else:
                # Upgrade drop
                upgrade_types = ['health', 'damage', 'speed', 'attack_speed']
                upgrade_type = random.choice(upgrade_types)
                drop = Drop(spawn_x, spawn_y, upgrade_type)
                
            # Add to drops list
            if not hasattr(self, 'drops'):
                self.drops = []
            self.drops.append(drop)
            
            print(f"Spawned {drop_type} drop at {spawn_x}, {spawn_y}")
            return drop
            
        except Exception as e:
            print(f"Error spawning world drop: {e}")
            return None

    def scale_position(self, x, y):
        """Scale world position to screen position"""
        if not hasattr(self, 'camera_x') or not hasattr(self, 'camera_y'):
            return x, y
            
        screen_x = int(x - self.camera_x + self.screen_width // 2)
        screen_y = int(y - self.camera_y + self.screen_height // 2)
        
        return screen_x, screen_y

    def scale_size(self, width, height):
        """Scale dimensions based on zoom level"""
        return int(width), int(height)

    def handle_player_movement(self):
        """Handle player movement with robust error handling"""
        try:
            # Check if player exists
            if not hasattr(self, 'player') or self.player is None:
                return
                
            # Get keyboard state
            keys = pygame.key.get_pressed()
            
            # Calculate movement direction
            dx, dy = 0, 0
            
            # WASD movement
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1
                
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                magnitude = (dx**2 + dy**2)**0.5
                dx /= magnitude
                dy /= magnitude
                
            # Apply player speed
            if hasattr(self.player, 'speed'):
                dx *= self.player.speed
                dy *= self.player.speed
            
            # Move player
            if hasattr(self.player, 'move'):
                self.player.move(dx, dy)
            else:
                # Fallback movement if move method doesn't exist
                if hasattr(self.player, 'pos'):
                    self.player.pos[0] += dx
                    self.player.pos[1] += dy
            
            # Check world boundaries
            if hasattr(self, 'world_map') and hasattr(self.world_map, 'check_boundaries'):
                self.world_map.check_boundaries(self.player)
            
            # Handle mouse aiming
            mouse_pos = pygame.mouse.get_pos()
            world_pos = self.screen_to_world(mouse_pos[0], mouse_pos[1])
            
            # Update player aim
            if hasattr(self.player, 'update_aim'):
                self.player.update_aim(world_pos)
            
            # Handle shooting
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:  # Left mouse button
                self.shoot_projectile()
            if mouse_buttons[2]:  # Right mouse button
                self.shoot_special_projectile()
            
        except Exception as e:
            self.logger.error(f"Error handling player movement: {e}")

    def spawn_wave(self):
        """Spawn a new wave of enemies"""
        try:
            self.wave_number += 1
            base_enemies = 3 + self.wave_number  # Increase enemies per wave
            self.enemies_in_wave = base_enemies  # Set the number of enemies in this wave
            self.enemies_killed_this_wave = 0
            
            print(f"Spawning wave {self.wave_number}")
            
            # Create wave announcement text centered on player's view
            self.floating_texts.append(
                FloatingText(
                    text=f"WAVE {self.wave_number}",
                    position=(self.player.pos[0], self.player.pos[1] - 100),
                    color=COLORS['yellow'],
                    size=48,
                    lifetime=180
                )
            )
            
            # Calculate number of enemies based on wave number (ensure integers)
            # Enhanced scaling logic for better difficulty progression
            base_enemies = max(3, self.wave_number * 2)  # At least 3 enemies, increasing by 2 per wave
            
            # Calculate enemy distribution
            num_normal = max(3, int(base_enemies * 0.4))  # 40% normal enemies, at least 3
            num_fast = max(0, int(base_enemies * 0.3))    # 30% fast enemies
            num_tank = max(0, int(base_enemies * 0.15))   # 15% tank enemies
            num_ranged = max(0, int(base_enemies * 0.15)) # 15% ranged enemies
            
            # Add boss every 5 waves
            has_boss = self.wave_number % 5 == 0 and self.wave_number > 0
            
            # Add special wave types for variety
            is_special_wave = False
            if not has_boss and self.wave_number > 3 and random.random() < 0.3:  # 30% chance for special wave
                wave_type = random.choice(["fast", "tank", "ranged", "mixed"])
                
                if wave_type == "fast":
                    num_normal //= 2
                    num_fast *= 2
                    num_tank //= 2
                    num_ranged //= 2
                    is_special_wave = True
                    self.floating_texts.append(
                        FloatingText(
                            text="FAST ENEMY RUSH!",
                            position=(self.player.pos[0], self.player.pos[1] - 70),
                            color=COLORS['blue'],
                            size=36,
                            lifetime=180
                        )
                    )
            
            # Spawn enemies with these counts
            # Keep track of enemies spawned for wave completion tracking
            self.enemies_in_wave = num_normal + num_fast + num_tank + num_ranged
            if has_boss:
                self.enemies_in_wave += 1
                
            # Actually spawn the enemies now
            self._spawn_enemies(num_normal, "normal")
            self._spawn_enemies(num_fast, "fast")
            self._spawn_enemies(num_tank, "tank")
            self._spawn_enemies(num_ranged, "ranged")
            
            if has_boss:
                # Boss spawns directly in player's view for dramatic effect
                boss_x = self.player.pos[0] + random.randint(300, 400) * random.choice([-1, 1])
                boss_y = self.player.pos[1] + random.randint(300, 400) * random.choice([-1, 1])
                
                # Ensure boss is within world bounds
                if hasattr(self, 'world_map'):
                    boss_x = max(50, min(boss_x, self.world_map.width - 50))
                    boss_y = max(50, min(boss_y, self.world_map.height - 50))
                    
                self.create_enemy("boss", boss_x, boss_y)
                
                # Dramatic boss announcement
                self.floating_texts.append(
                    FloatingText(
                        text="BOSS APPROACHING!",
                        position=(self.player.pos[0], self.player.pos[1] - 50),
                        color=COLORS['red'],
                        size=42,
                        lifetime=180
                    )
                )
                
            # Update wave stats
            self.wave_number += 1
            self.enemies_killed_this_wave = 0
            
            print(f"Wave {self.wave_number} spawned with {self.enemies_in_wave} enemies")
            
            # Reset the next_wave_scheduled flag as we're spawning now
            self.next_wave_scheduled = False
            
        except Exception as e:
            print(f"Error in spawn_wave: {e}")
            # Log the full error for debugging
            import traceback
            traceback.print_exc()
            
    def update_wave(self):
        """Update wave status, handle spawning of enemies, and check wave completion"""
        try:
            # Check if no enemies left in the current wave and not currently spawning
            current_time = pygame.time.get_ticks()
            
            # Handle gradual enemy spawning
            if self.is_spawning_wave and len(self.spawn_queue) > 0:
                # Check if it's time to spawn another enemy
                if current_time - self.last_enemy_spawn_time > self.enemy_spawn_interval:
                    # Get next enemy from queue
                    enemy_type, x, y = self.spawn_queue.pop(0)
                    
                    # Spawn the enemy
                    self.create_enemy(enemy_type, x, y)
                    
                    # Update last spawn time
                    self.last_enemy_spawn_time = current_time
                    
                    # If this was the last enemy, set spawning flag to false
                    if len(self.spawn_queue) == 0:
                        self.is_spawning_wave = False
            
            # Check for wave completion (all enemies dead)
            if not self.is_spawning_wave and len(self.spawn_queue) == 0:
                self.check_wave_completion()
                
            # Check if it's time to trigger next wave
            self.trigger_next_wave(current_time)
        except Exception as e:
            logging.error(f"Error updating wave status: {e}")
            import traceback
            traceback.print_exc()

    def update_projectiles(self):
        """Update all projectiles in the game"""
        try:
            # Skip if projectiles list doesn't exist
            if not hasattr(self, 'projectiles'):
                self.projectiles = []
                return
                
            # Get world bounds
            world_bounds = None
            if hasattr(self, 'world_map'):
                world_bounds = (0, 0, self.world_map.width, self.world_map.height)
                
            # Update each projectile and remove if no longer active
            for i in range(len(self.projectiles) - 1, -1, -1):
                projectile = self.projectiles[i]
                
                # Skip if projectile doesn't have update method
                if not hasattr(projectile, 'update'):
                    self.projectiles.pop(i)
                    continue
                    
                # Update projectile
                result = projectile.update(world_bounds)
                
                # Remove if not active
                if not result:
                    self.projectiles.pop(i)
                    
        except Exception as e:
            logging.error(f"Error updating projectiles: {e}")
            import traceback
            traceback.print_exc()

    def update_enemies(self, dt):
        """Update all enemies in the game"""
        try:
            # Skip if enemies list doesn't exist
            if not hasattr(self, 'enemies'):
                self.enemies = []
                return
                
            # Skip if player doesn't exist
            if not hasattr(self, 'player') or not self.player:
                return
                
            # Keep track of enemies to remove
            enemies_to_remove = []
            
            # Update each enemy
            for enemy in self.enemies:
                if hasattr(enemy, 'update'):
                    # Skip enemies that are far from player
                    dx = enemy.pos[0] - self.player.pos[0]
                    dy = enemy.pos[1] - self.player.pos[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Only update enemies within active range
                    if distance < 2000:  # Adjust this value for performance
                        enemy.update(dt, self.player.pos)
                        
                        # Check if enemy should shoot
                        if hasattr(enemy, 'should_shoot') and enemy.should_shoot():
                            try:
                                # Only shoot if on screen
                                screen_pos = self.world_to_screen(enemy.pos[0], enemy.pos[1])
                                if 0 <= screen_pos[0] <= self.screen_width and 0 <= screen_pos[1] <= self.screen_height:
                                    if hasattr(enemy, 'shoot'):
                                        enemy.shoot(self.player.pos)
                            except Exception as e:
                                logging.error(f"Error during enemy shooting: {e}")
                
                # Check if enemy should be removed
                if hasattr(enemy, 'health') and enemy.health <= 0:
                    if not enemy in enemies_to_remove:
                        enemies_to_remove.append(enemy)
                    
            # Remove dead enemies
            for enemy in enemies_to_remove:
                self.enemies.remove(enemy)
                
                # Award kill to player
                self.award_kill(enemy)
                
            # Update enemy count
            self.enemies_killed_this_wave = max(0, self.enemies_in_wave - len(self.enemies))
            
        except Exception as e:
            logging.error(f"Error updating enemies: {e}")
            import traceback
            traceback.print_exc()

    def create_enemy(self, enemy_type, x, y):
        """Create and return an enemy of the specified type at the given position"""
        # Calculate scaled stats based on current wave number
        wave_multiplier = 1.0 + (self.wave_number - 1) * 0.1  # 10% increase per wave
        
        # Base enemy stats
        enemy_stats = {
            "normal": {
                "health": 100 * wave_multiplier,
                "speed": 1.5,
                "damage": 10 * wave_multiplier,
                "bullet_speed": 5,
                "shoot_delay": 2000,  # ms
                "bullet_damage": 8 * wave_multiplier,
                "score_value": 50,
                "radius": 20,
                "color": COLORS["red"],
                "gold_value": 1
            },
            "fast": {
                "health": 70 * wave_multiplier,
                "speed": 3.0,
                "damage": 5 * wave_multiplier,
                "bullet_speed": 7,
                "shoot_delay": 1500,  # ms
                "bullet_damage": 5 * wave_multiplier,
                "score_value": 75,
                "radius": 15,
                "color": COLORS["blue"],
                "gold_value": 2
            },
            "tank": {
                "health": 200 * wave_multiplier,
                "speed": 1.0,
                "damage": 15 * wave_multiplier,
                "bullet_speed": 4,
                "shoot_delay": 2500,  # ms
                "bullet_damage": 12 * wave_multiplier,
                "score_value": 100,
                "radius": 30,
                "color": COLORS["purple"],
                "gold_value": 3
            },
            "ranged": {
                "health": 80 * wave_multiplier,
                "speed": 1.8,
                "damage": 8 * wave_multiplier,
                "bullet_speed": 8,
                "shoot_delay": 1000,  # ms
                "bullet_damage": 15 * wave_multiplier,
                "score_value": 150,
                "radius": 18,
                "color": COLORS["orange"],
                "gold_value": 4,
                "range": 500  # Ranged enemies stay at distance
            },
            "boss": {
                "health": 500 * wave_multiplier,
                "speed": 1.2,
                "damage": 25 * wave_multiplier,
                "bullet_speed": 6,
                "shoot_delay": 800,  # ms
                "bullet_damage": 20 * wave_multiplier,
                "score_value": 500,
                "radius": 40,
                "color": COLORS["pink"],
                "gold_value": 10
            }
        }
        
        # Get base stats for this enemy type
        if enemy_type not in enemy_stats:
            print(f"Unknown enemy type: {enemy_type}, defaulting to normal")
            enemy_type = "normal"
            
        stats = enemy_stats[enemy_type]
        
        # Create the enemy with the appropriate type and stats
        # Modified to use positional parameters instead of keyword arguments
        enemy = Enemy(x, y)
        
        # Set enemy properties after creation
        enemy.type = enemy_type
        enemy.max_health = stats["health"]
        enemy.health = stats["health"]
        enemy.speed = stats["speed"]
        enemy.damage = stats["damage"]
        enemy.bullet_speed = stats["bullet_speed"]
        enemy.shoot_delay = stats["shoot_delay"]
        enemy.bullet_damage = stats["bullet_damage"]
        enemy.color = stats["color"]
        enemy.radius = stats["radius"]
        enemy.score_value = stats["score_value"]
        enemy.gold_value = stats["gold_value"]
        
        # Special settings for different enemy types
        if enemy_type == "ranged":
            # Ranged enemies prefer to keep distance
            if hasattr(enemy, "set_preferred_distance"):
                enemy.set_preferred_distance(stats["range"])
        elif enemy_type == "boss":
            # Bosses can shoot special projectiles
            if hasattr(enemy, "enable_special_attacks"):
                enemy.enable_special_attacks(True)
        
        return enemy

    def update_floating_texts(self, dt=None):
        """Update all floating text elements in the game"""
        # Iterate through floating texts in reverse order to safely remove items
        for i in range(len(self.floating_texts) - 1, -1, -1):
            try:
                # Get the current floating text
                text = self.floating_texts[i]
                
                # Update lifetime
                text.lifetime -= 1
                
                # Move text upward for floating effect
                text.y -= 0.5
                
                # Remove text if its lifetime is over
                if text.lifetime <= 0:
                    self.floating_texts.pop(i)
                    continue
                
                # Apply fade-out effect for the last 20 frames
                if text.lifetime < 20:
                    text.alpha = text.lifetime / 20
            except Exception as e:
                print(f"Error updating floating text: {e}")
                # Remove problematic floating text
                self.floating_texts.pop(i)

    def check_collisions(self):
        """
        Check for collisions between game entities.
        This handles collisions between:
        - Player and enemies (damage to player)
        - Projectiles and enemies (damage to enemies)
        - Player and drops (collecting items)
        """
        try:
            # Skip if game is not in playing state
            if self.state != "playing":
                return
                
            # Skip if player is not initialized
            if not hasattr(self, 'player') or not self.player:
                return
                
            # Prepare lists to store entities to remove
            projectiles_to_remove = []
            enemies_to_remove = []
            
            # Check if player collides with any enemies
            for enemy in self.enemies:
                # Calculate distance between player and enemy
                dx = self.player.pos[0] - enemy.pos[0]
                dy = self.player.pos[1] - enemy.pos[1]
                distance = (dx**2 + dy**2)**0.5
                
                # Check for collision (sum of radii)
                collision_distance = self.player.radius + enemy.radius
                if distance < collision_distance:
                    # Handle player damage from enemy collision
                    damage = enemy.damage  # Get enemy damage value
                    if self.player.take_damage(damage):
                        # Player died
                        self.state = "game_over"
                        self.logger.info(f"Player died from collision with enemy. Final score: {self.score}")
                        return
                    
                    # Push player away from enemy (collision response)
                    pushback_strength = 5.0
                    if distance > 0:  # Avoid division by zero
                        push_x = dx / distance * pushback_strength
                        push_y = dy / distance * pushback_strength
                        self.player.pos[0] += push_x
                        self.player.pos[1] += push_y
            
            # Check player projectiles against enemies
            for i, projectile in enumerate(self.projectiles):
                if i in projectiles_to_remove:
                    continue
                    
                for j, enemy in enumerate(self.enemies):
                    if j in enemies_to_remove:
                        continue
                    
                    # Calculate distance between projectile and enemy
                    dx = projectile.pos[0] - enemy.pos[0]
                    dy = projectile.pos[1] - enemy.pos[1]
                    distance = (dx**2 + dy**2)**0.5
                    
                    # Check for collision
                    if distance < projectile.radius + enemy.radius:
                        # Apply damage to enemy
                        if enemy.take_damage(projectile.damage):
                            # Enemy died
                            self.award_kill(enemy)
                            enemies_to_remove.append(j)
                        
                        # Add projectile to remove list unless it has pierce ability
                        if getattr(projectile, 'pierce', False):
                            # For pierce projectiles, track which enemies were hit
                            if not hasattr(projectile, 'hits'):
                                projectile.hits = []
                            
                            # Only register hit if enemy was not already hit by this projectile
                            if j not in projectile.hits:
                                projectile.hits.append(j)
                                
                                # If projectile hit its limit, mark for removal
                                if len(projectile.hits) >= getattr(projectile, 'pierce_count', 3):
                                    projectiles_to_remove.append(i)
                            else:
                                # Regular projectile is removed after hitting one enemy
                                projectiles_to_remove.append(i)
                            
                            # Break the inner loop since this projectile hit something
                            # (except for piercing projectiles)
                            if not getattr(projectile, 'pierce', False):
                                break
            
            # Handle enemy projectiles against player
            for i, projectile in enumerate(self.enemy_projectiles):
                # Calculate distance between projectile and player
                dx = projectile.pos[0] - self.player.pos[0]
                dy = projectile.pos[1] - self.player.pos[1]
                distance = (dx**2 + dy**2)**0.5
                
                # Check for collision
                if distance < projectile.radius + self.player.radius:
                    # Apply damage to player
                    if self.player.take_damage(projectile.damage):
                        # Player died
                        self.state = "game_over"
                        self.logger.info(f"Player died from enemy projectile. Final score: {self.score}")
                        return
                    
                    # Add projectile to remove list
                    projectiles_to_remove.append(i)
            
            # Remove all marked projectiles (in reverse order to avoid index issues)
            for i in sorted(projectiles_to_remove, reverse=True):
                if i < len(self.projectiles):
                    self.projectiles.pop(i)
                    
            # Remove all marked enemies (in reverse order to avoid index issues)
            for j in sorted(enemies_to_remove, reverse=True):
                if j < len(self.enemies):
                    self.enemies.pop(j)
                    
        except Exception as e:
            self.logger.error(f"Error in collision detection: {e}")
            import traceback
            traceback.print_exc()

    def shoot_projectile(self):
        """
        Create a new projectile from the player's position toward the mouse cursor.
        Handles cooldown checks and special conditions.
        """
        try:
            # Skip if player can't shoot
            if not hasattr(self, 'player') or not self.player:
                logging.debug("Can't shoot - player not available")
                return False
            
            # Check if player can shoot based on cooldown
            current_time = pygame.time.get_ticks()
            last_shot_time = getattr(self.player, 'last_shot_time', 0)
            shoot_delay = getattr(self.player, 'shoot_delay', 250)
            
            if current_time - last_shot_time < shoot_delay:
                logging.debug("Weapon on cooldown")
                return False
                
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Convert to world coordinates using the world map
            if hasattr(self, 'world_map') and hasattr(self.world_map, 'screen_to_world'):
                mouse_world_pos = self.world_map.screen_to_world(mouse_pos[0], mouse_pos[1])
            else:
                # Fallback if world_map isn't available
                mouse_world_pos = [
                    mouse_pos[0] + getattr(self, 'camera_x', 0) - getattr(self, 'WINDOW_WIDTH', 1280) // 2,
                    mouse_pos[1] + getattr(self, 'camera_y', 0) - getattr(self, 'WINDOW_HEIGHT', 720) // 2
                ]
                
            # Calculate direction
            dx = mouse_world_pos[0] - self.player.pos[0]
            dy = mouse_world_pos[1] - self.player.pos[1]
            
            # Normalize direction
            distance = max(0.1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
            dx /= distance
            dy /= distance
            
            # Apply spread if configured
            bullet_spread = getattr(self.player, 'bullet_spread', 0)
            if bullet_spread > 0:
                import random
                import math
                angle = math.atan2(dy, dx)
                spread = math.radians(random.uniform(-bullet_spread, bullet_spread))
                angle += spread
                dx = math.cos(angle)
                dy = math.sin(angle)
            
            # Create projectile with current player stats
            try:
                from entities.projectile import PlayerProjectile
                projectile = PlayerProjectile(
                    self.player.pos[0],
                    self.player.pos[1],
                    dx,
                    dy,
                    speed=getattr(self.player, 'bullet_speed', 8),
                    damage=getattr(self.player, 'bullet_damage', 10)
                )
                
                # Make sure projectiles list exists
                if not hasattr(self, 'projectiles'):
                    self.projectiles = []
                    
                # Add to projectiles list
                self.projectiles.append(projectile)
                
                # Update player's last shot time
                self.player.last_shot_time = current_time
                
                # Play sound if available
                if hasattr(self, 'shoot_sound') and self.shoot_sound:
                    self.shoot_sound.play()
                    
                return True
            except ImportError:
                logging.error("Failed to import PlayerProjectile - check your module structure")
                return False
            
        except Exception as e:
            logging.error(f"Error creating projectile: {e}")
            import traceback
            traceback.print_exc()
            return False

    def shoot_special_projectile(self):
        """
        Create a special projectile that has unique properties.
        This is used for the player's special attack.
        """
        try:
            # Skip if special ability isn't available
            special_unlocked = getattr(self, 'special_projectile_unlocked', False)
            if not special_unlocked:
                logging.debug("Special projectile not unlocked")
                return False
                
            # Get current time
            current_time = pygame.time.get_ticks()
            
            # Check cooldown
            last_special_shot = getattr(self, 'last_special_shot', 0)
            special_cooldown = getattr(self, 'special_cooldown', 5000)
            
            if current_time - last_special_shot < special_cooldown:
                logging.debug("Special ability on cooldown")
                return False
                
            # Get mouse position
            mouse_pos = pygame.mouse.get_pos()
            
            # Convert to world coordinates
            if hasattr(self, 'world_map') and hasattr(self.world_map, 'screen_to_world'):
                mouse_world_pos = self.world_map.screen_to_world(mouse_pos[0], mouse_pos[1])
            else:
                # Fallback if world_map isn't available
                mouse_world_pos = [
                    mouse_pos[0] + getattr(self, 'camera_x', 0) - getattr(self, 'WINDOW_WIDTH', 1280) // 2,
                    mouse_pos[1] + getattr(self, 'camera_y', 0) - getattr(self, 'WINDOW_HEIGHT', 720) // 2
                ]
                
            # Calculate direction
            dx = mouse_world_pos[0] - self.player.pos[0]
            dy = mouse_world_pos[1] - self.player.pos[1]
            
            # Normalize direction
            distance = max(0.1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
            dx /= distance
            dy /= distance
            
            # Create multiple special projectiles in a spread pattern
            try:
                from entities.projectile import SpecialProjectile
                import math
                
                # Make sure projectiles list exists
                if not hasattr(self, 'projectiles'):
                    self.projectiles = []
                    
                num_projectiles = 3  # Number of projectiles in the special attack
                spread_angle = 30  # Total spread angle in degrees
                base_angle = math.atan2(dy, dx)
                
                for i in range(num_projectiles):
                    # Calculate angle for this projectile
                    if num_projectiles > 1:
                        angle_offset = spread_angle * (i / (num_projectiles - 1) - 0.5)
                        angle = base_angle + math.radians(angle_offset)
                        proj_dx = math.cos(angle)
                        proj_dy = math.sin(angle)
                    else:
                        proj_dx = dx
                        proj_dy = dy
                        
                    # Create special projectile
                    special_projectile_speed = getattr(self, 'special_projectile_speed', 7)
                    special_projectile_damage = getattr(self, 'special_projectile_damage', 25)
                    
                    projectile = SpecialProjectile(
                        self.player.pos[0],
                        self.player.pos[1],
                        proj_dx,
                        proj_dy,
                        speed=special_projectile_speed,
                        damage=special_projectile_damage,
                        special_type="explosive"  # Options: "homing", "explosive", "spinning"
                    )
                    
                    # Add to projectiles list
                    self.projectiles.append(projectile)
                
                # Update last special shot time
                self.last_special_shot = current_time
                
                # Play sound if available
                if hasattr(self, 'special_sound') and self.special_sound:
                    self.special_sound.play()
                    
                return True
            except ImportError:
                logging.error("Failed to import SpecialProjectile - check your module structure")
                return False
            
        except Exception as e:
            logging.error(f"Error creating special projectile: {e}")
            import traceback
            traceback.print_exc()
            return False

    # Shop methods with improved reliability and feedback
    def buy_speed_boost(self):
        """Buy speed boost from shop"""
        try:
            if not hasattr(self, 'coins') or not hasattr(self, 'player'):
                print("Cannot buy: missing coins or player attributes")
                return False
                
            # Set boost amount and price check
            speed_increase = max(0.5, self.player.speed * 0.1)  # 10% increase or at least 0.5 speed
            cost = 20  # Cost for speed boost
            
            if self.coins < cost:
                # Show cannot afford message
                self.floating_texts.append(
                    FloatingText(
                        text="Cannot afford speed boost!",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["red"],
                        lifetime=60
                    )
                )
                return False
                
            # Apply the boost    
            self.player.speed += speed_increase
            
            # Subtract cost
            self.coins -= cost
            
            # Show success message
            self.floating_texts.append(
                FloatingText(
                    text=f"+{speed_increase:.1f} Speed",
                    position=(self.player.pos[0], self.player.pos[1] - 30),
                    color=COLORS["blue"],
                    lifetime=90
                )
            )
            
            # Show cost message
            self.floating_texts.append(
                FloatingText(
                    text=f"-{cost} coins",
                    position=(self.player.pos[0], self.player.pos[1] - 60),
                    color=COLORS["gold"],
                    lifetime=90
                )
            )
            
            print(f"Purchased speed boost: +{speed_increase:.1f} Speed for {cost} coins")
            return True
            
        except Exception as e:
            print(f"Error buying speed boost: {e}")
            import traceback
            traceback.print_exc()
            return False

    def buy_attack_speed_boost(self):
        """Buy attack speed boost from shop"""
        try:
            if not hasattr(self, 'coins') or not hasattr(self, 'player'):
                print("Cannot buy: missing coins or player attributes")
                return False
                
            # Set boost amount and price check
            cost = 25  # Cost for attack speed boost
            
            if self.coins < cost:
                # Show cannot afford message
                self.floating_texts.append(
                    FloatingText(
                        text="Cannot afford attack speed boost!",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["red"],
                        lifetime=60
                    )
                )
                return False
                
            # Calculate cooldown decrease
            cooldown_decrease = max(10, self.player.shoot_delay * 0.1)  # 10% decrease or at least 10ms
            
            # Apply the boost with a minimum floor to prevent too fast firing
            self.player.shoot_delay = max(50, self.player.shoot_delay - cooldown_decrease)  # Minimum 50ms delay
            
            # Subtract cost
            self.coins -= cost
            
            # Calculate percentage improvement for better feedback
            percent_improvement = int((cooldown_decrease / (self.player.shoot_delay + cooldown_decrease)) * 100)
            
            # Show success message
            self.floating_texts.append(
                FloatingText(
                    text=f"+{percent_improvement}% Attack Speed",
                    position=(self.player.pos[0], self.player.pos[1] - 30),
                    color=COLORS["yellow"],
                    lifetime=90
                )
            )
            
            # Show cost message
            self.floating_texts.append(
                FloatingText(
                    text=f"-{cost} coins",
                    position=(self.player.pos[0], self.player.pos[1] - 60),
                    color=COLORS["gold"],
                    lifetime=90
                )
            )
            
            print(f"Purchased attack speed boost: +{percent_improvement}% for {cost} coins")
            return True
            
        except Exception as e:
            print(f"Error buying attack speed boost: {e}")
            import traceback
            traceback.print_exc()
            return False

    def buy_max_health(self):
        """Buy maximum health boost from shop"""
        try:
            if not hasattr(self, 'coins') or not hasattr(self, 'player'):
                print("Cannot buy: missing coins or player attributes")
                return False
                
            # Set boost amount and price check
            cost = 30  # Cost for max health boost
            
            if self.coins < cost:
                # Show cannot afford message
                self.floating_texts.append(
                    FloatingText(
                        text="Cannot afford health boost!",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["red"],
                        lifetime=60
                    )
                )
                return False
                
            # Calculate health increase
            health_increase = max(10, self.player.max_health * 0.1)  # 10% increase or at least 10 HP
            
            # Apply the boost
            self.player.max_health += health_increase
            self.player.health += health_increase  # Also increase current health
            
            # Subtract cost
            self.coins -= cost
            
            # Show success message
            self.floating_texts.append(
                FloatingText(
                    text=f"+{int(health_increase)} Max HP",
                    position=(self.player.pos[0], self.player.pos[1] - 30),
                    color=COLORS["green"],
                    lifetime=90
                )
            )
            
            # Show cost message
            self.floating_texts.append(
                FloatingText(
                    text=f"-{cost} coins",
                    position=(self.player.pos[0], self.player.pos[1] - 60),
                    color=COLORS["gold"],
                    lifetime=90
                )
            )
            
            print(f"Purchased max health boost: +{int(health_increase)} HP for {cost} coins")
            return True
            
        except Exception as e:
            print(f"Error buying max health boost: {e}")
            import traceback
            traceback.print_exc()
            return False

    def buy_damage_boost(self):
        """Buy damage boost from shop"""
        try:
            if not hasattr(self, 'coins') or not hasattr(self, 'player'):
                print("Cannot buy: missing coins or player attributes")
                return False
                
            # Set boost amount and price check
            cost = 35  # Cost for damage boost
            
            if self.coins < cost:
                # Show cannot afford message
                self.floating_texts.append(
                    FloatingText(
                        text="Cannot afford damage boost!",
                        position=(self.player.pos[0], self.player.pos[1] - 30),
                        color=COLORS["red"],
                        lifetime=60
                    )
                )
                return False
                
            # Calculate damage increase
            damage_increase = max(1, self.player.bullet_damage * 0.1)  # 10% increase or at least 1 damage
            
            # Apply the boost
            self.player.bullet_damage += damage_increase
            self.player.damage = self.player.bullet_damage  # Sync damage values
            
            # Subtract cost
            self.coins -= cost
            
            # Show success message
            self.floating_texts.append(
                FloatingText(
                    text=f"+{int(damage_increase)} Damage",
                    position=(self.player.pos[0], self.player.pos[1] - 30),
                    color=COLORS["red"],
                    lifetime=90
                )
            )
            
            # Show cost message
            self.floating_texts.append(
                FloatingText(
                    text=f"-{cost} coins",
                    position=(self.player.pos[0], self.player.pos[1] - 60),
                    color=COLORS["gold"],
                    lifetime=90
                )
            )
            
            print(f"Purchased damage boost: +{int(damage_increase)} DMG for {cost} coins")
            return True
            
        except Exception as e:
            print(f"Error buying damage boost: {e}")
            import traceback
            traceback.print_exc()
            return False

    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        if not hasattr(self, 'camera_x') or not hasattr(self, 'camera_y'):
            return world_x, world_y
            
        screen_x = int(world_x - self.camera_x + self.screen_width // 2)
        screen_y = int(world_y - self.camera_y + self.screen_height // 2)
        return screen_x, screen_y
    
    def is_on_screen(self, world_x, world_y, radius=0):
        """Check if a world position is visible on screen"""
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        if 0 <= screen_x <= self.screen_width and 0 <= screen_y <= self.screen_height:
            return True
        # Also check if it's just slightly off-screen but should still be rendered
        return (-radius <= screen_x <= self.screen_width + radius and
                -radius <= screen_y <= self.screen_height + radius)

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        if not hasattr(self, 'camera_x') or not hasattr(self, 'camera_y'):
            return screen_x, screen_y
            
        world_x = int(screen_x - self.screen_width // 2 + self.camera_x)
        world_y = int(screen_y - self.screen_height // 2 + self.camera_y)
        return world_x, world_y
        
    def is_visible(self, entity):
        """Check if an entity is visible on screen"""
        # Skip visibility check if entity doesn't have required attributes
        if not hasattr(entity, 'pos'):
            return False
            
        # Get entity radius (default to 20 if not specified)
        radius = getattr(entity, 'radius', 20)
        
        # Check if entity's position is on screen
        return self.is_on_screen(entity.pos[0], entity.pos[1], radius)

    def draw_debug_info(self):
        """Draw debug information to help identify rendering issues"""
        try:
            # Draw coordinate grid
            grid_spacing = 100
            grid_color = COLORS.get('grid', (60, 60, 80))
            
            # Draw vertical grid lines
            for x in range(0, self.screen_width, grid_spacing):
                pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.screen_height), 1)
                
            # Draw horizontal grid lines
            for y in range(0, self.screen_height, grid_spacing):
                pygame.draw.line(self.screen, grid_color, (0, y), (self.screen_width, y), 1)
            
            # Draw screen center
            center_x = self.screen_width // 2
            center_y = self.screen_height // 2
            pygame.draw.circle(self.screen, COLORS.get('red', (255, 0, 0)), (center_x, center_y), 5)
            pygame.draw.line(self.screen, COLORS.get('red', (255, 0, 0)), (center_x - 10, center_y), (center_x + 10, center_y), 2)
            pygame.draw.line(self.screen, COLORS.get('red', (255, 0, 0)), (center_x, center_y - 10), (center_x, center_y + 10), 2)
            
            # Draw camera position
            if hasattr(self, 'camera_x') and hasattr(self, 'camera_y'):
                camera_text = f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})"
                font = pygame.font.Font(None, 20)
                text = font.render(camera_text, True, COLORS.get('white', (255, 255, 255)))
                self.screen.blit(text, (10, 10))
            
            # Draw player position
            if hasattr(self, 'player') and hasattr(self.player, 'pos'):
                player_text = f"Player: ({int(self.player.pos[0])}, {int(self.player.pos[1])})"
                font = pygame.font.Font(None, 20)
                text = font.render(player_text, True, COLORS.get('white', (255, 255, 255)))
                self.screen.blit(text, (10, 30))
            
            # Draw entity counts
            counts_text = f"Enemies: {len(getattr(self, 'enemies', []))} | Projectiles: {len(getattr(self, 'projectiles', []))} | Drops: {len(getattr(self, 'drops', []))}"
            font = pygame.font.Font(None, 20)
            text = font.render(counts_text, True, COLORS.get('white', (255, 255, 255)))
            self.screen.blit(text, (10, 50))
            
            # Draw FPS
            fps_text = f"FPS: {getattr(self, 'current_fps', 0)}"
            text = font.render(fps_text, True, COLORS.get('white', (255, 255, 255)))
            self.screen.blit(text, (self.screen_width - 100, 10))
            
            # Draw game state
            state_text = f"State: {self.state}"
            text = font.render(state_text, True, COLORS.get('white', (255, 255, 255)))
            self.screen.blit(text, (self.screen_width - 150, 30))
            
            # Draw visible entities bounding boxes
            if hasattr(self, 'enemies'):
                for enemy in self.enemies:
                    if self.is_visible(enemy):
                        screen_pos = self.world_to_screen(enemy.pos[0], enemy.pos[1])
                        radius = getattr(enemy, 'radius', 20)
                        pygame.draw.circle(self.screen, COLORS.get('red', (255, 0, 0)), screen_pos, radius, 1)
            
            if hasattr(self, 'projectiles'):
                for proj in self.projectiles:
                    if hasattr(proj, 'pos'):
                        screen_pos = self.world_to_screen(proj.pos[0], proj.pos[1])
                        radius = getattr(proj, 'radius', 5)
                        pygame.draw.circle(self.screen, COLORS.get('yellow', (255, 255, 0)), screen_pos, radius, 1)
            
            if hasattr(self, 'drops'):
                for drop in self.drops:
                    if hasattr(drop, 'world_pos'):
                        screen_pos = self.world_to_screen(drop.world_pos[0], drop.world_pos[1])
                        radius = getattr(drop, 'radius', 10)
                        pygame.draw.circle(self.screen, COLORS.get('green', (0, 255, 0)), screen_pos, radius, 1)
                        
        except Exception as e:
            self.logger.error(f"Error drawing debug info: {e}")

    def toggle_pause(self):
        """Toggle game pause state"""
        try:
            if self.state == "playing":
                self.state = "paused"
                logging.info("Game paused")
            elif self.state == "paused":
                self.state = "playing"
                logging.info("Game resumed")
        except Exception as e:
            logging.error(f"Error toggling pause: {e}")

    def check_player_health(self):
        """Check if player is dead and trigger game over if needed"""
        try:
            if not hasattr(self, 'player') or self.player is None:
                return
                
            if self.player.health <= 0:
                self.state = "game_over"
                logging.info("Player died - game over")
                
                # Create game over floating text
                self.floating_texts.append(
                    FloatingText("GAME OVER", 
                                (self.screen_width // 2, self.screen_height // 2 - 50),
                                COLORS['red'], 
                                72, 
                                300,
                                is_screen_position=True)
                )
                
                # Create score text
                self.floating_texts.append(
                    FloatingText(f"Score: {self.score}",
                                (self.screen_width // 2, self.screen_height // 2 + 20),
                                COLORS['white'],
                                36,
                                300,
                                is_screen_position=True)
                )
        except Exception as e:
            logging.error(f"Error checking player health: {e}")

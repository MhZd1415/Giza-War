import pygame
import random
from utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLORS, WORLD_SIZE

class WorldMap:
    """
    Represents the game world map, handles camera positioning and world-to-screen coordinate conversion.
    
    This class is responsible for:
    - Managing the world size and boundaries
    - Converting between world and screen coordinates
    - Managing the camera position and movement
    - Drawing the world grid and background
    """
    
    def __init__(self, width=WORLD_SIZE, height=WORLD_SIZE):
        """
        Initialize the world map with the given dimensions.
        
        Args:
            width (int): Width of the world in pixels
            height (int): Height of the world in pixels
        """
        self.width = width
        self.height = height
        
        # Set default colors with fallbacks if they don't exist in COLORS
        self.grid_color = COLORS.get('grid', (60, 60, 80))  # Use fallback color if 'grid' not in COLORS
        self.ground_color = COLORS.get('ground', (40, 40, 60))  # Use fallback color if 'ground' not in COLORS
        
        # Camera position (centered initially)
        self.camera_x = width // 2
        self.camera_y = height // 2
        
        # Grid properties
        self.grid_size = 100
        self.grid_line_width = 1
        
        # Screen dimensions
        self.screen_width = 0
        self.screen_height = 0
        
        # Cache screen dimensions on first draw
        self.update_screen_dimensions = True

    def update_screen_dimensions_from_surface(self, surface):
        """Update cached screen dimensions from the provided surface"""
        if surface:
            self.screen_width = surface.get_width()
            self.screen_height = surface.get_height()
            self.update_screen_dimensions = False

    def update_camera(self, target_x, target_y):
        """
        Update the camera position to center on the target coordinates.
        
        Args:
            target_x (int): Target X coordinate in world space
            target_y (int): Target Y coordinate in world space
        """
        # Center camera on target, but respect world boundaries
        self.camera_x = target_x
        self.camera_y = target_y

    def world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x (int): X coordinate in world space
            world_y (int): Y coordinate in world space
            
        Returns:
            tuple: (screen_x, screen_y) coordinates
        """
        screen_x = int(world_x - self.camera_x + self.screen_width // 2)
        screen_y = int(world_y - self.camera_y + self.screen_height // 2)
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x (int): X coordinate in screen space
            screen_y (int): Y coordinate in screen space
            
        Returns:
            tuple: (world_x, world_y) coordinates
        """
        world_x = int(screen_x + self.camera_x - self.screen_width // 2)
        world_y = int(screen_y + self.camera_y - self.screen_height // 2)
        return world_x, world_y

    def is_on_screen(self, world_x, world_y, buffer=50):
        """
        Check if a point in world space is visible on screen.
        
        Args:
            world_x (int): X coordinate in world space
            world_y (int): Y coordinate in world space
            buffer (int): Extra margin to consider around the screen
            
        Returns:
            bool: True if point is on screen, False otherwise
        """
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return (-buffer <= screen_x <= self.screen_width + buffer and
                -buffer <= screen_y <= self.screen_height + buffer)

    def check_boundaries(self, entity):
        """
        Check if an entity is trying to move outside world boundaries and adjust position if needed.
        
        Args:
            entity: The entity (player, enemy, etc.) with a pos attribute to check
            
        Returns:
            bool: True if position was adjusted, False otherwise
        """
        adjusted = False
        
        # Get entity position
        if not hasattr(entity, 'pos'):
            return False
            
        entity_size = getattr(entity, 'size', 20)  # Default size if not specified
        half_size = entity_size / 2
        
        # Check boundaries and adjust if needed
        # Left boundary
        if entity.pos[0] < half_size:
            entity.pos[0] = half_size
            adjusted = True
            
        # Right boundary
        if entity.pos[0] > self.width - half_size:
            entity.pos[0] = self.width - half_size
            adjusted = True
            
        # Top boundary
        if entity.pos[1] < half_size:
            entity.pos[1] = half_size
            adjusted = True
            
        # Bottom boundary
        if entity.pos[1] > self.height - half_size:
            entity.pos[1] = self.height - half_size
            adjusted = True
            
        return adjusted

    def draw(self, surface):
        """
        Draw the world map (background and grid).
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Update screen dimensions if needed
        if self.update_screen_dimensions:
            self.update_screen_dimensions_from_surface(surface)
        
        # Draw the background first
        self.draw_background(surface)
        
        # Draw the grid lines
        self.draw_grid(surface)

    def draw_background(self, surface):
        """
        Draw the world background.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Fill background with ground color
        surface.fill(self.ground_color)
        
    def draw_grid(self, surface):
        """
        Draw the world grid.
        
        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Calculate grid lines positions
        start_x = (self.camera_x // self.grid_size) * self.grid_size
        start_y = (self.camera_y // self.grid_size) * self.grid_size
        
        # Draw vertical grid lines
        for x in range(start_x - self.screen_width, start_x + self.screen_width * 2, self.grid_size):
            screen_x, _ = self.world_to_screen(x, 0)
            if 0 <= screen_x <= self.screen_width:
                pygame.draw.line(
                    surface,
                    self.grid_color,
                    (screen_x, 0),
                    (screen_x, self.screen_height),
                    self.grid_line_width
                )
        
        # Draw horizontal grid lines
        for y in range(start_y - self.screen_height, start_y + self.screen_height * 2, self.grid_size):
            _, screen_y = self.world_to_screen(0, y)
            if 0 <= screen_y <= self.screen_height:
                pygame.draw.line(
                    surface,
                    self.grid_color,
                    (0, screen_y),
                    (self.screen_width, screen_y),
                    self.grid_line_width
                )

    def get_random_position(self, margin=100):
        """
        Get a random position within the world boundaries.
        
        Args:
            margin (int): Margin from the world edges
            
        Returns:
            tuple: (x, y) coordinates
        """
        x = random.randint(margin, self.width - margin)
        y = random.randint(margin, self.height - margin)
        return x, y

    def get_random_position_offscreen(self, screen_width, screen_height, margin=250):
        """
        Get a random position outside the screen but within the world.
        
        Args:
            screen_width (int): Width of the screen
            screen_height (int): Height of the screen
            margin (int): Minimum distance from screen edge
            
        Returns:
            tuple: (x, y) coordinates
        """
        # Determine which side to spawn from (0=top, 1=right, 2=bottom, 3=left)
        side = random.randint(0, 3)
        
        # Calculate screen boundaries in world coordinates
        min_x = self.camera_x - screen_width // 2
        max_x = self.camera_x + screen_width // 2
        min_y = self.camera_y - screen_height // 2
        max_y = self.camera_y + screen_height // 2
        
        # Ensure we stay within world boundaries
        world_min_x = max(0, min_x - margin * 2)
        world_max_x = min(self.width, max_x + margin * 2)
        world_min_y = max(0, min_y - margin * 2)
        world_max_y = min(self.height, max_y + margin * 2)
        
        # Generate position based on chosen side
        if side == 0:  # Top
            x = random.randint(world_min_x, world_max_x)
            y = random.randint(world_min_y, min_y - margin)
        elif side == 1:  # Right
            x = random.randint(max_x + margin, world_max_x)
            y = random.randint(world_min_y, world_max_y)
        elif side == 2:  # Bottom
            x = random.randint(world_min_x, world_max_x)
            y = random.randint(max_y + margin, world_max_y)
        else:  # Left
            x = random.randint(world_min_x, min_x - margin)
            y = random.randint(world_min_y, world_max_y)
        
        # Validate and clamp position
        x = max(0, min(x, self.width))
        y = max(0, min(y, self.height))
        
        return x, y 
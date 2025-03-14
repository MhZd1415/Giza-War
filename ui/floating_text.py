import pygame
import random
import math
from utils.constants import COLORS

class FloatingText:
    """A class for handling floating text for damage numbers, notifications, etc."""
    
    def __init__(self, text, x=None, y=None, position=None, color=(255, 255, 255), size=24, lifetime=60):
        """
        Initialize a floating text object
        
        Args:
            text: The text to display
            x, y: Position coordinates (can be provided separately or as position)
            position: A tuple/list of (x, y) coordinates (alternative to separate x, y)
            color: RGB color tuple
            size: Font size
            lifetime: Duration in frames for text to remain visible
        """
        self.text = text
        
        # Handle position input (either separate x,y or position tuple/list)
        if position is not None:
            self.x, self.y = position
        else:
            self.x, self.y = x, y
            
        self.position = [self.x, self.y]  # Add position as a list for x,y coordinates
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.alpha = 1.0  # For fade effects
        self.font = pygame.font.Font(None, size)
        
    def draw(self, screen, camera_x=0, camera_y=0):
        """
        Draw the floating text on the screen
        
        Args:
            screen: Pygame screen surface
            camera_x, camera_y: Camera position offset
        """
        try:
            # Calculate screen position (world position adjusted for camera)
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            
            # Render text
            text_surface = self.font.render(self.text, True, self.color)
            
            # Apply alpha for fading effect
            if self.alpha < 1.0:
                text_surface.set_alpha(int(255 * self.alpha))
            
            # Center text on position
            text_rect = text_surface.get_rect(center=(screen_x, screen_y))
            
            # Draw to screen
            screen.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error drawing floating text: {e}")
        
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw text at a specific screen position rather than world position"""
        if self.alpha <= 0:
            return  # Don't draw if completely transparent
            
        # Render text with current alpha
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        
        # Center text horizontally at position
        x = int(screen_pos[0] - text_surface.get_width() // 2)
        y = int(screen_pos[1] - self.y)
        
        screen.blit(text_surface, (x, y))
            
    @staticmethod
    def debug_check_instances(floating_texts):
        """Debug method to check for invalid floating text instances"""
        for i, text in enumerate(floating_texts):
            if not isinstance(text, FloatingText):
                print(f"Warning: Invalid FloatingText at index {i}: {text}")
            elif not hasattr(text, 'x') or not hasattr(text, 'y') or not isinstance(text.x, (int, float)) or not isinstance(text.y, (int, float)):
                print(f"Warning: FloatingText at index {i} has invalid position: ({getattr(text, 'x', None)}, {getattr(text, 'y', None)})")
        return True

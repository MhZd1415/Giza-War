"""
DEPRECATED MODULE - Use entities.projectile instead

This module is maintained for backward compatibility only.
New code should import directly from entities.projectile.
"""

import logging
import pygame
import math
from pygame import Vector2
from utils.constants import COLORS

# Display deprecation warning
logging.warning("Using deprecated entities.bullet module. Use entities.projectile instead.")

# Import the actual implementation
from entities.projectile import PlayerProjectile as ModernBullet

class Bullet:
    """
    DEPRECATED - Legacy Bullet class
    
    This is maintained for backward compatibility with older code.
    New code should use PlayerProjectile from entities.projectile.
    """
    
    def __init__(self, x, y, speed, damage, dx, dy):
        """Initialize a bullet with the given parameters"""
        logging.debug("Creating bullet using deprecated Bullet class")
        
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.dx = dx
        self.dy = dy
        self.radius = 3
        self.active = True
        
        # Create a modern bullet instance for actual implementation
        self._modern_bullet = ModernBullet(x, y, dx, dy, speed, damage)
        
        # Copy position to pos for compatibility with both APIs
        self.pos = [x, y]

    def update(self, world_bounds=None):
        """Update bullet position and check bounds"""
        if not self.active:
            return False
            
        # Update using modern implementation
        result = self._modern_bullet.update(world_bounds)
        
        # Sync position data between APIs
        self.x, self.y = self._modern_bullet.pos
        self.pos = self._modern_bullet.pos
        
        # Update active state
        self.active = result
        
        return result

    def draw(self, screen, camera_pos=None):
        """Draw bullet on screen (legacy method)"""
        if not self.active:
            return
            
        # Convert world position to screen position if camera_pos is provided
        screen_x = int(self.x)
        screen_y = int(self.y)
        if camera_pos:
            camera_x, camera_y = camera_pos
            screen_x = int(self.x - camera_x)
            screen_y = int(self.y - camera_y)
            
        pygame.draw.circle(screen, (255, 255, 0), (screen_x, screen_y), self.radius)

    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw bullet at the given screen position"""
        pygame.draw.circle(screen, COLORS.get('player_projectile', (255, 255, 0)), 
            (round(screen_pos[0]), round(screen_pos[1])), self.radius)
        
    def check_collision(self, target):
        """Check if this bullet collides with the given target"""
        # Calculate distance between centers
        dx = self.x - target.pos[0]
        dy = self.y - target.pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        # Check if distance is less than sum of radii
        return distance < self.radius + getattr(target, 'radius', 20)

# For backward compatibility - redirect imports to the new module
from entities.projectile import Projectile, PlayerProjectile, EnemyProjectile, SpecialProjectile

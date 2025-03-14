import pygame
import math
import random
from utils.constants import COLORS

class Projectile:
    """Base class for all projectiles"""
    def __init__(self, x, y, dir_x, dir_y, speed=8, damage=10, radius=4, color=COLORS['white']):
        self.pos = [x, y]
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.color = color
        self.lifetime = 300  # 5 seconds at 60 FPS
        
    def update(self, world_bounds=None):
        """Update projectile position, return False if it's out of bounds or lifetime expired"""
        # Move projectile
        self.pos[0] += self.dir_x * self.speed
        self.pos[1] += self.dir_y * self.speed
        
        # Reduce lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            return False
            
        # Check world boundaries if provided
        if world_bounds:
            # Unpack world bounds (x_min, y_min, x_max, y_max)
            x_min, y_min, x_max, y_max = world_bounds
            
            # Check if projectile is out of bounds
            if (self.pos[0] < x_min - 50 or self.pos[0] > x_max + 50 or
                self.pos[1] < y_min - 50 or self.pos[1] > y_max + 50):
                return False
                
        return True
    
    def draw(self, screen, camera_offset):
        """Draw projectile on screen, adjusting for camera offset"""
        # Calculate screen position
        screen_x = self.pos[0] - camera_offset[0]
        screen_y = self.pos[1] - camera_offset[1]
        
        # Only draw if on screen
        if (0 <= screen_x <= screen.get_width() and
            0 <= screen_y <= screen.get_height()):
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)
            
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw projectile directly at a given screen position"""
        pygame.draw.circle(screen, self.color, 
                         (int(screen_pos[0]), int(screen_pos[1])), 
                         self.radius)

class PlayerProjectile(Projectile):
    """Player projectiles with extra properties"""
    def __init__(self, x, y, dir_x, dir_y, speed=12, damage=10, pierce=False):
        super().__init__(x, y, dir_x, dir_y, speed, damage, 4, COLORS['blue'])
        self.pierce = pierce  # Can projectile pierce through enemies?
        self.hits = []  # Track enemies this has hit (for pierce)
        
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw player projectile at the given screen position"""
        pygame.draw.circle(screen, self.color, 
                         (int(screen_pos[0]), int(screen_pos[1])), 
                         self.radius)
        # Add a glowing effect by drawing a slightly larger, more transparent circle
        pygame.draw.circle(screen, (self.color[0]//2, self.color[1]//2, 255), 
                         (int(screen_pos[0]), int(screen_pos[1])), 
                         self.radius + 2)

class EnemyProjectile(pygame.sprite.Sprite):
    """Enemy projectiles with extra properties"""
    def __init__(self, x, y, dir_x, dir_y, speed=5, damage=5, color=COLORS['red']):
        # Initialize the sprite base class properly
        pygame.sprite.Sprite.__init__(self)
        
        self.pos = [x, y]
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.damage = damage
        self.radius = 4
        self.color = color
        self.lifetime = 240  # 4 seconds at 60 FPS
        
        # Create a rect for collision detection (required for sprite)
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                              self.radius * 2, self.radius * 2)
        
        # Create an image (required for sprite)
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
    def update(self, world_bounds=None):
        """Update projectile position, return False if it's out of bounds or lifetime expired"""
        # Move projectile
        self.pos[0] += self.dir_x * self.speed
        self.pos[1] += self.dir_y * self.speed
        
        # Update rect position to match actual position
        self.rect.x = self.pos[0] - self.radius
        self.rect.y = self.pos[1] - self.radius
        
        # Reduce lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            return False
            
        # Check world boundaries if provided
        if world_bounds:
            # Unpack world bounds (x_min, y_min, x_max, y_max)
            x_min, y_min, x_max, y_max = world_bounds
            
            # Check if projectile is out of bounds
            if (self.pos[0] < x_min - 50 or self.pos[0] > x_max + 50 or
                self.pos[1] < y_min - 50 or self.pos[1] > y_max + 50):
                return False
                
        return True
        
    def draw(self, screen, camera_offset):
        """Draw bullet-shaped projectile on screen, adjusting for camera offset"""
        # Calculate screen position
        screen_x = self.pos[0] - camera_offset[0]
        screen_y = self.pos[1] - camera_offset[1]
        
        # Only draw if on screen
        if (0 <= screen_x <= screen.get_width() and
            0 <= screen_y <= screen.get_height()):
            self.draw_bullet(screen, (screen_x, screen_y))
    
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw bullet-shaped projectile directly at a given screen position"""
        self.draw_bullet(screen, screen_pos)
        
    def draw_bullet(self, screen, pos):
        """Draw a bullet shape instead of simple circle"""
        # Calculate bullet points based on direction
        angle = math.atan2(self.dir_y, self.dir_x)
        
        # Bullet length and width
        length = 8
        width = 3
        
        # Calculate bullet points
        tip_x = pos[0] + length * math.cos(angle)
        tip_y = pos[1] + length * math.sin(angle)
        back_x = pos[0] - length/2 * math.cos(angle)
        back_y = pos[1] - length/2 * math.sin(angle)
        
        # Calculate perpendicular points for width
        perp_angle = angle + math.pi/2
        side1_x = back_x + width * math.cos(perp_angle)
        side1_y = back_y + width * math.sin(perp_angle)
        side2_x = back_x - width * math.cos(perp_angle)
        side2_y = back_y - width * math.sin(perp_angle)
        
        # Draw bullet shape
        points = [(tip_x, tip_y), (side1_x, side1_y), (side2_x, side2_y)]
        pygame.draw.polygon(screen, self.color, points)
        
        # Add a small trail
        trail_length = 12
        trail_end_x = back_x - trail_length * math.cos(angle)
        trail_end_y = back_y - trail_length * math.sin(angle)
        
        # Draw trail with gradient
        steps = 5
        for i in range(steps):
            t = i / steps
            trail_x = back_x * (1-t) + trail_end_x * t
            trail_y = back_y * (1-t) + trail_end_y * t
            radius = 2 * (1 - t)
            # Fade out the color
            alpha = 200 * (1 - t)
            trail_color = (self.color[0], self.color[1], self.color[2], alpha)
            # Create surface for semi-transparent circle
            trail_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, trail_color, (radius, radius), radius)
            screen.blit(trail_surf, (trail_x - radius, trail_y - radius))

class SpecialProjectile(pygame.sprite.Sprite):
    """Special projectiles with unique behaviors"""
    def __init__(self, x, y, dir_x, dir_y, speed=7, damage=15, 
                special_type="homing", color=COLORS['yellow']):
        # Initialize the sprite base class properly
        pygame.sprite.Sprite.__init__(self)
        
        self.pos = [x, y]
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = speed
        self.damage = damage
        self.radius = 6
        self.color = color
        self.lifetime = 300  # 5 seconds at 60 FPS
        self.special_type = special_type
        
        # Homing properties
        self.homing = special_type == "homing"
        self.homing_strength = 0.05
        self.target = None
        
        # Explosion properties
        self.explodes = special_type == "explosive"
        self.explosion_radius = 100
        self.explosion_damage = damage * 0.6
        
        # Movement pattern for spinning projectiles
        self.spin = special_type == "spinning"
        self.angle = 0
        self.spin_radius = 30
        self.spin_speed = 0.1
        self.base_pos = [x, y]  # Center of spin
        
        # For sprite requirements
        self.rect = pygame.Rect(x - self.radius, y - self.radius, 
                              self.radius * 2, self.radius * 2)
        
        self.image = pygame.Surface([self.radius * 2, self.radius * 2], pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        
    def update(self, world_bounds=None, player_pos=None):
        """Update projectile position with special behaviors"""
        # Handle homing logic
        if self.homing and player_pos:
            # Adjust direction towards player
            target_x, target_y = player_pos[0], player_pos[1]
            dx = target_x - self.pos[0]
            dy = target_y - self.pos[1]
            
            # Normalize direction
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                dx = dx / dist
                dy = dy / dist
                
                # Gradually adjust direction
                self.dir_x = (1 - self.homing_strength) * self.dir_x + self.homing_strength * dx
                self.dir_y = (1 - self.homing_strength) * self.dir_y + self.homing_strength * dy
                
                # Normalize direction again
                mag = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if mag > 0:
                    self.dir_x = self.dir_x / mag
                    self.dir_y = self.dir_y / mag
        
        # Handle spinning projectile
        if self.spin:
            # Update angle
            self.angle += self.spin_speed
            
            # Calculate position based on spiral pattern
            radius = self.spin_radius * (1 - (300 - self.lifetime) / 300)  # Spiral inward
            
            # Move the base position forward
            self.base_pos[0] += self.dir_x * self.speed * 0.5
            self.base_pos[1] += self.dir_y * self.speed * 0.5
            
            # Calculate final position
            self.pos[0] = self.base_pos[0] + radius * math.cos(self.angle)
            self.pos[1] = self.base_pos[1] + radius * math.sin(self.angle)
        else:
            # Normal movement
            self.pos[0] += self.dir_x * self.speed
            self.pos[1] += self.dir_y * self.speed
            
        # Update sprite rect
        self.rect.x = self.pos[0] - self.radius
        self.rect.y = self.pos[1] - self.radius
        
        # Reduce lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            # Handle explosion at end of lifetime
            if self.explodes:
                # Implement explosion logic here if needed
                pass
            return False
            
        # Check world boundaries if provided
        if world_bounds:
            # Unpack world bounds (x_min, y_min, x_max, y_max)
            x_min, y_min, x_max, y_max = world_bounds
            
            # Check if projectile is out of bounds
            if (self.pos[0] < x_min - 100 or self.pos[0] > x_max + 100 or
                self.pos[1] < y_min - 100 or self.pos[1] > y_max + 100):
                # Handle explosion if it explodes
                if self.explodes:
                    # Implement explosion logic here if needed
                    pass
                return False
                
        return True
        
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw special projectile directly at a given screen position"""
        if self.special_type == "homing":
            # Draw a glowing orb with pulsing effect
            pulse = math.sin(pygame.time.get_ticks() / 100) * 2
            inner_radius = max(2, self.radius - 2)
            
            # Outer glow
            glow_radius = self.radius + pulse
            glow_surf = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (self.color[0], self.color[1], self.color[2], 100), 
                             (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surf, (screen_pos[0]-glow_radius, screen_pos[1]-glow_radius))
            
            # Inner core
            pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), inner_radius)
            
        elif self.special_type == "explosive":
            # Draw explosive projectile
            pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), self.radius)
            
            # Draw inner pattern (like a bomb)
            inner_color = (min(255, self.color[0]+50), min(255, self.color[1]+50), min(255, self.color[2]+50))
            pygame.draw.circle(screen, inner_color, (int(screen_pos[0]), int(screen_pos[1])), self.radius//2)
            
            # Draw a small "fuse"
            fuse_length = 6
            pygame.draw.line(screen, COLORS['white'], 
                           (screen_pos[0], screen_pos[1] - self.radius),
                           (screen_pos[0], screen_pos[1] - self.radius - fuse_length), 2)
            
        elif self.special_type == "spinning":
            # Draw a spinning projectile with trail
            for i in range(5):
                # Draw fading trail
                trail_pos = (
                    int(screen_pos[0] - i*2*self.dir_x),
                    int(screen_pos[1] - i*2*self.dir_y)
                )
                alpha = 200 - i*40
                trail_color = (self.color[0], self.color[1], self.color[2], alpha)
                trail_surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, trail_color, (self.radius, self.radius), self.radius-i)
                screen.blit(trail_surf, (trail_pos[0]-self.radius, trail_pos[1]-self.radius))
            
            # Draw main projectile
            pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), self.radius)
        else:
            # Default drawing for other special types
            pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), self.radius)

class Bullet(PlayerProjectile):
    """Legacy compatibility class - redirects to PlayerProjectile"""
    def __init__(self, x, y, direction_x, direction_y, speed=10, damage=10, lifetime=180):
        super().__init__(x, y, direction_x, direction_y, speed, damage, lifetime, COLORS['player_projectile']) 
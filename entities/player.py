import pygame
import math
import random
from utils.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from entities.projectile import PlayerProjectile

class Player:
    def __init__(self, x=0, y=0):
        # Initialize position
        self.pos = [x, y]
        
        # Combat stats
        self.health = 100
        self.max_health = 100
        self.damage = 10
        self.bullet_damage = 10
        self.bullet_speed = 8
        self.bullet_spread = 5  # Spread in degrees
        self.shoot_delay = 250  # Time between shots in milliseconds
        self.last_shot_time = 0
        self.can_shoot = True  # Property for whether player can shoot
        self.bullet_cooldown = 250  # Cooldown between shots
        
        # Movement
        self.speed = 3
        self.radius = 20
        
        # Special attack
        self.special_cooldown = 5000  # 5 seconds
        self.last_special_time = 0
        self.special_projectile_count = 8  # Number of projectiles in special attack
        
        # Progression
        self.level = 1
        self.experience = 0
        self.xp_to_next_level = 100
        self.coins = 0
        
        # Initialize bullet list
        self.bullets = []
        
        # Experience and leveling
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100  # Base XP requirement
        
        # Upgrades
        self.max_health_upgrade = 0
        self.speed_upgrade = 0
        self.bullet_damage_upgrade = 0
        self.fire_rate_upgrade = 0
        
        # Position and physics
        self.vel = [0, 0]  # Velocity
        self.speed = 5.0   # Base movement speed
        self.radius = 20   # Collision radius (important for hit detection)
        
        # Health regeneration
        self.health_regen = 0  # Health regenerated per second
        self.health_regen_timer = 0
        
        # Active buffs
        self.active_buffs = []
        
        # UI and visual elements
        self.color = COLORS['blue']
        self.direction = 0  # Direction in radians
        
        # Game reference (will be set by Game instance)
        self.game = None
        
        # Position and movement
        self.velocity = [0, 0]
        self.speed = 3.0
        
        # Appearance
        self.turret_color = COLORS['dark_green']
        
        # Aiming
        self.aim_direction = [1, 0]  # Default aim right
        self.aim_angle = 0  # In radians, 0 = right
        
        # Tank dimensions for drawing
        self.width = 40
        self.height = 30
        self.turret_length = 30
        self.turret_width = 8
        
    def take_damage(self, damage):
        """Take damage and return True if killed"""
        self.health -= damage
        return self.health <= 0
        
    def heal(self, amount):
        """Heal the player by the given amount"""
        self.health = min(self.health + amount, self.max_health)
        
    def update(self, dt):
        """Update player state"""
        # Update bullets
        for i in range(len(self.bullets) - 1, -1, -1):
            bullet = self.bullets[i]
            # Check if bullet is still active
            if not bullet.update():
                self.bullets.pop(i)
        
        # Update active buffs
        if hasattr(self, 'active_buffs'):
            for i in range(len(self.active_buffs) - 1, -1, -1):
                buff = self.active_buffs[i]
                if not buff.update(dt):
                    # Buff expired, remove it
                    self.active_buffs.pop(i)
                    
        # Regenerate health if the player has health regen
        if self.health_regen > 0 and self.health < self.max_health:
            self.health_regen_timer += dt
            if self.health_regen_timer >= 60:  # Every second at 60 FPS
                self.health = min(self.health + self.health_regen, self.max_health)
                self.health_regen_timer = 0
        
        # Update direction based on mouse position if game is available
        if self.game:
            mouse_pos = pygame.mouse.get_pos()
            # Convert screen to world coordinates
            if hasattr(self.game, 'world_map') and self.game.world_map:
                world_mouse = self.game.world_map.screen_to_world(mouse_pos[0], mouse_pos[1])
                # Calculate angle
                dx = world_mouse[0] - self.pos[0]
                dy = world_mouse[1] - self.pos[1]
                self.direction = math.atan2(dy, dx)
        
    def move(self, dx, dy):
        """Move the player by the given delta"""
        self.pos[0] += dx
        self.pos[1] += dy
        
        # Ensure we're within world boundaries (if game and world_map are available)
        if self.game and hasattr(self.game, 'world_map') and self.game.world_map:
            self.game.world_map.check_boundaries(self)
            
    def shoot(self, target_pos):
        """Shoot a bullet towards the target position"""
        current_time = pygame.time.get_ticks()
        
        # Check if player can shoot based on cooldown
        if not self.can_shoot or current_time - self.last_shot_time < self.bullet_cooldown:
            return False
            
        # Calculate direction vector
        dir_x = target_pos[0] - self.pos[0]
        dir_y = target_pos[1] - self.pos[1]
        
        # Normalize direction
        length = math.sqrt(dir_x * dir_x + dir_y * dir_y)
        if length > 0:
            dir_x = dir_x / length
            dir_y = dir_y / length
            
        # Apply spread if enabled
        if self.bullet_spread > 0:
            angle = math.atan2(dir_y, dir_x)
            spread = math.radians(random.uniform(-self.bullet_spread, self.bullet_spread))
            angle += spread
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
        
        # Create bullet
        bullet = PlayerProjectile(
            self.pos[0],
            self.pos[1],
            dir_x,
            dir_y,
            speed=self.bullet_speed,
            damage=self.bullet_damage
        )
        
        # Add to bullets list
        self.bullets.append(bullet)
        
        # Update last shot time
        self.last_shot_time = current_time
        
        return True
        
    def can_shoot_special(self):
        """Check if player can use special attack"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_special_time >= self.special_cooldown
        
    def draw(self, screen):
        """Draw player on screen"""
        # Draw player body
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        
        # Draw player direction/turret
        end_x = self.pos[0] + math.cos(self.direction) * (self.radius + 10)
        end_y = self.pos[1] + math.sin(self.direction) * (self.radius + 10)
        pygame.draw.line(screen, COLORS['dark_blue'], 
                        (int(self.pos[0]), int(self.pos[1])), 
                        (int(end_x), int(end_y)), 
                        4)
                        
        # Draw health bar above player
        self.draw_health_bar(screen)
        
    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw player at specified screen position"""
        # Draw player body
        pygame.draw.circle(screen, self.color, 
                         (int(screen_pos[0]), int(screen_pos[1])), 
                         self.radius)
        
        # Draw player direction/turret
        end_x = screen_pos[0] + math.cos(self.direction) * (self.radius + 10)
        end_y = screen_pos[1] + math.sin(self.direction) * (self.radius + 10)
        pygame.draw.line(screen, COLORS['dark_blue'], 
                        (int(screen_pos[0]), int(screen_pos[1])), 
                        (int(end_x), int(end_y)), 
                        4)
                        
        # Draw health bar above player
        bar_width = 40
        bar_height = 5
        bar_x = screen_pos[0] - bar_width // 2
        bar_y = screen_pos[1] - self.radius - 10
        
        # Draw background (empty health)
        pygame.draw.rect(screen, COLORS['red'], 
                        (int(bar_x), int(bar_y), bar_width, bar_height))
        
        # Draw filled health
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, COLORS['green'], 
                        (int(bar_x), int(bar_y), health_width, bar_height))

    def draw_health_bar(self, screen):
        """Draw health bar above player"""
        bar_width = 40
        bar_height = 5
        bar_x = self.pos[0] - bar_width // 2
        bar_y = self.pos[1] - self.radius - 10
        
        # Draw background (empty health)
        pygame.draw.rect(screen, COLORS['red'], 
                        (int(bar_x), int(bar_y), bar_width, bar_height))
        
        # Draw filled health
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(screen, COLORS['green'], 
                        (int(bar_x), int(bar_y), health_width, bar_height))

    def add_experience(self, amount):
        """Add experience to the player"""
        self.xp += amount
        
        # Check for level up
        while self.xp >= self.xp_to_next_level:
            self.level_up()
            
        return self.xp
        
    def level_up(self):
        """Level up the player"""
        # Increase level
        self.level += 1
        
        # Subtract XP for this level
        self.xp -= self.xp_to_next_level
        
        # Increase XP required for next level (20% increase per level)
        self.xp_to_next_level = int(self.xp_to_next_level * 1.2)
        
        # Base stat increases
        self.max_health += 10
        self.health = self.max_health  # Heal to full on level up
        self.bullet_damage += 2
        self.damage = self.bullet_damage  # Update damage for compatibility
        
        # Return true to indicate level up occurred
        return True

    def update_aim(self, target_pos):
        """Update the player's aim direction based on target world position"""
        if not isinstance(target_pos, (list, tuple)) or len(target_pos) < 2:
            return  # Invalid target position
            
        # Calculate direction vector to target
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        
        # Calculate angle
        self.aim_angle = math.atan2(dy, dx)
        
        # Normalize direction vector
        length = max(0.1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
        self.aim_direction = [dx/length, dy/length]

    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw player at given screen position with proper turret aiming"""
        if not isinstance(screen_pos, (list, tuple)) or len(screen_pos) < 2:
            return  # Invalid screen position
            
        screen_x, screen_y = screen_pos
        
        # Draw tank body
        body_rect = pygame.Rect(screen_x - self.width//2, screen_y - self.height//2, 
                               self.width, self.height)
        pygame.draw.rect(screen, self.color, body_rect)
        
        # Draw treads
        tread_width = 2
        pygame.draw.line(screen, COLORS['black'],
                       (screen_x - self.width//2, screen_y - self.height//2),
                       (screen_x - self.width//2, screen_y + self.height//2), tread_width)
        pygame.draw.line(screen, COLORS['black'],
                       (screen_x + self.width//2, screen_y - self.height//2),
                       (screen_x + self.width//2, screen_y + self.height//2), tread_width)
        
        # Draw turret using aim angle
        end_x = screen_x + self.turret_length * math.cos(self.aim_angle)
        end_y = screen_y + self.turret_length * math.sin(self.aim_angle)
        pygame.draw.line(screen, self.turret_color, (screen_x, screen_y), (end_x, end_y), self.turret_width)
        
        # Draw health bar above player
        health_width = 40
        health_height = 5
        health_x = screen_x - health_width // 2
        health_y = screen_y - self.height // 2 - 10
        
        # Background (red)
        pygame.draw.rect(screen, COLORS['red'], (health_x, health_y, health_width, health_height))
        # Foreground (green) - scales with health percentage
        health_percentage = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, COLORS['green'], 
                       (health_x, health_y, int(health_width * health_percentage), health_height))

    def shoot(self, target_pos):
        """Attempt to shoot towards target position"""
        current_time = pygame.time.get_ticks()
        if not self.can_shoot or current_time - self.last_shot_time < self.shoot_delay:
            return False
        
        # Update aim direction towards target
        self.update_aim(target_pos)
        
        # Record shot time
        self.last_shot_time = current_time
        
        # No actual bullet creation here - this is handled by the game class
        return True

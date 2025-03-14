import pygame
import math
import random
from utils.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT
from entities.projectile import EnemyProjectile, SpecialProjectile

class Enemy:
    def __init__(self, x, y, enemy_type="normal", wave=1):
        self.pos = [x, y]
        self.enemy_type = enemy_type
        self.wave = wave
        self.radius = 15  # Default radius
        self.damage = 10  # Default damage
        self.speed = 1.0  # Default speed
        self.health = 100  # Default health
        self.melee_cooldown = 1000  # 1 second cooldown for melee attacks
        self.last_melee_attack = 0
        self.score_value = 50  # Default score value
        
        # Base color by enemy type
        self.color = {
            'normal': COLORS['red'],
            'fast': COLORS['blue'],
            'tank': COLORS['purple'],
            'ranged': COLORS['yellow'],
            'boss': COLORS['boss_red'] if 'boss_red' in COLORS else COLORS['red']
        }.get(enemy_type, COLORS['red'])
        
        # Initialize projectiles and special_projectiles as sprite groups
        self.projectiles = pygame.sprite.Group()
        self.special_projectiles = pygame.sprite.Group()
        
        # Set projectile properties
        self.projectile_cooldown = 2000  # Default cooldown (2 seconds)
        self.last_shot_time = 0
        self.projectile_speed = 5  # Default projectile speed
        self.bullet_damage = 5  # Default bullet damage
        
        # Set coin value based on enemy type
        self.gold_value = {
            'normal': 1,
            'fast': 2,
            'tank': 3,
            'ranged': 2,
            'boss': 10
        }.get(enemy_type, 1)
        
        # Scale stats based on wave number
        wave_scale = 1.0 + (wave - 1) * 0.1  # 10% increase per wave
        
        # Apply enemy type specific attributes
        if enemy_type == "normal":
            self.radius = 15
            self.speed = 1.0 * wave_scale
            self.health = 100 * wave_scale
            self.damage = 10 * wave_scale
            
        elif enemy_type == "fast":
            self.radius = 12
            self.speed = 2.0 * wave_scale
            self.health = 70 * wave_scale
            self.damage = 5 * wave_scale
            
        elif enemy_type == "tank":
            self.radius = 20
            self.speed = 0.7 * wave_scale
            self.health = 200 * wave_scale
            self.damage = 15 * wave_scale
            
        elif enemy_type == "ranged":
            self.radius = 14
            self.speed = 0.8 * wave_scale
            self.health = 80 * wave_scale
            self.damage = 8 * wave_scale
            self.projectile_cooldown = 1500  # 1.5 seconds
            self.bullet_damage = 7 * wave_scale
            
        elif enemy_type == "boss":
            self.radius = 30
            self.speed = 0.6 * wave_scale
            self.health = 500 * wave_scale
            self.damage = 20 * wave_scale
            self.projectile_cooldown = 1000  # 1 second
            self.bullet_damage = 10 * wave_scale
            
        # Store max health
        self.max_health = self.health
        
        # Initialize state variables for AI behavior
        self.ai_state = "follow"  # Initial AI state: follow, retreat, orbit, shoot
        self.ai_timer = 0  # Timer for AI state changes
        self.ai_target_distance = 200  # Target distance for ranged enemies
        
        # Set random AI change timer
        self.next_ai_change = random.randint(3000, 6000)  # 3-6 seconds
        
        # Movement variables
        self.orbit_direction = random.choice([-1, 1])  # Clockwise or counter-clockwise
        self.orbit_angle = random.random() * math.pi * 2  # Random start angle
        self.retreat_distance = random.randint(250, 350)  # Distance to retreat before returning
        
        # For boss enemies
        self.special_attack_cooldown = 5000  # 5 seconds between special attacks
        self.last_special_attack = 0
        self.phase = 1  # Boss phases (increases as boss health decreases)
        self.phase_thresholds = [0.7, 0.4, 0.2]  # Phase change at 70%, 40%, and 20% health
        
        # Game reference - will be set by Game instance
        self.game = None
        
    def update(self, dt, player_pos):
        """Update enemy position and state based on player position"""
        # Update projectiles
        for proj in list(self.projectiles.sprites()):
            if not proj.update():
                self.projectiles.remove(proj)
                
        for proj in list(self.special_projectiles.sprites()):
            if not proj.update(player_pos=player_pos if hasattr(proj, 'homing') else None):
                self.special_projectiles.remove(proj)
        
        # Boss phase changes
        if self.enemy_type == "boss":
            health_ratio = self.health / self.max_health
            for i, threshold in enumerate(self.phase_thresholds):
                if health_ratio <= threshold and self.phase <= i + 1:
                    self.phase = i + 2  # Phase 2, 3, or 4
                    # Each phase makes the boss more aggressive
                    self.speed *= 1.1
                    self.projectile_cooldown *= 0.8
        
        # Calculate distance to player
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Update AI state based on timing and distance
        current_time = pygame.time.get_ticks()
        if current_time > self.ai_timer + self.next_ai_change:
            self.ai_timer = current_time
            self.next_ai_change = random.randint(3000, 6000)  # 3-6 seconds
            
            # Different behavior based on enemy type
            if self.enemy_type == "normal":
                # Normal enemies just follow the player
                self.ai_state = "follow"
                
            elif self.enemy_type == "fast":
                # Fast enemies alternate between following and orbiting
                self.ai_state = random.choice(["follow", "orbit"])
                
            elif self.enemy_type == "tank":
                # Tank enemies mainly follow but occasionally pause
                self.ai_state = random.choices(["follow", "retreat"], weights=[0.8, 0.2])[0]
                
            elif self.enemy_type == "ranged":
                # Ranged enemies try to maintain distance
                if distance < self.ai_target_distance - 50:
                    self.ai_state = "retreat"
                elif distance > self.ai_target_distance + 50:
                    self.ai_state = "follow"
                else:
                    self.ai_state = random.choice(["orbit", "follow", "retreat"])
                    
            elif self.enemy_type == "boss":
                # Boss behavior changes based on health/phase
                if self.phase == 1:
                    self.ai_state = random.choice(["follow", "orbit"])
                elif self.phase == 2:
                    self.ai_state = random.choice(["follow", "orbit", "follow"])
                else:  # Phase 3 or 4
                    self.ai_state = random.choice(["follow", "follow", "follow", "orbit"])
        
        # Override for ranged enemies who are too close to player
        if self.enemy_type == "ranged" and distance < self.ai_target_distance / 2:
            self.ai_state = "retreat"
            
        # Override for ranged enemies who are too far from player
        if self.enemy_type == "ranged" and distance > self.ai_target_distance * 1.5:
            self.ai_state = "follow"
        
        # Act based on AI state
        if self.ai_state == "follow":
            # Move toward player
            if distance > 0:
                normalized_dx = dx / distance
                normalized_dy = dy / distance
                self.pos[0] += normalized_dx * self.speed
                self.pos[1] += normalized_dy * self.speed
                
        elif self.ai_state == "retreat":
            # Move away from player
            if distance > 0:
                normalized_dx = dx / distance
                normalized_dy = dy / distance
                self.pos[0] -= normalized_dx * self.speed * 1.2  # Retreat faster
                self.pos[1] -= normalized_dy * self.speed * 1.2
                
        elif self.ai_state == "orbit":
            # Orbit around player at a distance
            orbit_speed = self.speed * 1.5  # Move faster in orbit
            
            # Only orbit if we're close enough to the player
            if distance < self.ai_target_distance * 1.5:
                # Update orbit angle
                self.orbit_angle += self.orbit_direction * orbit_speed / self.ai_target_distance
                
                # Calculate desired position
                desired_x = player_pos[0] + math.cos(self.orbit_angle) * self.ai_target_distance
                desired_y = player_pos[1] + math.sin(self.orbit_angle) * self.ai_target_distance
                
                # Move toward desired position
                orbit_dx = desired_x - self.pos[0]
                orbit_dy = desired_y - self.pos[1]
                orbit_distance = math.sqrt(orbit_dx**2 + orbit_dy**2)
                
                if orbit_distance > 0:
                    self.pos[0] += (orbit_dx / orbit_distance) * orbit_speed
                    self.pos[1] += (orbit_dy / orbit_distance) * orbit_speed
            else:
                # If too far from player, move closer
                if distance > 0:
                    normalized_dx = dx / distance
                    normalized_dy = dy / distance
                    self.pos[0] += normalized_dx * self.speed
                    self.pos[1] += normalized_dy * self.speed
                
        # For ranged enemies, attempt to shoot if in the right state
        if self.enemy_type in ["ranged", "boss"]:
            current_time = pygame.time.get_ticks()
            
            # Shoot at player if cooldown has elapsed
            if current_time - self.last_shot_time >= self.projectile_cooldown:
                self.shoot(player_pos)
                
            # For bosses, use special attack if cooldown has elapsed
            if self.enemy_type == "boss" and current_time - self.last_special_attack >= self.special_attack_cooldown:
                self.special_attack(player_pos)
    
    def shoot(self, player_pos):
        """Shoot a projectile at the player"""
        # Calculate direction to player
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Add random spread based on enemy type
            if self.enemy_type == "ranged":
                spread = 0.1  # Small spread for ranged enemies
            else:  # Boss
                spread = 0.05  # Less spread for boss
                
            # Apply spread
            angle = math.atan2(dir_y, dir_x)
            angle += random.uniform(-spread, spread)
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            # Create new projectile
            projectile = EnemyProjectile(
                self.pos[0], self.pos[1],
                dir_x, dir_y,
                speed=self.projectile_speed,
                damage=self.bullet_damage,
                color=COLORS['yellow'] if self.enemy_type == "ranged" else COLORS['orange']
            )
            
            # Add to sprite group
            self.projectiles.add(projectile)
            
            # Update last shot time
            self.last_shot_time = pygame.time.get_ticks()
            
            # For boss enemies, shoot multiple projectiles
            if self.enemy_type == "boss":
                # Number of extra projectiles increases with phase
                num_extra = self.phase - 1
                spread_angle = math.pi / 6  # 30 degrees
                
                for i in range(num_extra):
                    # Calculate angle for extra projectiles
                    extra_angle = angle + spread_angle * (i + 1) / (num_extra + 1)
                    extra_dir_x = math.cos(extra_angle)
                    extra_dir_y = math.sin(extra_angle)
                    
                    extra_projectile = EnemyProjectile(
                        self.pos[0], self.pos[1],
                        extra_dir_x, extra_dir_y,
                        speed=self.projectile_speed,
                        damage=self.bullet_damage,
                        color=COLORS['orange']
                    )
                    
                    self.projectiles.add(extra_projectile)
                    
                    # Calculate angle for opposite side
                    opposite_angle = angle - spread_angle * (i + 1) / (num_extra + 1)
                    opposite_dir_x = math.cos(opposite_angle)
                    opposite_dir_y = math.sin(opposite_angle)
                    
                    opposite_projectile = EnemyProjectile(
                        self.pos[0], self.pos[1],
                        opposite_dir_x, opposite_dir_y,
                        speed=self.projectile_speed,
                        damage=self.bullet_damage,
                        color=COLORS['orange']
                    )
                    
                    self.projectiles.add(opposite_projectile)
            
            return True
        return False
        
    def special_attack(self, player_pos):
        """Special attack for boss enemies"""
        if self.enemy_type != "boss":
            return False
            
        # Different special attacks based on phase
        if self.phase == 1:
            # Phase 1: Spiral projectiles
            self.shoot_spiral(player_pos)
            
        elif self.phase == 2:
            # Phase 2: Homing projectiles
            self.shoot_homing(player_pos)
            
        elif self.phase >= 3:
            # Phase 3+: Shotgun blast
            self.shoot_shotgun(player_pos)
            
        # Update last special attack time
        self.last_special_attack = pygame.time.get_ticks()
        return True
    
    def shoot_spiral(self, player_pos):
        """Shoot projectiles in a spiral pattern"""
        num_projectiles = 8
        start_angle = random.random() * math.pi * 2
        
        for i in range(num_projectiles):
            angle = start_angle + (i * 2 * math.pi / num_projectiles)
            dir_x = math.cos(angle)
            dir_y = math.sin(angle)
            
            projectile = SpecialProjectile(
                self.pos[0], self.pos[1],
                dir_x, dir_y,
                speed=self.projectile_speed * 0.8,
                damage=self.bullet_damage * 1.2,
                special_type="spinning",
                color=COLORS['accent'] if 'accent' in COLORS else COLORS['yellow']
            )
            
            self.special_projectiles.add(projectile)
    
    def shoot_homing(self, player_pos):
        """Shoot homing projectiles"""
        # Calculate direction to player
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Create homing projectile
            homing = SpecialProjectile(
                self.pos[0], self.pos[1],
                dir_x, dir_y,
                speed=self.projectile_speed * 0.7,
                damage=self.bullet_damage * 1.5,
                special_type="homing",
                color=COLORS['yellow']
            )
            
            self.special_projectiles.add(homing)
    
    def shoot_shotgun(self, player_pos):
        """Shoot a spread of projectiles in a shotgun pattern"""
        # Calculate direction to player
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normalize direction
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Base angle
            angle = math.atan2(dir_y, dir_x)
            
            # Number of projectiles
            num_projectiles = 7 + (self.phase - 3) * 2  # More projectiles in higher phases
            spread = math.pi / 4  # 45 degree spread
            
            for i in range(num_projectiles):
                # Calculate angle for this projectile
                proj_angle = angle - spread/2 + spread * i / (num_projectiles - 1)
                proj_dir_x = math.cos(proj_angle)
                proj_dir_y = math.sin(proj_angle)
                
                # Small random speed variation
                speed_var = random.uniform(0.9, 1.1)
                
                projectile = EnemyProjectile(
                    self.pos[0], self.pos[1],
                    proj_dir_x, proj_dir_y,
                    speed=self.projectile_speed * speed_var,
                    damage=self.bullet_damage,
                    color=COLORS['red']
                )
                
                self.projectiles.add(projectile)
    
    def take_damage(self, damage):
        """Take damage and return True if killed"""
        self.health -= damage
        return self.health <= 0
    
    def can_melee_attack(self):
        """Check if enemy can perform a melee attack"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_melee_attack >= self.melee_cooldown
    
    def perform_melee_attack(self, player):
        """Perform a melee attack on the player and return damage dealt"""
        if not self.can_melee_attack():
            return 0
            
        # Update last attack time
        self.last_melee_attack = pygame.time.get_ticks()
        
        # Calculate damage - can vary slightly
        damage_variance = random.uniform(0.8, 1.2)
        damage = self.damage * damage_variance
        
        # Apply damage to player
        player.take_damage(damage)
        
        return damage
                    
    def draw(self, screen):
        """Draw enemy on screen"""
        pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)
        
        # Health bar
        self.draw_health_bar(screen)

    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw enemy at the given screen position"""
        # Draw enemy
        pygame.draw.circle(screen, self.color, (int(screen_pos[0]), int(screen_pos[1])), self.radius)
        
        # Add details based on enemy type
        if self.enemy_type == "fast":
            # Add speed lines
            speed_color = (min(255, self.color[0] + 40), 
                         min(255, self.color[1] + 40), 
                         min(255, self.color[2] + 40))
            pygame.draw.circle(screen, speed_color, 
                             (int(screen_pos[0]), int(screen_pos[1])), 
                             self.radius - 5)
        
        elif self.enemy_type == "tank":
            # Add armor-like decoration
            armor_color = (max(0, self.color[0] - 40), 
                         max(0, self.color[1] - 40), 
                         max(0, self.color[2] - 40))
            pygame.draw.circle(screen, armor_color, 
                             (int(screen_pos[0]), int(screen_pos[1])), 
                             self.radius - 3, 3)
        
        elif self.enemy_type == "ranged":
            # Add targeting reticle
            reticle_color = (min(255, self.color[0] + 70), 
                           min(255, self.color[1] + 70), 
                           min(255, self.color[2] + 70))
            pygame.draw.circle(screen, reticle_color, 
                             (int(screen_pos[0]), int(screen_pos[1])), 
                             self.radius - 4, 2)
            pygame.draw.line(screen, reticle_color, 
                           (screen_pos[0] - self.radius, screen_pos[1]),
                           (screen_pos[0] + self.radius, screen_pos[1]), 1)
            pygame.draw.line(screen, reticle_color, 
                           (screen_pos[0], screen_pos[1] - self.radius),
                           (screen_pos[0], screen_pos[1] + self.radius), 1)
        
        elif self.enemy_type == "boss":
            # Draw boss with crown and multiple layers
            crown_color = COLORS['gold'] if 'gold' in COLORS else (255, 215, 0)
            
            # Inner circle
            inner_color = COLORS['dark_red'] if 'dark_red' in COLORS else (150, 0, 0)
            pygame.draw.circle(screen, inner_color, 
                           (int(screen_pos[0]), int(screen_pos[1])), 
                             self.radius - 6)
            
            # Boss "crown" points
            points = []
            num_points = 5
            crown_radius = self.radius + 4
            for i in range(num_points):
                angle = math.pi * 2 * i / num_points - math.pi / 2
                x = screen_pos[0] + math.cos(angle) * crown_radius
                y = screen_pos[1] + math.sin(angle) * crown_radius
                points.append((x, y))
                
                # Add inner points for star shape
                inner_angle = angle + math.pi / num_points
                inner_radius = self.radius - 2
                inner_x = screen_pos[0] + math.cos(inner_angle) * inner_radius
                inner_y = screen_pos[1] + math.sin(inner_angle) * inner_radius
                points.append((inner_x, inner_y))
                
            pygame.draw.polygon(screen, crown_color, points, 2)
            
            # Phase indicator (glowing aura)
            if self.phase > 1:
                phase_colors = [
                    None,  # No aura for phase 1
                    (150, 0, 0, 100),  # Phase 2 (red)
                    (200, 50, 0, 120),  # Phase 3 (orange)
                    (255, 150, 0, 150)  # Phase 4 (yellow)
                ]
                
                # Create aura surface
                aura_size = self.radius * 2 + 12 + (self.phase - 1) * 4
                aura_surf = pygame.Surface((aura_size, aura_size), pygame.SRCALPHA)
                aura_color = phase_colors[min(self.phase, len(phase_colors) - 1)]
                pygame.draw.circle(aura_surf, aura_color, 
                                 (aura_size // 2, aura_size // 2), 
                                 aura_size // 2)
                
                # Draw aura
                screen.blit(aura_surf, 
                          (screen_pos[0] - aura_size // 2, 
                           screen_pos[1] - aura_size // 2))
        
        # Draw health bar at screen position
        self.draw_health_bar_at_screen_pos(screen, screen_pos)
        
    def draw_health_bar(self, screen):
        """Draw health bar above enemy"""
        # Only draw health bar if enemy has taken damage
        if self.health < self.max_health:
            health_percent = max(0, self.health / self.max_health)
            bar_width = self.radius * 2
            bar_height = 4
            
            # Position above enemy
            bar_x = self.pos[0] - bar_width / 2
            bar_y = self.pos[1] - self.radius - 10
            
            # Background (empty health)
            pygame.draw.rect(screen, COLORS['dark_gray'], 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Foreground (current health)
            health_width = bar_width * health_percent
            
            # Choose color based on health percent
            if health_percent > 0.6:
                health_color = COLORS['green']
            elif health_percent > 0.3:
                health_color = COLORS['yellow']
            else:
                health_color = COLORS['red']
                
            pygame.draw.rect(screen, health_color, 
                           (bar_x, bar_y, health_width, bar_height))
                           
    def draw_health_bar_at_screen_pos(self, screen, screen_pos):
        """Draw health bar above enemy at screen position"""
        # Only draw health bar if enemy has taken damage
        if self.health < self.max_health:
            health_percent = max(0, self.health / self.max_health)
            bar_width = self.radius * 2
            bar_height = 4
            
            # Position above enemy
            bar_x = screen_pos[0] - bar_width / 2
            bar_y = screen_pos[1] - self.radius - 10
            
            # Background (empty health)
            pygame.draw.rect(screen, COLORS['dark_gray'], 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Foreground (current health)
            health_width = bar_width * health_percent
            
            # Choose color based on health percent
            if health_percent > 0.6:
                health_color = COLORS['green']
            elif health_percent > 0.3:
                health_color = COLORS['yellow']
            else:
                health_color = COLORS['red']
                
            pygame.draw.rect(screen, health_color, 
                           (bar_x, bar_y, health_width, bar_height))

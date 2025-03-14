import pygame
import math
import random
from utils.constants import COLORS
from ui.floating_text import FloatingText

class Drop:
    def __init__(self, x, y, drop_type, value=1):
        """Initialize a drop with world coordinates"""
        self.world_pos = [x, y]
        self.drop_type = drop_type  # 'coin', 'health', 'damage', 'speed', 'attack_speed'
        self.value = value  # Amount to increase the corresponding stat
        self.radius = 10  # Visual radius 
        self.pickup_radius = 20  # Pickup detection radius (remains unchanged)
        self.lifetime = 600  # 10 seconds at 60 FPS
        self.spawn_time = pygame.time.get_ticks()
        self.collected = False
        self.color = self.get_color_for_type()
        self.floating_text = None  # Store floating text reference
        
        # Bouncing effect parameters
        self.bounce_height = 5  # Maximum bounce height
        self.bounce_speed = 0.1  # Speed of the bounce
        self.bounce_time = random.uniform(0, 3.14)  # Random start phase
        self.bounce_offset = 0  # Current bounce offset
        
        # Pulse animation parameters
        self.pulse_speed = 0.05
        self.pulse_time = 0
        self.pulse_amount = 1.5  # Max pulse size multiplier
        
        # For coins, add spin animation
        self.spin_angle = 0
        self.spin_speed = 0.1 if drop_type == 'coin' else 0

    def get_color_for_type(self):
        """Get appropriate color based on drop type"""
        if self.drop_type == 'health':
            return COLORS['green']
        elif self.drop_type == 'coin':
            return COLORS['gold']
        elif self.drop_type == 'damage':
            return COLORS['red']
        elif self.drop_type == 'speed':
            return COLORS['blue']
        elif self.drop_type == 'attack_speed':
            return COLORS['yellow']
        else:
            return COLORS['white']

    def update(self):
        """Update drop state"""
        # Check if drop has expired
        self.lifetime -= 1
        
        # Update bouncing effect
        self.bounce_time += self.bounce_speed
        self.bounce_offset = abs(math.sin(self.bounce_time) * self.bounce_height)
        
        # Update pulse animation
        self.pulse_time += self.pulse_speed
        
        # Update spin animation for coins
        if self.drop_type == 'coin':
            self.spin_angle += self.spin_speed
            if self.spin_angle >= 6.28:  # Full circle (2π)
                self.spin_angle = 0
        
        # Update floating text if it exists
        if self.floating_text:
            self.floating_text.update()
        
        # Return True if drop is still active
        return self.lifetime > 0
        
    def check_pickup(self, player_world_pos, pickup_radius=50):
        if self.collected:
            return False
            
        # Calculate distance between drop and player in world space
        dx = self.world_pos[0] - player_world_pos[0]
        dy = self.world_pos[1] - player_world_pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance < pickup_radius:
            self.collected = True
            
            # Create floating text based on drop type
            text = ""
            color = COLORS['white']
            if self.drop_type == 'coin':
                text = f"+{self.value} coins"
                color = COLORS['gold']
            elif self.drop_type == 'health':
                text = f"+{self.value} HP"
                color = COLORS['green']
            elif self.drop_type == 'damage':
                text = f"+{self.value} DMG"
                color = COLORS['red']
            elif self.drop_type == 'speed':
                text = f"+{self.value} SPD"
                color = COLORS['blue']
            elif self.drop_type == 'attack_speed':
                text = f"+{self.value} ATK SPD"
                color = COLORS['yellow']
            
            # Create floating text at the drop's position
            self.floating_text = FloatingText(
                text,
                self.world_pos[0],  # x coordinate
                self.world_pos[1],  # y coordinate
                color,
                size=20,
                lifetime=60
            )
            
            return True
        return False
        
    def draw(self, screen):
        """Draw drop at world position"""
        self.draw_at_screen_pos(screen, self.world_pos)
        
        # Draw floating text if it exists
        if self.floating_text:
            self.floating_text.draw(screen)

    def draw_at_screen_pos(self, screen, screen_pos):
        """Draw drop at given screen position"""
        # Apply bounce offset to y position
        draw_pos = (int(screen_pos[0]), int(screen_pos[1] - self.bounce_offset))
        
        if self.drop_type == 'coin':
            self.draw_coin(screen, draw_pos)
        elif self.drop_type == 'health':
            self.draw_health(screen, draw_pos)
        elif self.drop_type == 'damage':
            self.draw_damage(screen, draw_pos)
        elif self.drop_type == 'speed':
            self.draw_speed(screen, draw_pos)
        elif self.drop_type == 'attack_speed':
            self.draw_attack_speed(screen, draw_pos)
        else:
            # Generic drop
            pygame.draw.circle(screen, self.color, draw_pos, self.radius)
            pygame.draw.circle(screen, COLORS['white'], draw_pos, self.radius, 1)

    def draw_coin(self, screen, pos):
        """Draw a coin with animated effects"""
        # Calculate pulse effect
        pulse = abs(math.sin(self.pulse_time)) * 0.2 + 1.0
        current_radius = self.radius * pulse
        
        # Calculate spin effect (make coin appear thinner when viewed from side)
        squish = abs(math.sin(self.spin_angle)) * 0.7 + 0.3  # 0.3 to 1.0
        
        # Draw coin base (circle)
        pygame.draw.circle(screen, COLORS['gold'], pos, current_radius)
        
        # Draw coin highlight
        highlight_pos = (pos[0] - 2, pos[1] - 2)
        pygame.draw.circle(screen, COLORS['coin_highlight'], highlight_pos, current_radius * 0.4)
        
        # Draw coin outline
        pygame.draw.circle(screen, COLORS['yellow_dark'], pos, current_radius, 1)
        
        # Draw coin value if greater than 1
        if self.value > 1:
            font = pygame.font.Font(None, 20)
            value_text = font.render(str(self.value), True, COLORS['white'])
            screen.blit(value_text, (pos[0] - 4, pos[1] - 6))

    def draw_health(self, screen, pos):
        """Draw a health pickup (green cross)"""
        pulse = abs(math.sin(self.pulse_time)) * 0.2 + 1.0
        current_radius = self.radius * pulse
        
        # Draw circle background
        pygame.draw.circle(screen, COLORS['green'], pos, current_radius)
        
        # Draw white cross
        cross_size = int(current_radius * 0.7)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0], pos[1] - cross_size), 
                       (pos[0], pos[1] + cross_size), 2)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0] - cross_size, pos[1]), 
                       (pos[0] + cross_size, pos[1]), 2)
        
        # Draw outline
        pygame.draw.circle(screen, COLORS['white'], pos, current_radius, 1)

    def draw_damage(self, screen, pos):
        """Draw a damage pickup (red sword/arrow)"""
        pulse = abs(math.sin(self.pulse_time)) * 0.2 + 1.0
        current_radius = self.radius * pulse
        
        # Draw circle background
        pygame.draw.circle(screen, COLORS['red'], pos, current_radius)
        
        # Draw sword/arrow symbol
        arrow_size = int(current_radius * 0.8)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0], pos[1] - arrow_size), 
                       (pos[0], pos[1] + arrow_size), 2)
        # Arrow head
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0], pos[1] - arrow_size), 
                       (pos[0] - arrow_size//2, pos[1] - arrow_size//2), 2)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0], pos[1] - arrow_size), 
                       (pos[0] + arrow_size//2, pos[1] - arrow_size//2), 2)
        
        # Draw outline
        pygame.draw.circle(screen, COLORS['white'], pos, current_radius, 1)

    def draw_speed(self, screen, pos):
        """Draw a speed pickup (blue lightning bolt)"""
        pulse = abs(math.sin(self.pulse_time)) * 0.2 + 1.0
        current_radius = self.radius * pulse
        
        # Draw circle background
        pygame.draw.circle(screen, COLORS['blue'], pos, current_radius)
        
        # Draw lightning bolt symbol (simplified)
        bolt_size = int(current_radius * 0.8)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0] - bolt_size//2, pos[1] - bolt_size), 
                       (pos[0], pos[1]), 2)
        pygame.draw.line(screen, COLORS['white'], 
                       (pos[0], pos[1]), 
                       (pos[0] + bolt_size//2, pos[1] + bolt_size), 2)
        
        # Draw outline
        pygame.draw.circle(screen, COLORS['white'], pos, current_radius, 1)

    def draw_attack_speed(self, screen, pos):
        """Draw an attack speed pickup (yellow clock)"""
        pulse = abs(math.sin(self.pulse_time)) * 0.2 + 1.0
        current_radius = self.radius * pulse
        
        # Draw circle background
        pygame.draw.circle(screen, COLORS['yellow'], pos, current_radius)
        
        # Draw clock symbol (simplified)
        clock_radius = int(current_radius * 0.7)
        pygame.draw.circle(screen, COLORS['white'], pos, clock_radius, 1)
        
        # Draw clock hands
        hand_length = clock_radius * 0.6
        angle = self.pulse_time * 3  # Make hands rotate
        hand_x = pos[0] + math.cos(angle) * hand_length
        hand_y = pos[1] + math.sin(angle) * hand_length
        pygame.draw.line(screen, COLORS['white'], pos, (hand_x, hand_y), 1)
        
        # Draw outline
        pygame.draw.circle(screen, COLORS['white'], pos, current_radius, 1)

    def get_world_pos(self):
        return self.world_pos

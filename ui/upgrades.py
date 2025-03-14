import random
import pygame
from typing import Dict, List, Callable
from utils.constants import COLORS

class UpgradeSystem:
    def __init__(self, colors, game):
        self.colors = colors
        self.game = game
        self.available_upgrades = []
        self.show_upgrade_panel = False
        self.upgrade_buttons = []
        
        # Attack types and their levels/stats
        self.attack_types = {
            'click_attack': {'level': 1, 'damage': 10, 'cooldown': 250},  # Basic attack
            'auto_attack': {'level': 0, 'damage': 0, 'cooldown': 0},      # Locked initially
            'piercing': {'level': 0, 'damage': 0, 'cooldown': 0},         # Locked initially
            'special': {'level': 0, 'damage': 0, 'cooldown': 0}           # Locked initially
        }

        # Available upgrade choices
        self.upgrade_choices = {
            'new_auto_attack': {
                'name': "Unlock Auto Attack",
                'description': "Adds automatic targeting attack",
                'condition': lambda: self.attack_types['auto_attack']['level'] == 0
            },
            'new_piercing': {
                'name': "Unlock Piercing Shot",
                'description': "Adds piercing projectiles",
                'condition': lambda: self.attack_types['piercing']['level'] == 0
            },
            'new_special': {
                'name': "Unlock Special Attack",
                'description': "Adds powerful special attack",
                'condition': lambda: self.attack_types['special']['level'] == 0
            },
            'improve_click': {
                'name': "Improve Click Attack",
                'description': "+20% damage, -10% cooldown",
                'condition': lambda: True
            },
            'improve_auto': {
                'name': "Improve Auto Attack",
                'description': "+15% damage, -10% cooldown",
                'condition': lambda: self.attack_types['auto_attack']['level'] > 0
            },
            'improve_piercing': {
                'name': "Improve Piercing",
                'description': "+25% damage, -5% cooldown",
                'condition': lambda: self.attack_types['piercing']['level'] > 0
            },
            'improve_special': {
                'name': "Improve Special",
                'description': "+30% damage, -15% cooldown",
                'condition': lambda: self.attack_types['special']['level'] > 0
            }
        }

    def get_available_upgrades(self) -> List[str]:
        """Return list of available upgrades"""
        return ["max_health", "damage", "speed", "attack_speed"]

    def apply_upgrade(self, choice: str, player_damage: float) -> Dict:
        """Apply the selected upgrade and return updated attack_types"""
        if choice.startswith('new_'):
            attack_type = choice[4:]  # Remove 'new_' prefix
            self.attack_types[attack_type] = {
                'level': 1,
                'damage': player_damage * 0.8,  # Start at 80% of base damage
                'cooldown': 300  # Default cooldown for new attacks
            }
        elif choice.startswith('improve_'):
            attack_type = choice[8:]  # Remove 'improve_' prefix
            if self.attack_types[attack_type]['level'] > 0:
                self.attack_types[attack_type]['level'] += 1
                self.attack_types[attack_type]['damage'] *= 1.2  # 20% damage increase
                self.attack_types[attack_type]['cooldown'] *= 0.9  # 10% cooldown reduction
        
        return self.attack_types

    def show_upgrades(self, upgrades):
        """Show upgrade options"""
        self.upgrades = upgrades
        self.show_upgrade_panel = True
        print(f"Showing upgrades: {len(upgrades)} options available")  # Debug print

    def hide_upgrades(self):
        """Hide the upgrade panel"""
        self.show_upgrade_panel = False
        self.available_upgrades = []

    def draw_upgrade_panel(self, screen, window_width, window_height):
        """Draw the upgrade selection panel"""
        if not self.show_upgrade_panel:
            return
            
        # Draw semi-transparent background
        overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 70% opacity
        screen.blit(overlay, (0, 0))
        
        # Draw upgrade panel
        panel_width = 500
        panel_height = 350
        panel_x = window_width // 2 - panel_width // 2
        panel_y = window_height // 2 - panel_height // 2
        
        # Draw panel background
        pygame.draw.rect(overlay, (30, 30, 50, 255), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(overlay, (0, 255, 255, 255), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw title
        font = pygame.font.Font(None, 36)
        title = font.render("Level Up! Choose an Upgrade", True, (255, 255, 255))
        title_rect = title.get_rect(center=(window_width // 2, panel_y + 30))
        screen.blit(title, title_rect)
        
        # Clear previous upgrade rects
        self.available_upgrades = []
        
        # Draw upgrade options
        if len(self.upgrades) > 0:
            # Select 2 random upgrades to show
            upgrades_to_show = random.sample(self.upgrades, min(2, len(self.upgrades)))
            
            option_height = 80
            option_width = 450
            option_margin = 10
            option_y = panel_y + 70
            
            for i, upgrade in enumerate(upgrades_to_show):  # Show only 2 upgrades
                # Determine color based on upgrade type
                if upgrade == "damage":
                    color = (255, 0, 0)  # Red for damage
                    description = "Increases your attack damage"
                    title_text = "Damage +10%"
                elif upgrade == "speed":
                    color = (0, 0, 255)  # Blue for speed
                    description = "Increases your movement speed"
                    title_text = "Speed +10%"
                elif upgrade == "max_health":
                    color = (0, 255, 0)  # Green for health
                    description = "Increases your maximum health"
                    title_text = "Max Health +10%"
                elif upgrade == "attack_speed":
                    color = (255, 255, 0)  # Yellow for attack speed
                    description = "Increases your attack rate"
                    title_text = "Attack Speed +10%"
                else:
                    color = (200, 200, 200)  # Gray for unknown
                    description = "Unknown upgrade"
                    title_text = f"{upgrade.capitalize()} +10%"
                
                # Draw option background
                option_rect = pygame.Rect(
                    panel_x + (panel_width - option_width) // 2,
                    option_y + (option_height + option_margin) * i,
                    option_width,
                    option_height
                )
                pygame.draw.rect(screen, (50, 50, 70), option_rect)
                pygame.draw.rect(screen, color, option_rect, 2)
                
                # Store the upgrade and its rect for click detection
                self.available_upgrades.append((upgrade, option_rect))
                
                # Draw option title
                option_font = pygame.font.Font(None, 28)
                option_title = option_font.render(title_text, True, (255, 255, 255))
                screen.blit(option_title, (option_rect.x + 10, option_rect.y + 10))
                
                # Draw option description
                desc_font = pygame.font.Font(None, 20)
                desc_text = desc_font.render(description, True, (200, 200, 200))
                screen.blit(desc_text, (option_rect.x + 10, option_rect.y + 40))
                
                # Draw color indicator
                color_text = desc_font.render(f"Rect: <red({color[0]}, {color[1]}, {color[2]}, 100)>", True, (150, 150, 150))
                screen.blit(color_text, (option_rect.x + 10, option_rect.y + 60))

    def handle_upgrades(self, event, window_width, window_height, Button):
        """Handle upgrade events"""
        if not self.show_upgrade_panel:
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            upgrade_type = self.check_click(event.pos)
            if upgrade_type:
                self.game.apply_upgrade(upgrade_type)

    def check_click(self, mouse_pos):
        """Check if an upgrade was clicked and return its type"""
        print(f"Checking click at {mouse_pos}, buttons: {len(self.available_upgrades)}")  # Debug print
        
        if not self.show_upgrade_panel:
            return None
            
        for upgrade, rect in self.available_upgrades:
            if rect.collidepoint(mouse_pos):
                print(f"Clicked on upgrade: {upgrade}")  # Debug print
                return upgrade
                
        return None

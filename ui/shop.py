import pygame
from utils.constants import COLORS, WINDOW_WIDTH, WINDOW_HEIGHT, UI_SCALE
from ui.button import Button

class ShopItem:
    def __init__(self, x, y, width, height, name, base_cost, effect_func, color, 
                 description="", max_purchases=10, cost_increase=1.5):
        self.name = name
        self.description = description
        self.base_cost = base_cost
        self.current_cost = base_cost
        self.effect_func = effect_func
        self.max_purchases = max_purchases
        self.cost_increase = cost_increase
        self.purchases = 0
        
        self.button = Button(x, y, width, height, 
                           f"{int(base_cost)} coins", color)

    def update_cost_text(self):
        if self.purchases >= self.max_purchases:
            self.button.text = "SOLD OUT"
        else:
            self.button.text = f"{int(self.current_cost)} coins"

    def purchase(self):
        if self.purchases < self.max_purchases:
            self.effect_func()
            self.purchases += 1
            self.current_cost *= self.cost_increase
            self.update_cost_text()
            return True
        return False

class Shop:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        
        # Shop panel dimensions
        self.width = 300
        self.height = 400
        self.x = WINDOW_WIDTH - self.width - 10
        self.y = 60
        
        # Close button
        self.close_button = Button(
            self.x + self.width - 25, 
            self.y + 5, 
            20, 
            20, 
            "X", 
            COLORS['red'], 
            'small'
        )
        
        # Shop items with cost and effect
        self.items = [
            {
                'name': 'Max Health +10%',
                'description': 'Increases your maximum health by 10%',
                'cost': 50,
                'action': game.buy_max_health,
                'rect': pygame.Rect(self.x + 10, self.y + 60, self.width - 20, 60)
            },
            {
                'name': 'Damage +10%',
                'description': 'Increases your damage by 10%',
                'cost': 75,
                'action': game.buy_damage_boost,
                'rect': pygame.Rect(self.x + 10, self.y + 130, self.width - 20, 60)
            },
            {
                'name': 'Speed +10%',
                'description': 'Increases your movement speed by 10%',
                'cost': 60,
                'action': game.buy_speed_boost,
                'rect': pygame.Rect(self.x + 10, self.y + 200, self.width - 20, 60)
            },
            {
                'name': 'Attack Speed +10%',
                'description': 'Increases your attack speed by 10%',
                'cost': 80,
                'action': game.buy_attack_speed_boost,
                'rect': pygame.Rect(self.x + 10, self.y + 270, self.width - 20, 60)
            }
        ]
        
    def draw(self, screen):
        """Draw shop interface"""
        if not self.visible:
            # Just draw the shop button in the top-right corner
            self.game.shop_button.draw(screen)
            return
            
        # Draw shop background panel
        pygame.draw.rect(screen, COLORS['dark_gray'], 
                       (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, COLORS['white'], 
                       (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        title = self.title_font.render("Shop", True, COLORS['white'])
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Draw close button
        self.close_button.draw(screen)
        
        # Draw coins display
        coin_text = self.font.render(f"Coins: {self.game.coins}", True, COLORS['gold'])
        screen.blit(coin_text, (self.x + 10, self.y + 40))
        
        # Draw items
        for item in self.items:
            # Highlight if mouse is over item
            mouse_pos = pygame.mouse.get_pos()
            if item['rect'].collidepoint(mouse_pos):
                # Brighter background for hover
                pygame.draw.rect(screen, COLORS['gray'], item['rect'])
            else:
                # Normal background
                pygame.draw.rect(screen, COLORS['dark_gray'], item['rect'])
                
            # Draw border
            pygame.draw.rect(screen, COLORS['white'], item['rect'], 1)
            
            # Draw item name
            name_text = self.font.render(item['name'], True, COLORS['white'])
            screen.blit(name_text, (item['rect'].x + 10, item['rect'].y + 10))
            
            # Draw item description
            desc_text = self.font.render(item['description'], True, COLORS['light_gray'])
            screen.blit(desc_text, (item['rect'].x + 10, item['rect'].y + 30))
            
            # Draw cost
            cost_text = self.font.render(f"Cost: {item['cost']}", True, 
                                       COLORS['gold'] if self.game.coins >= item['cost'] else COLORS['red'])
            screen.blit(cost_text, (item['rect'].x + self.width - 80, item['rect'].y + 10))
    
    def handle_event(self, event):
        """Handle mouse clicks on shop items"""
        if not self.visible:
            return False
            
        # Check if close button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.close_button.rect.collidepoint(event.pos):
                self.visible = False
                return True
                
            # Check if any shop item was clicked
            for item in self.items:
                if item['rect'].collidepoint(event.pos):
                    if self.game.coins >= item['cost']:
                        if item['action']():  # Call the action function
                            self.game.coins -= item['cost']
                            return True
                    else:
                        # Show "Can't afford" message
                        print("Can't afford this item!")
                        return True
                        
        return False

import pygame
from utils.constants import COLORS, UI_SCALE

class Button:
    def __init__(self, x, y, width, height, text, color, size='medium'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hovered = False
        self.size = size
        self.corner_radius = int(10 * UI_SCALE)
        self.shadow_offset = int(4 * UI_SCALE)

    def draw(self, surface):
        # Draw shadow
        shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
        pygame.draw.rect(surface, (30, 30, 30), shadow_rect, 
                        border_radius=self.corner_radius)
        
        # Draw main button
        pygame.draw.rect(surface, self.color, self.rect, 
                        border_radius=self.corner_radius)
        
        # Hover effect
        if self.hovered:
            hover_color = tuple(min(c + 20, 255) for c in self.color)
            inner_rect = self.rect.inflate(-self.shadow_offset, -self.shadow_offset)
            pygame.draw.rect(surface, hover_color, inner_rect, 
                           border_radius=self.corner_radius)

        # Draw text
        font_size = {
            'small': int(24 * UI_SCALE),
            'medium': int(32 * UI_SCALE),
            'large': int(40 * UI_SCALE)
        }[self.size]
        
        font = pygame.font.SysFont('arial', font_size)
        text_surface = font.render(self.text, True, COLORS['white'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

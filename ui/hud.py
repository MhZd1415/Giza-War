import pygame
import math
from utils.constants import COLORS, UI_SCALE, WINDOW_WIDTH, WINDOW_HEIGHT

class HUD:
    def __init__(self, game):
        pygame.font.init()  # Ensure font system is initialized
        self.font = pygame.font.Font(None, 24)
        self.header_font = pygame.font.Font(None, 32)
        self.game = game
        
        # Initialize all required attributes
        self.stats_flash = {}
        self.xp_bar_current = 0
        self.wave_text_scale = 1.0
        self.coin_bounce = 0
        self.countdown_active = False
        self.countdown_end_time = 0
        self.last_update_time = pygame.time.get_ticks()
        
        # Initialize any required game attributes if they don't exist
        if not hasattr(self.game, 'player_experience'):
            self.game.player_experience = 0
        if not hasattr(self.game, 'required_xp'):
            self.game.required_xp = 100
        
    def start_countdown(self, duration):
        self.countdown_active = True
        self.countdown_end_time = pygame.time.get_ticks() / 1000.0 + duration
        
    def draw(self, screen):
        """Draw all HUD elements with error handling"""
        try:
            # Check if player exists
            if not hasattr(self.game, 'player'):
                # Draw a message if player doesn't exist
                font = pygame.font.Font(None, 36)
                text = font.render("Player not initialized", True, COLORS.get('red', (255, 0, 0)))
                screen.blit(text, (WINDOW_WIDTH // 2 - 100, 20))
                return
            
            # Draw main stats panel
            try:
                self.draw_main_stats(screen)
            except Exception as stats_error:
                import logging
                logging.error(f"Error drawing main stats: {stats_error}")
            
            # Draw basic HUD elements
            self.draw_health_bar(screen)
            self.draw_wave_info(screen)
            self.draw_score(screen)
            self.draw_coins(screen)
            
            # Draw minimap if world_map exists
            if hasattr(self.game, 'world_map'):
                self.draw_mini_map(screen)
            
            # Draw countdown if active
            if self.countdown_active:
                self.draw_countdown(screen)
            
            # Draw debug overlay if debug mode is enabled
            if hasattr(self.game, 'debug_mode') and self.game.debug_mode:
                self.draw_debug_overlay(screen)
            
        except Exception as e:
            import logging
            logging.error(f"Error drawing HUD: {e}")
            
            # Draw a basic error message
            try:
                font = pygame.font.Font(None, 24)
                text = font.render("HUD Error: Check logs", True, (255, 0, 0))
                screen.blit(text, (20, 20))
            except:
                pass

    def draw_countdown(self, screen):
        """Draw countdown timer"""
        try:
            current_time = pygame.time.get_ticks() / 1000.0
            remaining = self.countdown_end_time - current_time
            if remaining > 0:
                countdown_text = str(math.ceil(remaining))
                font = pygame.font.Font(None, 74)
                text = font.render(countdown_text, True, COLORS.get('warning', COLORS.get('yellow', (255, 255, 0))))
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                screen.blit(text, text_rect)
            else:
                self.countdown_active = False
        except Exception as e:
            import logging
            logging.error(f"Error drawing countdown: {e}")
        
    def draw_health_bar(self, screen):
        """Draw player health bar with error handling"""
        try:
            # Ensure player exists and has health attributes
            if not hasattr(self.game, 'player') or not hasattr(self.game.player, 'health') or not hasattr(self.game.player, 'max_health'):
                return
            
            # Draw health bar background
            bar_width = 200
            bar_height = 20
            bar_x = 20
            bar_y = 20
            pygame.draw.rect(screen, COLORS.get('red', (255, 0, 0)), (bar_x, bar_y, bar_width, bar_height))
            
            # Draw current health (green portion)
            health_percent = max(0, min(1, self.game.player.health / self.game.player.max_health))
            health_width = int(bar_width * health_percent)
            pygame.draw.rect(screen, COLORS.get('green', (0, 255, 0)), (bar_x, bar_y, health_width, bar_height))
            
            # Draw border around health bar
            pygame.draw.rect(screen, COLORS.get('white', (255, 255, 255)), (bar_x, bar_y, bar_width, bar_height), 2)
            
            # Draw health text
            health_text = self.font.render(f"Health: {int(self.game.player.health)}/{int(self.game.player.max_health)}", True, COLORS.get('white', (255, 255, 255)))
            screen.blit(health_text, (bar_x + 10, bar_y + 2))
        except Exception as e:
            import logging
            logging.error(f"Error drawing health bar: {e}")
        
    def draw_wave_info(self, screen):
        """Draw wave information with error handling"""
        try:
            # Check if necessary attributes exist
            if not hasattr(self.game, 'wave_number'):
                return
            
            # Draw wave text
            wave_text = self.font.render(f"Wave: {self.game.wave_number}", True, COLORS.get('white', (255, 255, 255)))
            screen.blit(wave_text, (20, 50))
            
            # Draw enemies left if enemies list exists
            if hasattr(self.game, 'enemies'):
                enemies_text = self.font.render(f"Enemies: {len(self.game.enemies)}", True, COLORS.get('white', (255, 255, 255)))
                screen.blit(enemies_text, (20, 75))
            
            # Draw kill count if it exists
            if hasattr(self.game, 'kills'):
                kills_text = self.font.render(f"Kills: {self.game.kills}", True, COLORS.get('white', (255, 255, 255)))
                screen.blit(kills_text, (20, 100))
        except Exception as e:
            import logging
            logging.error(f"Error drawing wave info: {e}")
        
    def draw_score(self, screen):
        """Draw score with error handling"""
        try:
            # Check if score exists
            if not hasattr(self.game, 'score'):
                return
            
            # Draw score text
            score_text = self.font.render(f"Score: {self.game.score}", True, COLORS.get('white', (255, 255, 255)))
            screen.blit(score_text, (WINDOW_WIDTH - 150, 20))
        except Exception as e:
            import logging
            logging.error(f"Error drawing score: {e}")
        
    def draw_coins(self, screen):
        """Draw coin counter with error handling"""
        try:
            # Check if coins exists
            if not hasattr(self.game, 'coins'):
                return
            
            # Draw coin icon (gold circle)
            coin_icon_x = WINDOW_WIDTH - 150
            coin_icon_y = 50
            coin_radius = 8
            
            pygame.draw.circle(screen, COLORS.get('gold', (255, 215, 0)), (coin_icon_x, coin_icon_y), coin_radius)
            pygame.draw.circle(screen, COLORS.get('yellow_dark', (190, 160, 0)), (coin_icon_x, coin_icon_y), coin_radius, 1)
            
            # Draw coin count
            coin_text = self.font.render(f"x {self.game.coins}", True, COLORS.get('white', (255, 255, 255)))
            screen.blit(coin_text, (coin_icon_x + 15, coin_icon_y - 8))
        except Exception as e:
            import logging
            logging.error(f"Error drawing coins: {e}")
        
    def draw_mini_map(self, screen):
        """Draw mini-map with error handling"""
        try:
            # Check required attributes exist
            if not hasattr(self.game, 'world_map') or not hasattr(self.game, 'player'):
                return
            
            # Mini-map dimensions
            map_width = 150
            map_height = 100
            map_x = WINDOW_WIDTH - map_width - 20
            map_y = WINDOW_HEIGHT - map_height - 20
            
            # Draw mini-map background
            pygame.draw.rect(screen, COLORS.get('dark_gray', (50, 50, 50)), (map_x, map_y, map_width, map_height))
            pygame.draw.rect(screen, COLORS.get('white', (255, 255, 255)), (map_x, map_y, map_width, map_height), 2)
            
            # Calculate scale factors
            scale_x = map_width / self.game.world_map.width
            scale_y = map_height / self.game.world_map.height
            
            # Draw player position on mini-map (small white dot)
            if hasattr(self.game.player, 'pos'):
                player_map_x = map_x + int(self.game.player.pos[0] * scale_x)
                player_map_y = map_y + int(self.game.player.pos[1] * scale_y)
                pygame.draw.circle(screen, COLORS.get('white', (255, 255, 255)), (player_map_x, player_map_y), 3)
            
            # Draw enemies on mini-map (small red dots)
            if hasattr(self.game, 'enemies'):
                for enemy in self.game.enemies:
                    if hasattr(enemy, 'pos'):
                        enemy_map_x = map_x + int(enemy.pos[0] * scale_x)
                        enemy_map_y = map_y + int(enemy.pos[1] * scale_y)
                        # Only draw if within map bounds
                        if (map_x <= enemy_map_x <= map_x + map_width and
                            map_y <= enemy_map_y <= map_y + map_height):
                            pygame.draw.circle(screen, COLORS.get('red', (255, 0, 0)), (enemy_map_x, enemy_map_y), 2)
            
            # Draw current view area on mini-map (white rectangle)
            if hasattr(self.game, 'camera_x') and hasattr(self.game, 'camera_y'):
                view_x = map_x + int(self.game.camera_x * scale_x)
                view_y = map_y + int(self.game.camera_y * scale_y)
                view_width = int(WINDOW_WIDTH * scale_x)
                view_height = int(WINDOW_HEIGHT * scale_y)
                pygame.draw.rect(screen, COLORS.get('white', (255, 255, 255)), 
                               (view_x, view_y, view_width, view_height), 1)
        except Exception as e:
            import logging
            logging.error(f"Error drawing mini-map: {e}")

    def draw_main_stats(self, screen):
        """Draw main player stats with robust error handling"""
        try:
            # Check if required attributes exist
            if not hasattr(self.game, 'player') or not hasattr(self.game, 'player_experience') or not hasattr(self.game, 'required_xp'):
                return
            
            # Larger stats panel in top-left corner
            panel_width = int(250 * UI_SCALE)  # Increased width
            panel_height = int(150 * UI_SCALE)  # Increased height
            padding = int(12 * UI_SCALE)  # Slightly increased padding
            
            # Draw semi-transparent panel background with more opacity
            try:
                panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
                panel_color = COLORS.get('panel', (40, 40, 60, 200))
                # Handle both RGB and RGBA color formats
                if len(panel_color) == 3:
                    panel_color = (*panel_color, 200)  # Add alpha if missing
                pygame.draw.rect(panel_surface, panel_color, (0, 0, panel_width, panel_height), border_radius=12)
                screen.blit(panel_surface, (padding, padding))
            except Exception as panel_error:
                logging.error(f"Error drawing stats panel: {panel_error}")
            
            # Experience bar at the very top
            try:
                xp_ratio = self.game.player_experience / max(1, self.game.required_xp)  # Avoid division by zero
                self.xp_bar_current += (xp_ratio - self.xp_bar_current) * 0.1
                self.draw_bar(screen, padding * 2, padding * 2,
                             panel_width - padding * 3, int(10 * UI_SCALE),  # Slightly taller bars
                             self.xp_bar_current, COLORS.get('accent', (100, 200, 255)),
                             f"Level {getattr(self.game, 'level', 1)}")
            except Exception as xp_error:
                logging.error(f"Error drawing XP bar: {xp_error}")
            
            # Health bar below XP bar
            try:
                if hasattr(self.game.player, 'health') and hasattr(self.game.player, 'max_health'):
                    health_ratio = self.game.player.health / max(1, self.game.player.max_health)  # Avoid division by zero
                    self.draw_bar(screen, padding * 2, padding * 4,
                                 panel_width - padding * 3, int(10 * UI_SCALE),
                                 health_ratio, COLORS.get('health', (0, 255, 0)),
                                 f"HP: {int(self.game.player.health)}/{int(self.game.player.max_health)}")
            except Exception as health_error:
                logging.error(f"Error drawing health bar: {health_error}")
            
            # Stats with improved icons
            try:
                y_offset = padding * 6  # Moved down to accommodate health bar
                icon_size = int(20 * UI_SCALE)  # Larger icons
                spacing = int(28 * UI_SCALE)  # Increased spacing
                
                # Only show stats that exist
                stats = []
                
                if hasattr(self.game.player, 'bullet_damage'):
                    stats.append(("🗡️", f"{self.game.player.bullet_damage:.1f}", COLORS.get('red', (255, 0, 0))))
                    
                if hasattr(self.game.player, 'shoot_delay') and self.game.player.shoot_delay > 0:
                    stats.append(("⚡", f"{(1000/self.game.player.shoot_delay):.1f}/s", COLORS.get('yellow', (255, 255, 0))))
                    
                if hasattr(self.game.player, 'speed'):
                    stats.append(("👟", f"{self.game.player.speed:.1f}", COLORS.get('blue', (0, 0, 255))))
                    
                if hasattr(self.game, 'coins'):
                    stats.append(("💰", f"{self.game.coins}", COLORS.get('gold', (255, 215, 0))))
                    
                if hasattr(self.game, 'kills'):
                    stats.append(("💀", f"{self.game.kills}", COLORS.get('purple', (150, 50, 200))))
                
                # Larger font for better readability
                small_font = pygame.font.SysFont('arial', int(16 * UI_SCALE))
                for i, (icon, value, color) in enumerate(stats):
                    # Draw stat in two columns
                    x_offset = padding * 2 + (i % 2) * (panel_width // 2)
                    row = i // 2
                    y = y_offset + row * spacing
                    
                    # Draw icon with background circle
                    icon_bg_radius = int(12 * UI_SCALE)
                    pygame.draw.circle(screen, color, (x_offset + icon_bg_radius, y + icon_bg_radius), icon_bg_radius)
                    icon_text = small_font.render(icon, True, COLORS.get('white', (255, 255, 255)))
                    icon_rect = icon_text.get_rect(center=(x_offset + icon_bg_radius, y + icon_bg_radius))
                    screen.blit(icon_text, icon_rect)
                    
                    # Draw value with improved spacing
                    value_text = small_font.render(str(value), True, COLORS.get('white', (255, 255, 255)))
                    screen.blit(value_text, (x_offset + icon_size + padding * 1.5, y + icon_bg_radius - value_text.get_height()//2))
            except Exception as stats_error:
                logging.error(f"Error drawing player stats: {stats_error}")
        except Exception as e:
            logging.error(f"Error in draw_main_stats: {e}")

    def draw_bar(self, screen, x, y, width, height, ratio, color, text=""):
        """Draw a progress bar with error handling"""
        try:
            # Draw background with rounded corners
            pygame.draw.rect(screen, COLORS.get('dark_gray', (50, 50, 50)), (x, y, width, height), border_radius=height//2)
            
            # Draw filled portion with rounded corners
            fill_width = int(width * max(0, min(1, ratio)))  # Clamp ratio between 0-1
            if fill_width > 0:
                pygame.draw.rect(screen, color, (x, y, fill_width, height), border_radius=height//2)
            
            # Draw text if provided with improved visibility
            if text:
                font = pygame.font.SysFont('arial', int(14 * UI_SCALE))
                text_surface = font.render(text, True, COLORS.get('white', (255, 255, 255)))
                text_rect = text_surface.get_rect(midleft=(x + 8, y + height // 2))
                # Draw text shadow for better readability
                shadow_surface = font.render(text, True, COLORS.get('black', (0, 0, 0)))
                shadow_rect = shadow_surface.get_rect(midleft=(text_rect.left + 1, text_rect.centery + 1))
                screen.blit(shadow_surface, shadow_rect)
                screen.blit(text_surface, text_rect)
        except Exception as e:
            logging.error(f"Error drawing bar: {e}")

    def draw_player_buffs(self, screen):
        if not hasattr(self.game.player, 'active_buffs'):
            return
            
        buff_size = int(30 * UI_SCALE)
        x = WINDOW_WIDTH - buff_size - int(10 * UI_SCALE)
        y = int(10 * UI_SCALE)
        
        for buff in self.game.player.active_buffs:
            if hasattr(buff, 'draw_icon'):
                pygame.draw.rect(screen, COLORS['panel'],
                               (x, y, buff_size, buff_size))
                buff.draw_icon(screen, x, y, buff_size)
                y += buff_size + int(5 * UI_SCALE)

    def draw_minimap(self, screen):
        # Placeholder for minimap implementation
        pass

    def update(self, dt):
        """Update HUD elements"""
        # Update countdown if active
        if self.countdown_active:
            current_time = pygame.time.get_ticks() / 1000.0
            if current_time >= self.countdown_end_time:
                self.countdown_active = False
            
        # Smoothly update XP bar
        if hasattr(self.game, 'player_experience') and hasattr(self.game, 'required_xp'):
            target_ratio = self.game.player_experience / self.game.required_xp
            self.xp_bar_current += (target_ratio - self.xp_bar_current) * 0.1
        
        # Update coin bounce animation
        self.coin_bounce = (self.coin_bounce + dt * 0.1) % (2 * math.pi)
        
        # Update wave text scale with pulsing effect
        if self.game.state == "playing":
            self.wave_text_scale = 1.0 + math.sin(pygame.time.get_ticks() * 0.005) * 0.1

    def draw_debug_overlay(self, screen):
        """Draw debug information overlay"""
        try:
            # Create a semi-transparent surface for debug info
            debug_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            debug_surface.fill((0, 0, 0, 150))  # Semi-transparent black
            
            # Debug text
            debug_info = [
                f"FPS: {getattr(self.game, 'current_fps', 0):.1f}",
                f"Game State: {getattr(self.game, 'state', 'unknown')}",
                f"Player Pos: {getattr(self.game.player, 'pos', [0, 0])}",
                f"Camera: [{getattr(self.game, 'camera_x', 0):.1f}, {getattr(self.game, 'camera_y', 0):.1f}]",
                f"Enemies: {len(getattr(self.game, 'enemies', []))}",
                f"Projectiles: {len(getattr(self.game, 'projectiles', []))}",
                f"Drops: {len(getattr(self.game, 'drops', []))}",
                f"Wave: {getattr(self.game, 'wave_number', 0)}",
                f"Shop Open: {getattr(self.game, 'shop_open', False)}"
            ]
            
            # Draw debug info
            font = pygame.font.Font(None, 20)
            for i, info in enumerate(debug_info):
                text = font.render(info, True, (255, 255, 255))
                debug_surface.blit(text, (10, 10 + i * 20))
            
            # Draw the debug surface in the bottom-left corner
            screen.blit(debug_surface, (10, WINDOW_HEIGHT - 310))
        except Exception as e:
            import logging
            logging.error(f"Error drawing debug overlay: {e}")
